---
name: e-ship
description: "Evaluates whether a project is ready to ship by checking docs, tests, security, dependencies, and ops readiness. Use before launches, major releases, or assessing release criteria. Also applies when: 'ready to ship?', 'launch checklist', 'release readiness', 'can we go live', 'pre-launch review'."
---

# Shipping Readiness

This skill evaluates whether a project meets the criteria for shipping by systematically checking documentation, test coverage, security posture, dependency health, operational readiness, and code quality. It produces a scored readiness report with a clear ship/no-ship recommendation and a punch list of blocking items.

## Prerequisites

Confirm with the user what "shipping" means in this context:

| Shipping Type | Key Concerns |
|--------------|-------------|
| Initial public launch | Everything: docs, security, ops, scalability |
| Major version release | Breaking changes, migration guides, changelog |
| Minor feature release | Tests, docs for new feature, backward compatibility |
| Hotfix/patch | Fix verification, regression tests, targeted scope |
| Internal tool release | Reduced requirements: tests and basic docs sufficient |

Adjust the checklist depth based on the shipping type. An initial launch requires all checks; a hotfix focuses on the fix and its tests.

### Step 1: Check Documentation Readiness

Use `filesystem` to scan for documentation files and `data_file_read` to assess their content.

| Document | Check | Pass Criteria |
|----------|-------|--------------|
| README.md | Exists and is current | Present, over 50 lines, updated within last 30 days |
| CHANGELOG.md | Covers the release | Has entry for the version being shipped |
| API documentation | Matches code | OpenAPI spec exists or API reference is current |
| Installation guide | Complete | Step-by-step instructions from zero to running |
| Configuration reference | All options documented | Env vars and config files have documentation |
| Migration guide | Exists for breaking changes | Required only if version has breaking changes |
| LICENSE | Exists | Present in repository root |
| CONTRIBUTING.md | Exists for open source | Required for public projects |

For each document, score:
- **Pass**: Document exists and appears current.
- **Partial**: Document exists but is outdated or incomplete.
- **Fail**: Document is missing.

Use `git` to check when documentation files were last modified relative to source code changes. Documentation that has not been updated while the codebase has changed significantly is a warning.

### Step 2: Evaluate Test Coverage

Use `test_run` to execute the test suite and capture results.

Record:

| Metric | Value | Threshold |
|--------|-------|-----------|
| Total tests | <N> | Varies by project |
| Passing | <N> | 100% required for ship |
| Failing | <N> | 0 required for ship |
| Skipped | <N> | Less than 5% of total |
| Coverage (if available) | <X%> | 70% minimum for ship |
| Execution time | <N>s | Under 10 minutes for CI |

**Test type distribution**: Use `ast_search` to classify tests by type.

| Test Type | Count | Coverage Area |
|-----------|-------|--------------|
| Unit tests | <N> | Individual functions and classes |
| Integration tests | <N> | Module interactions, database |
| End-to-end tests | <N> | Full user workflows |
| Contract tests | <N> | API contracts |
| Performance tests | <N> | Load and latency |

**Critical path coverage**: Identify the most important user workflows and verify they have end-to-end test coverage. Use `filesystem` to search test directories for tests named after key features.

**Recent test additions**: Use `git` to check whether tests were added alongside recent code changes. Code changes without corresponding test changes are a risk indicator.

Score:
- **Pass**: All tests passing, coverage above threshold, critical paths tested.
- **Partial**: Tests passing but coverage below threshold or gaps in critical paths.
- **Fail**: Failing tests, no test suite, or critical features untested.

### Step 3: Assess Security Posture

Use `ast_search` and `filesystem` to check for security concerns.

| Security Check | Method | Blocking |
|---------------|--------|----------|
| No hardcoded secrets | Search for API key, password, token patterns in source | Yes |
| Dependencies without known vulnerabilities | Run `shell` audit commands | Yes (critical/high) |
| Authentication on all protected routes | Verify middleware chains | Yes |
| Input validation on all endpoints | Check for validation middleware | Yes |
| HTTPS enforced | Check server configuration | Yes for production |
| Security headers | Check for helmet/CSP/HSTS configuration | No (warning) |
| CORS configured | Check CORS middleware settings | No (warning) |
| Rate limiting | Check for rate limit middleware | No (warning) |
| SQL injection prevention | Check for parameterized queries | Yes |
| XSS prevention | Check for output encoding | Yes |

Use `lsp_diagnostics` to check for compiler/linter security warnings.

Run dependency audit via `shell`:
- `npm audit --production` for Node.js.
- `pip-audit` for Python.
- `cargo audit` for Rust.

Score:
- **Pass**: No critical or high vulnerabilities, no hardcoded secrets, authentication and validation in place.
- **Partial**: Non-critical vulnerabilities, missing some security headers.
- **Fail**: Critical vulnerabilities, hardcoded secrets, missing authentication.

### Step 4: Verify Dependency Health

Use `data_file_read` to read dependency manifests and lock files.

| Check | Method | Concern |
|-------|--------|---------|
| Lock file exists | Check for package-lock.json, yarn.lock, etc. | Reproducible builds |
| Lock file committed | Check git status | Consistent installs across environments |
| No deprecated dependencies | Run `npm outdated`, check for deprecation notices | Maintenance risk |
| No prerelease dependencies in production | Check for alpha/beta/rc versions | Stability risk |
| License compatibility | Check dependency licenses | Legal compliance |
| Minimal unused dependencies | Compare declared vs imported | Attack surface, bundle size |

Use `git` to check when the lock file was last updated. A stale lock file means dependencies are not receiving security patches.

Score:
- **Pass**: Lock file present and current, no critical advisories, licenses compatible.
- **Partial**: Lock file present but outdated, minor advisories, some unused dependencies.
- **Fail**: No lock file, critical advisories unaddressed, license violations.

### Step 5: Check Build and CI Status

Use `data_file_read` to read CI/CD configuration and `shell` to verify build status.

| Check | Method | Blocking |
|-------|--------|----------|
| Build succeeds | Run build command or check CI | Yes |
| Linting passes | Run lint command or check CI | Yes |
| Type checking passes | Run type checker or check CI | Yes |
| CI pipeline defined | Check for CI config files | Yes for production |
| All CI checks green | Check latest CI run on main branch | Yes |
| Build reproducible | Lock files present, pinned versions | Yes |

Verify the project builds cleanly:
- Use `shell` to run the build command if available.
- Check for TypeScript compilation errors via `lsp_diagnostics`.
- Check for lint errors.

Score:
- **Pass**: Build succeeds, lint clean, types check, CI green.
- **Partial**: Build succeeds but lint warnings or CI partially configured.
- **Fail**: Build fails, type errors, CI not configured.

### Step 6: Evaluate Operational Readiness

Use `filesystem` and `data_file_read` to check for operational infrastructure.

| Operational Check | What to Look For | Blocking |
|------------------|-----------------|----------|
| Health check endpoint | `/health`, `/healthz`, `/ready` route | Yes for services |
| Logging configured | Structured logging, appropriate levels | Yes |
| Error tracking | Sentry, Bugsnag, or similar integration | No (recommended) |
| Monitoring | Prometheus metrics, Datadog, CloudWatch | No (recommended) |
| Deployment pipeline | Automated deployment to production | Yes for production |
| Rollback mechanism | Documented rollback procedure | Yes for production |
| Environment configuration | Separation of dev/staging/prod configs | Yes |
| Backup strategy | Database backup configuration | Yes for data services |

For containerized applications, additionally check:
- Dockerfile exists and builds successfully.
- Container runs as non-root user.
- Health check defined in container configuration.
- Resource limits specified.

Score:
- **Pass**: Health checks, logging, monitoring, deployment, and rollback all in place.
- **Partial**: Core operational features present but gaps in monitoring or rollback.
- **Fail**: No health check, no logging, no deployment pipeline.

### Step 7: Review Code Quality

Use `ast_search`, `lsp_diagnostics`, and `git` to assess code quality indicators.

| Quality Indicator | Method | Threshold |
|------------------|--------|-----------|
| Lint warnings | `lsp_diagnostics` or lint output | 0 errors, few warnings |
| Type safety | TypeScript strict mode, mypy, or equivalent | Strict mode enabled |
| Dead code | Unreachable code, unused exports | Minimal |
| TODO/FIXME count | Search annotations | No critical FIXMEs |
| Code complexity | Large files, deep nesting | No file over 500 lines |
| Recent refactoring stability | Git log for recent large changes | No major refactor in last week |

Use `git` to check for:
- Unmerged feature branches that were expected to be included.
- Recent force pushes or history rewrites on the main branch.
- Commits with "WIP" or "temp" in the message on the release branch.

Score:
- **Pass**: Clean lint, strict types, no critical debt, stable recent history.
- **Partial**: Minor warnings, some debt items, recent changes settling.
- **Fail**: Significant lint errors, type safety disabled, unstable code.

### Step 8: Verify Version and Release Metadata

Use `data_file_read` to check version consistency and `git` to verify release state.

| Check | Method | Blocking |
|-------|--------|----------|
| Version number updated | Read package.json, pyproject.toml, etc. | Yes |
| Version consistent across files | Compare all version references | Yes |
| Git tag matches version | Check for corresponding tag | No (created during release) |
| Changelog updated | Check CHANGELOG.md for new version entry | Yes for major releases |
| Branch is clean | No uncommitted changes | Yes |
| Branch is up to date | No unmerged changes from main | Yes |

Use `git` to verify the release branch state:
- `git_status` for uncommitted changes.
- `git_log` to compare with the main branch.
- Check that the branch is not behind the main branch (all main changes are incorporated).

Score:
- **Pass**: Version updated and consistent, changelog current, branch clean and up to date.
- **Partial**: Version updated but minor inconsistencies or changelog incomplete.
- **Fail**: Version not updated, branch has uncommitted changes, behind main.

### Step 9: Calculate Readiness Score

Aggregate scores from all categories into an overall readiness assessment.

| Category | Weight | Score | Weighted |
|----------|--------|-------|----------|
| Documentation | 15% | <0-100> | <weighted> |
| Tests | 20% | <0-100> | <weighted> |
| Security | 20% | <0-100> | <weighted> |
| Dependencies | 10% | <0-100> | <weighted> |
| Build/CI | 10% | <0-100> | <weighted> |
| Operations | 10% | <0-100> | <weighted> |
| Code Quality | 10% | <0-100> | <weighted> |
| Version/Release | 5% | <0-100> | <weighted> |
| **Overall** | **100%** | | **<total>** |

Scoring scale:
- Pass = 100 points.
- Partial = 50 points.
- Fail = 0 points.

Recommendation thresholds:
- 90-100: Ship. Minor items can be addressed post-launch.
- 70-89: Ship with conditions. Address the listed items within a defined timeframe.
- 50-69: Delay. Significant gaps need resolution before shipping.
- Below 50: Not ready. Substantial work remains.

### Step 10: Generate Readiness Report

Produce the final report with the ship/no-ship recommendation.

The report should include: project metadata (name, version, date, shipping type), recommendation (Ship / Ship with Conditions / Delay / Not Ready), overall score, category scores table (each category with score, status, key findings), blocking items table (must fix before ship with effort estimates), non-blocking items table (fix after ship with priorities), and per-category detailed findings from Steps 1-8.

Present the report directly and offer to write it to a file.

## Edge Cases

- **Library vs application**: Libraries have different shipping criteria (API documentation, semver compliance, backward compatibility) than applications (operational readiness, deployment pipeline).
- **Monorepo partial release**: If releasing one package from a monorepo, scope the readiness check to that package and its dependencies, not the entire repository.
- **Pre-release versions**: For alpha/beta releases, relax documentation and operational readiness thresholds. Security and test requirements remain.
- **Hotfix urgency**: For critical hotfixes, provide an expedited checklist focusing on: fix verification, regression test, security check, and deployment. Skip non-essential checks and note them for follow-up.
- **First-time project**: Projects being shipped for the first time have no baseline. Apply the full checklist but adjust expectations for operational maturity.
- **Regulated industries**: For healthcare, finance, or government projects, add compliance-specific checks and increase the weight of security and documentation categories.

## Related Skills

- **e-health** (eskill-meta): Run e-health before this skill to gather the health metrics that e-ship evaluates.
- **e-deploy** (eskill-devops): Follow up with e-deploy after this skill to prepare the deployment plan once readiness is confirmed.
- **e-scan** (eskill-quality): Run e-scan before this skill to include security status in the shipping readiness assessment.
