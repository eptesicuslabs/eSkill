---
name: e-e2e
description: "Orchestrates end-to-end test workflows including environment setup, test data seeding, execution, and result analysis. Use when setting up E2E testing, debugging E2E failures, or managing test environments. Also applies when: 'set up E2E tests', 'run end-to-end tests', 'Playwright setup', 'Cypress configuration', 'why is my E2E test failing'."
---

# E2E Orchestration

This skill manages the full lifecycle of end-to-end test workflows: detecting the E2E framework, provisioning test environments with Docker, seeding test data, executing tests, and analyzing failures including screenshot and video artifacts.

## Prerequisites

- A web application or service with a running or startable development server.
- An E2E framework installed or a preference for one.
- Docker available if the application depends on external services (databases, queues, etc.).

## Workflow

### Step 1: Detect the E2E Framework

Identify which E2E framework the project uses by inspecting dependency manifests and configuration files.

Use `filesystem` tools (fs_list, fs_read) to check the project root:

| File / Dependency                  | Framework    | Config File                    |
|------------------------------------|------------- |--------------------------------|
| `@playwright/test` in package.json | Playwright   | `playwright.config.ts`         |
| `cypress` in package.json          | Cypress      | `cypress.config.ts`            |
| `selenium-webdriver` in deps       | Selenium     | Custom, check for driver setup |
| `puppeteer` in package.json        | Puppeteer    | Custom launch scripts          |
| `testcafe` in package.json         | TestCafe     | `.testcaferc.json`             |
| `pytest` + `selenium` in Python    | Selenium/Py  | `conftest.py`                  |
| No framework detected              | Ask user     | --                             |

If no E2E framework is installed, recommend Playwright as the default for new projects due to its cross-browser support and built-in tooling. Provide installation steps but do not install without user confirmation.

Read the framework configuration file using `fs_read` to understand existing settings: base URL, browser targets, timeout values, and output directories.

### Step 2: Inventory External Service Dependencies

E2E tests often require external services. Identify what the application needs by scanning configuration:

1. Use `filesystem` tools to read environment files (`.env`, `.env.test`, `.env.e2e`).
2. Use `ast_search` to find database connection strings, API base URLs, and service endpoints in the source code.
3. Check for existing Docker Compose files (`docker-compose.yml`, `docker-compose.test.yml`, `docker-compose.e2e.yml`).

Build a dependency table:

| Service    | Required For        | Connection String                  | Docker Image         |
|------------|---------------------|------------------------------------|----------------------|
| PostgreSQL | User data, sessions | `DATABASE_URL` in .env             | `postgres:16-alpine` |
| Redis      | Session cache       | `REDIS_URL` in .env                | `redis:7-alpine`     |
| Mailhog    | Email verification  | `SMTP_HOST` in .env                | `mailhog/mailhog`    |

### Step 3: Set Up the Test Environment

Use `docker` tools from the eMCP Docker server to manage test infrastructure:

1. If a Docker Compose file for E2E exists, start it:
   ```
   docker compose -f docker-compose.e2e.yml up -d
   ```
2. If no Compose file exists, generate one based on the dependency table from Step 2. Write it using `filesystem` tools.
3. Wait for services to be healthy before proceeding. Use `shell` tools (shell_exec) to poll health endpoints:
   ```
   docker compose -f docker-compose.e2e.yml up -d --wait
   ```
4. Run database migrations if applicable:
   ```
   npx prisma migrate deploy
   python manage.py migrate
   ```

Verify each service is reachable. If a service fails to start, check its logs using `log` tools (log_read, log_tail) on the Docker container output.

### Step 4: Seed Test Data

E2E tests require a known data state. Determine the seeding strategy:

| Strategy               | When to Use                            | Implementation                    |
|------------------------|----------------------------------------|-----------------------------------|
| Seed script            | Fixed dataset for all tests            | Run `npm run seed:e2e`            |
| Per-test API setup     | Tests need isolated data               | Call API endpoints in beforeEach  |
| Database snapshot      | Large dataset, fast restore needed     | pg_restore or mongorestore        |
| Factory functions      | Dynamic data per test                  | Use e-factory skill       |

Use `filesystem` tools to check for existing seed scripts in `scripts/`, `test/`, or `e2e/` directories. If a seed script exists, run it using `shell` tools. If none exists, check for Prisma seed configuration (`prisma/seed.ts`), Django fixtures (`fixtures/`), or raw SQL seed files.

Use `data_file` tools to read and validate seed data files (JSON, CSV, SQL).

### Step 5: Start the Application Under Test

The application must be running before E2E tests execute:

1. Check if the application is already running by hitting the base URL with `shell` tools:
   ```
   curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
   ```
2. If not running, use `shell_bg` to start it in the background:
   ```
   npm run dev
   python manage.py runserver
   ```
   Use `shell_status` to confirm the background process is alive, then poll the health endpoint until the application is ready.

For Playwright, the config file typically handles this via the `webServer` option. Check `playwright.config.ts` for an existing `webServer` block.

### Step 6: Execute the E2E Tests

Run the tests using the appropriate command via `test_run` from the eMCP test server:

| Framework  | Command                                   | Key Flags                          |
|------------|-------------------------------------------|------------------------------------|
| Playwright | `npx playwright test`                     | `--project=chromium --reporter=json` |
| Cypress    | `npx cypress run`                         | `--browser chrome --reporter json` |
| Selenium   | `pytest tests/e2e/ -v`                    | `--tb=short --json-report`         |
| Puppeteer  | `node tests/e2e/run.js`                   | Custom runner                      |
| TestCafe   | `npx testcafe chrome tests/e2e/`          | `--reporter json`                  |

Pass the `--reporter json` flag (or equivalent) to get structured output for analysis.

For selective execution, use test filtering:
- Playwright: `npx playwright test --grep "login"`
- Cypress: `npx cypress run --spec "cypress/e2e/login.cy.ts"`

### Step 7: Analyze Test Results

Parse the JSON test results using `data_file` tools. Extract:

1. Total tests, passed, failed, skipped.
2. For each failure:
   - Test name and file location.
   - Error message and stack trace.
   - Duration (to detect timeout failures vs assertion failures).

Categorize failures:

| Category           | Indicators                                 | Common Cause                        |
|--------------------|--------------------------------------------|-------------------------------------|
| Timeout            | Error contains "timeout" or "exceeded"     | Slow application, missing element   |
| Selector not found | "locator resolved to 0 elements"           | Changed UI, wrong selector          |
| Assertion failure  | "expect(...).toBe(...)" style errors       | Logic change, data mismatch         |
| Network error      | Connection refused, 500 status             | Service down, wrong URL             |
| Authentication     | 401/403 status codes                       | Expired tokens, wrong credentials   |

### Step 8: Collect and Analyze Artifacts

E2E frameworks produce artifacts on failure. Locate and analyze them:

1. Use `filesystem` tools to find artifact directories:
   - Playwright: `test-results/` (screenshots, videos, traces)
   - Cypress: `cypress/screenshots/`, `cypress/videos/`
2. For Playwright traces, note the trace file path so the user can view it:
   ```
   npx playwright show-trace test-results/test-name/trace.zip
   ```
3. List all screenshots from failed tests and correlate them with the failure messages from Step 7.
4. Check video recordings to understand the sequence of events leading to failure.

Report artifacts alongside failures:

```
## Failed: Login with valid credentials
- Error: Locator "data-testid=submit-btn" resolved to 0 elements
- Screenshot: test-results/login-test/screenshot.png
- Trace: test-results/login-test/trace.zip
- Likely cause: Submit button test ID changed or element not rendered
```

### Step 9: Report Results and Suggest Fixes

Compile a summary report:

```
## E2E Test Results

### Summary
- Total: 45 tests across 8 spec files
- Passed: 41
- Failed: 3
- Skipped: 1
- Duration: 2m 34s

### Failures
1. login.spec.ts > Login with valid credentials
   - Category: Selector not found
   - Fix: Update selector from data-testid=submit-btn to data-testid=login-submit

2. checkout.spec.ts > Complete purchase flow
   - Category: Timeout
   - Fix: Payment service container not started; check docker-compose.e2e.yml

3. profile.spec.ts > Upload avatar
   - Category: Network error
   - Fix: File upload endpoint returns 500; check server logs
```

For each failure, use `ast_search` to find the test source code and identify the failing line. Cross-reference with the application source to suggest whether the fix belongs in the test or the application.

## Edge Cases

- **Parallel test execution**: If tests modify shared state (database, files), parallel runs cause flakiness. Check the framework's parallelism settings and recommend isolation strategies (per-worker databases, transactions that roll back).
- **Authentication flows**: Tests requiring login should use API-based authentication to set cookies or tokens directly, avoiding the UI login flow in every test.
- **Dynamic content**: Tests that assert against timestamps, random IDs, or live data need tolerance. Suggest using regex matchers or freezing time.
- **CI vs local differences**: If tests pass locally but fail in CI, check for headless browser configuration, screen resolution settings, font rendering differences, and environment variable availability.
- **Flaky tests**: If a test fails intermittently, delegate to the e-flaky skill for deeper analysis.
- **Port conflicts**: If the application or services fail to start due to port conflicts, use `shell_status` to check for orphaned background processes from previous test runs and `shell_kill` to terminate them.

## Related Skills

- **e-integ** (eskill-coding): Run e-integ before this skill to establish integration-level coverage before orchestrating end-to-end tests.
- **e-factory** (eskill-testing): Run e-factory before this skill to generate the test fixtures that end-to-end scenarios require.
