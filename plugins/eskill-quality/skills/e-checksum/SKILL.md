---
name: e-checksum
description: "Creates and verifies SHA-256 checksum manifests to detect unauthorized or accidental file changes. Use when validating release artifacts, monitoring sensitive files, or establishing change-detection baselines. Also applies when: 'verify checksums', 'detect tampering', 'create manifest', 'file verification', 'integrity check'."
---

# File Integrity Verification

This skill creates checksum manifests for sets of project files and verifies them to detect unauthorized modifications, missing files, or unexpected additions. It supports both manifest creation and verification workflows.

## Prerequisites

- Files or directories to include in the checksum manifest.
- The eMCP filesystem, fs_info, crypto_encode, and shell servers available for file reading, metadata retrieval, and hash computation.
- An existing manifest file for verification workflows (not needed for initial creation).

## Step 1: Define the Scope

Determine which files to include in the integrity check based on the use case.

1. Accept a scope definition from the user, or default to one of these common profiles:
   - **Release artifacts**: contents of `dist/`, `build/`, `out/`, or other output directories.
   - **Configuration files**: all configuration files at the project root and in config directories (*.json, *.yml, *.yaml, *.toml, *.env, *.ini, *.conf).
   - **Source code**: all source files excluding dependencies and build output.
   - **Full project**: all files excluding `.git/`, `node_modules/`, `vendor/`, `__pycache__/`, and other standard exclusions.
   - **Custom**: a specific list of files or glob patterns provided by the user.
2. Define exclusion patterns for the chosen scope:
   - Always exclude `.git/` directory contents.
   - Exclude dependency directories: `node_modules/`, `vendor/`, `.venv/`, `venv/`, `target/` (Rust).
   - Exclude build output unless explicitly included in scope.
   - Exclude the manifest file itself to avoid circular references.
3. Record the scope definition (included patterns, excluded patterns) for inclusion in the manifest metadata.

## Step 2: Enumerate Files in Scope

Build the complete list of files to be checksummed.

1. Use `filesystem` `fs_list` with recursive traversal to enumerate all files in the scope directories.
2. Apply inclusion patterns: filter to files matching the defined glob patterns.
3. Apply exclusion patterns: remove files matching exclusion globs.
4. Sort the file list alphabetically by path (using forward slashes as separators) for deterministic ordering.
5. Record the total file count for the manifest metadata.
6. If the file list is empty, report an error: no files match the scope definition.
7. For very large file sets (more than 10,000 files), warn the user that the process may take time and suggest narrowing the scope.

## Step 3: Compute File Hashes

For each file in the enumerated list, compute a cryptographic hash.

1. Use `crypto_hash_file` with the SHA-256 algorithm for each file.
2. SHA-256 is the default because it provides strong collision resistance while being computationally efficient. If the user requests a different algorithm (SHA-512, BLAKE2), use that instead.
3. For each file, record:
   - Relative path from the project root (using forward slashes).
   - SHA-256 hash (hex-encoded). Use `crypto_encode` to convert hash output to alternate formats (base64, hex) when the manifest consumer requires a specific encoding.
   - File size in bytes and modification timestamp from `fs_info` (file metadata). Using `fs_info` provides precise file size, creation time, and modification time in a single call, which is more efficient than separate filesystem stat operations.
4. Handle errors gracefully:
   - Files that cannot be read (permissions issues): record as "error" with the reason.
   - Symbolic links: follow the link and hash the target file content. Record that the entry is a symlink.
   - Empty files: compute the hash of empty content (SHA-256 of empty string is a known constant: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`).

## Step 4: Build the Manifest

Assemble all collected data into a structured manifest.

1. The manifest contains:
   - **Metadata section**:
     - Manifest format version (e.g., "1.0").
     - Creation timestamp (ISO 8601 format).
     - Project root path.
     - Scope definition (inclusion and exclusion patterns).
     - Hash algorithm used.
     - Hash encoding format (hex or base64, as produced by `crypto_encode`).
     - Total file count.
     - Total size of all files in bytes.
     - Per-file metadata from `fs_info`: modification time, creation time, file permissions.
     - Generator identifier: "eskill-quality/e-checksum".
   - **Files section**:
     - An array of entries, each with: path, hash (encoded via `crypto_encode`), size, and file metadata from `fs_info` (modification time, permissions).
     - Sorted alphabetically by path.
2. Format the manifest as JSON for machine readability and easy parsing during verification.
3. Validate the manifest structure before writing: ensure no duplicate paths, all hashes are the correct length, all sizes are non-negative integers.

## Step 5: Write the Manifest

Persist the manifest to a file in the project.

1. Default manifest location: `.integrity-manifest.json` at the project root.
2. If the user specifies a different location, use that instead.
3. Use `filesystem` `fs_write` or equivalent to write the JSON manifest.
4. The manifest file should be human-readable (pretty-printed JSON with 2-space indentation).
5. Report the manifest file location and size to the user.
6. Recommend adding the manifest to version control so changes to it are tracked.
7. If a previous manifest exists at the target location, rename it to `.integrity-manifest.previous.json` before writing the new one, to preserve the baseline for comparison.

## Step 6: Verify Against an Existing Manifest

When verifying (rather than creating), compare the current file state against a previously created manifest.

1. Read the existing manifest using `data_file_read` to parse the JSON structure.
2. Validate the manifest format: check for required fields (metadata, files), correct data types, and supported format version.
3. Enumerate the current files in scope using the same scope definition stored in the manifest metadata.
4. For each file listed in the manifest:
   - Check if the file still exists on disk.
   - If it exists, compute its current SHA-256 hash using `crypto_hash_file`.
   - Compare the current hash against the stored hash.
5. Classify each file into one of the following states:
   - **Unchanged**: file exists and hash matches.
   - **Modified**: file exists but hash does not match.
   - **Missing**: file is in the manifest but no longer exists on disk.
6. Check for files that exist on disk within the scope but are not in the manifest:
   - **New**: file exists on disk but is not in the manifest.
7. Record a count for each state category.

## Step 7: Report Verification Results

Generate a clear report of the verification outcome.

### Overall Result

- **PASS**: no modified, missing, or new files detected. All hashes match.
- **FAIL**: one or more files are modified, missing, or new.

### Detailed Findings

For each category of change:

#### Modified Files

- File path.
- Expected hash (from manifest).
- Current hash (computed now).
- File size change (if applicable).
- These files have been altered since the manifest was created. Determine whether the change is authorized.

#### Missing Files

- File path.
- Expected hash (from manifest).
- These files existed when the manifest was created but are no longer present. Determine whether the deletion is authorized.

#### New Files

- File path.
- Current hash.
- Current size.
- These files were not present when the manifest was created. Determine whether the addition is authorized.

#### Unchanged Files

- Total count of unchanged files.
- Optionally list them (useful for small scopes, omit for large scopes).

### Summary Statistics

- Total files in manifest.
- Total files currently on disk (within scope).
- Unchanged count.
- Modified count.
- Missing count.
- New count.
- Verification timestamp.

## Step 8: Sign the Manifest

Add a cryptographic signature to the manifest for tamper detection.

1. After writing the manifest, compute an HMAC-SHA256 signature of the manifest content using `crypto_hmac`.
2. The HMAC key should be a project-specific secret:
   - Check for a key in an environment variable (e.g., `INTEGRITY_SIGNING_KEY`).
   - If no key is available, generate a suggestion for the user to set one, but do not create a key automatically (this is a security-sensitive operation).
3. Append the signature to the manifest file as a separate field (`"signature": "<hex-encoded HMAC>"`).
4. During verification, if a signature is present in the manifest:
   - Recompute the HMAC of the manifest content (excluding the signature field itself).
   - Compare the computed HMAC with the stored signature.
   - If they match: the manifest has not been tampered with.
   - If they do not match: the manifest itself has been modified, and the verification results cannot be trusted. Report this as a critical finding.
5. If no signing key is available during verification, skip signature validation but note in the report that the manifest's integrity was not cryptographically verified.

## Step 9: Output Summary

Present the final output to the user.

### For Manifest Creation

- Manifest file location.
- Total files included.
- Total size covered.
- Scope definition used.
- Whether the manifest was signed.
- Recommendation to commit the manifest to version control.

### For Verification

- Overall result: PASS or FAIL.
- Summary of changes by category.
- Detailed list of modified, missing, and new files.
- Signature verification result (if applicable).
- Recommendation for next steps based on findings.

## Reference: Common Use Cases

### Release Validation

Create a manifest of build output after a successful build. Before deployment, verify the manifest to confirm that the artifacts have not been altered between build and deploy.

Scope: `dist/**/*` or `build/**/*`.

### Configuration Monitoring

Create a manifest of all configuration files. Periodically verify to detect unauthorized changes to server configuration, environment files, or infrastructure definitions.

Scope: `*.json`, `*.yml`, `*.yaml`, `*.toml`, `*.env`, `*.conf`, `*.ini` at the project root and in config directories.

### Source Code Baseline

Create a manifest of source code after a security audit. Verify before subsequent audits to identify exactly what has changed since the last review.

Scope: `src/**/*`, `lib/**/*`, excluding test files if desired.

### Dependency Verification

Create a manifest of vendored dependencies (when using vendoring instead of a package manager). Verify to detect accidental or malicious modifications to vendored code.

Scope: `vendor/**/*` or `third_party/**/*`.

## Edge Cases

- **Line ending differences across platforms**: The same file may produce different checksums on Windows (CRLF) vs. Unix (LF). Normalize line endings before hashing or document the expected platform.
- **Symlinks in the manifest scope**: Symlinks can point to files outside the project or to targets that change. Hash the symlink target's content, not the symlink itself, and record whether the path is a symlink.
- **Empty files**: Empty files produce a valid SHA-256 hash (the hash of zero bytes). Include them in the manifest rather than skipping them, since an unexpected empty file is itself a change worth detecting.
- **Binary files with metadata changes**: Some binary formats (JPEG, PDF) embed timestamps or tool versions. A recompiled binary may differ in checksum without any meaningful content change. Document which binary files are expected to change.
- **Manifest file included in its own scope**: If the manifest file is inside the directory being checksummed, exclude it from the computation to avoid a chicken-and-egg problem.

## Related Skills

- **e-backup** (eskill-system): Run e-backup before this skill to establish baseline checksums that e-checksum can verify against.
- **e-release** (eskill-devops): Run this skill before e-release to confirm file integrity before cutting a release.
