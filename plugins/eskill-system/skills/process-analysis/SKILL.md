---
name: process-analysis
description: "Analyzes running processes for resource consumption patterns and identifies potential issues like memory leaks, runaway processes, or resource contention. Use when investigating high CPU or memory usage, diagnosing slow systems, or monitoring long-running processes."
---

# Process Analysis

Analyze the running processes on the system to identify resource consumption patterns, detect anomalies, and surface potential issues such as memory leaks, runaway CPU usage, zombie processes, and port conflicts. This skill produces a structured report with findings and recommendations.

## Overview

Process analysis is essential when a system is exhibiting performance problems -- slow response times, high fan activity, unresponsive applications, or resource exhaustion warnings. By systematically examining what is running and how much each process consumes, you can identify the source of the problem and take corrective action.

## Step 1: Get Full Process List

Use `system_processes` to retrieve the complete list of running processes. For each process, collect:

- **PID**: Process identifier.
- **Name**: The process name or executable name.
- **CPU %**: Current CPU utilization as a percentage of one core (or total system, depending on the platform).
- **Memory**: Resident Set Size (RSS) or Working Set size, representing actual physical memory in use.
- **Status**: Running, sleeping, stopped, zombie, etc.
- **User**: The user account under which the process runs.
- **Start Time**: When the process was started (useful for identifying long-running processes).
- **Command**: The full command line used to launch the process (if available).
- **Parent PID (PPID)**: The PID of the parent process.

Store the complete process list for analysis. Note the total number of processes and the timestamp of collection for the report.

## Step 2: Sort and Rank by CPU Usage

Sort the process list by CPU usage in descending order. Identify the top 10 CPU consumers. For each:

- Record the process name, PID, CPU percentage, and command line.
- Determine if the high CPU usage is expected. Development tools like compilers (gcc, rustc, tsc), build systems (webpack, vite, gradle), and test runners (jest, pytest) are expected to use significant CPU during active work.
- Flag processes that are consuming high CPU but are not build-related or user-initiated. These may be runaway processes.

Calculate the total CPU usage across all processes. On a multi-core system, 100% per core means a system with 8 cores can show up to 800% total CPU usage. Contextualize the numbers accordingly.

Identify any single process consuming more than 90% of a single core for an extended period. This is a potential runaway process, especially if it is not a known compute-intensive task.

## Step 3: Sort and Rank by Memory Usage

Sort the process list by memory usage in descending order. Identify the top 10 memory consumers. For each:

- Record the process name, PID, memory in MB or GB, and command line.
- Compare memory usage against typical expected values for that type of process:
  - Web browsers (chrome, firefox, edge): high memory is common but excessive instances may indicate a leak.
  - Node.js processes: typical heap is 1-4 GB depending on configuration. Above the V8 default heap limit (approximately 1.7 GB on 64-bit) suggests either `--max-old-space-size` has been increased or something unusual is occurring.
  - Java processes: memory depends on JVM heap settings (`-Xmx`). Check if actual usage is near the maximum.
  - Database processes (postgres, mysql, mongod): memory usage depends on configuration; high usage is often by design for caching.
  - IDE/editor processes (code, idea): 500 MB to 2 GB is typical; significantly more may indicate extension issues.

Calculate total memory usage across all processes and compare against total system memory. If total process memory exceeds 80% of physical RAM, the system is under memory pressure and may be swapping, which severely degrades performance.

## Step 4: Identify Project-Related Processes

Filter the process list to find processes specifically related to the current project. Match by:

- **Process name**: Look for processes named `node`, `python`, `java`, `dotnet`, `ruby`, `go` and check their command lines for project directory references.
- **Working directory**: If available, match processes whose CWD is within the project directory tree.
- **Known development servers**: Look for processes listening on common development ports (3000, 3001, 4200, 5000, 5173, 8000, 8080, 8888).
- **Build tools**: Match processes running `webpack`, `vite`, `tsc`, `babel`, `esbuild`, `rollup`, `turbo`, `nx`.
- **Test runners**: Match `jest`, `mocha`, `pytest`, `cargo test`, `go test`.
- **Package managers**: Match `npm`, `yarn`, `pnpm`, `pip`, `cargo`, `go`.

For each project-related process, note its specific role (development server, build process, test runner, etc.) and current resource consumption.

## Step 5: Gather Additional Process Details

For processes that are flagged as suspicious or consuming unexpected resources, gather additional details using platform-specific commands via `run_command` (shell):

### Linux

```
ps aux --sort=-%mem | head -20          # Top memory consumers with details
ps aux --sort=-%cpu | head -20          # Top CPU consumers with details
ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head -30
cat /proc/<pid>/status                  # Detailed process status
cat /proc/<pid>/cmdline                 # Full command line
ls -la /proc/<pid>/fd | wc -l          # Open file descriptor count
cat /proc/<pid>/limits                  # Resource limits
```

### macOS

```
ps aux -m | head -20                    # Top memory consumers
ps aux -r | head -20                    # Top CPU consumers
lsof -p <pid> | wc -l                  # Open file descriptor count
sample <pid> 1                          # Brief CPU sample
```

### Windows

```
tasklist /v /fi "PID eq <pid>"          # Detailed task info
wmic process where processid=<pid> get CommandLine,WorkingSetSize,ThreadCount
Get-Process -Id <pid> | Format-List *   # PowerShell detailed process info
netstat -ano | findstr <pid>            # Network connections for process
```

Choose the appropriate commands based on the detected platform from `system_info`. Run only the commands relevant to the flagged processes to avoid excessive overhead.

## Step 6: Check for Zombie and Defunct Processes

Zombie processes are child processes that have terminated but whose parent has not yet read their exit status. They consume no resources but occupy a process table entry and may indicate a buggy parent process.

### Detection

- On Linux/macOS: look for processes with status `Z` (zombie) in the process list. Use `ps aux | grep Z` via shell if the process list does not include status.
- On Windows: zombie processes are less common due to different process lifecycle management. However, check for "suspended" processes that may be stuck.

### Analysis

For each zombie process found:

- Identify its parent process (PPID).
- Determine if the parent process is still running.
- If the parent is running but not reaping children, this is a bug in the parent process.
- If the parent has also exited, the zombie will be adopted and reaped by the init process (PID 1) shortly.

A few zombie processes are harmless. A large number (more than 10) or a growing count suggests a parent process with a child-reaping bug.

## Step 7: Check for Port Conflicts

List all listening network ports and the processes that own them. This reveals port conflicts and helps identify which services are running.

### Commands by Platform

**Linux**:
```
ss -tlnp                    # TCP listening ports with process info
ss -ulnp                    # UDP listening ports with process info
```

**macOS**:
```
lsof -iTCP -sTCP:LISTEN -P  # TCP listening ports
```

**Windows**:
```
netstat -ano | findstr LISTENING    # All listening ports with PIDs
```

### Analysis

Parse the output to build a map of port-to-process bindings. Check for:

- **Port conflicts**: Multiple processes attempting to bind the same port. The second process will typically fail to start, but the error may not be obvious.
- **Common development ports in use**: If the user is trying to start a development server on port 3000 but another process already holds that port, this is a common source of "address already in use" errors.
- **Unexpected services**: Processes listening on ports that are not part of the expected development stack. This could be leftover processes from previous sessions, or potentially unwanted services.
- **Wildcard bindings**: Processes binding to `0.0.0.0` or `::` (all interfaces) vs `127.0.0.1` (localhost only). Development servers bound to all interfaces are accessible from the network, which may be a security concern.

Present the port map as a table:

```
| Port  | Protocol | PID   | Process    | Binding     |
|-------|----------|-------|------------|-------------|
| 3000  | TCP      | 12345 | node       | 0.0.0.0     |
| 5432  | TCP      | 6789  | postgres   | 127.0.0.1   |
| 8080  | TCP      | 11111 | java       | 0.0.0.0     |
```

## Step 8: Identify Anomalous Processes

Based on all collected data, identify processes that exhibit anomalous behavior:

- **High CPU with no known cause**: A process using more than 50% CPU that is not a build tool, compiler, or user-initiated compute task.
- **Excessive memory growth**: If historical data is available (from previous snapshots or system monitoring), identify processes whose memory usage has grown significantly over time, suggesting a memory leak.
- **Too many instances**: Multiple instances of the same process running when only one is expected (e.g., multiple Node.js development servers, multiple database instances).
- **Long-running temporary processes**: Build or test processes that should have completed but are still running hours or days later.
- **High file descriptor count**: Processes with an unusually large number of open files or sockets, which may indicate resource leaks.
- **Orphaned processes**: Processes whose parent PID is 1 (reparented to init) that appear to be application processes, not system services. These may be leftover from crashed parent processes.

For each anomaly, record the process details, the nature of the anomaly, and the potential impact.

## Step 9: Generate the Analysis Report

Compile all findings into a structured report:

```
## Process Analysis Report

**Generated**: <timestamp>
**Platform**: <OS and version>
**Total Processes**: <count>
**System Load**: <CPU utilization summary>, <memory utilization summary>

### Top CPU Consumers

| Rank | PID   | Name      | CPU % | Command                    | Status   |
|------|-------|-----------|-------|----------------------------|----------|
| 1    | 12345 | node      | 67.2  | node server.js             | Expected |
| 2    | 6789  | chrome    | 23.4  | chrome --type=renderer     | Normal   |
| 3    | 11111 | rustc     | 99.1  | rustc --edition 2021 ...   | Building |

### Top Memory Consumers

| Rank | PID   | Name      | Memory   | Command                    | Status   |
|------|-------|-----------|----------|----------------------------|----------|
| 1    | 2222  | java      | 2.4 GB   | java -Xmx4g -jar app.jar  | Normal   |
| 2    | 3333  | chrome    | 1.8 GB   | chrome --type=gpu-process  | High     |

### Project-Related Processes

| PID   | Name  | Role              | CPU % | Memory  | Port |
|-------|-------|-------------------|-------|---------|------|
| 12345 | node  | Dev server        | 67.2  | 256 MB  | 3000 |
| 44444 | node  | TypeScript watcher| 5.1   | 128 MB  | --   |

### Listening Ports

| Port  | Process   | PID   | Binding   |
|-------|-----------|-------|-----------|
| 3000  | node      | 12345 | 0.0.0.0   |
| 5432  | postgres  | 6789  | 127.0.0.1 |

### Anomalies

1. **High CPU: unknown-process (PID 99999)**
   - CPU usage: 95.3% sustained
   - Command: /usr/bin/unknown-process --flag
   - Running since: 2 days ago
   - Recommendation: Investigate this process. It does not appear to be part of
     the development stack. Consider terminating it if it is not needed.

2. **Potential memory leak: my-service (PID 55555)**
   - Current memory: 1.8 GB (above typical 200 MB for this service)
   - Running since: 5 days ago
   - Recommendation: Restart the service and monitor memory growth over time.
     If memory increases steadily, profile the application for leaks.

### Zombie Processes

None detected. (or list found zombies with parent info)

### Recommendations

1. <specific actionable recommendation>
2. <specific actionable recommendation>
3. <specific actionable recommendation>
```

### Platform-Specific Notes

Include a section at the end with platform-specific observations:

- **Windows**: Note if Windows Defender or other antivirus is consuming significant resources during file scans. Note any Windows Update processes running in the background. Mention that Task Manager and Resource Monitor provide real-time graphical views for ongoing monitoring.
- **macOS**: Note if Spotlight indexing (mds, mdworker) is consuming resources. Note any Time Machine backup processes. Mention Activity Monitor for graphical monitoring.
- **Linux**: Note if any kernel threads (kworker, kswapd) are consuming unusual resources. Note if OOM killer has been active recently (check `dmesg` for OOM messages). Mention `htop` and `btop` for interactive monitoring.

Tailor recommendations to the specific platform and the user's context. If the analysis was triggered by a specific complaint (e.g., "my build is slow"), ensure the recommendations directly address that complaint.
