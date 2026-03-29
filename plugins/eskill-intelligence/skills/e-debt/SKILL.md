---
name: e-debt
description: "Catalogs technical debt by analyzing TODOs, FIXMEs, deprecated usage, and complexity hotspots with prioritization. Use during sprint planning, before refactors, or building a tech debt backlog. Also applies when: 'find tech debt', 'list all TODOs', 'what needs refactoring', 'technical debt report'."
---

# Technical Debt Tracker

This skill catalogs technical debt across a codebase by scanning for TODO/FIXME annotations, deprecated API usage, complexity hotspots, code duplication indicators, and outdated patterns. It produces a prioritized debt inventory with effort estimates and suggested groupings for sprint planning.

## Prerequisites

Confirm the project root and the scope of the analysis. For large monorepos, the user may want to focus on specific directories or packages. Identify the primary programming language(s) to select appropriate analysis patterns.

## Step 1: Scan for Annotation-Based Debt

Use `egrep_search` for the initial sweep to find code annotations that indicate known debt. The trigram-indexed search returns results instantly across the entire codebase, making it the preferred tool for pattern-matching TODO, FIXME, HACK, and similar markers. Follow up with `ast_search` for language-aware analysis where needed (e.g., distinguishing comments from string literals).

Search for these annotation patterns across all source files:

| Annotation | Meaning | Default Priority |
|-----------|---------|-----------------|
| `TODO` | Planned work not yet done | Medium |
| `FIXME` | Known bug or incorrect behavior | High |
| `HACK` | Workaround that should be replaced | High |
| `XXX` | Problematic code needing attention | Medium |
| `TEMP` / `TEMPORARY` | Code intended to be replaced | Medium |
| `DEPRECATED` | Code marked for removal | Low |
| `OPTIMIZE` / `PERF` | Performance improvement needed | Low |
| `REFACTOR` | Structural improvement needed | Medium |
| `DEBT` | Explicitly marked technical debt | Medium |
| `NOSONAR` / `noinspection` / `eslint-disable` | Suppressed lint warnings | Medium |

For each finding, extract:

1. **File path**: Absolute path with forward slashes.
2. **Line number**: Where the annotation appears.
3. **Annotation type**: Which marker was found.
4. **Content**: The text following the annotation (the description of the debt).
5. **Author**: Use `git` with `git_blame` or `git_log` for the file to determine who wrote the annotation and when.
6. **Age**: How long ago the annotation was added. Older debt is more likely to be forgotten and should be surfaced.

Use `egrep_search_files` to locate configuration files (`.eslintrc*`, `tsconfig.json`, `pyproject.toml`, `.prettierrc*`) that may define custom lint suppressions or debt-related ignores. Use `filesystem` to exclude generated directories (`node_modules`, `vendor`, `dist`, `build`, `.git`, `__pycache__`, `target`).

Record all findings in a working list.

## Step 2: Detect Deprecated API Usage

Use `egrep_search` for a fast first pass to find deprecation markers (`@deprecated`, `@Deprecated`, `#[deprecated]`, `[Obsolete]`, `DeprecationWarning`) across the codebase. Then use `ast_search` and `lsp_diagnostics` for language-aware verification and to find usage of deprecated functions, methods, and libraries.

**Language-specific patterns**:

- **JavaScript/TypeScript**: `@deprecated` JSDoc tags on functions/classes, deprecated library imports (check against known deprecated packages).
- **Python**: `warnings.warn("...", DeprecationWarning)`, `@deprecated` decorators from the `deprecated` package, usage of functions documented as deprecated in the standard library.
- **Java**: `@Deprecated` annotation on classes, methods, and fields.
- **Rust**: `#[deprecated]` attribute.
- **Go**: "Deprecated:" comments in godoc format.
- **C#**: `[Obsolete]` attribute.

Use `lsp_diagnostics` to retrieve compiler and linter warnings related to deprecation. LSP diagnostics provide accurate, language-server-verified deprecation information.

For each deprecated usage, record:
- The deprecated symbol name.
- Where it is used (file and line).
- The recommended replacement (from the deprecation message if available).
- Whether the deprecation comes from first-party code (within the project) or third-party dependencies.

## Step 3: Identify Complexity Hotspots

Analyze code complexity to find areas that are disproportionately difficult to maintain.

**File-level complexity indicators**:

Use `filesystem` to check file sizes. Flag files exceeding these thresholds:

| Metric | Warning Threshold | Critical Threshold |
|--------|------------------|--------------------|
| Lines of code per file | 300 lines | 600 lines |
| Functions per file | 15 functions | 30 functions |
| Classes per file | 3 classes | 5 classes |
| Nesting depth | 4 levels | 6 levels |
| Parameters per function | 5 parameters | 8 parameters |

Use `ast_search` to count functions and classes per file for the top-level source directories.

**Change-frequency analysis**:

Use `git` to identify files that change frequently. Files with high change frequency combined with high complexity are the highest-priority debt targets.

- Run `git_log` with `--stat` to get change frequency per file over the last 6 months.
- Rank files by number of commits that modified them.
- Cross-reference with complexity: files that are both complex and frequently changed are maintenance burdens.

Record the top 20 files by the combined metric of complexity multiplied by change frequency.

**Dependency complexity**:

Use `ast_search` to count import statements per file. Files importing many modules are coupling points that make refactoring difficult.

## Step 4: Detect Outdated Dependencies

Use `data_file_read` to read dependency manifests and lock files.

For each dependency, check:

1. **Major version behind**: Dependencies more than one major version behind are likely accumulating breaking changes that become harder to address over time.
2. **Unmaintained packages**: Packages with no releases in 2+ years.
3. **Known vulnerabilities**: Cross-reference with `lsp_diagnostics` or `shell` to run audit commands (`npm audit`, `pip-audit`, `cargo audit`).
4. **Duplicate dependencies**: Multiple versions of the same package in the dependency tree (common in npm).

Use `git` to check when the lock file was last updated. A lock file unchanged for months while dependency versions advance indicates deferred update work.

Record each outdated dependency with:
- Current version vs latest version.
- Number of major versions behind.
- Whether breaking changes are documented.
- Security advisory count.

## Step 5: Find Code Duplication Indicators

Use `egrep_search` and `ast_search` to detect potential code duplication without a full clone detection analysis. `egrep_search` is particularly effective here because trigram-indexed search can find repeated string patterns, function signatures, and code fragments across the entire codebase in milliseconds.

Heuristic indicators of duplication:

1. **Similar function names**: Functions with names like `processUserV2`, `handleOrderLegacy`, or numbered suffixes (`parseData1`, `parseData2`) suggest copied-and-modified code. Use `egrep_search` to find these patterns (e.g., search for `V2`, `Legacy`, `Old` in function definitions).
2. **Parallel directory structures**: Directories with similar structure and file names (e.g., `old/` alongside `new/`, `v1/` and `v2/`). Use `egrep_search_files` to find files with version-suffixed names.
3. **Utility sprawl**: Multiple utility files across the codebase (`utils.ts` in 5 different directories) that may contain overlapping functionality. Use `egrep_search_files` to locate all utility files by name pattern.
4. **Repeated patterns**: Use `egrep_search` to find identical code blocks appearing in multiple files (common string literals, similar error handling blocks, repeated configuration patterns).

For each duplication indicator, record:
- The files involved.
- The estimated scope (how many lines are duplicated).
- Suggested consolidation approach.

## Step 6: Assess Test Coverage Gaps

Use `data_file_read` to read test configuration and coverage reports if available.

Check for:

1. **Untested source files**: Source files in critical paths with no corresponding test file.
2. **Skipped tests**: Tests marked with `.skip`, `@pytest.mark.skip`, `@Ignore`, or `#[ignore]`. These represent deferred test fixes.
3. **Test-to-source ratio**: Calculate the ratio of test files to source files. A ratio below 0.5 may indicate insufficient test coverage for a mature project.
4. **Coverage reports**: Read coverage output files (`.nyc_output`, `coverage/`, `htmlcov/`) if they exist. Identify files with coverage below 50%.

Use `filesystem` to find test files and map them to their corresponding source files by naming convention.

Record coverage gaps with the associated source file and its risk level based on how critical the code is.

## Step 7: Prioritize Debt Items

Score each debt item using a priority matrix.

| Factor | Weight | Scoring |
|--------|--------|---------|
| Severity | 3x | Critical (4), High (3), Medium (2), Low (1) |
| Change frequency | 2x | High (3): changed weekly, Medium (2): changed monthly, Low (1): rarely changed |
| Business criticality | 2x | Core feature (3), Supporting feature (2), Internal tooling (1) |
| Effort estimate | 1x | Small (3): hours, Medium (2): days, Large (1): weeks |
| Age | 1x | Over 1 year (3), 3-12 months (2), Under 3 months (1) |

Calculate priority score: `(Severity * 3) + (Change Frequency * 2) + (Business Criticality * 2) + (Effort * 1) + (Age * 1)`

Higher scores indicate items that should be addressed sooner.

Sort the inventory by priority score descending.

## Step 8: Group Debt by Theme

Organize debt items into actionable groups that can be tackled as coherent units of work.

Common groupings:

| Theme | Includes | Typical Sprint Allocation |
|-------|----------|--------------------------|
| Security debt | Deprecated crypto, vulnerability-prone patterns, credential handling | Dedicated sprint |
| Dependency updates | Outdated packages, version conflicts, ecosystem migration | 1-2 days per sprint |
| Code hygiene | TODOs, FIXMEs, dead code, lint suppressions | Ongoing, 10% of sprint |
| Architecture debt | Coupling hotspots, misplaced responsibilities, pattern violations | Dedicated stories |
| Test debt | Missing tests, skipped tests, low coverage areas | 1 story per sprint |
| Documentation debt | Outdated docs, missing API documentation, stale README | Periodic cleanup |

For each group, provide:
- Total item count.
- Combined effort estimate.
- Recommended approach (dedicated sprint, spread across sprints, part of related features).

## Step 9: Generate Debt Inventory Report

Assemble all findings into a structured report.

```
## Technical Debt Inventory

**Project**: <name>
**Date**: <YYYY-MM-DD>
**Scope**: <directories analyzed>
**Total Items**: <count>

### Executive Summary

| Priority | Count | Estimated Effort |
|----------|-------|-----------------|
| Critical | <N> | <X days> |
| High | <N> | <X days> |
| Medium | <N> | <X days> |
| Low | <N> | <X days> |

### Top 10 Priority Items

| # | Type | Location | Description | Priority | Effort |
|---|------|----------|-------------|----------|--------|
| 1 | FIXME | src/auth.ts:45 | Race condition in token refresh | Critical | 2 days |
| 2 | Complexity | src/order.ts | 500 lines, 30 changes/month | High | 3 days |
| ... | ... | ... | ... | ... | ... |

### Debt by Category

#### Annotations (TODOs, FIXMEs)
<table of all annotation-based findings>

#### Deprecated Usage
<table of deprecated API usage>

#### Complexity Hotspots
<table of high-complexity files>

#### Outdated Dependencies
<table of outdated packages>

#### Code Duplication
<table of duplication indicators>

#### Test Coverage Gaps
<table of untested or under-tested areas>

### Thematic Groups
<groupings from Step 8 with suggested sprint allocation>

### Trends
<if previous debt reports exist, compare current vs previous>
```

## Step 10: Deliver and Suggest Tracking Approach

Present the report and recommend how to track debt reduction over time.

Suggestions:

1. **Periodic re-runs**: Schedule this analysis monthly or per-sprint to track trends.
2. **Debt budget**: Allocate a fixed percentage of sprint capacity (10-20%) to debt reduction.
3. **Boy Scout rule**: Improve debt items encountered during feature work (leave the code better than you found it).
4. **Debt ceiling**: Set a maximum acceptable debt count. When the ceiling is breached, prioritize debt reduction before new features.
5. **Integration with issue tracker**: Convert high-priority items to issues/tickets for backlog grooming.

If the user wants to save the report, write it using `filesystem` to a location like `docs/tech-debt-report-YYYY-MM-DD.md`.

## Edge Cases

- **Monorepos**: Analyze each package independently and provide per-package debt summaries alongside the aggregate view.
- **Generated code**: Exclude generated files (protobuf output, GraphQL codegen, ORM migrations) from complexity and annotation analysis. Generated code should not be refactored manually.
- **False positive annotations**: Some TODOs are legitimate future work items tracked in issue trackers. Cross-reference TODO comments containing issue numbers (e.g., `TODO(#123)`) with the issue tracker to check if they are already tracked.
- **New projects**: Young projects may have intentional debt taken to ship faster. Focus the report on critical items (security, correctness) rather than style and complexity for projects under 6 months old.
- **Very large codebases**: For projects with more than 10,000 source files, sample the top-level directories and the most-changed files rather than scanning everything. Report the sampling methodology.
- **No git history**: If the project has no git history (new clone with squashed history), change frequency and author analysis are not possible. Rely on static analysis only and note the limitation.

## Related Skills

- **e-refactor** (eskill-coding): Follow up with e-refactor after this skill to address the highest-priority technical debt items.
- **e-lint** (eskill-quality): Run e-lint alongside this skill to identify standards violations that contribute to technical debt.
- **e-deadcode** (eskill-coding): Run e-deadcode alongside this skill to include unused code in the technical debt inventory.
