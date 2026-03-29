---
name: e-lint
description: "Analyzes code against linter configs and convention rules to produce a quality report. Use when enforcing project standards, reviewing code for style violations, or onboarding to consistent practices. Also applies when: 'check lint rules', 'are we following conventions', 'style check', 'formatting issues', 'code quality'."
---

# Code Standards Enforcement

This skill analyzes code against configurable quality standards, combining existing linter output with additional AST-based checks that go beyond what standard linters catch. It produces a comprehensive quality report with actionable findings.

## Prerequisites

- A project with source code files to analyze.
- The eMCP filesystem, egrep_search, data_file_read, and ast_search servers available.
- Existing linter configs (.eslintrc, .pylintrc, rustfmt.toml, etc.) or willingness to use language-default rules.

## Step 1: Detect Existing Linter and Formatter Configuration

Scan the project root and common configuration directories for existing tool configurations.

1. Use `filesystem` to check for the following files at the project root:
   - ESLint: `.eslintrc`, `.eslintrc.js`, `.eslintrc.json`, `.eslintrc.yml`, `eslint.config.js`, `eslint.config.mjs`
   - Prettier: `.prettierrc`, `.prettierrc.js`, `.prettierrc.json`, `prettier.config.js`
   - TypeScript: `tsconfig.json`
   - Python flake8: `.flake8`, `setup.cfg` (with `[flake8]` section), `tox.ini`
   - Python black: `pyproject.toml` (with `[tool.black]` section)
   - Python mypy: `mypy.ini`, `.mypy.ini`, `pyproject.toml` (with `[tool.mypy]` section)
   - Rust: `rustfmt.toml`, `.rustfmt.toml`, `clippy.toml`
   - EditorConfig: `.editorconfig`
   - Stylelint: `.stylelintrc`, `.stylelintrc.json`
2. Read each detected configuration file using `data_file_read` or `filesystem` `fs_read`.
3. Record the detected tools and their configurations for use in subsequent steps.
4. Note any conflicts between tool configurations (e.g., ESLint and Prettier disagreeing on quote style).

## Step 2: Suggest Default Configuration

If no linter or formatter configuration is detected:

1. Determine the project language from package manifests (see e-scan Step 1 approach).
2. Suggest a baseline configuration appropriate for the language and framework:
   - JavaScript/TypeScript: ESLint with recommended rules plus Prettier for formatting.
   - Python: flake8 for linting, black for formatting, mypy for type checking.
   - Rust: rustfmt for formatting, clippy for linting (both are standard).
   - Go: gofmt and go vet are standard and typically do not require configuration.
3. Provide the suggested configuration as part of the report output, not as a file write (the user decides whether to adopt it).

## Step 3: Run Existing Linters

For each detected linter, execute it and capture output.

1. Use `shell` to run the linter with JSON or machine-readable output format where available:
   - ESLint: `npx eslint . --format json --no-error-on-unmatched-pattern`
   - flake8: `flake8 --format json` or `flake8 --format default`
   - mypy: `mypy . --no-error-summary`
   - clippy: `cargo clippy --message-format json`
   - Stylelint: `npx stylelint "**/*.css" --formatter json`
2. Parse the output to extract: file path, line number, column, rule ID, message, severity.
3. Store these findings in the working results, tagged as "linter" source.
4. If a linter is not installed or fails to run, record this and proceed with AST-based checks.

## Step 4: Run AST-Based Quality Checks

Perform additional structural analysis using `ast_search` for patterns that standard linters may not cover or may not enforce strictly enough. For text-based style violations (naming patterns, comment style, trailing whitespace), use `egrep_search` to scan the entire codebase instantly via its trigram index -- this is significantly faster than `fs_search` for broad pattern matching across many files.

### Function Length

- Use `ast_search` to find all function declarations, arrow functions, and method definitions.
- Count the number of lines or statements in each function body.
- Flag functions exceeding a configurable threshold (default: 50 lines or 30 statements).
- Report the function name, file, starting line, and line count.

### Cyclomatic Complexity

- For each function, count branch points that increase cyclomatic complexity:
  - `if` / `else if` / `else` statements
  - `switch` / `case` clauses
  - `for` / `while` / `do-while` loops
  - `catch` blocks
  - Logical operators `&&` and `||` in conditions
  - Ternary expressions `? :`
  - Null coalescing `??` and optional chaining `?.` in conditional contexts
- Complexity = 1 + number of branch points.
- Flag functions exceeding the threshold (default: 15).
- Report the function name, file, line, and computed complexity.

### Naming Conventions

- Use `egrep_search` to quickly find naming convention violations across the entire codebase (e.g., camelCase identifiers in a snake_case Python project, or UPPER_SNAKE_CASE violations). This is faster than scanning files individually with `fs_search`.
- Use `ast_search` to extract identifiers and their declaration context:
  - Variable declarations: check against the expected convention (camelCase for JS/TS, snake_case for Python/Rust).
  - Function names: same convention as variables in most languages.
  - Class names: PascalCase in nearly all languages.
  - Constants: UPPER_SNAKE_CASE for true constants.
  - File names: check against project convention (kebab-case, camelCase, snake_case).
- Flag names that deviate from the expected convention.
- Exclude external identifiers (imported names, framework-required names).

### Error Handling Patterns

- Search for empty `catch` blocks (catch block with no statements or only a comment).
- Search for `catch` blocks that swallow errors (catch without rethrowing, logging, or returning an error).
- Search for functions that return inconsistent types (sometimes a value, sometimes undefined).
- In async code: search for Promises without `.catch()` or missing try/catch around await.
- Flag error handling that does not preserve the original error (e.g., throwing a new error without chaining the cause).

### Import Organization

- Extract all import/require statements from each file using `ast_search`.
- Check whether imports follow a consistent grouping pattern:
  - Group 1: Built-in/standard library modules.
  - Group 2: External dependencies (from node_modules or site-packages).
  - Group 3: Internal project modules (relative imports).
- Check whether imports within each group are alphabetically sorted.
- Flag files with disorganized imports.

### Dead Code Detection

- Use `lsp_diagnostics` to identify unused variables, unused imports, and unreachable code.
- Use `egrep_search` to rapidly locate commented-out code blocks, TODO/FIXME markers, and debug-only statements across the entire codebase.
- Use `ast_search` to find:
  - Functions that are defined but never called (cross-reference with `lsp_references`).
  - Variables that are assigned but never read.
  - Code after unconditional return, break, continue, or throw statements.
  - Commented-out code blocks (heuristic: multi-line comments containing code-like syntax).
- Distinguish between truly dead code and code that is used dynamically (reflection, string-based access).

## Step 5: Gather LSP Diagnostics

Use `lsp_diagnostics` to collect IDE-level analysis results.

1. Request diagnostics for all files in the project source directories.
2. Extract warnings and errors that are not already covered by linter output.
3. Common LSP diagnostics to capture:
   - Type errors (TypeScript strict mode, mypy).
   - Deprecated API usage.
   - Unused exports.
   - Missing return type annotations.
   - Implicit any types.
4. Add these to the working results, tagged as "lsp" source.

## Step 6: Categorize All Findings

Assign each finding to one of three categories:

### Error (Must Fix)

- Type errors that would cause runtime failures.
- Security-related linter rules (no-eval, no-implied-eval).
- Unreachable code indicating logic errors.
- Syntax errors or malformed constructs.

### Warning (Should Fix)

- Functions exceeding complexity or length thresholds.
- Empty catch blocks.
- Unused variables and imports.
- Missing error handling in async code.
- Deprecated API usage.
- Naming convention violations in public APIs.

### Style (Cosmetic)

- Import ordering issues.
- Naming convention violations in private/internal code.
- Minor formatting inconsistencies not caught by formatters.
- Comment style inconsistencies.
- Trailing whitespace or inconsistent line endings.

## Step 7: Generate the Findings Report

Structure the report by file for easy review.

### Per-File Section

For each file with findings:
- File path (absolute, forward slashes).
- Total findings: errors, warnings, style issues.
- Each finding:
  - Line number and column.
  - Category (error / warning / style).
  - Source (linter name, AST check, LSP).
  - Rule ID or check name.
  - Description of the issue.
  - Suggested fix (where applicable).

### Ordering

- Files ordered by number of findings (most findings first).
- Within each file, findings ordered by severity (errors first), then by line number.

## Step 8: Generate Summary Statistics

Provide an overview of the entire scan.

- Total files scanned.
- Total findings: breakdown by category (error, warning, style).
- Findings by source (ESLint, flake8, AST checks, LSP).
- Top 10 most violated rules or checks.
- Cleanest files: files with zero findings (list up to 10).
- Most problematic files: top 10 files by finding count.
- Average findings per file.
- Comparison with previous scan if a baseline is available.

## Step 9: Suggest Configuration Improvements

Based on the findings, recommend additions to existing linter/formatter configurations.

1. If a particular pattern appears frequently and a linter rule exists for it, suggest enabling that rule.
   - Example: if many functions exceed 50 lines and ESLint is configured, suggest adding `max-lines-per-function` rule.
   - Example: if naming violations are frequent in Python, suggest configuring `pep8-naming` plugin for flake8.
2. If a formatter could prevent a class of style findings, suggest adding it.
3. If type checking could catch certain errors, suggest enabling strict mode or adding a type checker.
4. Present suggestions as specific configuration snippets that can be added to existing config files.
5. Note any rule conflicts between suggestions and existing configuration.

## Safety Protocol

1. This skill produces a report. It does not auto-fix code by default.
2. If the user asks to apply fixes, present each proposed change in diff format before modifying any file.
3. Group fixes by category (formatting, imports, naming) and apply one category at a time with user confirmation between each.
4. Never apply fixes that change program behavior (e.g., removing "dead code" that may be used via reflection). Only auto-fix purely cosmetic issues (whitespace, import ordering, formatting).
5. After applying fixes, re-run the relevant linter to confirm the fixes resolved the findings without introducing new ones.

## Reference: Common Rule Thresholds

These are sensible defaults. Adjust based on project conventions.

| Check                    | Default Threshold | Notes                                    |
|--------------------------|-------------------|------------------------------------------|
| Max function lines       | 50                | Count only non-empty, non-comment lines  |
| Max function statements  | 30                | Count executable statements              |
| Max cyclomatic complexity| 15                | Per function                             |
| Max file lines           | 500               | Suggests file should be split            |
| Max function parameters  | 5                 | Consider using an options object          |
| Max nesting depth        | 4                 | Deep nesting harms readability           |
| Max line length          | 120               | Defer to formatter if configured         |

## Edge Cases

- **Conflicting linter and formatter configs**: ESLint rules may conflict with Prettier formatting (e.g., semicolons, quotes). Detect both tools and recommend eslint-config-prettier or equivalent integration.
- **Generated code triggering violations**: Protobuf stubs, GraphQL codegen output, and ORM-generated models should be excluded from linting. Check for `.eslintignore`, `exclude` patterns, or generated file markers.
- **Legacy code with thousands of violations**: Running lint on a legacy codebase may produce overwhelming output. Recommend a baseline approach: suppress existing violations and only enforce rules on new/changed code.
- **Monorepo with per-package configs**: Different packages in a monorepo may have different lint rules. Detect per-directory configs and run linting per package rather than with a single root config.
- **Custom rules and plugins**: Some projects use custom ESLint/Pylint rules or internal plugins. Detect custom rule references and note when a rule cannot be evaluated without the custom plugin installed.

## Related Skills

- **e-review** (eskill-coding): Run e-review after this skill to verify that standards violations are addressed before review.
- **e-refactor** (eskill-coding): Follow up with e-refactor after this skill to systematically fix code standards violations across the codebase.
