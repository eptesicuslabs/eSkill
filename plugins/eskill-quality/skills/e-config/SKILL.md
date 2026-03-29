---
name: e-config
description: "Compares config files across environments to detect drift and missing values. Use when debugging environment-specific failures, verifying configs after changes, or auditing infra consistency. Also applies when: 'config drift', 'environment mismatch', 'why does staging differ from production', 'compare env files', 'missing config key'."
---

# Configuration Audit

This skill compares configuration files across environments and deployment targets to identify drift, inconsistencies, security misconfigurations, and missing values. It produces a structured comparison report with actionable findings.

## Prerequisites

- At least two environment configuration files to compare (e.g., .env.development and .env.production, or staging.yml and production.yml).
- The eMCP filesystem, egrep_search, and data_file_read servers available for parsing config files and searching for config references.
- Knowledge of which environments exist or willingness to auto-detect from file naming conventions.

## Step 1: Identify Configuration Files and Environment Variants

Scan the project for configuration files and determine which environments are defined.

1. Use `filesystem` to search for common configuration file patterns at the project root and in subdirectories:
   - Environment files: `.env`, `.env.local`, `.env.development`, `.env.staging`, `.env.production`, `.env.test`, `.env.example`
   - JSON configuration: `config/*.json`, `config/**/*.json`, `settings/*.json`
   - YAML configuration: `config/*.yml`, `config/*.yaml`, `*.config.yml`
   - TOML configuration: `config/*.toml`, `*.config.toml`
   - Docker: `docker-compose.yml`, `docker-compose.override.yml`, `docker-compose.prod.yml`, `docker-compose.staging.yml`, `Dockerfile`, `Dockerfile.prod`
   - Kubernetes: `k8s/*.yml`, `k8s/*.yaml`, `kubernetes/**/*.yml`, `manifests/**/*.yaml`
   - Terraform: `*.tf`, `*.tfvars`, `environments/*.tfvars`
   - Nginx/Apache: `nginx.conf`, `nginx/*.conf`, `.htaccess`
   - CI/CD: `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/config.yml`
2. Group files by their environment designation:
   - Parse the environment from the filename (e.g., `.env.production` belongs to the "production" environment).
   - For directory-based organization (e.g., `config/production/`), use the directory name.
   - For files without an explicit environment (e.g., `docker-compose.yml`), treat as the "base" or "default" configuration.
3. Record the complete list of environments detected and the configuration files belonging to each.

## Step 2: Read Configuration Files

Load the content of every identified configuration file.

1. For structured files (JSON, YAML, TOML): use `data_file_read` to parse into a structured representation. This allows key-by-key comparison.
2. For .env files: use `filesystem` `fs_read` and parse as key-value pairs. Handle:
   - Comments (lines starting with `#`).
   - Quoted values (single and double quotes).
   - Multi-line values (if supported by the .env parser in use).
   - Variable interpolation references (e.g., `${OTHER_VAR}`).
   - Empty values vs. missing keys.
3. For Dockerfiles and CI configs: use `filesystem` `fs_read` for raw content comparison.
4. Store all parsed configurations keyed by (file, environment) for comparison.

## Step 3: Compare Structured Configurations

For JSON, YAML, and TOML files that have environment variants, perform a structured comparison.

1. Use `data_file_query` to extract matching keys from each environment variant.
2. Build a unified key set: the union of all keys across all environments.
3. For each key, record the value in each environment (or mark as "missing").
4. Identify:
   - **Keys present in all environments**: compare values for expected differences.
   - **Keys present in some environments but not others**: these represent drift or incomplete configuration.
   - **Keys with identical values across environments that should differ**: flag as potential misconfiguration (e.g., same database URL in development and production).
   - **Keys with different values across environments that should be identical**: flag for review (e.g., application name, API version).

## Step 4: Compare Environment Variable Files

For .env files, perform a key-based comparison across environments.

1. Extract the key set from each .env file.
2. Build a comparison matrix: environments as columns, keys as rows.
3. For each key, record:
   - Present/absent in each environment.
   - Value in each environment (redact actual secret values in the report, showing only whether they differ).
4. Compare against the `.env.example` file (if present) as the canonical key set:
   - Keys in `.env.example` but missing from an environment file: flag as missing configuration.
   - Keys in an environment file but not in `.env.example`: flag as undocumented configuration.
5. Check for variable interpolation correctness: if a value references `${OTHER_VAR}`, verify that `OTHER_VAR` is defined in the same file.

## Step 5: Detect Configuration Drift

Analyze the comparison data to identify drift patterns.

### Missing Keys

- A key present in production but missing from staging suggests staging may not faithfully reproduce production behavior.
- A key present in the example file but missing from any environment indicates incomplete setup.
- For each missing key, use `egrep_search` to find all references to that config key across the codebase (e.g., `process.env.MISSING_KEY`, `os.environ['MISSING_KEY']`). This reveals which code paths are affected by the missing configuration and helps prioritize remediation.
- Report each missing key with the environments where it is absent.

### Suspicious Identical Values

Flag values that are identical across environments when they should not be:
- Database connection strings: development and production should differ.
- API endpoints: staging and production should point to different services.
- Secret keys, tokens, and passwords: must differ across environments.
- Encryption keys: reuse across environments is a security risk.

### Suspicious Different Values

Flag values that differ across environments when they should be identical:
- Application version strings.
- Feature flag configurations (unless intentionally staged rollouts).
- Logging format strings.
- Shared service configurations that are not environment-specific.

### Value Format Inconsistencies

- Boolean values represented differently: `true` vs `1` vs `"true"` vs `yes`.
- URL formats: trailing slash present in one environment but not another.
- Port numbers: string in one environment, integer in another.
- List delimiters: comma-separated in one environment, JSON array in another.

## Step 6: Generate Detailed Diffs

For each pair of environment configurations that show differences, produce a readable diff.

1. Use `diff` (`diff_text`) to generate a textual diff between corresponding configuration files.
2. For structured files, produce a semantic diff that shows:
   - Added keys (present in one environment, absent in the other).
   - Removed keys (present in the other, absent in this one).
   - Changed values (key exists in both, value differs).
3. Present diffs in a clear format:
   - Show the environment names being compared.
   - For each difference, show the key, the value in each environment, and whether this difference is expected or suspicious.
4. When comparing more than two environments, produce pairwise diffs between the base/default configuration and each environment-specific override.

## Step 7: Check for Security Issues

Scan all configuration files for security-related problems.

### Plaintext Secrets

- Search for values that appear to be secrets based on their key names: keys containing `password`, `secret`, `token`, `key`, `credential`, `auth`.
- Use `egrep_search` to find all references to these secret config keys across the entire codebase. This reveals whether secrets are accessed safely (via secret managers) or directly interpolated into code, connection strings, or log statements.
- If the value is present in plaintext (not a reference to a secret manager), flag it.
- Check whether the configuration file is in `.gitignore`. If not, flag the risk of secrets being committed to version control.

### Overly Permissive Settings

- `DEBUG=true` or `debug: true` in production configuration.
- `CORS_ALLOW_ALL=true` or `Access-Control-Allow-Origin: *` in production.
- `ALLOWED_HOSTS=*` or equivalent wildcard host settings in production.
- `SSL_VERIFY=false` or `NODE_TLS_REJECT_UNAUTHORIZED=0` in any environment.
- Verbose logging levels (`LOG_LEVEL=debug` or `LOG_LEVEL=trace`) in production.

### Default Credentials

- Values that match common defaults: `password`, `admin`, `root`, `changeme`, `default`, `test`.
- Database URLs with default credentials (e.g., `postgres:postgres@localhost`).
- API keys that are placeholder values (e.g., `your-api-key-here`, `xxx`, `TODO`).

### Missing Security Configuration

- No HTTPS enforcement configuration in production.
- No rate limiting configuration.
- No CSRF protection configuration.
- No session timeout configuration.
- No content security policy headers.

## Step 8: Generate the Audit Report

Structure the report for clarity and actionability.

### Configuration Inventory

- List all detected configuration files, grouped by environment.
- For each file: path, format, number of keys/settings, environment designation.

### Environment Comparison Matrix

A table showing each configuration key and its value (or status) in each environment. Redact sensitive values but indicate whether they are set and whether they differ.

### Drift Findings

For each detected drift issue:
- The key or setting affected.
- Which environments are involved.
- The nature of the drift (missing, unexpected match, unexpected difference, format inconsistency).
- Severity: critical (production security issue), high (likely misconfiguration), medium (inconsistency), low (cosmetic).
- Recommended action.

### Security Findings

For each security issue:
- The configuration file and key.
- The issue description.
- Severity.
- Recommended remediation (use a secret manager, change the value, add to .gitignore, etc.).

### Detailed Diffs

Include the generated diffs from Step 6 as an appendix for reviewers who want to see exact differences.

### Recommendations

- Summary of priority actions ordered by severity.
- Suggestions for configuration management improvements (centralized config, secret managers, environment validation scripts).
- Template for a `.env.example` file if one does not exist, based on the union of all discovered keys.

## Reference: Common Configuration Patterns to Audit

| Pattern                  | What to Check                                  | Risk if Misconfigured                  |
|--------------------------|------------------------------------------------|----------------------------------------|
| Database URL             | Different per environment, no plaintext creds  | Data breach, wrong database accessed   |
| API keys / secrets       | Different per environment, not in version control | Credential exposure                 |
| Debug / verbose flags    | Disabled in production                         | Information disclosure                 |
| CORS settings            | Restrictive in production                      | Cross-origin attacks                   |
| SSL / TLS settings       | Enabled and enforced in production             | Man-in-the-middle attacks              |
| Logging level            | Appropriate per environment                    | Performance issues, info disclosure    |
| Feature flags            | Correct per environment                        | Unintended feature exposure            |
| Cache settings           | Appropriate TTLs per environment               | Stale data, performance issues         |
| Rate limiting            | Configured in production                       | Denial of service                      |
| Session configuration    | Secure settings in production                  | Session hijacking                      |

## Edge Cases

- **Config values injected at runtime**: Some values are provided by secret managers, environment variables, or Kubernetes configmaps at deploy time and never appear in committed files. Mark these as "runtime-injected" rather than "missing."
- **Nested config formats with environment overrides**: Frameworks like Spring Boot use hierarchical property overrides (application.yml -> application-prod.yml). The effective config is a deep merge, not a simple file comparison.
- **Feature flag configs**: Feature flags may intentionally differ across environments (enabled in staging, disabled in production). Flag these differences as informational, not as drift.
- **Config files generated by build tools**: Some config files (e.g., Webpack-generated) are created during the build and should not be compared across environments. Detect generated files and exclude them.
- **Encrypted config values**: Values encrypted with SOPS, AWS KMS, or similar tools cannot be compared at the plaintext level. Detect encrypted fields and note that content comparison is not possible.

## Related Skills

- **e-deploy** (eskill-devops): Follow up with e-deploy after this skill to include configuration verification in the deploy process.
- **e-infra** (eskill-devops): Run e-infra alongside this skill to audit both application and infrastructure configurations.
