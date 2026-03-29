---
name: e-loadtest
description: "Generates load testing scripts from API route analysis and expected traffic patterns. Supports k6, Artillery, and Locust. Use when setting up performance testing or preparing for traffic increases. Also applies when: 'create load tests', 'performance test this API', 'k6 test script', 'stress test endpoints'."
---

# Load Test Scaffold

This skill generates load testing scripts by analyzing API routes, their characteristics, and expected traffic patterns. It produces ready-to-run scripts for k6, Artillery, or Locust with realistic virtual user scenarios, ramp-up profiles, and assertion thresholds.

## Prerequisites

- A codebase with identifiable API endpoints (route handlers, OpenAPI spec, or similar).
- The eMCP ast_search, lsp_symbols, filesystem, and data_file_read servers available.
- The target load testing tool (k6, Artillery, or Locust) installed for execution.

## Workflow

### Step 1: Detect API Routes

Identify all API endpoints in the project. Use `ast_search` and `lsp_symbols` to find route definitions based on the framework:

| Framework    | Search Pattern                                           |
|--------------|----------------------------------------------------------|
| Express      | `app.get`, `app.post`, `router.get`, `router.post`      |
| Fastify      | `fastify.get`, `fastify.route`, `fastify.register`      |
| Koa          | `router.get`, `router.post`                              |
| NestJS       | `@Get`, `@Post`, `@Put`, `@Delete`, `@Controller`       |
| FastAPI      | `@app.get`, `@app.post`, `@router.get`                   |
| Flask        | `@app.route`, `@blueprint.route`                          |
| Django REST  | `path()` in `urls.py`, `@action` decorators              |
| Spring Boot  | `@GetMapping`, `@PostMapping`, `@RequestMapping`         |
| Gin (Go)     | `r.GET`, `r.POST`, `group.GET`                            |
| Rails        | `get`, `post`, `resources` in `routes.rb`                 |

If an OpenAPI spec exists, use `data_file_read` to parse it and extract routes from the `paths` object instead.

For each route, record:
- HTTP method
- Path pattern (with parameter placeholders)
- Handler function name
- Middleware chain (especially auth requirements)
- Request body schema (if applicable)

### Step 2: Analyze Endpoint Characteristics

Classify each endpoint by its expected performance profile:

| Characteristic       | Detection Method                         | Impact            |
|----------------------|------------------------------------------|-------------------|
| Read vs. write       | GET/HEAD vs. POST/PUT/DELETE             | Concurrency model |
| Auth required        | Auth middleware in chain                 | Test setup needs  |
| File upload          | multipart/form-data content type        | Payload generation|
| Database query       | ORM/query builder calls in handler      | Latency profile   |
| External API call    | HTTP client calls in handler            | Latency variance  |
| Pagination           | limit/offset/cursor parameters          | Iteration pattern |
| Search/filter        | Query parameters for filtering          | Variable latency  |
| Webhook/async        | Queue publish or event emit in handler  | Response time     |

Use `ast_search` to trace from the route handler into its implementation. Follow function calls one level deep to identify database queries, external HTTP calls, and file operations.

### Step 3: Design Virtual User Scenarios

Group endpoints into realistic user scenarios. A scenario represents a sequence of API calls that a typical user or client would make:

**Example scenarios**:

```
Scenario: Browse and purchase
  1. GET /api/products (list products)
  2. GET /api/products/{id} (view product detail)
  3. POST /api/cart/items (add to cart)
  4. GET /api/cart (view cart)
  5. POST /api/orders (place order)
  6. GET /api/orders/{id} (view order confirmation)

Scenario: User authentication flow
  1. POST /api/auth/login (authenticate)
  2. GET /api/users/me (get profile)
  3. PUT /api/users/me (update profile)
  4. POST /api/auth/refresh (refresh token)

Scenario: Read-heavy browsing
  1. GET /api/products (list with pagination, repeat 5x)
  2. GET /api/products/{id} (view random product, repeat 3x)
  3. GET /api/products/{id}/reviews (view reviews)
```

If the user provides traffic distribution information, weight the scenarios accordingly. Otherwise, default to:

| Scenario Type     | Default Weight |
|-------------------|---------------|
| Read-heavy        | 60%           |
| Mixed read/write  | 30%           |
| Write-heavy       | 10%           |

### Step 4: Generate Load Test Scripts

Generate scripts in the format specified by the user. If no preference is stated, detect existing tooling in the project (check `package.json`, `requirements.txt`, project config files). If none found, default to k6.

**k6 (JavaScript)**:

Generate a `k6` script with:
- Import statements for k6 modules (http, check, sleep, group).
- Options block with stages (ramp-up, sustained, ramp-down).
- Scenario functions with grouped HTTP requests.
- Check assertions on response status and timing.
- Custom metrics for business-critical endpoints.
- Test data generation for request bodies.
- Authentication token handling (login once in setup, pass to VUs).

**Artillery (YAML)**:

Generate an Artillery configuration with:
- Target URL and phases (ramp-up, sustained, ramp-down).
- Scenarios with flow steps (get, post, think).
- Capture blocks for extracting response data (tokens, IDs).
- Match assertions for status codes and response bodies.
- Payload files for variable test data.
- Plugins configuration (expect plugin for assertions).

**Locust (Python)**:

Generate a Locust test file with:
- HttpUser class with task methods.
- Task weights based on scenario distribution.
- wait_time between requests (constant or between range).
- on_start method for authentication setup.
- Response validation in task methods.
- Custom event handlers for failure tracking.

### Step 5: Configure Ramp-Up Patterns

Generate appropriate load profiles based on the testing goal:

**Smoke test** (verify the test works):
```
- 1-2 virtual users
- Duration: 1 minute
- Purpose: Validate test script correctness
```

**Load test** (normal traffic):
```
- Ramp up to target VUs over 2 minutes
- Sustain target VUs for 10 minutes
- Ramp down over 1 minute
- Target VUs: based on expected concurrent users
```

**Stress test** (find breaking point):
```
- Ramp up to 2x target VUs over 5 minutes
- Sustain for 5 minutes
- Ramp to 3x target over 3 minutes
- Sustain for 5 minutes
- Ramp down over 2 minutes
```

**Spike test** (sudden traffic burst):
```
- Start at baseline VUs for 2 minutes
- Spike to 10x baseline instantly
- Hold spike for 1 minute
- Drop back to baseline
- Sustain baseline for 5 minutes
```

**Soak test** (sustained load over time):
```
- Ramp up to target VUs over 5 minutes
- Sustain for 1-4 hours
- Ramp down over 5 minutes
- Purpose: Detect memory leaks, connection pool exhaustion
```

Include all profiles as named configurations in the generated script. The user selects which profile to run.

### Step 6: Add Assertions and Thresholds

Define pass/fail criteria for the load test:

**Response time thresholds**:

| Metric                  | Default Threshold |
|-------------------------|-------------------|
| p95 response time       | < 500ms           |
| p99 response time       | < 1500ms          |
| Median response time    | < 200ms           |
| Max response time       | < 5000ms          |

**Error rate thresholds**:

| Metric                  | Default Threshold |
|-------------------------|-------------------|
| HTTP error rate (5xx)   | < 1%              |
| Total error rate        | < 5%              |
| Timeout rate            | < 0.1%            |

**Throughput thresholds**:

| Metric                  | Default Threshold |
|-------------------------|-------------------|
| Requests per second     | > 100 (adjust)    |
| Failed requests         | < 10 total        |

If the project has existing SLO or SLA definitions, use those values instead of defaults.

### Step 7: Generate Test Data

Create supporting test data files for the load test:

**Authentication credentials**:
- Generate a test user credentials file (or document that test users must be provisioned).
- Include token refresh logic in the test script.

**Request payloads**:
- Generate sample request bodies for POST/PUT endpoints based on their schemas.
- Create CSV or JSON data files for parameterized requests (e.g., different product IDs, user names).
- Use schema types to generate realistic data:

| Field Type  | Generated Value Pattern                    |
|-------------|--------------------------------------------|
| email       | `user{VU_ID}_{ITER}@loadtest.example.com`  |
| name        | Parameterized from a names list            |
| id/uuid     | Random or sequential from a pre-seeded set |
| date        | Current date with offset                   |
| number      | Random within schema min/max bounds        |
| enum        | Random selection from allowed values       |

**Environment configuration**:
- Base URL (default to localhost with a port).
- Target VU count (parameterized for different environments).
- Test duration (parameterized).

### Step 8: Output Generated Files

Write the load test files to the project using `filesystem` tools. Follow a conventional directory structure:

```
load-tests/
  k6/
    scenarios/
      smoke.js
      load.js
      stress.js
    lib/
      auth.js
      data.js
    config.js
  data/
    users.csv
    products.json
  README.md (only if explicitly requested)
```

Report what was generated:

```
## Generated Load Test Files

### Scripts
- load-tests/k6/scenarios/smoke.js (smoke test, 1 VU, 1 min)
- load-tests/k6/scenarios/load.js (load test, 50 VU, 13 min)
- load-tests/k6/scenarios/stress.js (stress test, 150 VU, 20 min)

### Support Files
- load-tests/k6/lib/auth.js (authentication helper)
- load-tests/k6/lib/data.js (test data generation)
- load-tests/k6/config.js (environment configuration)

### Test Data
- load-tests/data/users.csv (100 test user credentials)
- load-tests/data/products.json (sample product IDs)

### Endpoints Covered: 12/14 (2 excluded: webhooks)
### Scenarios: 3 (browse, purchase, admin)
### Run Command: k6 run load-tests/k6/scenarios/load.js
```

## Edge Cases

- **No route handlers found**: If the project is a frontend or has no API routes, inform the user that load test generation requires identifiable API endpoints. Suggest providing a target URL and endpoint list manually.
- **WebSocket endpoints**: If the project includes WebSocket routes, generate separate WebSocket load test scenarios using the appropriate tool module (k6/ws, Artillery WebSocket engine, or Locust with websocket-client).
- **GraphQL APIs**: For GraphQL endpoints, generate load tests that send different query shapes rather than testing different URL paths. Vary query complexity across scenarios.
- **File upload endpoints**: For multipart form data endpoints, generate tests with small binary payloads. Note that large file uploads will skew response time metrics and should be tested separately.
- **Rate-limited endpoints**: If rate limiting middleware is detected, configure the load test to stay within limits for functional tests and deliberately exceed limits for stress tests. Include rate limit header checking.
- **Authenticated endpoints**: If most endpoints require authentication, generate a setup phase that authenticates and distributes tokens across virtual users. Avoid having all VUs authenticate simultaneously.

## Notes

- This skill generates the test scaffolding. Tuning VU counts, ramp profiles, and thresholds to match production traffic patterns requires domain knowledge from the user.
- Load tests should run against a dedicated test environment, not production. The generated scripts default to localhost.
- For API specification validation before load testing, use the e-openapi skill.
- For analyzing performance bottlenecks found during load tests, use the e-perf skill from eskill-coding.

## Related Skills

- **e-perf** (eskill-coding): Follow up with e-perf after this skill to analyze results from load test execution.
- **e-monitor** (eskill-devops): Run e-monitor before this skill to ensure monitoring captures metrics during load testing.
