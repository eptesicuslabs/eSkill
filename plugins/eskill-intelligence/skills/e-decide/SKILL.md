---
name: e-decide
description: "Guides structured technical decisions with trade-off analysis and produces an architecture decision record. Use when choosing between libraries, picking an implementation approach, or making any architectural choice. Also applies when: help me decide, which option should I pick, write an ADR, compare trade-offs."
---

# Decision Framework

This skill facilitates rigorous technical decision-making by guiding the user through a structured process of defining options, evaluating trade-offs, and documenting the rationale. It produces a reasoning chain and an architecture decision record (ADR) that preserves the decision context for future reference.

## Prerequisites

The user should have a decision to make and ideally some initial options in mind. If the user is unsure what the options are, begin with an exploration phase to identify possibilities before entering the evaluation phase.

## Procedure

### Step 1: Define the Decision and Constraints

Establish the decision context clearly before evaluating options.

- State the decision to be made in a single sentence. For example: "Which message queue should we adopt for asynchronous task processing?"
- Identify the constraints that bound the decision:
  - **Time constraints**: When must this be decided? When must it be implemented?
  - **Resource constraints**: Team size, budget, available expertise.
  - **Technical constraints**: Must integrate with existing systems, must support specific protocols, must run on specific infrastructure.
  - **Organizational constraints**: Approved technology lists, compliance requirements, vendor preferences.
- Identify the stakeholders: who is affected by this decision? Who has veto power?
- Identify the urgency: is this reversible? What is the cost of delaying the decision?
- Record all of this as the decision context. This context will be included in the final ADR.

### Step 2: Start a Reasoning Chain

Use the eMCP reasoning server to begin a structured reasoning process. Before creating a new chain, check for prior decision analysis on the same topic.

- Use `think_status` to list all existing reasoning chains. Check whether a chain for this decision or a closely related decision already exists.
- If a prior chain exists, use `think_replay` to review the full reasoning trace and determine whether it can be extended or whether the prior analysis still holds. Avoid re-evaluating options that were already thoroughly analyzed unless new information has surfaced.
- Call `think_start` with the decision statement as the goal.
- Include the constraints as context for the reasoning chain.
- The reasoning chain provides a persistent, auditable record of the decision process. Each subsequent step adds to this chain.
- The reasoning chain should be linear when analyzing shared concerns (criteria definition, constraint analysis) and branching when evaluating individual options.

### Step 3: Enumerate Options

Identify all viable options to evaluate.

- Call `think_step` with type "thought" for each option. Record:
  - Option name: a short, memorable label.
  - Option description: a 2-3 sentence summary of what this option entails.
  - Initial impression: any preliminary assessment based on team experience or general knowledge.
- Aim for 2-5 options. Fewer than 2 means there is no real decision (but still document the rationale for the chosen approach). More than 5 usually means the options need to be pre-filtered.
- Include a "do nothing" or "status quo" option when applicable. This serves as a baseline for comparison.
- For each option, note any information gaps: what would you need to know to evaluate this option properly?
- If information gaps are significant, consider running the e-research skill for specific options before continuing with evaluation.

### Step 4: Evaluate Each Option

Create a reasoning branch for each option and evaluate it systematically.

For each option, call `think_branch` to start an evaluation branch, then evaluate the following dimensions:

**Pros** (call `think_step` with type "thought"):
- What does this option do well?
- What problems does it solve directly?
- What advantages does it have over the other options?
- Does it align well with existing team skills or infrastructure?
- Does it have strong community support, documentation, or tooling?

**Cons** (call `think_step` with type "thought"):
- What are the downsides or risks of this option?
- What problems does it not solve, or what new problems does it introduce?
- What are the known limitations or failure modes?
- Are there lock-in risks or vendor dependencies?
- Are there scalability, performance, or security concerns?

**Effort** (call `think_step` with type "thought"):
- What is the implementation complexity? Estimate in relative terms (low, medium, high) or time units.
- How much existing code needs to change?
- What new skills does the team need to acquire?
- What is the migration effort if moving from the current state?
- What is the operational overhead after implementation?

**Reversibility** (call `think_step` with type "thought"):
- How hard is it to change this decision later?
- Does this option create dependencies that are expensive to remove?
- Is there a natural migration path away from this option if it does not work out?
- What data migrations or API changes would reversal require?
- Rate reversibility: easily reversible (days), moderately reversible (weeks), difficult to reverse (months), practically irreversible.

Record each evaluation dimension as a separate step in the reasoning branch for auditability.

### Step 5: Define Evaluation Criteria

Establish the criteria against which options will be scored.

- Define 5-8 evaluation criteria relevant to this specific decision. Common criteria include:
  - **Functionality**: Does it meet the functional requirements?
  - **Performance**: Does it meet the performance requirements?
  - **Reliability**: What are the uptime, fault tolerance, and data durability characteristics?
  - **Scalability**: Can it handle projected growth?
  - **Security**: Does it meet security requirements?
  - **Developer experience**: How easy is it to develop with, debug, and maintain?
  - **Operational complexity**: How easy is it to deploy, monitor, and troubleshoot?
  - **Cost**: What is the total cost of ownership (licenses, infrastructure, maintenance time)?
  - **Community and ecosystem**: How active is the community? How mature is the ecosystem?
  - **Integration**: How well does it integrate with existing systems and tools?
  - **Learning curve**: How much effort to get the team productive?
  - **Time to implement**: How quickly can this be delivered?
- Assign a weight (1-5) to each criterion based on its importance to this particular decision. Not all criteria are equally important in every context.
- Call `think_step` with the criteria and weights to record them in the reasoning chain.

### Step 6: Score Each Option

Rate each option against every criterion to produce a quantitative comparison.

- For each option-criterion pair, assign a score from 1 to 5:
  - 1: Does not meet the criterion or meets it very poorly.
  - 2: Partially meets the criterion with significant gaps.
  - 3: Adequately meets the criterion.
  - 4: Meets the criterion well with minor gaps.
  - 5: Excels at this criterion.
- Calculate a weighted score for each option: sum of (criterion weight * option score) for all criteria.
- Construct a scoring matrix:

```
| Criterion           | Weight | Option A | Option B | Option C |
|---------------------|--------|----------|----------|----------|
| Functionality       |   5    |    4     |    5     |    3     |
| Performance         |   4    |    5     |    3     |    4     |
| Developer experience|   3    |    3     |    4     |    5     |
| ...                 |  ...   |   ...    |   ...    |   ...    |
| Weighted Total      |   -    |   XX     |   XX     |   XX     |
```

- Call `think_step` with the completed scoring matrix.
- Note: The scores are tools for discussion, not deterministic answers. A numerically lower-scoring option may still be the right choice if it excels on the most critical dimension in ways the weights do not capture.

### Step 7: Conclude the Reasoning Chain

Synthesize the evaluation into a recommendation. Use `think_summarize` to generate a structured summary of the reasoning chain before writing the conclusion. The summary surfaces the key evidence, trade-offs, and scoring patterns, making the conclusion easier to articulate.

- Call `think_conclude` with the following:
  - The recommended option and why.
  - The confidence level: high (clear winner), medium (close between top options), low (significant uncertainty remains).
  - The key factors that drove the recommendation.
  - What could change the recommendation (sensitivity analysis): if criterion X becomes more important, or if assumption Y proves false, the recommendation might change.
- If the decision is close between two options, state this clearly and identify what additional information would break the tie.
- If no option is clearly superior, recommend the most reversible option to preserve future flexibility.
- If the scoring reveals that the constraints are too restrictive (no option scores well), recommend revisiting the constraints before making a decision.

### Step 8: Store the Decision in Docs and Reasoning

Persist the decision and its rationale using the eMCP docs and reasoning servers.

**Index in docs server**:
- Use `docs_index` to index the generated ADR document so the decision is searchable via `docs_search`.

**Extend the reasoning chain**:
- The reasoning chain started in Step 2 already contains the full evaluation. Add final summary steps:
  - Call `think_step` with type="observation" recording the decision statement, date, and status (proposed, accepted, deprecated, superseded).
  - Call `think_step` with type="observation" recording: the decision context and constraints, the options considered, the evaluation criteria and weights, the scoring results, the recommendation and rationale, the confidence level.
  - Call `think_step` with type="thought" with evidenceFor/evidenceAgainst links to record relationships:
    - "affects": the decision affects specific components or systems.
    - "supersedes": if this decision replaces a previous decision.
    - "depends_on": if this decision depends on another decision.
    - "evaluated": the decision evaluated each option.
- The full reasoning chain can be reviewed later via `think_replay`, or distilled into a structured decision summary via `think_summarize`. Use `think_status` to check chain status at any point. If options were previously analyzed in a e-research reasoning chain, reference that chain rather than duplicating observations.

### Step 9: Generate Decision Record

Produce an Architecture Decision Record (ADR) in standard format.

Use the following template:

```markdown
# ADR-NNN: [Decision Title]

## Status

[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Date

[YYYY-MM-DD]

## Context

[Describe the situation that motivates this decision. What is the problem?
What are the constraints? What forces are at play? Include technical context,
business context, and any relevant history.]

## Options Considered

### Option 1: [Name]
[Description, pros, cons, effort, reversibility]

### Option 2: [Name]
[Description, pros, cons, effort, reversibility]

### Option 3: [Name]
[Description, pros, cons, effort, reversibility]

## Evaluation

[Scoring matrix and analysis]

| Criterion           | Weight | Option 1 | Option 2 | Option 3 |
|---------------------|--------|----------|----------|----------|
| [criterion]         | [1-5]  | [1-5]   | [1-5]   | [1-5]   |
| ...                 | ...    | ...      | ...      | ...      |
| **Weighted Total**  | -      | **XX**   | **XX**   | **XX**   |

## Decision

[State the decision clearly. "We will use [option] because [reasons]."]

## Consequences

### Positive
[What becomes easier or better as a result of this decision?]

### Negative
[What becomes harder or worse? What are the trade-offs accepted?]

### Risks
[What could go wrong? What are the mitigation strategies?]

## Notes

[Any additional context, links to research, related decisions, or follow-up actions.]
```

- Fill in the template with the information gathered during the decision process.
- If the project already has an ADR directory (adr/, decisions/, docs/decisions/), suggest placing the document there and assign the next sequential number.
- If no ADR directory exists, suggest creating one and starting with ADR-001.

## Scoring Matrix Format

For quick reference, here is the scoring matrix format to use during evaluation:

```
Criteria (weight 1-5) | Option A | Option B | Option C
---------------------------------------------------------
Criterion 1 (W)       |  score   |  score   |  score
Criterion 2 (W)       |  score   |  score   |  score
...
Weighted Total         |  total   |  total   |  total
```

Where:
- Weight (W) = importance of this criterion (1 = nice to have, 5 = critical)
- Score = how well the option meets the criterion (1 = poor, 5 = excellent)
- Weighted contribution = Weight * Score
- Weighted Total = sum of all weighted contributions

## Notes

- Decisions should be made at the last responsible moment: not too early (insufficient information) and not too late (too constrained to choose).
- For two-way door decisions (easily reversible), optimize for speed. For one-way door decisions (irreversible or expensive to reverse), optimize for thoroughness.
- When the team has strong prior experience with one option, weight that experience appropriately but guard against familiarity bias.
- The ADR is a living document. Update its status if the decision is later superseded or deprecated, and link to the new decision.
- Involve stakeholders in criteria definition and weighting. The evaluation itself can be done by the technical team, but the criteria reflect business priorities.

## Edge Cases

- **Only one viable option**: When constraints eliminate all but one option, the decision is already made. Document the constraints and rationale rather than running a full scoring exercise.
- **Criteria with conflicting stakeholder priorities**: Different stakeholders may weight the same criterion differently. Expose the weighting disagreement explicitly rather than averaging to a compromise that satisfies no one.
- **Reversible vs. irreversible decisions**: Two-way door decisions (easy to reverse) warrant less analysis than one-way doors. Classify the decision type upfront and scale the process accordingly.
- **Insufficient information to score**: When a criterion cannot be scored due to missing data, mark it as "unknown" rather than guessing. Recommend a timeboxed spike to gather the missing information.
- **Decision fatigue with too many options**: When more than 5 options exist, first eliminate clearly inferior options with a quick screen before running the full weighted analysis on the remaining candidates.

## Related Skills

- **e-adr** (eskill-office): Follow up with e-adr after this skill to record the decision outcome as an architectural decision record.
- **e-research** (eskill-intelligence): Run e-research before this skill to gather the data and evidence that inform the decision.
