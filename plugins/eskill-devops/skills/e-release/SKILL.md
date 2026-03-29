---
name: e-release
description: "Manages the release process: version bump, version file updates, tag creation, and release commit. Use when cutting a new release, bumping the version number, or tagging a release candidate. Also applies when: 'bump the version', 'cut a release', 'prepare a new version', 'tag a release'."
---

# Release Workflow

This skill manages the end-to-end release process for a project. It determines the current version, calculates the next version based on conventional commits, updates version references across the codebase, generates changelog entries, and prepares the release commit and tag. It never pushes or publishes automatically; all remote operations are left to the user.

## Prerequisites

- A git repository with at least one tagged or recorded version.
- Version files in the project (package.json, pyproject.toml, Cargo.toml, version.txt, or equivalent).
- The eMCP filesystem, shell, and data_file_read servers available.

## Step 1: Determine Current Version

Read the current version from the project's configuration files.

- Use `data_file_read` to read the version from the appropriate file based on project type:
  - Node.js: read the `version` field from `package.json`.
  - Python: read the `version` field from `pyproject.toml` under `[project]` or `[tool.poetry]`, or read `__version__` from `__init__.py`, or read `version.txt`.
  - Rust: read the `version` field from `Cargo.toml` under `[package]`.
  - Go: check for a `VERSION` file, or read the latest git tag.
  - Java: read the `<version>` element from `pom.xml`, or `version` from `build.gradle`.
  - Generic: check for `VERSION`, `version.txt`, or `.version` files in the project root.

- Parse the version string and validate it follows semantic versioning (MAJOR.MINOR.PATCH).
- If the version contains a pre-release suffix (e.g., `-alpha.1`, `-rc.1`), note this in the output.
- If no version can be found, fall back to reading the latest git tag that matches a version pattern (e.g., `v*.*.*`).
- Report the current version to the user before proceeding.

## Step 2: Determine Version Bump Type

Analyze the commit history since the last release to determine whether the next version should be a major, minor, or patch bump.

- Use `git_log` to retrieve all commits since the last version tag.
- Parse each commit message according to the Conventional Commits specification:
  - `feat:` or `feat(scope):` indicates a new feature (triggers minor bump).
  - `fix:` or `fix(scope):` indicates a bug fix (triggers patch bump).
  - `BREAKING CHANGE:` in the commit footer, or `!` after the type/scope (e.g., `feat!:`) indicates a breaking change (triggers major bump).
  - `docs:`, `chore:`, `style:`, `refactor:`, `perf:`, `test:`, `ci:` are non-release commits but should still appear in the changelog under their respective categories.

- Apply the highest applicable bump:
  - If any commit contains a breaking change, the bump is MAJOR.
  - Otherwise, if any commit is a `feat`, the bump is MINOR.
  - Otherwise, if any commit is a `fix`, the bump is PATCH.
  - If no feat or fix commits exist, default to PATCH and inform the user that only non-functional changes were detected.

- Allow the user to override the calculated bump type. Present the calculation and ask for confirmation.

## Step 3: Calculate New Version Number

Compute the new version by applying the bump to the current version.

- For a PATCH bump: increment the third segment (e.g., 1.2.3 becomes 1.2.4).
- For a MINOR bump: increment the second segment and reset the third to zero (e.g., 1.2.3 becomes 1.3.0).
- For a MAJOR bump: increment the first segment and reset the second and third to zero (e.g., 1.2.3 becomes 2.0.0).
- If the current version has a pre-release suffix, handle it according to semver rules:
  - Bumping from a pre-release (e.g., 2.0.0-rc.1) to a release: strip the pre-release suffix (becomes 2.0.0).
  - The user may also request a pre-release version (e.g., 2.0.0-rc.1, 2.0.0-beta.1).

Present the version transition to the user: `Current: X.Y.Z -> New: A.B.C` and wait for confirmation before proceeding to file modifications.

## Step 4: Update Version in Project Files

Update the version string in all relevant project files.

- Node.js:
  - Update `version` in `package.json`.
  - Update `version` in `package-lock.json` (both the root `version` and the entry under `packages.""`).
  - If a `yarn.lock` exists, note that it does not contain version numbers and needs no update.

- Python:
  - Update `version` in `pyproject.toml` under the appropriate section.
  - Update `__version__` in any `__init__.py` or `_version.py` file if one exists.
  - Update `version.txt` if it exists.

- Rust:
  - Update `version` in `Cargo.toml` under `[package]`.
  - Run `cargo update --workspace` via shell to update `Cargo.lock`.

- Go:
  - Update `VERSION` file if it exists.
  - Version is primarily tracked via git tags in Go projects.

- Java:
  - Update `<version>` in `pom.xml`.
  - Or update `version` in `build.gradle` / `build.gradle.kts`.

- Generic:
  - Update any `VERSION`, `version.txt`, or `.version` files found in the project root.

Search for additional files that may contain version references that need updating:
- `sonar-project.properties` (sonar.projectVersion)
- `docker-compose.yml` (image tags referencing the project version)
- Documentation files that reference the current version in installation instructions

For each file modified, record the change (old value to new value) for inclusion in the review step.

## Step 5: Generate Changelog Entries

Create structured changelog entries from the commit history since the last tag.

- Use `git_log` to retrieve all commits since the last version tag.
- Parse each commit message and categorize it:
  - **Breaking Changes**: commits with `BREAKING CHANGE` or `!` marker.
  - **Features**: commits with `feat` type.
  - **Bug Fixes**: commits with `fix` type.
  - **Performance Improvements**: commits with `perf` type.
  - **Documentation**: commits with `docs` type.
  - **Other Changes**: commits with `refactor`, `style`, `chore`, `test`, `ci`, or `build` types.

- For each entry, include:
  - The commit subject line (first line of the commit message).
  - The scope in parentheses if present (e.g., `**auth**: add OAuth2 support`).
  - The short commit hash as a reference.

- Group entries by category and sort them alphabetically within each group.
- Omit categories that have no entries.
- Format the entries in standard Keep a Changelog format.

## Step 6: Update CHANGELOG.md

Insert the generated changelog entries into the project's CHANGELOG.md file. Use `markdown_read_section` to extract the current `[Unreleased]` section for reference before modifying.

- If `CHANGELOG.md` exists, read it and insert the new version section at the top, after the file header but before previous version entries.
- If `CHANGELOG.md` does not exist, create it with a standard header:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
```

- The new version section should follow this format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Breaking Changes

- Description of breaking change (commit-hash)

### Features

- Description of feature (commit-hash)

### Bug Fixes

- Description of fix (commit-hash)
```

- Update the comparison links at the bottom of the CHANGELOG.md if they exist (e.g., `[X.Y.Z]: https://github.com/org/repo/compare/vA.B.C...vX.Y.Z`).

## Step 7: Review All Changes

Before committing, review every modification to ensure correctness.

- Use `diff_files` or `diff_text` to compare the original and modified versions of each changed file.
- Present a summary of all changes to the user:
  - List each file that was modified.
  - Show the specific version string changes.
  - Show the changelog additions.
- Verify that no unintended changes were introduced.
- Verify that the version string is consistent across all updated files.
- If any inconsistency is found, correct it before proceeding.

This step is essential. Version mismatches across files are a common source of release problems.

## Step 8: Present Release Summary for Confirmation

Before performing any git operations, present a complete release summary to the user and wait for explicit confirmation.

The summary should include:

```
## Release Summary

**Version**: X.Y.Z -> A.B.C
**Bump Type**: major/minor/patch
**Date**: YYYY-MM-DD

### Files Modified
- path/to/package.json (version: "X.Y.Z" -> "A.B.C")
- path/to/CHANGELOG.md (new section added)
- [list all modified files]

### Changelog Preview
[Show the changelog entries that will be added]

### Commits Included
[List all commits being released with their short hashes and subject lines]

### Next Steps (after confirmation)
1. Stage all modified files
2. Commit with message "release: vA.B.C"
3. Create git tag vA.B.C

Proceed? (The user must confirm before any git operations are performed.)
```

Do not proceed until the user explicitly confirms. This is the last opportunity to catch any issues before the release commit is created.

## Step 9: Create Release Commit and Tag

After user confirmation, perform the git operations to finalize the release.

- Stage all modified files using `git_add`:
  - The version files (package.json, pyproject.toml, etc.)
  - CHANGELOG.md
  - Lock files (package-lock.json, Cargo.lock, etc.)
  - Any other files that were modified in Step 4.

- Create a commit with the message: `release: vA.B.C`
  - The commit message should follow the project's conventional commit format.
  - The commit body may optionally include a summary of the changes.

- Create an annotated git tag: `git tag -a vA.B.C -m "Release vA.B.C"`
  - Use an annotated tag (not a lightweight tag) so that it includes the tagger, date, and message.
  - The tag message should include a brief summary or the changelog entries for this version.

- Verify the tag was created by running `git tag -l "vA.B.C"` and `git log --oneline -1`.

## Step 10: Generate Release Notes

Produce formatted release notes that can be used for the GitHub/GitLab release page.

- Compile the release notes from the changelog entries generated in Step 5.
- Add a header with the version number and release date.
- Include a "Highlights" section at the top summarizing the most important changes in one or two sentences.
- Include the full categorized changelog.
- Add an "Upgrade Guide" section if there are breaking changes, explaining what users need to change.
- Add a "Contributors" section listing unique commit authors for this release (from `git_log`).
- Format the release notes in GitHub-flavored Markdown.

Present the release notes to the user. These can be used when creating a release on GitHub/GitLab.

## Important Safeguards

- This skill never pushes to a remote repository. All operations are local.
- This skill never publishes to a package registry (npm, PyPI, crates.io, etc.).
- After creating the release commit and tag, present the user with the commands they would run to push:
  - `git push origin main` (or the appropriate branch)
  - `git push origin vA.B.C` (to push the tag)
  - Or `git push origin main --tags` (to push both)
- The user decides when and how to push and publish.
- If the user wants to undo the release: provide the commands to reset the commit and delete the tag:
  - `git reset --soft HEAD~1` (undo the commit but keep changes staged)
  - `git tag -d vA.B.C` (delete the local tag)

## Notes

- Always use semantic versioning unless the project explicitly uses a different versioning scheme.
- Conventional Commits are the recommended commit message format for automated changelog generation.
- If the project does not use conventional commits, fall back to listing all commit subjects without categorization.
- For monorepos with multiple packages, the release process may need to be run per-package with independent version numbers.
- Pre-release versions (alpha, beta, rc) follow semver pre-release rules and should not appear in the main CHANGELOG.md section.

## Edge Cases

- **Multiple version files out of sync**: Monorepos or projects with both package.json and a version.txt may have divergent version numbers. Detect all version sources and flag mismatches before bumping.
- **Pre-release versions**: Versions like `1.2.0-beta.3` follow different bumping rules than stable releases. Increment the pre-release segment rather than the minor/patch version when staying in pre-release.
- **No conventional commits**: When commit messages do not follow conventional commits, automatic version bump detection fails. Fall back to manual version selection with the user.
- **Version locked by external system**: Some projects have versions controlled by a CI variable, release branch name, or external build system rather than a committed file. Detect and defer to the external source.
- **Unsigned tags in a GPG-required repo**: If the repository requires signed tags, a plain `git tag` will be rejected. Check for tag signing configuration before creating the tag.

## Related Skills

- **e-changelog** (eskill-coding): Run e-changelog before this skill to prepare release notes from commit history.
- **e-deploy** (eskill-devops): Follow up with e-deploy after this skill to execute the deployment steps for the new release.
- **e-prune** (eskill-coding): Follow up with e-prune after this skill to remove release branches that are no longer needed.
