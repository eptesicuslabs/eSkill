---
name: session-recap
description: "Summarizes work completed in the current session including code changes, decisions, and remaining items. Use at the end of a work session or when creating a progress summary. Also applies when: what did I do today, recap this session, summarize my changes, end of day summary."
---

# Session Recap

Generate a comprehensive summary of work completed during the current coding session. The recap captures code changes, decisions, remaining work, and project state to facilitate handoffs, end-of-day summaries, and continuity between sessions.

## Overview

A session recap answers four questions:

1. What was accomplished?
2. What changed in the codebase?
3. What decisions were made and why?
4. What remains to be done?

The recap is formatted as a structured document that can be saved to a file, appended to a session log, or presented directly in the conversation.

## Step 1: Determine Session Boundaries

Establish the time range for the recap. Use one of the following strategies:

**Option A: Branch-based** (preferred for feature work)
Identify the current branch using `git_status`. Find the merge base with the main branch using `git_merge_base`. All commits from the merge base to HEAD constitute the session.

**Option B: Time-based**
If the user specifies a time frame (e.g., "today," "last 2 hours"), use `git_log` with the `--since` parameter to scope the commits.

**Option C: Commit-based**
If the user provides a starting commit hash, use that as the session boundary.

**Option D: Automatic**
If no boundary is specified, default to the last 8 hours of work or the current branch's divergence from main, whichever captures more relevant changes.

Use `git_log` to retrieve the list of commits within the determined range. Store the starting commit reference for use in subsequent steps.

## Step 2: Collect Commit History

Run `git_log` with the appropriate range to get all commits made during the session. For each commit, extract:

- Commit hash (abbreviated)
- Author
- Timestamp
- Subject line
- Body (if present)

Sort commits chronologically (oldest first) to tell the story of the session in order.

If there are no commits in the range, note this and check for uncommitted changes instead. A session with only uncommitted work is still worth recapping.

## Step 3: Categorize Changes

Use `git_diff` with the session range to get the full diff. Also run `git_diff` against the working tree to capture uncommitted changes.

Categorize all changes into the following groups:

### New Files Created
Use the diff to identify files with the "new file" status. For each new file:
- File path
- Brief description of purpose (infer from filename, directory, and contents)
- Approximate size (lines of code)

### Files Modified
For each modified file:
- File path
- Nature of the change (e.g., "added new function," "refactored error handling," "updated configuration")
- Lines added and removed

### Files Deleted
For each deleted file:
- File path
- Reason for deletion if discernible from commit messages

### Configuration Changes
Separately highlight changes to configuration files, CI/CD pipelines, dependency manifests, and similar infrastructure files. These often have outsized impact relative to their diff size.

## Step 4: Summarize Significant Changes

For each commit or logical group of changes, write a one-sentence summary. Focus on the intent and impact rather than the mechanical details.

Guidelines for good summaries:
- Use active voice: "Added authentication middleware" not "Authentication middleware was added"
- Include the why when it is not obvious: "Switched from JSON to TOML config to support nested structures"
- Mention breaking changes explicitly
- Group related commits: if three commits all relate to "adding user registration," combine them into one summary point

Aim for 5-15 summary points for a typical session. If there are more than 15 significant changes, group them into subsections by feature or area of the codebase.

## Step 5: Check Pending Tasks

Query the eMCP task server using `task_list` to find tasks that were created or modified during the session.

For each relevant task:
- Task ID and title
- Current status (done, in-progress, blocked, pending)
- Whether it was created, completed, or updated during this session

If no task server is available, skip this step silently.

## Step 6: Gather Decisions from Memory

Use `search_nodes` to search the eMCP memory graph for entries related to decisions, trade-offs, or architectural choices made during the session.

Common patterns to search for:
- Nodes tagged with "decision" or "rationale"
- Nodes created within the session time window
- Nodes referencing the current branch or feature

For each decision found:
- What was decided
- What alternatives were considered
- Why this option was chosen

If no memory server is available or no decisions are recorded, check commit messages for decision context (messages often contain reasoning after a blank line in the body).

## Step 7: Identify Unfinished Work

Check for signs of incomplete work:

### Uncommitted Changes
Run `git_status` to identify:
- Modified files not yet committed
- Untracked files that may need to be added
- Staged changes not yet committed

### Failing Tests
Run `test_run` to execute the test suite. Report:
- Total tests, passed, failed, skipped
- Names of failing tests with brief failure reasons
- Whether failures are pre-existing or introduced during this session

### TODO Comments
Search for TODO, FIXME, HACK, and XXX comments that were added during the session. Use `git_diff` to find only newly-added instances (lines starting with `+` that contain these markers).

For each new TODO:
- File and line number
- The TODO text
- Whether it blocks the current feature

### Incomplete Features
Look for partially implemented functions, empty test bodies, placeholder values, or commented-out code blocks in the diff. These indicate work that was started but not finished.

## Step 8: Run Tests and Report State

Execute the test suite using `test_run` (if not already done in Step 7). Capture:

- Test framework and command used
- Total number of tests
- Pass count
- Fail count
- Skip count
- Execution time
- Any tests that were added during this session

If tests cannot be run (no test framework configured, compilation errors, etc.), report the reason.

## Step 9: Format the Session Recap

Assemble the recap into a structured document. Use the following format:

```markdown
# Session Recap

**Date**: <YYYY-MM-DD>
**Branch**: <current branch name>
**Duration**: <approximate session duration or commit range>
**Commits**: <number of commits in the session>

## Completed

- <Summary point 1>
- <Summary point 2>
- <Summary point 3>
...

## Changes

### New Files
| File | Purpose |
|------|---------|
| <path> | <description> |

### Modified Files
| File | Change |
|------|--------|
| <path> | <description> |

### Deleted Files
| File | Reason |
|------|--------|
| <path> | <description> |

**Stats**: <N> files changed, <M> insertions, <K> deletions

## Decisions

- **<Decision topic>**: <What was decided>. <Why this was chosen over alternatives>.
...

## Remaining

- [ ] <Unfinished item 1>
- [ ] <Unfinished item 2>
- [ ] <TODO or FIXME that needs attention>
...

## State

- **Tests**: <X>/<Y> passing (<Z> failing, <W> skipped)
- **Uncommitted changes**: <Yes/No> (<list of files if yes>)
- **Branch status**: <ahead/behind remote, or no remote tracking>
```

Omit any section that has no content (e.g., if no decisions were recorded, omit the Decisions section). Do not include empty sections.

## Step 10: Deliver the Recap

Present the formatted recap directly in the conversation.

If the user requests it, also write the recap to a file:
- Default location: `.session-recaps/<YYYY-MM-DD>-<branch-name>.md`
- Create the directory if it does not exist using `create_directory`
- Use `write_text` to save the file
- Add `.session-recaps/` to `.gitignore` if not already present (session recaps are personal artifacts, not project files)

If the user wants to append to an existing session log, read the existing file first with `read_text`, then write the combined content.

## Handling Edge Cases

- **No commits in session**: Focus on uncommitted changes, task updates, and decisions. Note that no commits were made.
- **Very large sessions** (50+ commits): Group changes by feature or directory rather than listing every file individually. Provide a high-level summary with an option to expand details.
- **Multiple branches**: If the user switched branches during the session, recap each branch separately or ask which branch to focus on.
- **Merge commits**: When summarizing, collapse merge commits into their feature description rather than listing individual commits from the merged branch.
- **Pair programming or mob sessions**: If multiple authors appear in the commits, note all contributors in the recap header.

## Quality Checklist

Before presenting the recap, verify:

1. Every commit in the range is accounted for in the summary
2. File change counts match between the diff stats and the tables
3. No sensitive information (credentials, tokens) appears in the recap
4. The recap is readable by someone who was not present during the session
5. Remaining items are actionable (specific enough to act on)

## Related Skills

- **context-export** (eskill-intelligence): Follow up with context-export after this skill to package the session recap for use in future sessions.
- **retrospective-report** (eskill-meta): Follow up with retrospective-report after this skill to analyze patterns across multiple session recaps.
