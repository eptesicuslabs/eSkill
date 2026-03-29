---
name: e-env
description: "Validates tool versions and configs against project requirements and reports PASS/FAIL with fixes. Use when setting up a new machine, onboarding a developer, or troubleshooting build failures. Also applies when: 'check my setup', 'why won't it build', 'wrong node version', 'verify environment', 'dev setup broken'."
---

# Environment Validate

Systematically verify that the current development environment meets all project requirements. This skill reads project configuration files, checks installed tool versions, validates environment variables, and produces a structured PASS/FAIL report with remediation instructions for any failures.

## Prerequisites

- A project with configuration files that declare tool and runtime requirements (package.json, .nvmrc, pyproject.toml, rust-toolchain.toml, or equivalent).
- The eMCP filesystem, shell, and data_file_read servers available.
- Shell access to run version-checking commands (node --version, python --version, etc.).

### Step 1: Identify Project Requirements

Read the project root to locate configuration files that declare tool and runtime requirements. Check for the presence of each of the following and extract version constraints where specified:

- `package.json` -- look for the `engines` field (e.g., `engines.node`, `engines.npm`).
- `.nvmrc` -- contains the expected Node.js version string.
- `.node-version` -- alternative Node version file used by some version managers.
- `.python-version` -- specifies the Python version expected by pyenv.
- `.tool-versions` -- asdf version manager file; parse each line as `<tool> <version>`.
- `Dockerfile` -- inspect `FROM` directives for base image versions; look for `ARG` or `ENV` declarations that pin versions.
- `.ruby-version` -- Ruby version constraint.
- `go.mod` -- Go version requirement in the `go` directive.
- `rust-toolchain.toml` or `rust-toolchain` -- Rust toolchain channel and version.
- `.java-version` or `pom.xml` / `build.gradle` -- Java version requirements.

Use `fs_info` to check each configuration file for existence and read permissions before attempting to read it. This avoids unnecessary read errors and gives early visibility into permission problems that could affect the build. For each file that exists and is readable, use `fs_read` to parse its contents. Do not fail if a file is absent; simply skip it. Collect all discovered requirements into a structured list of `(tool, required_version, source_file)` tuples.

### Step 2: Check OS and Platform

Use `sys_info` to retrieve:

- Operating system name and version.
- CPU architecture (x64, arm64, etc.).
- Available memory.
- Node.js version of the eMCP runtime itself.

Record these values. Some projects have platform-specific requirements (e.g., native modules that only compile on certain architectures). Flag any known incompatibilities if the project documents them (check for a `.supported-platforms` file or similar).

### Step 3: Verify Installed Tool Versions

For each required tool discovered in Step 1, run the appropriate version command via `shell_exec` (shell tool). Use the following commands:

- Node.js: `node --version`
- npm: `npm --version`
- yarn: `yarn --version`
- pnpm: `pnpm --version`
- Python: `python --version` (also try `python3 --version`)
- pip: `pip --version` (also try `pip3 --version`)
- Git: `git --version`
- Docker: `docker --version`
- Docker Compose: `docker compose version` (also try `docker-compose --version`)
- Go: `go version`
- Rust / Cargo: `rustc --version` and `cargo --version`
- Java: `java -version` (note: output goes to stderr)
- Ruby: `ruby --version`
- Make: `make --version`

If a command fails (non-zero exit code or command not found), record the tool as NOT INSTALLED. Otherwise, parse the version string from the output. Normalize version strings by stripping leading `v` characters and other prefixes (e.g., `v18.17.0` becomes `18.17.0`).

### Step 4: Compare Installed Versions Against Requirements

For each `(tool, required_version, installed_version)` triple, determine the match status:

- **Exact match**: The installed version exactly matches the required version.
- **Compatible**: The installed major version matches and the installed minor/patch is equal or greater (semver compatible).
- **Mismatch**: The installed version does not satisfy the requirement.
- **Missing**: The tool is not installed at all.

Use semver comparison logic. If the required version uses a range (e.g., `>=16.0.0`, `^18.0.0`, `~3.9`), interpret the range according to standard semver semantics. Record the comparison result for each tool.

### Step 5: Check Environment Variables

Use `sys_env` to read the current environment. Check for variables commonly required by projects:

- `PATH` -- verify that expected tool directories are present (e.g., `/usr/local/bin`, `~/.nvm/versions/node/...`, `~/.cargo/bin`).
- `NODE_ENV` -- check if set and what value it holds.
- `HOME` / `USERPROFILE` -- should be defined.
- `SHELL` -- on Unix systems, should point to a valid shell.
- Project-specific variables -- look for a `.env.example` or `.env.template` file in the project root. If found, read it and verify that each listed variable has a corresponding value in the current environment. Do NOT read `.env` itself to avoid exposing secrets; only check for the presence of keys, not their values.

Flag any missing variables that appear in `.env.example` but are absent from the current environment.

Use `fs_info` on the `.env` and `.env.example` files to check their permissions. If `.env` is world-readable, flag it as a security warning -- environment files containing secrets should be readable only by the owner. Similarly, verify that `.env` is listed in `.gitignore` to prevent accidental commits of secrets.

### Step 6: Check Disk Space

Use `sys_disk` to retrieve disk usage information. Evaluate:

- Free space on the partition containing the project directory. Most development workflows require at least 5 GB free for build artifacts, caches, and dependencies.
- Free space on the partition containing temporary files (`/tmp` on Unix, `%TEMP%` on Windows). Build processes often write large temporary files.
- If Docker is installed, note the Docker storage driver and available space for images and containers.

Flag a warning if free space is below 5 GB and an error if below 1 GB.

### Step 7: Verify Package Manager Lock Files

Check that lock files are consistent with their corresponding manifest files:

- `package-lock.json` should be in sync with `package.json`. Run `npm ls --all` or check modification timestamps.
- `yarn.lock` should be in sync with `package.json`. Run `yarn check --integrity` if yarn is available.
- `pnpm-lock.yaml` should be in sync with `package.json`.
- `Pipfile.lock` should be in sync with `Pipfile`.
- `poetry.lock` should be in sync with `pyproject.toml`.
- `Gemfile.lock` should be in sync with `Gemfile`.
- `go.sum` should be in sync with `go.mod`.
- `Cargo.lock` should be in sync with `Cargo.toml`.

For each pair found, use `fs_info` on both the manifest and lock file to check existence and retrieve modification timestamps. If the lock file is missing but the manifest exists, flag it as a warning. If both exist, compare their modification times from the `fs_info` metadata -- a manifest newer than its lock file suggests the lock file needs regeneration.

### Step 8: Generate the Validation Report

Compile all findings into a structured report with the following sections:

### Report Format

```
## Environment Validation Report

**Date**: <timestamp>
**Project**: <project directory name>
**Platform**: <OS> <version> (<architecture>)

### Tool Versions

| Tool       | Required | Installed | Status |
|------------|----------|-----------|--------|
| node       | 18.x     | 18.17.0   | PASS   |
| python     | 3.9+     | NOT FOUND | FAIL   |

### Environment Variables

| Variable   | Status  | Note                        |
|------------|---------|---------------------------  |
| NODE_ENV   | SET     | Value: development          |
| API_KEY    | MISSING | Listed in .env.example      |

### Disk Space

| Mount      | Total   | Free    | Status  |
|------------|---------|---------|---------|
| /          | 500 GB  | 42 GB   | PASS    |

### Lock File Integrity

| Lock File          | Manifest      | Status  |
|--------------------|---------------|---------|
| package-lock.json  | package.json  | PASS    |

### Summary

- Total checks: <N>
- Passed: <N>
- Warnings: <N>
- Failed: <N>
```

### Fix Instructions for Common Failures

For each FAIL result, provide specific remediation instructions:

- **Node.js not installed or wrong version**: Recommend installing via nvm (`nvm install <version>`) or volta (`volta install node@<version>`). On Windows, also mention nvm-windows or the official installer.
- **Python not installed or wrong version**: Recommend pyenv (`pyenv install <version>`) or the official installer. On Windows, suggest the Microsoft Store or python.org installer.
- **Git not installed**: Link to https://git-scm.com/downloads. On macOS, suggest `xcode-select --install`.
- **Docker not installed**: Link to Docker Desktop for macOS/Windows or docker.io packages for Linux.
- **Missing environment variables**: Suggest copying `.env.example` to `.env` and filling in values, or exporting variables in shell profile.
- **Low disk space**: Suggest cleaning Docker images (`docker system prune`), clearing package caches (`npm cache clean --force`, `pip cache purge`), or removing old build artifacts.
- **Stale lock files**: Suggest running the appropriate install command (`npm install`, `yarn install`, `pip install`, etc.) to regenerate the lock file.

Present the report in a clear, scannable format. Use PASS, WARN, and FAIL markers consistently so the output is easy to parse both visually and programmatically.

## Edge Cases

- **Version managers with shims**: Tools like nvm, pyenv, and rbenv use shims that may report a different version than the one active in the current shell. Run the version command in the same shell context as the project build.
- **Global vs. local tool installations**: A globally installed CLI tool may differ in version from the locally installed one (e.g., global ESLint vs. project-local ESLint). Check the project-local binary first.
- **Docker-based development environments**: Projects using devcontainers or Docker Compose for development have tool versions defined in the container, not on the host. Detect Dockerized dev setups and validate inside the container.
- **Windows/macOS path differences**: Tool paths differ across operating systems (e.g., `/usr/local/bin/node` vs. `C:\Program Files\nodejs\node.exe`). Use `which`/`where` for portable detection rather than hardcoded paths.
- **Missing optional tools**: Some project tools are optional (e.g., pre-commit hooks require the pre-commit tool). Distinguish between required tools (build fails without them) and optional tools (some workflows are degraded).

## Related Skills

- **e-init** (eskill-meta): Run e-init before this skill to define the project requirements that environment validation will check.
- **e-containers** (eskill-system): Follow up with e-containers after this skill to verify containerized services are running correctly.
