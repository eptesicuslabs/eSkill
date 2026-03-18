# eSkill

eSkill is a Claude Code plugin marketplace of skills, subagents, and hooks that compose [eMCP](https://github.com/eptesicuslabs/eMCP) server tools into higher-level workflows. Where eMCP provides the primitives (`git_log`, `ast_search`, `sql_query`), eSkill provides the orchestration (changelog generation, codebase cartography, deployment checklists).

Both projects are local-only, MIT-licensed, and maintained by [Eptesicus Laboratories](https://github.com/eptesicuslabs).

## How eMCP and eSkill Relate

```
eMCP (tools)                          eSkill (workflows)
─────────────────────────             ─────────────────────────
git_log + git_show                 -> changelog-generation
git_diff + lsp_references + ast    -> code-review-prep
ast_search + ast_rewrite + test    -> refactoring-workflow
pdf_read + docx_read + pptx_read   -> document-to-markdown
lsp_symbols + ast_search + diagram -> diagram-from-code
docker_ps + docker_logs + log_*    -> container-dashboard
memory + docs + fetch + reasoning  -> research-workflow
crypto_hash_file + archive_create  -> backup-workflow
ast_search + lsp_diagnostics       -> security-scan
```

eMCP exposes 33 servers with ~130 tools. eSkill skills call sequences of those tools in deliberate order, handle edge cases, and produce structured output. A skill that wraps eMCP tools into a workflow is the intended use. A skill that reimplements what an eMCP server already does is waste.

## Installation

Install the full marketplace:

```
claude plugin install --marketplace https://github.com/eptesicuslabs/eSkill
```

Install a single plugin:

```
claude plugin install https://github.com/eptesicuslabs/eSkill --plugin eskill-coding
```

## Plugins

| Plugin | Domain | Skills | Agents |
|--------|--------|--------|--------|
| [eskill-coding](plugins/eskill-coding) | Git workflows, code review, testing, refactoring, API design, database, performance | 10 | 2 |
| [eskill-office](plugins/eskill-office) | Document conversion, data pipelines, diagrams, reports, presentations | 6 | - |
| [eskill-system](plugins/eskill-system) | Environment setup, Docker, log analysis, system diagnostics, backups | 6 | 1 |
| [eskill-intelligence](plugins/eskill-intelligence) | Codebase exploration, knowledge graphs, research, decisions, learning | 6 | 1 |
| [eskill-devops](plugins/eskill-devops) | CI/CD, infrastructure review, deployment, releases, monitoring | 5 | 1 |
| [eskill-quality](plugins/eskill-quality) | Security scanning, license compliance, code standards, accessibility | 6 | 1 |
| [eskill-meta](plugins/eskill-meta) | Project scaffolding, changelogs, session recaps, health dashboards | 5 | - |

**44 skills, 6 agents, 1 hook across 7 plugins.**

## Skill Reference

### Coding

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| changelog-generation | git, markdown | Generate changelogs from git commit history between refs |
| code-review-prep | git, lsp, ast, diff | Prepare code review summaries from diffs with semantic context |
| test-scaffolding | lsp, ast, filesystem, data-file | Generate test file scaffolds from code structure analysis |
| refactoring-workflow | ast, lsp, test-runner, diff, filesystem | Safe refactoring with AST rewriting and test verification loops |
| dependency-audit | data-file, shell, ast, filesystem | Audit dependencies for vulnerabilities, outdated versions, unused packages |
| api-surface-map | lsp, ast, filesystem | Extract and document public API surface |
| database-workflow | sqlite, filesystem, diff | Plan and validate database schema changes with migrations |
| performance-analysis | shell, log, lsp, ast | Profile, benchmark, and identify performance bottlenecks |
| branch-cleanup | git | Identify and manage stale git branches |
| merge-conflict-resolution | git, lsp, filesystem, test-runner | Systematic merge conflict resolution with semantic context |

### Office

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| document-to-markdown | pdf, docx, pptx, ocr, filesystem | Convert PDF, DOCX, PPTX to clean markdown |
| data-pipeline | spreadsheet, sqlite, filesystem | Import spreadsheet/CSV data into SQLite for querying and export |
| diagram-from-code | lsp, ast, diagram, filesystem | Generate architecture diagrams from codebase structure |
| report-builder | spreadsheet, sqlite, log, git, diagram, markdown | Compile structured reports from multiple data sources |
| presentation-extract | pptx, filesystem | Extract content and speaker notes from PowerPoint files |
| spreadsheet-validation | spreadsheet, filesystem | Validate spreadsheet data against configurable rules |

### System

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| environment-validate | system, shell, filesystem, data-file | Validate development environment against project requirements |
| container-dashboard | docker, log, notify | Docker container health overview with logs and metrics |
| log-investigation | log, docker, filesystem | Investigate issues through log parsing and timeline construction |
| system-snapshot | system, docker, shell, filesystem, crypto | Capture comprehensive system state for diagnostics |
| backup-workflow | archive, crypto, filesystem | Create verified backups with checksums and rotation |
| process-analysis | system, shell | Analyze running processes for resource consumption issues |

### Intelligence

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| codebase-cartography | filesystem, ast, lsp, memory, data-file | Map codebase architecture into navigable knowledge graphs |
| knowledge-graph-build | filesystem, memory, markdown, docs | Build knowledge graphs from project documentation and code |
| research-workflow | docs, fetch, memory, reasoning | Structured research with source gathering and synthesis |
| decision-framework | reasoning, memory | Guided decision-making with options analysis and ADR output |
| context-export | memory, git, filesystem | Export project context for session handoffs |
| learning-navigator | filesystem, lsp, ast, memory, git | Systematic exploration of unfamiliar codebases |

### DevOps

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| ci-config-generator | data-file, filesystem, shell | Generate CI/CD pipeline configs from project structure |
| infrastructure-review | filesystem, data-file, diff | Review IaC files for best practices and security |
| deployment-checklist | test-runner, shell, git, data-file, notify | Pre-deployment verification workflow |
| release-workflow | git, data-file, diff, markdown | Version bumping, tagging, changelog, and release notes |
| monitoring-config | ast, filesystem, data-file, log | Generate monitoring and alerting configurations |

### Quality

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| security-scan | ast, filesystem, lsp | Scan code for OWASP Top 10 vulnerabilities using AST patterns |
| license-check | data-file, filesystem, shell | Verify license compatibility across dependencies |
| code-standards | ast, lsp, shell, filesystem | Enforce coding standards with AST and LSP analysis |
| configuration-audit | data-file, filesystem, diff | Compare configs across environments to detect drift |
| file-integrity | crypto, filesystem | Create and verify checksum manifests for change detection |
| accessibility-scan | ast, filesystem | Scan frontend code for WCAG accessibility violations |

### Meta

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| project-scaffold | filesystem, data-file, shell, git | Initialize projects with directory structure and toolchain |
| changelog-maintain | git, markdown, filesystem | Maintain CHANGELOG.md in Keep a Changelog format |
| session-recap | git, test-runner, memory, task | Summarize work completed in the current session |
| project-health | test-runner, lsp, data-file, markdown, git, diagram | Generate project health dashboards with quality scores |
| issue-decompose | reasoning, ast, lsp, task, filesystem | Break complex issues into actionable subtasks |

## eMCP Server Coverage

Every eMCP server is used by at least one eSkill skill. The following table shows full coverage:

| eMCP Server | Tools Used | eSkill Plugins |
|-------------|-----------|----------------|
| `@emcp/server-filesystem` | `read_text`, `list_dir`, `tree`, `search_text`, `search_files`, `write_text`, `edit_text` | all |
| `@emcp/server-git` | `git_status`, `git_log`, `git_diff`, `git_show`, `git_branches`, `git_tags` | coding, devops, meta, intelligence |
| `@emcp/server-ast` | `ast_search`, `ast_rewrite` | coding, office, quality, intelligence |
| `@emcp/server-lsp` | `lsp_symbols`, `lsp_definition`, `lsp_references`, `lsp_hover`, `lsp_diagnostics` | coding, office, quality, intelligence, meta |
| `@emcp/server-shell` | `run_command` | coding, system, devops, quality, meta |
| `@emcp/server-test-runner` | `test_run`, `test_run_file`, `test_list_files` | coding, devops, meta |
| `@emcp/server-memory` | `create_entities`, `add_observations`, `create_relations`, `search_nodes`, `open_nodes`, `read_graph` | intelligence, meta |
| `@emcp/server-reasoning` | `think_start`, `think_step`, `think_branch`, `think_conclude` | intelligence, meta |
| `@emcp/server-docker` | `docker_ps`, `docker_logs`, `docker_inspect`, `docker_exec` | system, devops |
| `@emcp/server-log` | `log_parse`, `log_errors`, `log_stats`, `log_search` | system, devops |
| `@emcp/server-sqlite` | `sql_list_tables`, `sql_describe_table`, `sql_query`, `sql_execute` | office, coding |
| `@emcp/server-pdf` | `pdf_read_text`, `pdf_read_metadata`, `pdf_count_pages` | office |
| `@emcp/server-docx` | `docx_read_text`, `docx_read_html`, `docx_read_metadata` | office |
| `@emcp/server-pptx` | `pptx_read_text`, `pptx_read_slides`, `pptx_read_metadata` | office |
| `@emcp/server-spreadsheet` | `spreadsheet_read`, `spreadsheet_list_sheets`, `spreadsheet_query`, `spreadsheet_read_csv` | office |
| `@emcp/server-markdown` | `markdown_to_html`, `markdown_headings`, `markdown_links`, `markdown_code_blocks` | office, meta, intelligence |
| `@emcp/server-diagram` | `diagram_render`, `diagram_render_file` | office, meta |
| `@emcp/server-diff` | `diff_files`, `diff_text`, `diff_dirs` | coding, quality, devops |
| `@emcp/server-data-file` | `data_file_read`, `data_file_query`, `data_file_set`, `data_file_convert` | coding, devops, quality, meta, system |
| `@emcp/server-crypto` | `crypto_hash_file`, `crypto_hmac`, `crypto_hash` | system, quality |
| `@emcp/server-archive` | `archive_create`, `archive_list`, `archive_extract` | system |
| `@emcp/server-system` | `system_info`, `system_processes`, `system_disk`, `system_env` | system |
| `@emcp/server-notify` | `notify_send` | system, devops |
| `@emcp/server-docs` | `docs_index`, `docs_clone`, `docs_search` | intelligence |
| `@emcp/server-fetch` | `fetch_url`, `extract_text` | intelligence |
| `@emcp/server-task` | `task_create`, `task_list`, `task_tree` | meta |
| `@emcp/server-ocr` | `ocr_image` | office |
| `@emcp/server-browser` | `browser_search`, `browser_navigate` | intelligence |
| `@emcp/server-image` | `image_info`, `image_resize` | office |
| `@emcp/server-media` | `media_info`, `media_convert` | office |
| `@emcp/server-clipboard` | `clipboard_read`, `clipboard_write` | system |
| `@emcp/server-computer-use` | `screen_screenshot`, `screen_click` | system |
| `@emcp/server-time` | `current_time`, `convert_time` | meta |

## Design Principles

- **eMCP-complementary**: Skills compose eMCP server tools into workflows. A skill that wraps an MCP tool into a workflow is valuable. A skill that reimplements what an MCP server already does is waste.
- **Local-only**: No SaaS dependencies or API keys. Everything runs on your machine.
- **Cross-platform**: Windows, macOS, Linux. Forward slashes in all paths.
- **Professional**: No decorative language. Minimalist and focused.

## License

MIT -- Copyright (c) 2026 Eptesicus Laboratories
