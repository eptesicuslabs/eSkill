---
name: backup-workflow
description: "Creates timestamped, checksummed backups of project files and databases with manifest tracking. Use when backing up before risky changes, creating release archives, or managing backup rotation. Also applies when: 'back up my project', 'save a snapshot before refactor', 'archive this release', 'create a backup', 'safe copy before deploy'."
---

# Backup Workflow

Create reliable, verified backups of project files and databases. This skill produces timestamped archives with checksums, manifest files for traceability, integrity verification, and rotation management. It emphasizes safety and user control -- old backups are never deleted automatically.

## Principles

- Every backup must be verifiable. A checksum is computed and stored alongside the archive.
- Every backup must be auditable. A manifest records exactly what was included, when, and why.
- Deletion of old backups is never automatic. The skill identifies candidates for removal but the user makes the final decision.
- The backup process is non-destructive. It only reads source files and writes to the backup destination.

## Step 1: Define Backup Scope

Determine what needs to be backed up. The scope can be specified by the user or inferred from the project structure.

### Project Directory Backup

The most common case: back up the entire project directory. Identify the project root (typically the directory containing `.git/`, `package.json`, or similar markers).

Default inclusions:
- All source code files.
- Configuration files (package.json, tsconfig.json, Dockerfile, docker-compose.yml, etc.).
- Documentation files.
- Test files and fixtures.
- Lock files (package-lock.json, yarn.lock, etc.).

Default exclusions (these are typically regenerable and large):
- `node_modules/` -- can be restored with `npm install`.
- `.git/` -- the git history itself is usually backed up via remote repositories; including it makes archives very large.
- `dist/`, `build/`, `out/` -- build output directories.
- `.next/`, `.nuxt/`, `.svelte-kit/` -- framework cache directories.
- `__pycache__/`, `*.pyc` -- Python bytecode cache.
- `.venv/`, `venv/`, `env/` -- Python virtual environments.
- `target/` -- Rust/Java build output.
- `.cache/`, `.parcel-cache/` -- build caches.
- `*.log` -- log files (unless specifically requested).
- `.env` -- environment files with secrets (warn the user if included).

### Specific Subdirectory Backup

The user may request backup of specific subdirectories (e.g., `src/`, `config/`, `data/`). In this case, only the specified paths are included.

### Database File Backup

If the project uses file-based databases, include them:
- SQLite databases (`.sqlite`, `.sqlite3`, `.db` files).
- LevelDB directories.
- Other embedded database files.

## Step 2: List Files to Include

Use the filesystem tools (`list_dir`, `tree`) to enumerate all files within the backup scope. Apply the inclusion and exclusion rules from Step 1.

Additionally, check for a `.gitignore` file in the project root. Parse its patterns and apply them as exclusions. Files ignored by git are typically generated or temporary and do not need to be backed up.

If a `.backupignore` file exists in the project root, also parse and apply its patterns. This allows projects to define backup-specific exclusions separate from git exclusions.

Record the complete file list with relative paths and sizes. Compute the total size of all files to be included. Report this to the user before proceeding:

```
Backup scope:
  Files: 1,247
  Total size: 45.3 MB
  Largest files:
    - data/sample.json (12.1 MB)
    - assets/hero-image.png (3.4 MB)
```

If the total size exceeds 500 MB, warn the user and ask for confirmation before proceeding. Very large backups may take significant time and disk space.

## Step 3: Create the Archive

Use `archive_create` to produce the backup archive. Apply the following naming convention:

```
<project-name>-backup-<YYYY-MM-DD>-<HHMMSS>.<format>
```

For example: `my-project-backup-2025-01-15-143022.tar.gz`.

Use the backup destination directory specified by the user, or default to a `backups/` directory in the project root. Create the directory if it does not exist.

Supported archive formats:
- `.tar.gz` (gzip-compressed tar) -- preferred for Unix-like systems, good compression.
- `.zip` -- preferred when cross-platform compatibility with Windows is needed.
- `.tar.zst` (Zstandard-compressed tar) -- if available, offers better compression ratios and speed.

Choose the format based on the platform and user preference. Default to `.tar.gz` on Linux/macOS and `.zip` on Windows unless the user specifies otherwise.

Include the full relative path structure within the archive so that extraction recreates the original directory layout.

## Step 4: Generate Checksum

After the archive is created, compute its cryptographic hash using `crypto_hash_file`. Use SHA-256 as the default algorithm.

Record the checksum value. This will be written to both the manifest file and optionally to a separate `.sha256` sidecar file alongside the archive:

```
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  my-project-backup-2025-01-15-143022.tar.gz
```

The sidecar file allows verification using standard tools (`sha256sum -c` on Linux, `Get-FileHash` on PowerShell).

## Step 5: Write Manifest File

Create a manifest file alongside the backup archive. Use the naming convention:

```
<project-name>-backup-<YYYY-MM-DD>-<HHMMSS>.manifest.json
```

The manifest should contain:

```json
{
  "backup": {
    "name": "<project-name>-backup-<YYYY-MM-DD>-<HHMMSS>",
    "created": "<ISO 8601 timestamp>",
    "project": "<project directory name>",
    "source": "<absolute path to project root>",
    "destination": "<absolute path to backup directory>",
    "archive": "<archive filename>",
    "format": "tar.gz",
    "checksum": {
      "algorithm": "SHA-256",
      "value": "<hash>"
    },
    "stats": {
      "file_count": 1247,
      "total_size_bytes": 47500288,
      "archive_size_bytes": 15234567,
      "compression_ratio": "3.12:1"
    },
    "exclusions": [
      "node_modules/",
      ".git/",
      "dist/"
    ],
    "notes": "<user-provided notes or empty>"
  }
}
```

The manifest provides a complete record of the backup for future reference. It enables verification, restoration, and auditing without needing to inspect the archive contents.

## Step 6: Verify Archive Integrity

After creating the archive, verify its integrity by listing its contents using `archive_list`. Compare the file list from the archive against the original file list from Step 2:

- Verify that the file count matches.
- Spot-check several files to ensure their paths are correct within the archive.
- Verify that no unexpected files were included (e.g., files that should have been excluded).

If any discrepancy is found, report it as an error and warn the user that the backup may be incomplete or corrupted. Do not delete the archive in this case; let the user decide what to do.

Also verify the archive size is reasonable. An archive that is 0 bytes or suspiciously small (less than 1% of the source size) likely indicates a failure.

## Step 7: Database Backup Procedures

If the backup scope includes database files, apply additional handling:

### SQLite Databases

SQLite files require special attention because backing up a database file while it is actively being written can produce a corrupted backup. Use one of these approaches:

1. **File copy with WAL checkpoint**: If the database uses WAL (Write-Ahead Logging) mode, the WAL file and shared-memory file must be included alongside the main database file. Copy all three: `.db`, `.db-wal`, `.db-shm`.
2. **SQL dump**: Use `sqlite3 <database> .dump` via `run_command` to produce a SQL text dump. This is safer for active databases as SQLite handles locking internally during the dump. Save the dump as `<database-name>.sql` and include it in the archive.
3. **Backup API**: If the SQLite backup API is accessible, use it for an online backup. This is the safest method but requires tool support.

Recommend the SQL dump approach for active databases and the file copy approach for databases that are not currently in use.

### Other Database Files

For LevelDB, RocksDB, or similar embedded databases, the safest approach is to ensure the application is not writing to the database during backup. If this cannot be guaranteed, note the risk in the manifest.

## Step 8: Rotation Management

Check the backup destination directory for existing backups. Identify all files matching the backup naming pattern for this project.

List existing backups sorted by date, newest first:

```
Existing backups for my-project:
  1. my-project-backup-2025-01-15-143022.tar.gz  (15 MB, today)
  2. my-project-backup-2025-01-14-090000.tar.gz  (14 MB, 1 day ago)
  3. my-project-backup-2025-01-10-120000.tar.gz  (14 MB, 5 days ago)
  4. my-project-backup-2025-01-01-080000.tar.gz  (13 MB, 14 days ago)
  5. my-project-backup-2024-12-15-100000.tar.gz  (12 MB, 31 days ago)
```

If the user has specified a retention count (e.g., keep the last 5 backups), identify which backups exceed that count. Present the list of candidates for removal:

```
Retention policy: keep last 5 backups.
No backups exceed the retention count. All backups will be retained.
```

Or, if there are excess backups:

```
Retention policy: keep last 3 backups.
Candidates for removal (user approval required):
  - my-project-backup-2025-01-01-080000.tar.gz (13 MB)
  - my-project-backup-2024-12-15-100000.tar.gz (12 MB)
Total reclaimable space: 25 MB
```

**Important**: Never delete old backups automatically. Always present the rotation candidates and explicitly ask the user for confirmation before any deletion. Data loss from premature backup deletion is irreversible.

## Step 9: Report Backup Summary

Present the final backup summary to the user:

```
## Backup Complete

| Property          | Value                                          |
|-------------------|------------------------------------------------|
| Archive           | my-project-backup-2025-01-15-143022.tar.gz     |
| Location          | /home/user/projects/my-project/backups/        |
| Files included    | 1,247                                          |
| Source size       | 45.3 MB                                        |
| Archive size      | 15.2 MB                                        |
| Compression       | 3.12:1                                         |
| Checksum (SHA-256)| e3b0c44...b855                                 |
| Manifest          | my-project-backup-2025-01-15-143022.manifest.json |
| Verification      | PASSED (file count matches, checksum valid)    |
```

Include any warnings or issues encountered during the process:

- Files that could not be read (permission denied).
- Very large files that dominated the archive size.
- Database files that were backed up while potentially in use.
- Disk space warnings if the backup destination is running low.

## Additional Considerations

### Incremental Backups

This skill creates full backups by default. For projects that change frequently and have large file counts, suggest an incremental approach:

- Use git to identify files changed since the last backup (if the project is a git repository).
- Compare file modification times against the timestamp of the last backup manifest.
- Create a smaller archive containing only changed files, with a reference to the base backup.

Incremental backups are more complex to restore but significantly reduce storage requirements for frequent backups.

### Encryption

If the backup contains sensitive data, recommend encrypting the archive. Note that this skill does not perform encryption directly, but the user can apply encryption after creation using standard tools (GPG, age, or platform-specific encryption).

### Remote Storage

After creating a local backup, the user may want to copy it to remote storage (cloud storage, NAS, etc.). This skill does not handle remote transfers, but the archive and manifest are designed to be portable. Suggest appropriate transfer methods based on the platform.

## Related Skills

- **file-integrity** (eskill-quality): Follow up with file-integrity after this skill to verify backup checksums and confirm data integrity.
- **disaster-recovery-plan** (eskill-devops): Follow up with disaster-recovery-plan after this skill to document the backup procedures in the recovery plan.
