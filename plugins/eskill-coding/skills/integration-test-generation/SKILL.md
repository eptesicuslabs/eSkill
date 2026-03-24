---
name: integration-test-generation
description: "Generates integration test scaffolds that test component interactions, API endpoints, and database operations. Use when adding integration tests, testing API routes, or verifying database interactions. Also applies when: 'write integration tests', 'test this endpoint', 'add API tests', 'test database operations'."
---

# Integration Test Generation

This skill generates integration test scaffolds that verify interactions between components, API endpoints, and database layers. Unlike unit test scaffolds that isolate individual functions, integration tests exercise the wiring between modules, middleware chains, request/response cycles, and data persistence.

## Prerequisites

- A running or buildable application with identifiable API routes or component boundaries.
- A test framework installed in the project (or a preference for one).
- For database tests: a test database configuration or in-memory alternative.

## Workflow

### Step 1: Identify the Integration Boundary

Determine what interaction surface needs testing. Integration tests sit between unit tests and end-to-end tests on the testing pyramid:

| Boundary Type        | Description                                          | Example                              |
|----------------------|------------------------------------------------------|--------------------------------------|
| HTTP endpoint        | Request through middleware to handler and back        | POST /api/users returns 201          |
| Service-to-service   | One service calls another through an internal API     | AuthService calls UserRepository     |
| Database round-trip  | Write data, read it back, verify consistency          | Insert a row, query it, check fields |
| Message queue        | Publish a message, verify consumer processes it       | Emit event, assert side effect       |
| External API mock    | Call an external service through a mocked HTTP layer  | Stripe payment with nock/responses   |

Ask the user which boundary to target if not specified. If the user provides a file path, infer the boundary from the file contents.

### Step 2: Detect the Test Framework and HTTP Layer

Use `filesystem` tools (list_dir, read_text) and `data_file_read` from the eMCP data-file server to read manifest files and detect the stack.

**Test framework detection**:

| Check                                         | Framework        |
|-----------------------------------------------|------------------|
| package.json contains "vitest"                | Vitest           |
| package.json contains "jest"                  | Jest             |
| package.json contains "mocha" + "supertest"   | Mocha + Supertest|
| pyproject.toml contains "pytest"              | pytest           |
| pyproject.toml contains "httpx" or "TestClient"| pytest + httpx  |
| Cargo.toml `[dev-dependencies]` has "actix-rt"| Actix test       |
| go.mod exists                                 | Go testing       |

**HTTP testing library detection**:

| Framework      | HTTP Test Library     | Import                          |
|----------------|-----------------------|---------------------------------|
| Express/Jest   | supertest             | `import request from 'supertest'`|
| Express/Vitest | supertest             | `import request from 'supertest'`|
| Fastify        | fastify.inject()      | Built-in                        |
| FastAPI        | httpx.AsyncClient     | `from httpx import AsyncClient` |
| Flask          | app.test_client()     | Built-in                        |
| Gin            | httptest.NewRecorder  | `net/http/httptest`             |
| Actix          | actix_web::test       | `use actix_web::test`           |

Also check for existing integration test files to detect established patterns. Search for directories named `integration/`, `e2e/`, or files matching `*.integration.test.*` or `*_integration_test.*` using `filesystem` tools.

### Step 3: Analyze Route Handlers and Endpoints

Use `ast_search` from the eMCP AST server to find route definitions in the target file or directory. Search for framework-specific registration patterns:

**Node.js (Express/Fastify)**:
- Search for `router.get`, `router.post`, `router.put`, `router.delete`, `router.patch`.
- Search for `app.get`, `app.post`, `fastify.get`, `fastify.post`.
- For each route, extract: HTTP method, path, handler function, middleware chain.

**Python (FastAPI/Flask)**:
- Search for `@app.get`, `@app.post`, `@router.get`, `@router.post` (FastAPI).
- Search for `@app.route`, `@blueprint.route` (Flask).
- For each route, extract: method, path, handler, dependencies (FastAPI Depends).

**Go (Gin)**:
- Search for `r.GET`, `r.POST`, `group.GET`, `group.POST`.
- For each route, extract: method, path, handler function.

**Rust (Actix)**:
- Search for `web::get()`, `web::post()`, `#[get(...)]`, `#[post(...)]`.
- For each route, extract: method, path, handler, extractors.

Use `lsp_symbols` from the eMCP LSP server to get the full signature of each handler function. Use `lsp_references` to trace which services or repositories the handler calls.

### Step 4: Analyze Database Dependencies

For each handler identified in Step 3, trace database interactions:

1. Use `lsp_references` to follow the call chain from the handler to repository/model layers.
2. Use `ast_search` to find database operation patterns in the called functions:
   - ORM calls: `create`, `findMany`, `save`, `query`, `execute`.
   - Raw SQL: `db.query(`, `connection.execute(`, `cursor.execute(`.
3. Record each database operation: table/model, operation type (read/write), parameters.

This information determines what database fixtures the test needs and what assertions to make about database state after the request.

### Step 5: Generate Setup and Teardown

Produce setup and teardown blocks appropriate to the stack:

**Database setup strategies**:

| Strategy           | When to Use                          | Implementation                      |
|--------------------|--------------------------------------|-------------------------------------|
| In-memory database | SQLite-compatible schemas            | Override connection string           |
| Transaction rollback| Each test runs in a rolled-back txn | Begin transaction in setup, rollback in teardown |
| Seed and truncate  | Tests need specific fixture data     | Insert fixtures in setup, truncate tables in teardown |
| Docker test DB     | Production-like environment needed   | Start container in global setup     |

**Node.js (Express + Supertest + Jest/Vitest)**:
```javascript
let app;

beforeAll(async () => {
  // Initialize app with test database configuration
  app = await createApp({ database: testConfig });
});

afterAll(async () => {
  await app.close();
});

beforeEach(async () => {
  // Seed test data or begin transaction
});

afterEach(async () => {
  // Clean up or rollback transaction
});
```

**Python (FastAPI + pytest)**:
```python
@pytest.fixture
def client(test_db):
    app.dependency_overrides[get_db] = lambda: test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def test_db():
    # Create tables, seed data
    yield session
    session.rollback()
```

**Go (Gin + httptest)**:
```go
func setupRouter() *gin.Engine {
    gin.SetMode(gin.TestMode)
    r := setupApp(testDB)
    return r
}

func TestMain(m *testing.M) {
    testDB = setupTestDB()
    code := m.Run()
    testDB.Close()
    os.Exit(code)
}
```

**Rust (Actix + actix_web::test)**:
```rust
async fn setup_app() -> impl Service<Request, Response = ServiceResponse> {
    let pool = setup_test_pool().await;
    test::init_service(
        App::new().app_data(web::Data::new(pool)).configure(routes)
    ).await
}
```

### Step 6: Generate Database Fixture Helpers

If database operations were identified in Step 4, generate fixture creation helpers:

```
For each model/table involved:
1. Create a factory function that produces a valid entity with sensible defaults.
2. Allow overriding individual fields for specific test scenarios.
3. Return the created entity with its generated ID for use in assertions.
```

Name factories consistently: `createTestUser`, `create_test_user`, `CreateTestUser`, or `test_user_factory` depending on language convention.

Generate fixtures for the foreign key chain. If testing an endpoint that creates an Order, and Order requires a User, the fixture helper must create the User first.

### Step 7: Generate Test Cases per Endpoint

For each route/endpoint, generate test cases covering these categories:

**Success cases**:
- Valid request with all required fields returns expected status code and body.
- Valid request with optional fields returns enriched response.
- Verify the database state after a write operation (created/updated/deleted).

**Validation and error cases**:
- Missing required fields returns 400/422 with error details.
- Invalid field types or values returns 400/422.
- Request for nonexistent resource returns 404.

**Authentication and authorization** (if middleware detected):
- Request without credentials returns 401.
- Request with invalid credentials returns 401.
- Request with insufficient permissions returns 403.

**Edge cases**:
- Empty request body on POST/PUT returns appropriate error.
- Duplicate creation (e.g., unique constraint violation) returns 409.
- Concurrent requests do not produce inconsistent state.
- Large payload handling (if relevant).

Mark each test body with a `// TODO: implement assertion` comment for values that depend on business logic the scaffold cannot infer.

### Step 8: Generate Framework-Specific Test Skeletons

**Express/Fastify (Node.js)**:
```javascript
describe('POST /api/users', () => {
  it('should create a user and return 201', async () => {
    const payload = { email: 'test@example.com', name: 'Test User' };
    const response = await request(app)
      .post('/api/users')
      .send(payload)
      .expect(201);

    expect(response.body).toHaveProperty('id');
    expect(response.body.email).toBe(payload.email);

    // Verify database state
    // TODO: implement assertion
  });

  it('should return 400 for missing required fields', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({})
      .expect(400);

    expect(response.body).toHaveProperty('errors');
  });

  it('should return 401 without authentication', async () => {
    await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com', name: 'Test' })
      .expect(401);
  });
});
```

**FastAPI (Python)**:
```python
def test_create_user(client, test_db):
    payload = {"email": "test@example.com", "name": "Test User"}
    response = client.post("/api/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == payload["email"]

    # Verify database state
    # TODO: implement assertion

def test_create_user_missing_fields(client):
    response = client.post("/api/users", json={})
    assert response.status_code == 422

def test_create_user_unauthorized(unauthenticated_client):
    response = unauthenticated_client.post("/api/users", json={"email": "t@e.com", "name": "T"})
    assert response.status_code == 401
```

**Gin (Go)**:
```go
func TestCreateUser(t *testing.T) {
    router := setupRouter()
    payload := `{"email":"test@example.com","name":"Test User"}`
    req := httptest.NewRequest("POST", "/api/users", strings.NewReader(payload))
    req.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)

    assert.Equal(t, http.StatusCreated, w.Code)
    var body map[string]interface{}
    json.Unmarshal(w.Body.Bytes(), &body)
    assert.Contains(t, body, "id")

    // Verify database state
    // TODO: implement assertion
}
```

**Actix (Rust)**:
```rust
#[actix_web::test]
async fn test_create_user() {
    let app = setup_app().await;
    let payload = json!({"email": "test@example.com", "name": "Test User"});
    let req = test::TestRequest::post()
        .uri("/api/users")
        .set_json(&payload)
        .to_request();
    let resp = test::call_service(&app, req).await;
    assert_eq!(resp.status(), StatusCode::CREATED);

    let body: serde_json::Value = test::read_body_json(resp).await;
    assert!(body.get("id").is_some());

    // Verify database state
    // TODO: implement assertion
}
```

### Step 9: Place the Test File

Follow the project's existing conventions for integration test placement. Check for existing patterns:

| Pattern                              | Example Path                                |
|--------------------------------------|---------------------------------------------|
| Dedicated integration directory      | `tests/integration/users.test.ts`           |
| Co-located with `.integration.` tag  | `src/routes/__tests__/users.integration.test.ts` |
| Python tests directory               | `tests/integration/test_users.py`           |
| Go same-package                      | `handlers/users_integration_test.go`        |
| Rust tests directory                 | `tests/api/users.rs`                        |

Use `filesystem` tools to search for existing integration test files and match their naming convention. If no integration tests exist, default to a `tests/integration/` directory and note this in the output.

### Step 10: Validate the Scaffold

Run the generated test file to verify it compiles and the test runner discovers it:

1. Use `test_run` from the eMCP test-runner server to execute the new test file in isolation.
2. Tests should either pass (if the application is running and the database is available) or fail with clear assertion errors (not import errors or syntax errors).
3. If the test runner cannot find or parse the file, fix the imports and file placement before presenting to the user.

If the test database is not available, run with `--dry-run` or equivalent flag to verify at least that the test file loads without errors.

## Notes

- Integration tests are slower than unit tests. The scaffold includes setup/teardown patterns that minimize database operations per test while maintaining isolation.
- For projects without an existing test database configuration, suggest creating one before running the generated tests. Do not modify production database configurations.
- The generated scaffold is a starting point. Developers must fill in business-logic-specific assertions and may need to adjust fixture data for their domain.
- If the target file contains no route handlers or component boundaries, report this to the user and suggest the test-scaffolding skill for unit tests instead.

## Related Skills

- **test-scaffolding** (eskill-coding): Run test-scaffolding before this skill to ensure unit-level scaffolds exist before generating integration tests.
- **test-data-factory** (eskill-testing): Run test-data-factory alongside this skill to generate realistic test fixtures for integration scenarios.
- **e2e-orchestration** (eskill-testing): Follow up with e2e-orchestration after this skill to extend integration tests into full end-to-end workflows.
