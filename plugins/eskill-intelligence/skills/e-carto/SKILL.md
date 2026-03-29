---
name: e-carto
description: "Maps codebase architecture by analyzing file structure, dependencies, and component relationships into a navigable document. Use when documenting architecture or understanding how a project is organized. Also applies when: map this codebase, show me the architecture, how is this project structured."
---

# Codebase Cartography

This skill produces a structured architectural map of a codebase by systematically analyzing its file organization, dependency graphs, abstraction layers, and design patterns. The output is a navigable overview indexed for search and organized via structured reasoning, then rendered as a markdown architecture document.

## Prerequisites

Before starting, confirm the project root directory with the user. All paths in the analysis should be relative to this root.

## Procedure

### Step 1: Scan Project Structure

Use the eMCP filesystem server and trigram-indexed search to obtain the full directory tree and quickly locate key files.

- Call `fs_list` on the project root with a depth limit of 4 to get a manageable overview.
- Call `fs_list` on each top-level directory to enumerate its immediate children.
- Use `egrep_search_files` to locate configuration files by name pattern (e.g., `package.json`, `Cargo.toml`, `docker-compose*`) across the entire tree without manual traversal.
- Use `egrep_search` to scan for monorepo indicators (workspace declarations, lerna references, pnpm-workspace entries) across all config files instantly.
- Record the total file count, directory count, and notable file extensions present.
- Identify directories that are likely generated or vendored (node_modules, vendor, dist, build, __pycache__, .git) and exclude them from further deep analysis.
- Note any monorepo indicators: multiple package.json files, workspace configuration, lerna.json, pnpm-workspace.yaml, or Cargo workspace members.

### Step 2: Identify Project Type

Read configuration files to determine the language, framework, and build system. Use `markdown_front_matter` to parse any YAML frontmatter in documentation or configuration markdown files that describe the project setup.

- Use `data_file_read` on the following files if they exist:
  - package.json (Node.js/JavaScript/TypeScript)
  - pyproject.toml or setup.py or setup.cfg (Python)
  - Cargo.toml (Rust)
  - go.mod (Go)
  - pom.xml or build.gradle (Java/Kotlin)
  - Gemfile (Ruby)
  - composer.json (PHP)
  - *.csproj or *.sln (C#/.NET)
- Extract: project name, version, declared dependencies, scripts/tasks, and build configuration.
- Identify the primary language and any secondary languages in use.
- Detect the framework: React, Angular, Vue, Django, Flask, FastAPI, Spring, Rails, Express, Next.js, Nuxt, ASP.NET, Actix, Axum, and others.
- Detect the build system: webpack, vite, esbuild, setuptools, poetry, cargo, make, cmake, gradle, maven, msbuild.
- Detect testing frameworks: jest, pytest, cargo test, junit, rspec, phpunit, xunit.
- Detect linters and formatters: eslint, prettier, ruff, black, clippy, rustfmt, checkstyle.

### Step 3: Map Entry Points

Locate the files where execution begins or where the public API surface is defined.

- Look for main files: main.ts, main.py, main.rs, main.go, Main.java, index.ts, index.js, app.py, server.py, Program.cs.
- Look for route definitions: files in routes/ or controllers/ directories, or files containing route decorator patterns.
- Look for exported modules: index files that re-export from submodules, __init__.py files with __all__ definitions, mod.rs files with pub mod declarations.
- Look for CLI entry points: bin/ directories, console_scripts in pyproject.toml, bin field in package.json.
- Look for configuration entry points: webpack.config.js, vite.config.ts, docker-compose.yml, Dockerfile, terraform main.tf.
- Record each entry point with its type (application, library, CLI, configuration) and a brief description of its purpose.

### Step 4: Trace Import and Dependency Graphs

Use AST analysis and trigram-indexed code search to understand how modules depend on each other.

- Use `egrep_search` for fast initial sweeps: find all import/require/use statements across the codebase in seconds rather than walking files individually. This is especially effective for large codebases where `ast_search` on every file would be slow.
- Use `ast_search` for detailed, language-aware import analysis in the primary language:
  - JavaScript/TypeScript: import declarations, require calls, dynamic import() expressions.
  - Python: import statements, from...import statements.
  - Rust: use declarations, mod declarations, extern crate.
  - Go: import blocks.
  - Java/Kotlin: import statements.
- For each source file, record which other project modules it imports (exclude external dependencies).
- Build a directed dependency graph: nodes are modules/files, edges are import relationships.
- Identify hub modules: files imported by many others (high in-degree). These are core abstractions.
- Identify leaf modules: files that import others but are not imported themselves. These are typically entry points or endpoints.
- Identify circular dependencies: modules that directly or transitively import each other. Flag these as architectural concerns.
- Record the fan-in (number of importers) and fan-out (number of imports) for each module.

### Step 5: Extract Key Abstractions

Use LSP analysis to find the important types, classes, and interfaces.

- Use `lsp_symbols` to extract symbol definitions from key files identified in previous steps.
- Focus on: classes, interfaces, type aliases, enums, traits, structs, and function signatures of exported functions.
- For each abstraction, record: name, kind (class, interface, type, enum), file location, and a brief inferred purpose based on naming.
- Group abstractions by module or directory.
- Identify the domain model: classes or types that represent business entities (often found in models/, entities/, domain/, types/ directories).
- Identify service abstractions: classes or interfaces that define operations (often found in services/, usecases/, handlers/ directories).
- Identify data transfer objects: types used for API input/output (often found in dto/, schemas/, api/ directories).

### Step 6: Identify Architectural Layers

Classify directories and modules into architectural layers.

Apply the following heuristics:

**Presentation Layer** (how the system communicates with the outside world):
- Directories named: routes, controllers, handlers, views, pages, components, screens, api, endpoints, graphql, grpc.
- Files containing HTTP handler functions, route definitions, UI components, or CLI command definitions.

**Business Logic Layer** (what the system does):
- Directories named: services, usecases, domain, core, logic, engine, rules, workflows.
- Files containing business rules, validation logic, orchestration between data sources, or domain-specific computations.

**Data Access Layer** (how the system persists and retrieves data):
- Directories named: repositories, dal, database, db, store, persistence, models (when containing ORM definitions), migrations.
- Files containing database queries, ORM model definitions, cache access, or external service clients.

**Infrastructure Layer** (operational concerns):
- Directories named: infrastructure, infra, config, middleware, plugins, providers, adapters, external.
- Files containing logging setup, authentication middleware, configuration loading, message queue integration, or third-party service wrappers.

**Shared/Common Layer** (utilities used across layers):
- Directories named: shared, common, utils, helpers, lib, pkg, internal.
- Files containing general-purpose utilities, type definitions, constants, or error types.

For each identified layer, record: the directories that belong to it, the key files, and a confidence assessment of the classification.

### Step 7: Map Cross-Cutting Concerns

Identify how the codebase handles concerns that span multiple layers.

- **Logging**: Search for logging framework usage (console.log, logger, logging, log crate, slog, tracing). Note whether structured logging is used. Identify the logging configuration.
- **Authentication and Authorization**: Search for auth-related middleware, JWT handling, session management, role checks, permission decorators.
- **Error Handling**: Identify the error handling strategy. Look for global error handlers, custom error types, Result/Either patterns, try-catch boundaries.
- **Configuration**: Identify how configuration is loaded. Look for .env files, config/ directories, environment variable access patterns, configuration validation.
- **Validation**: Search for input validation patterns. Look for validation libraries (joi, zod, pydantic, validator), custom validation decorators, or validation middleware.
- **Serialization**: Identify how data is serialized and deserialized. Look for JSON handling, protobuf definitions, XML parsing, custom serializers.

Record each cross-cutting concern with: how it is implemented, which files are involved, and whether the approach is consistent across the codebase.

### Step 8: Detect Architectural Patterns

Based on the analysis so far, identify the dominant architectural pattern.

- **MVC (Model-View-Controller)**: Separate models, views/templates, and controllers directories. Common in Rails, Django, Spring MVC, ASP.NET MVC.
- **Layered/N-Tier**: Clear separation into presentation, business, and data layers with one-directional dependencies.
- **Hexagonal (Ports and Adapters)**: Core domain with no external dependencies, ports (interfaces) for external communication, adapters implementing those ports.
- **Clean Architecture**: Similar to hexagonal but with explicit use case layer. Dependency rule: inner layers do not depend on outer layers.
- **Event-Driven**: Presence of event bus, message queue integration, event handlers, pub/sub patterns.
- **Microservices**: Multiple independently deployable services, each with its own data store, communicating via API or messages.
- **Monolith**: Single deployable unit containing all functionality. Check whether it is a well-structured modular monolith or a tangled "big ball of mud."
- **CQRS (Command Query Responsibility Segregation)**: Separate read and write models, different handlers for commands and queries.
- **Serverless**: Functions as deployment units, event triggers, cloud function configuration files.

Record the detected pattern with confidence level and supporting evidence.

### Step 9: Store Findings in Docs and Reasoning

Persist the architectural knowledge using the eMCP docs and reasoning servers for future querying.

**Check existing indexed libraries** using `docs_list_libraries`:
- Before indexing, call `docs_list_libraries` to see what documentation is already indexed. Avoid re-indexing content that is already present and current.

**Index in docs server** using `docs_index`:
- Index the generated architecture document so its contents are searchable via `docs_search`.
- Include the project overview, module map, layer organization, and dependency graph as indexed content.

**Build reasoning chains** using the eMCP reasoning server:
- Call `think_start` to create a reasoning chain for the architectural analysis.
- For each significant module or directory, call `think_step` with type="observation" recording: file count, primary purpose, key exports.
- For each architectural layer, call `think_step` with type="observation" recording: directories, confidence, boundary clarity.
- For dependency relationships and cross-cutting concerns, call `think_step` with type="thought" recording connections:
  - "contains": project contains modules, modules contain components.
  - "depends_on": module A depends on module B.
  - "belongs_to_layer": module belongs to a layer.
  - "implements_pattern": project implements an architectural pattern.
  - "handles": concern is handled by specific modules.
- Use `think_step` with evidenceFor/evidenceAgainst links to connect related observations across modules.

### Step 10: Generate Architecture Document

Produce a comprehensive markdown document summarizing the codebase architecture.

The document should include the following sections:

1. **Overview**: Project name, language, framework, build system, and a one-paragraph summary of what the project does.
2. **Project Structure**: A formatted directory tree showing the top-level organization with annotations for each directory's purpose.
3. **Module Map**: A table listing each significant module with its purpose, layer, file count, and key dependencies.
4. **Dependency Graph**: A textual representation of module dependencies. Use indented lists or ASCII art to show the dependency flow. Note any circular dependencies.
5. **Architectural Layers**: A description of each identified layer with its responsibilities, directories, and boundary enforcement.
6. **Key Abstractions**: A catalog of the most important types, classes, and interfaces with their locations and purposes.
7. **Entry Points**: A list of all entry points with their type and description.
8. **Cross-Cutting Concerns**: How each concern is handled across the codebase.
9. **Architectural Pattern**: The detected pattern with evidence and assessment.
10. **Observations and Recommendations**: Any architectural concerns, inconsistencies, or improvement opportunities identified during the analysis.

## Notes

- Adjust depth of analysis based on codebase size. For small projects (under 50 files), analyze all files. For larger projects, focus on the most connected and most imported modules.
- When the project uses a well-known framework, leverage knowledge of that framework's conventional structure to accelerate classification.
- If the codebase lacks clear architectural boundaries, note this as an observation and classify based on the best available evidence.
- Always present findings with confidence levels when classification is uncertain.

## Edge Cases

- **Monorepos with independent packages**: Each package may follow a different architectural pattern. Map each package independently before attempting a cross-package dependency graph.
- **Serverless projects without a clear entry point**: Lambda handlers, Cloud Functions, and similar serverless architectures have many small entry points rather than a single main. Discover all handler exports and map each as a separate entry point.
- **Codebases with no clear layering**: Some projects evolved organically without architectural layers. When no layers can be detected, report the absence and classify by file purpose (routing, data access, utilities) instead.
- **Mixed framework conventions**: A project migrating from one framework to another (e.g., Express to Fastify, Django to FastAPI) may have two directory conventions coexisting. Map both and note the migration boundary.
- **Very large codebases (1000+ files)**: Full file-by-file analysis is impractical. Sample the most-imported and most-edited files (using git log frequency) to build a representative map.

## Related Skills

- **e-diagram** (eskill-office): Follow up with e-diagram after this skill to visualize the mapped codebase structure as diagrams.
- **e-learn** (eskill-intelligence): Follow up with e-learn after this skill to create a guided learning path through the mapped codebase.
