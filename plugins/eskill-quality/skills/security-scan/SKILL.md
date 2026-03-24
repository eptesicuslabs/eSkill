---
name: security-scan
description: "Scans source code for security vulnerabilities against OWASP Top 10 patterns. Use when auditing code before release, reviewing PRs for security holes, or checking for credential leaks. Also applies when: 'find security issues', 'check for vulnerabilities', 'any hardcoded secrets', 'scan for injection flaws', 'security review'."
---

# Security Vulnerability Scanner

This skill performs a comprehensive security scan of project source code by matching known vulnerability patterns against the OWASP Top 10 categories. It uses AST-based analysis for structural patterns and regex-based search for credential leaks and other textual patterns.

## Step 1: Determine Project Languages and Frameworks

Before scanning, identify the project's technology stack to select the correct vulnerability patterns.

- Use `filesystem` to check for configuration files that indicate the language and framework:
  - `package.json` (Node.js / JavaScript / TypeScript)
  - `requirements.txt`, `setup.py`, `pyproject.toml` (Python)
  - `Cargo.toml` (Rust)
  - `go.mod` (Go)
  - `pom.xml`, `build.gradle` (Java)
  - `composer.json` (PHP)
- Read each detected configuration file with `data_file_read` to extract framework dependencies (e.g., Express, Django, Flask, Spring).
- Record the primary language(s) and framework(s) for pattern selection in subsequent steps.

## Step 2: Define Security Patterns

Organize vulnerability patterns by OWASP category. Each pattern includes an identifier, a description, the AST or regex query to execute, and a default severity.

### SQL Injection (A03:2021 - Injection)

For JavaScript/TypeScript, search for string concatenation or template literals within database query calls:

- ast_search pattern: function calls to `query`, `execute`, `raw` where arguments contain binary expressions (concatenation) or template literals referencing variables.
- Example AST query for JS/TS: search for `CallExpression` where the callee property name is `query` and any argument is a `TemplateLiteral` containing `Identifier` expressions.
- For Python: search for f-strings or percent-formatting inside calls to `cursor.execute`, `session.execute`, or raw SQL methods.

### Cross-Site Scripting / XSS (A03:2021 - Injection)

- Search for assignments to `innerHTML`, `outerHTML`, or usage of `dangerouslySetInnerHTML` in JSX.
- Search for `document.write()` calls with variable arguments.
- In template engines: search for unescaped output directives (`{!! !!}` in Blade, `| safe` in Jinja2, `<%- %>` in EJS).

### Command Injection (A03:2021 - Injection)

- Search for calls to `child_process.exec`, `child_process.execSync`, `spawn`, `execFile` where the command string includes variable interpolation.
- For Python: `os.system`, `subprocess.call`, `subprocess.Popen` with `shell=True` and string arguments containing variables.
- For any language: backtick execution or system() calls with unsanitized input.

### Path Traversal (A01:2021 - Broken Access Control)

- Search for file operations (`fs.readFile`, `fs.writeFile`, `open()`, `Path()`) where the path argument includes user-controlled input without validation.
- Check for absence of path canonicalization or prefix checks before file access.
- Flag any usage of `../` patterns constructed from request parameters.

### Insecure Deserialization (A08:2021 - Software and Data Integrity Failures)

- JavaScript: `eval()`, `Function()` constructor with dynamic input, `JSON.parse` of data from HTTP requests without schema validation.
- Python: `pickle.loads`, `yaml.load` without `Loader=SafeLoader`, `marshal.loads`.
- Java: `ObjectInputStream.readObject()` without type filtering.

### Hardcoded Secrets (A07:2021 - Identification and Authentication Failures)

Use `filesystem` `search_text` with regex patterns:
- API key patterns: `(?i)(api[_-]?key|apikey)\s*[:=]\s*['"][A-Za-z0-9]{16,}['"]`
- Password patterns: `(?i)(password|passwd|pwd)\s*[:=]\s*['"][^'"]{4,}['"]`
- Token patterns: `(?i)(token|secret|auth)\s*[:=]\s*['"][A-Za-z0-9+/=]{16,}['"]`
- AWS key patterns: `AKIA[0-9A-Z]{16}`
- Private key blocks: `-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----`
- Generic high-entropy strings assigned to credential-like variable names.

### Insecure Cryptography (A02:2021 - Cryptographic Failures)

- Search for usage of MD5 or SHA1 for password hashing or security-sensitive operations.
- Search for `Math.random()` or `random.random()` used in security contexts (token generation, nonces).
- Hardcoded initialization vectors (IVs) or encryption keys in source code.
- ECB mode usage in block cipher operations.
- Disabled TLS certificate verification (`rejectUnauthorized: false`, `verify=False`).

### Missing Authentication (A07:2021 - Identification and Authentication Failures)

- In Express: route handlers (`app.get`, `app.post`, `router.get`) without authentication middleware in the middleware chain.
- In Django: view functions without `@login_required` or permission decorators.
- In Spring: controller methods without `@PreAuthorize` or security configuration.

### Server-Side Request Forgery / SSRF (A10:2021 - SSRF)

- Search for HTTP client calls (`fetch`, `axios`, `requests.get`, `http.Get`) where the URL is constructed from user input.
- Flag any URL passed to HTTP methods that originates from request parameters, query strings, or request bodies.

### Open Redirect (A01:2021 - Broken Access Control)

- Search for redirect calls (`res.redirect`, `redirect()`, `HttpResponseRedirect`) where the target URL comes from user input.
- Check for absence of URL validation or allowlist checking before redirect.

## Step 3: Execute AST-Based Pattern Searches

For each structural pattern defined in Step 2:

1. Construct the appropriate `ast_search` query for the detected language.
2. Execute the search across the entire source tree, excluding `node_modules/`, `vendor/`, `.git/`, `dist/`, `build/`, and other dependency/output directories.
3. Collect all matches with their file path and line number.
4. Store results in a working list keyed by vulnerability category.

When the project uses multiple languages, run language-specific patterns only against files of that language.

## Step 4: Execute Regex-Based Searches

For patterns better suited to text search (hardcoded secrets, URL patterns, specific string literals):

1. Use `filesystem` `search_text` with the regex patterns from Step 2.
2. Exclude binary files, lock files, and vendored dependencies.
3. Exclude known false positive paths: test fixtures, documentation examples, mock data.
4. Add matches to the working results list under the appropriate category.

## Step 5: Assign Severity Levels

For each finding, assign a severity based on the category and context:

- **Critical**: Hardcoded production secrets, SQL injection in production code, command injection with direct user input, deserialization of untrusted data.
- **High**: XSS in user-facing code, path traversal, SSRF, missing authentication on sensitive endpoints, disabled TLS verification.
- **Medium**: Weak cryptographic algorithms, open redirect, insecure random number generation, missing authorization checks.
- **Low**: Informational findings, patterns that may be intentional (e.g., eval in build scripts), deprecated function usage.

Adjust severity based on file context:
- Test files: reduce severity by one level (tests may intentionally use unsafe patterns).
- Configuration files: maintain or increase severity (misconfigurations have broad impact).
- Example/documentation files: reduce to low.

## Step 6: Check for Mitigating Factors

For each finding, check whether the vulnerability is actually mitigated:

- Is the input validated or sanitized before reaching the dangerous operation? Look for validation libraries (Joi, zod, cerberus), sanitization functions (DOMPurify, bleach), or manual checks upstream.
- Is the code behind an internal-only route or restricted to admin users?
- Is there a WAF, CSP header, or other infrastructure-level mitigation?
- Is the dangerous call using parameterized queries despite the pattern match?

If mitigation is confirmed, downgrade severity or mark the finding as mitigated with an explanation.

## Step 7: Trace Data Flow with LSP

For high and critical findings where the source of tainted data is not immediately clear:

1. Use `lsp_references` to find all references to the variable used in the dangerous operation.
2. Trace backwards from the sink (dangerous function call) to the source (user input).
3. Identify the full data flow path: entry point -> transformations -> sink.
4. Determine whether any transformation along the path constitutes effective sanitization.
5. Document the data flow path in the finding for reviewers.

This step adds significant confidence to findings and helps distinguish true positives from false positives.

## Step 8: Generate the Findings Report

Structure the report as follows:

### Report Header

- Project name and scan timestamp.
- Languages and frameworks detected.
- Files scanned count and lines of code scanned.
- Directories excluded from scan.

### Findings by Category

For each OWASP category that has findings, create a section:

- Category name and OWASP identifier.
- Number of findings in this category.
- For each finding:
  - **File**: absolute path with forward slashes.
  - **Line**: line number of the vulnerable code.
  - **Severity**: critical / high / medium / low.
  - **Description**: what the vulnerability is and why it is dangerous.
  - **Code snippet**: the relevant lines of code.
  - **Remediation**: specific instructions to fix the issue, with a corrected code example where feasible.
  - **Mitigated**: whether mitigation was detected, and what it is.

### Categories with No Findings

List categories that were scanned but produced no findings, to confirm they were checked.

## Step 9: Generate the Executive Summary

At the top of the report, include a summary:

- Total findings by severity (critical, high, medium, low).
- Top 5 most affected files (by number of findings).
- Most prevalent vulnerability category.
- Recommended remediation priority: address critical findings first, then high, then medium.
- Overall risk assessment: a brief narrative of the project's security posture based on findings.

## Reference: AST Search Patterns

### JavaScript / TypeScript

SQL Injection detection:
- Pattern: `CallExpression[callee.property.name='query'] TemplateLiteral`
- Pattern: `CallExpression[callee.property.name='execute'] BinaryExpression[operator='+']`

XSS detection:
- Pattern: `AssignmentExpression[left.property.name='innerHTML']`
- Pattern: `JSXAttribute[name.name='dangerouslySetInnerHTML']`

Command Injection detection:
- Pattern: `CallExpression[callee.property.name='exec'] TemplateLiteral`
- Pattern: `CallExpression[callee.name='exec'] BinaryExpression`

### Python

SQL Injection detection:
- Pattern: call to `execute` with f-string or %-format argument.
- Pattern: call to `raw` or `extra` with string concatenation.

Command Injection detection:
- Pattern: `subprocess.call` or `subprocess.Popen` with `shell=True` keyword argument and non-literal first argument.
- Pattern: `os.system` with f-string or concatenated argument.

Deserialization detection:
- Pattern: `pickle.loads` or `pickle.load` call.
- Pattern: `yaml.load` without `Loader=SafeLoader` keyword argument.

These patterns serve as starting points. Adapt and extend them based on the specific frameworks and libraries used in the target project.

## Related Skills

- **code-review-prep** (eskill-coding): Follow up with code-review-prep after this skill to include security findings in the code review summary.
- **dependency-audit** (eskill-coding): Run dependency-audit alongside this skill to cover both source code and dependency vulnerabilities.
- **secrets-remediation** (eskill-quality): Follow up with secrets-remediation after this skill to rotate and remove any hardcoded secrets that were detected.
