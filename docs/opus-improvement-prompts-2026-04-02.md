# Opus Improvement Prompts - 2026-04-02

This document packages the remaining improvement prompts into durable form.

The coverage cluster is intentionally omitted here because it has already been addressed in-repo:

- `e-coverage` now owns coverage analysis
- `e-threshold` now owns coverage policy and CI enforcement

Use these prompts with Opus after that split.

## Shared Operating Sequence

Apply this sequence to every prompt below:

1. Run `researcher` first and gather at least two independent sources for each substantive claim. Prefer official docs, standards, or mature project documentation.
2. Do the repo work directly. Do not stop at analysis.
3. Run `prosecutor` after implementation to pressure-test overlap, overclaiming, regressions, and weak workflow logic.
4. Update `README.md` and any impacted docs under `docs/`.
5. Run at least `python scripts/validate_skills.py --strict`, and add `--lint`, `--require-workflow`, `--max-lines 500`, and `--no-duplicates` when the scope is substantial.

## Prompt 1: e-contract Boundary Cleanup

You are working in the `eSkill` repository at `c:/Users/deyan/Projects/eSkill`.

Your target is `plugins/eskill-api/skills/e-contract/SKILL.md`.

Start by running `researcher` to compare modern consumer-driven contract testing guidance against mock-server workflows. I want at least two independent sources for every meaningful recommendation, with a strong preference for Pact docs, first-party framework docs, and mature testing guidance.

Then inspect the current `e-contract` skill and decide whether it should stay as one skill with clearer branching or become materially more explicit about its modes. The core problem to solve is that the current workflow blurs Pact-style CDC, schema validation, and mock-based API simulation.

Deliverables:

- rewrite or materially tighten `e-contract/SKILL.md`
- make the decision tree explicit about when to use consumer-driven contracts vs mock-driven workflows
- clarify the relationship with `e-mock` and `e-openapi`
- update `README.md` and any relevant docs if the workflow meaning changes

After implementation, run `prosecutor` on the changed files and ask it to look specifically for residual overlap, fuzzy branch logic, and claims that are not supported by the workflow.

## Prompt 2: Frontend Rigor Cluster

You are working in the `eSkill` repository at `c:/Users/deyan/Projects/eSkill`.

Your targets are:

- `plugins/eskill-frontend/skills/e-design/SKILL.md`
- `plugins/eskill-frontend/skills/e-tokens/SKILL.md`
- `plugins/eskill-frontend/skills/e-visual/SKILL.md`
- `plugins/eskill-frontend/skills/e-responsive/SKILL.md`
- `plugins/eskill-frontend/skills/e-bundle/SKILL.md`
- `plugins/eskill-frontend/skills/e-stories/SKILL.md`
- `plugins/eskill-quality/skills/e-a11y/SKILL.md`

Run `researcher` first. I want external benchmarking against authoritative sources for design tokens, Storybook interaction testing, Playwright visual testing, WCAG automation boundaries, responsive/container-query guidance, and Core Web Vitals. Use at least two independent sources per substantive recommendation.

Then improve this cluster with a clear boundary model:

- `e-design` should focus on design direction, system decisions, and handoff boundaries rather than owning every implementation or validation concern
- `e-tokens` should cover token-system structure, naming, validation, and transformation workflow more rigorously
- `e-visual` should support component-level and state-level visual regression flows, not only page-level flows
- `e-responsive` should account for container queries and more modern responsive checks
- `e-bundle` should connect bundle findings to user-facing performance impact, including Core Web Vitals where appropriate
- `e-stories` should support modern Storybook interaction patterns such as play functions where that fits
- `e-a11y` should tighten the high-value automated accessibility surface without overclaiming full compliance

Deliverables:

- substantive SKILL.md improvements across the cluster
- cleaner Related Skills boundaries across the affected files
- `README.md` updates if descriptions or server mappings need adjustment
- an updated doc under `docs/` if you need to explain the refined cluster model

After implementation, run `prosecutor` on the changed files with emphasis on boundary drift, duplicated workflow steps, fashionable-but-empty language, and claims that exceed what the tools can actually verify.

## Prompt 3: Security Durability Cluster

You are working in the `eSkill` repository at `c:/Users/deyan/Projects/eSkill`.

Your targets are:

- `plugins/eskill-quality/skills/e-comply/SKILL.md`
- `plugins/eskill-quality/skills/e-scan/SKILL.md`
- `plugins/eskill-quality/skills/e-secrets/SKILL.md`
- `plugins/eskill-quality/skills/e-variant/SKILL.md`

Run `researcher` first and ground the work in at least two independent sources per claim. Prefer OWASP, regulator or framework primary sources, mature scanner docs, and reputable platform security docs.

The core goals are:

- reduce overclaiming in `e-comply`
- separate automatable checks from manual evidence gathering
- make `e-scan`, `e-secrets`, and `e-variant` produce more durable follow-on outputs such as reusable rules, configs, or CI-oriented artifacts when appropriate

Deliverables:

- narrowed and more defensible `e-comply`
- stronger durable-output guidance in the scanning skills
- updated Related Skills sections so the four skills work as a coherent cluster rather than partially duplicating one another
- `README.md` and docs updates if the scope descriptions materially change

After implementation, run `prosecutor` and ask it to focus on false certainty, duplicated secrets logic, and whether the revised workflows actually produce reusable defensive artifacts instead of only ephemeral findings.

## Prompt 4: Report and Runbook Boundaries

You are working in the `eSkill` repository at `c:/Users/deyan/Projects/eSkill`.

Your targets are:

- `plugins/eskill-office/skills/e-report/SKILL.md`
- `plugins/eskill-office/skills/e-runbook/SKILL.md`

Run `researcher` first. Compare structured reporting guidance against operational runbook best practices using at least two independent sources per recommendation. Prefer operational documentation from established vendors and high-quality engineering guidance.

The core problem is boundary drift:

- `e-report` should focus on assembling and structuring reports
- `e-runbook` should follow stronger incident and operations-oriented structure rather than reading like generic report assembly

Deliverables:

- tighten both skills so their scopes are unmistakably different
- strengthen `e-runbook` structure around procedures, prerequisites, decision points, rollback paths, and escalation guidance where appropriate
- keep `e-report` focused on synthesis and report construction
- update docs if you need a short rationale note for the new boundary

After implementation, run `prosecutor` and ask it to test whether an engineer can still confuse the two skills after reading the revised files.

## Prompt 5: Intelligence Transfer Boundaries

You are working in the `eSkill` repository at `c:/Users/deyan/Projects/eSkill`.

Your targets are:

- `plugins/eskill-intelligence/skills/e-graph/SKILL.md`
- `plugins/eskill-intelligence/skills/e-carto/SKILL.md`
- `plugins/eskill-intelligence/skills/e-transfer/SKILL.md`

Run `researcher` first with a focus on knowledge graph practices, architecture mapping, and knowledge-transfer patterns. Use at least two independent sources for every substantive recommendation.

The core goals are:

- make `e-carto` clearly about code and structure mapping
- make `e-graph` clearly about knowledge extraction and relationship synthesis across broader project artifacts
- make `e-transfer` explicitly adapt its output to audience type, such as engineer, operator, or stakeholder

Deliverables:

- stronger boundary language across the three skills
- audience-aware output guidance in `e-transfer`
- improved cross-references so the cluster composes instead of blurring

After implementation, run `prosecutor` and ask it to look for conceptual overlap, redundant workflow steps, and weak audience assumptions.

## Prompt 6: Meta Readiness Boundaries

You are working in the `eSkill` repository at `c:/Users/deyan/Projects/eSkill`.

Your targets are:

- `plugins/eskill-meta/skills/e-health/SKILL.md`
- `plugins/eskill-meta/skills/e-ship/SKILL.md`

Run `researcher` first with at least two independent sources per claim. Compare project health dashboards, scorecards, and release-readiness or launch-checklist practices.

The core goals are:

- keep `e-health` as an ongoing health-assessment workflow without leaning on weak proxy scoring
- keep `e-ship` as a release-readiness workflow with sharper ship/no-ship criteria
- reduce implementation overlap between the two skills

Deliverables:

- clearer scoring and evidence rules in `e-health`
- sharper release-gate framing in `e-ship`
- improved separation of concerns in Related Skills and descriptions
- docs updates if the repo-level portfolio explanation should reflect the clearer split

After implementation, run `prosecutor` and ask it to look for pseudo-metrics, inflated confidence, and checklist duplication.

## Prompt 7: Frontend CSS and Boundary Follow-Up

You are working in the `eSkill` repository at `c:/Users/deyan/Projects/eSkill`.

Your targets are:

- `plugins/eskill-frontend/skills/e-css/SKILL.md`
- `plugins/eskill-frontend/skills/e-design/SKILL.md`
- `plugins/eskill-frontend/skills/e-tokens/SKILL.md`
- `plugins/eskill-frontend/skills/e-render/SKILL.md`
- `plugins/eskill-testing/skills/e-visual/SKILL.md`
- `README.md`
- any affected docs under `docs/`

Run `researcher` first. I want at least two independent sources for each substantive recommendation, with a strong preference for MDN, W3C or CSSWG materials, framework docs, and mature tool documentation.

Your main job is to finish the remaining frontend follow-up work without reopening already-settled scope.

The current state is:

- the main frontend rigor cluster has already been upgraded
- `e-css` is still the clearest remaining frontend improvement target
- there may still be small boundary ambiguities between `e-design`, `e-tokens`, `e-render`, and `e-visual`

Deliverables:

1. Upgrade `e-css` so it stops reading like a generic CSS lint pass and becomes architecture-aware.
2. Add explicit guidance for at least these architecture families where justified by research:
	- Tailwind and utility-first CSS
	- CSS Modules
	- CSS-in-JS or styled-components style systems
	- global CSS or SCSS pipelines
3. Make the skill distinguish between:
	- unused or redundant CSS
	- architecture-specific anti-patterns
	- cascade or specificity problems
	- rendering-cost issues that belong in CSS analysis rather than bundle analysis
4. Re-check the boundaries between:
	- `e-design` as design direction and implementation
	- `e-tokens` as token-structure and compliance validation
	- `e-render` as live render verification
	- `e-visual` as continuous regression protection
5. Tighten Related Skills sections and README descriptions only where needed.

Constraints:

- do not rework the whole frontend cluster again unless you find a real defect
- do not turn `e-css` into a duplicate of `e-lint`, `e-bundle`, or `e-responsive`
- prefer sharper workflow decisions over longer prose
- avoid fashionable wording that is not operationally useful

After implementation:

1. Run `prosecutor` on the changed files.
2. Ask it to look specifically for remaining boundary drift, duplicated workflow ownership, generic CSS advice, and claims that are not defensible from the workflow.
3. Update `README.md` and any affected docs.
4. Run at least:

```bash
python scripts/validate_skills.py --strict
python scripts/validate_skills.py --lint
```