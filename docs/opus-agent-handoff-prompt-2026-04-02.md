# Opus Agent Handoff Prompt - 2026-04-02

Use the following prompt with your Opus 4.6 agent.

---

You are taking over work in the `eSkill` repository at `c:/Users/deyan/Projects/eSkill`.

## Project Context

This repository is **eSkill**, the skill and workflow layer of the eAgent platform by Eptesicus Laboratories. It is not Claude-specific and should not be framed as a Claude Code product or marketplace. eSkill composes **eMCP** server tools into higher-level workflows. A skill is valuable when it orchestrates tools into a reusable workflow; reimplementing a primitive that eMCP already provides is waste.

Repository facts:

- 11 plugins
- 90 skills
- 3 hooks
- local-only
- MIT-licensed
- cross-platform
- no emojis in skill files, code, or commits

Important repo guidance is in:

- `CLAUDE.md`
- `README.md`
- `docs/skill-gap-analysis-2026-04-02.md`

Recent repository state:

- `README.md` was updated to correct skill-to-eMCP server mapping drift and to reflect the new `e-debug` skill and the completed frontend-cluster upgrades.
- `docs/skill-gap-analysis-2026-04-02.md` was updated to mark `e-debug` and the frontend-cluster work as done.
- `plugins/eskill-coding/skills/e-debug/SKILL.md` was added.
- `plugins/eskill-testing/skills/e-coverage/SKILL.md` now owns coverage analysis, and `plugins/eskill-coding/skills/e-threshold/SKILL.md` now owns coverage policy and CI enforcement.
- Validation currently passes with:

```bash
python scripts/validate_skills.py --strict
```

## What Was Already Found

The current high-confidence findings are:

### Most promising new skills

1. `e-codemod`
2. `e-incident`

### Most promising upgrades to existing skills

1. Clarify `e-contract` around Pact-style CDC vs. mock-driven workflows.
2. Tighten `e-report` and `e-runbook` so they no longer blur together.
3. Reduce overclaiming and strengthen durable outputs in `e-comply`, `e-scan`, `e-secrets`, and `e-variant`.
4. Sharpen boundary and audience guidance in `e-graph`, `e-transfer`, `e-health`, and `e-ship`.
5. Improve `e-css` with architecture-specific audit guidance.

### Lower-priority / likely platform-scope ideas

- persistent memory across sessions
- multi-agent orchestration

These surfaced in broader research but currently look more like eAgent/runtime concerns than immediate eSkill workflow-skill priorities.

## Your Job

Do **not** treat the existing analysis as final. Use it as starting context only.

You should:

1. Do your **own research** from scratch using authoritative and independent sources.
2. Re-evaluate the current conclusions instead of simply accepting them.
3. Improve the writing quality, clarity, and usefulness of the repo’s documentation and any skill content you touch.
4. Make concrete repository improvements, not just a memo.

You have access to the same subagents available in this environment, including:

- `researcher`
- `documentator`
- `prosecutor`
- `Explore`

Use them deliberately.

## Research Requirements

For any substantive claim you rely on, prefer at least **two independent sources**.

Bias toward:

- official documentation
- standards documents
- mature open-source project docs
- first-party framework/library docs
- widely used tool documentation

Avoid building conclusions on vague popularity claims, marketplace anecdotes, or single-source trend summaries.

If you disagree with the existing findings in `docs/skill-gap-analysis-2026-04-02.md`, say so and update the docs accordingly.

## Scope Of Work

I want you to take the repo from “good preliminary analysis” to “strong, well-written, documented next step”.

That means you should do all of the following unless you find a strong reason not to:

### 1. Re-audit the current recommendations

- Read `README.md`, `CLAUDE.md`, and `docs/skill-gap-analysis-2026-04-02.md`.
- Inspect the current skills that overlap with the proposed additions or improvements.
- Verify whether the proposed priorities still hold after your own review.

### 2. Choose the highest-leverage next deliverable

Pick one of these directions based on your own judgment:

- create a new high-value skill from the short list
- significantly improve one of the current frontend-related skills or a closely related cluster
- produce a better-structured roadmap document if implementation should be staged first

Do not choose based only on ease. Choose based on repository value.

### 3. Do real repo work

Depending on what you choose, produce one or more of the following:

- a new `SKILL.md`
- substantial updates to existing `SKILL.md` files
- updates to `README.md`
- updates to docs under `docs/`

The changes should be publishable-quality, not rough notes.

### 4. Update documentation properly

If you add or materially change a skill, update the relevant docs so the repo stays coherent.

At minimum, consider whether you must update:

- `README.md`
- `docs/skill-gap-analysis-2026-04-02.md`
- any adjacent docs you create to explain rationale, roadmap, or implementation priorities

### 5. Validate everything

Run the relevant repo validation commands after your edits. At minimum:

```bash
python scripts/validate_skills.py --strict
```

If you changed a lot of skill content, also consider:

```bash
python scripts/validate_skills.py --lint
python scripts/validate_skills.py --require-workflow
python scripts/validate_skills.py --max-lines 500
```

## Quality Bar

The work should meet these standards:

- strong writing
- precise workflow design
- defensible scope
- good taste in documentation structure
- no filler
- no vague “AI slop” wording
- no overclaiming
- explicit tool/workflow rationale

For any new or updated skill:

- keep frontmatter correct
- ensure the description has good trigger phrases
- ensure numbered workflow steps are concrete
- ensure the skill clearly composes eMCP tools rather than duplicating them
- include `## Related Skills`
- keep the file within the repo’s line limits

## Strong Candidate Directions

You do not have to follow this order, but this is the current recommendation stack:

### Option A: Build `e-debug`

Why this is promising:

- `e-debug` is already built and landed in the repository.
- This option is no longer an open deliverable.

If you choose this, I want:

- no further work here unless you discover concrete defects in the landed skill
- if defects exist, treat them as bug fixes rather than as a new-skill effort

### Option B: Build `e-codemod`

Why this is promising:

- It fills a migration-scale transformation gap not fully covered by `e-refactor`.
- It fits well with AST-aware, test-verified workflow orchestration.

If you choose this, I want:

- a robust new `SKILL.md`
- explicit dry-run, verification, rollback, and change-batch workflow thinking
- clear differentiation from `e-refactor` and `e-migrate`
- repo docs updated accordingly

### Option C: Upgrade the frontend skill cluster

Why this is promising:

- The main frontend-cluster upgrade has already landed across `e-design`, `e-tokens`, `e-stories`, `e-visual`, `e-responsive`, `e-bundle`, and `e-a11y`.
- The remaining frontend work is narrower and mostly concentrated in `e-css` or any follow-up defects you find in the landed changes.

If you choose this, I want you to look especially at:

- `e-css`
- any residual boundary issues between `e-design`, `e-tokens`, `e-visual`, and `e-render`

The likely themes are:

- CSS-architecture-specific guidance
- cleanup of any remaining boundary drift after the frontend upgrade
- verifying that README and docs stay aligned with the landed frontend work

### Option D: Build `e-incident`

Why this is promising:

- It fills a real gap between log parsing and incident-grade workflow orchestration.
- It could be valuable if scoped cleanly around technical incident handling, triage, timeline building, and postmortem preparation.

If you choose this, be careful about overlap with:

- `e-logs`
- `e-runbook`
- `e-recap`

### Option E: Tighten the Remaining Boundary and Trustwork Cluster

Why this is promising:

- The largest remaining repo-quality issues are now mostly about scope clarity, overclaiming, and durable outputs rather than missing headline skills.
- This work would improve the weakest remaining parts of the portfolio without creating new overlap.

If you choose this, prioritize:

- `e-contract`
- `e-report`
- `e-runbook`
- `e-comply`
- `e-scan`
- `e-secrets`
- `e-variant`
- `e-graph`
- `e-transfer`
- `e-health`
- `e-ship`

## Expectations For Your Output

When you finish, I want the repository in a better state, not just a set of ideas.

Your final work should include:

1. actual file changes
2. updated documentation
3. a short explanation of what you changed and why
4. what research materially changed or confirmed the earlier conclusions
5. validation results

## Constraints

- stay within this repository’s conventions
- do not introduce Claude-specific framing into public-facing repo content
- avoid unrelated cleanup
- keep changes focused and intentional
- prefer quality over volume

## Suggested Working Style

1. Read the core repo docs and recent analysis.
2. Use `Explore` for targeted codebase inspection.
3. Use `researcher` for external verification and comparison.
4. If needed, use `prosecutor` to pressure-test overlap, weak assumptions, or scope problems.
5. Use `documentator` to help ensure doc consistency if you touch multiple docs.
6. Make the changes.
7. Update docs.
8. Validate.

## Starting Files

Start here:

- `CLAUDE.md`
- `README.md`
- `docs/skill-gap-analysis-2026-04-02.md`

Then inspect the most relevant existing skills for whatever direction you choose.

Do not assume the previous agent’s conclusions are correct. Verify them.

Your mandate is to produce the strongest next increment for this repo.

---