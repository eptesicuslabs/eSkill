---
name: dependency-audit
description: "Audits dependencies for vulnerabilities, outdated versions, unused packages, and license issues. Use when checking security advisories, planning a major upgrade, or cleaning unused deps. Also applies when: 'audit dependencies', 'vulnerable packages', 'which deps are outdated', 'find unused deps'."
---

# Dependency Audit

This skill performs a comprehensive audit of a project's dependencies, covering security vulnerabilities, outdated packages, unused dependencies, and license compliance. It supports multiple package managers and produces an actionable report.

## Prerequisites

- A project with a dependency manifest file (package.json, requirements.txt, pyproject.toml, Cargo.toml, go.mod, etc.).
- Network access for fetching advisory databases (or cached audit data).

## Workflow

### Step 1: Detect the Package Manager

Identify the package ecosystem by checking for manifest files in the project root:

| File                     | Package Manager      | Ecosystem |
|--------------------------|----------------------|-----------|
| package.json             | npm / yarn / pnpm    | Node.js   |
| yarn.lock                | yarn                 | Node.js   |
| pnpm-lock.yaml           | pnpm                 | Node.js   |
| package-lock.json         | npm                  | Node.js   |
| requirements.txt          | pip                  | Python    |
| pyproject.toml            | pip / poetry / pdm   | Python    |
| Pipfile                   | pipenv               | Python    |
| Cargo.toml                | cargo                | Rust      |
| go.mod                    | go modules           | Go        |
| Gemfile                   | bundler              | Ruby      |
| build.gradle / pom.xml    | gradle / maven       | Java      |

Use `filesystem` tools (list_directory, read_file) to check for these files. If multiple ecosystems are present (e.g., a monorepo), audit each one separately.

### Step 2: Read the Dependency Manifest

Use `data_file_read` from the eMCP data-file server to parse the dependency manifest:

- For **package.json**: Extract `dependencies`, `devDependencies`, `peerDependencies`, and `optionalDependencies`.
- For **requirements.txt**: Extract each line as a dependency with its version constraint.
- For **pyproject.toml**: Extract `[project.dependencies]` and `[project.optional-dependencies]`.
- For **Cargo.toml**: Extract `[dependencies]`, `[dev-dependencies]`, and `[build-dependencies]`.
- For **go.mod**: Extract `require` directives.

Record the declared version constraint for each dependency.

### Step 3: Run the Security Audit

Execute the appropriate audit command using `shell` tools from the eMCP shell server:

| Ecosystem | Command                                    | Notes                                |
|-----------|--------------------------------------------|--------------------------------------|
| Node.js   | `npm audit --json`                         | Returns structured JSON              |
| Node.js   | `yarn audit --json`                        | Returns NDJSON                       |
| Python    | `pip-audit --format=json`                  | Requires pip-audit installed         |
| Python    | `safety check --json`                      | Alternative; requires safety package |
| Rust      | `cargo audit --json`                       | Requires cargo-audit installed       |
| Go        | `govulncheck ./...`                        | Requires govulncheck installed       |
| Ruby      | `bundle-audit check`                       | Requires bundler-audit gem           |

If the audit tool is not installed, note this in the report and suggest installation. Do not attempt to install tools without user permission.

### Step 4: Parse and Categorize Findings

Parse the audit output and categorize each finding by severity:

| Severity | Description                                          | Action        |
|----------|------------------------------------------------------|---------------|
| Critical | Remote code execution, authentication bypass         | Fix immediately |
| High     | Data exposure, privilege escalation                  | Fix urgently  |
| Moderate | Denial of service, information disclosure            | Plan fix      |
| Low      | Minor issues, theoretical attacks                    | Track         |

For each finding, record:
- Package name and installed version.
- Vulnerability ID (CVE, GHSA, etc.).
- Severity level.
- Description of the vulnerability.
- Fixed version (if available).
- Whether a fix requires a major version bump.

### Step 5: Detect Unused Dependencies

Search the codebase for actual usage of each declared dependency:

For **JavaScript/TypeScript**:
- Use `ast_search` to find `import` and `require` statements.
- Match imported module names against declared dependencies.
- Check for dynamic imports (`import()`) and require expressions.
- Check configuration files that may reference packages (babel, webpack, eslint configs).

For **Python**:
- Use `ast_search` to find `import` and `from ... import` statements.
- Match module names against declared dependencies (note: package names and import names sometimes differ, e.g., `Pillow` is imported as `PIL`).

For **Rust**:
- Use `ast_search` to find `use` statements and `extern crate` declarations.
- Check `build.rs` for build-time dependencies.

Mark dependencies as potentially unused if no import is found. Flag these for manual review, as some packages are used indirectly (plugins, runtime loaders, type definitions).

### Step 6: Check License Compliance

For each dependency, determine its license:

- For Node.js: Read the `license` field from each package's entry in `node_modules/<pkg>/package.json` or use `npm ls --json` to get license information.
- For Python: Use `pip show <package>` to get the license field.
- For Rust: Check `Cargo.lock` and crate metadata.

Flag potential issues:

| License       | Concern                                           |
|---------------|---------------------------------------------------|
| GPL-2.0/3.0   | Copyleft; may require open-sourcing your code     |
| AGPL-3.0       | Network copyleft; stricter than GPL               |
| SSPL           | Not OSI-approved; restrictive for SaaS            |
| UNLICENSED     | No license; legally risky to use                  |
| Unknown        | License not declared; needs manual investigation  |

If the project has a declared license policy (e.g., "MIT-compatible only"), check each dependency against it.

### Step 7: Generate the Audit Report

Produce a structured report with the following sections:

```
## Dependency Audit Report

### Summary
- Total dependencies: 142 (98 production, 44 development)
- Vulnerabilities: 2 critical, 1 high, 3 moderate
- Outdated packages: 15
- Potentially unused: 4
- License concerns: 1

### Vulnerabilities

#### Critical
- **lodash@4.17.19** -- CVE-2021-23337: Prototype pollution
  Fixed in: 4.17.21
  Path: lodash -> direct dependency
  Action: Run `npm update lodash`

#### High
- **axios@0.21.0** -- CVE-2021-3749: ReDoS vulnerability
  Fixed in: 0.21.2
  Path: axios -> direct dependency
  Action: Run `npm update axios`

[... additional entries ...]

### Potentially Unused
- **moment**: No import found in source files
- **uuid**: No import found in source files (check if used in config)

### License Concerns
- **gpl-package@2.0.0**: Licensed under GPL-3.0
  Used by: src/utils/transform.ts
  Action: Evaluate if GPL is compatible with project license

### Outdated Packages
| Package    | Current | Latest | Type   |
|------------|---------|--------|--------|
| typescript | 4.9.5   | 5.3.2  | Major  |
| eslint     | 8.45.0  | 8.56.0 | Minor  |
| prettier   | 2.8.8   | 3.1.1  | Major  |
```

### Step 8: Suggest an Upgrade Path

For critical and high severity vulnerabilities, provide specific upgrade commands:

- If the fix is a patch or minor version: suggest a direct update command.
- If the fix requires a major version: note breaking changes and suggest reviewing the changelog first.
- If a transitive dependency is vulnerable: identify which direct dependency pulls it in and whether updating the direct dependency resolves it.

For outdated packages that are not vulnerable, prioritize based on:
1. Security fixes in newer versions.
2. Bug fixes relevant to the project.
3. New features the project could benefit from.
4. Major version upgrades (suggest these as separate tasks due to potential breaking changes).

## Related Skills

- **security-scan** (eskill-quality): Run security-scan alongside this skill to cover both dependency and source code vulnerabilities.
- **license-check** (eskill-quality): Run license-check alongside this skill to verify dependency licenses comply with project requirements.
- **sbom-generator** (eskill-quality): Follow up with sbom-generator after this skill to produce a formal software bill of materials from the audit results.
