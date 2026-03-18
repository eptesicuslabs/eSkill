---
name: license-check
description: "Verifies license compatibility across all project dependencies and flags potential conflicts or compliance issues. Use when preparing for open-source release, during compliance audits, or when adding new dependencies to verify license compatibility."
---

# License Compliance Checker

This skill analyzes a project's dependency tree to verify that all dependency licenses are compatible with the project's own license and with each other. It identifies missing licenses, incompatible licenses, and provides actionable compliance recommendations.

## Step 1: Read the Project License

Determine the project's own license to establish the compatibility baseline.

1. Use `filesystem` `read_text` to check for a `LICENSE` or `LICENSE.md` file at the project root.
2. If no standalone license file exists, use `data_file_read` to read `package.json` and extract the `license` field.
3. For Python projects, check `setup.py`, `setup.cfg`, or `pyproject.toml` for the `license` field.
4. For Rust projects, read the `license` field from `Cargo.toml`.
5. For Go projects, check the `LICENSE` file (Go does not have a license field in `go.mod`).
6. Parse the license identifier using SPDX conventions (e.g., "MIT", "Apache-2.0", "GPL-3.0-only").
7. If the license cannot be determined, flag this as a critical issue: the project's own license must be established before compliance checking can proceed.

## Step 2: Read Dependency Manifests

Gather the complete list of direct and transitive dependencies.

1. Use `data_file_read` on the primary dependency manifest:
   - Node.js: `package.json` (dependencies, devDependencies, peerDependencies).
   - Python: `requirements.txt`, `Pipfile`, `pyproject.toml` (under `[project.dependencies]` or `[tool.poetry.dependencies]`).
   - Rust: `Cargo.toml` (under `[dependencies]`).
   - Go: `go.mod` (require blocks).
2. Also read lock files for the full transitive dependency tree:
   - `package-lock.json` or `yarn.lock` or `pnpm-lock.yaml`.
   - `Pipfile.lock` or `poetry.lock`.
   - `Cargo.lock`.
   - `go.sum`.
3. Build a dependency list: name, version, direct or transitive.

## Step 3: Extract Dependency Licenses (npm)

For Node.js projects:

1. Run `shell` command: `npx license-checker --json` if available, or fall back to manual extraction.
2. For manual extraction: iterate through `node_modules/*/package.json` using `filesystem` operations.
3. For each dependency package.json, extract:
   - The `license` field (string or object).
   - The `licenses` field (legacy format, array of objects with `type` and `url`).
4. If neither field exists, check for a LICENSE file in the package directory.
5. Record the license for each dependency. Mark as "Unknown" if no license information is found.

## Step 4: Extract Dependency Licenses (Python)

For Python projects:

1. Run `shell` command: `pip show <package>` for each dependency to extract the License field.
2. Alternatively, read metadata files directly:
   - `site-packages/<package>.dist-info/METADATA` or `PKG-INFO`.
   - Look for the `License:` header and `Classifier: License ::` classifiers.
3. For packages installed from source: check the package directory for LICENSE files.
4. Record the SPDX identifier for each dependency. If the license is specified as a classifier (e.g., `License :: OSI Approved :: MIT License`), map it to the corresponding SPDX identifier.

## Step 5: Categorize Dependency Licenses

Classify each dependency's license into one of the following categories:

### Permissive Licenses

These licenses impose minimal restrictions and are generally compatible with all project licenses:
- MIT
- BSD-2-Clause, BSD-3-Clause
- Apache-2.0
- ISC
- Unlicense
- CC0-1.0
- 0BSD

### Weak Copyleft Licenses

These licenses require modifications to the licensed component to be shared, but do not extend to the larger work:
- LGPL-2.1, LGPL-3.0
- MPL-2.0
- EPL-2.0
- CDDL-1.0

### Strong Copyleft Licenses

These licenses require the entire combined work to be distributed under the same license:
- GPL-2.0-only, GPL-2.0-or-later
- GPL-3.0-only, GPL-3.0-or-later
- AGPL-3.0-only, AGPL-3.0-or-later

### Non-Commercial or Restrictive Licenses

These licenses restrict commercial use or have other unusual restrictions:
- CC-BY-NC (any version)
- SSPL-1.0
- BSL-1.1 (Business Source License)
- Proprietary

### Unknown or No License

- "UNKNOWN": license metadata exists but could not be parsed.
- No license file or field found: legally this means all rights reserved, and the dependency cannot be used without explicit permission.

## Step 6: Check License Compatibility

Using the project's own license and each dependency's license, check for compatibility:

### Compatibility Rules

1. **Permissive project + Permissive dependency**: Compatible. No issues.
2. **Permissive project + Weak copyleft dependency**: Compatible if the dependency is used as a library (dynamically linked). The dependency modifications must remain under the copyleft license.
3. **Permissive project + Strong copyleft dependency**: Potentially incompatible. The combined work may need to be distributed under the copyleft license, which conflicts with the permissive project license.
4. **Copyleft project + Permissive dependency**: Compatible. Permissive licenses allow relicensing.
5. **GPL-3.0 project + Apache-2.0 dependency**: Compatible (Apache-2.0 is GPL-3.0 compatible).
6. **Apache-2.0 project + GPL-2.0-only dependency**: Incompatible (GPL-2.0 has patent clause conflicts with Apache-2.0).
7. **Any project + AGPL dependency**: The AGPL requires source distribution even for network use. Flag for review unless the project is also AGPL.
8. **Any project + No license dependency**: Incompatible. Cannot legally use.
9. **Any project + Unknown license dependency**: Requires manual review.

### Special Cases

- **Dual-licensed dependencies**: If a dependency offers a choice of licenses (e.g., "MIT OR Apache-2.0"), check compatibility with each option and use the compatible one.
- **SPDX expressions**: Parse compound expressions like "MIT AND BSD-3-Clause" or "Apache-2.0 WITH LLVM-exception" correctly.
- **DevDependencies**: Dependencies used only during development (test frameworks, build tools) may have more relaxed compatibility requirements since they are not distributed with the final product. Flag but do not mark as errors.

## Step 7: Flag Compliance Issues

Generate a list of issues, each with a severity level:

- **Critical**: Dependencies with no license (all rights reserved), or strong copyleft dependencies incompatible with the project license in production dependencies.
- **High**: Unknown licenses requiring manual review, AGPL dependencies in non-AGPL projects.
- **Medium**: Weak copyleft dependencies that may require special handling, deprecated license identifiers.
- **Low**: DevDependencies with copyleft licenses (not distributed), minor license metadata inconsistencies.

For each issue, provide:
- The dependency name and version.
- Its license (or lack thereof).
- Why it is flagged.
- What action to take: replace the dependency, seek a commercial license, restructure the code to isolate the dependency, or accept the copyleft terms.

## Step 8: Generate the Compliance Report

Structure the report with the following sections:

### Project License Summary

- Project name and detected license.
- SPDX identifier and license category.

### Dependency License Inventory

A table listing every dependency with:
- Name, version, license SPDX identifier, license category, compatibility status (compatible / review needed / incompatible).

### Compatibility Issues

For each flagged issue:
- Dependency name and version.
- License.
- Issue description.
- Severity.
- Recommended action.

### License Distribution

Summary statistics:
- Count of dependencies by license category (permissive, weak copyleft, strong copyleft, unknown, none).
- Percentage breakdown.

### Compliance Recommendations

- List dependencies that should be replaced due to license conflicts.
- List dependencies that require manual license review.
- Suggest alternative packages with more permissive licenses where known.
- If the project intends to change its own license, describe the implications for the current dependency set.

## Reference: License Compatibility Matrix

The following matrix summarizes compatibility for common license combinations. "Y" means compatible, "N" means incompatible, "R" means review needed.

| Project / Dependency | MIT | BSD | Apache-2.0 | LGPL-3.0 | GPL-2.0 | GPL-3.0 | AGPL-3.0 |
|---------------------|-----|-----|------------|----------|---------|---------|----------|
| MIT                 | Y   | Y   | Y          | R        | N       | N       | N        |
| BSD                 | Y   | Y   | Y          | R        | N       | N       | N        |
| Apache-2.0          | Y   | Y   | Y          | R        | N       | Y       | N        |
| LGPL-3.0            | Y   | Y   | Y          | Y        | N       | Y       | N        |
| GPL-2.0             | Y   | Y   | N          | Y        | Y       | N       | N        |
| GPL-3.0             | Y   | Y   | Y          | Y        | N       | Y       | N        |
| AGPL-3.0            | Y   | Y   | Y          | Y        | N       | Y       | Y        |

Notes:
- This matrix applies to dependencies included in the distributed work.
- DevDependencies are not distributed and are generally exempt from copyleft requirements.
- When in doubt, consult a legal professional for authoritative guidance on license compatibility.
