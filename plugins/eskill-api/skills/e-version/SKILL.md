---
name: e-version
description: "Analyzes API changes to determine versioning requirements and generates migration guides for breaking changes. Use when planning API changes, managing versions, or communicating changes to consumers. Also applies when: 'is this a breaking change', 'API version bump needed', 'migration guide for API change', 'backward compatibility check'."
---

# API Versioning Strategy

This skill analyzes changes to an API surface and classifies them by impact to determine the correct version bump. When breaking changes are detected, it generates a consumer migration guide. It supports both REST and code-level API versioning.

## Prerequisites

- A git repository with API-related changes (committed or staged).
- An identifiable API surface: OpenAPI spec, route handlers, or exported module interfaces.
- The eMCP ast_search, lsp_symbols, filesystem, git, and diff servers available.

## Workflow

### Step 1: Establish the Current API Baseline

Determine the current API surface by examining the most recent stable version. Use `git_log` to find the latest version tag or release commit:

- Look for tags matching `v*`, `release-*`, or semver patterns.
- If no tags exist, use the base branch (main/master) HEAD as the baseline.

Use `filesystem` tools to read the current API definition from the baseline:

| API Type        | Baseline Source                            |
|-----------------|--------------------------------------------|
| REST (spec)     | openapi.yaml or swagger.yaml at baseline   |
| REST (code)     | Route handler files at baseline            |
| Library         | Exported symbols from entry points         |
| GraphQL         | Schema SDL at baseline                     |
| gRPC            | Proto files at baseline                    |

For OpenAPI specs, use `data_file_read` to parse the baseline spec. For code-based APIs, use `ast_search` and `lsp_symbols` to extract the baseline API surface.

### Step 2: Extract the Proposed API Surface

Extract the API surface from the current working state (or target branch). Use the same extraction method as Step 1 but against the current files.

If comparing branches, use `git_diff` between the base branch and the feature branch to identify which files changed, then extract the full API surface from the feature branch.

### Step 3: Compute the Diff

Compare the baseline and proposed API surfaces element by element. Use `diff_text` from the eMCP diff server when comparing spec files directly.

For each API element, classify the change:

**REST API changes**:

| Change                                  | Classification |
|-----------------------------------------|---------------|
| New endpoint added                      | Additive      |
| New optional query parameter            | Additive      |
| New optional field in response body     | Additive      |
| New required field in request body      | Breaking      |
| Required field removed from request     | Additive      |
| Field removed from response body        | Breaking      |
| Field type changed in response          | Breaking      |
| Endpoint path changed                   | Breaking      |
| HTTP method changed                     | Breaking      |
| Status code changed for success         | Breaking      |
| Error response format changed           | Breaking      |
| Authentication requirement added        | Breaking      |
| Authentication requirement removed      | Additive      |
| Rate limit reduced                      | Breaking      |
| Field renamed in response body          | Breaking      |
| Optional field becomes required         | Breaking      |
| Required field becomes optional         | Additive      |
| Enum value added                        | Additive      |
| Enum value removed                      | Breaking      |
| Default value changed                   | Behavioral    |

**Library API changes**:

| Change                                  | Classification |
|-----------------------------------------|---------------|
| New exported function                   | Additive      |
| New optional parameter with default     | Additive      |
| Removed exported function               | Breaking      |
| Changed function return type            | Breaking      |
| New required parameter                  | Breaking      |
| Parameter type narrowed (more strict)   | Breaking      |
| Parameter type widened (more permissive) | Additive     |
| Return type narrowed                    | Additive      |
| Return type widened                     | Breaking      |
| Renamed export                          | Breaking      |
| Changed error type thrown               | Breaking      |

### Step 4: Determine Version Impact

Apply semver rules based on the most impactful change found:

| Highest Classification | Version Bump | Example        |
|------------------------|-------------|----------------|
| Breaking               | Major       | 2.3.1 -> 3.0.0 |
| Behavioral             | Minor       | 2.3.1 -> 2.4.0 |
| Additive               | Minor       | 2.3.1 -> 2.4.0 |
| None (docs/internal)   | Patch       | 2.3.1 -> 2.3.2 |

For pre-1.0 APIs (0.x.y), breaking changes increment the minor version and additive changes increment the patch version, following semver conventions for unstable APIs.

Present the version recommendation:

```
## Version Impact Analysis

Current version: 2.3.1
Recommended version: 3.0.0
Reason: 2 breaking changes detected

### Change Summary
- Breaking: 2
- Behavioral: 1
- Additive: 5
- Internal: 3
```

### Step 5: Generate Change Classification Report

List every detected change with its classification and affected consumers:

```
## Detailed Change Report

### Breaking Changes

1. POST /api/users -- new required field "email" in request body
   - Impact: All consumers sending POST /api/users must add "email" field
   - Affected consumers: user registration flow, admin user creation
   - Mitigation: Make "email" optional with a deprecation notice, or
     provide a default

2. GET /api/orders -- field "total" changed from number to string
   - Impact: Consumers parsing "total" as a number will break
   - Affected consumers: order display, invoice generation
   - Mitigation: Add new field "totalFormatted" (string) and deprecate
     "total" change in next major version

### Behavioral Changes

3. GET /api/products -- default page size changed from 20 to 50
   - Impact: Consumers relying on default pagination will receive larger
     responses
   - Risk: Low (consumers should handle variable page sizes)

### Additive Changes

4. GET /api/users -- new optional field "avatarUrl" in response
5. POST /api/orders -- new optional query parameter "dryRun"
6. New endpoint: GET /api/users/{id}/preferences
...
```

### Step 6: Generate Consumer Migration Guide

For each breaking change, produce a specific migration guide:

```
## Migration Guide: v2 -> v3

### Overview

Version 3.0.0 introduces 2 breaking changes to the Users and Orders APIs.
This guide covers the required changes for consumers upgrading from v2.

### Timeline

- v3.0.0 release: available now
- v2 deprecation notice: effective immediately
- v2 end-of-life: 90 days after v3 release

### Required Changes

#### 1. Add "email" field to user creation requests

**Before (v2)**:
```json
POST /api/v2/users
{
  "name": "Jane Doe",
  "role": "user"
}
```

**After (v3)**:
```json
POST /api/v3/users
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "role": "user"
}
```

**Action**: Update all POST /api/users calls to include the "email" field.
The field is required and must be a valid email address.

#### 2. Handle "total" field type change in order responses

**Before (v2)**: `"total": 29.99` (number)
**After (v3)**: `"total": "29.99"` (string)

**Action**: Update order response parsing to handle "total" as a string.
If numeric operations are needed, parse the string to a number.
```

### Step 7: Suggest Deprecation Strategy

When breaking changes are identified, suggest a phased deprecation approach:

**URL-based versioning** (REST APIs with path versioning):
- Deploy v3 alongside v2.
- Add `Sunset` header to v2 responses with the end-of-life date.
- Add `Deprecation` header to v2 responses.
- Log v2 usage to track consumer migration progress.

**Header-based versioning** (APIs using Accept or custom version headers):
- Support both version values simultaneously.
- Return a warning header on old version requests.

**Library versioning**:
- Publish the new major version to the package registry.
- Mark old version functions as deprecated in the current minor release before the major bump.
- Include migration notes in the changelog.

Suggest a timeline based on the severity of changes:

| Change Severity           | Suggested Deprecation Period |
|---------------------------|------------------------------|
| Minor breaking changes    | 30 days                      |
| Major breaking changes    | 90 days                      |
| Fundamental redesign      | 180 days                     |

### Step 8: Output Summary

Produce a final summary with actionable next steps:

```
## API Versioning Summary

### Version Decision
- Current: 2.3.1
- Recommended: 3.0.0

### Changes
- 2 breaking, 1 behavioral, 5 additive, 3 internal

### Artifacts Generated
- Change classification report (above)
- Consumer migration guide (above)
- Suggested deprecation timeline

### Next Steps
1. Review breaking changes and confirm they are intentional
2. Decide on deprecation period for v2
3. Update API spec version to 3.0.0
4. Publish migration guide to consumers
5. Add Sunset headers to v2 endpoints
```

## Edge Cases

- **No previous version tag**: If the project has never been versioned, recommend starting at 1.0.0 if the API is in production, or 0.1.0 if it is still in development. Classify all current API elements as the initial surface.
- **Multiple API versions already in production**: If the codebase already serves multiple versions (e.g., v1 and v2), analyze changes against the highest active version only.
- **Internal APIs**: For APIs consumed only within the same organization, breaking change tolerance may be higher. Note this in the report but still classify changes objectively.
- **Database-driven APIs**: Some APIs expose database schema changes directly (e.g., auto-generated CRUD endpoints). Flag that schema migrations may implicitly introduce breaking API changes.
- **Spec-only changes vs. code changes**: If the spec changed but the code did not (or vice versa), flag the discrepancy. The spec and implementation should change together.

## Notes

- This skill analyzes the impact of changes. It does not make the version bump or create git tags. Use the project's release tooling for those actions.
- For validating an OpenAPI spec before analyzing changes, use the e-openapi skill.
- For generating contract tests that verify backward compatibility at runtime, use the e-contract skill.
- The change classification tables in this skill cover common cases. Domain-specific APIs may have additional breaking change vectors (e.g., changing sort order, modifying rate limits, altering webhook payloads).

## Related Skills

- **e-openapi** (eskill-api): Run e-openapi before this skill to assess the current API spec before planning version changes.
- **e-apidoc** (eskill-office): Follow up with e-apidoc after this skill to update documentation to reflect the new versioning scheme.
