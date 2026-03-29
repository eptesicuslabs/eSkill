---
name: e-containers
description: "Builds a health dashboard of all Docker containers with status, ports, restarts, and log excerpts. Use when monitoring containers, debugging a failing service, or checking system state. Also applies when: 'Docker status', 'are my containers healthy', 'container overview', 'which containers are running', 'why did my container crash'."
---

# Container Dashboard

Build a comprehensive health dashboard for all Docker containers on the system. This skill collects container metadata, health status, resource usage indicators, port mappings, volume mounts, and recent log excerpts, then presents everything in a structured overview with actionable highlights.

## Prerequisites

Before proceeding, verify that Docker is available on the system. Run `docker --version` via `shell_exec`. If Docker is not installed or the daemon is not running, report the issue clearly and stop. Do not attempt to proceed without a functioning Docker installation.

### Step 1: List All Containers

Use `docker_ps` with the `all` flag set to true to retrieve every container, including those that are stopped, exited, or in a created state. This provides the baseline inventory. For each container, capture:

- Container ID (short form).
- Container name.
- Image name and tag.
- Current status string (e.g., "Up 3 hours", "Exited (1) 2 days ago").
- Ports mapping.
- Creation timestamp.

If the system has no containers at all, report that cleanly and stop. There is nothing to dashboard.

### Step 2: Inspect Each Running Container

For each container that is in a running state, use `docker_inspect` to retrieve the full inspection JSON. Extract the following fields from the inspection data:

- `State.Status` -- the container state (running, paused, restarting, etc.).
- `State.Health.Status` -- if the container has a health check defined, this will be "healthy", "unhealthy", or "starting". If no health check is defined, record as "no healthcheck".
- `State.StartedAt` -- the timestamp when the container last started.
- `State.FinishedAt` -- relevant for stopped containers.
- `RestartCount` -- how many times the container has been restarted.
- `HostConfig.RestartPolicy` -- the restart policy (no, always, unless-stopped, on-failure).
- `NetworkSettings.Ports` -- detailed port bindings with host and container ports.
- `Mounts` -- volume mounts with source and destination paths.
- `Config.Env` -- environment variables (be careful not to expose secrets; only note the variable names, not values).
- `Config.Image` -- the image specification.
- `Config.Labels` -- container labels, which often contain orchestration metadata.

For stopped containers, still run `docker_inspect` but note that resource metrics will not be available.

### Step 3: Extract Key Metrics

From the inspection data, compute the following derived metrics for each container:

- **Uptime**: Calculate the duration from `State.StartedAt` to now. Format as human-readable (e.g., "3 days 4 hours", "15 minutes").
- **Restart frequency**: If `RestartCount` is greater than 0, compute the average time between restarts. A high restart count relative to uptime indicates instability.
- **Port exposure**: List all host-to-container port mappings in `host:container` format. Flag any containers binding to `0.0.0.0` (all interfaces) on sensitive ports.
- **Volume mounts**: Count the number of bind mounts vs named volumes. Flag any mounts to sensitive host directories (e.g., `/`, `/etc`, `/var/run/docker.sock`).
- **Health check status**: Directly from the health status field. If the container is "unhealthy", this is a critical finding.

### Step 4: Retrieve Recent Logs

For each running container, use `docker_logs` to retrieve the most recent 50 lines of log output. Configure the following parameters:

- `tail`: 50 lines.
- `timestamps`: true, to correlate log entries with events.

Store the raw log text for each container. If a container produces no log output, note that it has empty logs (this can itself be an anomaly worth flagging).

For stopped containers that exited with a non-zero exit code, also retrieve their last 50 log lines, as these often contain the error that caused the exit.

### Step 5: Parse Logs for Error Patterns

Analyze the collected log text for each container using `log_errors` pattern matching. Search for the following common error indicators:

- Lines containing `ERROR`, `FATAL`, `CRITICAL`, `PANIC` (case-insensitive).
- Stack traces: lines starting with `at `, `Traceback`, or `Exception`.
- Connection errors: `connection refused`, `ECONNREFUSED`, `timeout`, `ETIMEDOUT`.
- Out-of-memory indicators: `OOM`, `out of memory`, `Cannot allocate memory`.
- Permission errors: `permission denied`, `EACCES`, `access denied`.
- Crash indicators: `segfault`, `SIGSEGV`, `SIGKILL`, `killed`.

Count the number of error-level entries per container. Record the most recent error message for each container to include in the dashboard.

### Step 6: Categorize Container Health

Assign each container to one of the following categories based on all collected data:

- **Healthy**: Running, health check passing (or no health check but no errors), restart count is 0 or very low, no error patterns in recent logs.
- **Warning**: Running but with minor concerns -- moderate restart count (1-5), some non-critical errors in logs, health check not defined on a long-running service.
- **Unhealthy**: Health check explicitly failing, high restart count (>5), frequent errors in logs, or container is in a restarting loop.
- **Stopped**: Container is not running. Sub-categorize as "exited cleanly" (exit code 0) or "exited with error" (non-zero exit code).
- **Critical**: Container is in a crash loop (restarting state with high restart count), OOM killed, or showing persistent connection/permission failures.

### Step 7: Build the Dashboard Output

Format the dashboard as a structured text report. Use the following layout:

```
## Docker Container Dashboard

**Generated**: <timestamp>
**Total Containers**: <N> (<running> running, <stopped> stopped)

### Overview

| Name            | Image          | Status    | Health      | Uptime     | Ports         | Errors |
|-----------------|----------------|-----------|-------------|------------|---------------|--------|
| my-app          | node:18-alpine | Running   | Healthy     | 3d 4h      | 3000:3000     | 0      |
| my-db           | postgres:15    | Running   | Unhealthy   | 3d 4h      | 5432:5432     | 12     |
| old-service     | nginx:latest   | Exited(0) | N/A         | --         | --            | 0      |

### Attention Required

#### CRITICAL: my-db
- Health check: FAILING
- Restart count: 8
- Recent error: "FATAL: could not open relation mapping file"
- Recommendation: Check database storage and file permissions.

### Container Details

#### my-app (node:18-alpine)
- Status: Running (Up 3 days)
- Health: Healthy
- Ports: 0.0.0.0:3000 -> 3000/tcp
- Volumes: ./src:/app/src (bind), app-data:/app/data (volume)
- Restart policy: unless-stopped
- Restart count: 0
- Recent logs (last 5 lines):
  [2025-01-15T10:30:00Z] Server listening on port 3000
  [2025-01-15T10:30:01Z] Connected to database
  ...
```

### Step 8: Highlight Containers Needing Attention

At the top of the dashboard, after the overview table, include an "Attention Required" section that lists only containers with issues. Sort by severity (critical first, then unhealthy, then warnings). For each flagged container, include:

- The specific issue detected.
- The most relevant log excerpt (1-3 lines).
- A concrete recommendation for resolution.

Common recommendations to provide:

- **Unhealthy container**: Check the health check command, review application logs, verify dependent services are accessible.
- **High restart count**: Investigate the cause of crashes. Check resource limits, application errors, and dependency availability.
- **OOM killed**: Increase memory limits in Docker Compose or run configuration. Review the application for memory leaks.
- **Connection refused in logs**: Verify that dependent services are running and network configuration is correct. Check Docker network connectivity.
- **Permission denied**: Check file ownership and permissions in mounted volumes. Review the user directive in the Dockerfile.
- **Exited with error**: Review the last log entries before exit. Check the exit code for specific meaning.

### Step 9: Optional Notification for Critical Issues

If any container is categorized as Critical, use `sys_notify` to dispatch a desktop notification with the following content:

- Title: "Docker Dashboard: Critical Issue Detected"
- Body: A brief summary of which containers are critical and the primary issue for each.

This ensures that critical container problems are surfaced even if the user is not actively reviewing the dashboard output. Only send notifications for genuinely critical conditions to avoid notification fatigue.

## Additional Notes

- When Docker Compose is in use, group containers by their Compose project (identified by the `com.docker.compose.project` label). Present each project as a section in the dashboard.
- For containers managed by Docker Compose, include the service name from the `com.docker.compose.service` label alongside the container name.
- If the system has a large number of containers (more than 20), provide a summary table first and only expand details for containers with issues. Offer to show full details for specific containers on request.
- Respect container log verbosity. If a container produces extremely high log volume, note this as a finding (it may indicate debug logging left enabled in production).

## Edge Cases

- **Docker not installed or daemon not running**: Report "Docker is not available" rather than failing. Suggest checking if Docker Desktop is running or if the user needs to install Docker.
- **Rootless Docker or Podman**: Rootless container runtimes may not expose all status information (e.g., network details). Detect the runtime type and adjust queries accordingly.
- **Containers in Kubernetes pods**: When Docker runs inside a K8s node, container inspection shows K8s system containers (pause, coredns). Filter these from the dashboard unless explicitly requested.
- **Extremely high log volume**: Containers producing thousands of log lines per second can cause log fetching to hang. Set a log line limit (e.g., last 200 lines) and a timeout on log retrieval.
- **Stopped containers with no logs**: Containers that exited immediately may have no log output. Check the exit code and Docker events for the container start/stop sequence instead.

## Related Skills

- **e-logs** (eskill-system): Follow up with e-logs after this skill to diagnose issues detected in container status.
- **e-monitor** (eskill-devops): Run e-monitor alongside this skill to correlate container health with configured monitoring rules.
