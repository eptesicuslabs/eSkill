---
name: e-variant
description: "Finds similar vulnerabilities and bugs across a codebase after an initial pattern is identified. Use when hunting bug variants, building search queries from known issues, or performing systematic code audits. Also applies when: 'find similar bugs', 'search for variants', 'this bug might exist elsewhere', 'systematic audit', 'pattern-based search'."
---

# Variant Analysis

This skill finds similar vulnerabilities and bugs across a codebase after identifying an initial pattern. Given a known bug, it systematically generalizes the pattern, searches the entire codebase, and triages matches to find other instances of the same root cause.

The core insight: most bugs are not unique. A logic error in one module often has variants in other modules written by the same team, using the same patterns, making the same assumptions.

## Prerequisites

- A known bug or vulnerability instance to use as the seed pattern.
- The eMCP filesystem, fs_search, egrep_search, and ast_search servers available.
- Access to the full codebase from the project root (not just the affected module).

## When to Use

- A vulnerability or bug has been found and you need to search for similar instances
- Building or refining search patterns for security audits
- Performing systematic code audits after an initial issue discovery
- Hunting for bug variants across a codebase
- Analyzing how a single root cause manifests in different code paths

## When NOT to Use

- Initial vulnerability discovery (use e-scan or domain-specific audit skills)
- General code review without a known pattern to search for
- Understanding unfamiliar code (use e-carto or e-learn first)
- The bug is truly unique to one location with no generalizable pattern

## Workflow

### Step 1: Understand the Original Issue

Before searching, deeply understand the known bug. Use `filesystem` tools to read the affected file and `ast_search` from the eMCP AST server to trace the call graph.

Answer these questions:

1. **What is the root cause?** Not the symptom, but WHY the code is wrong.
   - Symptom: "the auth check returns true for unauthenticated users"
   - Root cause: "null equality comparison -- when both userId and ownerId are null, `userId == ownerId` evaluates to true"

2. **What conditions are required?** Control flow, data flow, state that must exist for the bug to trigger.

3. **What makes it exploitable?** User-controlled input, missing validation, race condition window.

Document these answers before proceeding. If you cannot articulate the root cause, you are not ready to search for variants.

### Step 2: Create an Exact Match Pattern

Start with a search pattern that matches ONLY the known instance. Use `egrep_search` as the primary search tool -- it is specifically designed for pattern-based code search with a trigram index that returns results instantly even on very large codebases:

```
egrep_search("exact_vulnerable_code_here")
```

Verify: does the pattern match exactly ONE location (the original bug)? If it matches zero, the pattern is wrong. If it matches more than one, you may have already found variants.

### Step 3: Identify Abstraction Points

Examine the pattern and decide what can be generalized:

| Element | Keep Specific | Can Abstract |
|---------|---------------|--------------|
| Function name | If unique to this bug class | If pattern applies to a family of functions |
| Variable names | Never keep specific | Always replace with wildcards |
| Literal values | If the specific value matters | If any value triggers the bug |
| Argument count | If position matters | Use wildcards for variable args |
| Type names | If type-specific | If pattern applies across types |

### Step 4: Iteratively Generalize

This is the core of variant analysis. Change ONE element at a time:

1. Modify the search pattern to generalize one element
2. Run `egrep_search` against the ENTIRE codebase (project root scope, not just the current directory). The trigram index makes each iteration fast enough to support rapid generalization cycles.
3. Review ALL new matches
4. Classify each match as true positive or false positive
5. If false positive rate is acceptable (<50%), generalize the next element
6. If false positive rate is too high, revert and try a different abstraction
7. Repeat until further generalization produces >50% false positives

**Example generalization sequence:**

```
Round 1: userId == ownerId                    # exact match, 1 result
Round 2: \w+Id == \w+Id                       # generalize names, 8 results
Round 3: \w+ == \w+ (in auth context)         # generalize further, 23 results
Round 4: equality check in access control     # too broad, 150 results (60% FP)
         -> revert to Round 3
```

For structural patterns that text search cannot capture, escalate to `ast_search` from the eMCP AST server. AST-based search matches code structure (e.g., "equality comparison inside an if-block that guards a return statement") rather than text patterns.

### Step 5: Triage and Report Results

For each match, use `filesystem` tools to read the surrounding code and determine:

| Field | Description |
|-------|-------------|
| Location | File path and line number |
| Confidence | HIGH (same pattern), MEDIUM (similar), LOW (structural match only) |
| Exploitability | Is the code reachable? Are inputs user-controlled? |
| Priority | Based on impact and exploitability |

Generate a report with one entry per variant:
```
## Variant: [file:line]

**Confidence:** HIGH / MEDIUM / LOW
**Generalization round:** [which round found it]
**Code:** [relevant snippet with line numbers]

**Analysis:**
- Root cause applies: [yes/no, why]
- Reachable from user input: [yes/no, trace]
- Existing mitigations: [none / partial / full]

**Recommendation:** [fix / investigate further / false positive]
```

Sort by confidence (HIGH first), then by exploitability.

## Critical Pitfalls

### Narrow Search Scope
Searching only the module where the original bug was found misses variants in `utils/`, `middleware/`, or completely different services.

**Mitigation:** Always search from the project root. Use `egrep_search` with the widest scope.

### Pattern Too Specific
Using only the exact function name from the original bug.

**Example:** Bug uses `isAuthenticated` -- only searching that exact term -- missing `isActive`, `isAdmin`, `isVerified` which have the same logic error.

**Mitigation:** Enumerate ALL semantically related functions for the bug class.

### Single Vulnerability Class
Focusing on only one manifestation of the root cause.

**Example:** Original bug is "return allow when condition is false" -- only searching that pattern -- missing null equality bypasses, inverted conditional logic, documentation/code mismatches.

**Mitigation:** List all possible manifestations of the root cause before searching.

### Missing Edge Cases
Testing patterns only with normal scenarios.

**Mitigation:** Consider unauthenticated users, null/undefined values, empty collections, boundary values, and concurrent access when evaluating matches.

## Tool Selection

| Scenario | Tool | Rationale |
|----------|------|-----------|
| Quick surface search | `egrep_search` (eMCP egrep server) | Trigram-indexed instant results, fastest option for pattern-based code search |
| Fallback text search | `fs_search` (eMCP search server) | Use when egrep_search is unavailable |
| Structural matching | `ast_search` (eMCP AST server) | Matches code structure, ignores formatting |
| Cross-function tracing | `ast_search` with call graph mode | Follows values across function boundaries |
| Large codebase rules | External: Semgrep | Pattern rule files, no build required |
| Deep data flow | External: CodeQL | Best interprocedural taint analysis |

Start with `egrep_search` for speed -- its trigram index is specifically designed for the iterative pattern-matching workflow of variant analysis. Escalate to `ast_search` when text matching produces too many false positives. Recommend external tools when the analysis requires cross-function data flow tracking.

## Rationalizations to Reject

| Shortcut | Why it is wrong |
|----------|-----------------|
| "This bug is unique to this one location" | Most bugs have variants. Search before concluding. |
| "I searched this module, no other instances" | You searched one module, not the codebase. Search from root. |
| "The pattern is too generic, too many results" | You over-generalized. Revert one step and refine. |
| "I found 3 variants, that is probably all" | Run one more generalization round to verify. |
| "This code path is unreachable" | Prove it with a call graph trace, not intuition. |

## Edge Cases

- **Polyglot codebases**: The same bug pattern may manifest differently across languages in a monorepo. A null-equality issue in JavaScript (`==` vs `===`) has a different syntax variant in Python (`is` vs `==`). Search each language separately.
- **Vendored or forked dependencies**: Third-party code copied into the repo may contain the same vulnerability. Include `vendor/`, `third_party/`, and forked code in the search scope.
- **Dynamic dispatch and reflection**: Some variants are unreachable via static text or AST search because they use dynamic method calls, eval, or reflection. Flag these patterns as requiring manual review.
- **Test code with the same pattern**: A test helper may replicate the vulnerable pattern intentionally (to test the fix). Mark test-only matches as false positives but verify they are truly test-scoped.
- **Pattern appears in comments or documentation**: Search results include commented-out code that may be re-enabled later. Flag these separately as latent risk.

## Related Skills

- **e-scan** (eskill-quality): Use e-scan for initial vulnerability discovery, then chain e-variant to find additional instances of any pattern e-scan flags.
- **e-diffrev** (eskill-quality): When e-variant finds variants in recently changed code, use e-diffrev to assess the security impact of those changes.
- **e-deadcode** (eskill-coding): Run e-deadcode to confirm whether variant matches are in reachable code paths before triaging them as exploitable.
