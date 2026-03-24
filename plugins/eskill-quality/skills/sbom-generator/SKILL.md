---
name: sbom-generator
description: "Generates Software Bill of Materials in SPDX or CycloneDX format from dependency inventory. Use for supply chain compliance, security audits, or vulnerability tracking. Also applies when: 'generate SBOM', 'software bill of materials', 'dependency inventory', 'supply chain security'."
---

# SBOM Generator

This skill generates a Software Bill of Materials (SBOM) by inventorying all project dependencies, their licenses, versions, and provenance. It outputs the SBOM in SPDX or CycloneDX format for use in supply chain security compliance, vulnerability tracking, and procurement reviews.

## Prerequisites

Confirm the output format with the user: SPDX 2.3 (JSON or tag-value) or CycloneDX 1.5 (JSON or XML). If no preference is stated, default to CycloneDX 1.5 JSON as it has broader tooling support. Identify the project root directory.

## Step 1: Detect Package Ecosystems

Use `filesystem` to scan the project root for dependency manifests.

| Manifest File | Ecosystem | Lock File |
|--------------|-----------|-----------|
| `package.json` | npm / Node.js | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` |
| `pyproject.toml` | Python (PEP 621 / Poetry) | `poetry.lock`, `pdm.lock` |
| `requirements.txt` | Python (pip) | None (versions may be pinned inline) |
| `Pipfile` | Python (pipenv) | `Pipfile.lock` |
| `Cargo.toml` | Rust | `Cargo.lock` |
| `go.mod` | Go | `go.sum` |
| `pom.xml` | Java (Maven) | None (resolved from repositories) |
| `build.gradle` / `build.gradle.kts` | Java/Kotlin (Gradle) | `gradle.lockfile` |
| `Gemfile` | Ruby | `Gemfile.lock` |
| `composer.json` | PHP | `composer.lock` |
| `*.csproj` / `packages.config` | .NET | `packages.lock.json` |

Read each detected manifest with `data_file_read`. Prefer lock files over manifests when both exist, as lock files contain resolved exact versions.

Record the ecosystems found. A project may span multiple ecosystems (e.g., a Node.js frontend with a Python backend).

## Step 2: Extract Direct Dependencies

For each ecosystem, parse the manifest to extract direct dependencies.

For each dependency, record:

| Field | Source |
|-------|--------|
| Package name | Manifest key |
| Version constraint | Manifest value (e.g., `^2.1.0`, `>=3.0,<4.0`) |
| Resolved version | Lock file entry |
| Scope | `dependencies` vs `devDependencies`, `[tool.poetry.group.dev]`, etc. |
| Registry | Default registry or custom registry URL if specified |

Distinguish between production and development dependencies. The SBOM should include both but mark the scope, as consumers may filter on scope for runtime vulnerability assessment.

If no lock file exists, note that resolved versions are unavailable and the SBOM will contain version ranges instead of pinned versions. Flag this as a supply chain risk.

## Step 3: Resolve Transitive Dependencies

Transitive dependencies (dependencies of dependencies) form the bulk of most SBOMs.

**From lock files**: Lock files contain the complete resolved dependency tree. Parse the lock file to extract every transitive dependency with its exact version.

- `package-lock.json`: Read the `packages` object (npm v7+ format) or `dependencies` object (npm v6).
- `yarn.lock`: Parse the YAML-like format to extract package@version entries.
- `Cargo.lock`: Read the `[[package]]` entries.
- `poetry.lock`: Read the `[[package]]` entries.
- `go.sum`: Each line contains a module, version, and hash.
- `Gemfile.lock`: Parse the GEM section for all resolved gems.
- `composer.lock`: Read the `packages` and `packages-dev` arrays.

**Without lock files**: Use `shell` to run the package manager's list or tree command if the tool is available:
- `npm ls --all --json`
- `pip list --format=json`
- `cargo tree`
- `go list -m all`
- `mvn dependency:tree`
- `gradle dependencies`

If neither lock file nor package manager is available, document only direct dependencies and note the limitation.

Record the total dependency count (direct + transitive) for the SBOM metadata.

## Step 4: Collect License Information

For each dependency, determine its license.

**Primary sources**:
1. Lock file license field (if present, e.g., `package-lock.json` includes license for some entries).
2. Registry metadata: use `shell` to query the registry if available (`npm view <pkg> license`, `pip show <pkg>`).
3. Package source: look for `LICENSE`, `LICENSE.md`, `COPYING`, or `NOTICE` files in the dependency's distributed files.
4. Manifest declarations: `license` field in the dependency's own `package.json`, `Cargo.toml`, or `pyproject.toml`.

Map license identifiers to SPDX license expression format:
- `MIT` remains `MIT`.
- `Apache 2.0` becomes `Apache-2.0`.
- `BSD 3-Clause` becomes `BSD-3-Clause`.
- `GPL-3.0-only`, `LGPL-2.1-or-later`, etc.
- Dual licenses: `MIT OR Apache-2.0`.
- Unknown or custom licenses: `NOASSERTION`.

Use `crypto` to compute SHA-256 hashes of dependency archives or lock file entries for integrity verification.

Record the license for each component. Flag any dependencies with:
- No license information (`NOASSERTION`).
- Copyleft licenses (GPL, AGPL) if the project is not itself copyleft.
- Non-OSI-approved or custom licenses.

## Step 5: Collect Package Metadata

For each dependency, gather additional metadata required by the SBOM format.

| Metadata Field | SPDX Field | CycloneDX Field | Source |
|---------------|-----------|-----------------|--------|
| Package name | PackageName | name | Manifest/lock |
| Version | PackageVersion | version | Lock file |
| Supplier | PackageSupplier | supplier | Registry metadata |
| Download URL | PackageDownloadLocation | externalReferences[distribution] | Registry |
| Checksum | PackageChecksum | hashes | Lock file or computed |
| Homepage | PackageHomePage | externalReferences[website] | Registry metadata |
| Description | PackageDescription | description | Registry metadata |
| CPE | ExternalRef (cpe23Type) | cpe | Constructed from vendor/product/version |
| PURL | ExternalRef (purl) | purl | Constructed per PURL spec |

Construct Package URLs (PURLs) for each component following the PURL specification:
- npm: `pkg:npm/<scope>/<name>@<version>`
- PyPI: `pkg:pypi/<name>@<version>`
- Cargo: `pkg:cargo/<name>@<version>`
- Go: `pkg:golang/<namespace>/<name>@<version>`
- Maven: `pkg:maven/<group-id>/<artifact-id>@<version>`

PURLs are essential for cross-referencing with vulnerability databases (OSV, NVD).

## Step 6: Build Dependency Tree Structure

Construct the dependency graph showing which components depend on which other components.

For SPDX, this uses `Relationship` entries:
- `DEPENDS_ON`: Package A depends on Package B.
- `DEV_DEPENDENCY_OF`: Package A is a development dependency of Package B.
- `DESCRIBED_BY`: The SBOM document describes the root package.

For CycloneDX, this uses the `dependencies` array where each entry lists a component ref and its direct dependency refs.

The root of the tree is the project itself. Direct dependencies branch from the root. Transitive dependencies branch from their parent dependency.

If the dependency graph is not fully resolvable (no lock file, partial information), document the relationships that are known and note the incompleteness.

## Step 7: Generate SBOM Document

Assemble the collected data into the target format.

**CycloneDX 1.5 JSON structure**:

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "version": 1,
  "metadata": {
    "timestamp": "<ISO 8601>",
    "tools": [{ "name": "eskill-sbom-generator", "version": "1.0.0" }],
    "component": { "type": "application", "name": "<project>", "version": "<version>" }
  },
  "components": [ ... ],
  "dependencies": [ ... ]
}
```

**SPDX 2.3 JSON structure**:

```json
{
  "spdxVersion": "SPDX-2.3",
  "dataLicense": "CC0-1.0",
  "SPDXID": "SPDXRef-DOCUMENT",
  "name": "<project-sbom>",
  "documentNamespace": "<unique URI>",
  "creationInfo": { ... },
  "packages": [ ... ],
  "relationships": [ ... ]
}
```

Use `filesystem` to write the SBOM file. Default output paths:
- CycloneDX: `sbom.cdx.json`
- SPDX: `sbom.spdx.json`

## Step 8: Validate the SBOM

After generation, validate the SBOM for completeness and correctness.

Perform the following checks:

1. **Schema validation**: Verify the JSON structure conforms to the target specification schema.
2. **Component count**: Confirm the number of components matches the dependency count from Step 3.
3. **License coverage**: Calculate the percentage of components with identified licenses. Report the coverage rate. Below 80% coverage is a finding.
4. **PURL coverage**: Confirm all components have valid PURLs.
5. **Hash coverage**: Confirm all components have at least one hash (SHA-256 preferred).
6. **Relationship completeness**: Verify the dependency graph has no orphaned nodes (components not connected to the tree).
7. **Duplicate check**: Verify no component appears twice with different identifiers.

Report validation results with pass/fail for each check.

## Step 9: Generate Summary Report

Produce a human-readable summary alongside the machine-readable SBOM.

```
## SBOM Summary

**Project**: <name> v<version>
**Format**: <CycloneDX 1.5 / SPDX 2.3>
**Generated**: <timestamp>
**Output File**: <path>

### Component Statistics

| Metric | Count |
|--------|-------|
| Total components | <N> |
| Direct dependencies | <N> |
| Transitive dependencies | <N> |
| Production dependencies | <N> |
| Development dependencies | <N> |

### License Distribution

| License | Count | Percentage |
|---------|-------|------------|
| MIT | <N> | <X%> |
| Apache-2.0 | <N> | <X%> |
| ISC | <N> | <X%> |
| BSD-3-Clause | <N> | <X%> |
| NOASSERTION | <N> | <X%> |
| Other | <N> | <X%> |

### Ecosystem Breakdown

| Ecosystem | Direct | Transitive | Total |
|-----------|--------|------------|-------|
| npm | <N> | <N> | <N> |
| PyPI | <N> | <N> | <N> |

### Findings

- <license concerns, missing data, supply chain risks>
```

## Step 10: Cross-Reference with Vulnerability Databases

If vulnerability checking is requested, cross-reference the SBOM components against known vulnerability databases.

Use `shell` to query local tools if available:
- `npm audit --json` for Node.js dependencies.
- `pip-audit --format=json` for Python dependencies.
- `cargo audit --json` for Rust dependencies.

For each vulnerability found, add advisory references to the SBOM components (CycloneDX `vulnerabilities` array or SPDX `ExternalRef` with `SECURITY` category).

Report vulnerabilities in the summary with severity, affected component, and advisory ID.

## Edge Cases

- **Monorepos**: Scan each workspace package independently and produce either a single aggregated SBOM or per-package SBOMs based on user preference.
- **Vendored dependencies**: If dependencies are committed to the repository (Go vendor, PHP vendor), parse the vendored manifests rather than the lock file.
- **Native/system dependencies**: Some packages depend on system libraries (OpenSSL, libxml2) that are not tracked by the package manager. Note these as out-of-scope and recommend documenting them separately.
- **Private registries**: Dependencies from private registries may lack public metadata. Record what is available and mark missing fields appropriately.
- **Container base images**: If a Dockerfile is present, the base image contains its own dependencies. Note that a comprehensive SBOM should include container layer analysis, which requires tools like Syft or Trivy and is beyond the scope of this manifest-based analysis.
- **Dual-format output**: If the user needs both SPDX and CycloneDX, generate both from the same collected data.

## Related Skills

- **dependency-audit** (eskill-coding): Run dependency-audit before this skill to gather the dependency data that feeds into the SBOM.
- **license-check** (eskill-quality): Run license-check before this skill to include license classifications in the generated SBOM.
- **compliance-checklist** (eskill-quality): Follow up with compliance-checklist after this skill to verify the SBOM satisfies regulatory requirements.
