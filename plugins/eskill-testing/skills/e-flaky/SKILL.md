---
name: e-flaky
description: "Investigates flaky tests by analyzing execution timing, resource dependencies, shared state, and concurrency to identify root causes. Use when tests pass intermittently, CI is unreliable, or test ordering affects results. Also applies when: 'flaky tests', 'intermittent failures', 'test passes locally fails in CI', 'tests fail randomly'."
---

# Flaky Test Investigator

This skill systematically investigates tests that fail intermittently by reproducing the flakiness, categorizing the root cause, and recommending specific fixes. It covers timing issues, shared state, concurrency problems, environment differences, and order-dependent failures.

## Prerequisites

- One or more tests identified as flaky (failing intermittently).
- Ability to run the test suite from the command line.
- Access to CI logs if the flakiness occurs in CI but not locally.

## Workflow

### Step 1: Gather Flakiness Evidence

Collect information about the flaky test(s) before attempting reproduction.

Use `filesystem` tools (fs_read) to read CI configuration files and `log` tools (log_read) to access recent CI logs:

1. Test name(s) and file location(s).
2. Failure frequency: what percentage of runs fail?
3. Failure message: is it always the same error, or do different errors occur?
4. Environment: does it fail only in CI, only locally, or both?
5. Recent changes: use `git` tools (git_log, git_diff) to check if the test or its dependencies changed recently.

Build an evidence table:

| Property            | Value                                              |
|---------------------|----------------------------------------------------|
| Test file           | `tests/integration/checkout.test.ts`               |
| Test name           | `should complete checkout with valid payment`       |
| Failure rate        | ~20% of CI runs                                    |
| Error message       | `Timeout: exceeded 5000ms`                         |
| Fails in CI         | Yes                                                |
| Fails locally       | Rarely                                             |
| Last code change    | 3 days ago (unrelated file)                        |

### Step 2: Reproduce the Flakiness

Run the test multiple times to confirm and characterize the flakiness. Use `test_run` from the eMCP test server or `shell` tools (shell_exec):

**Repeated execution**:
```
# Run the specific test 20 times
for i in $(seq 1 20); do npx vitest run tests/checkout.test.ts 2>&1 | tail -1; done
```

**With randomized order** (to detect order dependencies):
```
npx vitest run --sequence.shuffle tests/
pytest tests/ -p random --count=10
```

**In isolation** (to detect shared state from other tests):
```
npx vitest run tests/checkout.test.ts --no-threads
pytest tests/integration/test_checkout.py -x --forked
```

**Under load** (to detect timing sensitivity):
```
# Run tests while stressing CPU
stress-ng --cpu 4 --timeout 60s &
npx vitest run tests/checkout.test.ts
```

Record the results:

| Run | Isolated | Shuffled | Under Load | Result  | Duration |
|-----|----------|----------|------------|---------|----------|
| 1   | Yes      | No       | No         | Pass    | 1.2s     |
| 2   | Yes      | No       | No         | Pass    | 1.1s     |
| 3   | No       | Yes      | No         | Fail    | 5.1s     |
| 4   | No       | No       | Yes        | Fail    | 5.0s     |
| 5   | Yes      | No       | Yes        | Pass    | 2.8s     |

The pattern in the results reveals the category. Failures only in shuffled mode suggest order dependence. Failures under load suggest timing sensitivity.

### Step 3: Categorize the Root Cause

Based on reproduction results, categorize the flakiness. Use `ast_search` from the eMCP AST server and `filesystem` tools to examine the test source code and its dependencies.

| Category              | Indicators                                           | Reproduction Pattern               |
|-----------------------|------------------------------------------------------|------------------------------------|
| Timing / Race         | Timeout errors, assertions on async results          | Fails under load or slow machines  |
| Shared state          | Different results depending on test order            | Fails in shuffled mode             |
| Resource leak         | Failures increase over long test runs                | Fails late in suite                |
| External dependency   | Network errors, service unavailable                  | Fails when service is slow/down    |
| Non-deterministic     | Random data, timestamps, UUIDs in assertions         | Fails sporadically regardless      |
| Concurrency           | Parallel test interference                           | Fails only with parallel execution |
| Environment           | Path, locale, timezone, OS differences               | Fails in CI but not locally        |
| Order dependence      | Relies on state from a preceding test                | Fails when run in isolation        |

### Step 4: Analyze Timing and Race Conditions

If the category is timing-related, examine the test for race conditions.

Use `ast_search` to search for these patterns in the test file:

1. **Hardcoded timeouts**: `setTimeout`, `sleep`, `time.sleep`, `Thread.sleep`. These are fragile under varying system load.
2. **Missing awaits**: Async operations without `await`, leading to assertions running before the operation completes.
3. **Event-based assertions**: Assertions that depend on events (DOM updates, message queue delivery) without explicit waits.
4. **Polling with tight intervals**: Code that polls a condition with short sleep intervals and a limited retry count.

Use `lsp_references` from the eMCP LSP server to trace async call chains from the test to the code under test:

```
Test calls: await checkout.process(order)
  -> checkout.process calls: paymentService.charge(amount)
    -> paymentService.charge calls: fetch(paymentAPI)
      -> If paymentAPI is slow, the entire chain may timeout
```

Check timeout configuration. Use `filesystem` tools to read the test framework config:
- Vitest: `testTimeout` in `vitest.config.ts`
- Jest: `testTimeout` in `jest.config.js`
- pytest: `@pytest.mark.timeout(seconds)` or `timeout` in `pytest.ini`

### Step 5: Analyze Shared State

If the category is shared state or order dependence, identify what state is being shared.

Use `ast_search` to find state that persists between tests:

| Shared State Type     | What to Search For                              | Risk Level |
|-----------------------|-------------------------------------------------|------------|
| Global variables      | Module-level `let`/`var`, Python module globals  | High       |
| Database records      | Missing cleanup in afterEach, no transaction wrap| High       |
| File system           | Temp files created but not cleaned up            | Medium     |
| Environment variables | `process.env` modifications without restore      | High       |
| Singletons            | Cached instances, module-level instances          | Medium     |
| In-memory caches      | Memoization without reset                        | Medium     |
| Mocks not restored    | `vi.mock()` / `jest.mock()` without `restoreAllMocks` | High  |

For each suspect, trace its lifecycle:
1. Where is it initialized?
2. Does the test modify it?
3. Is it reset in `beforeEach` / `afterEach`?
4. Can another test's modification affect this test?

Use `ast_search` to examine the `beforeEach`, `afterEach`, `setUp`, and `tearDown` blocks in the test file and any shared test utilities.

### Step 6: Analyze Environment Differences

If the test fails in CI but passes locally, compare environments:

1. Use `shell` tools to check the local environment:
   ```
   node --version
   python --version
   echo $TZ
   locale
   uname -a
   ```
2. Use `log` tools to read CI logs for the equivalent information.
3. Use `filesystem` tools to read CI configuration (`.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`).

Common CI vs local differences:

| Factor              | Local              | CI                    | Impact                         |
|---------------------|--------------------|-----------------------|--------------------------------|
| CPU/memory          | Fast workstation   | Shared runner, limited| Timeouts, slow operations      |
| Timezone            | Local TZ           | UTC                   | Date comparisons fail          |
| Locale              | System locale      | C or POSIX            | Sorting, string comparison     |
| File system         | Case-insensitive   | Case-sensitive        | Import path mismatches         |
| Network             | Low latency        | Variable              | External service calls fail    |
| Display             | Available          | Headless only         | Browser tests, screenshots     |
| Parallelism         | Single worker      | Multiple workers      | Resource contention            |
| Docker              | Docker Desktop     | Docker-in-Docker      | Different networking, slower   |

### Step 7: Determine Fix Strategy

Based on the root cause analysis, select the appropriate fix:

**Timing fixes**:
- Replace `sleep(N)` with explicit waits for conditions: `waitFor(() => expect(element).toBeVisible())`.
- Increase timeouts for CI environments with `CI` environment variable detection.
- Use retry logic for inherently async operations.
- Mock time-dependent code (use `vi.useFakeTimers()` or `freezegun`).

**Shared state fixes**:
- Add cleanup in `afterEach`: reset databases, restore mocks, delete temp files.
- Wrap database tests in transactions that roll back.
- Use `beforeEach` to set a known state rather than relying on previous test state.
- Isolate mocks with `vi.restoreAllMocks()` or `unittest.mock.patch` context managers.

**Environment fixes**:
- Set explicit timezone in tests: `process.env.TZ = 'UTC'`.
- Use relative dates instead of absolute dates in assertions.
- Normalize file paths for cross-platform compatibility.
- Pin browser versions in E2E tests.

**Concurrency fixes**:
- Give each parallel worker its own database schema or instance.
- Use file locks for shared file system resources.
- Avoid port conflicts with dynamic port allocation.

### Step 8: Verify the Fix

After implementing the fix, re-run the reproduction procedure from Step 2:

1. Run the test 20+ times to confirm it no longer fails.
2. Run with shuffled order to confirm order independence.
3. Run under load to confirm timing resilience.
4. Run the full test suite to confirm no regressions.

Use `test_run` to execute the verification runs and `shell` tools for the stress tests.

### Step 9: Report Findings

Compile the investigation results:

```
## Flaky Test Investigation Report

### Test
tests/integration/checkout.test.ts > should complete checkout with valid payment

### Root Cause
Category: Timing / Race condition
The test asserts on the checkout result immediately after calling process(), but the
payment service mock has a 100ms simulated delay. Under CI load, the assertion runs
before the mock resolves.

### Evidence
- Failed in 4 of 20 CI runs over the past week
- Reproduced locally under CPU stress in 3 of 20 runs
- Never failed when run in isolation without stress

### Fix Applied
Replaced direct assertion with waitFor():
- Before: expect(result.status).toBe('completed')
- After: await waitFor(() => expect(result.status).toBe('completed'))

### Verification
- 50 consecutive runs under CPU stress: 0 failures
- Full suite with shuffled order: 0 failures
```

## Edge Cases

- **Multiple root causes**: A single test can be flaky for more than one reason. If the first fix reduces but does not eliminate flakiness, repeat the investigation from Step 3.
- **Infrastructure flakiness**: If the flakiness is caused by CI infrastructure (disk full, OOM killer, network partition), the fix is infrastructure configuration, not test code. Check CI runner resource limits.
- **Flaky due to production bug**: Rarely, a flaky test is correctly detecting a real concurrency bug in the application code. If the test logic is sound and no test-level issue is found, investigate the application code.
- **Test pollution from other test files**: If flakiness only occurs when the full suite runs but not when the test file runs alone, another file's test is leaking state. Use bisection: run half the suite, then quarter, to identify the polluting file.
- **Non-deterministic external data**: If the test calls a live API or uses a shared database that other processes modify, the data can change between runs. Mock external dependencies or use a dedicated test database.
- **Clock skew in distributed tests**: Tests that involve multiple services with timestamp-based logic can fail if system clocks differ. Use a single time source or mock timestamps.

## Related Skills

- **e-e2e** (eskill-testing): Run e-e2e before this skill to reproduce flaky test failures in a controlled environment.
- **e-coverage** (eskill-testing): Follow up with e-coverage after this skill to reassess coverage after fixing or removing flaky tests.
