# eSkill

eSkill is the skill and workflow layer of the [eAgent](https://github.com/eptesicuslabs/eAgent) platform. It composes [eMCP](https://github.com/eptesicuslabs/eMCP) server tools into higher-level workflows — where eMCP provides primitives (`git_log`, `ast_search`, `sql_query`), eSkill provides orchestration (changelog generation, codebase cartography, deployment checklists).

10 plugins. 83 skills. 3 hooks. Local-only, MIT-licensed.

## Architecture

```
eMCP (primitives)                       eSkill (orchestration)
────────────────────────────────        ────────────────────────────────
git_log + git_show                   -> changelog-generation
git_diff + lsp_references + ast      -> code-review-prep
ast_search + ast_rewrite + test      -> refactoring-workflow
pdf_read + docx_read + pptx_read     -> document-to-markdown
lsp_symbols + ast_search + diagram   -> diagram-from-code
docker_ps + docker_logs + log_*      -> container-dashboard
memory + docs + fetch + reasoning    -> research-workflow
crypto_hash_file + archive_create    -> backup-workflow
ast_search + lsp_diagnostics         -> security-scan
```

eMCP exposes 33 servers with approximately 130 tools. eSkill's 83 skills call sequences of those tools in deliberate order, handle edge cases, and produce structured output. A skill that composes eMCP tools into a workflow is the intended design. A skill that reimplements what an eMCP server already provides is waste.

## Installation

eSkill is consumed by the eAgent runtime. Skills are loaded from the `plugins/` directory structure. See the [eAgent documentation](https://github.com/eptesicuslabs/eAgent) for integration details.

## Plugins

| Plugin | Domain | Skills |
|--------|--------|-------:|
| [eskill-coding](plugins/eskill-coding) | Git workflows, code review, refactoring, database, performance | 14 |
| [eskill-office](plugins/eskill-office) | Document conversion, data pipelines, diagrams, reports | 9 |
| [eskill-system](plugins/eskill-system) | Environment setup, Docker, log analysis, system diagnostics, backups | 8 |
| [eskill-intelligence](plugins/eskill-intelligence) | Codebase exploration, knowledge graphs, research, decisions | 8 |
| [eskill-devops](plugins/eskill-devops) | CI/CD, infrastructure review, deployment, releases, monitoring | 9 |
| [eskill-quality](plugins/eskill-quality) | Security scanning, license compliance, code standards, accessibility | 9 |
| [eskill-frontend](plugins/eskill-frontend) | Frontend design, component scaffolding, design system, responsive layout, CSS | 7 |
| [eskill-meta](plugins/eskill-meta) | Project scaffolding, changelogs, session recaps, health dashboards | 7 |
| [eskill-api](plugins/eskill-api) | OpenAPI validation, contract testing, GraphQL, versioning, mocks | 6 |
| [eskill-testing](plugins/eskill-testing) | E2E orchestration, mutation testing, test data, flaky tests, coverage | 6 |

## Skill Reference

### Coding

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| changelog-generation | git, markdown | Generate changelogs from commit history between refs |
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
| data-pipeline | spreadsheet, sqlite, filesystem | Import spreadsheet and CSV data into SQLite for querying and export |
| diagram-from-code | lsp, ast, diagram, filesystem | Generate architecture diagrams from codebase structure |
| report-builder | spreadsheet, sqlite, log, git, diagram, markdown | Compile structured reports from multiple data sources |
| presentation-extract | pptx, filesystem | Extract content and speaker notes from presentations |
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
| ci-config-generator | data-file, filesystem, shell | Generate CI/CD pipeline configurations from project structure |
| infrastructure-review | filesystem, data-file, diff | Review infrastructure-as-code for best practices and security |
| deployment-checklist | test-runner, shell, git, data-file, notify | Pre-deployment verification workflow |
| release-workflow | git, data-file, diff, markdown | Version bumping, tagging, changelog, and release notes |
| monitoring-config | ast, filesystem, data-file, log | Generate monitoring and alerting configurations |

### Quality

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| security-scan | ast, filesystem, lsp | Scan code for OWASP Top 10 vulnerabilities using AST patterns |
| license-check | data-file, filesystem, shell | Verify license compatibility across dependencies |
| code-standards | ast, lsp, shell, filesystem | Enforce coding standards with AST and LSP analysis |
| configuration-audit | data-file, filesystem, diff | Compare configurations across environments to detect drift |
| file-integrity | crypto, filesystem | Create and verify checksum manifests for change detection |
| accessibility-scan | ast, filesystem | Scan frontend code for WCAG accessibility violations |

### Frontend

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| frontend-design | filesystem, ast, lsp, image, browser, fetch | Create production-grade frontend interfaces with high visual craft |
| component-scaffold | filesystem, ast | Generate UI component scaffolds following project patterns |
| design-system-audit | ast, filesystem | Audit UI code for design system consistency and token compliance |
| responsive-layout-check | ast, filesystem | Analyze CSS and components for responsive design issues |
| css-optimization | ast, filesystem | Identify CSS optimization opportunities and specificity conflicts |
| bundle-analysis | data-file, filesystem, shell | Analyze bundle composition and dependency weight |
| storybook-scaffold | ast, filesystem | Generate Storybook story files from component analysis |

### API

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| openapi-validate | data-file, filesystem | Validate OpenAPI specifications against standards |
| contract-testing | data-file, test-runner, filesystem | Generate and verify API contract tests |
| graphql-audit | ast, filesystem, data-file | Audit GraphQL schemas and resolvers for best practices |
| api-versioning | ast, filesystem, diff, git | Manage API version strategy and breaking change detection |
| load-test-scaffold | filesystem, shell | Generate load testing configurations from API specifications |
| mock-server-generate | data-file, filesystem | Generate mock API servers from OpenAPI or GraphQL schemas |

### Testing

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| e2e-orchestration | test-runner, filesystem, shell, browser | Orchestrate end-to-end test suites with environment management |
| mutation-testing | test-runner, ast, filesystem | Configure and analyze mutation testing for test quality |
| test-data-factory | filesystem, ast, data-file | Generate test data factories from schema definitions |
| flaky-test-detective | test-runner, git, log, filesystem | Identify and diagnose flaky tests from history and logs |
| coverage-gap-analysis | test-runner, ast, lsp, filesystem | Identify untested code paths and generate targeted test suggestions |
| visual-regression-setup | filesystem, shell, browser | Configure visual regression testing for UI components |

### Meta

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| project-scaffold | filesystem, data-file, shell, git | Initialize projects with directory structure and toolchain |
| changelog-maintain | git, markdown, filesystem | Maintain CHANGELOG.md in Keep a Changelog format |
| session-recap | git, test-runner, memory, task | Summarize work completed in the current session |
| project-health | test-runner, lsp, data-file, markdown, git, diagram | Generate project health dashboards with quality scores |
| issue-decompose | reasoning, ast, lsp, task, filesystem | Break complex issues into actionable subtasks |

## eMCP Server Coverage

Every eMCP server is used by at least one skill.

| eMCP Server | Tools | Plugins |
|-------------|-------|---------|
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
| `@emcp/server-fetch` | `fetch_url`, `extract_text` | intelligence, frontend |
| `@emcp/server-task` | `task_create`, `task_list`, `task_tree` | meta |
| `@emcp/server-ocr` | `ocr_image` | office |
| `@emcp/server-browser` | `browser_search`, `browser_navigate` | intelligence, frontend |
| `@emcp/server-image` | `image_info`, `image_resize` | office, frontend |
| `@emcp/server-media` | `media_info`, `media_convert` | office |
| `@emcp/server-clipboard` | `clipboard_read`, `clipboard_write` | system |
| `@emcp/server-computer-use` | `screen_screenshot`, `screen_click` | system |
| `@emcp/server-time` | `current_time`, `convert_time` | meta |

## Design Principles

- **eMCP-complementary.** Skills compose eMCP server tools into workflows. They do not reimplement what eMCP already provides.
- **Local-only.** No SaaS dependencies or API keys. Everything runs on the local machine.
- **Cross-platform.** Windows, macOS, Linux. Forward slashes in all paths.
- **Minimal.** No decorative language, no unnecessary abstraction.

## License

MIT. Copyright (c) 2026 Eptesicus Laboratories.
