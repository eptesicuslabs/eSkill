---
name: compliance-checklist
description: "Evaluates project against SOC2, GDPR, HIPAA, or PCI-DSS compliance checklists by checking code and configs. Use for audit preparation, regulatory reviews, or assessing data handling. Also applies when: 'compliance check', 'are we SOC2 ready', 'GDPR audit', 'HIPAA requirements', 'regulatory checklist'."
---

# Compliance Checklist

This skill evaluates a project against regulatory compliance frameworks by inspecting code patterns, configurations, access controls, logging practices, and data handling. It produces a checklist report with pass/fail/partial status for each control, evidence references, and remediation guidance.

## Prerequisites

Confirm which compliance framework(s) to evaluate against. Supported frameworks:

| Framework | Focus Area | Common Industries |
|-----------|-----------|-------------------|
| SOC2 Type II | Security, Availability, Confidentiality, Processing Integrity, Privacy | SaaS, cloud services |
| GDPR | Data protection, privacy rights, consent management | Any handling EU resident data |
| HIPAA | Protected health information (PHI) safeguards | Healthcare, health tech |
| PCI-DSS v4.0 | Cardholder data protection | Payment processing, e-commerce |

Multiple frameworks can be evaluated simultaneously. The checklist will note overlapping controls.

## Step 1: Inventory Data Handling Patterns

Use `ast_search` to find code patterns related to data collection, storage, and processing.

Search for:

1. **User data collection**: Form handlers, API endpoints accepting user input, webhook receivers. Look for route definitions that accept POST/PUT/PATCH requests.
2. **Data storage**: Database write operations (INSERT, UPDATE, CREATE), file writes, cache sets. Use `lsp_symbols` to find repository/DAO classes and their methods.
3. **Data transmission**: HTTP client calls sending data externally, email sending, webhook dispatching, message queue publishing.
4. **Data logging**: Logging statements that may include PII. Search for log calls that interpolate request bodies, user objects, or error details containing user data.
5. **Data deletion**: DELETE operations, soft delete patterns, data retention cleanup jobs.

For each pattern found, record the file path, function name, and the type of data involved (PII, PHI, financial, authentication).

Use `filesystem` to check for data flow documentation if it exists (data flow diagrams, privacy impact assessments, data processing records).

## Step 2: Evaluate Authentication and Access Controls

Use `ast_search` and `lsp_symbols` to examine authentication implementation.

Check for:

| Control | What to Look For | Evidence |
|---------|-----------------|----------|
| Authentication mechanism | OAuth2, SAML, JWT, session-based auth | Auth middleware, identity provider config |
| Password policy | Minimum length, complexity, hashing algorithm | Validation rules, bcrypt/argon2 usage |
| Multi-factor authentication | MFA enrollment, TOTP/WebAuthn support | MFA middleware, enrollment endpoints |
| Session management | Session timeout, secure cookie flags, token rotation | Cookie configuration, session store setup |
| Role-based access | RBAC or ABAC implementation, permission checks | Authorization middleware, role definitions |
| API authentication | API key validation, OAuth scopes, rate limiting | API middleware chain, scope definitions |
| Account lockout | Failed login tracking, lockout threshold | Login attempt counting, lockout logic |

For each control, record whether it is:
- **Pass**: Implemented and configured according to framework requirements.
- **Partial**: Implemented but with gaps (e.g., password hashing exists but no minimum length enforcement).
- **Fail**: Not implemented or misconfigured.
- **N/A**: Not applicable to this project type.

## Step 3: Audit Encryption Practices

Use `ast_search` and `data_file_read` to check encryption at rest and in transit.

**Encryption in transit**:
- TLS configuration: Check for HTTPS enforcement, TLS version constraints, certificate configuration.
- Internal service communication: Check whether inter-service calls use TLS or mTLS.
- Database connections: Check connection strings for SSL/TLS parameters.
- Examine middleware for HSTS headers, secure redirect rules.

**Encryption at rest**:
- Database encryption: Check IaC configurations for encryption settings on RDS, DynamoDB, etc.
- File storage encryption: Check S3 bucket policies, Azure Blob encryption settings.
- Local file encryption: Check whether sensitive files (configuration, credentials) are encrypted.
- Backup encryption: Check backup configurations for encryption settings.

**Cryptographic practices**:
- Hashing algorithms: Verify password hashing uses bcrypt, argon2, or scrypt (not MD5, SHA1, or SHA256 alone).
- Encryption algorithms: Verify AES-256 or equivalent for data encryption. Flag ECB mode or weak algorithms.
- Key management: Check for hardcoded encryption keys versus KMS or vault integration.
- Random number generation: Verify cryptographically secure random number generators for security contexts.

## Step 4: Review Logging and Monitoring

Use `ast_search` to analyze logging practices and `data_file_read` to check monitoring configuration.

**Logging coverage**:
- Authentication events: Login success/failure, logout, MFA challenges.
- Authorization events: Access denied, privilege escalation attempts.
- Data access: Read/write operations on sensitive data.
- Administrative actions: User creation, role changes, configuration modifications.
- System events: Application start/stop, error conditions, dependency failures.

**Log security**:
- PII in logs: Search for logging statements that may include passwords, tokens, SSNs, credit card numbers, or health data. Use regex patterns to detect sensitive data in log format strings.
- Log integrity: Check for tamper-evident logging (centralized log service, write-once storage).
- Log retention: Check log rotation configuration and retention policies.
- Log access: Check who can access logs and whether access is audited.

**Monitoring and alerting**:
- Check for monitoring tool integration (Prometheus, Datadog, CloudWatch, New Relic).
- Check for alert definitions on security-relevant events.
- Check for uptime monitoring and health check endpoints.

## Step 5: Check Data Privacy Controls (GDPR/HIPAA Specific)

If evaluating GDPR or HIPAA, perform additional data privacy checks.

**GDPR-specific**:

| Article | Control | Check |
|---------|---------|-------|
| Art. 6 | Lawful basis for processing | Consent collection mechanism, legitimate interest documentation |
| Art. 7 | Consent conditions | Consent recording, withdrawal mechanism |
| Art. 13-14 | Privacy notice | Privacy policy page, data collection disclosure |
| Art. 15 | Right of access | Data export endpoint or process |
| Art. 17 | Right to erasure | Data deletion endpoint or process |
| Art. 20 | Data portability | Machine-readable data export (JSON, CSV) |
| Art. 25 | Privacy by design | Data minimization in schemas, purpose limitation |
| Art. 30 | Records of processing | Processing activity documentation |
| Art. 32 | Security of processing | Encryption, pseudonymization, resilience measures |
| Art. 33-34 | Breach notification | Incident response procedure, notification mechanism |

**HIPAA-specific**:

| Rule | Control | Check |
|------|---------|-------|
| Privacy Rule | PHI identification | Data classification, minimum necessary access |
| Security Rule - Administrative | Risk assessment | Security risk analysis documentation |
| Security Rule - Physical | Workstation security | Not code-checkable; note for manual review |
| Security Rule - Technical | Access control | User authentication, audit controls, integrity checks |
| Breach Notification | Breach procedures | Incident response plan, notification templates |
| BAA | Business associates | Third-party service agreements |

Use `filesystem` to search for privacy policies, DPA templates, BAA templates, and incident response plans in the repository.

## Step 6: Evaluate Infrastructure Security (SOC2/PCI-DSS Focus)

Use `data_file_read` to check IaC configurations and `shell` to verify runtime security settings.

**Network security**:
- Firewall rules / Security groups: Check for least-privilege network access.
- VPC configuration: Check for network segmentation.
- Public exposure: Identify resources directly accessible from the internet.
- WAF configuration: Check for web application firewall rules.

**Vulnerability management**:
- Dependency scanning: Check for automated dependency vulnerability scanning in CI.
- Container scanning: Check for image vulnerability scanning in Docker builds.
- SAST/DAST: Check for static and dynamic application security testing.
- Patch management: Check for automated dependency update tooling (Dependabot, Renovate).

**PCI-DSS specific**:

| Requirement | Control | Check |
|------------|---------|-------|
| Req 1 | Network segmentation | Firewall rules, VPC isolation |
| Req 2 | Secure defaults | No default passwords, hardened configurations |
| Req 3 | Protect stored data | Encryption of cardholder data, no PAN in logs |
| Req 4 | Encrypt transmission | TLS for all cardholder data transmission |
| Req 6 | Secure development | Secure SDLC practices, code review process |
| Req 7 | Restrict access | Role-based access to cardholder data |
| Req 8 | Identify users | Unique user IDs, MFA for admin access |
| Req 10 | Track access | Audit logging for cardholder data access |
| Req 11 | Test security | Vulnerability scanning, penetration testing |
| Req 12 | Security policy | Information security policy documentation |

## Step 7: Check CI/CD Security Controls

Use `data_file_read` to read CI/CD configuration files.

Search for `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`, `azure-pipelines.yml`, `bitbucket-pipelines.yml`.

Evaluate:

- **Secret management**: Secrets referenced via environment variables or secret store, not hardcoded in pipeline files.
- **Pipeline permissions**: Least-privilege service account for CI/CD.
- **Artifact signing**: Build artifacts signed for integrity verification.
- **Dependency verification**: Lock file integrity checked during builds.
- **Branch protection**: Required reviews, status checks, and signed commits for protected branches.
- **Deployment approval**: Manual approval gates for production deployments.

## Step 8: Assess Incident Response Readiness

Use `filesystem` to search for incident response documentation.

Check for:

- Incident response plan document.
- On-call rotation configuration (PagerDuty, OpsGenie configs).
- Runbook directory with operational procedures.
- Status page configuration.
- Communication templates for stakeholder notification.
- Post-incident review templates and historical post-mortems.

Score readiness:
- **Mature**: Documented plan, defined roles, regular drills, historical post-mortems.
- **Developing**: Plan exists but incomplete, roles partially defined.
- **Initial**: No formal plan, ad-hoc incident handling.
- **None**: No incident response artifacts found.

## Step 9: Generate Compliance Report

Assemble findings into a structured checklist report.

```
## Compliance Evaluation Report

**Project**: <name>
**Framework(s)**: <SOC2 / GDPR / HIPAA / PCI-DSS>
**Date**: <YYYY-MM-DD>
**Evaluator**: eSkill Automated Assessment

### Executive Summary

| Status | Count | Percentage |
|--------|-------|------------|
| Pass | <N> | <X%> |
| Partial | <N> | <X%> |
| Fail | <N> | <X%> |
| N/A | <N> | <X%> |

**Overall Readiness**: <Ready / Needs Work / Significant Gaps>

### Control Checklist

| ID | Control | Status | Evidence | Remediation |
|----|---------|--------|----------|-------------|
| AC-01 | Authentication mechanism | Pass | auth/middleware.ts | - |
| AC-02 | Password hashing | Partial | Missing min length | Add validation |
| ... | ... | ... | ... | ... |

### Priority Remediation Items

1. [Critical] <description>
2. [High] <description>
3. [Medium] <description>
```

Group controls by category (Access Control, Encryption, Logging, Privacy, Infrastructure, Incident Response).

## Step 10: Provide Remediation Roadmap

For each failing or partial control, provide specific remediation guidance.

Structure remediation items by priority:

1. **Critical** (address before any audit): Active security vulnerabilities, missing encryption, exposed secrets.
2. **High** (address within 30 days): Missing logging, incomplete access controls, undocumented data flows.
3. **Medium** (address within 90 days): Partial implementations, documentation gaps, process improvements.
4. **Low** (improvement items): Best practice enhancements, tooling upgrades, automation opportunities.

For each item, include:
- The specific control that failed.
- What needs to change (code, configuration, documentation, or process).
- Example implementation or reference to standards documentation.
- Estimated effort (hours/days).

## Edge Cases

- **Early-stage projects**: Many compliance controls involve organizational processes (security training, vendor management) that cannot be verified from code alone. Note these as requiring manual verification and provide templates where possible.
- **Third-party managed services**: If the application relies on managed services (Auth0, Stripe, AWS RDS), note that some controls are the responsibility of the service provider. Reference the provider's compliance certifications (SOC2 reports, PCI-DSS attestations).
- **Multiple compliance frameworks**: When evaluating against multiple frameworks simultaneously, map overlapping controls to avoid duplicate findings. Present a unified view with framework-specific annotations.
- **Microservices**: Each service may have different compliance requirements. Evaluate the most critical service first and note shared infrastructure controls that apply across services.
- **No IaC**: If infrastructure is managed manually (console-provisioned), note that infrastructure controls cannot be verified from the repository and require manual audit.

## Related Skills

- **security-scan** (eskill-quality): Run security-scan before this skill to generate the vulnerability findings referenced in compliance checks.
- **sbom-generator** (eskill-quality): Run sbom-generator before this skill to provide the software inventory required by compliance frameworks.
- **configuration-audit** (eskill-quality): Run configuration-audit alongside this skill to verify that system configurations meet compliance requirements.
