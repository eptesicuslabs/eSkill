---
name: e-terra
description: "Reviews Terraform configurations for module structure, state management, variable hygiene, and provider versioning. Use when writing Terraform, reviewing IaC PRs, or auditing state. Also applies when: 'review my Terraform', 'check Terraform best practices', 'audit IaC modules', 'Terraform code review'."
---

# Terraform Module Review

This skill performs a structured review of Terraform configurations by analyzing module organization, state management practices, variable definitions, provider version constraints, and resource naming conventions. It produces a graded report with actionable findings.

## Prerequisites

Confirm the root directory of the Terraform configuration with the user. This is typically the directory containing the top-level `main.tf` or the root module. All paths in the review are relative to this root.

## Step 1: Inventory Terraform Files

Use `egrep_search_files` to enumerate all Terraform-related files in the project by matching file name patterns (`*.tf`, `*.tfvars`, `*.tf.json`, `terragrunt.hcl`).

- Search for files matching `*.tf` and `*.tfvars` recursively from the project root.
- Search for `*.tf.json` files (JSON-based Terraform configuration).
- Identify `terragrunt.hcl` files if Terragrunt is in use.
- Record the total file count and directory structure.

Classify each directory as one of:

| Directory Type | Indicators |
|----------------|------------|
| Root module | Contains `main.tf`, `variables.tf`, `outputs.tf` at the top level |
| Child module | Lives under `modules/` and is referenced by `module` blocks |
| Environment config | Lives under `environments/`, `envs/`, or `stages/` |
| Shared module | Lives under `shared/` or `common/` and is used across environments |
| Generated | Contains `.terraform/`, `terraform.tfstate`, or lock files only |

Exclude `.terraform/` directories from further analysis. Note any `.tfstate` files found in the working tree, as these should typically not be committed.

## Step 2: Analyze Module Structure

Use `data_file_read` to read each `main.tf`, `variables.tf`, `outputs.tf`, and `providers.tf` file in the root module and each child module.

Evaluate the following structural conventions:

1. **File separation**: Each module should split configuration into at least `main.tf`, `variables.tf`, and `outputs.tf`. A single monolithic `.tf` file exceeding 300 lines is a finding.
2. **Module boundaries**: Child modules should be self-contained with their own variable and output declarations. Check that no child module references parent resources directly via `data` sources when a variable would be more appropriate.
3. **Module source references**: For each `module` block, examine the `source` attribute:
   - Local paths (`./modules/...`) are acceptable for in-repo modules.
   - Registry references (`hashicorp/...`) should include a version constraint.
   - Git references should pin to a tag or commit hash, not a branch.
4. **Module nesting depth**: Modules calling other modules that call further modules creates complexity. Flag nesting deeper than 2 levels.
5. **Module size**: A single module with more than 15 resources is a candidate for decomposition.

Record each finding with the file path, line reference, and a severity (critical, high, medium, low).

## Step 3: Review Provider Configuration

Use `data_file_read` to read all provider blocks across the configuration.

Check the following:

- **Version constraints**: Every `required_providers` block should specify a version constraint. Missing version constraints allow uncontrolled upgrades.
  - Acceptable: `version = "~> 5.0"`, `version = ">= 4.0, < 6.0"`
  - Problematic: no version specified, or `version = ">= 0.0.0"`
- **Provider lock file**: Verify that `.terraform.lock.hcl` exists and is committed. This file pins exact provider versions for reproducible builds.
- **Required Terraform version**: Check for a `required_version` constraint in the `terraform` block. This prevents running the configuration with an incompatible Terraform binary.
- **Provider aliases**: If multiple instances of the same provider are used (e.g., multi-region AWS), verify that aliases are defined and used consistently.
- **Backend configuration**: Check that the `backend` block is configured for remote state. Local state in team environments is a critical finding.

| Provider Check | Severity | Condition |
|---------------|----------|-----------|
| No version constraint | High | `required_providers` block missing version |
| No lock file | High | `.terraform.lock.hcl` absent |
| No Terraform version constraint | Medium | `required_version` not set |
| Local backend in shared project | Critical | `backend "local"` or no backend block |
| Provider alias inconsistency | Medium | Alias defined but not used, or used but not defined |

## Step 4: Audit Variable Hygiene

Use `data_file_read` to read all `variables.tf` files and any `.tfvars` files.

For each variable declaration, check:

1. **Description**: Every variable should have a `description` attribute. Undocumented variables make modules difficult to consume. Flag missing descriptions as medium severity.
2. **Type constraint**: Every variable should have an explicit `type` attribute. Untyped variables accept any value, which is error-prone.
3. **Default values**: Sensitive variables (passwords, keys, tokens) should never have default values. Check variable names matching patterns: `password`, `secret`, `key`, `token`, `credential`, `auth`.
4. **Validation blocks**: Complex variables (CIDR blocks, ARNs, email addresses) benefit from `validation` blocks. Note their presence or absence.
5. **Sensitive flag**: Variables containing secrets should have `sensitive = true`. Cross-reference variable names against the sensitive patterns above.
6. **Naming convention**: Variables should use snake_case. Flag camelCase or mixed-case variable names.
7. **Unused variables**: Variables declared but never referenced in any `.tf` file are dead code. Use `egrep_search` to search for references to each variable name across all `.tf` files.

Separately, check `.tfvars` files:

- Ensure no secrets appear in `.tfvars` files that are committed to version control.
- Verify that `.tfvars` files not intended for commit are listed in `.gitignore`.

## Step 5: Evaluate State Management

Use `filesystem` and `data_file_read` to examine backend configuration and state-related practices.

Check the following:

1. **Remote state backend**: Verify the backend is configured for a remote store (S3, GCS, Azure Blob, Terraform Cloud, Consul). Local state is acceptable only for personal experiments.
2. **State locking**: For S3 backends, verify a DynamoDB table is configured for locking. For GCS, verify the bucket has object versioning enabled. State corruption from concurrent writes is a critical risk.
3. **State file in repo**: Use `filesystem` to check whether any `*.tfstate` or `*.tfstate.backup` files exist in the repository. These should never be committed.
4. **State encryption**: For S3 backends, verify `encrypt = true` is set. For other backends, check encryption configuration.
5. **State segmentation**: Large deployments should split state across multiple configurations or workspaces. A single state file managing more than 100 resources is increasingly fragile.
6. **Remote state data sources**: Check `terraform_remote_state` data source usage. Each reference should document which state it reads and why.

| State Issue | Severity | Description |
|------------|----------|-------------|
| `.tfstate` in repository | Critical | State files committed to version control |
| No state locking | Critical | Concurrent modifications can corrupt state |
| No encryption at rest | High | State contains sensitive data in plaintext |
| No remote backend | High | Local state prevents collaboration |
| Single large state | Medium | Over 100 resources in one state increases blast radius |

## Step 6: Check Resource Naming and Tagging

Use `data_file_read` to scan all resource blocks for naming and tagging practices.

1. **Resource naming**: Terraform resource names (the label after the resource type) should be descriptive and use snake_case. Generic names like `this`, `main`, or `default` obscure intent.
2. **Name attributes**: Resources that support a `name` or `Name` tag should have meaningful names, ideally incorporating environment and purpose.
3. **Tagging strategy**: For cloud resources, check for consistent tagging:
   - Required tags: `Environment`, `Project`, `Owner`, `ManagedBy` (should be "terraform").
   - Check whether tags are applied via a `default_tags` block on the provider (preferred) or individually per resource.
4. **Lifecycle rules**: Check for appropriate `lifecycle` blocks:
   - `prevent_destroy` on critical resources (databases, S3 buckets with data).
   - `create_before_destroy` on resources that cannot tolerate downtime.
   - `ignore_changes` usage should be justified, not used to mask drift.

## Step 7: Review Security Posture

Use `data_file_read` to check for common security misconfigurations.

- **Open security groups**: `ingress` rules with `cidr_blocks = ["0.0.0.0/0"]` on non-HTTP/HTTPS ports.
- **Public S3 buckets**: `acl = "public-read"` or `acl = "public-read-write"` without explicit justification.
- **Unencrypted storage**: EBS volumes, RDS instances, S3 buckets, or similar resources without encryption enabled.
- **Hardcoded credentials**: Any `access_key`, `secret_key`, or similar fields with literal values instead of variable references.
- **Overly permissive IAM**: `Action = "*"` or `Resource = "*"` in IAM policy documents.
- **Default VPC usage**: Resources deployed to the default VPC rather than a purpose-built VPC.
- **Missing logging**: CloudTrail, VPC flow logs, or access logging not configured for auditable resources.

Flag each finding with the resource address (e.g., `aws_security_group.web`) and the specific attribute.

## Step 8: Validate Outputs

Use `data_file_read` to read all `outputs.tf` files.

Check the following:

1. **Description**: Every output should have a `description` attribute.
2. **Sensitive marking**: Outputs that expose secrets, connection strings, or keys should have `sensitive = true`.
3. **Unused outputs**: Outputs that are not consumed by any parent module or remote state data source add noise. Note these as low-severity findings.
4. **Output completeness**: Modules should expose enough outputs for consumers to use them without reading internal resource attributes. Check that commonly needed attributes (IDs, ARNs, endpoints) are exported.

## Step 9: Run Formatting and Validation Checks

Use `shell` to run Terraform's built-in validation tools if the Terraform binary is available.

- `terraform fmt -check -recursive`: Report files that do not conform to canonical formatting.
- `terraform validate`: Report configuration errors that can be detected without provider initialization.

If the Terraform binary is not available, skip this step and note it in the report. The review can still provide value through static analysis alone.

Use `diff` to compare any formatting differences if `terraform fmt` produces changes.

## Step 10: Generate Review Report

Assemble the findings into a structured report.

### Report Structure

```
## Terraform Module Review

**Configuration Root**: <path>
**Modules Reviewed**: <count>
**Total Resources**: <count>
**Provider(s)**: <list>

### Summary

| Severity | Count |
|----------|-------|
| Critical | <N>   |
| High     | <N>   |
| Medium   | <N>   |
| Low      | <N>   |

### Findings

#### [SEV] Finding Title
- **Location**: <file>:<line>
- **Resource**: <resource address>
- **Description**: <what was found>
- **Recommendation**: <how to fix>

### Module Structure Assessment
<narrative assessment of overall module organization>

### Recommendations
<prioritized list of improvements>
```

Order findings by severity (critical first), then by file path. Group related findings when multiple instances of the same issue appear across files.

## Edge Cases

- **Terragrunt configurations**: If `terragrunt.hcl` files are present, note that the review covers only the generated Terraform files. Terragrunt-specific concerns (DRY configuration, dependency blocks) require separate analysis.
- **Terraform workspaces**: If workspace-based environment separation is used, check that workspace-aware logic (e.g., `terraform.workspace` references) is consistent and documented.
- **Partial configurations**: Some teams split provider and backend configuration into separate files injected at plan time. If expected files are missing, ask the user whether partial configuration is intentional.
- **Generated code**: If Terraform is generated by CDK for Terraform (CDKTF) or Pulumi crosswalk, note that the review covers the generated output. Code generation tools may produce non-idiomatic Terraform that is acceptable in that context.
- **Large monorepos**: For repositories with many independent Terraform configurations, ask the user which configuration to review rather than attempting to review everything.

## Related Skills

- **e-infra** (eskill-devops): Run e-infra alongside this skill for a comprehensive assessment of the full infrastructure stack.
- **e-cost** (eskill-devops): Follow up with e-cost after this skill to evaluate the cost impact of Terraform module changes.
