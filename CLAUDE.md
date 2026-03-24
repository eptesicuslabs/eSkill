# eSkill

Skills and workflows for the eAgent platform by Eptesicus Laboratories.
Companion to [eMCP](https://github.com/eptesicuslabs/eMCP).

## Structure

This repository is the skill and workflow layer of eAgent, containing 10
plugins organized by domain:

| Plugin | Domain | Skills |
|--------|--------|--------|
| eskill-coding | Git workflows, code review, testing, refactoring | 14 |
| eskill-office | Document processing, data analysis, diagrams | 9 |
| eskill-system | Environment setup, Docker, logs, diagnostics | 8 |
| eskill-intelligence | Codebase exploration, research, knowledge management | 8 |
| eskill-devops | CI/CD, infrastructure, deployment, releases | 9 |
| eskill-quality | Security, licenses, standards, accessibility | 9 |
| eskill-meta | Project init, changelogs, session management | 7 |
| eskill-frontend | Components, design system, responsive, CSS, bundles | 6 |
| eskill-api | OpenAPI, contracts, GraphQL, versioning, load testing | 6 |
| eskill-testing | E2E, mutation, test data, flaky tests, coverage | 6 |

## Design Principles

- Skills orchestrate eMCP server tools into workflows. They do not reimplement
  tool-level functionality that MCP servers already provide.
- Local-only operation. No SaaS dependencies or API keys required.
- Cross-platform. All paths use forward slashes. Scripts use Node.js or Python.
- SKILL.md files stay under 500 lines. Reference material goes in separate files.
- Descriptions specify both what the skill does and when it should be triggered.
- No decorative language or emojis in code, skills, or commit messages.
- Agent definitions belong in eAgent, not here. eSkill is the workflow layer only.

## Conventions

- Skill names: kebab-case, max 64 characters
- Plugin names: prefixed with `eskill-`
- Hook scripts: placed in plugin `scripts/` directories
- All file paths in skills use forward slashes regardless of OS
