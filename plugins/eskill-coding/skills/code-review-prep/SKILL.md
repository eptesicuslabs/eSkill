---
name: code-review-prep
description: "Prepares comprehensive code review summaries by analyzing git diffs with LSP and AST context. Use before code review sessions, when submitting pull requests, or when reviewing others' changes."
---

# Code Review Preparation

This skill produces a structured code review summary by combining git diff analysis with semantic understanding from LSP and AST tools. The output helps reviewers focus on high-risk areas and understand the intent behind changes.

## Prerequisites

- A git repository with changes to review (staged, unstaged, or between branches).
- LSP server running for the project language (optional but recommended).

## Workflow

### Step 1: Get the Diff

Determine what changes to analyze. Use `git_diff` from the eMCP git server with the appropriate arguments:

- **Staged changes**: `git_diff --cached`
- **Unstaged changes**: `git_diff`
- **Branch comparison**: `git_diff main..feature-branch`
- **Specific commits**: `git_diff abc123..def456`

If reviewing a pull request, diff the PR branch against its base branch.

Collect the full diff output, including file paths, added/removed lines, and context lines.

### Step 2: Categorize Changed Files

For each file in the diff, determine the change type:

| Change Type | Indicator                          |
|-------------|------------------------------------|
| New         | File exists only in the new state  |
| Modified    | File exists in both states         |
| Deleted     | File exists only in the old state  |
| Renamed     | File path changed, content similar |

Group files by their role in the project:

- **Source code**: Application logic files
- **Tests**: Test files and test utilities
- **Configuration**: Config files, environment templates, CI definitions
- **Documentation**: Markdown, comments, API docs
- **Dependencies**: Package manifests, lock files

### Step 3: Analyze Impact with LSP

For each modified source file, use LSP tools to understand the ripple effects:

- **lsp_hover** on changed function signatures to confirm type compatibility.
- **lsp_references** on modified or deleted functions to find all callers. If a function signature changed, every caller is a potential breakage point.
- **lsp_references** on modified or deleted types/interfaces to find all consumers.

Record which other files depend on the changed code. These are indirect impact zones that reviewers should be aware of.

### Step 4: Analyze Structural Changes with AST

Use `ast_search` from the eMCP AST server to identify structural changes:

- **New functions or methods**: Search for function definitions in the new state that do not exist in the old state.
- **Modified signatures**: Compare function parameter lists and return types between old and new versions.
- **Removed exports**: Identify symbols that were exported before but are no longer. These are potential breaking changes.
- **New classes or modules**: Identify entirely new structural elements.
- **Changed inheritance or interfaces**: Detect modifications to class hierarchies.

### Step 5: Flag Potential Issues

Scan the diff for common code review concerns:

**Complexity**:
- Functions exceeding 50 lines of added code.
- Deeply nested conditionals (3+ levels).
- High cyclomatic complexity introduced by new branches.

**Error handling**:
- New async operations without try/catch or .catch().
- New file or network operations without error handling.
- Catch blocks that swallow errors silently.

**Security**:
- String concatenation in SQL queries (potential injection).
- User input passed directly to shell commands.
- Hard-coded secrets or credentials in the diff.
- Changes to authentication or authorization logic.

**Untested code paths**:
- New functions in source files without corresponding new tests.
- Modified branching logic without updated test coverage.

**Style and conventions**:
- Inconsistent naming compared to surrounding code.
- TODO or FIXME comments without issue references.
- Console.log, print, or debug statements left in production code.

### Step 6: Generate Review Summary

Produce a structured review summary with the following sections:

```
## Review Summary

### Overview
- Branch: feature/user-auth -> main
- Files changed: 12
- Lines added: 340, removed: 85
- Primary areas: authentication, API routes, database models

### Risk Assessment
- Overall risk: MEDIUM
- Breaking changes: Yes (removed deprecated endpoint)
- Security-sensitive: Yes (authentication logic modified)
- Test coverage: Partial (2 new functions lack tests)

### File-by-File Analysis

#### src/auth/oauth.ts (NEW)
- Adds OAuth2 authentication provider
- Exports: OAuthProvider class, authenticate function
- Dependencies: express, passport
- Concerns: No rate limiting on token exchange endpoint

#### src/routes/users.ts (MODIFIED)
- Changes: Added auth middleware to 3 routes
- Impact: All callers of GET /users now require authentication
- Concerns: None

[... additional files ...]

### Suggested Focus Areas
1. Review OAuth token handling in src/auth/oauth.ts for security
2. Verify migration rollback in migrations/003_add_sessions.sql
3. Confirm error handling in src/services/token-refresh.ts
```

### Step 7: Verify Test Coverage of Changes

If test files are included in the diff, cross-reference them with source changes:

- For each new source function, check if at least one test case targets it.
- For each modified function, check if existing tests were updated to cover the new behavior.
- If test files are absent from the diff but source files changed significantly, flag this as a gap.

Use `ast_search` on test files to find test cases that reference the changed functions by name.

Report coverage gaps in the review summary under a dedicated "Test Coverage" section.

## Output Customization

The review summary format can be adapted based on the project's review culture:

- **Formal reviews**: Include all sections with detailed impact analysis.
- **Quick reviews**: Include only the risk assessment and flagged concerns.
- **PR descriptions**: Format as a pull request body with markdown.

When the user specifies a preference, adjust the verbosity and format accordingly.
