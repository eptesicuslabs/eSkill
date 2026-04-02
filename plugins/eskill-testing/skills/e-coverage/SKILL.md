---
name: e-coverage
description: "Analyzes test coverage end to end, including gap reports, threshold compliance, and risk-weighted priorities. Use when improving coverage, checking whether targets are met, or deciding what to test next. Also applies when: 'coverage report', 'which code is untested', 'are we above 80% coverage', 'coverage gaps', 'risk analysis of untested code'."
---

# Test Coverage Analysis

This skill is the main coverage-analysis workflow for eSkill. It owns coverage collection, parsing, threshold comparison, risk scoring, and recommendation output.

Use this skill to answer two questions:

1. What is uncovered or under-covered?
2. What should the team test next, and why?

`e-threshold` is adjacent but distinct. Use `e-threshold` when the main task is to define or enforce the policy gate in CI. Use `e-coverage` when the main task is to measure, analyze, and prioritize coverage work.

## Prerequisites

- A project with an existing test suite.
- A coverage tool installed or installable for the target language.
- A way to run tests from the command line.
- If the repo already has thresholds or coverage policy, access to the config files and CI scripts.

## Workflow

### Step 1: Detect Coverage Tooling and Policy Inputs

Read project manifests and test configuration with `fs_list`, `fs_read`, and `data_file_read`.

Look for both coverage tooling and current policy definitions:

| Language | Typical Coverage Tool | Common Policy Location |
|----------|------------------------|------------------------|
| JS/TS | Vitest, Jest, nyc, c8 | `vitest.config.*`, `jest.config.*`, `.nycrc`, `.c8rc` |
| Python | coverage.py, pytest-cov | `.coveragerc`, `pyproject.toml`, `setup.cfg` |
| Rust | cargo-tarpaulin, cargo-llvm-cov | `tarpaulin.toml`, CI flags |
| Go | `go test -cover` | shell scripts or CI workflow |
| Java | JaCoCo | Gradle or Maven config |
| C# | coverlet | `.csproj`, test settings, CI workflow |

Also use `egrep_search_files` to locate test files, source files, and any prior coverage outputs.

Capture these decisions before moving on:

1. Which tool will produce the report?
2. Which output format is available: JSON, LCOV, XML, or coverprofile?
3. Are thresholds already defined?
4. Is there an existing no-regression or ratchet policy?

If the repo has no explicit policy, continue anyway. `e-coverage` should still produce analysis and recommend a baseline.

### Step 2: Collect Coverage Data

Run coverage with `test_run` when the test runner supports the required flags. Otherwise use `shell_exec`.

Prefer machine-readable output:

| Ecosystem | Example Command | Output |
|-----------|------------------|--------|
| Vitest | `npx vitest run --coverage` | `coverage/`, LCOV or JSON |
| Jest | `npx jest --coverage` | `coverage/` |
| nyc | `npx nyc npm test` | `coverage/coverage-summary.json` |
| pytest-cov | `pytest --cov=src --cov-report=json` | `coverage.json` |
| coverage.py | `coverage run -m pytest && coverage json` | `coverage.json` |
| cargo-tarpaulin | `cargo tarpaulin --out json` | JSON |
| Go | `go test -coverprofile=coverage.out ./...` | `coverage.out` |
| JaCoCo | `./gradlew jacocoTestReport` | XML report |

If coverage collection fails, stop and classify the failure:

1. test failures prevented a reliable run
2. tooling is missing or misconfigured
3. the project requires report merging across jobs or packages

Do not present partial coverage as authoritative unless the user explicitly asked for a partial scope.

### Step 3: Parse Global and Per-File Coverage

Read the report artifacts with `fs_read` and parse them with `data_file_read` or direct text parsing.

Extract at least:

- global line, branch, function, and statement coverage
- per-file coverage percentages
- uncovered lines or ranges where the format supports them
- ignored or excluded line counts when available

Normalize the data into a single table regardless of input format:

| File | Lines % | Branches % | Functions % | Uncovered Lines | Ignored Lines |
|------|---------|------------|-------------|-----------------|
| src/services/auth.ts | 58.1% | 41.7% | 66.7% | 134 | 0 |
| src/utils/parser.ts | 62.5% | 55.0% | 75.0% | 105 | 3 |

If multiple reports must be merged, prefer the tool's native merge path before analysis:

- `nyc merge`
- `coverage combine`
- `lcov --add-tracefile`

### Step 4: Map Coverage Gaps to Symbols and Behavior

Use `lsp_symbols` and `ast_search` to translate file-level gaps into function-level and branch-level insight.

For each important uncovered region, determine:

1. owning symbol or function
2. whether the gap is business logic, edge handling, validation, or wiring
3. whether the code path is high risk, medium risk, or low risk

Useful high-risk categories include:

- authentication and authorization
- payment or financial logic
- database writes and migration-sensitive code
- validation and sanitization
- retry, timeout, or error handling paths

Low-value categories that often should be deprioritized include:

- generated code
- trivial configuration wrappers
- logging-only branches
- development-only helpers

### Step 5: Estimate Complexity and Score Risk

Approximate cyclomatic complexity with `ast_search` by counting decision points.

Use a simple scoring model:

`risk = complexity * (1 - line_coverage_ratio)`

This keeps the workflow explainable and easy to compare across languages.

| Function | Complexity | Coverage | Risk Score | Priority |
|----------|------------|----------|------------|----------|
| revokeToken | 8 | 25.0% | 6.00 | Critical |
| parseQuery | 14 | 50.0% | 7.00 | Critical |
| calculateTotal | 15 | 93.3% | 1.00 | Low |

Priority guidance:

| Risk Score | Priority | Action |
|------------|----------|--------|
| Above 5.0 | Critical | Write tests now |
| 2.1 to 5.0 | High | Schedule in next sprint |
| 1.0 to 2.0 | Medium | Cover when modifying code |
| 0.1 to 0.9 | Low | Nice to have |
| 0.0 | None | Already covered |

### Step 6: Compare Against Thresholds and Baselines

Coverage analysis should include policy comparison, even when policy definition is not the main task.

Check for:

- global thresholds such as `coverageThreshold` or `--cov-fail-under`
- per-file or per-directory thresholds
- changed-lines or changed-files rules in CI
- no-regression baselines compared to the default branch or a saved artifact

If no thresholds exist, report that clearly and suggest a baseline rather than pretending policy is already defined.

Reasonable default baselines when nothing is configured:

| Metric | Minimum | Recommended | Stretch |
|--------|---------|-------------|---------|
| Line | 60% | 80% | 90% |
| Branch | 50% | 70% | 85% |
| Function | 70% | 85% | 95% |
| Statement | 60% | 80% | 90% |

Report both compliance and deficit:

| Scope | Metric | Actual | Target | Status | Deficit |
|-------|--------|--------|--------|--------|---------|
| Overall | Line | 74.2% | 80% | Fail | 290 lines |
| src/services | Line | 55.3% | 80% | Fail | 170 lines |
| src/utils | Line | 81.4% | 80% | Pass | 0 |

If policy design or CI enforcement becomes the main problem, hand off to `e-threshold` after completing the analysis.

### Step 7: Produce a Prioritized Testing Plan

Turn the data into a testing order that a team can act on.

The recommendation list should balance:

1. risk to the business
2. size of the coverage deficit
3. likelihood of quick wins
4. whether the file is actively changing

Example output:

```markdown
## Coverage Analysis Report

### Overall Summary
| Metric | Covered | Total | Percentage |
|--------|---------|-------|------------|
| Lines | 3710 | 5000 | 74.2% |
| Branches | 612 | 852 | 71.8% |
| Functions | 182 | 221 | 82.1% |

### Highest-Impact Gaps
1. src/services/payment.ts
	- 42.2% covered
	- error handling and refund paths are uncovered
	- high business risk
2. src/services/auth.ts
	- 58.1% covered
	- token refresh and OAuth callback branches are uncovered
	- auth-critical

### Recommended Next Tests
1. Cover payment gateway failure handling and refund edge cases.
2. Cover token refresh failures and OAuth callback validation.
3. Add parser tests for malformed nested input.
```

Where possible, include exact uncovered symbols and suggested scenarios, not just percentages.

### Step 8: Recommend Policy and Follow-Up Work

Close the skill with concrete next steps:

1. which tests to add now
2. which directories need a dedicated coverage push
3. whether the project needs threshold policy work
4. whether the project should run `e-mutate` to check assertion quality

If the repo lacks enforcement, recommend the smallest credible next step, for example:

- add a global line threshold only
- add no-regression gating first for legacy code
- add per-package thresholds in a monorepo before per-file thresholds

Do not force strict gating recommendations onto legacy repositories without acknowledging adoption cost.

## Notes

- High coverage is not the same thing as strong tests. Executed lines without meaningful assertions produce false confidence.
- Branch coverage is often more informative than line coverage for conditional business logic.
- The most useful report is usually a ranked gap list, not a raw dump of every file.
- If the user wants the merge gate or CI ratchet changed, follow up with `e-threshold`.

## Edge Cases

- **Generated code in scope**: Exclude generated clients, schema types, protobuf output, and other artifacts that distort percentages.
- **Monorepo aggregation masking weak packages**: Report per-package results before presenting an overall aggregate.
- **Coverage merged from multiple jobs**: Make the merge step explicit before any analysis.
- **Ignored lines hiding real debt**: Count ignore directives and mention suspiciously high ignore density.
- **Line coverage hiding branch debt**: Call out files with acceptable line coverage but weak branch coverage.
- **Partial test runs**: Make it explicit when the report only covers a subset of tests or packages.
- **Legacy code with low coverage**: Recommend incremental policy adoption instead of unrealistic immediate thresholds.

## Related Skills

- **e-testgen** (eskill-coding): Use after this skill to scaffold tests for the highest-priority gaps.
- **e-threshold** (eskill-coding): Use after this skill when the next task is to encode the chosen coverage policy in CI.
- **e-mutate** (eskill-testing): Use after this skill to verify that newly covered code is meaningfully asserted.
