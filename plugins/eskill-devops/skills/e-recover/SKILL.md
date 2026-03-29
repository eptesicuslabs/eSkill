---
name: e-recover
description: "Generates disaster recovery documentation by inventorying data stores, services, and backup configurations. Use when documenting DR plans, auditing recovery readiness, or preparing for compliance. Also applies when: 'create DR plan', 'disaster recovery documentation', 'RTO RPO requirements', 'backup strategy review'."
---

# Disaster Recovery Plan Generator

This skill produces disaster recovery documentation by inventorying the project's data stores, services, infrastructure dependencies, and backup configurations. It calculates recovery metrics, identifies gaps, and outputs a structured DR plan document suitable for compliance reviews and operational use.

## Prerequisites

Confirm the project scope with the user. Determine whether the DR plan covers a single application, a set of microservices, or an entire platform. Identify any existing DR documentation that should be incorporated or superseded.

## Step 1: Inventory Infrastructure Components

Use `filesystem` to scan for infrastructure configuration files and `data_file_read` to parse them.

Search for and read:

- `docker-compose.yml` / `docker-compose.*.yml`: Identifies services, databases, caches, and message brokers.
- `terraform/*.tf`: Identifies cloud resources, regions, and availability zones.
- `kubernetes/*.yaml` or `k8s/*.yaml`: Identifies deployed services and their dependencies.
- `serverless.yml` / `sam-template.yaml`: Identifies serverless functions and event sources.
- `ansible/`, `puppet/`, `chef/` directories: Identifies configuration management.
- `Makefile`, `Taskfile.yml`: May reference infrastructure provisioning commands.

For each component discovered, record:

| Field | Description |
|-------|-------------|
| Name | Service or resource identifier |
| Type | Database, cache, queue, storage, compute, network |
| Provider | AWS, GCP, Azure, self-hosted, or local |
| Region | Deployment region if applicable |
| Redundancy | Single instance, replicated, multi-AZ, multi-region |
| Data persistence | Ephemeral, persistent, backed-up |

## Step 2: Classify Data Stores

Use `data_file_read` to examine database connection strings, ORM configurations, and storage references in application code and configuration.

For each data store, document:

1. **Store type**: Relational (PostgreSQL, MySQL, SQLite), NoSQL (MongoDB, DynamoDB, Redis), object storage (S3, GCS, MinIO), file system.
2. **Data classification**:
   - Critical: Data that cannot be regenerated (user data, financial records, audit logs).
   - Important: Data that is expensive to regenerate (analytics, ML models, processed results).
   - Replaceable: Data that can be regenerated from source (caches, search indexes, build artifacts).
3. **Estimated data volume**: Infer from schema complexity, migration history, and any documented sizing.
4. **Growth rate**: Estimate based on data type (transactional data grows continuously; configuration data is relatively static).
5. **Consistency requirements**: Strong consistency (financial), eventual consistency (analytics), or best-effort (caches).

Use `shell` to check for database migration files (count of migrations indicates schema evolution history).

## Step 3: Audit Existing Backup Configuration

Search for backup-related configuration in the infrastructure files.

Check for:

- **Automated backups**: RDS automated backups, Cloud SQL backups, mongodump cron jobs, pg_dump scripts.
- **Backup retention**: How long backups are kept. Read retention policies from Terraform resource configurations or backup scripts.
- **Backup destination**: Where backups are stored. Cross-region or cross-account storage provides better protection.
- **Backup encryption**: Whether backups are encrypted at rest and in transit.
- **Backup testing**: Evidence of backup restoration testing (scripts, runbooks, or CI jobs that verify backups).

Use `docker` to check if any containers are running backup agents or scheduled backup tasks.

| Backup Aspect | Good | Acceptable | Concerning |
|--------------|------|------------|------------|
| Frequency | Continuous / hourly | Daily | Weekly or manual |
| Retention | 30+ days | 7-30 days | Less than 7 days |
| Location | Cross-region + cross-account | Cross-region | Same region only |
| Encryption | Encrypted at rest and in transit | Encrypted at rest | Unencrypted |
| Tested | Regular automated restore tests | Occasional manual tests | Never tested |

## Step 4: Map Service Dependencies

Build a dependency graph of all services to understand failure propagation.

- Read `docker-compose.yml` `depends_on` directives.
- Read Kubernetes service references and DNS names in configuration.
- Search application code for connection strings, base URLs, and service client initialization.
- Identify external dependencies: third-party APIs, SaaS services, DNS providers, CDNs, payment processors.

For each dependency, classify:

- **Hard dependency**: Service cannot function without it. Failure causes complete outage.
- **Soft dependency**: Service degrades but continues operating. Failure causes partial outage or reduced functionality.
- **Async dependency**: Service operates independently. Failure causes delayed processing but no user-facing impact.

Record the dependency graph in a format suitable for the DR plan document.

## Step 5: Define Recovery Objectives

Based on the data classification and service dependencies, propose RTO and RPO targets.

| Tier | RTO (Recovery Time Objective) | RPO (Recovery Point Objective) | Applies To |
|------|------------------------------|-------------------------------|------------|
| Tier 1 - Critical | Less than 1 hour | Less than 15 minutes | Core user-facing services, primary database |
| Tier 2 - Important | Less than 4 hours | Less than 1 hour | Internal tools, analytics, secondary services |
| Tier 3 - Standard | Less than 24 hours | Less than 24 hours | Development environments, non-critical batch jobs |
| Tier 4 - Low | Less than 72 hours | Best effort | Archives, historical reports, documentation sites |

Map each inventoried component to a tier. Present the proposed mapping to the user for validation, as business context may require different classifications than technical analysis alone suggests.

## Step 6: Identify Recovery Strategies

For each tier, define the recovery strategy.

**Tier 1 - Active/Active or Hot Standby**:
- Multi-AZ or multi-region deployment with automatic failover.
- Database replication with synchronous or semi-synchronous writes.
- DNS-based failover or global load balancing.
- Estimated recovery: automatic, under 5 minutes for infrastructure-level failures.

**Tier 2 - Warm Standby**:
- Scaled-down replica of the production environment in a secondary region.
- Asynchronous database replication.
- Manual or semi-automated failover procedure.
- Estimated recovery: 30-60 minutes including validation.

**Tier 3 - Pilot Light**:
- Minimal infrastructure pre-provisioned in a secondary region.
- Database backups restored on demand.
- Infrastructure provisioned via IaC (Terraform, CloudFormation) during recovery.
- Estimated recovery: 4-8 hours.

**Tier 4 - Backup and Restore**:
- Recovery from backups stored in a durable location.
- Infrastructure provisioned from scratch using IaC.
- Estimated recovery: 24-48 hours.

Check the existing infrastructure against these strategies to identify which strategy the current setup supports versus which it aspires to.

## Step 7: Document Recovery Procedures

For each critical and important service, generate a step-by-step recovery procedure.

Use `markdown` to format each procedure with:

1. **Trigger conditions**: What events indicate this procedure should be executed.
2. **Prerequisites**: Access credentials, tools, network connectivity required.
3. **Steps**: Numbered, actionable steps with specific commands where applicable. Reference actual infrastructure file paths and resource names from the inventory.
4. **Verification**: How to confirm the recovery was successful.
5. **Rollback**: How to revert if the recovery introduces new problems.
6. **Estimated duration**: Time estimate for each step and total procedure duration.
7. **Responsible team**: Which team or role executes this procedure.

Generate procedures for these common scenarios:

- Database failure and restoration from backup.
- Complete region failure and failover to secondary region.
- Accidental data deletion and point-in-time recovery.
- DNS failure and alternative access methods.
- Container orchestration failure and service restart.
- Secret or certificate expiration and rotation.

## Step 8: Identify Gaps and Risks

Compare the current state (from Steps 1-4) against the recovery objectives (Step 5) and strategies (Step 6).

Document each gap:

| Gap | Current State | Required State | Risk Level | Remediation |
|-----|--------------|----------------|------------|-------------|
| Single-region database | One region, no replication | Multi-AZ with read replica | High | Enable RDS Multi-AZ |
| No backup testing | Backups exist but untested | Monthly restore verification | Medium | Schedule restore tests |
| Manual failover only | No automation | Automated health checks and failover | High | Implement Route53 health checks |

For each gap, estimate:
- The probability of the failure scenario occurring.
- The business impact if recovery fails or exceeds the RTO.
- The effort and cost to remediate.

## Step 9: Generate Communication Plan

Document the communication procedures during a disaster recovery event.

Include:

1. **Escalation matrix**: Who to contact at each severity level. Use placeholder names and roles for the user to fill in.
2. **Notification channels**: Primary and backup communication methods (Slack, PagerDuty, email, phone tree).
3. **Status page updates**: How and when to update the public status page.
4. **Customer communication templates**: Pre-drafted messages for common scenarios:
   - Service degradation notice.
   - Full outage acknowledgment.
   - Recovery progress update.
   - Resolution confirmation with post-incident details.
5. **Post-incident review**: Timeline for conducting the post-mortem and distributing findings.

## Step 10: Assemble the DR Plan Document

Use `filesystem` to write the complete DR plan to a file and `markdown` for formatting.

Structure the document as follows:

```
# Disaster Recovery Plan

**Project**: <name>
**Version**: <version>
**Last Updated**: <date>
**Review Cadence**: Quarterly
**Next Review**: <date + 3 months>

## Table of Contents

## 1. Executive Summary
<one paragraph overview of the DR strategy>

## 2. Infrastructure Inventory
<tables from Step 1>

## 3. Data Stores and Classification
<tables from Step 2>

## 4. Backup Configuration
<audit results from Step 3>

## 5. Service Dependency Map
<dependency graph from Step 4>

## 6. Recovery Objectives (RTO/RPO)
<tier assignments from Step 5>

## 7. Recovery Strategies
<strategies from Step 6>

## 8. Recovery Procedures
<step-by-step procedures from Step 7>

## 9. Gaps and Remediation Plan
<gap analysis from Step 8>

## 10. Communication Plan
<communication procedures from Step 9>

## Appendix A: Contact Directory
<placeholder for team contact information>

## Appendix B: Credential Access
<instructions for accessing recovery credentials>

## Appendix C: Testing Schedule
<schedule for DR drills and backup verification>
```

After writing the file, present a summary of the key findings to the user: the number of components inventoried, the most significant gaps identified, and the recommended priority for remediation.

## Edge Cases

- **Serverless architectures**: DR for serverless is primarily about data stores and configuration, since compute is managed by the cloud provider. Focus the plan on database recovery, API Gateway configuration, and IAM policies.
- **Hybrid environments**: If the project spans on-premises and cloud infrastructure, document the network connectivity requirements for DR and any VPN or Direct Connect dependencies.
- **Multi-tenant systems**: DR procedures may need to account for tenant isolation during recovery. Document whether tenants can be recovered independently or only as a complete system.
- **Compliance-driven DR**: For SOC2, HIPAA, or PCI-DSS environments, note which DR plan sections map to specific compliance requirements and controls.
- **No infrastructure files**: If the project has no IaC or Docker configuration, the inventory must be built from application configuration files and user interviews. Note this limitation in the plan.
- **Cost constraints**: Some recovery strategies (multi-region active/active) are expensive. Include cost estimates where possible so the user can make informed trade-offs between resilience and budget.

## Related Skills

- **e-backup** (eskill-system): Run e-backup before this skill to establish the backup procedures referenced in the recovery plan.
- **e-monitor** (eskill-devops): Run e-monitor before this skill to ensure alerting is in place for disaster detection.
