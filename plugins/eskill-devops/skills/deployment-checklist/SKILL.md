---
name: deployment-checklist
description: "Runs pre-deployment verification covering tests, build, git state, deps, and config. Use before deploying to staging or production, as a final gate before a release. Also applies when: 'ready to deploy?', 'pre-deploy checks', 'can I ship this', 'deployment checklist', 'validate before release'."
---

# Deployment Checklist

This skill performs a comprehensive pre-deployment verification sequence. It runs tests, validates the build, checks git state, audits dependencies, verifies configuration, and produces a structured pass/fail checklist report. If any critical item fails, deployment is blocked with clear details on what must be fixed.

## Step 1: Run the Full Test Suite

Execute the project's test suite to verify that all tests pass.

- Use `test_run` from the eMCP test-runner tool to execute the full test suite.
- Detect the appropriate test command based on the project type:
  - Node.js: `npm test` or the `test` script from `package.json`.
  - Python: `pytest` or `python -m unittest discover`.
  - Rust: `cargo test`.
  - Go: `go test ./...`.
  - Java: `mvn test` or `./gradlew test`.
- Capture the test output, including the number of tests run, passed, failed, and skipped.
- Record the result: PASS if all tests pass (skipped tests are acceptable), FAIL if any test fails.
- If tests fail, capture the failure details including test name, file path, assertion message, and stack trace.

This is a blocking check. Any test failure means the deployment must not proceed.

## Step 2: Run the Build Process

Execute the project's build process to verify it completes without errors.

- Use the `shell` tool to run the build command:
  - Node.js: `npm run build`.
  - Python: `python -m build` or `pip install -e .`.
  - Rust: `cargo build --release`.
  - Go: `go build ./...`.
  - Java: `mvn package -DskipTests` or `./gradlew build -x test`.
- Monitor the build output for errors and warnings.
- Record the result: PASS if the build exits with code 0, FAIL otherwise.
- If the build fails, capture the error output for the report.
- Note any build warnings, even if the build succeeds, as they may indicate issues.

This is a blocking check. A failing build must not be deployed.

## Step 3: Check Git State

Verify that the working directory is clean and the branch is correct.

- Use `git_status` to check for uncommitted changes.
- The working directory must be clean: no modified files, no untracked files that should be tracked, no staged but uncommitted changes.
- Record the result: PASS if the working directory is clean, FAIL if there are uncommitted changes.
- If there are uncommitted changes, list each changed file in the report.

Additionally, verify the branch:
- Use `git_log` to check the current branch name and the latest commit.
- For production deployments, verify the branch is `main` or `master` (or the project's designated release branch).
- For staging deployments, verify the branch is the expected staging or release candidate branch.
- Record the branch name and latest commit hash in the report.

This is a blocking check. Uncommitted changes risk deploying code that is not in version control.

## Step 4: Verify Branch and Commit

Confirm the deployment source matches expectations.

- Read the latest commit hash and message using `git_log`.
- Verify the commit is the expected one (not behind the remote).
- Use `shell` to run `git fetch` followed by checking if the local branch is up to date with its remote tracking branch.
- If the local branch is behind the remote, record a FAIL and report the number of commits behind.
- If the local branch is ahead of the remote, record a WARNING (code may not be pushed yet).
- Record the commit hash, author, date, and message in the report for audit purposes.

This is a blocking check if the branch is behind the remote. Deploying stale code is dangerous.

## Step 5: Check Dependency Lock Files

Verify that dependency lock files are consistent and up to date.

- Use `data_file_read` to read the manifest file (package.json, pyproject.toml, Cargo.toml, go.mod, pom.xml).
- Verify the corresponding lock file exists:
  - Node.js: `package-lock.json`, `yarn.lock`, or `pnpm-lock.yaml`.
  - Python: `poetry.lock`, `Pipfile.lock`, or `requirements.txt` (with pinned versions).
  - Rust: `Cargo.lock`.
  - Go: `go.sum`.
- Check that the lock file is not older than the manifest file (using filesystem metadata).
- For Node.js: run `npm ls` via shell to check for missing or extraneous dependencies.
- For Python with Poetry: run `poetry check` via shell.
- Record the result: PASS if lock files are present and consistent, FAIL if missing or outdated.

This is a blocking check. Inconsistent dependencies can cause unpredictable behavior in deployment.

## Step 6: Verify Environment Configuration

Check that environment-specific configuration files exist and are syntactically valid.

- Search for environment configuration files: `.env.production`, `.env.staging`, `config/production.yml`, `config/staging.yml`, or similar patterns.
- Read each configuration file and verify it is syntactically valid:
  - For `.env` files: check that each line follows the `KEY=VALUE` format and no required keys are missing.
  - For YAML configuration files: validate YAML syntax.
  - For JSON configuration files: validate JSON syntax.
- Cross-reference with a template or example configuration (`.env.example`, `config/example.yml`) if one exists. Check that all keys present in the template are also present in the environment file.
- Check that configuration values are not placeholder values (e.g., `CHANGE_ME`, `TODO`, `xxx`).
- Record the result: PASS if all required configuration files exist and are valid, FAIL otherwise.

CRITICAL: Do not log or display the values of configuration files, as they may contain secrets. Only report the presence and validity of keys.

## Step 7: Check Database Migrations

Determine whether there are pending database migrations that need to run as part of the deployment.

- Search for migration files in common locations: `migrations/`, `db/migrate/`, `alembic/versions/`, `prisma/migrations/`.
- If a migration tool is detected, attempt to check migration status:
  - Django: `python manage.py showmigrations` via shell.
  - Alembic: `alembic current` and `alembic heads` via shell.
  - Prisma: `npx prisma migrate status` via shell.
  - Rails: `rake db:migrate:status` via shell.
- Identify any migrations that have been created but not yet applied.
- Record the result: WARNING if pending migrations exist (not necessarily blocking, but must be noted).
- List each pending migration with its filename and description.

This is a non-blocking but highly important check. Pending migrations should be applied as part of the deployment process and their order must be verified.

## Step 8: Verify Docker Image Build

If the project uses Docker, verify that the Docker image builds successfully.

- Search for `Dockerfile` or `Dockerfile.*` files in the project.
- If found, use `shell` to run `docker build --no-cache -t deploy-check:latest .` (or the appropriate Dockerfile path).
- Monitor the build output for errors.
- Record the result: PASS if the Docker build succeeds, FAIL if it fails, SKIP if no Dockerfile is present.
- If the build fails, capture the error output and the failing build step.
- Check the resulting image size and report it. Unusually large images may indicate unnecessary files being included.

This is a blocking check if the project uses Docker for deployment.

## Step 9: Run Security Audit on Dependencies

Check for known vulnerabilities in project dependencies.

- Run the appropriate security audit command via `shell`:
  - Node.js: `npm audit --audit-level=high` or `yarn audit --level high`.
  - Python: `pip-audit` or `safety check`.
  - Rust: `cargo audit`.
  - Go: `govulncheck ./...`.
  - Java: run OWASP dependency-check if configured, or `mvn dependency-check:check`.
- Parse the audit output to count vulnerabilities by severity (critical, high, moderate, low).
- Record the result: FAIL if any critical or high severity vulnerabilities are found, WARNING if only moderate or low.
- List each vulnerability with its package name, severity, and advisory URL.

This is a blocking check for critical and high severity vulnerabilities. Moderate and low vulnerabilities should be noted but do not block deployment.

## Step 10: Generate Checklist Report

Compile all results into a structured checklist report.

```
## Pre-Deployment Checklist Report

**Project**: [project name]
**Branch**: [branch name]
**Commit**: [commit hash] - [commit message]
**Date**: [current date and time]
**Target**: [staging/production]

### Results

| # | Check | Status | Details |
|---|-------|--------|---------|
| 1 | Test Suite | PASS/FAIL | [X tests passed, Y failed] |
| 2 | Build | PASS/FAIL | [build time, warnings] |
| 3 | Git State | PASS/FAIL | [clean/dirty, file list] |
| 4 | Branch/Commit | PASS/FAIL | [branch, ahead/behind status] |
| 5 | Dependencies | PASS/FAIL | [lock file status] |
| 6 | Configuration | PASS/FAIL | [config files found/missing] |
| 7 | Migrations | PASS/WARN | [pending migration count] |
| 8 | Docker Build | PASS/FAIL/SKIP | [image size, build time] |
| 9 | Security Audit | PASS/FAIL/WARN | [vulnerability counts by severity] |

### Verdict: READY / BLOCKED
```

## Step 11: Block on Critical Failures

If any blocking check (Steps 1-5, 8, or 9 with critical/high vulnerabilities) has a FAIL status:

- Set the overall verdict to BLOCKED.
- List all blocking issues at the top of the report.
- For each blocking issue, provide a clear remediation path:
  - Failing tests: list the failing tests and suggest running them locally to debug.
  - Build failure: include the error output and suggest checking build configuration.
  - Dirty git state: list the uncommitted files and suggest committing or stashing them.
  - Outdated dependencies: suggest running the lock file update command.
  - Docker build failure: include the failing step output.
  - Security vulnerabilities: list the vulnerable packages and suggest updating them.

Do not proceed with deployment when the verdict is BLOCKED.

## Step 12: Send Notification

After generating the report, send a notification with the results.

- Use `notify_send` from the eMCP notify tool to send the checklist results.
- The notification should include:
  - The project name and target environment.
  - The overall verdict (READY or BLOCKED).
  - A count of passed and failed checks.
  - If BLOCKED, the list of blocking issues.
- Format the notification as a concise summary, not the full report.

## Manual Tracking Checklist

Provide the following markdown checklist that can be copied for manual tracking outside of this tool:

```markdown
## Deployment Checklist

- [ ] All tests pass
- [ ] Build completes without errors
- [ ] Working directory is clean (no uncommitted changes)
- [ ] Deploying from the correct branch
- [ ] Branch is up to date with remote
- [ ] Dependency lock files are current
- [ ] Environment configuration files exist and are valid
- [ ] Database migrations identified and planned
- [ ] Docker image builds successfully (if applicable)
- [ ] No critical or high security vulnerabilities
- [ ] Release notes prepared
- [ ] Rollback plan documented
- [ ] Monitoring and alerting verified
- [ ] Team notified of deployment
```

## Notes

- Run this checklist every time before deploying to staging or production.
- All blocking checks must pass before deployment proceeds.
- Non-blocking warnings should be reviewed and addressed when possible.
- The checklist report should be saved or shared with the team for audit purposes.
- For automated deployments, integrate these checks into the CI/CD pipeline as a required gate.
- Never skip checks to meet a deployment deadline. If checks fail, fix the issues first.

## Related Skills

- **security-scan** (eskill-quality): Run security-scan before this skill to include security verification steps in the deployment checklist.
- **dependency-audit** (eskill-coding): Run dependency-audit before this skill to ensure dependency health checks are part of the deploy process.
- **configuration-audit** (eskill-quality): Run configuration-audit before this skill to verify environment configurations are correct before deploying.
