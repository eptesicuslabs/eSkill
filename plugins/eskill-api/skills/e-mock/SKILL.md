---
name: e-mock
description: "Generates mock API servers from OpenAPI specs or route analysis producing realistic response data. Use when developing frontends before backend is ready, testing client integrations, or setting up dev environments. Also applies when: 'mock this API', 'create mock server', 'fake API responses', 'stub backend for frontend'."
---

# API Mock Generator

This skill generates mock API servers that return realistic response data based on OpenAPI specifications or route handler analysis. The generated mocks support frontend development, client integration testing, and isolated development environments.

## Prerequisites

- An OpenAPI/Swagger specification or a codebase with API route handlers.
- The eMCP data_file_read, ast_search, lsp_symbols, and filesystem servers available.

## Workflow

### Step 1: Read API Definition

Determine the API source and extract endpoint definitions. Check sources in order of preference:

1. **OpenAPI/Swagger spec**: Use `data_file_read` to parse the specification file. Extract all paths, methods, request schemas, and response schemas.
2. **Route handler analysis**: Use `ast_search` and `lsp_symbols` to find route definitions in code. Extract paths, methods, and response types from handler implementations.
3. **TypeScript/Python type definitions**: If route handlers reference typed response objects, trace the types to extract response shapes.

For each endpoint, record:

| Field              | Source (Spec)                    | Source (Code)                    |
|--------------------|----------------------------------|----------------------------------|
| Path               | paths object keys                | Route decorator/registration     |
| Method             | Operation keys under path        | HTTP method in decorator         |
| Request body       | requestBody schema               | Parameter types/validation       |
| Response body      | responses.{code}.content schema  | Return type or response call     |
| Path parameters    | parameters with in: path         | Route pattern placeholders       |
| Query parameters   | parameters with in: query        | Request query access patterns    |
| Auth requirement   | security field                   | Auth middleware in chain         |
| Status codes       | responses object keys            | Response status calls            |

### Step 2: Extract Response Schemas

For each endpoint and status code combination, extract the full response schema:

**From OpenAPI spec**:
- Resolve all `$ref` references to produce flat schemas.
- Extract `example` values from schema properties when available.
- Record property types, formats, constraints (minLength, maximum, enum, pattern).
- Handle `oneOf`, `anyOf`, `allOf` compositions by selecting the first variant for mock data.

**From code analysis**:
- Use `lsp_symbols` to find the response type definition.
- Use `ast_search` to extract interface/type properties.
- Trace through type aliases and generics to reach concrete types.
- Check for validation decorators or schema definitions that specify constraints.

Build a schema inventory:

| Endpoint         | Method | Status | Schema             | Has Example |
|------------------|--------|--------|--------------------|-------------|
| /api/users       | GET    | 200    | User[]             | Yes         |
| /api/users       | POST   | 201    | User               | No          |
| /api/users       | POST   | 400    | ValidationError    | No          |
| /api/users/{id}  | GET    | 200    | User               | Yes         |
| /api/users/{id}  | GET    | 404    | NotFoundError      | No          |

### Step 3: Generate Realistic Mock Data

Generate mock response data for each schema. Use property types, formats, and names to produce realistic values:

**Type-based generation**:

| Type / Format      | Generation Strategy                           |
|--------------------|-----------------------------------------------|
| string             | Property-name-aware (see below)               |
| string (date-time) | ISO 8601 timestamp within past 30 days        |
| string (date)      | ISO 8601 date within past 30 days             |
| string (email)     | `{firstName}.{lastName}@example.com`          |
| string (uri)       | `https://example.com/{resource}/{id}`         |
| string (uuid)      | Valid v4 UUID                                 |
| string (enum)      | Random selection from enum values             |
| integer            | Random within min/max or 1-1000               |
| number             | Random float within min/max or 0.01-999.99    |
| boolean            | Alternating true/false across items           |
| array              | 2-5 items with unique data per item           |
| object             | Recursive generation for nested properties    |
| null               | null                                          |

**Property-name-aware string generation**:

| Property Name Pattern | Generated Value                        |
|-----------------------|----------------------------------------|
| *name, *Name          | Realistic name from a fixed set        |
| *email, *Email        | Formatted email address                |
| *phone, *Phone        | Formatted phone number                 |
| *url, *Url, *link     | https://example.com/resource           |
| *address, *Address    | Street address string                  |
| *description, *bio    | One-sentence placeholder text          |
| *id, *Id              | Sequential integer or UUID             |
| *status, *state       | From enum if defined, else "active"    |
| *created*, *updated*  | ISO 8601 timestamp                     |
| *color, *Color        | Hex color code                         |
| *image*, *avatar*     | https://example.com/images/placeholder |
| *price, *amount, *cost| Decimal number formatted as currency   |
| *count, *total, *qty  | Small positive integer                 |

When the spec includes `example` values, use those instead of generated data.

For array responses, generate between 3 and 5 items with distinct values to test list rendering. Each item should have a unique ID and varied field values.

### Step 4: Create Mock Server File

Generate the mock server implementation based on the project's technology stack. Detect the stack from project files:

**MSW (Mock Service Worker) -- for browser-based clients**:

Use MSW when the project is a frontend application (React, Vue, Angular, Svelte) or when `msw` is already in dependencies.

Generate:
- Handler file with `http.get()`, `http.post()`, etc. for each endpoint.
- Response resolver returning generated mock data with `HttpResponse.json()`.
- Setup file for browser (`setupWorker`) and Node (`setupServer`).
- Integration instructions for the project's dev server.

**Express mock server -- for Node.js service-to-service testing**:

Generate:
- Express application with route handlers for each endpoint.
- Each handler returns the mock data with appropriate status codes.
- CORS middleware enabled for cross-origin development.
- A start script with configurable port.

**json-server -- for simple CRUD APIs**:

Use json-server when the API follows RESTful CRUD patterns with resource-based routes.

Generate:
- `db.json` with mock data collections.
- `routes.json` for custom route mappings if paths differ from json-server conventions.
- Configuration for json-server middleware.

**Python responses/respx -- for Python client testing**:

Generate:
- Fixture file using `responses` (for requests library) or `respx` (for httpx).
- Decorator or context manager patterns for test functions.
- Mock data as Python dictionaries.

### Step 5: Include Error Response Mocks

Generate mock handlers for error responses alongside success responses:

**Standard error mocks per endpoint**:
- 400 Bad Request: Return validation error response when request body fails schema.
- 401 Unauthorized: Return authentication error when auth header is missing.
- 403 Forbidden: Return authorization error for restricted resources.
- 404 Not Found: Return not-found error for path-parameter endpoints with non-existent IDs.
- 500 Internal Server Error: Optional, triggered by a special header or query parameter.

**Error triggering mechanism**: Add a convention for triggering error responses from the mock:
- Special ID values: `GET /api/users/not-found` returns 404, `GET /api/users/error` returns 500.
- Request header: `X-Mock-Status: 404` forces a specific error response.
- Query parameter: `?_mockError=401` overrides the success response.

Document the error triggering conventions in the generated code comments.

### Step 6: Add Latency Simulation

Include configurable response delays to simulate realistic network conditions:

**Default latency profiles**:

| Profile   | Delay Range     | Use Case                        |
|-----------|----------------|---------------------------------|
| instant   | 0ms            | Fast development iteration      |
| fast      | 50-150ms       | Optimistic network conditions   |
| normal    | 100-500ms      | Typical production latency      |
| slow      | 500-2000ms     | Slow network / heavy operations |
| timeout   | 5000-10000ms   | Testing timeout handling        |

The latency profile should be configurable via:
- Environment variable (`MOCK_LATENCY=normal`).
- Query parameter on individual requests (`?_mockDelay=500`).
- Global configuration in the mock server setup.

For each endpoint, assign a default latency category based on the operation:
- GET (list): normal
- GET (single): fast
- POST (create): normal
- PUT/PATCH (update): normal
- DELETE: fast
- File upload: slow

### Step 7: Generate Stateful Mock Behavior (Optional)

If the API has CRUD operations on the same resource, generate stateful mock behavior:

- POST creates a new item and stores it in memory.
- GET list returns all stored items (seeded plus created).
- GET by ID returns the specific item.
- PUT/PATCH updates the stored item.
- DELETE removes the item from the store.

This allows frontend developers to test full creation and editing workflows without a backend.

Implement state as an in-memory store that resets on server restart. Seed the store with the generated mock data from Step 3.

### Step 8: Output Generated Files

Write mock files to the project using `filesystem` tools. Place them in a conventional location:

| Mock Type      | Default Location                     |
|----------------|--------------------------------------|
| MSW handlers   | src/mocks/handlers.ts                |
| MSW browser    | src/mocks/browser.ts                 |
| MSW server     | src/mocks/server.ts                  |
| Express mock   | mocks/server.js                      |
| json-server    | mocks/db.json, mocks/routes.json     |
| Python mocks   | tests/mocks/api_mocks.py             |
| Mock data      | mocks/data/ or src/mocks/data/       |

Report what was generated:

```
## Generated Mock Server

### Type: MSW (Mock Service Worker)

### Files
- src/mocks/handlers.ts (14 route handlers)
- src/mocks/browser.ts (browser setup)
- src/mocks/server.ts (Node test setup)
- src/mocks/data/users.json (5 mock users)
- src/mocks/data/orders.json (3 mock orders)

### Endpoints Mocked: 14/14
### Error Mocks: 404, 401, 400 per endpoint
### Latency: Configurable via MOCK_LATENCY env var

### Usage
  import { worker } from './mocks/browser'
  worker.start()
```

## Edge Cases

- **No spec and no typed handlers**: If the API surface cannot be determined from the codebase, ask the user to provide endpoint information manually (path, method, and expected response shape). Generate mocks from the manual input.
- **Binary responses**: For endpoints returning files (images, PDFs, downloads), generate mocks that return small placeholder files of the correct MIME type rather than JSON.
- **Streaming responses**: For Server-Sent Events or streaming endpoints, generate a mock that emits a fixed sequence of events with configurable intervals.
- **GraphQL APIs**: For GraphQL, generate a mock schema with resolvers that return type-appropriate mock data. Use tools like graphql-tools `addMocksToSchema` for JavaScript projects.
- **Authentication tokens**: Generate mock auth endpoints that return valid-looking JWT tokens. The tokens do not need to be cryptographically valid but should have the correct structure (header.payload.signature) for client-side parsing.
- **Large response schemas**: For schemas with deeply nested objects or large arrays, limit mock data depth to 3 levels and array sizes to 5 items to keep mock responses manageable.

## Notes

- Mock servers are for development and testing only. The generated code includes no production safeguards and should not be deployed.
- For validating the real API against its spec, use the e-openapi skill.
- For generating contract tests that verify real API compliance, use the e-contract skill.
- Mock data is deterministic by default (fixed seed). This ensures consistent behavior across development sessions. Add a random seed option for fuzz-style testing.

## Related Skills

- **e-openapi** (eskill-api): Run e-openapi before this skill to ensure the API spec used for mock generation is valid.
- **e-contract** (eskill-api): Follow up with e-contract after this skill to verify mocks match the actual API contracts.
