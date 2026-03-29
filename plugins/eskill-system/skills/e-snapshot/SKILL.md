---
name: e-snapshot
description: "Captures a timestamped record of OS, processes, disk, Docker state, and tool versions. Use when documenting a machine before upgrades, preparing a detailed bug report, or establishing a performance baseline. Also applies when: 'snapshot my system', 'what is running on this machine', 'system report', 'capture environment state', 'diagnostic dump'."
---

# System Snapshot

Capture a detailed point-in-time record of the entire system state. This skill collects hardware and OS information, running processes, disk utilization, environment variables, Docker container state, tool versions, and configuration files, then assembles everything into a timestamped, checksummed snapshot document.

## Prerequisites

- Shell access to run system inspection commands (uname, df, docker, etc.).
- The eMCP filesystem and shell servers available for gathering system state.
- A writable location to store the snapshot output file.

## Purpose

System snapshots serve multiple purposes:

- Documenting the state of a machine before making significant changes (OS upgrades, dependency updates, infrastructure migrations).
- Creating diagnostic reports to share with support teams or colleagues when troubleshooting.
- Establishing baselines for performance comparison (before/after analysis).
- Preparing detailed bug reports that include the full environment context.
- Auditing system configurations for security or compliance reviews.

### Step 1: Capture OS and Hardware Information

Use `sys_info` to retrieve the foundational system details:

- **Hostname**: The machine's network hostname.
- **Operating System**: Name, version, and build number (e.g., "Windows 11 Pro 10.0.26200", "macOS 14.2 Sonoma", "Ubuntu 22.04.3 LTS").
- **Kernel**: Kernel version on Linux, Darwin version on macOS.
- **Architecture**: CPU architecture (x64, arm64, etc.).
- **CPU**: Processor model, core count (physical and logical).
- **Memory**: Total installed RAM.
- **Node.js version**: The Node.js version powering the eMCP runtime.

Record each field with its exact value. Do not summarize or abbreviate. The snapshot should be precise enough to reproduce the environment.

### Step 2: List Running Processes

Use `sys_procs` to retrieve the current process list. For each process, capture:

- Process ID (PID).
- Process name.
- CPU usage percentage.
- Memory usage (RSS or working set size).
- Parent PID (if available).
- Command line (if available and not truncated).
- User/owner.
- Start time.

Sort the process list by CPU usage descending. Retain the top 20 processes by CPU usage and the top 20 by memory usage (these may overlap). Also separately list any processes that match the current project name or known development tools (node, python, java, docker, code, webpack, vite, tsc, jest, cargo, go).

If the process list is very large, do not attempt to include every process. The top consumers and project-related processes are sufficient for most diagnostic purposes.

### Step 3: Check Disk Usage

Use `sys_disk` to retrieve disk utilization for all mounted filesystems. For each mount point, record:

- Mount point / drive letter.
- Filesystem type (ext4, NTFS, APFS, etc.).
- Total capacity.
- Used space.
- Available space.
- Usage percentage.

Flag any filesystem that exceeds 90% usage as a warning. Flag any filesystem that exceeds 95% usage as critical. These thresholds are important because many systems behave poorly when disk space is nearly exhausted (failed writes, corrupted databases, inability to create temporary files).

### Step 4: Read Environment Variables

Use `sys_env` to capture the current environment. Record all environment variables, but apply the following security filtering:

### Variables to Include Fully

Include the complete key-value pair for non-sensitive variables:

- `PATH`, `HOME`, `USERPROFILE`, `SHELL`, `TERM`, `LANG`, `LC_ALL`.
- `NODE_ENV`, `PYTHON_PATH`, `GOPATH`, `GOROOT`, `JAVA_HOME`, `CARGO_HOME`, `RUSTUP_HOME`.
- `EDITOR`, `VISUAL`, `PAGER`.
- `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY` (values may contain hostnames, which are generally safe).
- `NVM_DIR`, `PYENV_ROOT`, `VOLTA_HOME`.
- `CI`, `GITHUB_ACTIONS`, `GITLAB_CI`, `JENKINS_URL` (CI environment indicators).

### Variables to Redact

Include only the key name (not the value) for potentially sensitive variables:

- Any variable containing `KEY`, `SECRET`, `TOKEN`, `PASSWORD`, `CREDENTIAL`, `AUTH` in its name.
- Any variable containing `AWS_`, `AZURE_`, `GCP_`, `GOOGLE_` prefixes (cloud credentials).
- `DATABASE_URL`, `REDIS_URL`, `MONGODB_URI` (connection strings may contain credentials).

Mark redacted variables as `<REDACTED>` in the snapshot. This ensures the snapshot is safe to share without exposing secrets.

### Step 5: Check Docker State (If Available)

First, test whether Docker is installed and the daemon is running by checking the `docker_ps` tool. If Docker is not available, note "Docker: not available" and move on.

If Docker is available, capture:

- Docker version (client and server).
- List of all containers with: name, image, status, ports, creation time.
- Count of containers by state: running, stopped, paused, restarting.
- List of Docker images: repository, tag, size, creation date.
- Docker disk usage summary if obtainable.
- Docker networks: name, driver, scope.

This provides a complete picture of the containerized workloads on the system.

### Step 6: Capture Tool Versions

Run version commands for common development tools via `shell_exec` (shell). Check each tool and record its version if installed, or "not installed" if the command fails:

- **Runtime environments**: `node --version`, `python --version`, `python3 --version`, `ruby --version`, `go version`, `rustc --version`, `java -version`, `dotnet --version`.
- **Package managers**: `npm --version`, `yarn --version`, `pnpm --version`, `pip --version`, `pip3 --version`, `gem --version`, `cargo --version`, `composer --version`, `brew --version`.
- **Version managers**: `nvm --version`, `pyenv --version`, `rbenv --version`, `volta --version`, `asdf --version`.
- **Build tools**: `make --version`, `cmake --version`, `gcc --version`, `g++ --version`, `clang --version`.
- **Container and orchestration**: `docker --version`, `docker compose version`, `kubectl version --client`, `helm version`.
- **Version control**: `git --version`, `gh --version` (GitHub CLI).
- **Editors and IDEs**: `code --version` (VS Code).
- **Databases**: `psql --version`, `mysql --version`, `mongosh --version`, `redis-cli --version`, `sqlite3 --version`.

Run these commands in sequence. For each, capture only the first line of output (the version string). Do not fail the entire snapshot if individual tools are missing; simply record "not installed" and continue.

### Step 7: Read Key Configuration Files

If the user specifies configuration files to include, read them using the filesystem tool (`fs_read`). Common files to offer:

- Shell configuration: `~/.bashrc`, `~/.zshrc`, `~/.bash_profile`, `~/.profile`.
- Git configuration: `~/.gitconfig`, `~/.gitignore_global`.
- SSH configuration: `~/.ssh/config` (do NOT include private keys).
- Docker configuration: `~/.docker/config.json` (redact any `auth` fields).
- npm configuration: `~/.npmrc` (redact any `authToken` fields).
- Project-specific: any configuration files in the current project directory.

Only include configuration files that the user explicitly requests or that are directly relevant to the diagnostic purpose of the snapshot. Do not indiscriminately include all configuration files.

Apply the same redaction rules as for environment variables: strip any values that may contain secrets, tokens, or credentials.

### Step 8: Compute Snapshot Checksum

Once all data has been collected, assemble the complete snapshot content as a single text document. Before writing it to disk, compute a checksum using `crypto_hash` with the SHA-256 algorithm.

The checksum serves as an integrity verification mechanism. If the snapshot is shared or stored, the recipient can recompute the hash to verify that the content has not been altered.

Include the checksum in the snapshot footer, along with the algorithm used:

```
---
Integrity: SHA-256 <hash_value>
```

### Step 9: Write Snapshot to File

Write the complete snapshot to a timestamped markdown file in the project directory. Use the following naming convention:

```
e-snapshot-<YYYY-MM-DD>-<HHMMSS>.md
```

For example: `e-snapshot-2025-01-15-143022.md`.

Place the file in a `snapshots/` subdirectory of the project root. Create the directory if it does not exist. If the user specifies a different output location, use that instead.

### Step 10: Format the Snapshot Document

Structure the snapshot document with the following sections:

```
# System Snapshot

**Generated**: <full ISO 8601 timestamp with timezone>
**Hostname**: <hostname>
**Purpose**: <user-specified purpose or "General system state capture">

## System Information

| Property          | Value                                    |
|-------------------|------------------------------------------|
| Operating System  | <OS name and version>                    |
| Kernel            | <kernel version>                         |
| Architecture      | <arch>                                   |
| CPU               | <model> (<N> cores)                      |
| Memory            | <total RAM>                              |
| Node.js           | <version>                                |

## Disk Usage

| Mount / Drive | Type  | Total   | Used    | Free    | Usage |
|---------------|-------|---------|---------|---------|-------|
| /             | ext4  | 500 GB  | 320 GB  | 180 GB  | 64%   |
| /home         | ext4  | 1 TB    | 750 GB  | 250 GB  | 75%   |

## Top Processes (by CPU)

| PID   | Name    | CPU % | Memory    | User    |
|-------|---------|-------|-----------|---------|
| 1234  | node    | 45.2  | 512 MB    | deyan   |
| 5678  | python  | 23.1  | 1.2 GB    | deyan   |

## Top Processes (by Memory)

| PID   | Name    | CPU % | Memory    | User    |
|-------|---------|-------|-----------|---------|
| 5678  | python  | 23.1  | 1.2 GB    | deyan   |
| 9012  | java    | 5.4   | 2.1 GB    | deyan   |

## Environment Variables

| Variable          | Value                                    |
|-------------------|------------------------------------------|
| PATH              | /usr/local/bin:/usr/bin:...               |
| NODE_ENV          | development                              |
| AWS_ACCESS_KEY_ID | <REDACTED>                               |

## Docker Containers

| Name        | Image          | Status  | Ports       |
|-------------|----------------|---------|-------------|
| my-app      | node:18        | Running | 3000:3000   |
| my-db       | postgres:15    | Running | 5432:5432   |

## Tool Versions

| Tool              | Version        |
|-------------------|----------------|
| node              | 18.17.0        |
| python3           | 3.11.5         |
| git               | 2.42.0         |
| docker            | 24.0.6         |

## Configuration Files

<contents of requested configuration files, with redactions>

---
Integrity: SHA-256 <hash>
```

Adjust column widths and content based on actual data. Omit sections that have no data (e.g., omit the Docker section if Docker is not installed). Keep the format consistent and machine-parseable where possible.

## Notes

- The snapshot process should be non-destructive. It only reads system state; it never modifies anything.
- Execution time depends on the number of tools to check and containers to inspect. Expect 10-30 seconds for a typical developer workstation.
- If a particular data collection step fails (e.g., a command hangs or returns an error), log the failure within the snapshot rather than aborting. A partial snapshot is more useful than no snapshot.
- Snapshots can be compared over time. Two snapshots taken before and after a change can be diffed to identify exactly what changed.

## Edge Cases

- **Docker not installed or not running**: The Docker state section should report "Docker not available" rather than failing the entire snapshot. Each section should be independently resilient.
- **Restricted permissions**: On shared or corporate machines, some commands (lsof, netstat, dmidecode) may require sudo. Attempt unprivileged execution first, note permission errors, and skip rather than halt.
- **WSL environments**: Windows Subsystem for Linux reports hybrid system information. The kernel version is Linux but hardware info comes from the Windows host. Document the WSL context to avoid confusion.
- **Ephemeral container environments**: Snapshots of CI runners, Docker build stages, or Kubernetes pods capture state that will be destroyed. Note the ephemeral nature and focus on tool versions and configuration rather than hardware.
- **Large numbers of running processes**: Systems running 500+ processes produce verbose output. Summarize by top resource consumers and process group counts rather than listing every process.

## Related Skills

- **e-env** (eskill-system): Run e-env alongside this skill to combine system state capture with requirements validation.
- **e-procs** (eskill-system): Follow up with e-procs after this skill to investigate any anomalies found in the system snapshot.
