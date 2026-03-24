---
name: test-coverage-reporter
description: "Generates detailed test coverage reports with gap analysis, risk-weighted prioritization, and per-function breakdown. Use when improving coverage, setting targets, or identifying high-risk untested code. Also applies when: 'coverage report', 'which code is untested', 'coverage gaps', 'risk analysis of untested code'."
---

# Test Coverage Reporter

This skill runs coverage collection, parses the output, computes risk-weighted prioritization based on complexity and coverage gaps, and produces per-file and per-function breakdowns with actionable recommendations.

## Prerequisites

- A project with an existing test suite.
- A coverage tool installed or installable for the project's language.
- Tests that can be run from the command line.

## Workflow

### Step 1: Detect Coverage Tooling

Identify the project's language and available coverage tools by reading manifest files with `filesystem` tools (list_directory, read_file):

| Language    | Coverage Tool         | Install / Enable                          | Output Format    |
|-------------|-----------------------|-------------------------------------------|------------------|
| JS/TS       | v8 (via Vitest/Jest)  | `--coverage` flag                         | lcov, json       |
| JS/TS       | istanbul / nyc        | `npx nyc` or `c8`                         | lcov, json       |
| Python      | coverage.py           | `pip install coverage`                    | xml, json, lcov  |
| Python      | pytest-cov            | `pip install pytest-cov`                  | xml, json, lcov  |
| Rust        | cargo-tarpaulin       | `cargo install cargo-tarpaulin`           | lcov, json       |
| Rust        | cargo-llvm-cov        | `cargo install cargo-llvm-cov`            | lcov, json       |
| Go          | go test -cover        | Built-in                                  | coverprofile     |
| Java        | JaCoCo                | Gradle/Maven plugin                       | xml, csv         |
| C#          | coverlet              | `dotnet add package coverlet.collector`   | cobertura, lcov  |

Check for existing coverage configuration:
- `vitest.config.ts` or `jest.config.js` with `coverage` section.
- `.nycrc` or `.c8rc` for Node.js.
- `.coveragerc` or `pyproject.toml [tool.coverage]` for Python.
- `tarpaulin.toml` for Rust.

Use `data_file` tools (data_file_read) to parse configuration and identify the output directory and format.

### Step 2: Run Coverage Collection

Execute the test suite with coverage enabled using `test_run` from the eMCP test server:

| Ecosystem  | Command                                            | Output Location                |
|------------|----------------------------------------------------|--------------------------------|
| Vitest     | `npx vitest run --coverage`                        | `coverage/`                    |
| Jest       | `npx jest --coverage`                              | `coverage/`                    |
| nyc        | `npx nyc npx mocha`                                | `.nyc_output/`, `coverage/`    |
| pytest-cov | `pytest --cov=src --cov-report=json`               | `coverage.json`                |
| coverage.py| `coverage run -m pytest && coverage json`          | `coverage.json`                |
| tarpaulin  | `cargo tarpaulin --out json`                       | `tarpaulin-report.json`        |
| llvm-cov   | `cargo llvm-cov --json`                            | stdout (capture to file)       |
| Go         | `go test -coverprofile=coverage.out ./...`         | `coverage.out`                 |
| JaCoCo     | `./gradlew jacocoTestReport`                       | `build/reports/jacoco/`        |

Use `shell` tools (run_command) if `test_run` does not support the coverage flags natively. Ensure the output format is machine-readable (JSON, lcov, or XML).

If coverage collection fails, check:
1. Are all tests passing? Coverage tools may abort on test failures.
2. Is the coverage tool installed? Provide the install command if missing.
3. Is source map support needed for TypeScript? Check for `sourceMaps: true` in tsconfig.

### Step 3: Parse Coverage Data

Read the coverage output using `filesystem` tools and parse it with `data_file` tools.

**JSON format** (Vitest, Jest, coverage.py, tarpaulin): Parse the JSON directly. Extract per-file coverage metrics.

**LCOV format**: Parse the line-based format:
```
SF:src/services/auth.ts      # Source file
FN:10,validateToken           # Function at line 10
FNDA:5,validateToken          # Function called 5 times
FNF:3                         # Functions found: 3
FNH:2                         # Functions hit: 2
DA:10,5                       # Line 10 executed 5 times
DA:15,0                       # Line 15 never executed
LF:45                         # Lines found: 45
LH:38                         # Lines hit: 38
BRF:12                        # Branches found: 12
BRH:8                         # Branches hit: 8
end_of_record
```

**Cobertura XML**: Parse the XML structure for `<package>`, `<class>`, and `<method>` elements with `line-rate` and `branch-rate` attributes.

Extract and store per-file metrics:

| Metric          | Definition                                  |
|-----------------|---------------------------------------------|
| Line coverage   | Lines executed / total executable lines     |
| Branch coverage | Branches taken / total branches             |
| Function coverage| Functions called / total functions          |
| Statement coverage| Statements executed / total statements    |

### Step 4: Compute Per-Function Coverage

For granular analysis, extract function-level coverage. Use `ast_search` from the eMCP AST server and `lsp_symbols` from the eMCP LSP server to map coverage data to named functions.

For each function, determine:

1. **Lines in function**: Use `ast_search` to get function start and end lines.
2. **Covered lines**: Cross-reference with coverage data to count executed lines within the function range.
3. **Uncovered lines**: Lines within the function range with zero execution count.
4. **Branch coverage**: Branches within the function that were not taken.

Build a per-function table:

| File                  | Function          | Lines | Covered | Uncovered | Line % | Branch % |
|-----------------------|-------------------|-------|---------|-----------|--------|----------|
| src/services/auth.ts  | validateToken     | 25    | 20      | 5         | 80.0%  | 66.7%    |
| src/services/auth.ts  | refreshSession    | 18    | 18      | 0         | 100.0% | 100.0%   |
| src/services/auth.ts  | revokeToken       | 12    | 3       | 9         | 25.0%  | 0.0%     |
| src/services/cart.ts  | calculateTotal    | 30    | 28      | 2         | 93.3%  | 87.5%    |

### Step 5: Estimate Cyclomatic Complexity

Compute or approximate cyclomatic complexity for each function to enable risk scoring. Use `ast_search` to count decision points:

| Decision Point            | Complexity Increment |
|---------------------------|---------------------|
| `if` / `else if`          | +1 each             |
| `for` / `while` / `do`   | +1 each             |
| `case` in switch          | +1 each             |
| `&&` / `\|\|` in conditions | +1 each          |
| `catch` block             | +1 each             |
| `? :` ternary             | +1 each             |
| Base complexity           | 1                   |

For each function, count the decision points by searching for these patterns with `ast_search`. The total is the cyclomatic complexity.

Complexity classification:

| Complexity | Classification | Testing Effort   |
|------------|----------------|------------------|
| 1-5        | Low            | Minimal          |
| 6-10       | Moderate       | Standard         |
| 11-20      | High           | Thorough         |
| 21+        | Very high      | Refactor advised |

### Step 6: Compute Risk Scores

Combine coverage and complexity into a risk score that prioritizes what to test next. The principle: high complexity with low coverage represents the highest risk.

Risk score formula: `risk = complexity * (1 - line_coverage_ratio)`

| Function          | Complexity | Coverage | Risk Score | Priority  |
|-------------------|-----------|----------|------------|-----------|
| revokeToken       | 8         | 25.0%    | 6.00       | Critical  |
| validateToken     | 12        | 80.0%    | 2.40       | Medium    |
| calculateTotal    | 15        | 93.3%    | 1.00       | Low       |
| refreshSession    | 4         | 100.0%   | 0.00       | None      |

Risk priority thresholds:

| Risk Score | Priority   | Action                                     |
|------------|------------|--------------------------------------------|
| > 5.0      | Critical   | Write tests immediately                    |
| 2.1-5.0    | High       | Schedule for next sprint                   |
| 1.0-2.0    | Medium     | Add when modifying the function            |
| 0.1-0.9    | Low        | Nice to have                               |
| 0.0        | None       | Fully covered                              |

### Step 7: Compare Against Thresholds

Check coverage against project-defined thresholds. Use `filesystem` tools to read threshold configuration:

- Vitest/Jest: `coverageThreshold` in config.
- pytest-cov: `--cov-fail-under` flag or `[tool.coverage.report] fail_under` in pyproject.toml.
- Custom: `.coverage-thresholds.json` or similar.

If no thresholds are defined, use industry baselines:

| Metric     | Minimum | Recommended | Stretch |
|------------|---------|-------------|---------|
| Line       | 60%     | 80%         | 90%     |
| Branch     | 50%     | 70%         | 85%     |
| Function   | 70%     | 85%         | 95%     |

Report threshold compliance per directory and overall:

| Directory          | Line % | Threshold | Status |
|--------------------|--------|-----------|--------|
| src/services/      | 82.3%  | 80%       | Pass   |
| src/utils/         | 71.5%  | 80%       | Fail   |
| src/controllers/   | 88.1%  | 80%       | Pass   |
| Overall            | 80.6%  | 80%       | Pass   |

### Step 8: Generate the Coverage Report

Compile the full report using `data_file` tools to write structured output:

```
## Test Coverage Report

### Overall Summary
| Metric    | Covered | Total | Percentage |
|-----------|---------|-------|------------|
| Lines     | 1,245   | 1,550 | 80.3%      |
| Branches  | 312     | 420   | 74.3%      |
| Functions | 89      | 102   | 87.3%      |

### Per-Directory Breakdown
| Directory          | Lines  | Branches | Functions |
|--------------------|--------|----------|-----------|
| src/services/      | 82.3%  | 76.1%    | 90.0%     |
| src/utils/         | 71.5%  | 65.0%    | 78.6%     |
| src/controllers/   | 88.1%  | 82.4%    | 94.1%     |

### High-Risk Uncovered Functions (Top 10)
| # | Function          | File                 | Complexity | Coverage | Risk  |
|---|-------------------|----------------------|-----------|----------|-------|
| 1 | revokeToken       | src/services/auth.ts | 8         | 25.0%    | 6.00  |
| 2 | parseQuery        | src/utils/query.ts   | 14        | 50.0%    | 7.00  |
| 3 | handleWebhook     | src/controllers/wh.ts| 11        | 45.5%    | 5.99  |

### Recommended Actions
1. Write tests for revokeToken: cover error paths (expired token, revoked token, DB failure)
2. Write tests for parseQuery: cover malformed input, injection attempts, empty query
3. Write tests for handleWebhook: cover signature validation, payload parsing, retry logic
```

## Edge Cases

- **Generated code**: Exclude auto-generated files (GraphQL types, Prisma client, protobuf stubs) from coverage metrics. They inflate the total line count and suppress the real coverage percentage.
- **Configuration-only files**: Files that only export configuration objects have low complexity and low risk regardless of coverage. Deprioritize them.
- **Test files in coverage**: Ensure the coverage tool excludes test files themselves. Check the `include`/`exclude` configuration.
- **Monorepo coverage**: In monorepos, generate per-package reports. Aggregate coverage across packages can mask low coverage in critical packages.
- **Coverage without assertions**: A line is "covered" if it is executed, even if no assertion validates its behavior. High coverage with weak assertions provides false confidence. Recommend the mutation-test-runner skill for assertion quality analysis.
- **Merge coverage from multiple runs**: If the test suite is split across multiple CI jobs (unit, integration, E2E), merge the coverage files before analysis. Tools: `nyc merge`, `coverage combine`, `lcov --add-tracefile`.

## Related Skills

- **coverage-threshold-check** (eskill-coding): Run coverage-threshold-check before this skill to define the thresholds that the coverage report will evaluate against.
- **mutation-test-runner** (eskill-testing): Follow up with mutation-test-runner after this skill to validate that covered code is effectively tested.
