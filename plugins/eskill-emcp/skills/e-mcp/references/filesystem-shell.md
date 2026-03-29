# Filesystem and Shell Servers

## @emcp/server-filesystem (9 tools)

Read, write, search, and manage files within configured root directories. All paths are validated against allowed roots with symlink and traversal protection.

### fs_read

Read one or more text files.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | one of path/paths | | Single file path |
| `paths` | string[] | one of path/paths | | Multiple file paths |
| `encoding` | "utf8" \| "base64" | no | "utf8" | Use "base64" for binary files |

### fs_list

List a directory. Use recursive mode for tree views.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Directory path |
| `recursive` | boolean | no | false | Recurse into subdirectories |
| `maxDepth` | number | no | 1 | Maximum recursion depth (max 10) |

Replaces the legacy `list_dir` and `tree` tools. For tree-style output, use `recursive: true` with an appropriate `maxDepth`.

### fs_search

Search files by content or name.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | string | yes | | Regex pattern (content mode) or glob pattern (glob mode) |
| `mode` | "content" \| "glob" | no | "content" | Search mode |
| `path` | string | no | | Directory to search in |
| `caseSensitive` | boolean | no | false | Case-sensitive matching |
| `maxResults` | number | no | 50 | Maximum results |
| `maxFileSize` | number | no | | Skip files larger than N bytes |
| `includeGlobs` | string[] | no | | Only search files matching these globs |
| `excludeGlobs` | string[] | no | | Skip files matching these globs |

Replaces the legacy `search_text` (mode="content") and `search_files` (mode="glob") tools.

### fs_info

Get file or directory metadata (size, timestamps, permissions).

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | File or directory path |

### fs_write

Write text to a file. Creates parent directories if needed.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | File path |
| `text` | string | yes | | Content to write |

### fs_edit

Apply exact text replacements to a file.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | File path |
| `edits` | {oldText, newText}[] | yes | | Array of replacements |

Each edit object has `oldText` (string to find) and `newText` (replacement). Applied sequentially.

### fs_mkdir

Create a directory (and parents).

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Directory path |

### fs_move

Move or rename a file or directory.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `source` | string | yes | | Source path |
| `destination` | string | yes | | Destination path |

### fs_watch

Watch a directory for changes. First call starts watching; subsequent calls return events since last check.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Directory path |

---

## @emcp/server-shell (4 tools)

Execute commands within configured working directories. Commands must be in the allowlist. Supports foreground execution with timeout, background processes, and process management.

### shell_exec

Run an allowlisted command.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `command` | string | yes | | Command name (must be allowlisted) |
| `args` | string[] | no | [] | Command arguments |
| `cwd` | string | yes | | Working directory (must be in allowed roots) |
| `env` | Record<string,string> | no | | Additional environment variables |
| `stdin` | string | no | | Standard input data |
| `shell` | boolean | no | false | Run through shell (requires config flag) |

Replaces the legacy `run_command` tool.

### shell_bg

Start a background process. Returns PID for tracking.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `command` | string | yes | | Command name |
| `args` | string[] | no | [] | Command arguments |
| `cwd` | string | yes | | Working directory |
| `env` | Record<string,string> | no | | Additional environment variables |

Requires `allowBackground: true` in server config.

### shell_status

Check status of a background process.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `pid` | number | yes | | Process ID from shell_bg |

Returns buffered stdout/stderr since last check, plus running/exited status.

### shell_kill

Kill a background process.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `pid` | number | yes | | Process ID |
| `signal` | string | no | "SIGTERM" | Signal to send |
