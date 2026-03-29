---
name: e-init
description: "Initializes new projects with directory structure, configs, license, git setup, and toolchain for Node.js, Python, Rust, or Go. Use when starting a new project or bootstrapping a repository from scratch. Also applies when: scaffold a project, create a new repo, init a new app, set up project boilerplate."
---

# Project Scaffold

Initialize a new project with a complete, opinionated directory structure, configuration files, and development toolchain. This skill produces production-ready project scaffolds that follow community conventions for the chosen language and framework.

## Prerequisites

Before scaffolding, gather the following from the user:

- **Language**: Node.js, Python, Rust, or Go
- **Framework** (optional): Express, Fastify, FastAPI, Flask, Actix, Gin, etc.
- **Purpose**: library, CLI tool, web application, or API service
- **Project name**: valid package/crate/module name
- **Description**: one-line summary of the project
- **License**: MIT by default, or another SPDX identifier
- **Target directory**: where to create the project (defaults to current working directory)

If the user does not specify all parameters, use sensible defaults and inform them of the choices made.

## Step 1: Determine Project Type

Parse the user's input to identify the language, framework, and purpose. Validate that the combination is coherent (e.g., do not pair Express with Python). If ambiguous, ask for clarification before proceeding.

Set internal variables for the scaffold:

- `lang`: one of `node`, `python`, `rust`, `go`
- `framework`: the specific framework or `none`
- `purpose`: one of `library`, `cli`, `webapp`, `api`
- `project_name`: sanitized name suitable for the package manager
- `project_dir`: absolute path using forward slashes

## Step 2: Create Directory Structure

Use the filesystem eMCP tools (`create_directory`) to build the directory tree. The structure depends on the language:

### Node.js

```
<project_dir>/
  src/
    index.ts (or index.js)
  test/
    index.test.ts
  scripts/
  .github/
    workflows/
  dist/           (in .gitignore)
```

### Python

```
<project_dir>/
  src/
    <package_name>/
      __init__.py
      main.py
  tests/
    __init__.py
    test_main.py
  scripts/
  .github/
    workflows/
```

### Rust

```
<project_dir>/
  src/
    main.rs (for cli/webapp/api) or lib.rs (for library)
  tests/
    integration_test.rs
  benches/
    benchmark.rs
  examples/
```

### Go

```
<project_dir>/
  cmd/
    <project_name>/
      main.go
  internal/
  pkg/
  test/
  .github/
    workflows/
```

Create all directories using `create_directory`. Then create placeholder source files using `fs_write` with minimal but functional content. Each source file should contain a basic hello-world or library stub appropriate to the purpose.

## Step 3: Generate Configuration Files

### Package Manifest

Use `fs_write` to create the appropriate manifest:

- **Node.js** (`package.json`): name, version "0.1.0", description, main/types entry points, scripts (build, test, lint, format), devDependencies (typescript, vitest or jest, eslint, prettier), engine requirements
- **Python** (`pyproject.toml`): project metadata, build-system (setuptools or hatchling), optional-dependencies for dev (pytest, flake8, black, mypy), scripts entry points
- **Rust** (`Cargo.toml`): package metadata, edition "2021", dependencies section, dev-dependencies (criterion for benchmarks), binary or library target
- **Go** (`go.mod`): module path, go version, require section

### TypeScript Configuration (Node.js only)

Create `tsconfig.json` with:
- target: ES2022
- module: NodeNext
- moduleResolution: NodeNext
- outDir: ./dist
- rootDir: ./src
- strict: true
- declaration: true
- sourceMap: true

### Linter Configuration

- **Node.js**: `.eslintrc.json` or `eslint.config.js` with recommended rules, TypeScript parser
- **Python**: `pyproject.toml` [tool.flake8] section or `.flake8` with max-line-length 100, standard ignores
- **Rust**: `clippy.toml` or rely on default clippy settings, add `#![warn(clippy::all)]` to source
- **Go**: rely on `go vet` and `golangci-lint` config (`.golangci.yml`)

### Formatter Configuration

- **Node.js**: `.prettierrc` with printWidth 100, singleQuote true, trailingComma "all"
- **Python**: `pyproject.toml` [tool.black] section with line-length 100
- **Rust**: `rustfmt.toml` with max_width 100, edition 2021
- **Go**: `gofmt` is standard, no config needed

### Editor Configuration

Create `.editorconfig` with:
```
root = true

[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.{py,rs,go}]
indent_size = 4

[Makefile]
indent_style = tab
```

### Git Ignore

Create `.gitignore` with language-appropriate patterns:

- **Node.js**: node_modules/, dist/, .env, *.log, coverage/, .DS_Store
- **Python**: __pycache__/, *.pyc, .venv/, dist/, *.egg-info/, .env, .mypy_cache/, .pytest_cache/
- **Rust**: target/, Cargo.lock (for libraries only), *.swp
- **Go**: bin/, *.exe, *.test, vendor/ (if not vendoring), .env

## Step 4: Create LICENSE File

Use `fs_write` to create a LICENSE file. Default to MIT license. Replace the year with the current year and the copyright holder with "Eptesicus Laboratories" unless the user specifies otherwise.

If the user requests a different license (Apache-2.0, ISC, BSD-2-Clause, etc.), generate the appropriate full license text.

## Step 5: Create README.md

Generate a README.md with the following sections:

```markdown
# <project_name>

<description>

## Installation

<language-appropriate installation instructions>

## Usage

<basic usage example>

## Development

<how to build, test, lint, and format>

## License

<license type> - see [LICENSE](LICENSE) for details.
```

Populate each section with concrete instructions based on the language and framework. For example, Node.js projects should reference `npm install` and `npm test`.

## Step 6: Create Project Convention File

Generate a project convention file (e.g., `PROJECT.md` or `CONVENTIONS.md`) documenting the tech stack and development commands:

```markdown
# Project Conventions

## Overview

<project_name>: <description>

## Tech Stack

- Language: <language and version>
- Framework: <framework> (if applicable)
- Package Manager: <npm/pip/cargo/go>
- Test Framework: <vitest/pytest/cargo test/go test>

## Conventions

- Source code lives in src/
- Tests mirror source structure in test(s)/
- Use <formatter> for formatting
- Use <linter> for linting
- Follow conventional commits for git messages

## Commands

- Build: <build command>
- Test: <test command>
- Lint: <lint command>
- Format: <format command>
```

## Step 7: Initialize Git Repository

Use the git eMCP tools:

1. Run `git_init` to initialize the repository
2. Run `git_add` to stage all created files
3. Run `git_commit` with the message "Initial project scaffold" and description "Generated by eskill-meta e-init"

If the target directory is already a git repository, skip initialization and inform the user. Do not overwrite existing git history.

## Step 8: Set Up Test Infrastructure

Create a test configuration file and an example test:

- **Node.js**: `vitest.config.ts` (or `jest.config.ts`) with basic configuration, plus `test/index.test.ts` with a passing placeholder test
- **Python**: `pyproject.toml` [tool.pytest.ini_options] section with testpaths and standard options, plus `tests/test_main.py` with a passing placeholder test
- **Rust**: Tests are built in. Ensure `tests/integration_test.rs` has a `#[test]` function that passes
- **Go**: Create `test/<package>_test.go` or `cmd/<name>/main_test.go` with a passing `TestMain` function

Run the test suite using `test_run` to confirm everything passes. If tests fail, diagnose and fix before completing.

## Step 9: Validate the Scaffold

Perform a final validation pass:

1. Use `fs_list` to verify all expected files and directories exist
2. Run `git_status` to confirm the working tree is clean after the initial commit
3. Verify key files are non-empty: package manifest, main source file, test file, README, LICENSE
4. Report the scaffold summary to the user:
   - Project location
   - Language and framework
   - Files created (count and list)
   - Next steps (e.g., "Run `npm install` to install dependencies")

## Templates and Defaults

When no framework is specified, use these defaults:

| Language | Default Test | Default Lint | Default Format |
|----------|-------------|-------------|----------------|
| Node.js  | vitest      | eslint      | prettier       |
| Python   | pytest      | flake8      | black          |
| Rust     | cargo test  | clippy      | rustfmt        |
| Go       | go test     | go vet      | gofmt          |

When generating source files, always include:
- A brief module-level comment explaining the file's purpose
- Proper imports/use statements
- A main function (for CLI/webapp/api) or a public function (for library)
- An associated test that exercises the basic functionality

## Safety Protocol

1. Before creating any files, present the complete directory structure and file list to the user for confirmation.
2. Maintain a manifest of all created files and directories during scaffolding.
3. If the user wants to undo the scaffold, present the manifest and ask for confirmation before deleting.
4. Never overwrite existing files without explicit user approval. If a target file already exists, report the conflict and ask whether to skip, overwrite, or merge.
5. After scaffolding, report the complete list of files created so the user has a record.

## Error Handling

If any step fails:
- Report the specific error to the user
- Do not leave a partially-created scaffold without informing the user
- Offer to clean up partial artifacts or continue from the point of failure
- Never silently skip a step

## Edge Cases

- **Non-empty target directory**: If the target directory already contains files, scaffolding may conflict with existing content. Detect existing files and offer to skip, merge, or abort.
- **Monorepo package initialization**: Initializing a new package inside a monorepo requires respecting the workspace configuration (pnpm-workspace.yaml, lerna.json, Cargo workspace). Detect the parent workspace and add the new package to it.
- **Offline initialization**: When npm/pip/cargo registries are unreachable, dependency installation fails. Create the scaffold files first and defer dependency installation with clear instructions for when connectivity is restored.
- **Multiple language scaffolds**: The user may want both a Python backend and a Node.js frontend in the same project. Detect the request and scaffold each in a subdirectory with separate manifests.
- **License selection uncertainty**: When the user does not specify a license, do not default to a permissive license without asking. Present the most common options (MIT, Apache 2.0, GPL 3.0) and wait for selection.

## Related Skills

- **e-ci** (eskill-devops): Follow up with e-ci after this skill to set up CI/CD pipelines for the new project.
- **e-health** (eskill-meta): Follow up with e-health after this skill to establish baseline health metrics for the new project.
