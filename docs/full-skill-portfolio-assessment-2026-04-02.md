# Full Skill Portfolio Assessment 2026-04-02

## Scope

This report assesses all 90 current eSkill skills.

Historical note: this report reflects the portfolio as of 2026-04-02. The later changelog consolidation removed `e-changelog` as a standalone skill and folded that responsibility into `e-keeplog` and `e-release`.

For each skill, it records:

- status: `keep`, `improve`, or `likely redundant`
- why that status was chosen
- the concrete next action

This report combines:

1. direct repo inspection of every `SKILL.md`
2. plugin-level internal audits
3. deep external benchmark research on the weak, overlapping, or boundary-sensitive areas
4. an adversarial review of the most suspect skills

## Executive Summary

The portfolio is strong overall. Most skills are distinct, well-scoped, and aligned with eSkill's core purpose: orchestrating eMCP primitives into higher-level workflows.

The largest confirmed issue at the start of this assessment was **coverage duplication** between `e-coverage` and `e-threshold`. That duplication has now been addressed by making `e-coverage` the analysis workflow and narrowing `e-threshold` to CI policy enforcement.

The most important remaining improvement clusters are:

1. documentation/workflow boundary cleanup around `e-report`, `e-runbook`, `e-graph`, `e-transfer`, `e-health`, and `e-ship`
2. security hardening workflow durability around `e-comply`, `e-scan`, `e-secrets`, and `e-variant`
3. API boundary clarity around `e-contract`
4. frontend follow-up work around `e-css` and any residual boundary drift after the recently landed frontend-cluster upgrade

## Portfolio Summary

| Status | Count |
|--------|------:|
| Keep | 78 |
| Improve | 12 |
| Likely redundant | 0 |

## External Benchmark Notes

The following external conclusions materially informed this report:

- Coverage reporting and threshold enforcement are typically part of a tightly linked workflow in mainstream tooling such as Jest, Vitest, and Coverage.py; in this repo, that now means `e-coverage` owns analysis and `e-threshold` owns policy enforcement.
- Contract testing and API mocking are distinct practices; Pact-style CDC and MSW-style mocking should not be treated as interchangeable without explicit decision logic.
- Frontend best practice strongly supports design-token standardization, component-level visual testing, accessibility-first component testing, Core Web Vitals awareness, and container-query-aware responsive auditing.
- Runbooks benefit from standardized operational structure rather than generic markdown assembly.
- Health dashboards and ship-readiness checks are distinct, but eSkill's current implementation still needs sharper differentiation.

Key external sources used in the benchmark pass:

- Jest: https://jestjs.io/docs/configuration#coveragethreshold
- Vitest: https://vitest.dev/guide/coverage.html
- Coverage.py: https://coverage.readthedocs.io/
- Pact: https://docs.pact.io/
- MSW: https://mswjs.io/docs/
- Martin Fowler on tests and TDD: https://martinfowler.com/
- W3C WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
- W3C Design Tokens: https://design-tokens.github.io/community-group/format/
- MDN Responsive Design: https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout/Responsive_Design
- web.dev Core Web Vitals: https://web.dev/articles/vitals
- Storybook docs: https://storybook.js.org/docs/
- Playwright screenshots: https://playwright.dev/docs/test-snapshots
- PagerDuty runbook guidance: https://www.pagerduty.com/resources/learn/what-is-a-runbook/
- Kubernetes probes and lifecycle: https://kubernetes.io/docs/

## Plugin Assessments

### eskill-api

| Skill | Status | Why | Next Action |
|-------|--------|-----|-------------|
| e-contract | improve | Valuable domain, but the current workflow mixes consumer-driven contracts, mock-based API simulation, and schema validation without a strong decision tree. | Clarify Pact vs. MSW modes, or explicitly split the workflow internally into provider-contract and mock-contract branches. |
| e-graphql | keep | Clear schema and resolver review workflow with specific GraphQL concerns. | No immediate change. |
| e-loadtest | keep | Clean scope and strong distinction from mocking or contract testing. | No immediate change. |
| e-mock | keep | Distinct from e-contract and e-loadtest; focused on mock generation. | No immediate change. |
| e-openapi | keep | Focused specification validation workflow. | No immediate change. |
| e-version | keep | Clearly scoped to versioning policy and breakage analysis. | No immediate change. |

### eskill-coding

| Skill | Status | Why | Next Action |
|-------|--------|-----|-------------|
| e-changelog | keep | Focused, useful, and differentiated. | No immediate change. |
| e-deadcode | keep | Clear static-analysis workflow with concrete value. | No immediate change. |
| e-debug | keep | New skill fills a real red-to-green gap and is well differentiated from refactoring and review. | No immediate change. |
| e-deps | keep | Broad but still coherent dependency-audit workflow. | No immediate change. |
| e-integ | keep | Distinct boundary-oriented test generation workflow. | No immediate change. |
| e-merge | keep | Specific conflict-resolution workflow with clear purpose. | No immediate change. |
| e-migrate | keep | Focused on DB schema migration planning and risk. | No immediate change. |
| e-nplus | keep | Narrow, valuable, and not duplicated elsewhere. | No immediate change. |
| e-perf | keep | Properly scoped performance-investigation workflow. | No immediate change. |
| e-prune | keep | Clear repository-maintenance skill. | No immediate change. |
| e-refactor | keep | Strong safety-first design and distinct from debugging. | No immediate change. |
| e-review | keep | Good semantic diff review workflow. | No immediate change. |
| e-surface | keep | Clear public-surface extraction workflow. | No immediate change. |
| e-testgen | keep | Useful unit-test scaffolding skill with distinct scope. | No immediate change. |
| e-threshold | keep | After narrowing, it now has a distinct role: encoding thresholds, no-regression rules, and ratchets into CI policy rather than duplicating coverage analysis. | No immediate change. |

### eskill-devops

| Skill | Status | Why | Next Action |
|-------|--------|-----|-------------|
| e-ci | keep | Strong CI generation skill with clear platform targeting. | No immediate change. |
| e-cost | keep | Distinct infrastructure-cost estimation workflow. | No immediate change. |
| e-deploy | keep | Good deployment-gate workflow. | No immediate change. |
| e-infra | keep | Broad IaC security review still reads as justified and distinct from e-terra. | Improve cross-references with e-terra over time, but keep the skill. |
| e-kube | keep | End-to-end K8s generation skill is well differentiated. | No immediate change. |
| e-monitor | keep | Specific observability/alerting workflow. | No immediate change. |
| e-recover | keep | Legitimate DR-focused workflow. | No immediate change. |
| e-release | keep | Clean release-management workflow. | No immediate change. |
| e-terra | keep | Terraform-specific quality and structure review remains justified next to e-infra. | Improve cross-references with e-infra over time, but keep the skill. |

### eskill-emcp

| Skill | Status | Why | Next Action |
|-------|--------|-----|-------------|
| e-mcp | keep | Essential reference layer for the rest of the repo. | Keep current and refresh regularly. |

### eskill-frontend

| Skill | Status | Why | Next Action |
|-------|--------|-----|-------------|
| e-bundle | keep | The recent upgrade connected bundle analysis to Core Web Vitals, Lighthouse CI, and lab-vs-field limitations in a credible way. | No immediate change. |
| e-component | keep | Clear scaffold-generation skill with good scope separation from render and visual testing. | No immediate change. |
| e-css | improve | Good static CSS audit, but it treats multiple CSS architectures too generically. | Add architecture-specific rules for Tailwind, CSS Modules, CSS-in-JS, and other patterns. |
| e-design | keep | The recent upgrade narrowed its ownership toward design direction, implementation, and handoff, with downstream validation delegated more cleanly. | No immediate change. |
| e-render | keep | Strong live-browser validation sink. | No immediate change. |
| e-responsive | keep | The recent upgrade added container-query-aware guidance, modern viewport units, and clearer handoff to rendered validation. | No immediate change. |
| e-stories | keep | The recent upgrade added play-function patterns, clearer Storybook testing roles, and stronger accessibility integration. | No immediate change. |
| e-tokens | keep | The recent upgrade added DTCG awareness, tiered token hierarchy validation, and Style Dictionary pipeline recognition. | No immediate change. |

### eskill-intelligence

| Skill | Status | Why | Next Action |
|-------|--------|-----|-------------|
| e-carto | keep | Useful code-structure mapping skill. | Improve boundary explanation relative to e-graph, but keep the skill. |
| e-context | keep | Session/export use case remains distinct enough to retain. | Improve cross-references to e-recap and e-transfer over time. |
| e-debt | keep | Focused and useful. | No immediate change. |
| e-decide | keep | Strong internal decision-analysis workflow. | No immediate change. |
| e-graph | improve | It is not redundant, but its distinction from e-carto is still too implicit. | Clarify that it is for knowledge extraction and relationship synthesis, not just structural mapping. |
| e-learn | keep | Distinct onboarding and exploration skill. | No immediate change. |
| e-research | keep | Clear external research workflow. | No immediate change. |
| e-transfer | improve | Useful, but the output guidance should adapt more explicitly to audience type. | Add audience-specific output templates and transfer styles. |

### eskill-meta

| Skill | Status | Why | Next Action |
|-------|--------|-----|-------------|
| e-decompose | keep | Well-scoped planning/decomposition skill. | No immediate change. |
| e-health | improve | The overall category is justified, but the scoring model overreaches in places, especially around pseudo-coverage proxies. | Tighten scoring logic and avoid weak structural proxies shaping overall health grades. |
| e-init | keep | Strong and distinct project initialization skill. | No immediate change. |
| e-keeplog | keep | Focused changelog maintenance skill. | No immediate change. |
| e-recap | keep | Session-level recap remains useful and distinct. | No immediate change. |
| e-retro | keep | Sprint/milestone retrospective still has distinct scope. | No immediate change. |
| e-ship | improve | Distinct from e-health in concept, but still too similar in scoring and repo-wide checklist execution. | Sharpen release-readiness-specific criteria and reduce overlap with generic health scoring. |

### eskill-office

| Skill | Status | Why | Next Action |
|-------|--------|-----|-------------|
| e-adr | keep | Strong and focused. | No immediate change. |
| e-apidoc | keep | Good API-doc generation workflow. | No immediate change. |
| e-diagram | keep | Useful visualization skill distinct enough to keep. | Improve relationship messaging with e-carto over time, but do not remove. |
| e-doc | keep | Clear document-conversion scope. | No immediate change. |
| e-pipe | keep | Distinct ETL/data-ingestion utility. | No immediate change. |
| e-report | improve | Valuable skill, but it currently sprawls into adjacent concerns such as diagram and data-pipeline orchestration. | Refocus on report assembly, structure, and synthesis rather than owning neighboring workflows. |
| e-runbook | improve | Legitimate domain, but it should follow stronger, battle-tested operational structure and avoid becoming generic report assembly. | Add standardized runbook structure and tighten ops-specific extraction. |
| e-sheet | keep | Clear spreadsheet-validation scope. | No immediate change. |
| e-slides | keep | Narrow and justified PPTX extraction skill. | No immediate change. |

### eskill-quality

| Skill | Status | Why | Next Action |
|-------|--------|-----|-------------|
| e-a11y | keep | The recent upgrade materially improved honesty about automation boundaries, updated WCAG framing, and strengthened downstream handoffs. | No immediate change. |
| e-checksum | keep | Distinct and valuable integrity workflow. | No immediate change. |
| e-comply | improve | The skill tackles a legitimate problem, but it currently overclaims what static repository inspection can prove across regulatory frameworks. | Narrow framework claims, separate automatable checks from manual evidence, and avoid false PASS/FAIL certainty. |
| e-config | keep | Useful config-drift and environment-audit skill. | No immediate change. |
| e-defaults | keep | Strong fail-open/fail-secure focus. | No immediate change. |
| e-diffrev | keep | Good security-focused review specialization. | No immediate change. |
| e-license | keep | Focused, distinct dependency-license workflow. | No immediate change. |
| e-lint | keep | Broad but coherent code-standard workflow. | No immediate change. |
| e-sbom | keep | Supply-chain inventory workflow is justified. | No immediate change. |
| e-scan | improve | Strong scanner, but it should produce more durable outputs and reduce duplicated secrets logic with related skills. | Add machine-readable output and CI-rule export path. |
| e-secrets | improve | Strong incident-response side, but prevention could be much stronger. | Generate preventive hook/scanner config after incident cleanup. |
| e-variant | improve | Valuable post-discovery workflow, but its findings should be exportable into durable future checks. | Add Semgrep-style or rule-export output from discovered patterns. |

### eskill-system

| Skill | Status | Why | Next Action |
|-------|--------|-----|-------------|
| e-backup | keep | Strong and clearly distinct. | No immediate change. |
| e-containers | keep | Narrow Docker/container health workflow. | No immediate change. |
| e-disk | keep | Clear disk-usage/cleanup workflow. | No immediate change. |
| e-env | keep | Clear environment-validation workflow. | No immediate change. |
| e-logs | keep | Strong incident/log analysis skill. | No immediate change. |
| e-ports | keep | Focused conflict-detection utility. | No immediate change. |
| e-procs | keep | Distinct process-analysis scope. | No immediate change. |
| e-snapshot | keep | Useful system-state capture workflow. | No immediate change. |

### eskill-testing

| Skill | Status | Why | Next Action |
|-------|--------|-----|-------------|
| e-coverage | keep | It now owns the full coverage analysis workflow, including threshold comparison, risk ranking, and next-test prioritization. | No immediate change. |
| e-e2e | keep | Clear end-to-end orchestration skill. | No immediate change. |
| e-factory | keep | Distinct data-factory workflow. | No immediate change. |
| e-flaky | keep | Clear flaky-test investigation workflow. | No immediate change. |
| e-mutate | keep | Distinct mutation-testing workflow. | No immediate change. |
| e-proptest | keep | Distinct property-based testing workflow. | No immediate change. |
| e-visual | keep | The recent upgrade added component-level and state-level capture patterns, baseline guidance, and clearer Playwright integration. | No immediate change. |

## Highest Priority Recommendations

1. Clarify `e-contract`.
2. Refocus `e-report` and structure `e-runbook` more strictly.
3. Reduce overclaiming in `e-comply` and strengthen durable outputs in `e-scan`, `e-secrets`, and `e-variant`.
4. Sharpen the `e-health` vs `e-ship` distinction in implementation, not just intent.
5. Improve `e-css` with architecture-specific audit guidance.

Completed on 2026-04-02:

- Consolidated coverage analysis into `e-coverage` and narrowed `e-threshold` to policy enforcement.
- Upgraded the frontend rigor cluster across `e-design`, `e-tokens`, `e-stories`, `e-visual`, `e-responsive`, `e-bundle`, and `e-a11y`.

## Skills Marked Likely Redundant

No skills are currently classified as likely redundant after the coverage-workflow split was resolved.

## Notes

- This report is intentionally conservative about marking skills redundant. Most boundary problems in this repo are better framed as scope and clarity issues than outright deletion candidates.
- Where external research validated separation, the report keeps the skill even if it still needs sharper writing or stronger outputs.
- The portfolio is strong. The work ahead is mostly about tightening boundaries, reducing duplicate logic, and increasing rigor in a handful of skills.