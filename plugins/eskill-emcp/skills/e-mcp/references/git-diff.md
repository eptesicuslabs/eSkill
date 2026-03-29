# Git and Diff Servers

## @emcp/server-git (6 tools)

Read-only git operations using isomorphic-git (pure JS, no git binary required). All operations require a `repository` path parameter pointing to a directory containing a `.git` folder.

### git_status

List changed files in a repository.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `repository` | string | yes | | Path to git repository |

Returns file paths with status indicators (modified, added, deleted, untracked).

### git_log

List commit history.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `repository` | string | yes | | Path to git repository |
| `limit` | number | no | 10 | Maximum commits to return |

Returns commit hash, author, date, and message for each entry.

### git_diff

Return changed files with diff data.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `repository` | string | yes | | Path to git repository |

Uses isomorphic-git status matrix to identify changes between HEAD, working tree, and staging area.

### git_show

Read a file from a specific ref (branch, tag, or commit).

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `repository` | string | yes | | Path to git repository |
| `path` | string | yes | | File path relative to repo root |
| `ref` | string | no | "HEAD" | Git ref (branch, tag, or commit SHA) |

### git_branches

List all branches (local).

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `repository` | string | yes | | Path to git repository |

### git_tags

List all tags.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `repository` | string | yes | | Path to git repository |

---

## @emcp/server-diff (4 tools)

Compare files, text, and directories. Uses patience diff algorithm by default for more readable output.

### diff_files

Compare two files.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `fileA` | string | yes | | First file path |
| `fileB` | string | yes | | Second file path |
| `contextLines` | number | no | | Lines of context around changes |
| `algorithm` | "myers" \| "patience" | no | "patience" | Diff algorithm |

### diff_text

Compare two text strings.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `textA` | string | yes | | First text |
| `textB` | string | yes | | Second text |
| `labelA` | string | no | "a" | Label for first text |
| `labelB` | string | no | "b" | Label for second text |
| `mode` | "lines" \| "words" | no | "lines" | Comparison granularity |

### diff_dirs

Compare two directories.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `dirA` | string | yes | | First directory |
| `dirB` | string | yes | | Second directory |
| `deep` | boolean | no | false | Recurse into subdirectories |

### diff_apply

Apply a unified diff patch to a file. Requires `allowWrite` in server config.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `file` | string | yes | | Target file path |
| `patch` | string | yes | | Unified diff content |
