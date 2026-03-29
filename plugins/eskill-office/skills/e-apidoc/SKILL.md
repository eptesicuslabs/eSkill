---
name: e-apidoc
description: "Generates API documentation in OpenAPI format from code analysis of routes, types, and middleware. Use when documenting REST APIs, generating specs for clients, or creating API references. Also applies when: 'document this API', 'generate OpenAPI spec', 'create API docs', 'Swagger from code'."
---

# API Documentation Generator

This skill generates OpenAPI 3.1 specifications from source code analysis by extracting route definitions, request/response types, middleware chains, and validation schemas. It produces a complete API specification document suitable for client generation, interactive documentation, and contract testing.

## Prerequisites

Confirm the API framework in use and the desired output format (OpenAPI 3.1 JSON or YAML). Identify the base path or prefix for the API routes. If the project already has a partial OpenAPI spec, locate it for merging.

## Step 1: Detect API Framework

Use `ast_search` and `lsp_symbols` to identify the web framework and routing approach.

| Framework | Detection Pattern | Route Definition Style |
|-----------|------------------|----------------------|
| Express.js | `require('express')`, `import express` | `app.get('/path', handler)`, `router.post(...)` |
| Fastify | `require('fastify')`, `import fastify` | `fastify.get('/path', opts, handler)` |
| Koa | `require('koa')`, `import Koa` | `router.get('/path', handler)` via koa-router |
| Hono | `import { Hono }` | `app.get('/path', handler)` |
| NestJS | `@Controller()`, `@Module()` | `@Get('/path')`, `@Post('/path')` decorators |
| Django REST | `rest_framework` imports | `urlpatterns`, `@api_view`, `ViewSet` |
| FastAPI | `from fastapi import` | `@app.get('/path')`, type-annotated parameters |
| Flask | `from flask import` | `@app.route('/path', methods=[...])` |
| Spring Boot | `@RestController`, `@RequestMapping` | `@GetMapping`, `@PostMapping` annotations |
| Go net/http | `http.HandleFunc`, `mux.HandleFunc` | `HandleFunc("/path", handler)` |
| Gin | `gin.Default()`, `gin.New()` | `r.GET("/path", handler)` |
| ASP.NET | `[ApiController]`, `[Route]` | `[HttpGet]`, `[HttpPost]` attributes |
| Actix-web | `use actix_web` | `#[get("/path")]`, `web::resource` |
| Axum | `use axum` | `Router::new().route("/path", get(handler))` |

Read the main application entry point and routing configuration files with `data_file_read` to understand the routing structure.

## Step 2: Extract Route Definitions

Use `ast_search` to find all route registration patterns for the detected framework.

For each route, extract:

1. **HTTP method**: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS.
2. **Path**: The URL pattern including path parameters (e.g., `/users/:id`, `/users/{id}`).
3. **Handler function**: The function or method that processes the request.
4. **Middleware chain**: Authentication, authorization, validation, rate limiting middleware applied to this route.
5. **Route metadata**: Any descriptions, tags, or documentation annotations on the route.

Organize routes by resource (group routes that share a path prefix). For example, `/users`, `/users/:id`, `/users/:id/posts` all belong to the Users resource.

Use `lsp_symbols` to resolve handler function locations when the handler is defined in a separate file.

Record each route in a working list:

| Method | Path | Handler | Middleware | File |
|--------|------|---------|------------|------|
| GET | /users | listUsers | auth, paginate | routes/users.ts:15 |
| POST | /users | createUser | auth, validate | routes/users.ts:32 |
| GET | /users/:id | getUser | auth | routes/users.ts:48 |

## Step 3: Extract Request Schemas

For each route, determine the request format by analyzing the handler and validation middleware.

**Path parameters**:
- Extract parameter names from the route path (`:id`, `{id}`).
- Use `lsp_references` to find where the parameter is used in the handler to infer its type (string, integer, UUID).

**Query parameters**:
- Search the handler body for query parameter access (`req.query`, `request.args`, `@Query()` decorators).
- Extract parameter names, types, and whether they are required or optional.

**Request body**:
- Check for body parsing middleware or decorators (`@Body()`, `request.json`, `req.body`).
- Use `ast_search` to find the validation schema applied to the request:
  - Zod schemas: `z.object({ ... })` definitions.
  - Joi schemas: `Joi.object({ ... })` definitions.
  - Pydantic models: class definitions extending `BaseModel`.
  - TypeScript interfaces or types used as generic parameters.
  - JSON Schema definitions.
  - Jakarta validation annotations (`@NotNull`, `@Size`, `@Pattern`).
- Convert the validation schema to an OpenAPI schema object.

**Request headers**:
- Check for custom header requirements (API version headers, content negotiation, correlation IDs).
- Note standard headers that affect behavior (Accept, Content-Type, Authorization).

For frameworks with built-in schema support (FastAPI, NestJS with Swagger), extract the schemas directly from the framework's metadata.

## Step 4: Extract Response Schemas

For each route, determine the response format.

**From return types**:
- In TypeScript/NestJS: examine the return type annotation of the handler function.
- In FastAPI: examine the `response_model` parameter and return type annotation.
- In Spring: examine the `ResponseEntity<T>` generic type parameter.
- Use `lsp_symbols` to resolve type definitions to their full schema.

**From response construction**:
- Search the handler body for response construction patterns (`res.json()`, `Response()`, `ResponseEntity.ok()`).
- Analyze the object structure passed to the response.

**Status codes**:
- Extract explicit status code settings (`res.status(201)`, `status_code=201`, `@HttpCode(201)`).
- Infer common status codes from the route method:
  - GET: 200, 404
  - POST: 201, 400, 409
  - PUT/PATCH: 200, 400, 404
  - DELETE: 204, 404

**Error responses**:
- Check for error handling middleware that produces standard error formats.
- Search for thrown HTTP exceptions and their status codes.
- Document the common error response schema.

For each response, build an OpenAPI response object with status code, description, and schema.

## Step 5: Document Authentication and Authorization

Analyze the authentication middleware to define OpenAPI security schemes.

| Auth Pattern | OpenAPI Security Scheme |
|-------------|----------------------|
| Bearer token (JWT) | `bearerAuth` with `type: http`, `scheme: bearer`, `bearerFormat: JWT` |
| API key in header | `apiKeyAuth` with `type: apiKey`, `in: header`, `name: X-API-Key` |
| API key in query | `apiKeyAuth` with `type: apiKey`, `in: query`, `name: api_key` |
| Basic auth | `basicAuth` with `type: http`, `scheme: basic` |
| OAuth2 | `oauth2` with flows, authorization URL, token URL, scopes |
| Cookie session | `cookieAuth` with `type: apiKey`, `in: cookie`, `name: session` |

For each route, record which security scheme applies based on the middleware chain. Routes without authentication middleware should be marked with an empty security requirement (public endpoint).

If OAuth2 scopes are used, extract scope definitions from the authorization middleware and document them.

## Step 6: Extract Additional Metadata

Gather supplementary information for the OpenAPI spec.

**API versioning**:
- Check for version prefixes in routes (`/v1/`, `/v2/`).
- Check for version headers (`Accept-Version`, custom headers).
- Check for URL parameter versioning.

**Rate limiting**:
- If rate limiting middleware is present, document the limits as `x-ratelimit` extensions or in the operation description.
- Extract rate limit configuration (requests per window, window duration).

**Pagination**:
- Detect pagination patterns (limit/offset, cursor-based, page/size).
- Document pagination query parameters and response envelope structure.

**CORS configuration**:
- Read CORS middleware configuration for allowed origins, methods, and headers.

**Tags and grouping**:
- Group operations by resource or controller.
- Use controller names, route prefixes, or decorator-defined tags as OpenAPI tags.

## Step 7: Build OpenAPI Specification

Assemble all extracted data into a valid OpenAPI 3.1 document.

Structure:

```yaml
openapi: "3.1.0"
info:
  title: <project name> API
  version: <project version>
  description: <extracted or user-provided>
servers:
  - url: <base URL>
    description: <environment>
paths:
  /resource:
    get:
      summary: <derived from handler name>
      operationId: <handler function name>
      tags: [<resource group>]
      security: [<applicable scheme>]
      parameters: [<query and path params>]
      responses:
        "200":
          description: <success description>
          content:
            application/json:
              schema: <response schema>
        "400":
          description: Validation error
          content:
            application/json:
              schema: <error schema>
components:
  schemas: <all extracted types>
  securitySchemes: <auth configurations>
```

Use `filesystem` to write the specification file. Default output: `openapi.yaml` or `openapi.json` in the project root.

## Step 8: Validate the Specification

After generation, validate the OpenAPI document for correctness.

Perform these checks:

1. **Structural validity**: All required fields present per the OpenAPI 3.1 specification.
2. **Reference resolution**: All `$ref` pointers resolve to existing components.
3. **Schema completeness**: No `{}` empty schemas for request or response bodies.
4. **Path parameter consistency**: Every path parameter in the URL has a corresponding parameter definition.
5. **Operation ID uniqueness**: No duplicate `operationId` values.
6. **Response coverage**: Every operation has at least a success response and a common error response.
7. **Security consistency**: Operations referencing security schemes that are defined in components.

Use `shell` to run a spec linter if available (e.g., `npx @redocly/cli lint openapi.yaml`).

Report validation results and fix any issues before finalizing.

## Step 9: Generate Human-Readable Documentation

Alongside the OpenAPI spec, produce a markdown summary of the API.

```
## API Reference

**Base URL**: <URL>
**Authentication**: <scheme description>
**Version**: <version>

### Endpoints

#### Users

| Method | Path | Summary | Auth |
|--------|------|---------|------|
| GET | /users | List all users | Bearer |
| POST | /users | Create a user | Bearer |
| GET | /users/{id} | Get a user by ID | Bearer |
| PUT | /users/{id} | Update a user | Bearer |
| DELETE | /users/{id} | Delete a user | Bearer |

#### Products

| Method | Path | Summary | Auth |
|--------|------|---------|------|
| GET | /products | List products | Public |
| GET | /products/{id} | Get a product | Public |

### Common Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Validation error |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not found |
| 500 | Internal server error |

### Models

<schema descriptions for key request/response types>
```

## Step 10: Present Results and Next Steps

Provide the user with:

1. The generated OpenAPI specification file path.
2. The API summary with endpoint count, schema count, and coverage statistics.
3. Any routes that could not be fully documented (missing types, unresolvable handlers).
4. Recommendations for improving API documentation:
   - Adding JSDoc/docstring comments to handlers.
   - Using validation libraries with schema extraction support.
   - Adding response type annotations.

Suggest next steps:
- Generate client SDKs using `openapi-generator` or `openapi-typescript`.
- Set up interactive documentation with Swagger UI or Redoc.
- Integrate spec validation into CI to prevent documentation drift.

## Edge Cases

- **GraphQL APIs**: This skill focuses on REST APIs. For GraphQL, the schema itself serves as documentation. Note that a separate skill or tool (like GraphQL introspection) is more appropriate.
- **gRPC APIs**: For gRPC services, `.proto` files are the source of truth. Extract service definitions from proto files rather than code if the project uses gRPC.
- **Mixed API styles**: Some projects expose both REST and WebSocket endpoints. Document REST endpoints in the OpenAPI spec and note WebSocket endpoints separately, as OpenAPI has limited WebSocket support.
- **Code-first vs spec-first**: If the project already has an OpenAPI spec that is manually maintained (spec-first), compare the generated spec against the existing one to find discrepancies rather than overwriting it.
- **Internal vs public APIs**: Ask whether the documentation is for internal or public consumers. Internal APIs may document all endpoints; public APIs may need to exclude admin or internal-only routes.
- **Versioned APIs**: If the API has multiple versions, generate a separate spec per version or use OpenAPI's path-level organization.

## Related Skills

- **e-surface** (eskill-coding): Run e-surface before this skill to identify all API endpoints that need documentation.
- **e-openapi** (eskill-api): Follow up with e-openapi after this skill to verify generated docs conform to OpenAPI standards.
