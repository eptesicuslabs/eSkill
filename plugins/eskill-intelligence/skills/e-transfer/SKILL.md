---
name: e-transfer
description: "Generates knowledge transfer documentation for modules or features by tracing code paths and extracting business rules. Use for team transitions, onboarding to specific features, or documenting domain logic. Also applies when: 'knowledge transfer', 'document this module', 'onboarding guide for this feature', 'how does this feature work'."
---

# Knowledge Transfer Guide

This skill generates knowledge transfer documentation for a specific module, feature, or subsystem by tracing code paths, extracting business rules, identifying key abstractions, and documenting operational concerns. The output is structured to bring a new engineer up to speed without requiring the departing engineer's presence.

## Prerequisites

Confirm the target module or feature with the user. This may be:

- A directory or package (e.g., `src/billing/`).
- A feature area (e.g., "the authentication system").
- A specific workflow (e.g., "how orders are processed").
- A full codebase overview for team transition.

Identify the target audience (new team member, replacement engineer, cross-team collaborator) to calibrate the level of detail.

## Step 1: Map Module Boundaries

Use `filesystem` to identify all files belonging to the target module.

- List all files in the module directory recursively.
- Use `ast_search` to find import statements that reference the module from outside, establishing the module's public interface.
- Use `lsp_symbols` to extract exported symbols (functions, classes, types, constants) that constitute the module's API.
- Identify internal files (not imported from outside) versus public files (imported by other modules).

Record the module structure:

| File | Type | Public/Internal | Purpose |
|------|------|----------------|---------|
| index.ts | Entry point | Public | Re-exports public API |
| types.ts | Type definitions | Public | Shared types and interfaces |
| service.ts | Business logic | Internal | Core processing logic |
| repository.ts | Data access | Internal | Database queries |
| utils.ts | Utilities | Internal | Helper functions |
| __tests__/ | Test directory | Internal | Test suites |

Calculate module statistics: file count, total lines, test-to-source ratio, number of exported symbols.

## Step 2: Trace Entry Points and Data Flow

Use `ast_search` and `lsp_references` to trace how data enters and exits the module.

**Incoming data paths** (how the module receives work):
- HTTP route handlers that invoke module functions.
- Event listeners or message queue consumers.
- Scheduled job triggers (cron, task schedulers).
- Direct function calls from other modules.

For each entry point, trace the call chain through the module:

1. Start at the entry function.
2. Use `lsp_references` to follow each function call within the module.
3. Record the sequence of functions called and data transformations applied.
4. Note where external services are called (database queries, API calls, cache operations).
5. Identify the return path (what data flows back to the caller).

**Outgoing data paths** (what the module produces):
- Return values to callers.
- Database writes.
- Events published.
- Notifications sent.
- Files written.

Document each major data flow as a numbered sequence:

```
Flow: Create Order
1. POST /orders -> OrderController.create()
2. OrderController.create() -> OrderService.createOrder(dto)
3. OrderService.createOrder() validates input against OrderSchema
4. OrderService.createOrder() -> InventoryService.reserveItems(items)
5. OrderService.createOrder() -> OrderRepository.save(order)
6. OrderService.createOrder() -> EventBus.publish('order.created', order)
7. Return OrderResponse to caller
```

## Step 3: Extract Business Rules

Use `ast_search` to find conditional logic, validation rules, and business constraints within the module.

**Validation rules**: Search for validation schema definitions, guard clauses, assertion statements, and input checking patterns.

For each validation rule, document:
- What is being validated.
- The constraint (min/max, required, format, relationship between fields).
- What happens when validation fails (error response, exception, default value).

**Business logic branches**: Search for conditional statements (`if`, `switch`, `match`) in service-layer code that implement business decisions.

For each business rule, document:
- The condition in plain language (e.g., "If the order total exceeds $1000, require manager approval").
- Where the rule is implemented (file and line).
- Whether the rule is configurable (threshold in config vs hardcoded).
- Edge cases handled (null values, boundary conditions, race conditions).

**State machines**: Identify any state machine patterns (order status transitions, workflow states, approval processes).

| Current State | Event | Next State | Side Effects |
|--------------|-------|-----------|-------------|
| Draft | Submit | Pending Review | Send notification |
| Pending Review | Approve | Active | Enable features |
| Pending Review | Reject | Draft | Send rejection reason |
| Active | Expire | Expired | Disable features |
| Active | Cancel | Cancelled | Process refund |

## Step 4: Identify Key Abstractions

Use `lsp_symbols` to extract the most important types, interfaces, and classes in the module.

For each key abstraction:

1. **Name and kind**: Class, interface, type alias, enum.
2. **Purpose**: What it represents in the domain.
3. **Fields/properties**: What data it holds, with types and descriptions.
4. **Methods**: What operations it supports, with parameter and return types.
5. **Relationships**: How it relates to other types (extends, implements, contains, references).
6. **Invariants**: What must always be true about instances of this type (e.g., "end_date is always after start_date").

Use `lsp_references` to find where each abstraction is instantiated and used, which reveals its role in the system.

Present the domain model as a table:

| Type | Kind | Key Fields | Used By | Invariants |
|------|------|-----------|---------|------------|
| Order | Class | id, items, total, status | OrderService, OrderController | total == sum(items.price * items.qty) |
| OrderItem | Class | productId, quantity, price | Order | quantity > 0, price >= 0 |
| OrderStatus | Enum | Draft, Pending, Active, Cancelled | Order, OrderService | Transitions follow state machine |

## Step 5: Document External Dependencies

Identify all external services, APIs, and infrastructure the module depends on.

Use `ast_search` to find:
- HTTP client calls to external services.
- Database connection usage.
- Cache operations.
- Message queue publish/subscribe calls.
- File system operations.
- Third-party SDK usage.

For each dependency, document:

| Dependency | Type | Purpose | Failure Impact | Fallback |
|-----------|------|---------|---------------|----------|
| PostgreSQL | Database | Order persistence | Module non-functional | None (hard dependency) |
| Redis | Cache | Session and rate limiting | Degraded performance | Falls back to DB queries |
| Stripe API | Payment processing | Charge creation | Cannot complete orders | Queue for retry |
| S3 | Object storage | Invoice PDF storage | Invoices unavailable | Generate on demand |

Note authentication requirements for each dependency (API keys, service accounts, connection strings) and where the credentials are stored (environment variables, secret manager, config file).

## Step 6: Map Configuration and Feature Flags

Use `filesystem` and `data_file_read` to identify configuration values that affect module behavior.

Search for:
- Environment variable access (`process.env.`, `os.environ`, `std::env::var`).
- Configuration file reads.
- Feature flag checks.
- Constants defined at the module level.

Document each configuration value:

| Config Key | Type | Default | Description | Impact of Change |
|-----------|------|---------|-------------|-----------------|
| ORDER_MAX_ITEMS | number | 100 | Maximum items per order | Validation behavior |
| ENABLE_BULK_ORDERS | boolean | false | Feature flag for bulk ordering | Enables new API endpoint |
| PAYMENT_TIMEOUT_MS | number | 30000 | Payment processing timeout | Affects order completion rate |
| TAX_RATE_OVERRIDE | string | null | Override default tax calculation | Uses fixed rate instead of dynamic |

Note which configuration changes require restart versus which are hot-reloadable.

## Step 7: Document Error Handling and Failure Modes

Use `ast_search` to analyze error handling within the module.

Identify:

1. **Custom error types**: Classes extending Error, custom exception hierarchies.
2. **Error propagation**: How errors flow through the module (thrown, returned as Result, passed to callback).
3. **Error recovery**: Retry logic, circuit breakers, fallback behavior.
4. **Error reporting**: How errors are logged, monitored, and alerted on.
5. **User-facing errors**: How internal errors translate to user-visible error messages or status codes.

Document common failure scenarios:

| Scenario | Error Type | User Impact | Recovery | Monitoring |
|----------|-----------|-------------|----------|------------|
| Database unavailable | ConnectionError | 500 error on all requests | Retry with backoff, then circuit break | Alert on connection failure count |
| Payment declined | PaymentError | 402 with decline reason | User retries with different method | Dashboard metric |
| Inventory insufficient | BusinessError | 409 with item availability | User adjusts quantities | Log only |
| Rate limit hit | ThrottleError | 429 with retry-after header | Automatic after cooldown | Alert on sustained throttling |

## Step 8: Analyze Test Coverage and Quality

Use `filesystem` to find test files for the module and `data_file_read` to read them.

Document:

1. **Test organization**: Where tests live, naming conventions, test utilities.
2. **Test types**: Unit tests, integration tests, end-to-end tests, contract tests.
3. **Key test scenarios**: What business scenarios are covered by tests. Map tests to the business rules from Step 3.
4. **Test fixtures and factories**: How test data is created. Identify shared fixtures.
5. **Mocking strategy**: What is mocked (external services, databases) and how (manual mocks, library mocks, in-memory substitutes).
6. **Coverage gaps**: Business rules or code paths that lack test coverage.

Present as a coverage map:

| Business Rule | Test Coverage | Test File | Notes |
|--------------|--------------|-----------|-------|
| Order total calculation | Covered | order.test.ts:15 | Tests edge cases for discounts |
| Manager approval threshold | Covered | order.test.ts:45 | Tests boundary at $1000 |
| Inventory reservation | Partial | order.test.ts:78 | Missing concurrent reservation test |
| Payment retry logic | Not covered | - | Risk area, needs test |

## Step 9: Compile the Knowledge Transfer Document

Use `filesystem` to write the guide and `markdown` for formatting. Structure the document with these sections: Overview (2-3 sentences), Architecture (module structure from Step 1, data flows from Step 2), Business Rules (rules and state machines from Step 3), Domain Model (key abstractions from Step 4), Dependencies (table from Step 5), Configuration (table from Step 6), Error Handling (failure modes from Step 7), Testing (coverage analysis from Step 8), Operational Notes (deployment considerations, monitoring, known issues), and Quick Reference (common tasks table, key files table with read-first priority).

## Step 10: Review and Deliver

Review the document for completeness and accuracy.

Checklist:

1. A new engineer can understand the module's purpose from the overview alone.
2. All major code paths are documented with entry points and data flows.
3. Business rules are described in plain language, not just code references.
4. External dependencies list includes failure modes and authentication.
5. Configuration values are documented with their impact.
6. Common operational tasks have step-by-step instructions.
7. No sensitive information (credentials, internal URLs) appears in the document.

Present the guide to the user. If they identify gaps, iterate on specific sections using the analysis tools.

Use `git` to determine if there are recent changes to the module that should be highlighted as "recent context" for the incoming engineer.

## Edge Cases

- **Module with no clear boundaries**: If the feature spans multiple directories without clean separation, define the boundary by the set of files that participate in the feature's primary workflow. Document the boundary definition in the guide.
- **Heavily coupled modules**: If the module has tight coupling with other modules (circular dependencies, shared mutable state), document the coupling points explicitly and note them as architectural debt.
- **Legacy code without tests**: For untested modules, emphasize the business rule documentation and recommend writing characterization tests as part of the knowledge transfer process.
- **Microservice boundary**: If the module is an entire microservice, include API contract documentation, deployment runbook references, and inter-service communication patterns.
- **Shared library**: If the module is a shared library consumed by multiple services, document the versioning strategy, release process, and consumer list.
- **Departing engineer unavailable**: If the knowledge transfer is happening without the original author, rely more heavily on code analysis and git history (commit messages, PR descriptions) to reconstruct intent.

## Related Skills

- **e-context** (eskill-intelligence): Run e-context before this skill to gather the session context and artifacts for the transfer package.
- **e-carto** (eskill-intelligence): Run e-carto before this skill to include architectural maps in the knowledge transfer guide.
- **e-adr** (eskill-office): Run e-adr before this skill to include decision records in the knowledge transfer package.
