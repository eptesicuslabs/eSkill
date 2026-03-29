# System Operations Servers

## @emcp/server-system (6 tools)

System information, process management, and notifications. The `sys_notify` tool was merged from the former standalone notify server.

### sys_info

Get OS, CPU, memory, network interfaces, and Node.js version.

No parameters.

### sys_procs

List running processes.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `filter` | string | no | | Filter by process name |
| `tree` | boolean | no | false | Show process tree |

### sys_disk

Get disk usage for all drives, or per-directory size.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | no | | Specific path to check (omit for all drives) |

### sys_env

Read allowlisted environment variables.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `names` | string[] | no | | Specific variable names (omit for all allowlisted) |

### sys_kill

Send a signal to a process.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `pid` | number | yes | | Process ID |
| `signal` | string | no | "SIGTERM" | Signal name |

### sys_notify

Send a native desktop notification.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `title` | string | no | | Notification title |
| `message` | string | yes | | Notification body |
| `sound` | boolean | no | | Play notification sound |

Replaces the legacy `notify_send` from the removed `@emcp/server-notify`.

---

## @emcp/server-docker (5 tools)

Docker container management. Read operations are always available; `docker_exec` requires `allowExec` in config.

### docker_ps

List containers.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `all` | boolean | no | false | Include stopped/exited containers |

### docker_images

List locally available images.

No parameters.

### docker_logs

Get container logs.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `container` | string | yes | | Container name or ID |
| `tail` | number | no | 100 | Number of log lines |

### docker_inspect

Inspect a container or image for detailed metadata.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `target` | string | yes | | Container or image name/ID |

### docker_exec

Execute a command inside a running container. Requires `allowExec`.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `container` | string | yes | | Container name or ID |
| `command` | string | yes | | Command to run |
| `args` | string[] | no | [] | Command arguments |

---

## @emcp/server-archive (4 tools)

ZIP archive operations. Write operations require `allowWrite`.

### archive_list

List entries in a ZIP archive.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Archive path |

### archive_read_file

Read a single file from an archive without extracting.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Archive path |
| `entry` | string | yes | | Entry path within archive |

### archive_extract

Extract all files. Requires `allowWrite`.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Archive path |
| `destination` | string | yes | | Extraction directory |

### archive_create

Create a ZIP archive. Requires `allowWrite`.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `outputPath` | string | yes | | Output archive path |
| `files` | string[] | yes | | Files to include |

---

## @emcp/server-crypto (5 tools)

Hashing, encoding, HMAC, and random generation.

### crypto_hash

Hash text.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `text` | string | yes | | Text to hash |
| `algorithm` | string | no | "sha256" | Hash algorithm |

### crypto_hash_file

Hash a file.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | File path |
| `algorithm` | string | no | "sha256" | Hash algorithm |

### crypto_encode

Encode or decode text.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `text` | string | yes | | Text to encode/decode |
| `encoding` | "base64" \| "base64url" \| "hex" | yes | | Encoding format |
| `direction` | "encode" \| "decode" | no | "encode" | Direction |

### crypto_random

Generate random bytes, hex, or UUID.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `type` | "bytes" \| "hex" \| "uuid" | no | "hex" | Output type |
| `length` | number | no | 32 | Byte length (for bytes/hex) |

### crypto_hmac

Compute HMAC.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `text` | string | yes | | Input text |
| `key` | string | yes | | Secret key |
| `algorithm` | string | no | "sha256" | Hash algorithm |

---

## @emcp/server-clipboard (2 tools)

System clipboard read/write. Write requires `allowWrite`.

### clip_read

Read current clipboard text.

No parameters.

### clip_write

Write text to clipboard. Requires `allowWrite`.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `text` | string | yes | | Text to copy |
