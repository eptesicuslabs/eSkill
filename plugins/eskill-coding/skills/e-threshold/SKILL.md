---
name: e-threshold
description: "Checks test coverage against configurable thresholds and identifies the largest coverage gaps by module. Use when enforcing coverage policies, prioritizing test writing, or assessing risk areas. Also applies when: 'check coverage', 'are we above 80% coverage', 'which files need more tests', 'coverage report'."
---

# Coverage Threshold Check

This skill runs test coverage tools, parses the output, compares results against configurable thresholds, and identifies the modules with the largest coverage gaps. It supports multiple languages and coverage tools, and prioritizes gaps by risk to help teams allocate testing effort where it matters most.

## Prerequisites

- A project with an existing test suite.
- A coverage tool installed or installable for the target language.
- Optional: a coverage threshold policy (e.g., 80% line coverage).

## Workflow

### Step 1: Detect the Coverage Tool

Use `fs_list`, `fs_read`, and `data_file_read` from the eMCP data-file server to inspect manifest and configuration files:

| File / Content                                    | Coverage Tool       | Language   |
|---------------------------------------------------|---------------------|------------|
| package.json contains "vitest"                    | Vitest (c8/v8)      | TypeScript |
| package.json contains "jest"                      | Jest (built-in)     | TypeScript |
| package.json contains "nyc" or "istanbul"         | nyc/istanbul        | JavaScript |
| vitest.config.* has `coverage` section            | Vitest coverage     | TypeScript |
| jest.config.* has `collectCoverage`               | Jest coverage       | TypeScript |
| pyproject.toml contains "pytest-cov"              | pytest-cov          | Python     |
| setup.cfg or .coveragerc exists                   | coverage.py         | Python     |
| Cargo.toml `[dev-dependencies]` exists            | cargo-tarpaulin     | Rust       |
| go.mod exists                                     | go test -cover      | Go         |
| build.gradle contains "jacoco"                    | JaCoCo              | Java       |

If no coverage tool is detected, recommend one based on the project's language and test framework:

| Language   | Recommended Tool   | Install Command                        |
|------------|--------------------|----------------------------------------|
| TypeScript | Vitest coverage    | Already included with Vitest           |
| JavaScript | nyc                | `npm install --save-dev nyc`           |
| Python     | pytest-cov         | `pip install pytest-cov`               |
| Rust       | cargo-tarpaulin    | `cargo install cargo-tarpaulin`        |
| Go         | go test -cover     | Built-in                               |
| Java       | JaCoCo             | Add JaCoCo plugin to build config      |

### Step 2: Determine Thresholds

Check for existing coverage threshold configurations:

**Vitest/Jest**:
- Read `vitest.config.*` or `jest.config.*` for `coverageThreshold` settings.
- Example: `coverageThreshold: { global: { branches: 80, functions: 80, lines: 80, statements: 80 } }`.

**pytest-cov**:
- Read `.coveragerc`, `setup.cfg [tool:pytest]`, or `pyproject.toml [tool.pytest]` for `--cov-fail-under` value.

**cargo-tarpaulin**:
- Read `tarpaulin.toml` or command-line flags for `--fail-under` percentage.

**Go**:
- Go does not have a built-in threshold mechanism. Check for CI scripts that parse coverage output.

If no thresholds are configured, use these defaults and inform the user:

| Metric     | Default Threshold | Description                            |
|------------|-------------------|----------------------------------------|
| Lines      | 80%               | Percentage of executable lines covered |
| Branches   | 75%               | Percentage of conditional branches covered |
| Functions  | 80%               | Percentage of functions with at least one call |
| Statements | 80%               | Percentage of statements executed      |

Ask the user if they want to adjust these defaults before proceeding.

### Step 3: Run Coverage Collection

Execute the coverage command using `shell_exec` from the eMCP shell server:

**Vitest**:
```
npx vitest run --coverage --reporter=json --outputFile=coverage-report.json
```

**Jest**:
```
npx jest --coverage --coverageReporters=json-summary --json --outputFile=coverage-report.json
```

**nyc**:
```
npx nyc --reporter=json-summary npm test
```
Output goes to `coverage/coverage-summary.json`.

**pytest-cov**:
```
pytest --cov=src --cov-report=json:coverage.json
```

**cargo-tarpaulin**:
```
cargo tarpaulin --out json --output-dir coverage
```

**Go**:
```
go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out
```

**JaCoCo** (after build):
```
./gradlew jacocoTestReport
```
Output goes to `build/reports/jacoco/test/jacocoTestReport.xml`.

If the test suite fails, report the failures and stop. Coverage data from a partially-run test suite is unreliable.

Use `egrep_search_files` from the eMCP egrep server to quickly enumerate all test files in the project (matching patterns like `*.test.*`, `*_test.*`, `test_*.*`). This helps verify that the coverage run included all relevant test files.

### Step 4: Parse Coverage Data

Read the coverage output using `fs_read` and `data_file_read`:

**JSON summary format (Jest, Vitest, nyc)**:
Extract the `total` section for global metrics and per-file sections for file-level data. Each entry contains:
- `lines`: `{ total, covered, skipped, pct }`
- `statements`: `{ total, covered, skipped, pct }`
- `functions`: `{ total, covered, skipped, pct }`
- `branches`: `{ total, covered, skipped, pct }`

**pytest-cov JSON format**:
Extract `totals` for global metrics and `files` for per-file data. Each file entry contains:
- `summary`: `{ covered_lines, num_statements, percent_covered, missing_lines }`
- `missing_lines`: Array of line numbers not covered.

**Go coverage profile**:
Parse `coverage.out` line by line. Each line has format:
```
file:startline.col,endline.col count
```
Aggregate by file to compute per-file and total coverage.

**cargo-tarpaulin JSON**:
Extract from the JSON output. Per-file data includes covered and coverable line counts.

Record the following for each file:
- File path.
- Line coverage percentage.
- Branch coverage percentage (if available).
- Function coverage percentage (if available).
- Number of uncovered lines.
- List of uncovered line ranges (if available).

### Step 5: Compare Against Thresholds

Check each metric against the thresholds from Step 2:

**Global threshold check**:

| Metric     | Threshold | Actual  | Status |
|------------|-----------|---------|--------|
| Lines      | 80%       | 74.2%   | FAIL   |
| Branches   | 75%       | 71.8%   | FAIL   |
| Functions  | 80%       | 82.1%   | PASS   |
| Statements | 80%       | 75.0%   | FAIL   |

**Per-file threshold check** (if per-file thresholds are configured):
Apply the same comparison to each file individually. Files below the threshold are flagged.

Calculate the coverage deficit: how many additional lines/branches must be covered to reach the threshold.

```
Deficit calculation:
  total_lines = 5000
  covered_lines = 3710
  threshold = 80%
  required_covered = 5000 * 0.80 = 4000
  deficit = 4000 - 3710 = 290 lines
```

### Step 6: Identify Coverage Gaps by Module

Sort files by coverage gap (most uncovered lines first) to prioritize testing effort:

```
## Coverage Gaps (sorted by uncovered lines)

| File                              | Lines   | Coverage | Uncovered | Gap to 80% |
|-----------------------------------|---------|----------|-----------|------------|
| src/services/payment.ts           | 450     | 42.2%    | 260       | 170 lines  |
| src/services/auth.ts              | 320     | 58.1%    | 134       | 70 lines   |
| src/utils/parser.ts               | 280     | 62.5%    | 105       | 49 lines   |
| src/handlers/webhook.ts           | 200     | 65.0%    | 70        | 30 lines   |
| src/middleware/rate-limit.ts      | 150     | 70.0%    | 45        | 15 lines   |
```

Group gaps by directory or module to identify which areas of the codebase have systematically low coverage:

```
## Coverage by Directory

| Directory               | Files | Avg Coverage | Below Threshold |
|-------------------------|-------|--------------|-----------------|
| src/services/           | 12    | 55.3%        | 9               |
| src/handlers/           | 8     | 68.2%        | 5               |
| src/middleware/          | 4     | 72.1%        | 2               |
| src/utils/              | 15    | 81.4%        | 3               |
| src/models/             | 6     | 88.0%        | 0               |
```

### Step 7: Assess Risk of Uncovered Code

For the top coverage gaps identified in Step 6, use `ast_search` from the eMCP AST server to analyze what the uncovered code does:

**High-risk uncovered code** (prioritize testing):
- Error handling paths (catch blocks, error callbacks).
- Authentication and authorization logic.
- Payment processing or financial calculations.
- Data validation and sanitization.
- Database write operations (INSERT, UPDATE, DELETE).

**Medium-risk uncovered code**:
- Business logic with conditional branches.
- Data transformation and formatting.
- External API integration code.

**Low-risk uncovered code** (acceptable to defer):
- Logging and telemetry code.
- Debug-only code paths.
- Trivial getters and setters.
- Generated code or boilerplate.

Read the uncovered line ranges (from Step 4) using `fs_read` and classify each gap by risk level.

### Step 8: Generate the Report

Produce a structured coverage report:

```
## Coverage Threshold Report

### Global Coverage

| Metric     | Threshold | Actual  | Status | Deficit    |
|------------|-----------|---------|--------|------------|
| Lines      | 80%       | 74.2%   | FAIL   | 290 lines  |
| Branches   | 75%       | 71.8%   | FAIL   | 160 branches|
| Functions  | 80%       | 82.1%   | PASS   | --         |
| Statements | 80%       | 75.0%   | FAIL   | 250 stmts  |

### Highest-Impact Gaps

These files contribute the most to the coverage deficit. Testing them
first yields the largest improvement toward the threshold:

1. **src/services/payment.ts** (42.2% covered, 260 uncovered lines)
   - Lines 45-92: Error handling for payment gateway failures [HIGH RISK]
   - Lines 120-155: Refund processing logic [HIGH RISK]
   - Lines 200-240: Receipt generation [MEDIUM RISK]

2. **src/services/auth.ts** (58.1% covered, 134 uncovered lines)
   - Lines 30-52: Token refresh edge cases [HIGH RISK]
   - Lines 88-110: OAuth callback handling [HIGH RISK]
   - Lines 150-170: Session expiry cleanup [MEDIUM RISK]

3. **src/utils/parser.ts** (62.5% covered, 105 uncovered lines)
   - Lines 55-80: Malformed input handling [MEDIUM RISK]
   - Lines 100-140: Nested structure parsing [MEDIUM RISK]

### Coverage by Directory

| Directory               | Files | Avg Coverage | Below Threshold |
|-------------------------|-------|--------------|-----------------|
| src/services/           | 12    | 55.3%        | 9               |
| src/handlers/           | 8     | 68.2%        | 5               |
| src/utils/              | 15    | 81.4%        | 3               |

### Recommended Testing Order

Based on risk assessment and coverage deficit:
1. src/services/payment.ts -- high risk, largest gap
2. src/services/auth.ts -- high risk, auth-critical
3. src/handlers/webhook.ts -- medium risk, integration point
4. src/utils/parser.ts -- medium risk, input validation
5. src/middleware/rate-limit.ts -- low risk, small gap
```

### Step 9: Suggest Threshold Configuration

If the project does not have coverage thresholds configured, suggest adding them to prevent coverage regression:

**Vitest** (vitest.config.ts):
```typescript
export default defineConfig({
  test: {
    coverage: {
      thresholds: {
        lines: 80,
        branches: 75,
        functions: 80,
        statements: 80
      }
    }
  }
});
```

**Jest** (jest.config.js):
```javascript
module.exports = {
  coverageThreshold: {
    global: {
      branches: 75,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

**pytest-cov** (pyproject.toml):
```toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-fail-under=80"
```

**Go** (CI script):
```bash
coverage=$(go test -coverprofile=coverage.out ./... | grep total | awk '{print $3}' | tr -d '%')
if [ $(echo "$coverage < 80" | bc) -eq 1 ]; then
  echo "Coverage $coverage% is below 80% threshold"
  exit 1
fi
```

Recommend adding the threshold check to the CI pipeline so coverage regressions are caught before merge.

## Notes

- Coverage percentage alone does not indicate test quality. A test that executes a code path without meaningful assertions provides coverage but not confidence. This skill identifies quantity gaps; the e-testgen skill helps with quality.
- Branch coverage is more informative than line coverage for conditional logic. A function may have 100% line coverage but miss important branches if only one path through each conditional is tested.
- Coverage tools have overhead. If the test suite is large, consider running coverage only in CI or on a subset of tests during local development.
- Some code is intentionally untested (debug utilities, development-only features). Use coverage ignore comments (`/* istanbul ignore next */`, `# pragma: no cover`, `// nolint`) to exclude these from threshold calculations rather than writing meaningless tests.

## Edge Cases

- **Coverage tools not installed**: The project may not have a coverage tool configured. Detect the test framework and recommend the appropriate coverage tool (c8/istanbul for Node, coverage.py for Python, tarpaulin for Rust) before running.
- **Threshold set too high for legacy code**: A legacy project with 30% coverage cannot realistically reach 80% in one sprint. Recommend incremental thresholds (e.g., "no regression" + 1% per sprint) rather than a single ambitious target.
- **Coverage ignore comments masking real gaps**: Overuse of `istanbul ignore` or `pragma: no cover` can artificially inflate coverage. Count and report the number of ignored lines alongside actual coverage.
- **Test-only code inflating coverage**: If test helper files are included in the coverage scope, they inflate the percentage. Exclude test directories from the coverage source scope.
- **Branch coverage vs. line coverage disagreement**: A function can have 100% line coverage but low branch coverage if conditional branches are tested with only one path. Report both metrics and flag disagreements.

## Related Skills

- **e-testgen** (eskill-coding): Run e-testgen after this skill to generate tests for modules that fall below coverage thresholds.
- **e-coverage** (eskill-testing): Follow up with e-coverage after this skill to produce a formatted coverage report for the team.
