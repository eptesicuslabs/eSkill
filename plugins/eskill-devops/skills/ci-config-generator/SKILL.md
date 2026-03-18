---
name: ci-config-generator
description: "Generates CI/CD pipeline configurations for GitHub Actions, GitLab CI, or similar platforms based on project structure and detected toolchain. Use when setting up continuous integration for a new project, adding pipeline stages, or migrating between CI platforms."
---

# CI/CD Configuration Generator

This skill produces CI/CD pipeline configuration files tailored to the project's language, framework, build system, and target CI platform. It detects the project toolchain automatically and generates pipeline definitions that include dependency installation, linting, building, testing, security scanning, and deployment stages.

## Step 1: Detect Project Type

Read the project root to identify the primary language and runtime by checking for well-known configuration files.

- Use `data_file_read` on `package.json` to detect a Node.js project. Extract the `engines` field to determine required Node versions.
- Use `data_file_read` on `pyproject.toml` or `setup.cfg` to detect a Python project. Extract the `requires-python` field for version constraints.
- Use `data_file_read` on `Cargo.toml` to detect a Rust project. Read the `edition` field to determine the Rust edition.
- Use `data_file_read` on `go.mod` to detect a Go project. Read the `go` directive for the minimum Go version.
- Use `data_file_read` on `pom.xml` or `build.gradle` to detect a Java project. Extract the Java version from compiler plugin configuration or `sourceCompatibility`.

If multiple project files are found, treat the project as a monorepo and generate configurations that handle each sub-project.

## Step 2: Detect Test Framework

Identify the test framework in use so the pipeline runs the correct test commands.

- For Node.js: check `package.json` devDependencies for `jest`, `mocha`, `vitest`, `ava`, or `tap`. Check for a `test` script in the `scripts` field.
- For Python: check `pyproject.toml` for `[tool.pytest]` or `[tool.unittest]` sections. Search for `conftest.py` or `test_*.py` files using filesystem search.
- For Rust: check for `#[cfg(test)]` blocks and `tests/` directory.
- For Go: search for `*_test.go` files.
- For Java: check for `src/test/` directory and detect JUnit or TestNG from dependencies.

Record the test command that should be used in the pipeline (e.g., `npm test`, `pytest`, `cargo test`, `go test ./...`, `mvn test`).

## Step 3: Detect Build System and Build Commands

Determine how the project is built so the pipeline includes the correct build step.

- For Node.js: check `package.json` for a `build` script. Detect bundlers like webpack, vite, esbuild, or rollup from devDependencies.
- For Python: check for `setup.py`, `pyproject.toml` build-system, or `Makefile` with build targets.
- For Rust: the build command is `cargo build --release`.
- For Go: the build command is `go build ./...` or a Makefile target.
- For Java: detect Maven (`mvn package`) or Gradle (`./gradlew build`).

Also check for a `Makefile` or `Taskfile.yml` at the project root, which may define custom build commands.

## Step 4: Detect Target CI Platform

Determine which CI platform to generate configuration for by checking for existing CI configuration.

- Check for `.github/workflows/` directory. If present, the target is GitHub Actions.
- Check for `.gitlab-ci.yml` file. If present, the target is GitLab CI.
- Check for `.circleci/` directory. If present, the target is CircleCI.
- Check for `Jenkinsfile`. If present, the target is Jenkins.
- Check for `azure-pipelines.yml`. If present, the target is Azure DevOps.

If no existing CI configuration is found, default to GitHub Actions as the target platform. Inform the user of the chosen platform and allow them to override.

## Step 5: Generate Pipeline Stages

Build the pipeline configuration with the following stages, in order. Each stage should only be included if it is relevant to the detected project type.

### Install Dependencies

- Node.js: `npm ci` or `yarn install --frozen-lockfile` or `pnpm install --frozen-lockfile`
- Python: `pip install -r requirements.txt` or `pip install -e ".[dev]"` or `poetry install`
- Rust: dependencies are fetched during build, but include `cargo fetch` for cache priming
- Go: `go mod download`
- Java: `mvn dependency:resolve` or `./gradlew dependencies`

### Lint and Format Check

- Node.js: `npm run lint` if a lint script exists; check for eslint, prettier
- Python: `ruff check .` or `flake8` or `pylint`; `black --check .` or `ruff format --check .`
- Rust: `cargo clippy -- -D warnings` and `cargo fmt -- --check`
- Go: `golangci-lint run` or `go vet ./...`
- Java: `mvn checkstyle:check` or spotbugs

### Build

Use the build command detected in Step 3.

### Test

- Run the test command detected in Step 2.
- Separate unit tests and integration tests into distinct stages if the project structure supports it.
- Include test result reporting (JUnit XML output) where supported.

### Security Scan

- Node.js: `npm audit --audit-level=high`
- Python: `pip-audit` or `safety check`
- Rust: `cargo audit`
- Go: `govulncheck ./...`
- Java: OWASP dependency-check plugin

### Deploy

Only include a deploy stage if deployment configuration is detected (e.g., Dockerfile, deployment manifests, serverless.yml). Mark deployment stages as manual/conditional so they do not run automatically on every push.

## Step 6: Configure Caching

Add caching configuration to speed up pipeline execution.

- Node.js: cache `node_modules/` or the npm/yarn/pnpm cache directory, keyed on the lock file hash.
- Python: cache `.venv/` or pip cache directory, keyed on `requirements.txt` or `poetry.lock` hash.
- Rust: cache `target/` and `~/.cargo/registry/`, keyed on `Cargo.lock` hash.
- Go: cache `~/go/pkg/mod/`, keyed on `go.sum` hash.
- Java: cache `~/.m2/repository/` or `~/.gradle/caches/`, keyed on `pom.xml` or `build.gradle` hash.

For GitHub Actions, use the `actions/cache` action. For GitLab CI, use the `cache` keyword with appropriate key definitions.

## Step 7: Set Up Matrix Builds

If the project needs to support multiple runtime versions, configure matrix builds.

- Node.js: test against active LTS versions (e.g., 18, 20, 22).
- Python: test against supported versions (e.g., 3.10, 3.11, 3.12, 3.13).
- Rust: test against stable and MSRV (minimum supported Rust version) from `Cargo.toml`.
- Go: test against the two most recent minor versions.
- Java: test against LTS versions (e.g., 17, 21).

Also consider matrix builds for multiple operating systems (ubuntu-latest, windows-latest, macos-latest) if the project is cross-platform.

## Step 8: Write the Configuration File

Generate the pipeline configuration in the correct format for the target platform.

- GitHub Actions: write a YAML file to `.github/workflows/ci.yml`. Use proper workflow syntax with `on`, `jobs`, `steps`, and `uses` directives.
- GitLab CI: write `.gitlab-ci.yml` with `stages`, job definitions, `image`, `script`, `artifacts`, and `cache` sections.
- Jenkins: write a `Jenkinsfile` in declarative pipeline syntax with `pipeline`, `agent`, `stages`, and `steps` blocks.
- CircleCI: write `.circleci/config.yml` with `version`, `jobs`, `workflows`, and `executors`.

Use filesystem write operations to create the file. If a CI config already exists, present a diff showing the proposed changes before writing.

## Step 9: Validate the Configuration

After writing the configuration file, validate its syntax.

- GitHub Actions: use `actionlint` if available via shell, or validate YAML structure manually.
- GitLab CI: use `gitlab-ci-lint` or the GitLab API lint endpoint if credentials are available.
- Jenkins: validate Groovy syntax if a linter is available.
- General: validate that the YAML is well-formed by parsing it with a YAML validator.

Report validation results. If errors are found, fix them and re-validate before presenting the final output.

## GitHub Actions Template: Node.js

When generating a GitHub Actions workflow for a Node.js project, use this structure as a baseline:

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: npm
      - run: npm ci
      - run: npm run lint --if-present
      - run: npm run build --if-present
      - run: npm test
```

Adjust this template based on detected tooling, adding or removing steps as appropriate.

## GitLab CI Template: Python

When generating a GitLab CI configuration for a Python project, use this structure as a baseline:

```yaml
stages:
  - lint
  - test
  - build

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"

cache:
  paths:
    - .pip-cache/
    - .venv/

lint:
  stage: lint
  image: python:3.12
  script:
    - pip install ruff
    - ruff check .
    - ruff format --check .

test:
  stage: test
  image: python:3.12
  script:
    - python -m venv .venv
    - source .venv/bin/activate
    - pip install -e ".[dev]"
    - pytest --junitxml=report.xml
  artifacts:
    reports:
      junit: report.xml

build:
  stage: build
  image: python:3.12
  script:
    - pip install build
    - python -m build
  artifacts:
    paths:
      - dist/
```

Adjust this template based on detected tooling and project structure.

## Notes

- Always prefer lock file-based installs (npm ci, yarn --frozen-lockfile) over regular installs in CI to ensure reproducible builds.
- Pin action versions to specific SHA hashes or major version tags (e.g., `actions/checkout@v4`) rather than using `@latest`.
- Include timeout limits on jobs to prevent runaway builds.
- Set `fail-fast: false` on matrix builds so that a failure in one combination does not cancel the others.
- Add concurrency groups to cancel redundant runs on the same branch.
