---
name: e-mutate
description: "Configures and analyzes mutation testing to assess test suite effectiveness by introducing code mutations and checking detection rates. Use when evaluating test quality, finding weak assertions, or improving coverage. Also applies when: 'run mutation tests', 'are my tests effective', 'test quality check', 'mutation score'."
---

# Mutation Test Runner

This skill configures mutation testing tools, runs mutation analysis, and interprets results to identify where the test suite fails to detect code changes. Surviving mutants reveal weak assertions, missing test cases, and false-confidence coverage.

## Prerequisites

- A project with an existing test suite that passes.
- Source code in a supported language (JavaScript/TypeScript, Python, Rust, Java, C#).
- Tests that can be run from the command line.

## Workflow

### Step 1: Detect Language and Test Framework

Identify the project's language and test runner by inspecting manifest files using `filesystem` tools (fs_list, fs_read):

| Manifest File       | Language     | Common Test Runners               |
|---------------------|--------------|------------------------------------|
| package.json        | JS/TS        | Jest, Vitest, Mocha                |
| pyproject.toml      | Python       | pytest, unittest                   |
| Cargo.toml          | Rust         | cargo test                         |
| build.gradle        | Java/Kotlin  | JUnit, TestNG                      |
| pom.xml             | Java         | JUnit, TestNG                      |
| *.csproj            | C#           | NUnit, xUnit, MSTest               |

Use `data_file` tools (data_file_read) to parse the manifest and extract the test command. Confirm the test suite passes before proceeding by running it with `test_run` from the eMCP test server.

If the test suite has failures, report them and stop. Mutation testing against a failing suite produces meaningless results.

### Step 2: Select the Mutation Testing Tool

Choose the appropriate mutation tool based on the language:

| Language       | Tool            | Install Command                           | Config File            |
|----------------|-----------------|-------------------------------------------|------------------------|
| JavaScript/TS  | Stryker         | `npm install --save-dev @stryker-mutator/core` | `stryker.config.json`  |
| Python         | mutmut          | `pip install mutmut`                      | `setup.cfg` or CLI     |
| Rust           | cargo-mutants   | `cargo install cargo-mutants`             | CLI flags              |
| Java (Maven)   | PIT             | Add plugin to `pom.xml`                   | `pom.xml` plugin block |
| Java (Gradle)  | PIT             | Add plugin to `build.gradle`              | `build.gradle` block   |
| C#             | Stryker.NET     | `dotnet tool install dotnet-stryker`      | `stryker-config.json`  |

Check if the tool is already installed by looking for its config file or checking the dependency list. If not installed, present the install command and wait for user confirmation before running it via `shell` tools (shell_exec).

### Step 3: Configure Mutation Scope

Mutation testing is computationally expensive. Scope the run to relevant code to avoid multi-hour executions.

Use `ast_search` from the eMCP AST server to identify source files and their test coverage relevance. Configure the tool to target specific directories or files:

**Stryker (JS/TS)** -- generate or update `stryker.config.json`:
```json
{
  "mutate": ["src/**/*.ts", "!src/**/*.d.ts", "!src/**/*.test.ts"],
  "testRunner": "vitest",
  "reporters": ["clear-text", "json"],
  "timeoutMS": 60000,
  "concurrency": 4
}
```

**mutmut (Python)** -- configure via CLI flags or `setup.cfg`:
```ini
[mutmut]
paths_to_mutate=src/
tests_dir=tests/
runner=python -m pytest -x
```

**cargo-mutants (Rust)** -- use CLI flags:
```
cargo mutants --package my_crate --file src/lib.rs
```

Write the configuration file using `filesystem` tools. Key scoping decisions:

| Scope Strategy          | When to Use                              | Configuration                     |
|-------------------------|------------------------------------------|-----------------------------------|
| Single file             | Investigating one module's test quality  | `mutate: ["src/auth.ts"]`         |
| Single directory        | Auditing a feature area                  | `mutate: ["src/services/**"]`     |
| Changed files only      | PR-scoped mutation testing               | Derive from `git diff --name-only`|
| Full source             | Baseline quality assessment              | `mutate: ["src/**"]`              |

For initial runs, prefer single-directory scope to keep execution time under 10 minutes.

### Step 4: Run the Mutation Tests

Execute the mutation tool using `shell` tools:

| Tool          | Command                                        | Expected Duration        |
|---------------|------------------------------------------------|--------------------------|
| Stryker       | `npx stryker run`                              | Minutes to hours         |
| mutmut        | `mutmut run`                                   | Minutes to hours         |
| cargo-mutants | `cargo mutants`                                | Minutes to hours         |
| PIT           | `mvn org.pitest:pitest-maven:mutationCoverage` | Minutes to hours         |
| Stryker.NET   | `dotnet stryker`                               | Minutes to hours         |

Monitor progress. Mutation tools log each mutant as it is tested. Use `log` tools (log_tail) to follow the output if running in the background.

If the run is taking too long, consider:
- Reducing the mutation scope (fewer files).
- Increasing the timeout to kill slow mutants faster.
- Using incremental mode if the tool supports it (Stryker: `--incremental`).

### Step 5: Parse Mutation Results

Read the results report using `filesystem` tools. Each tool produces output in a different format:

**Stryker** produces `reports/mutation/mutation.json`:
```json
{
  "files": {
    "src/auth.ts": {
      "mutants": [
        { "id": "1", "status": "Killed", "mutatorName": "BooleanLiteral" },
        { "id": "2", "status": "Survived", "mutatorName": "ConditionalExpression" }
      ]
    }
  }
}
```

**mutmut** stores results in a cache; extract with:
```
mutmut results
mutmut junitxml > mutmut-results.xml
```

Parse the results using `data_file` tools and classify each mutant:

| Status      | Meaning                                        | Action Required          |
|-------------|------------------------------------------------|--------------------------|
| Killed      | Test suite detected the mutation               | None; tests are effective|
| Survived    | Mutation was not detected by any test          | Write or strengthen tests|
| Timeout     | Mutated code caused an infinite loop or hang   | Generally acceptable     |
| No Coverage | No test executes the mutated line              | Add test coverage first  |
| Runtime Error | Mutation caused a crash, not a test failure  | Review; may indicate fragile code |

Calculate the mutation score: `killed / (killed + survived) * 100`.

### Step 6: Analyze Surviving Mutants

Surviving mutants are the primary finding. For each survivor, determine why it was not detected.

Use `ast_search` to read the source code at the mutation location. Use `filesystem` tools to read the corresponding test file.

Common reasons mutants survive:

| Reason                        | Example                                            | Fix                                |
|-------------------------------|----------------------------------------------------|------------------------------------|
| Missing assertion             | Test calls function but does not assert the result | Add assertion on return value      |
| Weak assertion                | `expect(result).toBeTruthy()` instead of exact val | Use `toBe()` or `toEqual()`       |
| Untested branch               | `if (x > 0)` mutated to `if (x >= 0)`, no test covers boundary | Add boundary test case |
| Dead code                     | Mutated code is unreachable                        | Remove the dead code               |
| Equivalent mutant             | Mutation produces identical behavior               | No action; mark as equivalent      |

Group survivors by file and function. Use `ast_search` to count surviving mutants per function to identify hotspots.

### Step 7: Generate the Mutation Report

Compile a structured report:

```
## Mutation Testing Report

### Summary
- Tool: Stryker 7.0
- Scope: src/services/
- Total mutants: 156
- Killed: 128 (82.1%)
- Survived: 22 (14.1%)
- Timeout: 4 (2.6%)
- No coverage: 2 (1.3%)
- Mutation score: 85.3%

### Score Interpretation
| Score Range | Quality      |
|-------------|--------------|
| 90-100%     | Strong       |
| 75-89%      | Adequate     |
| 60-74%      | Weak         |
| Below 60%   | Insufficient |

### Survivor Hotspots
| File                  | Function          | Survived | Total | Score  |
|-----------------------|-------------------|----------|-------|--------|
| src/services/auth.ts  | validateToken     | 8        | 12    | 33.3%  |
| src/services/cart.ts  | calculateDiscount | 5        | 15    | 66.7%  |
| src/utils/format.ts   | formatCurrency    | 4        | 8     | 50.0%  |

### Top Priority Fixes
1. auth.ts:validateToken -- 8 survivors; conditional mutations not caught
   Mutations: ConditionalExpression (5), EqualityOperator (3)
   Suggested tests: boundary conditions for token expiry, empty token, malformed token

2. cart.ts:calculateDiscount -- 5 survivors; arithmetic mutations not caught
   Mutations: ArithmeticOperator (3), ConditionalExpression (2)
   Suggested tests: discount at 0%, 100%, negative price, multiple discount rules
```

### Step 8: Recommend Test Improvements

For each survivor hotspot, provide specific test case suggestions:

1. Use `ast_search` to read the function body and identify the mutated line.
2. Determine what input would distinguish the original code from the mutant.
3. Write a test case description (not full implementation) that would kill the mutant.

Structure recommendations as:

```
### Function: validateToken (src/services/auth.ts)

Surviving mutation at line 45: `if (token.exp > now)` mutated to `if (token.exp >= now)`

Test to kill: Call validateToken with a token whose `exp` equals the current timestamp.
Assert that the function returns false (token expired), not true.
This tests the exact boundary condition.
```

Use `lsp_references` from the eMCP LSP server to find how the function is called in existing tests and identify gaps.

## Edge Cases

- **Equivalent mutants**: Some mutations produce code that behaves identically to the original. These cannot be killed and should not count against the score. If the mutation score is low but many survivors appear to be equivalent, note this.
- **Slow test suites**: If the base test suite takes over 30 seconds, mutation testing will be very slow. Recommend running mutations only on changed files (PR scope) rather than the full codebase.
- **Test infrastructure mutations**: Exclude test files, configuration files, and type definitions from mutation scope. These produce false survivors.
- **Flaky tests during mutation**: If tests are flaky, they may randomly kill or miss mutants. Recommend fixing flaky tests first (use e-flaky skill).
- **Build failures from mutations**: Some mutations cause compilation errors rather than test failures. These are neither killed nor survived and should be excluded from scoring.
- **Monorepo scope**: In monorepos, scope mutations to the package being evaluated. Cross-package mutations produce misleading results.

## Related Skills

- **e-threshold** (eskill-coding): Run e-threshold before this skill to identify areas with low coverage where mutation testing is most valuable.
- **e-testgen** (eskill-coding): Follow up with e-testgen after this skill to generate tests for code areas where mutations survived.
