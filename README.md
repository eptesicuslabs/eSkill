# eSkill

Claude Code skills, subagents, and hooks by [Eptesicus Laboratories](https://github.com/eptesicuslabs).

Companion to [eMCP](https://github.com/eptesicuslabs/eMCP). Skills orchestrate eMCP's 33 local MCP servers into higher-level workflows.

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

**Total: 44 skills, 6 agents, 1 hook**

## Installation

Install the full marketplace:

```
claude plugin install --marketplace https://github.com/eptesicuslabs/eSkill
```

Install a single plugin:

```
claude plugin install https://github.com/eptesicuslabs/eSkill --plugin eskill-coding
```

## Design Principles

- **eMCP-complementary**: Skills compose eMCP server tools into workflows. They do not reimplement tool-level functionality.
- **Local-only**: No SaaS dependencies or API keys required. Everything runs on your machine.
- **Cross-platform**: Works on Windows, macOS, and Linux. All paths use forward slashes.
- **Professional**: No decorative language or emojis. Minimalist and focused.

## Skill Domains

### Coding (eskill-coding)

| Skill | Description |
|-------|-------------|
| changelog-generation | Generate changelogs from git commit history between refs |
| code-review-prep | Prepare code review summaries from diffs with LSP/AST context |
| test-scaffolding | Generate test file scaffolds from code structure analysis |
| refactoring-workflow | Safe refactoring with AST rewriting and test verification loops |
| dependency-audit | Audit dependencies for vulnerabilities, outdated versions, unused packages |
| api-surface-map | Extract and document public API surface using LSP and AST |
| database-workflow | Plan and validate database schema changes with migrations |
| performance-analysis | Profile, benchmark, and identify performance bottlenecks |
| branch-cleanup | Identify and manage stale git branches |
| merge-conflict-resolution | Systematic merge conflict resolution with semantic context |

### Office (eskill-office)

| Skill | Description |
|-------|-------------|
| document-to-markdown | Convert PDF, DOCX, PPTX to clean markdown |
| data-pipeline | Import spreadsheet/CSV data into SQLite for querying and export |
| diagram-from-code | Generate architecture diagrams from codebase structure |
| report-builder | Compile structured reports from multiple data sources |
| presentation-extract | Extract content and speaker notes from PowerPoint files |
| spreadsheet-validation | Validate spreadsheet data against configurable rules |

### System (eskill-system)

| Skill | Description |
|-------|-------------|
| environment-validate | Validate development environment against project requirements |
| container-dashboard | Docker container health overview with logs and metrics |
| log-investigation | Investigate issues through log parsing and timeline construction |
| system-snapshot | Capture comprehensive system state for diagnostics |
| backup-workflow | Create verified backups with checksums and rotation |
| process-analysis | Analyze running processes for resource consumption issues |

### Intelligence (eskill-intelligence)

| Skill | Description |
|-------|-------------|
| codebase-cartography | Map codebase architecture into navigable knowledge graphs |
| knowledge-graph-build | Build knowledge graphs from project documentation and code |
| research-workflow | Structured research with source gathering and synthesis |
| decision-framework | Guided decision-making with options analysis and ADR output |
| context-export | Export project context for session handoffs |
| learning-navigator | Systematic exploration of unfamiliar codebases |

### DevOps (eskill-devops)

| Skill | Description |
|-------|-------------|
| ci-config-generator | Generate CI/CD pipeline configs from project structure |
| infrastructure-review | Review IaC files for best practices and security |
| deployment-checklist | Pre-deployment verification workflow |
| release-workflow | Version bumping, tagging, changelog, and release notes |
| monitoring-config | Generate monitoring and alerting configurations |

### Quality (eskill-quality)

| Skill | Description |
|-------|-------------|
| security-scan | Scan code for OWASP Top 10 vulnerabilities using AST patterns |
| license-check | Verify license compatibility across dependencies |
| code-standards | Enforce coding standards with AST and LSP analysis |
| configuration-audit | Compare configs across environments to detect drift |
| file-integrity | Create and verify checksum manifests for change detection |
| accessibility-scan | Scan frontend code for WCAG accessibility violations |

### Meta (eskill-meta)

| Skill | Description |
|-------|-------------|
| project-scaffold | Initialize projects with directory structure and toolchain |
| changelog-maintain | Maintain CHANGELOG.md in Keep a Changelog format |
| session-recap | Summarize work completed in the current session |
| project-health | Generate project health dashboards with quality scores |
| issue-decompose | Break complex issues into actionable subtasks |

## eMCP Integration

Skills reference tools from these eMCP servers:

| Server | Used By |
|--------|---------|
| git | coding, devops, meta |
| lsp | coding, office, intelligence |
| ast | coding, office, quality |
| test-runner | coding, devops, meta |
| filesystem | all plugins |
| shell | coding, system, devops, quality |
| docker | system, devops |
| log | system, devops |
| sqlite | office, coding |
| pdf, docx, pptx | office |
| spreadsheet | office |
| markdown | office, meta, intelligence |
| diagram | office, meta |
| memory | intelligence, meta |
| reasoning | intelligence, meta |
| docs | intelligence |
| fetch | intelligence |
| system | system |
| crypto | system, quality |
| archive | system |
| notify | system, devops |
| diff | coding, quality, devops |
| data-file | coding, devops, quality, meta |
| task | meta |
| ocr | office |

## License

MIT License. Copyright (c) 2026 Eptesicus Laboratories.
