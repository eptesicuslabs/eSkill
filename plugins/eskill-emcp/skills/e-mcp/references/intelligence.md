# Intelligence Servers

## @emcp/server-reasoning (8 tools)

Persistent structured reasoning backed by SQLite. Supports multi-step chains with goals, branching, confidence tracking, evidence linking, cross-chain search, and summarization. Project-scoped.

### think_start

Start a new reasoning chain.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `goal` | string | yes | | What this chain aims to resolve |
| `context` | string | no | | Additional context |

Returns a `chainId` used by all subsequent tools.

### think_step

Add a reasoning step to a chain.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `chainId` | string | yes | | Chain ID from think_start |
| `type` | enum | yes | | One of: "thought", "hypothesis", "observation", "action", "reflection", "revision", "conclusion" |
| `content` | string | yes | | Step content |
| `confidence` | number | no | | Confidence level (0-1) |
| `parentStepId` | number | no | | Branch from a specific step |
| `branchLabel` | string | no | | Name for the branch |
| `revisesStepId` | number | no | | Step this revises |
| `evidenceFor` | number[] | no | | Step IDs this supports |
| `evidenceAgainst` | number[] | no | | Step IDs this contradicts |

### think_branch

Create a named branch to explore an alternative.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `chainId` | string | yes | | Chain ID |
| `label` | string | yes | | Branch name |
| `fromStepId` | number | no | | Branch point (defaults to latest step) |
| `reason` | string | no | | Why branching |

### think_conclude

Conclude a reasoning chain.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `chainId` | string | yes | | Chain ID |
| `conclusion` | string | yes | | Final answer |
| `confidence` | number | no | | Overall confidence (0-1) |

### think_status

Get chain status or list all chains.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `chainId` | string | no | | Specific chain (omit to list all) |

### think_replay

Replay the full reasoning trace.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `chainId` | string | yes | | Chain ID |
| `branch` | string | no | | Filter to specific branch |

### think_search

Search past reasoning chains via full-text search.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | string | yes | | Search query |
| `maxResults` | number | no | 10 | Maximum results |
| `global` | boolean | no | false | Search across all projects |

### think_summarize

Generate a structured summary of a chain.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `chainId` | string | yes | | Chain ID |

---

## @emcp/server-docs (6 tools)

Local documentation indexing and hybrid search. Clones git repos, parses markdown/text into code-aware chunks, indexes into SQLite FTS5 with trigram fallback. Hybrid BM25 + trigram + TF-IDF re-ranking. Replaces the need for the removed memory server for knowledge persistence use cases.

### docs_index

Index a local directory of documentation.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Directory containing docs |
| `library` | string | yes | | Library/project name |
| `version` | string | no | | Version (auto-detected from package manifests) |

### docs_clone

Clone a git repo and index its documentation.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `url` | string | yes | | Git repository URL |
| `library` | string | no | | Library name (defaults to repo name) |
| `version` | string | no | | Version |
| `branch` | string | no | | Specific branch |
| `shallow` | boolean | no | true | Shallow clone |

### docs_search

Search indexed documentation.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | string | yes | | Search query |
| `library` | string | no | | Filter to specific library |
| `maxResults` | number | no | | Maximum results |
| `topic` | string | no | | Topic filter |

### docs_list_libraries

List all indexed libraries with statistics.

No parameters.

### docs_remove

Remove all indexed documentation for a library.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `library` | string | yes | | Library name |

### docs_bootstrap

Bulk-index from node_modules or explicit library paths.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `libraries` | {name, path, version?}[] | one of | | Explicit library paths |
| `from` | "node_modules" | one of | | Auto-discover from node_modules |
| `path` | string | with `from` | | Project root for node_modules |

---

## @emcp/server-task (5 tools)

Task management with priority, status, dependencies, and hierarchy.

### task_create

Create a task.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `title` | string | yes | | Task title |
| `description` | string | no | | Task description |
| `priority` | "low" \| "medium" \| "high" \| "critical" | no | "medium" | Priority level |
| `parentId` | number | no | | Parent task ID |
| `dependsOn` | number[] | no | | Task IDs this depends on |

### task_list

List tasks with optional filters.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `status` | "todo" \| "in_progress" \| "done" \| "blocked" | no | | Filter by status |
| `priority` | "low" \| "medium" \| "high" \| "critical" | no | | Filter by priority |
| `parentId` | number | no | | Filter by parent |

### task_update

Update a task.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `id` | number | yes | | Task ID |
| `title` | string | no | | New title |
| `description` | string | no | | New description |
| `status` | "todo" \| "in_progress" \| "done" \| "blocked" | no | | New status |
| `priority` | "low" \| "medium" \| "high" \| "critical" | no | | New priority |

### task_delete

Delete a task.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `id` | number | yes | | Task ID |

### task_tree

Show task hierarchy.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `rootId` | number | no | | Root task (omit for full tree) |

---

## @emcp/server-fetch (4 tools)

HTTP fetching with SSRF protection (blocks localhost, private IPs, enforces host allowlists).

### fetch_url

Fetch a URL and return text content with metadata.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `url` | string (URL) | yes | | URL to fetch |

### fetch_many

Fetch multiple URLs in parallel.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `urls` | string[] (URLs) | yes | | URLs to fetch |

### extract_links

Fetch a URL and extract anchor links from HTML.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `url` | string (URL) | yes | | URL to extract links from |

### extract_text

Fetch a URL and extract normalized body text.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `url` | string (URL) | yes | | URL to extract text from |

---

## @emcp/server-time (2 tools)

Time queries and timezone conversion.

### current_time

Get the current time.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `timezone` | string | no | | IANA timezone (defaults to server config) |

### convert_time

Convert between timezones.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `sourceTimezone` | string | yes | | Source IANA timezone |
| `targetTimezone` | string | yes | | Target IANA timezone |
| `time` | string | yes | | Time in HH:MM format |
