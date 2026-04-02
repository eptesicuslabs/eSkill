---
name: e-threshold
description: "Defines and enforces coverage policy in CI with thresholds, no-regression rules, and ratchets. Use when adding a coverage gate, tightening policy, or preventing backsliding. Also applies when: 'coverage gate', 'coverageThreshold', 'cov-fail-under', 'ratchet coverage', 'block coverage regressions'."
---

# Coverage Policy Gate

This skill is for policy, not analysis.

Use `e-threshold` when the main task is to decide how coverage should block merges or releases, then encode that decision into project config and CI.

Use `e-coverage` first when the repo still needs measurement, gap analysis, or testing priorities.

## Core Principle

Coverage gates should reflect repository reality.

A good policy prevents backsliding without turning the pipeline into a permanent red light for legacy code. Prefer enforceable policy over aspirational numbers that nobody can maintain.

## Prerequisites

- A project with a test suite and some form of coverage output.
- Access to test configuration and CI workflow files.
- A baseline understanding of the repository's current coverage state, ideally from `e-coverage`.

## Workflow

### Step 1: Inspect the Current Gate Surface

Read the files that currently control testing and CI with `fs_list`, `fs_read`, and `data_file_read`.

Inspect all layers that may already encode policy:

- test framework config
- coverage tool config
- CI workflow files
- package scripts or Make targets
- repository docs that describe the expected threshold

Capture these facts:

1. where coverage is produced
2. where failure conditions are defined
3. whether the repo currently blocks merges on coverage
4. whether the repo compares against a saved baseline or only a fixed threshold

If there is no reliable coverage artifact yet, stop and run `e-coverage` first.

### Step 2: Choose the Right Gate Model

Select the policy model that matches the maturity of the codebase.

Common models:

| Model | Best For | Tradeoff |
|-------|----------|----------|
| Global fixed threshold | Mature repos with stable coverage | Easy to understand, coarse |
| Per-file threshold | Repos that want local accountability | More maintenance |
| Per-package threshold | Monorepos | Good compromise, still broad |
| Changed-files threshold | Large legacy repos | Encourages improvement where people touch code |
| No-regression gate | Low-coverage legacy repos | Prevents decline without forcing a jump |
| Ratchet policy | Teams steadily improving coverage | Requires baseline management |

Decision guidance:

1. If current coverage is already healthy, use a fixed global threshold plus optional package rules.
2. If current coverage is weak, start with no-regression or ratchet mode.
3. If one package masks another, use per-package thresholds.
4. If teams repeatedly touch hot files without tests, consider changed-files enforcement.

Do not recommend strict per-file gating by default unless the repo already has the discipline to maintain it.

### Step 3: Read and Normalize Existing Threshold Config

Look for existing policy settings in tool-specific locations:

| Tool | Common Config Surface |
|------|------------------------|
| Vitest | `coverage.thresholds` |
| Jest | `coverageThreshold` |
| pytest-cov | `--cov-fail-under` or coverage config |
| coverage.py | `[report] fail_under` |
| tarpaulin | `--fail-under` or `tarpaulin.toml` |
| Go | custom shell or CI script |

Normalize what is already there into a single policy summary:

- global line, branch, function, statement targets
- per-package or per-file overrides
- exclusions
- current failure path in CI

If the repository has conflicting definitions in multiple places, resolve that first. Duplicate policy definitions are a common source of flaky gates.

### Step 4: Encode the Policy in Tooling

Update the project so the policy lives in one authoritative path wherever practical.

Examples:

**Vitest**
```typescript
export default defineConfig({
  test: {
    coverage: {
      thresholds: {
        lines: 80,
        branches: 75,
        functions: 80,
        statements: 80,
      },
    },
  },
});
```

**Jest**
```javascript
module.exports = {
  coverageThreshold: {
    global: {
      branches: 75,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

**coverage.py**
```toml
[tool.coverage.report]
fail_under = 80
show_missing = true
skip_covered = false
```

If the policy requires custom logic, encode it in a small, readable script rather than spreading shell fragments across multiple CI steps.

### Step 5: Wire the Gate into CI

The policy is not real until CI enforces it.

Add or tighten the CI step so it:

1. runs or downloads the coverage artifact
2. verifies the threshold or baseline comparison
3. exits non-zero on failure
4. prints enough detail for a developer to fix the issue quickly

If the repo uses a no-regression or ratchet policy, define the source of truth for the baseline:

- default branch artifact
- committed baseline file
- CI-generated historical record

Keep the baseline mechanism explicit. Hidden or implicit baselines become impossible to trust.

### Step 6: Validate Both Pass and Fail Paths

Do not stop after a green run. Prove that the gate actually fails when it should.

Validation checklist:

1. run the configured gate once on the current branch
2. confirm the command exits zero when policy is met
3. simulate or identify a failing case
4. confirm the pipeline reports the reason clearly

For custom scripts, validate edge cases such as missing artifacts, malformed JSON, or partial monorepo reports.

### Step 7: Handle Legacy Repositories Carefully

When the repo cannot realistically meet the target today, choose an adoption path rather than a false hard gate.

Recommended adoption strategies:

| Situation | Recommended Policy |
|-----------|--------------------|
| Coverage is low across the whole repo | no-regression gate |
| Coverage is uneven between packages | per-package thresholds |
| Active areas are under-tested | changed-files rule |
| Team wants gradual improvement | ratchet upward on a schedule |

Document the rollout in plain language:

- what the target is now
- what will tighten later
- who owns the next ratchet

### Step 8: Produce a Policy Summary

Finish with a short implementation summary that records:

1. the chosen gate model
2. the configured thresholds or baseline rule
3. where the policy is defined
4. how CI enforces it
5. what developers should run locally before pushing

Example summary:

```markdown
## Coverage Policy Summary

- Gate model: no regression on overall line coverage, plus 80% target for new packages
- Source of truth: coverage-policy.json and CI workflow `test.yml`
- Enforcement command: `npm run coverage:check`
- Local workflow: run `npm run test:coverage` before opening a PR
- Next ratchet: increase line target from 76% to 78% after the next release
```

## Notes

- Fixed thresholds are simplest, but they are not always the right first move.
- The most credible legacy-code policy is usually no-regression first, then ratcheting.
- Keep one clear source of truth for policy. Duplicated threshold values drift quickly.
- Coverage gates should be fast enough to run consistently. If full coverage is too slow for every PR, document the tradeoff and consider package-scoped or changed-files enforcement.

## Edge Cases

- **Monorepo artifact fan-in**: Package-level reports often need to be merged or checked independently.
- **Generated code skewing policy**: Exclusions must live in the coverage config, not in ad hoc CI logic.
- **Flaky tests causing false red coverage gates**: Stabilize the test suite before tightening policy.
- **Branch protection with stale baselines**: A ratchet policy is only trustworthy if the baseline is refreshed deliberately.
- **Per-file thresholds on rapidly moving codegen or framework files**: Prefer package-level rules when file churn is high.
- **Teams bypassing coverage by overusing ignore directives**: Audit ignore counts as part of policy review.

## Related Skills

- **e-coverage** (eskill-testing): Run first to measure current coverage and choose a defensible policy.
- **e-testgen** (eskill-coding): Use after a failing gate to scaffold tests for the biggest deficits.
- **e-mutate** (eskill-testing): Use after tightening thresholds to ensure higher coverage also means stronger assertions.
