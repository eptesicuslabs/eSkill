# eSkill

Claude Code skills, subagents, and hooks by Eptesicus Laboratories.
Companion to [eMCP](https://github.com/eptesicuslabs/eMCP).

## Structure

This repository is a Claude Code plugin marketplace containing 7 plugins
organized by domain:

| Plugin | Domain | Skills |
|--------|--------|--------|
| eskill-coding | Git workflows, code review, testing, refactoring | 10 |
| eskill-office | Document processing, data analysis, diagrams | 6 |
| eskill-system | Environment setup, Docker, logs, diagnostics | 6 |
| eskill-intelligence | Codebase exploration, research, knowledge management | 6 |
| eskill-devops | CI/CD, infrastructure, deployment, releases | 5 |
| eskill-quality | Security, licenses, standards, accessibility | 6 |
| eskill-meta | Project init, changelogs, session management | 5 |

## Design Principles

- Skills orchestrate eMCP server tools into workflows. They do not reimplement
  tool-level functionality that MCP servers already provide.
- Local-only operation. No SaaS dependencies or API keys required.
- Cross-platform. All paths use forward slashes. Scripts use Node.js or Python.
- SKILL.md files stay under 500 lines. Reference material goes in separate files.
- Descriptions specify both what the skill does and when it should be triggered.
- No decorative language or emojis in code, skills, or commit messages.

## Installation

Full marketplace:
```
claude plugin install --marketplace https://github.com/eptesicuslabs/eSkill
```

Individual plugin:
```
claude plugin install https://github.com/eptesicuslabs/eSkill --plugin eskill-coding
```

## Conventions

- Skill names: kebab-case, max 64 characters
- Plugin names: prefixed with `eskill-`
- Agent names: descriptive, kebab-case
- Hook scripts: placed in plugin `scripts/` directories
- All file paths in skills use forward slashes regardless of OS
