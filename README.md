# eSkill

eSkill is the skill and workflow layer of the [eAgent](https://github.com/eptesicuslabs/eAgent) platform. It composes [eMCP](https://github.com/eptesicuslabs/eMCP) server tools into higher-level workflows — where eMCP provides primitives (`git_log`, `ast_search`, `sql_query`), eSkill provides orchestration (changelog generation, codebase cartography, deployment checklists).

11 plugins. 89 skills. 3 hooks. Local-only, MIT-licensed.

## Architecture

```
eMCP (primitives)                       eSkill (orchestration)
────────────────────────────────        ────────────────────────────────
git_log + git_show                   -> e-changelog
git_diff + lsp_references + ast      -> e-review
ast_search + ast_rewrite + test      -> e-refactor
pdf_read_text + docx_read_html       -> e-doc
lsp_symbols + ast_search + diagram   -> e-diagram
docker_ps + docker_logs + log_*      -> e-containers
docs_search + think_* + fetch_url    -> e-research
crypto_hash_file + archive_create    -> e-backup
ast_search + lsp_diagnostics         -> e-scan
```

eMCP exposes 31 servers (plus 2 composites) with 174 tools. eSkill's 89 skills call sequences of those tools in deliberate order, handle edge cases, and produce structured output. A skill that composes eMCP tools into a workflow is the intended design. A skill that reimplements what an eMCP server already provides is waste.

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
| [eskill-quality](plugins/eskill-quality) | Security scanning, license compliance, code standards, accessibility | 12 |
| [eskill-frontend](plugins/eskill-frontend) | Frontend design, component scaffolding, design system, responsive layout, CSS | 8 |
| [eskill-meta](plugins/eskill-meta) | Project scaffolding, changelogs, session recaps, health dashboards | 7 |
| [eskill-api](plugins/eskill-api) | OpenAPI validation, contract testing, GraphQL, versioning, mocks | 6 |
| [eskill-testing](plugins/eskill-testing) | E2E orchestration, mutation testing, test data, flaky tests, coverage | 7 |
| [eskill-emcp](plugins/eskill-emcp) | eMCP server and tool reference, knowledge correction, API schemas | 1 |

## Skill Reference

### Coding

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| e-changelog | git, markdown | Generate changelogs from commit history between refs |
| e-review | git, lsp, ast, diff | Prepare code review summaries from diffs with semantic context |
| e-testgen | lsp, ast, filesystem, data-file | Generate test file scaffolds from code structure analysis |
| e-refactor | ast, lsp, test-runner, diff, filesystem | Safe refactoring with AST rewriting and test verification loops |
| e-deps | data-file, shell, ast, filesystem | Audit dependencies for vulnerabilities, outdated versions, unused packages |
| e-surface | lsp, ast, filesystem | Extract and document public API surface |
| e-migrate | sqlite, filesystem, diff | Plan and validate database schema changes with migrations |
| e-perf | shell, log, lsp, ast | Profile, benchmark, and identify performance bottlenecks |
| e-prune | git | Identify and manage stale git branches |
| e-merge | git, lsp, filesystem, test-runner | Systematic merge conflict resolution with semantic context |
| e-deadcode | lsp, ast, filesystem, git | Identify unreachable code, unused exports, and orphan files |
| e-integ | ast, lsp, filesystem, data-file, test-runner | Generate integration test scaffolds for API endpoints and database operations |
| e-nplus | ast, lsp, filesystem | Detect N+1 query patterns in ORM code and suggest batch alternatives |
| e-threshold | shell, filesystem, data-file, ast | Check test coverage against configurable thresholds and identify gaps |

### Office

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| e-doc | pdf, docx, pptx, image, filesystem | Convert PDF, DOCX, PPTX to clean markdown |
| e-pipe | spreadsheet, sqlite, filesystem | Import spreadsheet and CSV data into SQLite for querying and export |
| e-diagram | lsp, ast, diagram, filesystem | Generate architecture diagrams from codebase structure |
| e-report | spreadsheet, sqlite, log, git, diagram, markdown | Compile structured reports from multiple data sources |
| e-slides | pptx, filesystem | Extract content and speaker notes from presentations |
| e-sheet | spreadsheet, filesystem | Validate spreadsheet data against configurable rules |
| e-adr | filesystem, git, markdown | Create Architecture Decision Records in standard ADR format |
| e-apidoc | ast, lsp, filesystem, data-file, shell | Generate API documentation in OpenAPI format from code analysis |
| e-runbook | filesystem, data-file, docker, log, markdown, shell | Generate operational runbooks from infrastructure configs and monitoring rules |

### System

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| e-env | system, shell, filesystem, data-file | Validate development environment against project requirements |
| e-containers | docker, log, system | Docker container health overview with logs and metrics |
| e-logs | log, docker, filesystem | Investigate issues through log parsing and timeline construction |
| e-snapshot | system, docker, shell, filesystem, crypto | Capture comprehensive system state for diagnostics |
| e-backup | archive, crypto, filesystem | Create verified backups with checksums and rotation |
| e-procs | system, shell | Analyze running processes for resource consumption issues |
| e-disk | system, filesystem, shell, docker | Analyze disk usage from dev artifacts and suggest safe cleanup |
| e-ports | system, shell, docker, filesystem, data-file | Detect and resolve port conflicts between dev services and containers |

### Intelligence

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| e-carto | filesystem, ast, lsp, docs, data-file | Map codebase architecture into navigable knowledge graphs |
| e-graph | filesystem, reasoning, markdown, docs | Build knowledge graphs from project documentation and code |
| e-research | docs, fetch, reasoning, task | Structured research with source gathering and synthesis |
| e-decide | reasoning, docs | Guided decision-making with options analysis and ADR output |
| e-context | docs, reasoning, git, filesystem | Export project context for session handoffs |
| e-learn | filesystem, lsp, ast, docs, git | Systematic exploration of unfamiliar codebases |
| e-debt | ast, lsp, filesystem, git, data-file | Catalog technical debt by analyzing TODOs, complexity hotspots, and deprecated usage |
| e-transfer | ast, lsp, filesystem, data-file, git, markdown | Generate knowledge transfer documentation by tracing code paths and business rules |

### DevOps

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| e-ci | data-file, filesystem, shell | Generate CI/CD pipeline configurations from project structure |
| e-infra | filesystem, data-file, diff | Review infrastructure-as-code for best practices and security |
| e-deploy | test-runner, shell, git, data-file, system | Pre-deployment verification workflow |
| e-release | git, data-file, diff, markdown | Version bumping, tagging, changelog, and release notes |
| e-monitor | ast, filesystem, data-file, log | Generate monitoring and alerting configurations |
| e-cost | filesystem, data-file, shell | Estimate cloud infrastructure costs from IaC configurations |
| e-kube | filesystem, data-file, shell | Generate Kubernetes manifests from application analysis |
| e-recover | filesystem, data-file, docker, markdown, shell | Generate disaster recovery documentation and recovery procedures |
| e-terra | filesystem, data-file, shell, diff | Review Terraform configurations for structure, state, and security |

### Quality

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| e-scan | ast, filesystem, lsp | Scan code for OWASP Top 10 vulnerabilities using AST patterns |
| e-license | data-file, filesystem, shell | Verify license compatibility across dependencies |
| e-lint | ast, lsp, shell, filesystem | Enforce coding standards with AST and LSP analysis |
| e-config | data-file, filesystem, diff | Compare configurations across environments to detect drift |
| e-checksum | crypto, filesystem | Create and verify checksum manifests for change detection |
| e-a11y | ast, filesystem | Scan frontend code for WCAG accessibility violations |
| e-diffrev | git, ast, filesystem, shell | Security-focused differential review of code changes with blast radius analysis |
| e-defaults | ast, filesystem, data-file | Detect fail-open insecure defaults and hardcoded secrets |
| e-variant | ast, filesystem | Find similar vulnerabilities across a codebase from a known pattern |
| e-comply | ast, lsp, filesystem, data-file, shell | Evaluate project against SOC2, GDPR, HIPAA, or PCI-DSS compliance checklists |
| e-sbom | filesystem, data-file, shell, crypto | Generate Software Bill of Materials in SPDX or CycloneDX format |
| e-secrets | filesystem, git, shell, crypto | Detect committed secrets in git history and generate rotation plans |

### Frontend

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| e-design | filesystem, ast, lsp, image, browser, fetch | Create production-grade frontend interfaces with high visual craft |
| e-component | filesystem, ast | Generate UI component scaffolds following project patterns |
| e-tokens | ast, filesystem | Audit UI code for design system consistency and token compliance |
| e-responsive | ast, filesystem | Analyze CSS and components for responsive design issues |
| e-css | ast, filesystem | Identify CSS optimization opportunities and specificity conflicts |
| e-bundle | data-file, filesystem, shell | Analyze bundle composition and dependency weight |
| e-stories | ast, filesystem | Generate Storybook story files from component analysis |
| e-render | browser, computer-use, shell, image, filesystem | Render and validate frontend output in a live browser |

### API

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| e-openapi | data-file, filesystem | Validate OpenAPI specifications against standards |
| e-contract | data-file, test-runner, filesystem | Generate and verify API contract tests |
| e-graphql | ast, filesystem, data-file | Audit GraphQL schemas and resolvers for best practices |
| e-version | ast, filesystem, diff, git | Manage API version strategy and breaking change detection |
| e-loadtest | filesystem, shell | Generate load testing configurations from API specifications |
| e-mock | data-file, filesystem | Generate mock API servers from OpenAPI or GraphQL schemas |

### Testing

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| e-e2e | test-runner, filesystem, shell, browser | Orchestrate end-to-end test suites with environment management |
| e-mutate | test-runner, ast, filesystem | Configure and analyze mutation testing for test quality |
| e-factory | filesystem, ast, data-file | Generate test data factories from schema definitions |
| e-flaky | test-runner, git, log, filesystem | Identify and diagnose flaky tests from history and logs |
| e-coverage | test-runner, ast, lsp, filesystem | Identify untested code paths and generate targeted test suggestions |
| e-visual | filesystem, shell, browser | Configure visual regression testing for UI components |
| e-proptest | ast, filesystem, test-runner | Generate property-based tests for serialization, parsing, and validation |

### Meta

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| e-init | filesystem, data-file, shell, git | Initialize projects with directory structure and toolchain |
| e-keeplog | git, markdown, filesystem | Maintain CHANGELOG.md in Keep a Changelog format |
| e-recap | git, test-runner, reasoning, task | Summarize work completed in the current session |
| e-health | test-runner, lsp, data-file, markdown, git, diagram | Generate project health dashboards with quality scores |
| e-decompose | reasoning, ast, lsp, task, filesystem | Break complex issues into actionable subtasks |
| e-retro | git, test-runner, filesystem, data-file, markdown | Generate sprint or milestone retrospectives from git history and metrics |
| e-ship | filesystem, data-file, git, ast, lsp, shell, test-runner | Evaluate shipping readiness by checking docs, tests, security, and ops |

### eMCP

| Skill | eMCP Servers | Description |
|-------|-------------|-------------|
| e-mcp | all | Current eMCP server and tool reference with parameter schemas |

## eMCP Server Coverage

Every eMCP server is used by at least one skill. See the [e-mcp](plugins/eskill-emcp/skills/e-mcp) skill for full parameter schemas.

| eMCP Server | Tools | Plugins |
|-------------|-------|---------|
| `@emcp/server-filesystem` | `fs_read`, `fs_list`, `fs_search`, `fs_info`, `fs_write`, `fs_edit`, `fs_mkdir`, `fs_move`, `fs_watch` | all |
| `@emcp/server-git` | `git_status`, `git_log`, `git_diff`, `git_show`, `git_branches`, `git_tags` | coding, devops, meta, intelligence |
| `@emcp/server-ast` | `ast_search`, `ast_rewrite` | coding, office, quality, intelligence |
| `@emcp/server-lsp` | `lsp_symbols`, `lsp_definition`, `lsp_references`, `lsp_hover`, `lsp_diagnostics` | coding, office, quality, intelligence, meta |
| `@emcp/server-shell` | `shell_exec`, `shell_bg`, `shell_status`, `shell_kill` | coding, system, devops, quality, meta, testing, frontend |
| `@emcp/server-test-runner` | `test_run`, `test_run_file`, `test_list_files` | coding, devops, meta, testing |
| `@emcp/server-reasoning` | `think_start`, `think_step`, `think_branch`, `think_conclude`, `think_status`, `think_replay`, `think_search`, `think_summarize` | intelligence, meta |
| `@emcp/server-docker` | `docker_ps`, `docker_images`, `docker_logs`, `docker_inspect`, `docker_exec` | system, devops |
| `@emcp/server-log` | `log_parse`, `log_errors`, `log_stats`, `log_search` | system, devops |
| `@emcp/server-sqlite` | `sql_list_tables`, `sql_describe_table`, `sql_query`, `sql_execute` | office, coding |
| `@emcp/server-pdf` | `pdf_read_text`, `pdf_read_metadata`, `pdf_count_pages`, `pdf_search`, `pdf_extract_tables` | office |
| `@emcp/server-docx` | `docx_read_text`, `docx_read_html`, `docx_read_metadata`, `docx_read_tables`, `docx_read_sections` | office |
| `@emcp/server-pptx` | `pptx_read_text`, `pptx_read_slides`, `pptx_read_metadata`, `pptx_read_slide`, `pptx_extract_tables` | office |
| `@emcp/server-spreadsheet` | `spreadsheet_read`, `spreadsheet_list_sheets`, `spreadsheet_query`, `spreadsheet_read_csv`, `spreadsheet_read_range` | office |
| `@emcp/server-markdown` | `markdown_to_html`, `markdown_headings`, `markdown_links`, `markdown_code_blocks`, `markdown_front_matter`, `markdown_read_section` | office, meta, intelligence, coding |
| `@emcp/server-diagram` | `diagram_render`, `diagram_render_file`, `diagram_formats` | office, meta |
| `@emcp/server-diff` | `diff_files`, `diff_text`, `diff_dirs`, `diff_apply` | coding, quality, devops, api |
| `@emcp/server-data-file` | `data_file_read`, `data_file_query`, `data_file_set`, `data_file_convert` | coding, devops, quality, meta, system |
| `@emcp/server-crypto` | `crypto_hash`, `crypto_hash_file`, `crypto_encode`, `crypto_random`, `crypto_hmac` | system, quality, testing |
| `@emcp/server-archive` | `archive_list`, `archive_read_file`, `archive_extract`, `archive_create` | system |
| `@emcp/server-system` | `sys_info`, `sys_procs`, `sys_disk`, `sys_env`, `sys_kill`, `sys_notify` | system |
| `@emcp/server-docs` | `docs_index`, `docs_clone`, `docs_search`, `docs_list_libraries`, `docs_remove`, `docs_bootstrap` | intelligence, emcp |
| `@emcp/server-fetch` | `fetch_url`, `fetch_many`, `extract_links`, `extract_text` | intelligence, frontend |
| `@emcp/server-task` | `task_create`, `task_list`, `task_update`, `task_delete`, `task_tree` | meta |
| `@emcp/server-browser` | `browser_search`, `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, + 13 more | intelligence, frontend |
| `@emcp/server-image` | `image_info`, `image_metadata`, `image_resize`, `image_convert`, `image_ocr`, `image_ocr_languages` | office, frontend, testing |
| `@emcp/server-media` | `media_info`, `media_convert`, `media_trim`, `media_extract_audio`, `media_extract_frame` | office |
| `@emcp/server-clipboard` | `clip_read`, `clip_write` | system |
| `@emcp/server-computer-use` | `screen_screenshot`, `screen_left_click`, `screen_type`, `screen_key`, + 17 more | system |
| `@emcp/server-egrep` | `egrep_search`, `egrep_search_files`, `egrep_status`, `egrep_reindex` | coding, quality, intelligence, devops, frontend, testing, meta |
| `@emcp/server-time` | `current_time`, `convert_time` | meta |
| `@emcp/server-desktop` | Composite: filesystem + shell + diff + system + clipboard | system |
| `@emcp/server-document` | Composite: pdf + docx + pptx + markdown + spreadsheet | office |

## Design Principles

- **eMCP-complementary.** Skills compose eMCP server tools into workflows. They do not reimplement what eMCP already provides.
- **Local-only.** No SaaS dependencies or API keys. Everything runs on the local machine.
- **Cross-platform.** Windows, macOS, Linux. Forward slashes in all paths.
- **Minimal.** No decorative language, no unnecessary abstraction.

## License

MIT. Copyright (c) 2026 Eptesicus Laboratories.
