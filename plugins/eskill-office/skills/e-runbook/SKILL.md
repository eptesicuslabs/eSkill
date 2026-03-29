---
name: e-runbook
description: "Generates operational runbooks from infrastructure configs, monitoring rules, and incident patterns. Use when documenting ops procedures, creating on-call guides, or standardizing incident response. Also applies when: 'create a runbook', 'on-call documentation', 'incident response guide', 'ops playbook'."
---

# Runbook Generator

This skill generates operational runbooks by analyzing infrastructure configurations, monitoring rules, deployment scripts, and log patterns. It produces step-by-step procedures for common operational scenarios including incident response, scaling operations, deployment rollbacks, and maintenance tasks.

## Prerequisites

Confirm the scope of the runbook with the user. Determine whether the runbook covers a single service, a group of services, or the entire platform. Identify the target audience (on-call engineer, SRE team, developer on rotation) as this affects the level of detail.

The following eMCP tools support runbook content extraction:

- `markdown_front_matter` -- parse YAML frontmatter from existing runbook or documentation files to extract metadata (service name, owner, last updated, severity levels) without reading the full document
- `markdown_read_section` -- extract content under a specific heading from existing runbooks or operational docs (e.g., pull just the "Escalation" or "Diagnostic Steps" section for reuse)

## Step 1: Inventory Operational Infrastructure

Use `filesystem` to scan the project for operational configuration files and `data_file_read` to read them. If existing runbooks or operational documentation exist, use `markdown_front_matter` to read their metadata (service, owner, last-updated) and `markdown_read_section` to extract specific sections for reuse or reference rather than re-reading entire documents.

Locate and read:

- **Monitoring configuration**: Prometheus rules, Grafana dashboards (JSON), Datadog monitors, CloudWatch alarms, PagerDuty service definitions.
- **Deployment configuration**: CI/CD pipelines, deployment scripts, Kubernetes manifests, Docker Compose files, Helm charts.
- **Infrastructure definitions**: Terraform files, CloudFormation templates, Ansible playbooks.
- **Logging configuration**: Log shipping configs (Fluentd, Filebeat, Vector), log storage settings.
- **Alerting rules**: Alert definitions with thresholds, escalation policies, notification channels.

For each operational component, record:

| Component | Type | Configuration File | Key Settings |
|-----------|------|-------------------|--------------|
| PostgreSQL | Database | docker-compose.yml | Port 5432, 2 replicas |
| Redis | Cache | docker-compose.yml | Port 6379, maxmemory 256mb |
| API service | Application | kubernetes/deployment.yaml | 3 replicas, 512Mi memory |
| Nginx | Reverse proxy | nginx/nginx.conf | Upstream to API, SSL termination |

## Step 2: Extract Alert Definitions

Use `data_file_read` to parse monitoring and alerting configurations.

For Prometheus alerting rules, extract:
- Alert name and severity label.
- Condition expression (PromQL query).
- Duration (`for` clause).
- Annotations (summary, description, runbook URL).

For CloudWatch alarms, extract:
- Alarm name and metric.
- Threshold and comparison operator.
- Period and evaluation periods.
- Alarm actions (SNS topics, Auto Scaling actions).

For each alert, document:

| Alert | Severity | Condition | Threshold | Duration |
|-------|----------|-----------|-----------|----------|
| HighCPU | Warning | `avg(cpu_usage) > 80%` | 80% | 5 min |
| HighErrorRate | Critical | `rate(http_5xx) > 0.05` | 5% of requests | 2 min |
| DiskSpaceLow | Warning | `disk_usage > 85%` | 85% | 10 min |
| HealthCheckFailing | Critical | `up == 0` | Target down | 1 min |
| MemoryPressure | Warning | `memory_usage > 90%` | 90% | 5 min |
| QueueBacklog | Warning | `queue_depth > 1000` | 1000 messages | 15 min |

## Step 3: Analyze Deployment Procedures

Use `data_file_read` to read CI/CD configuration files and deployment scripts.

Extract:

1. **Deployment method**: Direct push, blue-green, canary, rolling update.
2. **Deployment steps**: Build, test, stage, deploy, verify sequence.
3. **Rollback mechanism**: How to revert to the previous version.
4. **Environment progression**: Which environments exist and in what order deployments flow (dev, staging, production).
5. **Approval gates**: Manual approvals required before production deployment.
6. **Feature flags**: Feature flag system configuration if present.

Use `docker` to check for running containers and their current image versions, which provides context for rollback targets.

Document the current deployment pipeline as a numbered procedure.

## Step 4: Analyze Log Patterns

Use `log` tools if available, or `data_file_read` to examine log configuration files.

Identify:

- **Log locations**: Where logs are stored (files, stdout, centralized logging service).
- **Log format**: Structured JSON, plain text, syslog format.
- **Log levels**: What constitutes ERROR, WARN, INFO in the application.
- **Key log messages**: Error messages associated with common failure modes. Use `filesystem` to search for error message strings in the codebase.
- **Log search procedures**: How to query logs (Kibana, CloudWatch Logs Insights, Grafana Loki, journalctl).

Build a reference table of common log patterns and their meaning:

| Log Pattern | Meaning | Likely Cause | Severity |
|------------|---------|-------------|----------|
| `connection refused` | Dependency unreachable | Service down or network issue | High |
| `out of memory` | Process killed by OOM | Memory leak or insufficient limits | Critical |
| `timeout exceeded` | Request timed out | Slow dependency or deadlock | Medium |
| `authentication failed` | Auth rejection | Expired credentials or misconfiguration | Medium |
| `disk full` | Write failures | Insufficient storage or log rotation failure | Critical |
| `rate limit exceeded` | Throttled by dependency | Traffic spike or misconfigured limits | Low |

## Step 5: Generate Alert Response Runbooks

For each alert identified in Step 2, generate a response runbook.

Each alert runbook follows this structure:

```markdown
## Alert: <Alert Name>

**Severity**: <Critical/Warning/Info>
**Service**: <affected service>
**On-Call Response Time**: <expected response SLA>

### Description
<What this alert means in plain language>

### Impact
<What users or systems are affected when this alert fires>

### Diagnostic Steps

1. Check the alert details in the monitoring dashboard.
   - Dashboard URL: <link or placeholder>
   - Relevant panel: <panel name>

2. Verify the service is running.
   - Command: <specific command to check service status>
   - Expected output: <what healthy looks like>

3. Check recent logs for errors.
   - Command: <log query command>
   - Look for: <specific patterns>

4. Check dependent services.
   - <list of dependencies and how to verify each>

### Resolution Steps

#### If caused by <cause A>:
1. <Step 1>
2. <Step 2>
3. Verify resolution: <verification command>

#### If caused by <cause B>:
1. <Step 1>
2. <Step 2>
3. Verify resolution: <verification command>

### Escalation
- If unresolved after 15 minutes: Escalate to <team/person>
- If data loss suspected: Notify <stakeholder>

### Prevention
- <What can be done to prevent this alert from firing>
```

Generate runbooks for at least these common scenarios:

1. **Service health check failure**: The application is not responding.
2. **High error rate**: HTTP 5xx errors exceed threshold.
3. **High latency**: Response times exceed SLA.
4. **Resource exhaustion**: CPU, memory, or disk nearing capacity.
5. **Database connectivity**: Cannot connect to the primary database.
6. **Queue backlog**: Message queue depth growing beyond normal.
7. **Certificate expiration**: TLS certificates approaching expiration.

## Step 6: Generate Deployment Runbook

Create a step-by-step deployment procedure covering:

1. **Pre-deployment checklist**: Tests passing, change reviewed, monitoring dashboards open, rollback procedure reviewed, stakeholder communication.
2. **Standard deployment sequence**: Verify build artifact, deploy to staging, run smoke tests, monitor staging for 15 minutes, deploy to production, monitor production for 30 minutes.
3. **Rollback procedure**: Identify last known good version, execute rollback command, verify rollback, notify team and create incident ticket.

Populate all commands from the actual deployment scripts and CI/CD configuration found in Step 3. Use placeholders only where project-specific values cannot be determined.

## Step 7: Generate Scaling Runbook

Document procedures for horizontal scaling (adding/removing replicas via Kubernetes, ECS, or Auto Scaling), vertical scaling (changing instance types or resource limits, noting restart requirements), database scaling (read replicas, connection pools, storage expansion), and cache scaling (adding nodes, adjusting memory). Include guidance on when to scale, how to determine target size, cost implications, and how to scale back down.

## Step 8: Generate Maintenance Runbooks

Document routine maintenance procedures using `markdown`: database maintenance (vacuum, reindex, backup verification), certificate rotation, secret rotation, dependency updates, log rotation and cleanup, and backup verification. For each task, include frequency, maintenance window requirements, user impact, and verification steps.

## Step 9: Assemble the Complete Runbook

Use `filesystem` to write the runbook document and `markdown` for formatting.

Structure:

```
# Operations Runbook

**Service**: <name>
**Last Updated**: <date>
**Maintainer**: <team or individual>

## Table of Contents

## 1. Service Overview
<brief description of the service, its purpose, and architecture>

### Architecture Diagram
<text-based architecture description or reference to diagram>

### Key Endpoints
| Endpoint | Purpose | Health Check |
|----------|---------|-------------|
| <URL> | <purpose> | <health URL> |

### Dependencies
| Dependency | Type | Criticality | Health Check |
|-----------|------|-------------|-------------|
| PostgreSQL | Database | Hard | pg_isready |
| Redis | Cache | Soft | redis-cli ping |

## 2. Monitoring and Alerts
<alert reference table from Step 2>

## 3. Alert Response Procedures
<individual alert runbooks from Step 5>

## 4. Deployment
<deployment runbook from Step 6>

## 5. Scaling
<scaling runbook from Step 7>

## 6. Maintenance
<maintenance procedures from Step 8>

## 7. Troubleshooting Guide
<common issues and diagnostic procedures>

## 8. Contact and Escalation
<on-call schedule, escalation paths, stakeholder contacts>

## Appendix: Useful Commands
<quick reference of frequently used commands>
```

## Step 10: Review and Deliver

Before presenting the runbook, validate its quality.

Check:

1. **All commands are specific**: No generic placeholders where actual commands can be determined from configuration files.
2. **Procedures are testable**: Each procedure can be followed by an engineer who has not seen it before.
3. **Escalation paths are defined**: Every procedure has clear guidance on when and how to escalate.
4. **Links and references are valid**: Dashboard links, documentation links, and file references point to real locations.
5. **No sensitive data**: The runbook does not contain actual passwords, tokens, or connection strings. Use references to secret stores instead.

Present a summary of the generated runbook sections and their coverage. Note any operational areas that could not be covered due to missing configuration or documentation.

## Edge Cases

- **No monitoring configured**: If no monitoring rules are found, generate runbooks based on common failure modes for the detected technology stack and recommend setting up monitoring as a priority.
- **Serverless architectures**: Runbooks for serverless focus on function errors, cold starts, throttling, and service quotas rather than instance-level operations.
- **Multi-service systems**: Generate a top-level runbook that covers system-wide procedures (full outage response, disaster recovery) and per-service runbooks for service-specific operations.
- **Legacy systems**: Older systems may lack IaC or modern CI/CD. Document what exists and note manual procedures that should be automated.
- **Highly regulated environments**: For healthcare, finance, or government systems, include compliance-specific procedures (audit trail verification, data integrity checks) in the maintenance section.
- **On-premise vs cloud**: Adjust procedures based on whether the infrastructure is cloud-managed (AWS, GCP) or self-hosted. On-premise systems require hardware-level procedures that cloud systems abstract away.

## Related Skills

- **e-monitor** (eskill-devops): Run e-monitor before this skill to reference configured alerts and dashboards in the runbook.
- **e-recover** (eskill-devops): Run e-recover alongside this skill to align runbook procedures with the recovery plan.
