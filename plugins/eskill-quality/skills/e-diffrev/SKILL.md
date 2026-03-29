---
name: e-diffrev
description: "Performs security-focused differential review of code changes by analyzing diffs, calculating blast radius, checking test coverage, and generating structured security reports. Use when reviewing PRs or commits for security regressions. Also applies when: 'security review this PR', 'check this diff for vulnerabilities', 'blast radius analysis', 'is this change safe', 'security regression check'."
---

# Differential Security Review

This skill performs security-focused code review for PRs, commits, and diffs. It adapts analysis depth to codebase size, uses version control history for context, calculates blast radius, checks test coverage gaps, and generates a structured markdown report.

Unlike general code review, this skill focuses on **security regressions**: changes that weaken existing protections, remove validation, expand attack surface, or introduce new vulnerability patterns.

## Prerequisites

- A git repository with at least one commit to diff against.
- The eMCP filesystem, shell, ast_search, fs_search, egrep_search, and diff_apply servers available.
- Access to the test suite for coverage verification.

## When to Use

- Reviewing PRs or commits that touch auth, crypto, access control, or external calls
- Pre-merge security checks for changes with high blast radius
- Auditing commits that modify security-critical code paths
- Any diff review where security regression is a concern

## When NOT to Use

- Greenfield code with no baseline to compare (use e-scan instead)
- Documentation-only or formatting-only changes
- The user explicitly requests a quick summary and accepts the risk
- General code quality review without security focus (use e-review instead)

## Workflow

### Step 1: Triage the Change

Determine the scope and risk level of the change. Use `shell` tools (shell_exec) to examine the diff:

1. Get the list of changed files and their change size (lines added/removed)
2. Classify each changed file by risk level:

| Risk Level | Triggers |
|------------|----------|
| HIGH | Auth, crypto, external calls, value transfer, validation removal |
| MEDIUM | Business logic, state changes, new public APIs |
| LOW | Comments, tests, UI-only, logging |

3. Determine codebase size for strategy selection:

| Codebase Size | Strategy | Approach |
|---------------|----------|----------|
| SMALL (<20 changed files) | DEEP | Read all dependencies, full version history |
| MEDIUM (20-200 files) | FOCUSED | 1-hop dependencies, priority files only |
| LARGE (200+ files) | SURGICAL | Critical paths only, skip LOW risk files |

4. Check for immediate red flags that require escalation regardless of triage:
   - Removed code from commits with "security", "CVE", or "fix" in the message
   - Access control modifiers removed (public where private was, exported where internal was)
   - Validation removed without replacement
   - External calls added without input sanitization

### Step 2: Analyze Code Changes

For each HIGH and MEDIUM risk file, use `filesystem` tools and `ast_search` from the eMCP AST server to analyze the change:

1. **Read the diff** to understand what changed
2. **Read the full file** (not just the diff) for context
3. **Check version history** for the changed lines:
   - Were these lines part of a security fix? If removed code came from a "fix" or "CVE" commit, this is a potential regression.
   - Who wrote the original code and why?

4. For each changed function, answer:
   - What security property did this code enforce before?
   - Does the new code maintain that property?
   - Does the change expand the input domain (accept more values)?
   - Does the change reduce validation (check fewer conditions)?

### Step 3: Calculate Blast Radius

For each HIGH risk change, determine how many callers are affected:

1. Use `ast_search` to find all call sites for the changed function
2. Use `egrep_search` to find references across the codebase -- the trigram-indexed search is faster than `fs_search` for blast radius analysis, especially on large codebases where you need to scan every file for function name references. Fall back to `fs_search` only if `egrep_search` is unavailable.
3. Count direct callers and transitive callers (callers of callers, one level deep)

| Blast Radius | Direct Callers | Risk Adjustment |
|-------------|----------------|-----------------|
| Contained | 1-5 | No change |
| Moderate | 6-20 | Elevate MEDIUM to HIGH |
| Wide | 21-50 | Require adversarial analysis |
| Critical | 50+ | Require senior review |

A HIGH risk change with wide blast radius is the most dangerous combination. Prioritize analysis of these.

### Step 4: Check Test Coverage

For each security-relevant change:

1. Use `egrep_search` to find test files that reference the changed function (faster than `fs_search` for scanning all test directories)
2. Check if the security property is explicitly tested:
   - Is there a test for the auth check?
   - Is there a test for the validation logic?
   - Is there a negative test (verifying that unauthorized access is denied)?

3. Classify coverage:

| Coverage | Meaning | Impact on Review |
|----------|---------|-----------------|
| Tested | Security property has explicit test | Normal review |
| Partially tested | Function tested but security property not | Elevate concern |
| Untested | No tests reference the changed function | Flag in report, elevate severity |

Missing security tests for HIGH risk changes should be called out explicitly in the report.

### Step 5: Adversarial Analysis (HIGH Risk Only)

For HIGH risk changes, think from an attacker's perspective:

1. **Attack surface change**: Does this change expose a new endpoint, accept new input, or weaken a boundary?
2. **Concrete exploit scenario**: Write a 2-3 sentence scenario of how an attacker could exploit this change. Not generic ("could be exploited") but specific ("an unauthenticated user sends a crafted JWT with the 'none' algorithm to /api/admin, bypassing the removed signature check").
3. **Exploitability rating**:

| Rating | Criteria |
|--------|----------|
| Proven | Exploit scenario is complete and requires no special access |
| Likely | Exploit requires specific conditions that are plausible |
| Possible | Exploit requires unlikely conditions or significant effort |
| Unlikely | Theoretical only, no practical attack path found |

### Step 6: Generate Report

Produce a structured markdown report. Include every section:

```markdown
# Differential Security Review

**Change:** [PR/commit reference]
**Strategy:** DEEP / FOCUSED / SURGICAL
**Files analyzed:** N of M changed files
**Coverage limitation:** [what was not analyzed and why]

## Summary
- HIGH risk findings: N
- MEDIUM risk findings: N
- Coverage gaps: N
- Overall assessment: APPROVE / CONCERNS / BLOCK

## Findings

### [Finding Title]
**Risk:** HIGH / MEDIUM
**Location:** file:line
**Blast radius:** N direct callers, M transitive
**Test coverage:** Tested / Partially tested / Untested

**What changed:**
[Before/after comparison]

**Security impact:**
[What security property is affected]

**Exploit scenario:** (HIGH risk only)
[Concrete attack description]

**Recommendation:**
[Specific fix or mitigation]

**Suggested patch:** (when applicable)
Use `diff_apply` to propose unified patches that fix the identified security issue. Generate the patch in unified diff format and apply it with `diff_apply` so the fix can be reviewed and applied atomically. This is preferred over manual file edits for security fixes because the patch can be reviewed as a self-contained unit.

## Coverage Gaps
[Security-relevant changes without test coverage]

## Recommendations
[Ordered list of actions: block, fix before merge, fix after merge, accept risk]
```

Sort findings by risk level (HIGH first), then by blast radius (widest first).

## Quality Checklist

Before delivering the report, verify:

- [ ] All changed files classified by risk level
- [ ] Version history checked for removed security code
- [ ] Blast radius calculated for HIGH risk changes
- [ ] Attack scenarios are concrete, not generic
- [ ] Findings reference specific line numbers
- [ ] Coverage gaps identified for security-critical changes
- [ ] Report file generated (not just chat output)
- [ ] Coverage limitations stated honestly

## Rationalizations to Reject

| Shortcut | Why it is wrong |
|----------|-----------------|
| "Small PR, quick review" | Heartbleed was 2 lines. Classify by RISK, not size. |
| "I know this codebase" | Familiarity breeds blind spots. Build explicit context. |
| "Version history takes too long" | History reveals regressions. Never skip it. |
| "Blast radius is obvious" | You will miss transitive callers. Calculate quantitatively. |
| "No tests means not my problem" | Missing tests means elevated risk. Flag it. |
| "Just a refactor, no security impact" | Refactors break invariants. Analyze as HIGH until proven LOW. |

## Edge Cases

- **Squashed merge commits**: When a PR is squash-merged, the diff shows all changes at once but commit history context is lost. Reconstruct intent from PR description or individual commits if available.
- **Generated code in the diff**: Protobuf stubs, OpenAPI clients, or ORM migrations may appear as large changes. Identify the generator and review the source definition instead of the output.
- **Moved files with modifications**: Git may report a file as deleted + created rather than renamed + modified. Check for renames to avoid missing modifications hidden inside a "new" file.
- **Dependency lockfile changes**: Large lockfile diffs can contain supply chain attack vectors (new transitive dependencies). Do not skip them even though they appear mechanical.
- **Cross-PR dependencies**: A change may be safe in isolation but introduce a vulnerability when combined with another pending PR targeting the same branch. Flag shared critical paths.

## Related Skills

- **e-review** (eskill-coding): Use e-review for general code quality review, then chain e-diffrev for the security-focused pass on the same diff.
- **e-scan** (eskill-quality): Run e-scan on the full codebase when e-diffrev finds a HIGH-risk pattern that may exist in unchanged code.
- **e-variant** (eskill-quality): When e-diffrev finds a vulnerability in a diff, use e-variant to search for the same pattern across the rest of the codebase.
