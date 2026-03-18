---
name: infrastructure-review
description: "Reviews infrastructure-as-code files for best practices, security issues, and potential misconfigurations. Supports Terraform, Docker Compose, Kubernetes manifests, and CloudFormation. Use when auditing infrastructure configurations, reviewing IaC changes, or establishing infrastructure standards."
---

# Infrastructure Review

This skill performs a structured review of infrastructure-as-code (IaC) files, checking for security issues, misconfigurations, missing best practices, and inconsistencies across environments. It produces a categorized report with findings ranked by severity and actionable remediation recommendations.

## Step 1: Identify IaC Files

Search the project for all infrastructure-as-code files using filesystem search operations.

- Search for `*.tf` and `*.tfvars` files to locate Terraform configurations.
- Search for `docker-compose*.yml` and `docker-compose*.yaml` files.
- Search for Kubernetes manifests: files in `k8s/`, `kubernetes/`, `manifests/`, `deploy/` directories with `.yml` or `.yaml` extensions. Also search for files matching common patterns like `*-deployment.yaml`, `*-service.yaml`, `*-ingress.yaml`.
- Search for CloudFormation templates: files matching `cloudformation*.json`, `cloudformation*.yaml`, `template*.json`, `template*.yaml`, or files in a `cfn/` directory.
- Search for Helm charts: look for `Chart.yaml` files and associated `values.yaml` and templates in `templates/` directories.
- Search for Ansible playbooks: look for `playbook*.yml`, `site.yml`, and `roles/` directories.

Log each discovered file with its type classification. If no IaC files are found, inform the user and suggest common locations where these files are typically placed.

## Step 2: Read IaC Files

Read the content of each identified IaC file using `read_text` from the filesystem tool.

- Read files in order of type: Terraform first, then Docker Compose, then Kubernetes, then CloudFormation.
- For large files (over 500 lines), note the file size and read in sections if necessary.
- Parse the file structure to identify individual resource definitions, service definitions, or configuration blocks.
- Build an inventory of all defined resources, services, and components for cross-referencing in later steps.

## Step 3: Docker Compose Review

For each Docker Compose file, check the following items.

### Image Version Pinning
- CRITICAL: Check that every `image:` directive uses a specific tag, not `:latest` or no tag at all.
- Prefer digest-pinned images (`image: nginx@sha256:...`) for production configurations.
- Flag any image references that use `:latest` or omit the tag entirely.

### Health Checks
- WARNING: Check that every service defines a `healthcheck` with `test`, `interval`, `timeout`, and `retries`.
- Services without health checks cannot be reliably monitored or restarted by the container runtime.

### Resource Limits
- WARNING: Check that services define `deploy.resources.limits` for both `cpus` and `memory`.
- Without resource limits, a single container can starve others of resources.

### Restart Policies
- SUGGESTION: Check that services define a `restart` policy (`always`, `unless-stopped`, or `on-failure`).
- Production services should always have a restart policy to recover from crashes.

### Network Isolation
- SUGGESTION: Check that services use named networks rather than the default bridge network.
- Services that do not need to communicate with each other should be on separate networks.

### Secrets Management
- CRITICAL: Check that no service passes secrets through `environment` variables with inline values.
- Secrets should use Docker secrets, external files referenced via `env_file`, or a secrets manager.

### Volume Configuration
- WARNING: Check that named volumes are used for persistent data rather than bind mounts.
- Verify that read-only mounts (`ro`) are used where the container does not need write access.

## Step 4: Terraform Review

For each Terraform configuration, check the following items.

### State Backend Configuration
- CRITICAL: Check that a remote backend is configured (S3, GCS, Azure Blob, Terraform Cloud).
- Local state files are a serious risk for team environments and should never be used in shared projects.
- Verify that state locking is enabled (DynamoDB table for S3, built-in for GCS/Azure).

### Provider Version Pinning
- WARNING: Check that all `provider` blocks include a `version` constraint or that a `required_providers` block exists with version constraints.
- Use pessimistic version constraints (e.g., `~> 5.0`) to prevent unexpected breaking changes.

### Variable Validation
- SUGGESTION: Check that `variable` blocks include `description`, `type`, and `validation` blocks where appropriate.
- Variables without descriptions make the configuration harder to understand and maintain.

### Output Documentation
- SUGGESTION: Check that `output` blocks include `description` fields.
- Outputs should clearly document what value they expose and why it is needed.

### Sensitive Data Handling
- CRITICAL: Check that variables containing secrets are marked with `sensitive = true`.
- Check that no `.tfvars` files contain plaintext secrets.
- Verify that `.tfvars` files with secrets are listed in `.gitignore`.

### Resource Naming
- SUGGESTION: Check for consistent resource naming conventions across all `.tf` files.
- Resource names should follow a clear pattern (e.g., `{project}-{environment}-{resource_type}`).

### Module Usage
- SUGGESTION: Check that repeated resource patterns are extracted into modules.
- Modules should be versioned when sourced from registries.

## Step 5: Kubernetes Review

For each Kubernetes manifest, check the following items.

### Resource Limits and Requests
- CRITICAL: Check that every container in every Pod spec defines `resources.requests` and `resources.limits` for both `cpu` and `memory`.
- Without resource requests, the scheduler cannot make informed placement decisions.
- Without resource limits, a pod can consume unbounded resources on a node.

### Liveness and Readiness Probes
- WARNING: Check that every container defines both `livenessProbe` and `readinessProbe`.
- Liveness probes detect deadlocks and trigger restarts. Readiness probes prevent traffic from reaching unready pods.
- Verify that probe configurations include appropriate `initialDelaySeconds`, `periodSeconds`, and `failureThreshold` values.

### Security Context
- CRITICAL: Check that pods and containers define a `securityContext`.
- Containers should run as non-root (`runAsNonRoot: true`).
- Containers should drop all capabilities and add only those needed (`capabilities: { drop: ["ALL"] }`).
- File systems should be read-only where possible (`readOnlyRootFilesystem: true`).

### Image Tag Pinning
- CRITICAL: Check that no container image uses the `:latest` tag.
- All images should use a specific version tag or digest.
- Flag any image references that use `:latest` or omit the tag.

### Namespace Isolation
- WARNING: Check that resources define an explicit `namespace` rather than relying on the default namespace.
- Workloads in the `default` namespace indicate missing organizational structure.

### Network Policies
- SUGGESTION: Check for the presence of `NetworkPolicy` resources that restrict pod-to-pod communication.
- Without network policies, all pods can communicate with all other pods in the cluster.

### Pod Disruption Budgets
- SUGGESTION: Check for `PodDisruptionBudget` resources for critical deployments.
- PDBs ensure that voluntary disruptions (upgrades, scaling) do not take down too many pods simultaneously.

### Service Account Configuration
- WARNING: Check that pods do not use the default service account.
- Check that `automountServiceAccountToken: false` is set where the service account token is not needed.

## Step 6: Check for Hardcoded Secrets

Across all IaC files, search for patterns that indicate hardcoded secrets or credentials.

- Search for string patterns that look like API keys, tokens, passwords, or connection strings.
- Common patterns to check: `password:`, `secret:`, `api_key:`, `token:`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, base64-encoded strings that decode to credential-like values.
- Check environment variable definitions for inline secret values rather than references to secret stores.
- Check for TLS certificates or private keys embedded directly in configuration files.
- Any finding in this category is automatically CRITICAL severity.

Report each finding with the exact file path and line range, and recommend the appropriate secrets management approach for the platform (Kubernetes Secrets with encryption at rest, AWS Secrets Manager, HashiCorp Vault, etc.).

## Step 7: Cross-Reference with Project Requirements

Check whether the infrastructure configuration aligns with the project's documented requirements.

- Search for architecture documentation (docs/architecture.md, ARCHITECTURE.md, docs/infrastructure.md).
- If documentation exists, read it and compare the described components against the actual IaC definitions.
- Flag any documented components that are missing from the IaC.
- Flag any IaC resources that are not documented.
- Check that scaling parameters (replica counts, instance sizes) match documented capacity requirements.

## Step 8: Compare Across Environments

If the project has configurations for multiple environments (dev, staging, production), compare them for consistency.

- Use `diff_files` to compare environment-specific configurations side by side.
- Check that production configurations are at least as restrictive as staging configurations.
- Verify that security settings are not relaxed in production compared to staging.
- Check that resource allocations scale appropriately between environments.
- Flag any settings that exist in one environment but are missing from another.
- Pay special attention to configurations that are identical across environments when they should differ (e.g., database connection strings, domain names).

## Step 9: Generate Review Report

Compile all findings into a structured report organized by severity.

### Report Structure

```
## Infrastructure Review Report

### Summary
- Files reviewed: [count]
- Critical findings: [count]
- Warnings: [count]
- Suggestions: [count]

### Critical Findings
[Each finding with file path, line number, description, and fix recommendation]

### Warnings
[Each finding with file path, line number, description, and fix recommendation]

### Suggestions
[Each finding with file path, line number, description, and fix recommendation]

### Checklist Compliance
[Per IaC type, show which checklist items passed and which failed]
```

Present the report to the user. For each finding, include:
- The severity level (CRITICAL, WARNING, SUGGESTION).
- The file path and approximate line range.
- A clear description of the issue.
- A specific recommendation for how to fix it, including a code example where helpful.

## Docker Compose Checklist

- [ ] All images use pinned version tags
- [ ] All services have health checks
- [ ] Resource limits are defined for all services
- [ ] Restart policies are set for all services
- [ ] Named networks are used for service isolation
- [ ] No inline secrets in environment variables
- [ ] Named volumes used for persistent data
- [ ] Read-only mounts where write access is unnecessary

## Terraform Checklist

- [ ] Remote state backend is configured with locking
- [ ] Provider versions are pinned
- [ ] All variables have descriptions and type constraints
- [ ] Sensitive variables are marked as sensitive
- [ ] No plaintext secrets in .tfvars files
- [ ] Outputs have descriptions
- [ ] Consistent resource naming convention
- [ ] Repeated patterns extracted into modules

## Kubernetes Checklist

- [ ] Resource requests and limits on all containers
- [ ] Liveness and readiness probes on all containers
- [ ] Security context with non-root user and dropped capabilities
- [ ] No :latest image tags
- [ ] Explicit namespace on all resources
- [ ] Network policies defined
- [ ] Pod disruption budgets for critical workloads
- [ ] Dedicated service accounts (not default)

## Notes

- Findings marked CRITICAL should be resolved before merging or deploying.
- Findings marked WARNING indicate significant risk and should be addressed soon.
- Findings marked SUGGESTION are improvements that enhance maintainability and reliability.
- When in doubt about a finding's severity, err on the side of caution and assign a higher severity.
- Cross-environment comparisons are especially important before production deployments.
