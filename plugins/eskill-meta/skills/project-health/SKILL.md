---
name: project-health
description: "Generates a scored project health dashboard covering tests, code quality, dependencies, docs, and repo hygiene. Use for periodic checkups, sprint reviews, or before a major release. Also applies when: how healthy is this project, project status, code quality dashboard, run a health check."
---

# Project Health Dashboard

Produce a comprehensive health assessment of the current project. The dashboard evaluates five categories -- testing, code quality, dependencies, documentation, and repository hygiene -- and produces both individual scores and an overall health rating.

## Overview

The health dashboard serves as a periodic checkup for the project. Run it:

- Before major releases to identify outstanding issues
- During sprint reviews to track quality trends
- When onboarding to a new codebase to understand its state
- After major refactors to verify nothing was degraded

Each category is scored on a 0-100 scale. The overall score is a weighted average with the following default weights:

| Category            | Weight |
|--------------------|--------|
| Testing            | 30%    |
| Code Quality       | 25%    |
| Dependencies       | 15%    |
| Documentation      | 15%    |
| Repository Hygiene | 15%    |

## Step 1: Run Test Suite

Execute the project's test suite using `test_run`. Capture the following metrics:

- **Total tests**: number of test cases
- **Passed**: tests that passed
- **Failed**: tests that failed (list names and failure reasons)
- **Skipped**: tests that were skipped
- **Duration**: total execution time
- **Exit code**: whether the test runner exited cleanly

If no test runner is configured, or if the test command fails to execute, record a score of 0 for testing and note the reason.

If the test suite passes partially, the testing score is calculated as:

```
testing_score = (passed / total) * 80 + (has_tests ? 10 : 0) + (no_failures ? 10 : 0)
```

The formula rewards having tests at all (+10) and having zero failures (+10), with the bulk of the score based on pass rate.

## Step 2: Estimate Test Coverage

Since full coverage instrumentation may not be available, estimate coverage by comparing test files to source files:

1. Use `list_directory` recursively or filesystem tools to list all source files (*.ts, *.py, *.rs, *.go, etc.)
2. List all test files (files matching *test*, *spec*, or in test/tests directories)
3. For each source file, check if a corresponding test file exists (e.g., `src/auth.ts` -> `test/auth.test.ts`)
4. Calculate the ratio: `coverage_estimate = test_files_with_match / total_source_files`

This is a rough structural coverage estimate. Note its limitations when reporting.

Add the coverage estimate as a bonus to the testing score (up to 10 additional points for >80% structural coverage).

## Step 3: Check Linting and Formatting

Determine if linting and formatting tools are configured by checking for configuration files:

- ESLint: `.eslintrc*`, `eslint.config.*`
- Prettier: `.prettierrc*`, `prettier.config.*`
- Flake8: `.flake8`, `pyproject.toml` [tool.flake8]
- Black: `pyproject.toml` [tool.black]
- Clippy: `clippy.toml` or Cargo.toml [lints]
- Rustfmt: `rustfmt.toml`
- GolangCI-Lint: `.golangci.yml`

If a linter is configured, attempt to run it using `shell` and capture the output:
- Count the number of warnings and errors
- Categorize by severity

If a formatter is configured, run a check-only pass (e.g., `prettier --check`, `black --check`, `rustfmt --check`) to count files that would be reformatted.

Code quality scoring:

```
quality_score = 100
quality_score -= (errors * 5)        # -5 per error, minimum 0
quality_score -= (warnings * 1)      # -1 per warning
quality_score -= (unformatted * 2)   # -2 per unformatted file
quality_score = max(0, quality_score)
# Bonus: +10 if linter is configured, +5 if formatter is configured
quality_score = min(100, quality_score + config_bonus)
```

## Step 4: Analyze LSP Diagnostics

Use `lsp_diagnostics` to collect warnings and errors across the codebase. This provides language-server-level insights that go beyond simple linting:

- Type errors
- Unused imports or variables
- Unreachable code
- Deprecation warnings
- Missing type annotations (in typed languages)

Categorize diagnostics by severity:
- **Error**: critical issues that would prevent compilation or cause runtime failures
- **Warning**: potential issues that should be addressed
- **Information**: suggestions and hints

Count each category and factor into the code quality score. Errors have 5x the weight of warnings, and warnings have 2x the weight of informational diagnostics.

## Step 5: Check Dependency Freshness

Read the project's dependency manifest and lock file:

- Node.js: `package.json` and `package-lock.json` or `yarn.lock`
- Python: `pyproject.toml` or `requirements.txt` and any lock files
- Rust: `Cargo.toml` and `Cargo.lock`
- Go: `go.mod` and `go.sum`

Evaluate dependencies:

1. **Count**: total number of direct dependencies and dev dependencies
2. **Lock file present**: whether a lock file exists (important for reproducibility)
3. **Audit**: if an audit tool is available (`npm audit`, `pip-audit`, `cargo audit`, `govulncheck`), run it and count vulnerabilities by severity
4. **Staleness**: check if `npm outdated`, `pip list --outdated`, or equivalent commands report outdated packages. Count how many are outdated.

Dependency scoring:

```
dep_score = 100
dep_score -= (critical_vulns * 20)   # -20 per critical vulnerability
dep_score -= (high_vulns * 10)       # -10 per high vulnerability
dep_score -= (medium_vulns * 5)      # -5 per medium vulnerability
dep_score -= (outdated_pct * 30)     # -30 scaled by percentage of outdated deps
dep_score += (has_lock_file ? 10 : 0)
dep_score = clamp(0, 100, dep_score)
```

If no audit tool is available, score based on lock file presence and dependency count alone (fewer dependencies is mildly positive).

## Step 6: Evaluate Documentation

Check for the presence and quality of documentation files:

### README.md
- Does it exist? (+20 points)
- Is it substantive (more than 50 lines)? (+10 points)
- Use `markdown_headings` to check for key sections: Installation, Usage, License (+5 each, up to +15)

### CHANGELOG.md
- Does it exist? (+10 points)
- Does it follow Keep a Changelog format? (+5 points)
- Has it been updated recently (within the last 3 months based on latest entry date)? (+5 points)

### CONTRIBUTING.md
- Does it exist? (+10 points)

### Code Documentation
- Sample 5-10 key source files (largest or most imported)
- Check for module-level docstrings or documentation comments
- Calculate the ratio of documented modules to total modules sampled
- Score: `code_docs_ratio * 25`

Documentation scoring:

```
doc_score = readme_score + changelog_score + contributing_score + code_docs_score
doc_score = clamp(0, 100, doc_score)
```

## Step 7: Assess Repository Hygiene

Evaluate the health of the git repository and project configuration:

### Git Ignore
- Does `.gitignore` exist? (+10 points)
- Check for common anti-patterns: are `node_modules/`, `__pycache__/`, `target/`, or build directories being tracked? (-10 per anti-pattern found)
- Are environment files (`.env`) properly ignored? (+5 points)

### Large Files
- Use `git_log` or filesystem tools to identify files larger than 1MB in the repository
- Binary files in the repo that should use Git LFS: (-5 per file, up to -20)
- Large generated files that should be in .gitignore: (-5 per file)

### Commit Quality
- Use `git_log` to sample the last 20 commits
- Check for conventional commit format or at least descriptive messages
- Flag empty commit messages, single-word messages, or "WIP" commits
- Score: `(good_commits / total_sampled) * 30`

### Stale Branches
- Use `git_branches` to list all local branches
- Identify branches that have not been updated in over 30 days
- Score: deduct 2 points per stale branch, up to -20

### CI Configuration
- Check for `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, or similar CI configuration (+15 points)
- Check if CI includes test, lint, and build steps (+5 points)

Repository hygiene scoring:

```
hygiene_score = gitignore_score + large_files_penalty + commit_quality + stale_branch_penalty + ci_score
hygiene_score = clamp(0, 100, hygiene_score)
```

## Step 8: Calculate Health Scores

Compute the final scores:

```
overall = (testing * 0.30) + (quality * 0.25) + (dependencies * 0.15) + (documentation * 0.15) + (hygiene * 0.15)
```

Assign a grade based on the overall score:

| Score Range | Grade | Label        |
|-------------|-------|--------------|
| 90-100      | A     | Excellent    |
| 80-89       | B     | Good         |
| 70-79       | C     | Acceptable   |
| 60-69       | D     | Needs Work   |
| 0-59        | F     | Critical     |

## Step 9: Generate the Dashboard Report

Format the report as follows:

```markdown
# Project Health Dashboard

**Project**: <project name>
**Date**: <YYYY-MM-DD>
**Overall Score**: <score>/100 (<grade>)

## Category Breakdown

| Category            | Score | Grade | Key Findings |
|--------------------|-------|-------|--------------|
| Testing            | <N>   | <G>   | <brief note> |
| Code Quality       | <N>   | <G>   | <brief note> |
| Dependencies       | <N>   | <G>   | <brief note> |
| Documentation      | <N>   | <G>   | <brief note> |
| Repository Hygiene | <N>   | <G>   | <brief note> |

## Top Issues

1. <Most impactful issue to address>
2. <Second most impactful issue>
3. <Third most impactful issue>
...

## Details

### Testing
- Tests: <passed>/<total> passing
- Estimated structural coverage: <N>%
- Failing tests: <list or "none">

### Code Quality
- Linter errors: <N>, warnings: <M>
- Unformatted files: <N>
- LSP diagnostics: <N> errors, <M> warnings

### Dependencies
- Direct dependencies: <N>
- Vulnerabilities: <N> critical, <M> high, <K> medium
- Outdated packages: <N>/<total>

### Documentation
- README: <present/missing> (<quality note>)
- CHANGELOG: <present/missing> (<last updated>)
- CONTRIBUTING: <present/missing>
- Code documentation: <estimated coverage>

### Repository Hygiene
- .gitignore: <adequate/missing/incomplete>
- Large tracked files: <N>
- Commit quality: <assessment>
- Stale branches: <N>
- CI configured: <yes/no>

## Trend

<If previous reports exist, show comparison. Otherwise, note this is the baseline.>
```

Present the report directly in the conversation.

If the user requests it, save the report to `.project-health/<YYYY-MM-DD>.md` using `create_directory` and `write_text`.

## Step 10: Generate Visual Representation

If the user requests a visual dashboard or if the diagram tools are available, generate a Mermaid chart using `diagram_render`:

```mermaid
pie title Project Health
    "Testing (30%)" : <testing_score * 0.3>
    "Code Quality (25%)" : <quality_score * 0.25>
    "Dependencies (15%)" : <dep_score * 0.15>
    "Documentation (15%)" : <doc_score * 0.15>
    "Hygiene (15%)" : <hygiene_score * 0.15>
```

Alternatively, generate a radar chart or bar chart if the diagram tool supports it.

Also consider generating a trend chart if historical data is available from previous health reports stored in `.project-health/`.

## Customization

The user may customize the health check:

- **Skip categories**: If the user says "skip dependency check," omit that category and redistribute weights
- **Custom weights**: The user may assign different weights to categories
- **Strict mode**: In strict mode, any failing test or critical vulnerability results in an automatic F grade regardless of other scores
- **Focus mode**: Check only one or two categories in depth rather than all five

## Limitations

- Test coverage is estimated structurally, not by actual code coverage instrumentation
- Dependency freshness depends on network access for audit tools
- LSP diagnostics require a running language server
- The scoring formulas are heuristics, not industry-standard metrics
- Historical trends require previous reports to be saved

## Related Skills

- **deployment-checklist** (eskill-devops): Follow up with deployment-checklist after this skill to address any health issues before the next deployment.
- **shipping-readiness** (eskill-meta): Follow up with shipping-readiness after this skill to evaluate whether health metrics meet release criteria.
