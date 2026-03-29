---
name: e-secrets
description: "Detects committed secrets in git history and generates rotation plans with cleanup options. Use when secrets are committed, during security audits, or setting up secret scanning. Also applies when: 'leaked secret in git', 'rotate credentials', 'clean git history', 'secret in commit history'."
---

# Secrets Remediation

This skill detects secrets committed to git repositories, assesses exposure scope, generates credential rotation plans, and provides history cleanup options. It handles the full lifecycle from detection through remediation and prevention.

## Prerequisites

Confirm the repository root with the user. Determine whether the repository is public or private, and whether it has been pushed to a remote. Public repository exposure is significantly more severe because secrets may already be cached by third parties.

The eMCP egrep_search and crypto_random servers must be available. `egrep_search` provides trigram-indexed instant code search for scanning large codebases and git history for secret patterns. `crypto_random` generates cryptographically secure replacement secrets during rotation.

## Step 1: Scan Current Working Tree

Use `egrep_search` to scan the current state of all tracked files for secret patterns. The trigram-indexed search is significantly faster than `fs_search` for applying multiple regex patterns across a large codebase and returns results instantly.

Apply the following detection patterns:

| Secret Type | Pattern | Example Match |
|------------|---------|---------------|
| AWS Access Key | `AKIA[0-9A-Z]{16}` | AKIAIOSFODNN7EXAMPLE |
| AWS Secret Key | `(?i)aws_secret_access_key\s*[=:]\s*[A-Za-z0-9/+=]{40}` | wJalrXUtnFEMI/K7MDENG... |
| GitHub Token | `gh[pousr]_[A-Za-z0-9_]{36,255}` | ghp_xxxxxxxxxxxx |
| GitLab Token | `glpat-[A-Za-z0-9\-_]{20,}` | glpat-xxxxxxxxxxxx |
| Generic API Key | `(?i)(api[_-]?key\|apikey)\s*[=:]\s*['"][A-Za-z0-9]{20,}['"]` | api_key = "abc123..." |
| Generic Secret | `(?i)(secret\|token\|password\|passwd)\s*[=:]\s*['"][^'"]{8,}['"]` | password = "hunter2" |
| Private Key | `-----BEGIN (RSA\|EC\|DSA\|OPENSSH\|PGP) PRIVATE KEY-----` | PEM-encoded key block |
| JWT | `eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}` | eyJhbGciOi... |
| Connection String | `(?i)(mongodb\|postgres\|mysql\|redis\|amqp)://[^\s'"]+@[^\s'"]+` | postgres://user:pass@host |
| Slack Webhook | `https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+` | Slack incoming webhook URL |
| Stripe Key | `sk_(test\|live)_[A-Za-z0-9]{20,}` | sk_test_xxxxxxxxxxxx |
| SendGrid Key | `SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}` | SG.xxxxxx.xxxxxx |
| Google API Key | `AIza[0-9A-Za-z\-_]{35}` | AIzaSyxxxxxxxxxx |

Exclude files in:
- `.git/` directory.
- `node_modules/`, `vendor/`, `.venv/`, `target/`, `dist/`, `build/` directories.
- Binary files (images, compiled assets, archives).
- Lock files (`package-lock.json`, `yarn.lock`, etc.) which may contain registry tokens that are separate concerns.

For each finding, record the file path, line number, secret type, and a truncated preview (first 8 and last 4 characters only, to avoid displaying the full secret).

## Step 2: Scan Git History

Use `git` and `egrep_search` to search the commit history for secrets that may have been committed and later removed.

Execute the following approach:

1. Use `git_log` to retrieve the list of all commits on the current branch.
2. For each commit (or for a targeted range if the user specifies), use `git_diff` to examine the changes introduced.
3. Apply the same detection patterns from Step 1 against the `+` lines (additions) in each diff. Use `egrep_search` to scan diff output for secret patterns -- its trigram index handles large diffs efficiently.
4. Record findings with the commit hash, author, date, file path, and secret type.

Alternative approach for large repositories:
- Use `shell` to run `git log --all -p --diff-filter=A` piped through pattern matching, limiting to relevant file types.
- Focus on commits that modified files commonly associated with secrets: `.env`, `config.*`, `credentials.*`, `*.pem`, `*.key`.

Note: Secrets found only in history (not in the current tree) are still a risk because:
- Anyone who has cloned the repository has the full history.
- Git hosting platforms may cache commit diffs.
- Automated scanners continuously harvest secrets from public repositories.

## Step 3: Assess Exposure Scope

For each detected secret, determine how widely it has been exposed.

| Factor | Low Exposure | Medium Exposure | High Exposure |
|--------|-------------|-----------------|---------------|
| Repository visibility | Private, limited access | Private, team-wide access | Public |
| Duration in history | Less than 24 hours | Days to weeks | Months or more |
| Branch | Unmerged feature branch | Main/default branch | Main + tagged releases |
| Remote pushed | Not pushed | Pushed to private remote | Pushed to public remote |
| Forks | No forks | Internal forks only | Public forks exist |

Use `git` to determine:
- When the secret was first committed: `git_log` for the file or specific line.
- Whether the commit exists on the main branch or only a feature branch.
- Whether the commit has been pushed to a remote.

For each secret, assign an exposure level: low, medium, high, or critical.

Use `crypto` to generate a SHA-256 hash of each detected secret value. This hash can be used to track the secret through rotation without storing the actual value. Use `crypto_random` to generate cryptographically secure replacement values (random bytes, UUIDs) for each secret that needs rotation.

## Step 4: Generate Rotation Plan

For each detected secret, produce a rotation procedure specific to the secret type.

For all secret types below, use `crypto_random` to generate the replacement secret value (e.g., a 32-byte random hex string for API keys, a UUID for tokens, a 64-character random string for passwords). This ensures cryptographic randomness rather than relying on ad-hoc generation.

**AWS Access Keys**:
1. Create a new access key pair in the IAM console or via AWS CLI.
2. Update all services using the old key to reference the new key.
3. Test all dependent services with the new key.
4. Deactivate the old key (do not delete immediately).
5. After 48 hours with no errors, delete the old key.

**Database Credentials**:
1. Create a new database user or change the password for the existing user.
2. Update connection strings in environment variables or secret manager.
3. Restart dependent services to pick up the new credentials.
4. Verify connectivity and run integration tests.
5. Drop the old user or confirm the old password no longer works.

**API Keys (Generic)**:
1. Generate a new API key in the service's dashboard.
2. Update the application configuration to use the new key.
3. Deploy the configuration change.
4. Verify the new key works in all environments.
5. Revoke the old key.

**Private Keys (SSH, TLS)**:
1. Generate a new key pair.
2. Deploy the new public key to all authorized_keys or certificate stores.
3. Update the application or service to use the new private key.
4. Test all connections.
5. Remove the old public key from all authorized locations.

**OAuth Client Secrets**:
1. Generate a new client secret in the OAuth provider.
2. Update the application configuration.
3. Deploy and verify authentication flows.
4. Delete the old client secret.

For each rotation procedure, note:
- Estimated downtime (if any).
- Services that will be affected.
- Rollback procedure if the new credential fails.

## Step 5: Clean Git History (If Requested)

If the user requests history cleanup, provide the appropriate method based on the situation.

**Option A: BFG Repo Cleaner** (recommended for most cases):
- Provide the command: `bfg --replace-text secrets.txt <repo>`
- Create the `secrets.txt` file listing each secret value with its replacement placeholder.
- Note: requires all collaborators to re-clone after force push.

**Option B: git filter-repo** (for complex cases):
- Provide the command structure for `git filter-repo --path <file> --invert-paths` or content-based replacement.
- Note: more flexible than BFG but more complex to use.

**Option C: git filter-branch** (legacy, last resort):
- Note this is deprecated in favor of git filter-repo but may be the only option on systems without additional tools.

Before any history rewrite:
1. Ensure all team members have pushed their work.
2. Create a full backup of the repository.
3. Coordinate the force push and re-clone with all collaborators.
4. Update any CI/CD pipeline references that may cache the old history.

After history rewrite:
1. Run the secret scan again to verify removal.
2. Contact the git hosting platform to clear cached data:
   - GitHub: contact support to clear cached views.
   - GitLab: run housekeeping on the project.
3. Force-push all branches and tags.
4. All collaborators must delete their local clone and re-clone.

## Step 6: Implement Prevention Measures

Recommend and help configure secret detection prevention.

**Pre-commit hooks**:
- Provide a `.pre-commit-config.yaml` configuration using `detect-secrets` or `gitleaks`:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

- Generate a `.gitleaks.toml` configuration file with rules matching the patterns from Step 1.
- Add appropriate allowlist entries for false positives (test fixtures, documentation examples).

**Gitignore rules**:
- Verify `.gitignore` includes common secret file patterns:
  - `.env`, `.env.local`, `.env.*.local`
  - `*.pem`, `*.key`, `*.p12`, `*.pfx`
  - `credentials.json`, `service-account.json`
  - `*.keystore`, `*.jks`

**CI/CD scanning**:
- Recommend integrating secret scanning into the CI pipeline.
- Provide configuration snippets for the project's CI platform.

**Secret management migration**:
- Recommend moving secrets to a dedicated secret manager (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault, Doppler).
- Provide the pattern for referencing secrets from environment variables rather than files.

## Step 7: Handle False Positives

Review each finding for potential false positives before finalizing the report.

Common false positives:

| Pattern | Context | Action |
|---------|---------|--------|
| API key pattern in test files | Test fixtures with dummy keys | Mark as false positive if clearly fake |
| JWT in documentation | Example tokens in README | Mark as false positive |
| Connection string with `localhost` | Local development config | Lower severity, not a production risk |
| Base64-encoded non-secret data | Encoded configuration values | Verify content is not sensitive |
| Password pattern in password policy docs | "Password must be 8 characters" | Mark as false positive |
| Private key in test certificates | Self-signed test certs | Lower severity if clearly marked as test |

For each finding, check the file context (surrounding lines, file path, file purpose) to assess whether the match is a true secret or a false positive.

Present uncertain findings to the user for manual classification.

## Step 8: Generate Remediation Report

Assemble findings into a structured report.

```
## Secrets Remediation Report

**Repository**: <name>
**Scan Date**: <YYYY-MM-DD>
**Repository Visibility**: <public/private>
**Scan Scope**: Working tree + git history

### Summary

| Metric | Count |
|--------|-------|
| Secrets in working tree | <N> |
| Secrets in git history only | <N> |
| False positives excluded | <N> |
| Critical exposure | <N> |
| Requiring rotation | <N> |

### Findings

| # | Type | File | Exposure | Status | Action Required |
|---|------|------|----------|--------|----------------|
| 1 | AWS Key | config/aws.js | Critical | Active | Rotate immediately |
| 2 | DB Password | .env | High | Removed in tree | Rotate + clean history |
| ... | ... | ... | ... | ... | ... |

### Rotation Plan
<per-secret rotation procedures from Step 4>

### History Cleanup Plan
<cleanup approach from Step 5>

### Prevention Recommendations
<measures from Step 6>
```

## Step 9: Verify Remediation

After rotation and cleanup are performed, re-run the scan to confirm remediation is complete.

1. Re-scan the working tree for any remaining secrets.
2. Re-scan the git history if history was rewritten.
3. Verify new secrets are stored in environment variables or a secret manager, not in files.
4. Verify pre-commit hooks are installed and functional.
5. Test the application with rotated credentials to confirm no service disruption.

Report the verification results as a follow-up to the remediation report.

## Step 10: Document the Incident

If the secret exposure constitutes a security incident, generate incident documentation.

Include:
- Timeline: when the secret was committed, when it was detected, when it was rotated.
- Scope: which systems and data could have been accessed with the compromised credential.
- Impact assessment: whether unauthorized access occurred (may require log analysis).
- Remediation steps taken.
- Prevention measures implemented.
- Lessons learned and process improvements.

This documentation supports compliance requirements (SOC2, HIPAA) that mandate incident tracking and resolution documentation.

## Edge Cases

- **Encrypted secret files**: Files encrypted with `git-crypt`, `sops`, or `age` may trigger false positives on the encrypted blob. Check for `.gitattributes` entries indicating encryption and exclude those files.
- **Environment-specific secrets**: Different environments (dev, staging, production) may have different secrets. Prioritize production secrets for immediate rotation; development secrets are lower risk.
- **Shared credentials**: If a credential is used across multiple repositories or services, rotation requires coordinated updates. Document all known consumers before rotating.
- **Service account keys**: Cloud service account keys (GCP JSON key files, Azure service principal) may have broad permissions. Check the associated IAM policies to assess blast radius.
- **Revoked but cached tokens**: Some tokens (JWTs, OAuth tokens) remain valid until expiration even after the signing key is rotated. Note the token lifetime and whether a force-revocation mechanism exists.
- **Large repositories**: For repositories with thousands of commits, scanning the full history may be slow. Offer to scan only the last N commits or a specific date range as a faster alternative.

## Related Skills

- **e-scan** (eskill-quality): Run e-scan before this skill to identify the hardcoded secrets that need remediation.
- **e-config** (eskill-quality): Follow up with e-config after this skill to verify secrets are properly externalized to secure storage.
