---
name: log-investigation
description: "Parses log files, correlates errors across sources, and builds incident timelines with root-cause hypotheses. Use when diagnosing production outages, debugging intermittent failures, or running post-incident analysis. Also applies when: 'check the logs', 'what went wrong', 'find the error', 'debug production issue', 'why is it failing'."
---

# Log Investigation

Perform structured investigation of application and system logs to identify root causes, build incident timelines, and produce actionable analysis reports. This skill handles multiple log formats, correlates events across sources, and surfaces patterns that point to underlying issues.

## Overview

Log investigation follows a systematic approach: identify sources, parse and normalize entries, filter for relevant events, build a chronological timeline, correlate errors with preceding activity, identify patterns and clusters, and produce a report with hypotheses and recommendations.

## Step 1: Identify Log Sources

Determine which log files and sources are relevant to the investigation. Check for:

### File-Based Logs

- Application log files: look in common locations such as `./logs/`, `./log/`, `/var/log/`, and any path specified by the user.
- Framework-specific log locations:
  - Node.js: check for `pm2` logs in `~/.pm2/logs/`, or custom log directories configured in the application.
  - Python: check for files referenced in `logging.config` or `LOGGING` settings.
  - Java: check `log4j2.xml`, `logback.xml` configurations for output paths.
- System logs: `/var/log/syslog`, `/var/log/messages`, `/var/log/kern.log` on Linux; Event Log on Windows.
- Web server logs: `/var/log/nginx/`, `/var/log/apache2/`, or custom paths.

Use the filesystem tool (`list_dir`) to scan likely log directories. Identify files with `.log`, `.log.1`, `.log.gz` extensions and note their sizes and modification times.

### Container Logs

If Docker is available and the investigation involves containerized services, identify relevant containers using `docker_ps`. Container logs will be retrieved via `docker_logs` in later steps.

### User-Specified Sources

If the user has specified particular log files or paths, prioritize those. Always start with user-specified sources before broadening the search.

Record all identified sources with their type (file, container, system) and estimated size.

## Step 2: Parse Log Files

For each identified log file, use `log_parse` to read and normalize the entries. Handle the following formats:

### JSON Lines (JSONL)

Each line is a JSON object. Common field names to extract:

- Timestamp: `timestamp`, `time`, `ts`, `@timestamp`, `date`, `datetime`.
- Level: `level`, `severity`, `log_level`, `loglevel`.
- Message: `message`, `msg`, `text`, `log`.
- Source: `source`, `logger`, `module`, `component`, `service`.
- Additional context: `error`, `stack`, `trace_id`, `request_id`, `user_id`.

### Syslog Format

Parse the standard syslog format: `<priority>timestamp hostname process[pid]: message`. Extract the timestamp, hostname, process name, PID, and message body.

### Generic Text Logs

For logs that do not follow a structured format, apply heuristic parsing:

- Look for timestamp patterns at the start of each line: ISO 8601 (`2025-01-15T10:30:00Z`), common date formats (`2025-01-15 10:30:00`), Unix epoch timestamps.
- Look for log level indicators: `[INFO]`, `[ERROR]`, `[WARN]`, `[DEBUG]`, `INFO`, `ERROR`, etc.
- Treat lines without a timestamp as continuation of the previous entry (common for stack traces and multi-line messages).

Normalize all timestamps to a consistent format (ISO 8601 with timezone) for cross-source correlation.

## Step 3: Extract Error Entries

Use `log_errors` to filter all parsed entries for error-level events. Apply the following severity classification:

- **FATAL / CRITICAL / EMERGENCY**: Application or service is non-functional. Highest priority.
- **ERROR**: A specific operation failed but the application may still be running.
- **WARN / WARNING**: Something unexpected occurred that may lead to errors.

For each error entry, capture:

- The full error message.
- The timestamp.
- The source file and log source.
- Any associated stack trace (subsequent lines until the next timestamped entry).
- Contextual fields such as request ID, user ID, or trace ID if available.

## Step 4: Get Statistical Overview

Use `log_stats` to produce aggregate statistics across all parsed log sources:

- Total entries per log level (DEBUG, INFO, WARN, ERROR, FATAL).
- Entries per time bucket (e.g., per minute or per hour depending on the time range).
- Error rate over time: are errors increasing, stable, or sporadic?
- Top error messages by frequency (group similar messages, normalize variable parts like IDs and timestamps).
- Entries per source/component if the logs include source information.

This overview helps identify whether the issue is a sudden spike, a gradual degradation, or a constant background error rate.

## Step 5: Search for Specific Patterns

Use `log_search` with regular expressions to find entries matching specific patterns relevant to the investigation. Common searches include:

### Connection and Network Issues
- `connection refused|ECONNREFUSED` -- upstream service unavailable.
- `timeout|ETIMEDOUT|ESOCKETTIMEDOUT` -- slow or unresponsive dependencies.
- `DNS.*fail|ENOTFOUND|getaddrinfo` -- DNS resolution failures.
- `SSL|TLS|certificate` -- TLS handshake or certificate issues.

### Resource Exhaustion
- `out of memory|OOM|heap|ENOMEM` -- memory exhaustion.
- `too many open files|EMFILE|ENFILE` -- file descriptor limits.
- `disk full|ENOSPC|no space left` -- disk space exhaustion.
- `pool exhausted|connection pool|max connections` -- connection pool saturation.

### Application Errors
- `NullPointerException|TypeError|undefined is not|Cannot read prop` -- null reference errors.
- `deadlock|lock timeout|lock wait` -- database or resource locking issues.
- `authentication|unauthorized|forbidden|403|401` -- auth failures.
- `rate limit|throttl|429` -- rate limiting.

### Stack Traces
- `^\\s+at\\s+` -- JavaScript/Java stack trace lines.
- `Traceback \\(most recent call last\\)` -- Python stack traces.
- `panic:` -- Go panic traces.
- `Caused by:` -- Java chained exceptions.

For each pattern match, record the entry with full context (including surrounding lines for multi-line matches).

## Step 6: Build the Event Timeline

Collect all relevant entries (errors, warnings, and significant info-level events) and sort them chronologically across all sources. Build a unified timeline:

1. Merge entries from all log sources into a single chronological sequence.
2. Preserve the source identifier so each entry can be traced back to its origin.
3. Include a time delta column showing the gap between consecutive entries.
4. Mark error entries distinctly from info/warning entries.

The timeline should cover the period of interest. If the user has specified a time range, filter to that range. Otherwise, focus on the period surrounding the first error occurrence, extending 15 minutes before and after.

Format the timeline as:

```
## Event Timeline

| Time                | Delta  | Source      | Level | Message (truncated)              |
|---------------------|--------|-------------|-------|----------------------------------|
| 10:30:00.000Z       | --     | app.log     | INFO  | Database connection established   |
| 10:30:15.123Z       | +15s   | app.log     | WARN  | Slow query detected (2.3s)       |
| 10:30:16.456Z       | +1.3s  | nginx.log   | ERROR | 502 Bad Gateway /api/users       |
| 10:30:16.789Z       | +0.3s  | app.log     | ERROR | Connection pool exhausted        |
```

## Step 7: Correlate Errors with Preceding Events

For each error in the timeline, look backward to identify what happened in the seconds or minutes before the error. This is the core analytical step. Apply the following correlation logic:

1. **Immediate predecessors**: What events occurred in the 5 seconds before the error in the same source? These are the most likely direct causes.
2. **Cross-source predecessors**: What events occurred in other log sources in the 30 seconds before the error? These may reveal cascading failures.
3. **First occurrence**: Find the very first error in the timeline. The events preceding this initial error are the most important for root cause analysis.
4. **Request tracing**: If entries share a request ID or trace ID, link them together regardless of source. This builds a per-request timeline that may reveal where a specific request went wrong.
5. **State changes**: Look for entries indicating state transitions (service started/stopped, connection opened/closed, deployment events, configuration changes) that precede the errors.

Document each correlation as a causal chain: "Event A (source X, time T) was followed by Event B (source Y, time T+5s), which led to Error C."

## Step 8: Identify Error Clusters

Analyze the distribution of errors over time to identify clusters:

- **Burst clusters**: Multiple errors occurring within a short window (e.g., 10+ errors in 1 minute). These often indicate a sudden failure event.
- **Periodic clusters**: Errors occurring at regular intervals (e.g., every 5 minutes). These suggest scheduled tasks, health checks, or retry loops.
- **Escalating clusters**: Error rate increasing over time. This suggests resource leaks, queue buildup, or cascading failures.
- **Isolated errors**: Single errors with no nearby companions. These may be transient issues or independent failures.

For each cluster, note the start time, duration, error count, and the dominant error message. If a cluster coincides with a specific event (deployment, traffic spike, dependency failure), note the correlation.

## Step 9: Container Log Context

If the investigation involves containerized services, use `docker_logs` to retrieve additional context:

- For each container implicated by the file-based log analysis, retrieve the matching time range of container logs.
- Check for container restart events that coincide with error clusters.
- Look for Docker-level events (OOM kills, health check failures) that may not appear in application logs.
- If the application logs reference external services, check those service containers for corresponding errors.

Cross-reference container logs with file-based logs using timestamps. Container log timestamps may have slight offsets from application timestamps due to buffering.

## Step 10: Generate Investigation Report

Compile all findings into a structured investigation report:

```
## Log Investigation Report

**Date**: <timestamp>
**Scope**: <log sources examined>
**Time Range**: <start> to <end>
**Total Entries Analyzed**: <count>

### Summary

<2-3 sentence overview of findings>

### Error Statistics

| Level    | Count | Rate (per hour) |
|----------|-------|-----------------|
| FATAL    | 0     | 0               |
| ERROR    | 47    | 15.7            |
| WARNING  | 123   | 41.0            |

### Timeline of Key Events

<Abbreviated timeline showing the most significant events>

### Error Clusters

1. **Cluster at 10:30-10:35**: 23 errors, primarily connection pool exhaustion.
   Preceded by: slow query warnings starting at 10:28.
   Likely cause: database performance degradation caused pool saturation.

### Root Cause Hypothesis

Based on the analysis, the most likely root cause is: <hypothesis>.

Evidence supporting this:
- <evidence point 1>
- <evidence point 2>
- <evidence point 3>

### Affected Components

- <component 1>: <how affected>
- <component 2>: <how affected>

### Recommendations

1. **Immediate**: <action to resolve the current issue>
2. **Short-term**: <action to prevent recurrence>
3. **Long-term**: <structural improvement>
```

### Common Log Patterns and Their Meanings

For reference during analysis, these are common patterns and what they typically indicate:

- Repeated connection refused errors to a specific host/port: the target service is down or unreachable.
- Gradual increase in response times followed by timeouts: resource exhaustion or memory leak in the target service.
- Authentication failures in bursts: potential credential rotation issue or unauthorized access attempt.
- "Too many open files" errors: file descriptor limit reached, often due to connection leaks.
- OOM kill messages in system logs: a process exceeded its memory limit; check for memory leaks or insufficient limits.
- Periodic exact-same errors: a cron job or scheduled task is failing consistently.
- Errors immediately after deployment markers: the deployment introduced a bug.

Always present findings with confidence levels. Distinguish between confirmed facts (directly observed in logs) and hypotheses (inferred from patterns). Recommend specific next steps for confirming or refuting each hypothesis.

## Related Skills

- **container-dashboard** (eskill-system): Run container-dashboard before this skill to identify which containers are producing error logs.
- **monitoring-config** (eskill-devops): Follow up with monitoring-config after this skill to add alerting rules for the log patterns discovered.
