---
name: e-contract
description: "Generates consumer-driven contract tests from API specifications to verify provider and consumer compliance. Use when implementing contracts between services, verifying backward compatibility, or testing microservice integrations. Also applies when: 'contract tests', 'Pact tests', 'API compatibility tests', 'verify API contracts'."
---

# Contract Test Generator

This skill generates consumer-driven contract tests from API specifications or route handler analysis. The generated tests verify that providers honor their contracts and that consumers correctly handle provider responses.

## Prerequisites

- An OpenAPI specification or a codebase with identifiable API route handlers.
- A testing framework installed in the project (Jest, Vitest, Mocha, pytest, or equivalent).
- The eMCP filesystem, data_file_read, ast_search, and lsp_symbols servers available.

## Workflow

### Step 1: Identify the API Contract Source

Determine where the API contract is defined. Check in this order of preference:

1. **OpenAPI/Swagger spec**: Use `data_file_read` to parse `openapi.yaml`, `openapi.json`, `swagger.yaml`, or `swagger.json`. This is the most reliable contract source.
2. **Route handler code**: If no spec exists, use `ast_search` and `lsp_symbols` to analyze route handler files and infer contracts from code.
3. **Existing type definitions**: Check for shared types or DTOs that define request/response shapes between services.

Record the contract source for each endpoint:

| Endpoint         | Method | Contract Source          |
|------------------|--------|--------------------------|
| /api/users       | GET    | openapi.yaml             |
| /api/users       | POST   | openapi.yaml             |
| /api/orders      | GET    | src/routes/orders.ts     |

### Step 2: Extract Contracts from Spec

If an OpenAPI spec is available, extract the following for each operation:

- **Request contract**: HTTP method, path, required headers, query parameters with types, path parameters, request body schema.
- **Response contract**: Status codes, response body schema per status code, required response headers.
- **Authentication**: Required security schemes and their format.

For each schema, resolve all `$ref` references to produce a flat, self-contained contract definition.

If no spec is available, use `ast_search` to find route handlers and extract contracts from:
- Parameter decorators or type annotations on handler functions.
- Validation schemas (Joi, Zod, Yup, Pydantic models) applied to routes.
- Response type annotations or explicit response construction calls.

Use `lsp_symbols` to navigate from route handlers to their associated types and validation schemas.

### Step 3: Generate Provider Verification Tests

Generate tests that verify the API provider (server) honors each contract. The tests make real HTTP requests against the provider and validate responses.

**Test structure per endpoint**:

```
describe('Contract: GET /api/users')
  it('returns 200 with valid user array schema')
    - Send GET request to /api/users
    - Assert status code is 200
    - Assert response body matches User[] schema
    - Assert required headers present (Content-Type)

  it('returns 401 without authentication')
    - Send GET request without auth header
    - Assert status code is 401
    - Assert response body matches Error schema

  it('returns 400 for invalid query parameters')
    - Send GET request with invalid page=-1
    - Assert status code is 400
    - Assert response body matches Error schema
```

**Schema validation approach**: Generate JSON Schema validators from the OpenAPI component schemas. Use ajv (JavaScript), jsonschema (Python), or equivalent library for runtime schema validation in tests.

Detect the project's test framework and HTTP client:

| Language   | Test Framework       | HTTP Client           |
|------------|----------------------|-----------------------|
| JavaScript | Jest, Vitest, Mocha  | supertest, axios      |
| TypeScript | Jest, Vitest, Mocha  | supertest, axios      |
| Python     | pytest               | httpx, requests       |
| Go         | testing              | net/http              |
| Java       | JUnit                | RestAssured            |

### Step 4: Generate Consumer Stub Tests

Generate tests that verify consumers correctly handle provider responses. These tests use mocked/stubbed responses instead of real HTTP calls.

**Pact-style consumer tests**:

For JavaScript/TypeScript projects, generate Pact or MSW-based consumer tests:

```
describe('UserService consumer contract')
  it('handles successful user list response')
    - Set up mock/stub returning valid User[] response
    - Call consumer's fetchUsers() method
    - Assert consumer correctly parses the response
    - Assert consumer handles all required fields

  it('handles error responses gracefully')
    - Set up mock/stub returning 500 error
    - Call consumer's fetchUsers() method
    - Assert consumer surfaces error appropriately
    - Assert consumer does not crash
```

**Mock implementation by framework**:

| Pattern | Library | Use Case                          |
|---------|---------|-----------------------------------|
| Pact    | pact-js | Full contract testing lifecycle   |
| MSW     | msw     | Browser and Node request mocking  |
| Nock    | nock    | Node.js HTTP request mocking      |

Choose the mock pattern based on existing project dependencies. If none are present, default to MSW for JavaScript/TypeScript projects and `responses` or `respx` for Python projects.

### Step 5: Generate Request/Response Pair Fixtures

For each contract, generate fixture data that represents valid request/response pairs:

**Request fixtures**:
- A valid request with all required fields populated.
- A minimal request with only required fields (no optional fields).
- Boundary value requests (empty strings, zero values, maximum length strings).

**Response fixtures**:
- A success response with all fields populated.
- A success response with only required fields.
- Error responses for each documented error status code.

Generate fixture data based on schema types:

| Schema Type | Example Value               |
|-------------|-----------------------------|
| string      | "test-string"               |
| integer     | 42                          |
| number      | 3.14                        |
| boolean     | true                        |
| date-time   | "2025-01-15T10:30:00Z"      |
| email       | "user@example.com"          |
| uuid        | "550e8400-e29b-41d4-a716-446655440000" |
| uri         | "https://example.com/resource" |
| enum        | First defined enum value    |
| array       | Array with 2 items          |

Use `format` hints from the OpenAPI schema to generate realistic values.

### Step 6: Handle Backward Compatibility Checks

Generate tests that specifically verify backward compatibility when the API is changing:

- **Additive changes**: New optional fields in responses should not break existing consumers. Generate a test that validates the old response schema still passes against the new response.
- **Removed fields**: If a field is removed from a response, generate a test that the consumer handles its absence.
- **Type changes**: If a field type changes, generate tests for both the old and new type.
- **New required fields in requests**: Generate a test verifying the provider rejects requests missing the new required field with a clear error message.

Use git history to detect changes. Compare the current spec against the previous version using `git_diff` or `git_log` to identify what changed.

### Step 7: Generate Test Configuration

Generate supporting configuration files:

**Test setup file**:
- Base URL configuration (environment variable with localhost default).
- Authentication helpers (token generation or fixture credentials).
- Common assertion helpers for schema validation.
- Test database seeding or fixture loading if the provider tests need data.

**CI integration**:
- Suggest running provider tests against a locally running server.
- Suggest running consumer tests as part of the standard unit test suite.
- Note that Pact tests produce pact files that should be shared via a Pact Broker or committed to the repository.

### Step 8: Output Generated Tests

Write the generated test files to the project's test directory. Follow the project's existing test file conventions for naming and location:

| Convention             | Example Path                           |
|------------------------|----------------------------------------|
| Colocated tests        | src/routes/__tests__/users.contract.ts |
| Separate test dir      | tests/contract/users.test.ts           |
| Python convention      | tests/contract/test_users.py           |

Use `filesystem` tools to write the files. Report what was generated:

```
## Generated Contract Tests

### Provider Tests
- tests/contract/provider/users.test.ts (4 tests)
- tests/contract/provider/orders.test.ts (6 tests)

### Consumer Tests
- tests/contract/consumer/user-service.test.ts (3 tests)
- tests/contract/consumer/order-service.test.ts (4 tests)

### Fixtures
- tests/contract/fixtures/users.json
- tests/contract/fixtures/orders.json

### Total: 17 contract tests covering 8 endpoints
```

Optionally, run the generated tests using `test_run` to verify they pass against the current implementation.

## Edge Cases

- **No spec and no types**: If neither an API spec nor typed route handlers exist, inform the user that contract extraction requires at least one structured source. Suggest creating an OpenAPI spec first using the e-mock skill's spec extraction capabilities.
- **Spec-implementation mismatch**: If both a spec and code exist, note that the generated tests validate against the spec. Discrepancies between spec and code will surface as test failures, which is the intended behavior.
- **GraphQL APIs**: This skill targets REST/HTTP APIs. For GraphQL contract testing, use the e-graphql skill to validate the schema and generate operation-level tests.
- **gRPC and Protocol Buffers**: Proto files serve as contracts natively. The skill can generate client-side tests that validate proto compatibility but does not generate proto-specific tooling.
- **Microservice chains**: When a service is both a consumer and a provider, generate both sets of tests. Label them clearly to avoid confusion.

## Notes

- Contract tests complement but do not replace integration tests. Contract tests verify the shape and schema of data. Integration tests verify business logic and data flow.
- For ongoing contract management, consider adopting Pact Broker or a similar contract sharing mechanism. This skill generates the initial tests; the team workflow around contract sharing is outside its scope.
- To validate an existing OpenAPI spec for correctness before generating contracts, use the e-openapi skill.

## Related Skills

- **e-openapi** (eskill-api): Run e-openapi before this skill to confirm the API spec is valid before generating contract tests.
- **e-integ** (eskill-coding): Follow up with e-integ after this skill to extend contract tests into broader integration coverage.
