---
name: monitoring-config
description: "Generates monitoring and alerting configs for Prometheus, health checks, and log-based alerts. Use when setting up observability, adding monitoring to a service, or reviewing coverage gaps. Also applies when: 'set up monitoring', 'add Prometheus metrics', 'create alerting rules', 'health check'."
---

# Monitoring Configuration

This skill generates monitoring, alerting, and observability configurations tailored to the project's architecture. It scans the codebase to identify monitorable components, generates health check endpoints, produces Prometheus metric and alerting rule configurations, sets up log-based alerting, and creates a monitoring coverage report.

## Step 1: Scan for Monitorable Components

Analyze the project to build an inventory of all components that should be monitored.

### HTTP Endpoints

- Use `ast_search` or filesystem search to find route definitions in the codebase.
- For Express.js (Node.js): search for `app.get(`, `app.post(`, `router.get(`, `router.post(`, and similar patterns.
- For FastAPI/Flask (Python): search for `@app.route(`, `@app.get(`, `@app.post(`, `@router.get(`, and similar decorators.
- For Gin/Echo (Go): search for `r.GET(`, `r.POST(`, `e.GET(`, `e.POST(` and similar.
- For Spring Boot (Java): search for `@GetMapping`, `@PostMapping`, `@RequestMapping` annotations.
- For Actix/Axum (Rust): search for route macro patterns and handler function definitions.
- Record each endpoint with its HTTP method, path pattern, and handler function name.

### Background Jobs and Workers

- Search for job scheduling patterns: cron expressions, queue consumers, background task definitions.
- For Node.js: search for Bull/BullMQ queue definitions, node-cron patterns, or Agenda job definitions.
- For Python: search for Celery tasks (`@app.task`, `@shared_task`), APScheduler jobs, or RQ workers.
- For Go: search for goroutine-based workers, ticker patterns, or cron library usage.
- For Java: search for `@Scheduled` annotations, Quartz job definitions.
- Record each background job with its name, schedule (if periodic), and purpose.

### Database Connections

- Search for database connection configuration: connection strings, ORM configuration, database client initialization.
- Identify the database type: PostgreSQL, MySQL, MongoDB, Redis, SQLite, etc.
- Record each database connection with its type and purpose (primary datastore, cache, session store, etc.).
- Note connection pool configurations if present (min/max connections, timeout settings).

### External Service Dependencies

- Search for HTTP client instantiation and API calls to external services.
- Search for SDK initialization for cloud services (AWS, GCP, Azure).
- Search for message broker connections (RabbitMQ, Kafka, NATS).
- Search for email service configuration (SMTP, SendGrid, SES).
- Record each external dependency with its type, endpoint (if discoverable), and purpose.

## Step 2: Determine Key Metrics per Component

For each component identified in Step 1, define the key metrics based on the four golden signals of monitoring.

### HTTP Endpoints
- **Latency**: request duration in milliseconds, measured as a histogram with p50, p90, p95, and p99 percentiles.
- **Error Rate**: percentage of responses with 4xx and 5xx status codes, tracked separately.
- **Throughput**: requests per second, broken down by endpoint and method.
- **Saturation**: number of in-flight requests, connection pool usage.

### Background Jobs
- **Latency**: job execution duration from dequeue to completion.
- **Error Rate**: percentage of jobs that fail or are retried.
- **Throughput**: jobs processed per second/minute.
- **Saturation**: queue depth (number of pending jobs), worker utilization.

### Database Connections
- **Latency**: query execution time, connection acquisition time.
- **Error Rate**: failed queries, connection errors, timeout errors.
- **Throughput**: queries per second.
- **Saturation**: connection pool utilization (active/idle/max connections).

### External Services
- **Latency**: response time from external service calls.
- **Error Rate**: failed requests, timeout errors, circuit breaker trips.
- **Throughput**: requests per second to each external service.
- **Saturation**: concurrent outbound connections.

## Step 3: Generate Health Check Endpoint

If the project does not already have a health check endpoint, generate one. Search for existing health check routes first (common paths: `/health`, `/healthz`, `/readyz`, `/status`, `/ping`).

### Basic Health Check

Generate a minimal health check endpoint that returns HTTP 200 with a JSON body:

```json
{
  "status": "healthy",
  "timestamp": "2026-03-18T12:00:00Z"
}
```

This endpoint should:
- Respond within milliseconds (no external calls).
- Be used by load balancers and container orchestrators to determine if the process is running.
- Return HTTP 200 for healthy, HTTP 503 for unhealthy.

### Deep Health Check

Generate a comprehensive health check endpoint that verifies all dependencies:

```json
{
  "status": "healthy",
  "timestamp": "2026-03-18T12:00:00Z",
  "checks": {
    "database": { "status": "healthy", "latency_ms": 12 },
    "redis": { "status": "healthy", "latency_ms": 3 },
    "external_api": { "status": "healthy", "latency_ms": 45 },
    "disk_space": { "status": "healthy", "free_gb": 42.5 }
  }
}
```

This endpoint should:
- Check database connectivity by executing a lightweight query (e.g., `SELECT 1`).
- Check Redis connectivity by executing `PING`.
- Check external service availability with a lightweight request or known health endpoint.
- Check disk space availability.
- Return HTTP 200 if all checks pass, HTTP 503 if any critical check fails.
- Include latency for each check.
- Implement a timeout for each individual check (e.g., 5 seconds) so a slow dependency does not block the entire health check.

Generate the health check code in the project's primary language, following the existing code style and patterns.

## Step 4: Generate Prometheus Metrics Configuration

Generate Prometheus metric definitions and scrape configuration for the project.

### Metric Definitions

Define the following metrics using the appropriate Prometheus metric types:

#### HTTP Request Duration Histogram

```yaml
- name: http_request_duration_seconds
  type: histogram
  help: "Duration of HTTP requests in seconds"
  labels: [method, path, status_code]
  buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
```

#### HTTP Request Total Counter

```yaml
- name: http_requests_total
  type: counter
  help: "Total number of HTTP requests"
  labels: [method, path, status_code]
```

#### Active Connections Gauge

```yaml
- name: http_active_connections
  type: gauge
  help: "Number of active HTTP connections"
```

#### Database Query Duration Histogram

```yaml
- name: db_query_duration_seconds
  type: histogram
  help: "Duration of database queries in seconds"
  labels: [operation, table]
  buckets: [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 5]
```

#### Database Connection Pool Gauge

```yaml
- name: db_connection_pool_size
  type: gauge
  help: "Current size of the database connection pool"
  labels: [state]  # active, idle, waiting
```

#### Background Job Duration Histogram

```yaml
- name: job_duration_seconds
  type: histogram
  help: "Duration of background job execution in seconds"
  labels: [job_name, status]
  buckets: [0.1, 0.5, 1, 5, 10, 30, 60, 300]
```

#### Background Job Queue Depth Gauge

```yaml
- name: job_queue_depth
  type: gauge
  help: "Number of jobs waiting in the queue"
  labels: [queue_name]
```

#### Custom Business Metrics

Based on the project type, suggest relevant business metrics:
- E-commerce: orders_processed_total, cart_abandonment_total, payment_failures_total.
- SaaS: active_users_gauge, api_calls_by_tenant_total, feature_usage_total.
- Content platform: content_views_total, upload_size_bytes_histogram, processing_queue_depth.

### Prometheus Scrape Configuration

Generate a `prometheus.yml` scrape configuration:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "application"
    metrics_path: "/metrics"
    static_configs:
      - targets: ["localhost:PORT"]
        labels:
          environment: "production"
          service: "SERVICE_NAME"
```

Replace `PORT` and `SERVICE_NAME` with values detected from the project configuration.

## Step 5: Generate Alerting Rules

Define alerting rules based on the SRE golden signals. Generate these in Prometheus alerting rule format.

### Latency Alerts

```yaml
groups:
  - name: latency_alerts
    rules:
      - alert: HighRequestLatency
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High p99 request latency"
          description: "The p99 request latency has exceeded 1 second for the past 5 minutes. Current value: {{ $value }}s."

      - alert: CriticalRequestLatency
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 5.0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Critical p99 request latency"
          description: "The p99 request latency has exceeded 5 seconds for the past 2 minutes. Current value: {{ $value }}s."
```

### Error Rate Alerts

```yaml
      - alert: HighErrorRate
        expr: sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High 5xx error rate"
          description: "More than 5% of requests are returning 5xx errors. Current rate: {{ $value | humanizePercentage }}."

      - alert: CriticalErrorRate
        expr: sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.10
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Critical 5xx error rate"
          description: "More than 10% of requests are returning 5xx errors. Current rate: {{ $value | humanizePercentage }}."
```

### Traffic Alerts

```yaml
      - alert: TrafficDrop
        expr: sum(rate(http_requests_total[5m])) < (sum(rate(http_requests_total[5m] offset 1h)) * 0.5)
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Significant traffic drop detected"
          description: "Current traffic is less than 50% of the traffic from 1 hour ago."

      - alert: NoTraffic
        expr: sum(rate(http_requests_total[5m])) == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "No traffic detected"
          description: "No HTTP requests have been received in the past 5 minutes."
```

### Saturation Alerts

```yaml
      - alert: HighConnectionPoolUsage
        expr: db_connection_pool_size{state="active"} / db_connection_pool_size{state="max"} > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connection pool usage is high"
          description: "More than 80% of database connections are in use."

      - alert: JobQueueBacklog
        expr: job_queue_depth > 1000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Background job queue backlog"
          description: "The job queue has more than 1000 pending jobs. Current depth: {{ $value }}."
```

## Step 6: Generate Log-Based Alerts

Define alerting rules based on log patterns. Use `log_search` from the eMCP log tool to identify existing log patterns in the project.

### Error Rate Spike

Monitor for a sudden increase in error-level log entries:

- Define a baseline error rate by analyzing recent logs.
- Alert when the error rate exceeds 2x the baseline over a 5-minute window.
- Include the log source and error patterns in the alert definition.

### Specific Error Patterns

Search the codebase for error handling patterns and log statements that indicate critical failures:

- Database connection failures: search for log messages containing "connection refused", "timeout", "connection pool exhausted".
- Authentication failures: search for log messages related to "unauthorized", "invalid token", "authentication failed".
- External service failures: search for log messages about "upstream error", "service unavailable", "circuit breaker open".
- Out of memory: search for patterns indicating memory pressure.

For each identified pattern, create an alert rule:

```yaml
- pattern: "connection pool exhausted"
  threshold: 1
  window: 5m
  severity: critical
  action: "Check database connection pool configuration and active connections"

- pattern: "circuit breaker open"
  threshold: 1
  window: 1m
  severity: critical
  action: "Check external service availability and circuit breaker configuration"
```

### Missing Expected Log Entries (Heartbeat)

Identify periodic processes that should produce regular log entries:

- Cron jobs or scheduled tasks should log their execution.
- Health check endpoints should produce access logs.
- Background workers should log activity.

Create absence-based alerts for these expected log entries:

```yaml
- name: MissingHeartbeat
  description: "Expected periodic log entry not seen"
  pattern: "scheduled task completed"
  expected_interval: 5m
  alert_after_missing: 15m
  severity: warning
```

## Step 7: Write Configuration Files

Write all generated configurations to the appropriate file paths.

- Write Prometheus scrape configuration to `monitoring/prometheus.yml`.
- Write Prometheus alerting rules to `monitoring/alerts/application.rules.yml`.
- Write health check endpoint code to the appropriate source directory based on project structure.
- Write log-based alert configurations to `monitoring/alerts/log-alerts.yml`.
- Write a monitoring dashboard configuration if applicable (e.g., Grafana JSON).

Use the filesystem write tool to create each file. Create the `monitoring/` directory structure if it does not exist.

For each file written, report the file path and a brief description of its contents.

Ensure all configuration files use proper YAML or JSON syntax. Validate the structure before writing.

## Step 8: Generate Monitoring Coverage Report

Produce a report that summarizes what is monitored, what is not, and what should be added.

### Report Structure

```
## Monitoring Coverage Report

### Components Inventory
| Component | Type | Monitored | Metrics | Alerts | Health Check |
|-----------|------|-----------|---------|--------|--------------|
| /api/users | HTTP endpoint | Yes | latency, errors, throughput | Yes | N/A |
| /api/orders | HTTP endpoint | Yes | latency, errors, throughput | Yes | N/A |
| order-processor | Background job | Yes | duration, queue depth | Yes | N/A |
| PostgreSQL | Database | Yes | query latency, pool usage | Yes | Deep check |
| Redis | Cache | Yes | connection status | Yes | Deep check |
| Stripe API | External service | Partial | error rate | No | No |

### Coverage Summary
- HTTP endpoints: X/Y monitored (Z%)
- Background jobs: X/Y monitored (Z%)
- Databases: X/Y monitored (Z%)
- External services: X/Y monitored (Z%)

### Gaps and Recommendations
1. [Component] is not monitored. Recommended: add [specific metrics and alerts].
2. [Component] has metrics but no alerting rules. Recommended: add alerts for [conditions].
3. No log-based alerting for [pattern]. Recommended: add pattern-based alert.

### Generated Files
- monitoring/prometheus.yml - Prometheus scrape configuration
- monitoring/alerts/application.rules.yml - Alerting rules
- monitoring/alerts/log-alerts.yml - Log-based alert definitions
- src/health.js (or equivalent) - Health check endpoint
```

Present this report to the user. Highlight any critical gaps where important components lack monitoring entirely.

## Safety Protocol

1. Before writing any configuration file, validate the generated YAML syntax by parsing it.
2. For Prometheus alerting rules, verify that all PromQL expressions are syntactically valid.
3. Present all generated configurations to the user for review before writing to disk.
4. If existing monitoring configuration files are present, show a diff and ask for confirmation before overwriting.
5. For health check endpoint code, present the code for review before writing to the source directory.

## Notes

- Metric names should follow Prometheus naming conventions: snake_case, with a unit suffix (e.g., `_seconds`, `_bytes`, `_total`).
- Use labels judiciously. High-cardinality labels (e.g., user IDs, request IDs) should never be used as metric labels as they cause excessive time series.
- Histogram buckets should be chosen based on expected latency ranges. The defaults above are starting points and should be tuned based on actual performance characteristics.
- Alert thresholds are starting values. Recommend that the team tunes them based on observed baseline behavior after initial deployment.
- The `for` duration on alerts prevents alerting on transient spikes. Critical alerts should have shorter `for` durations than warnings.
- Always include both a `summary` and `description` annotation on alerts. The summary should be short enough for a pager notification. The description should include the current metric value.
- Health check endpoints should not require authentication, as they are called by infrastructure components (load balancers, orchestrators) that may not have credentials.
- Deep health checks should be rate-limited or cached to prevent them from overwhelming downstream dependencies when called frequently.

## Related Skills

- **deployment-checklist** (eskill-devops): Run deployment-checklist before this skill to ensure monitoring is configured as part of the deployment process.
- **log-investigation** (eskill-system): Follow up with log-investigation after this skill to verify that configured monitors capture the expected log patterns.
