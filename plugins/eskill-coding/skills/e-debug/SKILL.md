---
name: e-debug
description: "Structured debugging from a failing test or runtime error to a verified fix. Use when a test fails, an error appears at runtime, or a stack trace needs diagnosis. Also applies when: 'fix this test', 'why is this failing', 'debug this error', 'find and fix the bug', 'the build is broken'."
---

# Debugging Workflow

This skill provides a structured, iterative approach to debugging. It starts from a failing state (test failure, runtime error, stack trace, or build failure), isolates the root cause, applies a minimal fix, and verifies the fix with a test rerun. If the fix does not resolve the failure, it loops with updated context until the failure is resolved or the investigation is escalated.

## Core Principle

Start from red. End at green. Every iteration narrows the hypothesis space.

The loop:

1. Capture the failure.
2. Isolate the root cause.
3. Form a hypothesis.
4. Apply a minimal patch.
5. Rerun verification.
6. If still failing, loop with updated context.

## When To Use This Skill vs. Others

| Situation | Use This Skill | Use Instead |
|-----------|---------------|-------------|
| Test is failing, need to fix the code | Yes | -- |
| Runtime error or stack trace to diagnose | Yes | -- |
| Build error that needs code changes | Yes | -- |
| Logs show errors, need root-cause analysis without fixing | No | e-logs |
| Tests are green, want to restructure code | No | e-refactor |
| Need to generate test scaffolds for untested code | No | e-testgen |
| Reviewing changes for potential issues | No | e-review |
| Performance is slow but functionally correct | No | e-perf |

## Prerequisites

- A reproducible failure: a test command that fails, an error message, a stack trace, or a build command that errors.
- Access to the source code that is suspected to contain the defect.
- A way to verify the fix (typically the same test or command that demonstrated the failure).

## Workflow

### Step 1: Capture the Failure

Obtain the exact failure output. There are several entry points:

#### From a Test Command

Run the failing test using `test_run` or `test_run_file` from the eMCP test-runner server:

```
test_run_file with the specific test file or test name
```

If no specific test is known, run the full suite with `test_run` and isolate the first failure.

Record:
- The test name and file path.
- The assertion that failed (expected vs. actual).
- The full error message.
- The stack trace, if present.

#### From a Runtime Error

If the failure is a runtime error rather than a test failure, capture:
- The error message and type (TypeError, NullPointerException, segfault, etc.).
- The stack trace with file paths and line numbers.
- The input or conditions that triggered the error.

If the error is in logs rather than direct output, use `log_errors` from the eMCP log server to extract the relevant entries, then return here with the extracted error.

#### From a Build Error

If the failure is a build or compilation error, run the build command with `shell_exec` from the eMCP shell server and capture:
- The file and line number where the error occurs.
- The compiler or bundler error message.
- Any preceding warnings that may be related.

### Step 2: Locate the Defect

Use the failure output from Step 1 to narrow down where the defect lives.

#### Follow the Stack Trace

If a stack trace is available, identify the topmost application frame (skip framework and library frames). Read that file and the surrounding code:

```
fs_read the file at the line number from the stack trace
```

Use `lsp_definition` from the eMCP LSP server to navigate to the definition of any symbol referenced in the error (the function that threw, the variable that was null, the type that was unexpected).

#### No Stack Trace Available

If no stack trace is available (e.g., a wrong value assertion), work backward from the assertion:

1. Read the failing test to understand what it expects.
2. Identify the function or code path under test.
3. Use `lsp_definition` to navigate to that function.
4. Use `ast_search` from the eMCP AST server to understand its structure (branches, early returns, error handling paths).

#### Narrow the Search

If the defect location is still unclear after reading the obvious code:

- Use `lsp_references` from the eMCP LSP server to find all callers of the function under test. One of the callers may be passing bad input.
- Use `egrep_search` from the eMCP egrep server to search for related patterns across the codebase (error message strings, constant names, configuration keys referenced in the error).
- Use `git_log` or `git_diff` from the eMCP git server to check recent changes to the file. If the test was passing before, the defect is likely in a recent commit.

```
git_log with the file path to see recent changes
git_diff to compare the current state against the last known good state
```

### Step 3: Build a Hypothesis

Based on the code inspection in Step 2, form a specific hypothesis about the root cause. Common categories:

| Category | Indicators | Example |
|----------|-----------|---------|
| Null/undefined reference | TypeError, NullPointerException, "Cannot read property" | A function returns undefined when a caller expects an object |
| Wrong return value | Assertion mismatch (expected X, got Y) | Off-by-one error, wrong branch taken, stale cached value |
| Missing error handling | Unhandled promise rejection, uncaught exception | An async call lacks a catch block or error callback |
| Type mismatch | Type errors, serialization failures | A string is passed where a number is expected |
| State mutation | Intermittent failures, order-dependent test failures | Shared mutable state modified by one test affects another |
| API contract violation | Wrong arguments, missing fields | A function signature changed but callers were not updated |
| Import/dependency error | Module not found, circular dependency | A file was moved or renamed without updating imports |
| Configuration error | Wrong environment, missing config key | A config value is expected but not set in the test environment |

Write the hypothesis as a single sentence: "The failure occurs because [specific cause] in [specific location]."

If the evidence supports multiple hypotheses, rank them by likelihood and test the most likely one first.

### Step 4: Verify the Hypothesis

Before applying a fix, confirm the hypothesis is correct. This step prevents wasted effort on wrong guesses.

#### Trace the Code Path

Use `ast_search` to examine the control flow through the suspected code:

```
ast_search for the function body, branch conditions, or error handling blocks
```

Verify that the hypothesized cause actually matches what the code does. Check:
- Does the branch condition match the failing input?
- Is the variable actually uninitialized on the failing path?
- Does the function signature match what callers pass?

#### Check Preconditions

Use `lsp_hover` from the eMCP LSP server to inspect types and signatures at the suspected location. Verify:
- The types match expectations.
- The function accepts the arguments being passed.
- The return type matches what callers consume.

#### Inspect Test Expectations

Re-read the failing test to confirm whether the test expectation is correct. Sometimes the bug is in the test, not the code:
- Is the expected value correct for the given input?
- Is the test using the right setup/teardown?
- Is the test isolating state properly, or is it affected by test ordering?

If the test expectation itself is wrong, the fix is to the test, not the application code. Document this clearly.

### Step 5: Apply a Minimal Fix

Apply the smallest change that resolves the failure. Use `fs_edit` from the eMCP filesystem server:

```
fs_edit to modify only the lines that address the root cause
```

Guidelines for the fix:

- **Minimal scope.** Change only the code that is directly responsible for the failure. Do not refactor, rename, or clean up surrounding code.
- **One logical change.** The fix should address exactly one defect. If the investigation reveals multiple defects, fix one at a time and rerun verification between each.
- **Preserve behavior.** The fix should make the failing test pass without breaking other tests. If the fix changes the behavior of other code paths, verify those paths too.
- **No speculative hardening.** Do not add defensive null checks, try-catch blocks, or validation "just in case" if the hypothesis identifies a specific cause. Fix the cause.

If the fix requires structural changes (adding a parameter, changing a return type, updating callers), use `lsp_references` to find all affected locations before editing, to avoid partial updates.

If the defect is in a test (wrong expectation, missing setup, incorrect assertion), fix the test. Document that the application code was correct and the test was wrong.

### Step 6: Rerun Verification

Run the same test or command from Step 1 to verify the fix:

```
test_run_file with the same test file from Step 1
```

Evaluate the result:

#### All Tests Pass

The fix is verified. Proceed to Step 7.

#### Same Test Still Fails

The hypothesis was wrong or incomplete.

1. Read the new failure output. Compare it to the original failure from Step 1.
2. If the error message changed, the fix addressed part of the problem. Update the hypothesis with the new information and return to Step 3.
3. If the error message is identical, the fix did not reach the failing code path. Revert the change with `fs_edit` and return to Step 2 with the knowledge that the suspected location was wrong.

#### Different Test Now Fails

The fix introduced a regression.

1. Read the newly failing test to understand what it expects.
2. Determine whether the fix changed behavior that the other test depends on.
3. If the fix is correct and the other test's expectation is outdated, update the other test.
4. If the fix is incorrect (it changes behavior it should not), revert and return to Step 3 with a refined hypothesis.

#### Iteration Limit

If three iterations of the fix-verify loop have not resolved the failure:

1. Summarize what has been tried and what was learned.
2. List the remaining hypotheses in order of likelihood.
3. Present this summary to the user for guidance before continuing.

Do not loop indefinitely. Three iterations without convergence means the hypothesis space needs human input.

### Step 7: Confirm No Regressions

After the specific failing test passes, run the broader test suite to confirm no regressions:

```
test_run with the project's full test command
```

If the full suite takes too long, run at minimum:
- The test file containing the fixed test.
- Any test files for modules that were modified by the fix (use `lsp_references` to identify which modules were touched).

If regressions are found, return to Step 6 with the new failure. The fix must pass both the original failing test and the full suite.

### Step 8: Document the Fix

After verification succeeds, produce a concise summary:

```
## Debug Summary

**Failure**: <what was failing -- test name, error message, or build error>
**Root Cause**: <one-sentence explanation of why it was failing>
**Fix**: <what was changed and why>
**Files Modified**: <list of changed files>
**Verification**: <test results -- number of tests passing, any notable changes>
```

If the root cause reveals a broader pattern (e.g., the same mistake exists elsewhere), note it but do not fix the other instances in this pass. That is a separate task for e-refactor or e-review.

## Debugging Strategies by Error Type

### Assertion Failures (Expected vs. Actual)

1. Read both the expected and actual values carefully.
2. Trace backward from the actual value: which code path produced it?
3. Use `ast_search` on the function under test to find the branch that returns the wrong value.
4. Check the branch condition: is it inverted? Is it using the wrong comparison operator? Is it checking a stale variable?

### Null Reference Errors

1. Identify which variable is null from the stack trace.
2. Use `lsp_definition` to find where the variable is assigned.
3. Walk the assignment chain: is there a code path where the variable is never assigned?
4. Check for async timing issues: is the variable set in a callback that has not fired yet?

### Type Errors

1. Use `lsp_hover` on the variable or expression that caused the type error.
2. Compare the actual type to the expected type.
3. Trace the source of the wrong type: was it a function return, a parameter, or a data transformation?
4. Check for implicit type coercion in loosely typed languages.

### Import/Module Errors

1. Verify the import path matches the actual file location.
2. Check for circular dependencies: A imports B which imports A.
3. Use `egrep_search` to find the correct export name if the import name is wrong.
4. Check for case sensitivity issues in file paths (relevant on case-sensitive filesystems).

### Async/Timing Errors

1. Look for missing `await` keywords, unhandled promise rejections, or race conditions.
2. Check whether the test framework is configured to handle async tests (e.g., returning a promise, using `done` callback).
3. Use `ast_search` to find async functions that are called without `await`.
4. Check for shared state between tests that may cause order-dependent failures.

### Build/Compilation Errors

1. Read the compiler error message for the exact file and line.
2. Check whether the error is a syntax error (fix the syntax), a type error (fix the types), or a missing dependency (install or import it).
3. For dependency-related build errors, check `data_file_read` on the package manifest (package.json, requirements.txt, Cargo.toml) to verify the dependency is declared.
4. For TypeScript or similar typed languages, use `lsp_diagnostics` to get all diagnostic errors in the affected file.

## Edge Cases

- **Flaky tests**: If the test passes on rerun without any code change, the test is flaky, not a code bug. Use `test_run_file` to run it multiple times. If it passes inconsistently, flag it as a flaky test for e-flaky rather than debugging the application code.
- **Environment-dependent failures**: If the test passes locally but fails in CI (or vice versa), check for environment differences: different OS, different Node/Python version, missing environment variables, different timezone, or different file system case sensitivity. Use `sys_info` or `sys_env` from the eMCP system server to inspect the current environment.
- **Test pollution**: If a test fails only when run as part of the full suite but passes in isolation, the problem is shared mutable state. Run the test file in isolation with `test_run_file`, then compare with the full suite. Identify which preceding test modifies shared state.
- **Generated code**: If the defect is in generated code (protobuf stubs, ORM models, build artifacts), do not fix the generated file. Find the generator input (schema, template, configuration) and fix it there.
- **Third-party library bugs**: If the root cause is inside a library, not application code, document the library bug and apply a workaround in application code. Note the library version and the known issue for future reference.

## Related Skills

- **e-logs** (eskill-system): Use e-logs first when the failure appears in log files rather than test output, then return here with the extracted error for fix-verify cycling.
- **e-testgen** (eskill-coding): Use e-testgen to create a regression test after fixing a bug that had no test coverage, so the defect does not recur.
- **e-refactor** (eskill-coding): Use e-refactor after debugging if the fix reveals code that should be restructured. e-refactor requires green tests, so debug first, refactor second.
- **e-review** (eskill-coding): Use e-review to summarize the debugging changes for code review after the fix is verified.
- **e-flaky** (eskill-testing): Use e-flaky instead of this skill when the test passes inconsistently without code changes.
- **e-perf** (eskill-coding): Use e-perf instead of this skill when the code is functionally correct but too slow.
