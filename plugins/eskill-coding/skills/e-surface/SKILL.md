---
name: e-surface
description: "Extracts the public API surface including exports and HTTP routes. Use when documenting a library's interface, checking for breaking changes, or mapping module boundaries. Also applies when: 'map the API', 'list all exported functions', 'what endpoints does this expose', 'show public interface'."
---

# API Surface Map

This skill extracts the public-facing API of a codebase and produces structured documentation. It covers both programmatic APIs (exported functions, classes, types) and HTTP APIs (route endpoints).

## Prerequisites

- A codebase with identifiable public modules or entry points.
- LSP server running for the project language (recommended).

## Workflow

### Step 1: Identify Entry Points

Determine where the public API surface begins. Entry points vary by project type:

**Libraries and packages**:
- Check `package.json` `main`, `module`, and `exports` fields for Node.js.
- Check `pyproject.toml` `[project.scripts]` and `[project.entry-points]` for Python.
- Check `Cargo.toml` `[lib]` section for Rust.
- Check `src/index.*` or `src/lib.*` files as common conventions.

**HTTP services**:
- Look for route registration files (e.g., `routes/`, `api/`, `controllers/`).
- Check the application entry point for middleware and route mounting.

**Monorepos**:
- Identify each package or workspace member.
- Map each package's entry point separately.

Use `fs_list` and `fs_search` to locate these files and `data_file_read` to parse manifest contents. For large codebases, use `egrep_search` from the eMCP egrep server to quickly find export statements (`export`, `module.exports`, `pub fn`, `__all__`) across all source files.

### Step 2: Extract Exported Symbols with LSP

For each entry point module, use `lsp_symbols` from the eMCP LSP server to get all symbols:

- Filter for exported symbols only. Exclude private/internal symbols.
- Record each symbol's kind: function, class, interface, type, constant, enum.
- For re-exported symbols, trace back to the original definition module.

Process the module dependency tree breadth-first from each entry point. For each module that is exported or re-exported, repeat the symbol extraction.

### Step 3: Extract Signatures with AST

Use `ast_search` from the eMCP AST server to get detailed type information for each exported symbol:

**Functions**:
```
- Name
- Parameters: name, type, default value, optional flag
- Return type
- Async flag
- Generic type parameters
```

**Classes**:
```
- Name
- Constructor parameters
- Public methods (with signatures as above)
- Public properties: name, type, readonly flag
- Static members
- Generic type parameters
- Extends/implements
```

**Interfaces and types**:
```
- Name
- Properties: name, type, optional flag
- Method signatures
- Generic type parameters
- Extends
```

**Constants and enums**:
```
- Name
- Type
- Value (for constants)
- Members (for enums)
```

### Step 4: Extract HTTP API Routes

For HTTP services, search for route definitions using `egrep_search` for a fast initial pass to locate files containing route registration patterns, then `ast_search` for structured extraction specific to the framework:

| Framework      | Pattern to Search                                    |
|----------------|------------------------------------------------------|
| Express        | `app.get`, `app.post`, `router.get`, `router.post`  |
| Fastify        | `fastify.get`, `fastify.route`                       |
| Koa            | `router.get`, `router.post`                          |
| FastAPI        | `@app.get`, `@app.post`, `@router.get`               |
| Flask          | `@app.route`, `@blueprint.route`                     |
| Django         | `path()`, `re_path()` in `urls.py`                   |
| Spring         | `@GetMapping`, `@PostMapping`, `@RequestMapping`     |
| Rails          | `get`, `post`, `resources` in `routes.rb`            |
| Gin (Go)       | `r.GET`, `r.POST`, `group.GET`                       |
| Actix (Rust)   | `web::get()`, `web::post()`, `#[get]`, `#[post]`    |

For each route, extract:
- HTTP method (GET, POST, PUT, DELETE, PATCH).
- Path pattern (including path parameters).
- Handler function reference.
- Middleware applied to the route.
- Request body type (if definable from the handler signature).
- Response type (if determinable).

### Step 5: Build the Structured Map

Organize the extracted information into a hierarchical structure:

```
Project
  Module A
    Function: doSomething(input: string): Promise<Result>
    Class: Processor
      constructor(config: Config)
      method: process(data: Buffer): Output
      method: reset(): void
    Type: Config
      property: timeout (number)
      property: retries (number, optional)
  Module B
    Function: validate(schema: Schema, data: unknown): ValidationResult
    Constant: VERSION (string)
  HTTP API
    GET /api/v1/users
      handler: getUsers
      middleware: [auth, rateLimit]
      response: User[]
    POST /api/v1/users
      handler: createUser
      middleware: [auth, rateLimit]
      body: CreateUserRequest
      response: User
```

### Step 6: Identify Documentation Gaps

For each exported symbol, check whether documentation exists:

- **JSDoc/TSDoc**: Search for `/** ... */` comment blocks immediately preceding the symbol.
- **Python docstrings**: Search for triple-quoted strings as the first statement in functions/classes.
- **Rust doc comments**: Search for `///` or `//!` comments preceding items.
- **Go doc comments**: Search for comments immediately preceding exported identifiers.

Mark each symbol as:
- **Documented**: Has a doc comment with a description.
- **Partially documented**: Has a doc comment but missing parameter or return descriptions.
- **Undocumented**: No doc comment found.

Include documentation coverage statistics in the output.

### Step 7: Output as Structured Documentation

Generate the API surface map as markdown with a table of contents:

```markdown
# API Surface Map

## Table of Contents
- [Module: auth](#module-auth)
- [Module: data](#module-data)
- [HTTP API](#http-api)

---

## Module: auth

### Functions

#### `authenticate(credentials: Credentials): Promise<Token>`

Authenticates a user and returns a session token.

- **Parameters**:
  - `credentials` (Credentials) -- The user's login credentials.
- **Returns**: `Promise<Token>` -- A session token on success.
- **Throws**: `AuthError` -- If credentials are invalid.
- **Documentation**: Fully documented.

#### `refreshToken(token: Token): Promise<Token>`

- **Parameters**:
  - `token` (Token) -- The current session token.
- **Returns**: `Promise<Token>` -- A new session token.
- **Documentation**: Undocumented.

### Classes

#### `SessionManager`

Manages active user sessions.

- **Constructor**: `new SessionManager(store: SessionStore)`
- **Methods**:
  - `create(userId: string): Session` -- Creates a new session.
  - `destroy(sessionId: string): void` -- Destroys an active session.
  - `get(sessionId: string): Session | null` -- Retrieves a session.
- **Documentation**: Partially documented (missing method descriptions).

---

## HTTP API

### GET /api/v1/users

Retrieves a list of users.

- **Middleware**: auth, rateLimit
- **Query Parameters**: `page` (number), `limit` (number)
- **Response**: `200 OK` -- `User[]`
- **Handler**: `src/routes/users.ts:getUsers`

[... additional endpoints ...]

---

## Coverage Summary

| Category        | Documented | Partial | Undocumented | Total |
|-----------------|------------|---------|--------------|-------|
| Functions       | 12         | 3       | 5            | 20    |
| Classes         | 4          | 2       | 1            | 7     |
| Types           | 8          | 0       | 3            | 11    |
| HTTP Endpoints  | 10         | 2       | 0            | 12    |
```

## Notes

- This skill produces a snapshot of the current API surface. It does not track changes over time. Use the e-version skill for API change tracking and breaking-change analysis.
- For large codebases, the user may request a map of a specific module or directory rather than the entire project.
- The output format can be adapted: markdown (default), JSON (for tooling consumption), or OpenAPI spec (for HTTP APIs).

## Edge Cases

- **Re-exports through barrel files**: A symbol exported from module A and re-exported through index.ts appears at two paths. Deduplicate by tracking the original definition location.
- **Express router middleware stacks**: Routes defined via `router.use()` apply middleware to multiple endpoints. Trace the middleware chain to accurately report which middleware applies to which route.
- **Dynamically registered routes**: Frameworks like Fastify plugins or Django URL patterns may register routes at runtime. These cannot be statically extracted. Report detected dynamic registration patterns as coverage gaps.
- **TypeScript declaration files without implementation**: `.d.ts` files declare types but contain no runtime code. Include them in the surface map for type exports but flag that no implementation exists in the project.
- **Internal exports consumed only within the package**: Not all exports are part of the public API. Distinguish between exports consumed externally and those used only for internal module composition.

## Related Skills

- **e-apidoc** (eskill-office): Follow up with e-apidoc after this skill to produce documentation from the mapped API surface.
- **e-openapi** (eskill-api): Follow up with e-openapi after this skill to validate that the mapped endpoints conform to their OpenAPI spec.
