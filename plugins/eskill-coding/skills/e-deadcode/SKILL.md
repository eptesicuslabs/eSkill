---
name: e-deadcode
description: "Identifies unreachable code, unused exports, and orphan files by cross-referencing LSP usage data with AST definitions. Use during codebase cleanup, before refactors, or to reduce bundle size. Also applies when: 'find dead code', 'unused exports', 'orphan files', 'what can I delete safely'."
---

# Dead Code Finder

This skill identifies dead code in a codebase by cross-referencing LSP reference data with AST-extracted definitions. Dead code includes unused exports, unreachable statements, orphan files, unused variables, commented-out code blocks, and dead CSS selectors. Removing dead code reduces maintenance burden, shrinks bundle sizes, and improves codebase clarity.

## Prerequisites

- LSP server running for the project language (strongly recommended for accuracy).
- Access to the project's source files.
- A clear scope: single file, directory, or entire codebase.

## Workflow

### Step 1: Define the Scan Scope

Determine which files and directories to scan. Dead code detection is expensive on large codebases, so scoping is important.

| Scope              | When to Use                                  | Approach                          |
|--------------------|----------------------------------------------|-----------------------------------|
| Single file        | Cleaning up a specific module                | Scan exports and internal symbols |
| Directory          | Cleaning a package or feature area           | Scan all files in directory       |
| Changed files only | Pre-merge cleanup                            | Use `git_log` to get changed files|
| Full codebase      | Major cleanup or bundle size reduction       | Scan all source directories       |

Use `fs_list` to enumerate files in the target scope. Filter by source file extensions:

| Language     | Extensions                    |
|--------------|-------------------------------|
| JavaScript   | `.js`, `.jsx`, `.mjs`, `.cjs` |
| TypeScript   | `.ts`, `.tsx`, `.mts`, `.cts` |
| Python       | `.py`                         |
| Ruby         | `.rb`                         |
| Go           | `.go`                         |
| Rust         | `.rs`                         |
| CSS          | `.css`, `.scss`, `.less`      |

Exclude test files, configuration files, generated files, and vendor/node_modules directories from the dead code scan. These files may legitimately reference code that appears unused in the main source.

### Step 2: Extract All Definitions

For each source file in scope, use `lsp_symbols` from the eMCP LSP server to extract all defined symbols:

- **Exported functions**: Functions with `export` keyword, or listed in `module.exports`, `__all__`, or `pub` visibility.
- **Exported classes**: Classes with export visibility.
- **Exported constants and variables**: Named exports of values.
- **Exported types and interfaces**: Type-level exports (TypeScript, Rust traits).
- **Internal functions**: Non-exported functions defined at module scope.
- **Internal variables**: Module-scope variables not exported.

For each symbol, record:
- File path and line number.
- Symbol name and kind (function, class, variable, type).
- Visibility (exported, internal, private).

If LSP is unavailable, fall back to `ast_search` from the eMCP AST server with language-specific patterns for function definitions, class definitions, and export statements.

### Step 3: Find References for Each Symbol

For each exported symbol, use `lsp_references` from the eMCP LSP server to find all references across the codebase:

- A symbol with zero external references (referenced only in its own file, at its definition site) is a candidate for dead code.
- A symbol referenced only in test files may be dead in production code but still needed for testing. Flag these separately.
- A symbol referenced only in type positions (e.g., used in a type annotation but never called) may indicate dead runtime code with live type usage.

For internal (non-exported) symbols, check references within the same file. An internal function with no callers in its own module is dead.

Process symbols in batches to avoid excessive LSP queries. Group symbols by file and query references for all symbols in a file before moving to the next. For large codebases, use `egrep_search` from the eMCP egrep server for fast trigram-indexed cross-reference checks before confirming with LSP. This significantly reduces the number of LSP queries needed.

### Step 4: Detect Unreachable Code

Use `ast_search` to find code that is structurally unreachable:

**Statements after unconditional returns**:
- Code following a `return`, `throw`, `raise`, `panic!`, `os.Exit`, `break`, or `continue` at the same block level.
- Pattern: any statement in a block that follows a terminating statement.

**Dead branches**:
- `if (false)` or `if (true) { ... } else { ... }` where the else branch is unreachable.
- Conditions that are compile-time constants evaluating to a fixed value.
- Note: only flag conditions that are obviously constant. Do not attempt to evaluate complex expressions.

**Unreachable match/switch arms**:
- A `default` or `_` arm preceded by arms that cover all possible values.
- Duplicate case values in switch statements.

**Empty catch/except blocks**:
- `catch (e) {}` or `except Exception: pass` -- while not unreachable, these silently swallow errors and are often vestigial dead code.

### Step 5: Detect Orphan Files

Orphan files are source files that are not imported by any other file in the project. They represent entire modules of dead code.

1. For each source file in scope, use `egrep_search` from the eMCP egrep server to search the codebase for import statements referencing the file. Prefer `egrep_search` over `fs_search` for this step as it uses trigram indexing for near-instant results on large codebases.
2. Check for both relative imports (`./module`, `../utils/helper`) and package imports (`@org/package/module`).
3. Account for index files: a directory import (`import from './utils'`) resolves to `./utils/index.ts`.
4. Check entry points: the application's main entry file(s) and any files referenced in build configurations are not orphans even if nothing imports them.
5. Check for dynamic imports: `import()` expressions, `require()` with variable paths, and framework-specific lazy loading patterns.

Files with no incoming imports and that are not entry points are orphan candidates. Flag them for manual review.

Also check for orphan test files: test files whose corresponding source file has been deleted. These tests are likely stale.

### Step 6: Detect Unused Variables and Parameters

Use `lsp_diagnostics` from the eMCP LSP server to retrieve compiler or linter warnings about unused symbols:

- TypeScript: `noUnusedLocals` and `noUnusedParameters` diagnostics.
- Python: `F841` (local variable assigned but never used) from flake8/ruff.
- Rust: `unused_variables`, `dead_code` compiler warnings.
- Go: Unused variables are compile errors (already caught).

If LSP diagnostics are not available or do not cover unused variables, use `ast_search` to find variable declarations and then `lsp_references` to check if each has any read references beyond its assignment.

Exclude variables with names that indicate intentional non-use: `_`, `__`, `_unused`, `_ignore`.

### Step 7: Detect Commented-Out Code Blocks

Use `fs_search` (content mode) to find commented-out code blocks. These are comments that contain syntactically valid code rather than natural language descriptions.

Heuristics for identifying commented-out code:

| Indicator                         | Example                                  |
|-----------------------------------|------------------------------------------|
| Contains assignment operators     | `// const x = getValue();`               |
| Contains function calls           | `// processData(input);`                 |
| Contains control flow keywords    | `// if (condition) {`                    |
| Contains import/require statements| `// import { foo } from './bar';`        |
| Multi-line block with code syntax | `/* return items.filter(i => i.active) */`|
| Consecutive single-line comments with code | `// for (const item of list) {` |

Exclude:
- JSDoc/docstring examples (code inside documentation blocks).
- TODO/FIXME comments that reference code patterns.
- License headers and copyright notices.

Report commented-out code blocks with their location and a recommendation to either restore or delete them.

### Step 8: Detect Dead CSS Selectors

If the project contains CSS/SCSS/LESS files, check for selectors that are not referenced in any template or component file:

1. Use `ast_search` or `fs_search` to extract all CSS selectors from stylesheets.
2. For each class selector (`.classname`), search template files (`.html`, `.jsx`, `.tsx`, `.vue`, `.svelte`, `.erb`) for references to that class name.
3. For each ID selector (`#idname`), search similarly.
4. Account for dynamic class construction: `className={styles.name}` (CSS Modules), `class:name` (Svelte), template literals with class names.

Note: Dynamic class names constructed at runtime (e.g., `class={`btn-${variant}`}`) cannot be statically analyzed. Flag selectors matching common dynamic patterns as low confidence.

### Step 9: Generate the Report

Produce a structured report organized by category:

```
## Dead Code Report

### Summary
- Files scanned: 128
- Unused exports: 12
- Unreachable code blocks: 5
- Orphan files: 3
- Unused variables: 18
- Commented-out code blocks: 7
- Dead CSS selectors: 14
- Estimated removable lines: ~450

### Unused Exports

| File                          | Symbol          | Kind     | References | Note              |
|-------------------------------|-----------------|----------|------------|-------------------|
| src/utils/format.ts           | formatCurrency  | function | 0          | Safe to remove    |
| src/utils/format.ts           | formatPercent   | function | 0          | Safe to remove    |
| src/services/legacy-auth.ts   | LegacyAuth      | class    | 0          | Entire class unused|
| src/types/deprecated.ts       | OldConfig       | type     | 1 (test)   | Used only in tests|

### Unreachable Code

| File                          | Line  | Pattern                    |
|-------------------------------|-------|----------------------------|
| src/handlers/payment.ts       | 89    | Code after unconditional return |
| src/utils/parse.ts            | 145   | Dead else branch (condition always true) |

### Orphan Files

| File                          | Last Modified | Lines | Recommendation     |
|-------------------------------|---------------|-------|--------------------|
| src/services/old-mailer.ts    | 2024-03-15    | 230   | Review and delete   |
| src/utils/deprecated-hash.ts  | 2023-11-02    | 45    | Review and delete   |
| src/components/unused-modal.tsx| 2024-01-20   | 180   | Review and delete   |

### Commented-Out Code

| File                          | Lines     | Content Preview                  |
|-------------------------------|-----------|----------------------------------|
| src/services/auth.ts          | 34-42     | `// const oldToken = ...`        |
| src/routes/api.ts             | 112-118   | `// router.get('/v1/legacy'...`  |

### Removal Safety Notes
- Verify that no dynamic imports or reflection reference the symbols before deleting.
- Exports used only in tests: confirm whether the test should be removed too.
- Orphan files: check git history for recent activity before deleting.
```

### Step 10: Assess Removal Safety

For each finding, evaluate whether removal is safe:

**Safe to remove**:
- Unreachable code after returns (structurally unreachable).
- Internal variables with no references beyond assignment.
- Commented-out code blocks.

**Review before removing**:
- Unused exports: Check for dynamic imports, `require()` with variable paths, or reflection.
- Orphan files: Check git log using `git_log` from the eMCP git server for recent activity. A recently modified orphan may be a work-in-progress.
- Test-only references: The test may be testing an intentionally isolated code path.

**Do not remove automatically**:
- Symbols that serve as public API contracts (documented in README or API docs).
- Symbols referenced in configuration files, build scripts, or deployment manifests.
- CSS selectors that may be applied dynamically or referenced in third-party code.

Present the safety assessment alongside each finding so the user can make informed decisions about what to delete.

## Notes

- Dead code detection is inherently conservative. False positives occur when code is referenced through dynamic patterns that static analysis cannot trace. Prefer false positives (flagging live code as dead) over false negatives (missing actual dead code), as manual review catches false positives.
- For monorepos, run the scan across all packages. A symbol exported from one package but unused in all other packages and applications is dead at the monorepo level even if it has references within its own package's tests.
- This skill produces a snapshot. Run it periodically or integrate the findings into a CI check to prevent dead code accumulation.

## Edge Cases

- **Dynamic imports and lazy loading**: Code referenced only through `import()` expressions or framework-specific lazy loading (React.lazy, Vue async components) may appear unused to static analysis. Check for dynamic import patterns before classifying as dead.
- **Plugin and extension systems**: Functions registered as plugin hooks, middleware, or event listeners may have no static callers but are invoked dynamically. Detect registration patterns before flagging.
- **Public library exports**: If the project is a published library, all public API exports are "used" by external consumers even if no internal callers exist. Only flag unexported or internal-only dead code.
- **Conditional compilation and feature flags**: Code guarded by build-time flags (ifdef, process.env.FEATURE_X) may be dead in one build configuration but alive in another. Report the flag dependency.
- **Test helpers and fixtures**: Utility functions in test directories may only be used by a subset of tests. Cross-reference test utility usage across the full test suite rather than individual test files.

## Related Skills

- **e-refactor** (eskill-coding): Follow up with e-refactor after this skill to safely remove the identified dead code.
- **e-bundle** (eskill-frontend): Run e-bundle alongside this skill to quantify the size impact of unused code on frontend bundles.
