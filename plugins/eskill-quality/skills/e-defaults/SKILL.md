---
name: e-defaults
description: "Detects fail-open insecure defaults such as hardcoded secrets, weak authentication fallbacks, and permissive security configurations that allow apps to run insecurely in production. Use when auditing security, reviewing configuration management, or analyzing environment variable handling. Also applies when: 'find hardcoded secrets', 'check default credentials', 'audit config security', 'fail-open check', 'production config review'."
---

# Insecure Defaults Detection

This skill finds fail-open vulnerabilities where applications run insecurely when configuration is missing or uses default values. It distinguishes exploitable defaults from fail-secure patterns that crash safely.

The critical distinction:
- **Fail-open (vulnerable):** `SECRET = env.get('KEY') or 'default-secret'` -- app runs with a weak secret
- **Fail-secure (safe):** `SECRET = env['KEY']` -- app crashes if the variable is missing

This skill complements code-level security scanning (injection, XSS) by focusing on **configuration-level** attack surface: the gap between what a developer sets up locally and what reaches production.

## Prerequisites

- A codebase with configuration files (.env, application.yml, appsettings.json, or equivalent).
- The eMCP filesystem, data_file_read, ast_search, fs_search, and egrep_search servers available.
- Access to deployment configs (Dockerfiles, CI/CD configs, K8s manifests) for production override verification.

## When to Use

- Security audits of production applications (auth, crypto, API security)
- Configuration review of deployment files, IaC templates, Docker configs
- Code review of environment variable handling and secrets management
- Pre-deployment checks for hardcoded credentials or weak defaults
- Reviewing new services before first deployment

## When NOT to Use

- Test fixtures explicitly scoped to test environments (files in `test/`, `spec/`, `__tests__/`)
- Example or template files (`.example`, `.template`, `.sample` suffixes)
- Development-only tools (local Docker Compose for dev, debug scripts)
- Documentation examples in README.md or docs/ directories
- Build-time configuration that gets replaced during deployment
- Code that crashes on missing config (fail-secure by design)

When in doubt: trace the code path to determine if the app runs with the default or crashes.

## Workflow

### Step 1: Project Discovery

Determine the project's language, framework, and configuration approach.

1. Use `filesystem` tools to check for configuration files:
   - `.env`, `.env.example`, `.env.production`
   - `config/`, `settings/`, `application.yml`, `appsettings.json`
   - `Dockerfile`, `docker-compose.yml`, `kubernetes/`
   - IaC files: `terraform/`, `cloudformation/`, `pulumi/`

2. Use `data_file_read` from the eMCP data-file server to parse manifest files and identify:
   - Authentication libraries (passport, devise, next-auth, spring-security)
   - Crypto libraries (bcrypt, argon2, jose, crypto)
   - Configuration management (dotenv, config, viper)

3. Map the configuration flow: where do secrets enter the application? Environment variables, config files, secret managers, hardcoded values?

### Step 2: Search for Insecure Default Patterns

Use `egrep_search` as the primary search tool for these pattern categories. Its trigram-indexed instant search is faster than `fs_search` for finding default value patterns across large codebases. Fall back to `fs_search` only if `egrep_search` is unavailable. Tailor the exact patterns to the language identified in Step 1.

**Fallback secrets** (app runs with a weak default when env var is missing):

| Language | Pattern |
|----------|---------|
| Python | `os.environ.get('...', '...')` or `os.getenv('...') or '...'` |
| JavaScript | `process.env.VAR \|\| 'default'` or `process.env.VAR ?? 'fallback'` |
| Ruby | `ENV.fetch('...', '...')` or `ENV['...'] \|\| '...'` |
| Go | `os.Getenv("...")` with fallback assignment |
| Java | `System.getenv("...")` with ternary or `Optional.orElse` |

**Hardcoded credentials** (passwords, API keys, tokens embedded in source):

- `password`, `passwd`, `secret`, `api_key`, `apikey`, `token`, `auth` followed by `=` and a string literal
- Private keys: `-----BEGIN.*PRIVATE KEY-----`
- Connection strings with embedded passwords: `://user:pass@`

**Weak security defaults** (security features disabled by default):

- `DEBUG = True`, `debug: true`, `DEBUG=1`
- `AUTH_REQUIRED = false`, `REQUIRE_AUTH = false`
- `CORS_ORIGIN = *`, `Access-Control-Allow-Origin: *`
- `VERIFY_SSL = false`, `SSL_VERIFY = false`, `NODE_TLS_REJECT_UNAUTHORIZED = 0`

**Weak cryptography** (insecure algorithms in security contexts):

- `MD5`, `SHA1`, `DES`, `RC4`, `ECB` used for passwords, tokens, or encryption
- Note: MD5/SHA1 for checksums or cache keys is acceptable -- only flag security contexts

### Step 3: Verify Each Finding

For each match from Step 2, trace the code path to classify the finding. Use `ast_search` from the eMCP AST server to follow the variable through the call graph.

**Verification questions:**

1. **When is this code executed?** Startup vs. runtime vs. test-only?
2. **What happens if the configuration variable is missing?** Does the app crash (fail-secure) or continue (fail-open)?
3. **Is there validation that enforces secure configuration?** Some apps validate at startup and refuse to run with weak defaults.
4. **Does the production deployment provide this value?** Check Dockerfiles, CI configs, deployment scripts.

**Classification:**

| Behavior | Classification |
|----------|---------------|
| App crashes if config is missing | Fail-secure (SAFE) |
| App runs with a weak default | Fail-open (FINDING) |
| App logs a warning but continues | Fail-open (FINDING, reduced severity) |
| Default is overridden in production config | Code-level vulnerability (FINDING, lower severity) |
| Config is test-only or dev-only | Not a finding |

### Step 4: Assess Production Impact

For each confirmed fail-open finding:

1. Check if the production deployment provides the secure value:
   - Read Dockerfiles for `ENV` directives
   - Read CI/CD configs for secret injection
   - Read Kubernetes manifests for `secretKeyRef`
   - Read IaC templates for parameter definitions

2. Determine exploitation scenario:
   - **Hardcoded JWT secret**: Attacker forges tokens, gains unauthorized access
   - **Debug mode in production**: Stack traces leak internal paths, dependencies, database schemas
   - **Permissive CORS**: Cross-origin requests steal session data
   - **Disabled SSL verification**: Man-in-the-middle attacks on API calls

3. Assign severity:

| Severity | Criteria |
|----------|----------|
| CRITICAL | Secret used in auth/crypto, no production override found |
| HIGH | Security feature disabled by default, production override uncertain |
| MEDIUM | Weak default exists but production config provides secure value |
| LOW | Development convenience default with clear documentation |

### Step 5: Generate Report

Produce a structured report with one entry per finding:

```
## Finding: [Title]

**Severity:** CRITICAL / HIGH / MEDIUM / LOW
**Location:** file:line
**Pattern:** [exact code snippet]

**Verification:**
- App behavior when config is missing: [crashes / runs with default]
- Production config provides value: [yes / no / unknown]

**Exploitation scenario:**
[1-2 sentences describing what an attacker could do]

**Recommended fix:**
[Specific code change -- e.g., remove fallback, add startup validation, use secret manager]
```

Sort findings by severity (CRITICAL first). Include a summary count at the top.

### Step 6: Recommend Fixes

For each finding, recommend a specific fix pattern:

**Replace fail-open with fail-secure:**
```python
# Before (fail-open)
SECRET = os.environ.get('JWT_SECRET', 'default-secret')

# After (fail-secure)
SECRET = os.environ['JWT_SECRET']  # crashes if missing
```

**Add startup validation:**
```python
# Validate at startup, before any request handling
required_vars = ['JWT_SECRET', 'DB_PASSWORD', 'API_KEY']
missing = [v for v in required_vars if not os.environ.get(v)]
if missing:
    raise RuntimeError(f"Missing required env vars: {missing}")
```

**Use environment-aware defaults:**
```python
# Different defaults for dev vs production
if os.environ.get('ENV') == 'production':
    SECRET = os.environ['JWT_SECRET']  # fail-secure in prod
else:
    SECRET = os.environ.get('JWT_SECRET', 'dev-only-secret')
```

## Verification Checklist

Use this for quick triage before full analysis:

- [ ] Fallback secrets: `env.get(X) or Y` -- does app start without X?
- [ ] Default credentials: hardcoded username/password -- active in deployed config?
- [ ] Fail-open security: `AUTH_REQUIRED = false` -- default is insecure?
- [ ] Weak crypto: MD5/SHA1/DES/RC4/ECB -- used for passwords or encryption?
- [ ] Permissive access: CORS `*`, permissions `0777` -- allows unauthorized access?
- [ ] Debug features: stack traces, introspection -- enabled by default?

## Rationalizations to Reject

| Shortcut | Why it is wrong |
|----------|-----------------|
| "It's just a development default" | If it reaches production code, it is a finding |
| "The production config overrides it" | Verify the override exists; code-level vulnerability remains if not |
| "This would never run without proper config" | Prove it with a code trace; many apps fail silently |
| "It's behind authentication" | Defense in depth; a compromised session still exploits weak defaults |
| "We'll fix it before release" | Document now; "later" rarely comes |

## Edge Cases

- **Environment-aware defaults with incomplete coverage**: An app may have fail-secure defaults for production but fail-open defaults for staging. Check all deployment targets, not just production.
- **Secrets injected via orchestration layer**: Kubernetes secrets, AWS Secrets Manager, or Vault may inject values at runtime. Verify the injection path actually reaches the application variable, not just that the secret exists in the manager.
- **Multi-language monorepos with mixed config patterns**: A Python service may use fail-secure `os.environ['KEY']` while a Node.js service in the same repo uses fail-open `process.env.KEY || 'default'`. Audit each service independently.
- **Docker Compose overrides**: `docker-compose.override.yml` or profile-specific files may set different defaults than the base `docker-compose.yml`. Check all compose files in the merge chain.
- **Feature flags with insecure defaults**: Feature flag systems that default to "enabled" for debug or admin features when the flag service is unreachable.

## Related Skills

- **e-scan** (eskill-quality): Run e-scan alongside this skill to cover injection and OWASP patterns that e-defaults does not check.
- **e-config** (eskill-quality): Run e-config after this skill to detect environment drift where a secure default in one environment is missing in another.
- **e-secrets** (eskill-quality): Chain e-secrets before this skill to find committed secrets in git history, then use e-defaults to find secrets hardcoded as fallback values in source.
