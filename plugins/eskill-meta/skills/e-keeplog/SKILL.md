---
name: e-keeplog
description: "Maintains an existing CHANGELOG.md by adding entries, cutting releases, and validating format per Keep a Changelog. Use when appending a new change entry, preparing a release section, or initializing a changelog. Also applies when: update the changelog, add to changelog, cut a release, create CHANGELOG.md."
---

# Changelog Maintain

Manage CHANGELOG.md files following the Keep a Changelog (https://keepachangelog.com) specification. This skill handles initialization, entry addition, release preparation, and automated generation from git history.

## Prerequisites

- A project with a git repository (for git-based changelog generation).
- The eMCP filesystem and shell servers available for reading and writing CHANGELOG.md.
- An existing CHANGELOG.md file for add/cut operations, or a project root for initialization.

## Supported Operations

- **Initialize**: Create a new CHANGELOG.md with the standard header and structure
- **Add entry**: Add a single change entry to the [Unreleased] section
- **Generate from git**: Scan git history and produce changelog entries automatically
- **Cut release**: Move [Unreleased] entries into a new version section with today's date
- **Validate**: Check the changelog for formatting and structural correctness

Determine the operation from the user's request. If unclear, ask which operation they need.

## Step 1: Check for Existing Changelog

Use `fs_read` to attempt to read CHANGELOG.md from the project root. Also check for alternate names: CHANGELOG, CHANGES.md, HISTORY.md.

If no changelog file exists and the operation is anything other than "initialize," inform the user and offer to create one first.

If creating a new changelog, write the following header using `fs_write`:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

```

Then proceed with the requested operation.

## Step 2: Read and Parse the Current Changelog

Use `fs_read` to load the full contents of CHANGELOG.md. Then use `markdown_headings` to extract the structural outline.

Identify the following elements by parsing the content:

- **Header block**: Everything before the first version heading
- **Version sections**: Each `## [x.y.z]` or `## [Unreleased]` heading and its content
- **Category headings**: Level-3 headings within each version (### Added, ### Changed, etc.)
- **Entries**: Bullet points under each category
- **Link references**: The `[x.y.z]: <url>` references at the bottom of the file

Store this parsed structure in working memory so modifications can be made precisely.

## Step 3: Determine What to Add

Based on the user's request:

### For Adding Manual Entries

The user provides a description and optionally a category. Map the entry to one of the six standard categories (see Step 6). If the user does not specify a category, infer it from the description:

- Descriptions starting with "add," "new," "introduce" map to Added
- Descriptions starting with "change," "update," "modify" map to Changed
- Descriptions starting with "deprecate" map to Deprecated
- Descriptions starting with "remove," "delete," "drop" map to Removed
- Descriptions starting with "fix," "correct," "resolve" map to Fixed
- Descriptions mentioning "security," "vulnerability," "CVE" map to Security

If uncertain, ask the user to confirm the category.

### For Cutting a Release

Collect all entries currently under [Unreleased]. The user must provide the new version number. Validate that it follows semantic versioning (MAJOR.MINOR.PATCH). The release date defaults to today's date in YYYY-MM-DD format.

### For Generating from Git

Proceed to Step 5 for git-based generation.

## Step 4: Handle Release Cutting

When cutting a new release:

1. Read all content under the `## [Unreleased]` section
2. If the Unreleased section is empty, warn the user and ask whether to proceed with an empty release or cancel
3. Create a new version heading: `## [<version>] - <YYYY-MM-DD>`
4. Move all category headings and entries from Unreleased to the new version section
5. Leave the Unreleased section empty (but keep the heading)
6. Insert the new version section between the Unreleased heading and the previous latest version
7. Update the link references at the bottom of the file:
   - Add `[<version>]: <repo_url>/compare/v<prev_version>...v<version>`
   - Update the Unreleased link: `[Unreleased]: <repo_url>/compare/v<version>...HEAD`

If this is the first release, the version link should point to the tag directly rather than a comparison.

## Step 5: Generate Entries from Git History

Use the git eMCP tools to extract commit information:

1. Run `git_tags` to find the most recent version tag (e.g., v1.0.0, 1.0.0)
2. Run `git_log` with the range from the last tag to HEAD to get all commits since the last release
3. If no tags exist, get all commits or ask the user for a starting point

For each commit, extract:
- The commit message subject line
- The conventional commit prefix if present (feat, fix, chore, docs, refactor, perf, test, build, ci, style)
- Any breaking change indicators (BREAKING CHANGE footer or `!` after the type)

Filter out commits that should not appear in the changelog:
- Merge commits (unless they contain meaningful descriptions)
- Commits with prefixes: chore, ci, build, style, test (unless the user wants them)
- Commits that are purely internal refactoring (unless the user wants them)

## Step 6: Categorize Entries

Apply the Keep a Changelog categories strictly:

| Category       | Description                                 | Conventional Commit Prefixes |
|---------------|---------------------------------------------|------------------------------|
| **Added**     | New features                                | feat                         |
| **Changed**   | Changes in existing functionality           | refactor, perf               |
| **Deprecated**| Soon-to-be removed features                 | (manual only)                |
| **Removed**   | Now removed features                        | (manual only)                |
| **Fixed**     | Bug fixes                                   | fix                          |
| **Security**  | Vulnerability fixes                         | (manual or tagged)           |

## Step 7: Map Conventional Commit Prefixes

For repositories using conventional commits, apply this mapping:

- `feat:` or `feat(<scope>):` maps to **Added**
- `fix:` or `fix(<scope>):` maps to **Fixed**
- `refactor:` maps to **Changed**
- `perf:` maps to **Changed**
- `docs:` is excluded by default (documentation changes are internal)
- `test:` is excluded by default
- `chore:` is excluded by default
- `build:` is excluded by default
- `ci:` is excluded by default

For commits without conventional prefixes, attempt to infer the category from the commit message. If inference is uncertain, place the entry under **Changed** as a default.

Breaking changes (indicated by `!` or `BREAKING CHANGE` footer) should be prominently marked. Prepend "**BREAKING:**" to the entry text and ensure it appears first in its category.

## Step 8: Format Entries

Each changelog entry is a single bullet point. Formatting rules:

- Start with a hyphen and a space: `- `
- Begin the description with a capital letter
- Use imperative mood when possible ("Add feature" not "Added feature")
- Keep entries concise: one line, under 100 characters if possible
- Do not include commit hashes in the changelog (the compare links serve that purpose)
- If a commit references an issue, include it: `- Fix crash on startup ([#42](link))`
- Group related commits into a single entry when they represent one logical change

Example formatted entries:

```markdown
### Added
- Add user authentication with OAuth2 support
- Add rate limiting middleware for API endpoints

### Fixed
- Fix memory leak in connection pool under high concurrency
- Fix incorrect timezone handling in date parser ([#127](https://github.com/org/repo/issues/127))

### Changed
- **BREAKING:** Change configuration file format from YAML to TOML
- Improve query performance for large datasets
```

## Step 9: Write Updated Changelog

Reconstruct the full CHANGELOG.md content:

1. Write the header block (preserved from the original)
2. Write the [Unreleased] section (empty if a release was cut, or with new entries)
3. Write each version section in reverse chronological order (newest first)
4. Write the link references at the bottom

Use `fs_write` to write the complete file. Do not use partial writes or appends -- always write the full file to avoid corruption.

After writing, use `fs_read` to read the file back and confirm it was written correctly.

## Step 10: Validate the Changelog

Perform the following validation checks:

1. **Structure**: The file starts with `# Changelog` and contains `## [Unreleased]`
2. **Date format**: All release dates match YYYY-MM-DD (use regex validation)
3. **Version format**: All version numbers follow semantic versioning (MAJOR.MINOR.PATCH, with optional pre-release suffix)
4. **Ordering**: Versions are in reverse chronological order
5. **Categories**: Only the six standard categories are used (Added, Changed, Deprecated, Removed, Fixed, Security)
6. **Entry format**: All entries start with `- ` (hyphen space)
7. **Link references**: Each version has a corresponding link reference at the bottom
8. **No duplicates**: The same version number does not appear twice

Report any validation failures to the user with specific line numbers and descriptions of the issues.

## Keep a Changelog Format Reference

The canonical changelog format:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2024-03-15

### Added
- New feature description

### Fixed
- Bug fix description

## [1.0.0] - 2024-01-01

### Added
- Initial release features

[Unreleased]: https://github.com/org/repo/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/org/repo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/org/repo/releases/tag/v1.0.0
```

## Edge Cases

- **Empty Unreleased section**: When cutting a release with no entries, warn the user but allow it if they confirm
- **Pre-existing non-standard changelog**: Attempt to parse it, but warn the user about deviations from the standard format and offer to reformat
- **Monorepo changelogs**: If the project is a monorepo, each package may have its own CHANGELOG.md. Ask the user which package they are targeting
- **Amending a released version**: Do not modify released version sections. If the user needs to correct a released entry, add a note under the next Unreleased or advise them to use a patch release instead

## Related Skills

- **e-changelog** (eskill-coding): Run e-changelog before this skill to produce the entries that will be integrated into the changelog file.
- **e-release** (eskill-devops): Follow up with e-release after this skill to include the updated changelog in the next release.
