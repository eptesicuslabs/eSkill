# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Identity

eSkill is the skill and workflow layer of the [eAgent](https://github.com/eptesicuslabs/eAgent) platform by Eptesicus Laboratories. It composes [eMCP](https://github.com/eptesicuslabs/eMCP) server tools (174 tools across 31+2 composite MCP servers) into higher-level workflows. eSkill is platform-agnostic — any runtime that understands the SKILL.md format can consume it.

**Do not** frame eSkill as a Claude Code product, Claude Code plugin marketplace, or exclusive to any single platform. The primary consumer is eAgent. Claude Code is one of several compatible runtimes.

## Validation Commands

```bash
# basic validation (frontmatter exists, files readable)
python scripts/validate_skills.py

# strict — requires name + description in frontmatter
python scripts/validate_skills.py --strict

# lint — no emojis, valid UTF-8, no trailing whitespace
python scripts/validate_skills.py --lint

# regression check — skill count must not decrease (reads .eara-state.json)
python scripts/validate_skills.py --no-regression

# duplicate names — unique skill names across all plugins
python scripts/validate_skills.py --no-duplicates

# workflow check — every skill must have numbered steps or decision logic
python scripts/validate_skills.py --require-workflow

# line limit — no skill file exceeds 500 lines
python scripts/validate_skills.py --max-lines 500

# composite metric (coverage 40% + quality 60%), prints score to stdout
python scripts/measure_score.py
```

All gates defined in `eara.yaml` must pass before merging.

## Architecture

```
plugins/
  eskill-{domain}/          # 11 plugins
    skills/
      {skill-name}/
        SKILL.md            # one file per skill, self-contained
    hooks/                  # optional, only 3 plugins have hooks
      hooks.json
scripts/
  validate_skills.py        # eARA gate validator
  measure_score.py          # composite metric calculator
```

Skills orchestrate eMCP server tools into multi-step workflows. A skill that composes tools into a workflow is correct design. A skill that reimplements what an eMCP server already provides is waste.

## SKILL.md Format

```yaml
---
name: kebab-case-identifier
description: "What it does. Use when [primary trigger]. Also applies when: '[alt phrase 1]', '[alt phrase 2]'."
---
```

After frontmatter, the markdown body must include:
- Numbered workflow steps (`### Step N: Title`)
- Tool references in backticks (`ast_search`, `lsp_symbols`, `fs_read`, `shell_exec`)
- The `e-mcp` skill in eskill-emcp has full parameter schemas for all 174 tools
- Code examples with language-specified fenced blocks
- `## Related Skills` section with cross-references to other skills

Typical length: 200–400 lines. Maximum: 500 lines (enforced by validation gate).

## Hooks Format

Hooks live in `plugins/eskill-{domain}/hooks/hooks.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "^(Write|Edit)$",
        "hooks": [{ "type": "prompt", "prompt": "...", "model": "haiku" }]
      }
    ]
  }
}
```

Hook types: `PreToolUse`, `PostToolUse`. Only three plugins have hooks: eskill-quality (security checks on Write/Edit), eskill-meta (context budget on Read), eskill-system (destructive command guard on Bash).

## Commit Style

- Lowercase messages, no emojis, no `Co-Authored-By` lines
- No Claude-specific artifacts (CLAUDE.md, `.claude-plugin/`, `marketplace.json`) in public commits
- Descriptive but concise

## Constraints

- **Local-only.** No SaaS dependencies or API keys required.
- **Cross-platform.** Forward slashes in all paths. Windows, macOS, Linux.
- **No emojis** in skill files, code, or commits.
- **MIT license.** Copyright (c) 2026 Eptesicus Laboratories.
