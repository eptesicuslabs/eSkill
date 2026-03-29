---
name: e-merge
description: "Resolves merge conflicts by analyzing intent from both branches via LSP. Use when a merge, rebase, or cherry-pick produces conflicts or conflict markers appear in files. Also applies when: 'fix merge conflicts', 'resolve conflicts', 'conflicting changes after rebase', 'merge failed'."
---

# Merge Conflict Resolution

This skill provides a structured approach to resolving merge conflicts by understanding the intent behind each side's changes before choosing a resolution strategy. It emphasizes comprehension over speed -- understanding why the conflict exists leads to better resolutions.

## Core Principle

Understand intent before resolving. Never blindly pick a side. Every conflict exists because two developers made changes to the same code with different goals. The correct resolution preserves both goals when possible.

## Prerequisites

- A git repository with active merge conflicts (from a merge, rebase, or cherry-pick).
- Access to eMCP git and LSP tools.

## Workflow

### Step 1: Identify Conflicted Files

Use `git_status` from the eMCP git server to list all files with unresolved conflicts.

Conflicted files are marked with a specific status indicator (e.g., `UU` for both modified, `AA` for both added, `DU` for deleted by us/modified by them).

Record the full list of conflicted files and their conflict type:

| Status | Meaning                                          |
|--------|--------------------------------------------------|
| UU     | Both branches modified the same file              |
| AA     | Both branches added a file with the same name     |
| DU     | Our branch deleted the file, theirs modified it   |
| UD     | Our branch modified the file, theirs deleted it   |
| AU     | We added, they modified (during rebase)           |

The resolution strategy differs based on the conflict type.

### Step 2: Read the Conflict Markers

For each conflicted file (type UU or AA), read the file content to locate conflict markers:

```
<<<<<<< HEAD (or ours)
[code from the current branch]
=======
[code from the incoming branch]
>>>>>>> feature-branch (or theirs)
```

Some merge strategies also include a common ancestor section:

```
<<<<<<< HEAD
[our changes]
||||||| merged common ancestors
[original code before either change]
=======
[their changes]
>>>>>>> feature-branch
```

The three-way view (with the common ancestor) is especially valuable because it shows what each side changed relative to the original. If the merge was initiated without `diff3` style, the common ancestor section is absent.

For each conflict block, record:
- The file path and line range.
- The "ours" content.
- The "theirs" content.
- The common ancestor content (if available).

### Step 3: Understand Intent from Commit History

For each conflicted file, use `git_log` from the eMCP git server to find the commits that caused the conflict:

- **Our commits**: Commits on the current branch that modified the conflicted lines.
- **Their commits**: Commits on the incoming branch that modified the conflicted lines.

Read the commit messages and, if available, the associated pull request descriptions. These explain why the change was made.

Key questions to answer:
- What feature or fix does each side's change serve?
- Are the changes independent (both can coexist) or contradictory (only one can be kept)?
- Is one side a refactoring while the other is a functional change?

### Step 4: View File State on Each Branch

Use `git_show` from the eMCP git server to see the complete file as it exists on each branch:

- `git_show HEAD:<filepath>` for the current branch version.
- `git_show <incoming-ref>:<filepath>` for the incoming branch version.

Reading the full file (not just the conflict markers) provides context:
- Other changes in the same file that are not conflicting but are relevant.
- Whether the conflict is in the middle of a larger refactoring.
- Whether surrounding code depends on the conflict resolution.

### Step 5: Analyze Semantic Impact with LSP

Use LSP tools to understand how the conflicting code is used in the broader codebase:

- **lsp_references** on functions or variables in the conflict zone. Determine which callers depend on the current behavior and which would depend on the incoming behavior.
- **lsp_hover** on types in the conflict to verify type compatibility between the two versions.

This is especially important for conflicts involving:
- Function signatures (parameter changes may affect all callers).
- Type definitions (changes may affect all consumers).
- Import statements (may affect module resolution).
- Configuration files (may affect runtime behavior).

If LSP is not available (e.g., the file is not a supported language), skip this step and rely on manual analysis.

### Step 6: Determine the Resolution Strategy

Based on the analysis from Steps 3-5, choose a resolution strategy for each conflict:

**Take ours**:
- Use when our change is correct and theirs is outdated or superseded.
- Use when theirs was a temporary fix that our change properly addresses.

**Take theirs**:
- Use when their change is correct and ours is outdated or superseded.
- Use when their change is a more recent fix for the same issue.

**Manual merge (combine both)**:
- Use when both changes are needed and can coexist.
- This is the most common case for independent features touching the same code.
- Requires understanding both changes to produce correct combined code.

**Rewrite**:
- Use when neither version is correct as-is and the conflict reveals a deeper issue.
- Write new code that satisfies both sides' requirements.

**Delete (for file-level conflicts)**:
- For DU/UD conflicts, decide whether the file should exist.
- If deleted by one side for a good reason (e.g., module was replaced), accept the deletion.
- If modified by the other side with important changes, keep the file.

Document the chosen strategy and rationale for each conflict before applying it.

### Step 7: Apply the Resolution

For each conflict, edit the file to produce the resolved version:

- Remove all conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
- Apply the chosen strategy.
- Ensure the resolved code is syntactically correct.
- Ensure imports and dependencies are consistent.

Use `fs_edit` from the eMCP filesystem server to make the changes.

After resolving all conflicts in a file, mark it as resolved:
- This is typically done by staging the file (`git add <filepath>`).

### Step 8: Run Tests to Verify

After resolving all conflicts, run the test suite using `test_run` from the eMCP test-runner server.

This step is non-negotiable. Merge conflicts are a prime source of subtle bugs:
- A function was renamed on one branch and called on the other -- the call site may reference the old name.
- A type was extended on one branch and consumed on the other -- the consumer may not handle the new fields.
- An import was changed on one branch and the imported symbol was used differently on the other.

Run the full test suite, not just tests for the conflicted files, because conflicts can have ripple effects.

### Step 9: Handle Test Failures

If tests fail after resolution:

1. **Identify which test failed** and trace it back to a conflict resolution.
2. **Determine if the resolution was incorrect** or if the test itself needs updating.
3. **Revisit the specific conflict** that caused the failure, returning to Step 3 for that file.
4. **Do not mark the merge as complete** until all tests pass.

Common post-resolution failures:
- Type errors from incompatible merged signatures.
- Import errors from conflicting module restructuring.
- Logic errors from combining two independent code paths incorrectly.
- Test assertion failures from changed behavior that was correctly merged but the test was not updated.

## Conflict Prevention Notes

While this skill focuses on resolving conflicts, some practices reduce their frequency:

- **Small, focused branches**: Fewer changes per branch means fewer potential conflict points.
- **Frequent rebasing**: Regularly rebasing feature branches onto the main branch keeps the delta small.
- **Communication**: When two developers need to modify the same file, coordinate to avoid parallel changes.
- **Modular code**: Well-separated modules with clear interfaces reduce the chance of overlapping changes.

## Special Cases

### Lock file conflicts (package-lock.json, yarn.lock)

Do not manually resolve lock file conflicts. Instead:
1. Accept either side's version.
2. Run the package manager's install command to regenerate the lock file.
3. Stage the regenerated lock file.

### Generated file conflicts

For files generated by tooling (protobuf outputs, GraphQL codegen, etc.):
1. Accept either side's version.
2. Re-run the code generation tool.
3. Stage the regenerated output.

### Binary file conflicts

Binary files cannot be merged textually. Choose one version or the other based on which branch has the correct version. If both versions are needed (e.g., different image assets), coordinate with the team on which to keep.

## Edge Cases

- **Conflicts in auto-generated files**: Protobuf outputs, GraphQL codegen, and ORM-generated code should not be manually merged. Accept either side and re-run the generator.
- **Semantic conflicts without textual conflict markers**: Two branches may both compile but produce incorrect behavior when combined (e.g., both add an item to the same list in different places). Run tests after resolution to catch these.
- **Rebase vs. merge conflicts**: Conflicts during rebase appear one commit at a time and may require different resolutions per commit. Do not assume the resolution for commit N applies to commit N+1.
- **Whitespace and formatting-only conflicts**: When one branch reformatted a file while the other modified logic, the diff is large but the real conflict is small. Identify the logical change and re-apply the formatter after resolution.
- **Nested conflict markers**: If a previous unresolved merge left conflict markers in a file and a new merge introduces more, the file may contain nested `<<<<<<<` markers. Resolve the inner conflicts first.

## Related Skills

- **e-review** (eskill-coding): Follow up with e-review after this skill to verify the conflict resolution did not introduce regressions.
- **e-testgen** (eskill-coding): Follow up with e-testgen after this skill to add tests covering the merged code paths.
