---
name: refactoring-workflow
description: "Guides safe refactoring with reference tracking and test verification loops. Use when renaming a symbol across files, extracting a function or module, or restructuring layout. Also applies when: 'refactor this', 'rename across all files', 'extract into its own module', 'move this function'."
---

# Refactoring Workflow

This skill provides a structured, safety-first approach to code refactoring. Every transformation is bracketed by test runs to ensure correctness. It leverages AST tools for structural changes and LSP for reference tracking.

## Core Principle

Never skip the test verification loop. The sequence is always:

1. Run tests (establish green baseline).
2. Make a single refactoring change.
3. Run tests again.
4. If red, revert and investigate. If green, proceed to the next change.

## Prerequisites

- A working test suite that passes (green baseline).
- LSP server running for the project language.
- Clear definition of the refactoring goal.

## Workflow

### Step 1: Define the Refactoring Goal

Identify exactly what transformation is needed. Common refactoring types:

| Refactoring       | Description                                                |
|-------------------|------------------------------------------------------------|
| Rename            | Change the name of a symbol (variable, function, class)    |
| Extract function  | Pull a block of code into a new named function             |
| Extract module    | Move related functions/classes into a separate file         |
| Inline            | Replace a function call with the function body             |
| Move              | Relocate a symbol from one module to another               |
| Change signature  | Add, remove, or reorder function parameters                |
| Simplify          | Reduce complexity of conditionals or nested logic          |

Document the goal clearly: what symbol or code block is being transformed, and what the end state should look like.

### Step 2: Establish a Green Baseline

Before making any changes, run the full test suite using `test_run` from the eMCP test-runner server:

```
test_run with the project's test command
```

If tests are not green, stop. Refactoring on a red test suite makes it impossible to distinguish pre-existing failures from regressions introduced by the refactoring.

Record the test results as the baseline. Note the number of passing tests and execution time.

### Step 3: Find All Usages with LSP

Use `lsp_references` from the eMCP LSP server to locate every reference to the target symbol:

- For **renames**: Find all files and locations where the symbol is used.
- For **extract function**: Find all occurrences of the code pattern being extracted.
- For **move**: Find all imports/requires of the symbol being relocated.
- For **change signature**: Find all call sites that pass arguments to the function.

Create a complete list of locations that will need updating. This is the change manifest.

If LSP is unavailable, fall back to `ast_search` with pattern matching and `grep` via shell as a last resort. Note that text-based search may produce false positives.

### Step 4: Analyze Structure with AST

Use `ast_search` from the eMCP AST server to understand the structural context:

- For **extract function**: Identify the variables used in the target block that would become parameters, and the values produced that would become return values.
- For **change signature**: Identify all call sites and their argument patterns to understand how callers use the function.
- For **simplify**: Map the branching structure to understand which paths can be consolidated.
- For **move**: Identify internal dependencies that must move with the symbol or become imports.

### Step 5: Apply Changes

Choose the appropriate mechanism based on the refactoring type:

**Structural changes** (extract, inline, change signature): Use `ast_rewrite` from the eMCP AST server. This ensures syntactically correct transformations that respect the language grammar.

**Simple renames**: Use `edit_text` from the eMCP filesystem server applied to each location in the change manifest from Step 3. Process files one at a time.

**Module moves**: This is a multi-step operation:
1. Create the new file with the moved symbol(s).
2. Update all import statements to point to the new location.
3. Remove the symbol(s) from the original file.
4. If the original file re-exported the symbol, add a re-export for backward compatibility (optional, based on user preference).

Apply changes in small batches. Prefer one logical change per iteration so that if tests fail, the cause is isolated.

### Step 6: Run Tests After Each Change

After each batch of changes, run the test suite again using `test_run`:

- Compare results against the baseline from Step 2.
- If all tests pass: the change is safe. Record it and proceed.
- If tests fail: proceed to Step 7.

For large refactorings with many files, it is acceptable to run only the tests related to the changed modules first (if the test framework supports filtering), then run the full suite after all changes are applied.

### Step 7: Handle Test Failures

If tests fail after a change:

1. **Do not proceed** with additional changes.
2. Read the test failure output carefully to identify the root cause.
3. Determine if the failure is:
   - **A missed reference**: A usage of the old symbol that was not updated. Fix it and re-run.
   - **A logic error**: The transformation changed behavior, not just structure. This means the change was not a pure refactoring. Revert and reconsider the approach.
   - **A test that needs updating**: The test asserts on internal details (e.g., function names in snapshots) rather than behavior. Update the test and document why.
4. If the root cause is unclear, revert the last change and investigate further before retrying.

To revert, use `git_checkout` on the affected files or `git_stash` to save the work-in-progress.

### Step 8: Review All Changes

After all refactoring steps are complete and tests are green, review the full set of changes:

- Use `diff_files` from the eMCP diff server to see the complete diff.
- Verify that no unintended changes crept in.
- Confirm that the diff only contains the planned refactoring, not accidental formatting or logic changes.
- Check that no debugging artifacts (console.log, print statements) were introduced.

Present the diff summary to the user for confirmation before committing.

## Safety Guidelines

- **One refactoring at a time.** Do not combine a rename with an extract. Complete one, verify, commit, then start the next.
- **Commit after each successful refactoring.** This creates save points that can be reverted individually.
- **Preserve behavior.** A refactoring changes structure, not behavior. If behavior must change, that is a separate task.
- **Watch for side effects.** Some refactorings (especially moves) can change module initialization order, which may have runtime effects even if tests pass.
- **Communicate scope.** If the refactoring touches more files than expected, pause and confirm with the user before proceeding.

## Related Skills

- **test-scaffolding** (eskill-coding): Run test-scaffolding before this skill to establish a safety net for refactoring changes.
- **dead-code-finder** (eskill-coding): Run dead-code-finder before this skill to identify removal candidates as part of the refactoring plan.
- **code-review-prep** (eskill-coding): Follow up with code-review-prep after completing this skill to summarize refactoring changes for reviewers.
