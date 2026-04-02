# Skill Gap Analysis 2026-04-02

## Research Question

Which current eSkill to eMCP mappings needed correction, and which missing or improvable skills should be prioritized based on repeated evidence from current coding-agent and frontend workflow documentation?

## Executive Summary

The current repository already covers most of the eSkill to eMCP surface area well. The main correction was not a missing architecture layer, but README drift: a few server and skill rows no longer matched the actual workflow text in the SKILL.md files.

After correcting the documented mappings, the highest-confidence additions are `e-debug`, `e-codemod`, and `e-incident`. These are all common workflow shapes in modern coding or operations guidance, and they fit eSkill's orchestration role cleanly. The highest-confidence upgrades are concentrated in frontend workflows: formal design-token handling, accessibility-first component and story scaffolding, stronger visual regression flows, and explicit Core Web Vitals plus Lighthouse validation.

Two broad categories surfaced in the wider research but do not look like immediate eSkill priorities: persistent agent memory and multi-agent orchestration. They are real demand areas, but they fit the eAgent/runtime layer more naturally than self-contained workflow skills.

## Mapping Corrections Applied

| Area | Change | Reason |
|------|--------|--------|
| `e-research` README row | Removed `task` | The skill body references `docs_*`, `fetch_*`, and `think_*`, but not `task_*`. |
| `e-retro` README row | Added `egrep`, `reasoning` | The skill explicitly uses `egrep_search` and `think_search`. |
| Server coverage intro | Reworded usage claim | Some servers are documented by `e-mcp` but not used by a workflow skill yet. |
| `@emcp/server-browser` | Changed plugin coverage to `frontend, testing` | README previously attributed browser usage to intelligence, but current workflow usage sits in frontend/testing. |
| `@emcp/server-media` | Marked `emcp (reference only)` | Current workflow skills do not invoke `media_*`. |
| `@emcp/server-clipboard` | Marked `emcp (reference only)` | Current workflow skills do not invoke `clip_*`. |
| `@emcp/server-computer-use` | Changed plugin coverage to `frontend` | Current workflow usage is in `e-render`. |
| `@emcp/server-time` | Marked `emcp (reference only)` | Current workflow skills do not invoke `current_time` or `convert_time`. |

## Recommended New Skills

| Candidate | Why It Is Still Missing | Evidence | Suggested eMCP Servers | Priority |
|-----------|-------------------------|----------|------------------------|----------|
| ~~`e-debug`~~ | **Built.** Added to eskill-coding. Owns the loop from failing test or stack trace to root-cause analysis, minimal patch, and verification rerun. Includes iteration limits, hypothesis verification, and regression checking. | VS Code Copilot explicitly frames agent workflows around debugging and fixing failing tests, tracing root causes, applying a fix, and rerunning verification [1]. Aider documents automatic test execution and automatic fix attempts when test commands fail [2]. | `lsp`, `ast`, `shell`, `test-runner`, `git`, `filesystem`, `egrep` | ~~High~~ Done |
| `e-codemod` | `e-refactor` is safety-first refactoring guidance, but it is not a dedicated migration-scale codemod workflow with dry runs, transforms, and migration reporting. | jscodeshift describes itself as a toolkit for running codemods over multiple JavaScript or TypeScript files and includes dry-run, ignore, parser, and test utilities [3]. ast-grep supports structural search and replace, interactive rewrites, lint-style scanning, and polyglot large-scale rewriting [4]. | `ast`, `filesystem`, `diff`, `git`, `test-runner`, `shell` | High |
| `e-incident` | `e-logs` parses failures and `e-runbook` documents operations, but there is no skill that assembles incidents into a timeline, response workflow, and postmortem-ready output. | PagerDuty's incident response docs break incident handling into before, during, and after phases with severity, roles, and postmortem guidance [5]. Monzo's Response is built specifically to reduce cognitive burden during incidents and create information-rich reports for later learning [6]. | `log`, `git`, `filesystem`, `shell`, `markdown`, `data-file`, `reasoning` | Medium-High |

## Recommended Skill Upgrades

| Target Skills | Improvement | Evidence | Suggested eMCP Servers Or Workflow Changes | Priority |
|--------------|-------------|----------|--------------------------------------------|----------|
| ~~`e-design`, `e-tokens`, `e-component`~~ | **Done.** `e-tokens` now includes W3C DTCG 2025.10 format awareness, three-tier token hierarchy (global/semantic/component), Style Dictionary pipeline recognition, and explicit validation boundaries. `e-design` refocused on direction and handoff rather than owning validation. | The W3C Design Tokens Community Group published a stable 2025.10 specification intended for implementation [7]. Carbon documents tokens as a consistent, reusable, scalable replacement for hard-coded values and distinguishes core from component tokens [8]. | `e-tokens` added `data-file` and `egrep` to server list; token hierarchy and format detection added. | ~~High~~ Done |
| ~~`e-component`, `e-stories`, `e-a11y`~~ | **Done.** `e-stories` now includes `@storybook/test` play function patterns, `@storybook/addon-a11y` integration with correct mode names (`off`/`todo`/`error`), and dual documentation-test framing. `e-a11y` now includes honest automation boundary framing (41-57% detection rate), "What This Skill Cannot Check" section, and WCAG 2.2 update. | Storybook's accessibility testing is built on axe-core, runs in CI, and supports `off`, `todo`, and `error` modes [9]. Testing Library recommends semantic query priority led by `getByRole` and `getByLabelText` [10]. Deque reports 57% detection rate [Deque, 2023]. GDS found 41% in controlled testing [GDS, 2017]. | Cross-skill handoffs tightened across `e-stories`, `e-a11y`, `e-design`, and `e-tokens`. | ~~High~~ Done |
| ~~`e-render`, `e-visual`~~ | **Done.** `e-visual` now supports page-level, component-level (`LocatorAssertions`), and state-level (hover, focus, error) visual regression. Includes Playwright `mask`, `maskColor`, `stylePath`, `animations` options. Platform-specific baselines documented. Font rendering non-determinism acknowledged with Docker mitigation. | Playwright provides `toHaveScreenshot()` on both `PageAssertions` and `LocatorAssertions` [11]. Storybook visual testing provides story-based baselines [12]. | `e-visual` added `image` to server list; component and state capture documented. | ~~High~~ Done |
| ~~`e-render`, `e-bundle`~~ | **Done.** `e-bundle` now includes Core Web Vitals assessment (LCP, INP, CLS with current thresholds), FID-to-INP transition noted, Lighthouse CI regression checking, and explicit lab-vs-field data limitations. | web.dev defines LCP, INP, and CLS thresholds at 75th percentile [13]. Lighthouse CI runs lab data with documented throttling limitations [14]. Google confirms lab data cannot measure INP accurately. | `e-bundle` added `egrep` and `ast` to server list; Step 10 (CWV assessment) added. | ~~High~~ Done |

## Platform-Scope Ideas, Not Immediate eSkill Priorities

These came up repeatedly in the broader research, but they are better treated as eAgent or runtime concerns unless a concrete workflow boundary emerges:

- Persistent memory across sessions
- Multi-agent orchestration and delegation

They are worth revisiting after the workflow-skill gaps above are addressed.

## Recommendation Order

1. ~~Build `e-debug`.~~ Done. Added to eskill-coding with 317-line SKILL.md.
2. Build `e-codemod`.
3. ~~Upgrade the frontend cluster: `e-design`, `e-tokens`, `e-component`, `e-render`, `e-visual`.~~ Done. Upgraded `e-design`, `e-tokens`, `e-stories`, `e-visual`, `e-responsive`, `e-bundle`, and `e-a11y`. Added DTCG token support, Storybook interaction testing, component-level visual regression, container queries, Core Web Vitals, and honest accessibility automation boundaries.
4. Add `e-incident` once the coding gaps are closed.

## Sources Consulted

1. GitHub Copilot in VS Code overview: https://code.visualstudio.com/docs/copilot/overview
2. Aider linting and testing: https://aider.chat/docs/usage/lint-test.html
3. jscodeshift: https://github.com/facebook/jscodeshift
4. ast-grep: https://ast-grep.github.io/
5. PagerDuty incident response: https://response.pagerduty.com/
6. Monzo Response: https://github.com/monzo/response
7. Design Tokens Technical Reports 2025.10: https://www.designtokens.org/tr/2025.10/
8. Carbon Design System color tokens: https://carbondesignsystem.com/elements/color/tokens/
9. Storybook accessibility testing: https://storybook.js.org/docs/writing-tests/accessibility-testing
10. Testing Library query guidance: https://testing-library.com/docs/queries/about/
11. Playwright visual comparisons: https://playwright.dev/docs/test-snapshots
12. Storybook visual testing: https://storybook.js.org/docs/writing-tests/visual-testing
13. Web Vitals: https://web.dev/articles/vitals
14. Lighthouse CI: https://github.com/GoogleChrome/lighthouse-ci

## Notes

- This report intentionally excludes one-source claims, marketplace anecdotes, and vague popularity statements.
- The recommendations above are limited to claims corroborated by at least two independent sources.
- The focus is workflow fit for eSkill, not every trend in the broader agent ecosystem.