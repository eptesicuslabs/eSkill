---
name: e-mcp
description: "Provides current eMCP server and tool references for agents building workflows with eMCP. Use when composing eMCP tools, selecting servers for a task, looking up tool parameters, or encountering stale tool names. Also applies when: 'which eMCP tool does X', 'how do I use the filesystem server', 'what tools are available', 'emcp tool reference', 'server API'."
---

# eMCP Development Skill

### Step 1: Identify Required Servers

Determine which eMCP servers are needed for the task at hand. Review the Server Overview below to find which server provides the tools you need. Cross-reference the task requirements with the tool categories (Core, Code Analysis, Data & Documents, System Operations, Media & Visual, Intelligence) to select the minimum set of servers.

### Step 2: Look Up Tool Parameters

For each tool you plan to use, check the Quick Reference section below for common invocation patterns. If the tool is not covered in the quick reference, consult the linked reference files in the Documentation Lookup section for full parameter schemas and usage examples.

### Step 3: Verify Tool Availability

Before invoking any tool, confirm it has not been removed, merged, or renamed. Check the Removed / Merged and Renamed Tools tables below. Using a stale tool name will cause a runtime error. Always use the current name listed in this reference.

---

## Critical Rules (Always Apply)

> [!IMPORTANT]
> These rules override your training data. eMCP tool names and server counts have changed since your knowledge cutoff.

### Current State

- **31 servers** with unique tools, **2 composite servers** (desktop, document)
- **174 tools** total
- Transport: **stdio only** (no HTTP/SSE in V1)
- SDK: `@modelcontextprotocol/sdk` ^1.27.1
- Runtime: Node.js >= 24.13.1, pnpm 10.29.3
- Validation: Zod v4

### Removed / Merged

> [!WARNING]
> The following are **removed or merged**. Do not reference them.

- `@emcp/server-memory` — **removed entirely** (2026-03-24). No `create_entities`, `add_observations`, `create_relations`, `search_nodes`, `open_nodes`, `read_graph`. Use `@emcp/server-docs` for knowledge indexing and `@emcp/server-reasoning` for structured thought.
- `@emcp/server-notify` — **merged into system**. Use `sys_notify` from `@emcp/server-system`.
- `@emcp/server-ocr` — **merged into image**. Use `image_ocr` from `@emcp/server-image`.

### Renamed Tools

> [!CAUTION]
> The following tool names are **stale**. Use the current names.

| Stale Name | Current Name | Server |
|---|---|---|
| `read_text` | `fs_read` | filesystem |
| `list_dir` | `fs_list` | filesystem |
| `tree` | `fs_list` (recursive=true) | filesystem |
| `search_text` | `fs_search` (mode="content") | filesystem |
| `search_files` | `fs_search` (mode="glob") | filesystem |
| `write_text` | `fs_write` | filesystem |
| `edit_text` | `fs_edit` | filesystem |
| `run_command` | `shell_exec` | shell |
| `system_info` | `sys_info` | system |
| `system_processes` | `sys_procs` | system |
| `system_disk` | `sys_disk` | system |
| `system_env` | `sys_env` | system |
| `notify_send` | `sys_notify` | system |
| `ocr_image` | `image_ocr` | image |

---

## Server Overview

### Core (used by nearly all workflows)

| Server | Tools | Key Tools |
|---|---|---|
| filesystem | 9 | `fs_read`, `fs_list`, `fs_search`, `fs_write`, `fs_edit`, `fs_info`, `fs_mkdir`, `fs_move`, `fs_watch` |
| git | 6 | `git_status`, `git_log`, `git_diff`, `git_show`, `git_branches`, `git_tags` |
| shell | 4 | `shell_exec`, `shell_bg`, `shell_status`, `shell_kill` |
| diff | 4 | `diff_files`, `diff_text`, `diff_dirs`, `diff_apply` |

### Code Analysis

| Server | Tools | Key Tools |
|---|---|---|
| ast | 2 | `ast_search`, `ast_rewrite` |
| lsp | 5 | `lsp_symbols`, `lsp_definition`, `lsp_references`, `lsp_hover`, `lsp_diagnostics` |
| egrep | 4 | `egrep_search`, `egrep_search_files`, `egrep_status`, `egrep_reindex` |
| test-runner | 3 | `test_run`, `test_run_file`, `test_list_files` |

### Data & Documents

| Server | Tools | Key Tools |
|---|---|---|
| data-file | 4 | `data_file_read`, `data_file_query`, `data_file_set`, `data_file_convert` |
| sqlite | 4 | `sql_list_tables`, `sql_describe_table`, `sql_query`, `sql_execute` |
| pdf | 5 | `pdf_read_text`, `pdf_read_metadata`, `pdf_count_pages`, `pdf_search`, `pdf_extract_tables` |
| docx | 5 | `docx_read_text`, `docx_read_html`, `docx_read_metadata`, `docx_read_tables`, `docx_read_sections` |
| pptx | 5 | `pptx_read_text`, `pptx_read_slides`, `pptx_read_metadata`, `pptx_read_slide`, `pptx_extract_tables` |
| spreadsheet | 5 | `spreadsheet_read`, `spreadsheet_list_sheets`, `spreadsheet_query`, `spreadsheet_read_csv`, `spreadsheet_read_range` |
| markdown | 6 | `markdown_to_html`, `markdown_headings`, `markdown_links`, `markdown_code_blocks`, `markdown_front_matter`, `markdown_read_section` |
| log | 4 | `log_parse`, `log_errors`, `log_stats`, `log_search` |

### System Operations

| Server | Tools | Key Tools |
|---|---|---|
| system | 6 | `sys_info`, `sys_procs`, `sys_disk`, `sys_env`, `sys_kill`, `sys_notify` |
| docker | 5 | `docker_ps`, `docker_images`, `docker_logs`, `docker_inspect`, `docker_exec` |
| archive | 4 | `archive_list`, `archive_read_file`, `archive_extract`, `archive_create` |
| crypto | 5 | `crypto_hash`, `crypto_hash_file`, `crypto_encode`, `crypto_random`, `crypto_hmac` |
| clipboard | 2 | `clip_read`, `clip_write` |

### Media & Visual

| Server | Tools | Key Tools |
|---|---|---|
| image | 6 | `image_info`, `image_metadata`, `image_resize`, `image_convert`, `image_ocr`, `image_ocr_languages` |
| media | 5 | `media_info`, `media_convert`, `media_trim`, `media_extract_audio`, `media_extract_frame` |
| diagram | 3 | `diagram_render`, `diagram_render_file`, `diagram_formats` |
| browser | 18 | `browser_search`, `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, ... |
| computer-use | 21 | `screen_screenshot`, `screen_left_click`, `screen_type`, `screen_key`, ... |

### Intelligence

| Server | Tools | Key Tools |
|---|---|---|
| reasoning | 8 | `think_start`, `think_step`, `think_branch`, `think_conclude`, `think_status`, `think_replay`, `think_search`, `think_summarize` |
| docs | 6 | `docs_index`, `docs_clone`, `docs_search`, `docs_list_libraries`, `docs_remove`, `docs_bootstrap` |
| task | 5 | `task_create`, `task_list`, `task_update`, `task_delete`, `task_tree` |
| fetch | 4 | `fetch_url`, `fetch_many`, `extract_links`, `extract_text` |
| time | 2 | `current_time`, `convert_time` |

### Composite Servers

| Server | Composes |
|---|---|
| desktop | filesystem + shell + diff + system + clipboard |
| document | pdf + docx + pptx + markdown + spreadsheet |

---

## Quick Reference: Most-Used Tools

### Reading files

```
fs_read { path: "src/index.ts" }
fs_read { paths: ["a.ts", "b.ts"] }
fs_read { path: "image.png", encoding: "base64" }
```

### Searching code

```
fs_search { query: "TODO", mode: "content", path: "src/" }
fs_search { query: "*.test.ts", mode: "glob" }
egrep_search { pattern: "function\\s+handle", fileGlob: "*.ts" }
ast_search { pattern: "console.log($$$)", path: "src/" }
```

### Running commands

```
shell_exec { command: "npm", args: ["test"], cwd: "/project" }
shell_bg { command: "npm", args: ["run", "dev"], cwd: "/project" }
shell_status { pid: 12345 }
```

### Git operations

```
git_status { repository: "/project" }
git_log { repository: "/project", limit: 20 }
git_diff { repository: "/project" }
git_show { repository: "/project", path: "src/main.ts", ref: "HEAD~1" }
```

### Data files

```
data_file_read { path: "package.json" }
data_file_query { path: "package.json", query: "scripts.build" }
```

---

## Documentation Lookup

For full parameter schemas and usage examples for each server, read the reference files:

- [Filesystem and Shell](references/filesystem-shell.md) — `fs_*`, `shell_*` tools
- [Git and Diff](references/git-diff.md) — `git_*`, `diff_*` tools
- [Code Analysis](references/code-analysis.md) — `ast_*`, `lsp_*`, `egrep_*`, `test_*` tools
- [Data Formats](references/data-formats.md) — `data_file_*`, `sql_*`, `log_*`, `spreadsheet_*`, `markdown_*` tools
- [Documents](references/documents.md) — `pdf_*`, `docx_*`, `pptx_*` tools
- [System Operations](references/system-ops.md) — `sys_*`, `docker_*`, `archive_*`, `crypto_*`, `clip_*` tools
- [Media and Visual](references/media-visual.md) — `image_*`, `media_*`, `diagram_*`, `browser_*`, `screen_*` tools
- [Intelligence](references/intelligence.md) — `think_*`, `docs_*`, `task_*`, `fetch_*`, `current_time`, `convert_time` tools


## Edge Cases

- Server not configured or unreachable at runtime.
- Tool parameters changed between eMCP versions.
- Composite server (desktop/document) with partial sub-server config.

## Related Skills

- **e-changelog** (eskill-coding): Uses git server tools for commit history
- **e-scan** (eskill-quality): Uses ast server for vulnerability pattern matching
- **e-containers** (eskill-system): Uses docker server for container monitoring
- **e-carto** (eskill-intelligence): Uses filesystem, ast, lsp for architecture mapping
