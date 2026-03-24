---
name: branch-cleanup
description: "Identifies stale and merged git branches and produces a prioritized cleanup plan. Use when the branch list is cluttered, during repo maintenance, or before a release. Also applies when: 'too many branches', 'clean up old branches', 'which branches can I delete', 'remove merged branches'."
---

# Branch Cleanup

This skill analyzes all branches in a git repository, categorizes them by status and activity, and presents a prioritized cleanup plan. It never deletes branches automatically -- all deletions require explicit user confirmation.

## Prerequisites

- A git repository with multiple branches.
- Access to the eMCP git server tools.

## Workflow

### Step 1: List All Branches

Use `git_branches` from the eMCP git server to retrieve all local and remote-tracking branches.

Collect the following for each branch:
- Branch name.
- Whether it is local, remote, or both.
- The tracking relationship (which remote branch a local branch tracks, if any).

Identify the main branch (usually `main` or `master`). This serves as the merge target for status checks. If the main branch name is ambiguous, check for:
- A branch named `main`.
- A branch named `master`.
- The default branch configured in the remote.

### Step 2: Get Last Commit Date for Each Branch

For each branch, use `git_log` from the eMCP git server to retrieve the most recent commit:

- Request only the latest commit (limit 1).
- Extract the commit date, author, and subject.

Record this information. It determines whether the branch is active or stale.

### Step 3: Determine Merge Status

For each branch, determine whether it has been fully merged into the main branch.

A branch is considered **merged** if the main branch contains all commits from the branch. This can be checked by:
- Running the equivalent of `git branch --merged main` via git tools.
- Or checking if the diff between the branch and main is empty (all changes have been incorporated).

Record the merge status for each branch:
- **Merged**: All commits are in main. Safe to delete.
- **Unmerged**: The branch contains commits not in main. Deletion would lose work.
- **Partially merged**: Some commits are in main (e.g., via cherry-pick) but the branch was not formally merged.

### Step 4: Check Remote Tracking State

For each local branch, determine its relationship with remote branches:

| State              | Description                                              |
|--------------------|----------------------------------------------------------|
| Tracked            | Local branch has a remote counterpart and they are in sync |
| Behind remote      | Remote has commits the local branch does not              |
| Ahead of remote    | Local has commits not pushed to remote                    |
| Orphaned           | Local branch exists but its remote counterpart was deleted |
| Local only         | Branch was never pushed to a remote                       |
| Remote only        | Branch exists on remote but has no local checkout         |

Orphaned branches are common after PRs are merged and the remote branch is deleted. They are usually safe to clean up.

### Step 5: Categorize Branches

Assign each branch to one of the following categories:

**Safe to delete** (merged branches):
- The branch is fully merged into main.
- The branch is not the current branch.
- The branch is not a protected branch (main, master, develop, release/*).

**Stale** (inactive branches):
- The last commit is older than 30 days.
- The branch is not merged into main.
- Requires review before deletion -- work may be abandoned or still needed.

**Active** (recently worked on):
- The last commit is within the last 30 days.
- The branch is not merged into main.
- Should be kept.

**Orphaned** (remote deleted):
- Local branch whose remote tracking branch no longer exists.
- If merged, safe to delete. If unmerged, flag for review.

**Protected** (never suggest deletion):
- main, master, develop, staging, production, release/*.
- Any branch matching patterns the user has designated as protected.

### Step 6: Present the Categorized List

Format the results as a clear, actionable report:

```
## Branch Cleanup Report

### Repository Summary
- Total branches: 47 (32 local, 15 remote-only)
- Main branch: main
- Current branch: feature/new-dashboard

### Safe to Delete (12 branches)
These branches are fully merged into main.

| Branch                  | Last Commit  | Author     | Merged Via          |
|-------------------------|--------------|------------|---------------------|
| feature/user-auth       | 2025-01-15   | Alice      | PR #142             |
| fix/login-redirect      | 2025-01-20   | Bob        | PR #145             |
| chore/update-deps       | 2025-02-01   | Charlie    | PR #148             |
[... additional entries ...]

### Stale Branches (5 branches)
These branches have no commits in the last 30 days and are NOT merged.

| Branch                  | Last Commit  | Author     | Days Inactive |
|-------------------------|--------------|------------|---------------|
| feature/old-experiment  | 2024-09-10   | Dave       | 160           |
| wip/refactor-api        | 2024-11-22   | Alice      | 87            |
[... additional entries ...]

### Orphaned Branches (3 branches)
These local branches track remote branches that no longer exist.

| Branch                  | Last Commit  | Merge Status |
|-------------------------|--------------|--------------|
| feature/completed-task  | 2025-01-10   | Merged       |
| experiment/prototype    | 2024-12-01   | Unmerged     |
[... additional entries ...]

### Active Branches (8 branches)
These branches have recent activity and are not merged.

| Branch                  | Last Commit  | Author     | Status         |
|-------------------------|--------------|------------|----------------|
| feature/new-dashboard   | 2025-03-01   | Eve        | Current branch |
| feature/api-v2          | 2025-02-28   | Alice      | Ahead by 12    |
[... additional entries ...]
```

### Step 7: Suggest Deletions

Based on the categorization, suggest specific cleanup actions:

**Recommended (safe)**:
- Delete all merged branches (list them explicitly).
- Delete orphaned branches that are merged.

**Suggested (review first)**:
- Archive or delete stale unmerged branches after confirming the work is no longer needed.
- Delete orphaned unmerged branches after confirming the work was incorporated another way.

**No action needed**:
- Active branches.
- Protected branches.

Format suggestions as executable commands but do not run them:

```
## Suggested Commands

# Delete merged local branches:
git branch -d feature/user-auth
git branch -d fix/login-redirect
git branch -d chore/update-deps

# Delete orphaned local branches (merged):
git branch -d feature/completed-task

# Prune remote-tracking references:
git remote prune origin
```

## Important Safety Rules

- **Never auto-delete branches.** Always present the list and wait for user confirmation.
- **Never delete the current branch.** Warn if it appears in any deletion list.
- **Never delete protected branches.** These include main, master, develop, and release branches.
- **Preserve unmerged work.** Stale unmerged branches may contain valuable work. Always flag them for review rather than suggesting immediate deletion.
- **Prefer -d over -D.** Use `git branch -d` (lowercase) which refuses to delete unmerged branches, as an additional safety net. Only suggest `-D` (uppercase, force delete) when the user has explicitly confirmed the branch should be deleted despite being unmerged.

## Related Skills

- **release-workflow** (eskill-devops): Run release-workflow before this skill to finalize releases before cleaning up stale branches.
- **changelog-generation** (eskill-coding): Run changelog-generation before this skill to capture branch history before branches are removed.
