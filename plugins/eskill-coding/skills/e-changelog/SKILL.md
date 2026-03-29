---
name: e-changelog
description: "Generates a changelog from git history between two refs or date ranges. Use when producing release notes for a tag, summarizing commits between versions, or diffing work across sprints. Also applies when: 'generate changelog', 'what changed since last release', 'release notes from commits'."
---

# Changelog Generation

This skill produces structured changelogs by reading git commit history, categorizing entries by conventional commit type, and formatting the output in a standard changelog format.

## Prerequisites

- A git repository with commit history.
- Optionally, tags or date ranges to scope the changelog window.

## Workflow

### Step 1: Determine the Range

Identify the commit range to include in the changelog. The range is one of:

- **Two tags**: e.g., `v1.2.0..v1.3.0`. Use when generating notes for a specific release.
- **Tag to HEAD**: e.g., `v1.3.0..HEAD`. Use when preparing notes for an upcoming release.
- **Date range**: e.g., `--since=2025-01-01 --until=2025-02-01`. Use when summarizing work over a time period.

If no range is provided, default to the last tag to HEAD. If no tags exist, use the full history.

To find the latest tag:

```
git_log with --tags --simplify-by-decoration to find recent tags
```

### Step 2: Collect Commits

Use the `git_log` tool from the eMCP git server to retrieve commits within the determined range.

Request the following fields for each commit:
- Hash (abbreviated)
- Subject line
- Body (if present)
- Author name
- Date

Filter out merge commits unless they carry meaningful information (e.g., squash merges with detailed bodies).

### Step 3: Categorize Commits by Conventional Commit Type

Parse each commit subject line against the conventional commits specification. The expected format is:

```
<type>[optional scope]: <description>
```

Recognized types and their changelog sections:

| Type       | Changelog Section     |
|------------|-----------------------|
| feat       | Added                 |
| fix        | Fixed                 |
| chore      | Maintenance           |
| refactor   | Changed               |
| docs       | Documentation         |
| test       | Testing               |
| perf       | Performance           |
| ci         | CI/CD                 |
| build      | Build                 |
| breaking   | Breaking Changes      |

Check for `BREAKING CHANGE:` in the commit body or `!` after the type as indicators of breaking changes. Breaking changes should be listed in their own section regardless of the commit type.

### Step 4: Format Entries

For each category, produce entries in the following format:

```
- <short hash> <subject line> (<author>)
```

If the commit body contains additional context that is useful for release notes, include it as indented text below the entry:

```
- a1b2c3d Add user authentication via OAuth2 (Alice)
  Supports Google and GitHub providers. Adds new environment variables
  for client credentials.
```

### Step 5: Handle Edge Cases

**No conventional commits found**: If fewer than 20% of commits follow the conventional format, fall back to grouping by file area. Use the primary directory of changed files to create sections (e.g., "API Changes", "Frontend Changes", "Infrastructure").

**Merge commits**: Skip standard merge commits (those matching `Merge branch '...'` or `Merge pull request #...`). However, retain squash-merge commits if they contain a meaningful subject and body.

**Empty ranges**: If the range contains no commits, report that no changes were found for the specified range.

**Commits with multiple types**: Use the primary type from the subject line. If the body references additional types, the commit appears only once under its primary type.

### Step 6: Output in Changelog Format

Produce output following the Keep a Changelog format (https://keepachangelog.com/):

```markdown
# Changelog

## [1.3.0] - 2025-03-15

### Breaking Changes
- d4e5f6a Remove deprecated /v1/users endpoint (Bob)
  Clients must migrate to /v2/users before upgrading.

### Added
- a1b2c3d Add user authentication via OAuth2 (Alice)
- b2c3d4e Add rate limiting to public API (Charlie)

### Fixed
- c3d4e5f Fix race condition in session cleanup (Alice)
- e5f6a7b Fix incorrect timezone handling in scheduler (Dave)

### Changed
- f6a7b8c Refactor database connection pooling (Bob)

### Performance
- 1a2b3c4 Optimize image processing pipeline (Charlie)
  Reduces average processing time by 40%.

### Documentation
- 2b3c4d5 Update API documentation for v2 endpoints (Eve)

### Maintenance
- 3c4d5e6 Update CI pipeline to Node 20 (Dave)
```

If the user requests a different format (e.g., plain text, JSON, or a project-specific template), adapt the output accordingly while preserving the same categorization logic.

## Conventional Commits Reference

The conventional commits specification (https://www.conventionalcommits.org/) defines the following structure:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Common footers include:
- `BREAKING CHANGE: <description>` -- indicates a breaking API change
- `Refs: #<issue>` -- references an issue
- `Reviewed-by: <name>` -- review attribution

This skill relies on authors following this convention. When commits do not follow it, the fallback grouping-by-file-area strategy ensures useful output regardless.

## Edge Cases

- **Squash-merged PRs**: Squash merges collapse multiple commits into one, losing the individual commit types. Use PR titles or labels as a fallback when commit messages lack detail.
- **Non-conventional commit messages**: When most commits do not follow conventional commit format, the categorization heuristic must fall back to file-path grouping (e.g., changes to `test/` go under Testing).
- **Merge commits and reverts**: Merge commits should be excluded from changelog entries. Reverts should cancel out the original commit's entry if both fall within the same ref range.
- **Empty ref ranges**: When the two refs are identical or no commits exist between them, report an empty changelog rather than failing.
- **Monorepo with package-scoped changelogs**: Some monorepos maintain a changelog per package. Scope entries by the changed package path and produce per-package output when detected.

## Related Skills

- **e-release** (eskill-devops): Follow up with e-release after this skill to include the generated changelog in the release process.
- **e-keeplog** (eskill-meta): Follow up with e-keeplog after this skill to integrate generated entries into the project changelog file.
