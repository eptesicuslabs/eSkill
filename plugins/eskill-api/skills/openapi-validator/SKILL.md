---
name: openapi-validator
description: "Validates OpenAPI/Swagger specifications for completeness, consistency, and best practices. Use when reviewing API specs, before publishing APIs, or during design reviews. Also applies when: 'validate my OpenAPI spec', 'check swagger file', 'is my API spec complete', 'API documentation review'."
---

# OpenAPI Validator

This skill validates OpenAPI 3.x and Swagger 2.0 specifications against structural rules, completeness requirements, and API design best practices. It produces a severity-graded report of issues found in the specification.

## Prerequisites

- An OpenAPI or Swagger specification file in YAML or JSON format.
- The eMCP filesystem and data_file_read servers available.

## Workflow

### Step 1: Detect Specification Files

Search the project for OpenAPI/Swagger specification files. Use `filesystem` tools to scan for common file names and locations:

| File Pattern             | Format  |
|--------------------------|---------|
| `openapi.yaml`          | YAML    |
| `openapi.json`          | JSON    |
| `swagger.yaml`          | YAML    |
| `swagger.json`          | JSON    |
| `api-spec.yaml`         | YAML    |
| `api/openapi.*`         | Either  |
| `docs/openapi.*`        | Either  |
| `spec/openapi.*`        | Either  |

Also check `package.json` or project configuration files for custom spec paths. Some projects reference the spec location in build or documentation tooling configuration.

If multiple spec files exist, validate each one separately and clearly label results per file.

### Step 2: Parse and Validate Structure

Use `data_file_read` from the eMCP data server to parse the specification file. Verify the top-level structure:

**OpenAPI 3.x required fields**:
- `openapi` -- version string (3.0.x or 3.1.x)
- `info` -- title, version at minimum
- `paths` -- at least one path defined

**Swagger 2.0 required fields**:
- `swagger` -- version string (2.0)
- `info` -- title, version at minimum
- `paths` -- at least one path defined

Check for valid JSON/YAML syntax. Record any parsing errors as critical severity.

Validate that `$ref` references resolve to existing definitions within the spec or in referenced external files. Unresolved references are errors.

### Step 3: Check Response Schema Coverage

For every operation (path + method combination), verify that response schemas are defined:

**Required response definitions**:
- At least one success response (2xx status code).
- A response schema or content type for each defined response.
- The `description` field on every response.

**Recommended response definitions**:
- 400 Bad Request for operations that accept a request body.
- 401 Unauthorized for operations behind authentication.
- 404 Not Found for operations with path parameters.
- 500 Internal Server Error as a catch-all.

Record missing required responses as errors and missing recommended responses as warnings.

Build a coverage table:

| Endpoint            | Method | 2xx | 4xx | 5xx | Schema |
|---------------------|--------|-----|-----|-----|--------|
| /api/users          | GET    | Yes | No  | No  | Yes    |
| /api/users          | POST   | Yes | Yes | No  | Yes    |
| /api/users/{id}     | GET    | Yes | No  | No  | No     |

### Step 4: Verify Error Response Documentation

Check that error responses follow a consistent pattern across the specification:

- All error responses should share a common error schema or reference a shared component.
- Error schemas should include at minimum: a message field, an error code or type field.
- If the spec defines a reusable error component (e.g., `#/components/schemas/Error`), verify all error responses reference it.
- Flag error responses that use ad-hoc inline schemas instead of the shared component.

### Step 5: Check Authentication Definitions

Validate the security configuration:

**OpenAPI 3.x**:
- `components/securitySchemes` defines at least one scheme if any operation uses security.
- Each security scheme has a valid `type` (apiKey, http, oauth2, openIdConnect).
- The global `security` field or per-operation `security` fields reference defined schemes.
- OAuth2 flows include valid authorization and token URLs.
- API key schemes specify `in` (header, query, cookie) and `name`.

**Swagger 2.0**:
- `securityDefinitions` defines schemes.
- Each scheme has a valid `type` (basic, apiKey, oauth2).

Flag operations that have no security requirement and are not explicitly marked as public. These may be unintentional omissions.

### Step 6: Validate Path Parameter Consistency

For every path that contains parameters (e.g., `/users/{id}/orders/{orderId}`):

- Every path parameter placeholder has a corresponding parameter definition with `in: path` and `required: true`.
- Path parameter names are consistent across the spec. For example, if `/users/{userId}` and `/users/{id}` both exist, flag the inconsistency.
- Parameter types are appropriate: path parameters should not be objects or arrays.
- Parameters defined at the path level are not redundantly redefined at the operation level.

Use `ast_search` to cross-reference parameter names in the spec with any corresponding route handler code, verifying that the spec matches the implementation.

### Step 7: Check Naming and Style Conventions

Validate naming consistency across the specification:

| Element        | Convention           | Example                |
|----------------|----------------------|------------------------|
| Paths          | kebab-case           | /user-profiles         |
| Parameters     | camelCase            | userId, pageSize       |
| Schema names   | PascalCase           | UserProfile, OrderItem |
| Properties     | camelCase            | firstName, createdAt   |
| Enum values    | UPPER_SNAKE_CASE     | PENDING, IN_PROGRESS   |

Flag deviations as style warnings. Report the most common convention found in the spec alongside the deviations so the user can decide which convention to standardize on.

### Step 8: Check for Additional Best Practices

Validate the following best practices:

- **Descriptions**: All paths, operations, parameters, and schema properties should have `description` fields. Calculate a description coverage percentage.
- **Examples**: Request bodies and response schemas should include `example` or `examples` fields. These are important for documentation generation and mock servers.
- **Pagination**: List endpoints (GET operations returning arrays) should include pagination parameters (page/limit, offset/limit, or cursor-based).
- **Versioning**: The base path or server URL should include a version indicator (e.g., `/v1/`, `/api/v2/`).
- **Tags**: Operations should be organized with `tags`. Verify no orphan tags exist (defined but unused, or used but undefined).
- **Operation IDs**: Every operation should have a unique `operationId`. Check for duplicates.
- **Deprecated operations**: Deprecated operations should include a description noting what replaces them.

### Step 9: Report Findings by Severity

Produce a structured validation report grouped by severity:

```
## OpenAPI Validation Report

### Spec: api/openapi.yaml
- Version: OpenAPI 3.0.3
- Title: User Management API v2.1.0
- Paths: 14
- Operations: 32
- Schemas: 18

### Critical (must fix)
1. Unresolved $ref: #/components/schemas/UserRole (line 142)
2. Path parameter {orderId} in /orders/{orderId} has no parameter definition

### Error (should fix)
1. GET /users/{id} -- missing success response schema
2. POST /orders -- missing 400 response for request body validation
3. Security scheme "bearerAuth" referenced but not defined

### Warning (consider fixing)
1. GET /users -- list endpoint missing pagination parameters
2. POST /users -- no request body example provided
3. Inconsistent path parameter naming: userId vs id

### Style
1. Path /user_profiles uses snake_case (expected kebab-case)
2. Schema property "first_name" uses snake_case (expected camelCase)

### Summary
| Severity | Count |
|----------|-------|
| Critical | 2     |
| Error    | 3     |
| Warning  | 2     |
| Style    | 2     |

Description coverage: 72% (23/32 operations documented)
Example coverage: 44% (14/32 operations with examples)
```

### Step 10: Cross-Reference Spec Against Implementation

When the project contains both an API specification and route handler code, use `ast_search` and `lsp_symbols` to cross-reference the two:

- For each path defined in the spec, verify that a corresponding route handler exists in the codebase.
- For each route handler in the codebase, verify that a corresponding path exists in the spec.
- Flag endpoints present in code but missing from the spec as undocumented.
- Flag endpoints present in the spec but missing from code as potentially stale.

Present the cross-reference as a table:

| Endpoint            | Method | In Spec | In Code | Status          |
|---------------------|--------|---------|---------|-----------------|
| /api/users          | GET    | Yes     | Yes     | Matched         |
| /api/users          | POST   | Yes     | Yes     | Matched         |
| /api/health         | GET    | No      | Yes     | Undocumented    |
| /api/legacy/export  | GET    | Yes     | No      | Stale in spec   |

This step is informational. Mismatches are reported as warnings, not errors, since the spec may intentionally omit internal endpoints.

## Edge Cases

- **Multi-file specs**: Some projects split specs across multiple files with `$ref` to external documents. Follow external references and validate the resolved spec as a whole.
- **Generated specs**: Specs generated from code annotations (e.g., via swagger-jsdoc or FastAPI) may have systematic gaps. Identify patterns rather than listing every instance.
- **OpenAPI 3.1 vs 3.0**: OpenAPI 3.1 aligns with JSON Schema 2020-12. Validate schema keywords against the correct JSON Schema draft for the spec version.
- **Swagger 2.0 migration**: If a Swagger 2.0 spec is found, note that migration to OpenAPI 3.x is recommended and flag 2.0-specific patterns that have better 3.x alternatives (e.g., `consumes`/`produces` replaced by content negotiation).
- **Empty paths object**: A spec with no paths defined is structurally valid but functionally useless. Flag this as a warning.
- **Conflicting specs**: If both an `openapi.yaml` and `swagger.json` exist, validate each independently and warn that maintaining two specs risks drift. Recommend consolidating to a single OpenAPI 3.x file.

## Notes

- This skill validates the specification document itself, not the running API. To verify that an implementation matches its spec, use the contract-test-generator skill.
- For GraphQL schemas, use the graphql-schema-review skill instead.
- The severity classifications follow a simple rule: critical means the spec is unparseable or unusable, error means a likely bug or omission, warning means a deviation from best practices, style means a naming convention issue.
- To generate mock servers from a validated spec, use the api-mock-generator skill.

## Related Skills

- **api-docs-generator** (eskill-office): Run api-docs-generator before this skill to produce the documentation that validation will check against.
- **contract-test-generator** (eskill-api): Follow up with contract-test-generator after this skill to generate tests that enforce the validated API contracts.
