---
name: e-ports
description: "Detects and resolves port conflicts between dev services, Docker containers, and config files. Use when services fail to start, debugging address-in-use errors, or setting up multiple local services. Also applies when: 'port already in use', 'address in use error', 'which process is using port 3000', 'port conflict'."
---

# Port Conflict Resolver

This skill detects and resolves port conflicts between development services, Docker containers, and application configuration files. It maps all port usage across the local system and project configuration, identifies conflicts, and provides resolution options including process termination, port reassignment, and configuration updates.

## Prerequisites

Identify the context for the port conflict. The user may report:

- A specific error message (e.g., "EADDRINUSE: address already in use :::3000").
- A service that fails to start without a clear error.
- A request to audit all port usage before starting a new project.
- A need to run multiple instances of the same service on different ports.

Extract the specific port number(s) from the error message if provided.

## Step 1: Map Running Processes to Ports

Use `sys_procs` to retrieve the list of running processes and their network connections.

For each process with active network listeners, record:

| PID | Process Name | Port | Protocol | State | User | Command |
|-----|-------------|------|----------|-------|------|---------|
| 1234 | node | 3000 | TCP | LISTEN | deyan | node server.js |
| 5678 | postgres | 5432 | TCP | LISTEN | postgres | /usr/lib/postgresql/15/bin/postgres |
| 9012 | python | 8000 | TCP | LISTEN | deyan | python manage.py runserver |

Use `shell` to supplement process information with network connection details:

- On Linux/macOS: `lsof -i -P -n | grep LISTEN` or `ss -tlnp`
- On Windows: `netstat -ano | findstr LISTENING`

Group listeners by port number. A port with multiple listeners (on different interfaces) should be noted, as this can cause subtle conflicts (e.g., one service on `127.0.0.1:3000` and another on `0.0.0.0:3000`).

If a specific port was reported in the error, highlight the process occupying that port.

## Step 2: Map Docker Container Ports

Use `docker_ps` to list running Docker containers and their port mappings.

For each container with published ports, record:

| Container | Image | Host Port | Container Port | Protocol | Status |
|-----------|-------|-----------|---------------|----------|--------|
| my-postgres | postgres:15 | 5432 | 5432 | TCP | Running |
| my-redis | redis:7 | 6379 | 6379 | TCP | Running |
| my-app | my-app:dev | 3000 | 3000 | TCP | Running |

Also check for Docker Compose port mappings by reading `docker-compose.yml` with `data_file_read`:

```yaml
services:
  db:
    ports:
      - "5432:5432"    # Host port 5432 -> Container port 5432
  cache:
    ports:
      - "6379:6379"
  app:
    ports:
      - "3000:3000"
```

Note: Docker port mappings can conflict with both native processes and other Docker containers. A Docker container publishing port 5432 will conflict with a locally installed PostgreSQL on the same port.

## Step 3: Scan Project Configuration for Port References

Use `filesystem` and `data_file_read` to find all port references in the project configuration.

Search these files for port numbers:

| File Pattern | Port Location |
|-------------|---------------|
| `.env`, `.env.local`, `.env.development` | `PORT=`, `DB_PORT=`, `REDIS_PORT=` variables |
| `docker-compose.yml` | `ports:` sections |
| `package.json` | `scripts` section (e.g., `--port 3000`) |
| `vite.config.*`, `webpack.config.*` | `devServer.port`, `server.port` |
| `next.config.*` | Port configuration |
| `application.properties`, `application.yml` | `server.port` |
| `nginx.conf`, `httpd.conf` | `listen` directives |
| `Caddyfile` | Address with port |
| `Procfile` | Port references in commands |
| `kubernetes/*.yaml` | `containerPort`, `targetPort`, `nodePort` |
| `Dockerfile` | `EXPOSE` directives |

For each port reference found, record:

| File | Port | Variable/Config Key | Service |
|------|------|-------------------|---------|
| .env | 3000 | PORT | Application server |
| .env | 5432 | DB_PORT | PostgreSQL |
| docker-compose.yml | 5432 | db.ports | PostgreSQL container |
| docker-compose.yml | 6379 | cache.ports | Redis container |

## Step 4: Identify Conflicts

Compare all three port maps (running processes, Docker containers, project configuration) to identify conflicts.

A conflict exists when:

1. **Process vs process**: Two non-Docker processes listen on the same port and interface.
2. **Process vs Docker**: A native process listens on a port that a Docker container wants to publish.
3. **Docker vs Docker**: Two Docker containers attempt to publish the same host port.
4. **Config vs running**: The project configuration specifies a port that is already occupied by an unrelated process.
5. **Config vs config**: Two configuration files within the project specify the same port for different services.

For each conflict, determine:

| Conflict | Port | Service A | Service B | Severity |
|----------|------|-----------|-----------|----------|
| Process vs Docker | 5432 | Local PostgreSQL (PID 5678) | Docker postgres container | High |
| Config vs running | 3000 | Project .env PORT=3000 | Unrelated node process (PID 1234) | Medium |
| Config vs config | 8080 | docker-compose app | docker-compose admin-panel | High |

## Step 5: Diagnose the Specific Conflict

For the primary conflict (the one causing the user's error), provide detailed diagnostic information.

1. **Identify the blocking process**: Use `shell` to get detailed information about the process occupying the port.
   - Process name and command line.
   - Process start time (how long it has been running).
   - Parent process (did it spawn from a known tool like Docker, VS Code, or a package manager?).
   - Memory and CPU usage.

2. **Determine if the process is needed**: Check whether the blocking process is:
   - A leftover from a previous development session (orphaned process).
   - Part of a currently running project.
   - A system service that should remain running.
   - A Docker container that was not stopped.

3. **Check for zombie containers**: Use `docker_ps` to check for stopped containers that may have reserved port mappings. Docker containers in "Exited" state do not hold ports, but containers in "Created" or partially started states may.

## Step 6: Present Resolution Options

Offer the user multiple resolution strategies, ordered by recommendation.

**Option 1: Terminate the blocking process** (when the process is unnecessary)

- Provide the specific command to stop the process:
  - Graceful: `kill <PID>` (SIGTERM) or stopping the service.
  - Forceful: `kill -9 <PID>` (SIGKILL) as a last resort.
  - Docker: `docker stop <container>` or `docker compose down`.
- Warn if the process appears to be a system service or is owned by another user.

**Option 2: Change the port of the new service** (when both services are needed)

- Identify the configuration file where the port can be changed.
- Suggest a new port number that is not in use.
- List all files that need to be updated for the port change to take effect.
- Verify the replacement port is available.

**Option 3: Change the port of the existing service** (when the new service has a fixed port requirement)

- Identify how the existing service's port is configured.
- Suggest the reconfiguration steps.

**Option 4: Use port forwarding or proxying** (for complex setups)

- Suggest running one service on a different port and using a reverse proxy.
- Provide a minimal nginx or Caddy configuration for the proxy.

## Step 7: Execute the Chosen Resolution

After the user selects an option, execute it.

**For process termination**:
1. Use `shell` to send the appropriate signal.
2. Wait briefly and verify the process has stopped.
3. Verify the port is now free using `shell` to check listeners.

**For port reassignment**:
1. Select an available port. Standard alternatives for common services:

| Service | Default Port | Common Alternatives |
|---------|-------------|-------------------|
| HTTP server | 3000 | 3001, 3002, 8080, 8081 |
| PostgreSQL | 5432 | 5433, 5434 |
| MySQL | 3306 | 3307, 3308 |
| Redis | 6379 | 6380, 6381 |
| MongoDB | 27017 | 27018, 27019 |
| Elasticsearch | 9200 | 9201, 9202 |
| Nginx | 80/443 | 8080/8443 |

2. Use `filesystem` to update all configuration files that reference the old port.
3. If Docker Compose is involved, update the port mapping in `docker-compose.yml`.
4. If environment variables are involved, update `.env` files.
5. Verify the new port is free before committing the change.

## Step 8: Verify Resolution

After applying the fix, verify the conflict is resolved.

1. Use `shell` to confirm the previously conflicted port is in the expected state:
   - If a process was killed: port should be free.
   - If a port was reassigned: old port should be free, new port should be free (before starting the service).
2. If the user's service can be started, attempt to start it and verify it binds successfully.
3. Re-run the port scan from Step 1 to confirm no new conflicts were introduced by the resolution.

## Step 9: Generate Port Allocation Map

Produce a comprehensive port allocation map for the project to prevent future conflicts.

```
## Port Allocation Map

**Project**: <name>
**Generated**: <date>

### Active Port Assignments

| Port | Service | Source | Protocol | Interface |
|------|---------|--------|----------|-----------|
| 3000 | Application server | .env PORT | TCP | 0.0.0.0 |
| 5432 | PostgreSQL | docker-compose.yml | TCP | 0.0.0.0 |
| 6379 | Redis | docker-compose.yml | TCP | 0.0.0.0 |
| 8080 | Admin panel | .env ADMIN_PORT | TCP | 127.0.0.1 |

### Reserved Ports (configured but not currently running)

| Port | Service | Source |
|------|---------|--------|
| 9090 | Prometheus | docker-compose.monitoring.yml |
| 3100 | Grafana Loki | docker-compose.monitoring.yml |

### Available Port Ranges for New Services

| Range | Suitable For |
|-------|-------------|
| 3001-3009 | Additional application instances |
| 8081-8089 | Additional HTTP services |
| 9091-9099 | Monitoring and metrics |
```

Suggest adding this map to the project documentation for team reference.

## Step 10: Recommend Prevention Measures

Suggest practices to prevent future port conflicts.

1. **Centralized port configuration**: Keep all port assignments in a single `.env` file or configuration document rather than scattered across files.
2. **Docker Compose for isolation**: Use Docker networks and internal DNS instead of publishing every port to the host. Services within a Docker network can communicate by service name without host port mapping.
3. **Dynamic port assignment**: For test environments, use port 0 (OS-assigned) and read the actual port from the server after startup.
4. **Port checking in startup scripts**: Add a port availability check to the project's startup script that warns before attempting to bind.
5. **Documentation**: Maintain the port allocation map from Step 9 in the project README or a dedicated ops document.

## Edge Cases

- **Ephemeral ports**: Some conflicts involve ephemeral ports (typically 49152-65535) used by outgoing connections. These resolve themselves when the connection closes. If a conflict involves an ephemeral port, waiting a few seconds may be sufficient.
- **IPv4 vs IPv6**: A process listening on `::1:3000` (IPv6 localhost) may not conflict with `127.0.0.1:3000` (IPv4 localhost) depending on the OS and application configuration. Some frameworks bind to both by default.
- **Permission-restricted ports**: Ports below 1024 require root/admin privileges on most systems. If the conflict involves a low port, the resolution may require elevated permissions.
- **WSL and host machine**: On Windows with WSL, ports can conflict between the Windows host and WSL environments. A service in WSL binding to port 3000 may also be accessible on the Windows host, and vice versa.
- **Multiple Docker Compose files**: Projects using multiple Compose files (`docker-compose.yml`, `docker-compose.override.yml`, `docker-compose.dev.yml`) may have port definitions spread across files. Check all Compose files.
- **VPN and tunnel software**: VPN clients and tools like ngrok, cloudflared, or SSH tunnels can occupy ports. Check for these if the blocking process is not a standard development tool.

## Related Skills

- **e-procs** (eskill-system): Run e-procs before this skill to identify the processes that are causing port conflicts.
- **e-containers** (eskill-system): Run e-containers before this skill to check whether containerized services are involved in the port conflict.
