---
name: adr-generator
description: "Creates Architecture Decision Records in standard ADR format capturing context, decision, and consequences. Use after making architectural choices, documenting technical decisions, or building decision logs. Also applies when: 'write an ADR', 'document this decision', 'architecture decision record', 'record why we chose this'."
---

# ADR Generator

This skill creates Architecture Decision Records following the standard ADR format. It captures the context, alternatives considered, decision made, and consequences of architectural choices. ADRs are numbered sequentially and stored in a project directory to maintain a decision log over time.

## Prerequisites

Determine the ADR storage location. Check for an existing ADR directory:

- `docs/adr/`
- `docs/architecture/decisions/`
- `adr/`
- `doc/adr/`

If no ADR directory exists, default to `docs/adr/` and create it. Use `filesystem` to check for existing ADR files to determine the next sequence number.

## Step 1: Gather Decision Context

Collect information about the architectural decision from the user and from the codebase.

The user should provide or confirm:

1. **Decision title**: A short, descriptive title (e.g., "Use PostgreSQL for primary data store").
2. **Context**: The forces at play, including technical constraints, business requirements, and team considerations.
3. **Decision**: The specific choice that was made.
4. **Alternatives considered**: Other options that were evaluated.

To supplement user input, gather context from the codebase:

- Use `git` to check recent commits for changes related to the decision (new dependencies, configuration changes, architectural refactoring).
- Use `filesystem` to identify relevant configuration files, dependency manifests, or infrastructure definitions that reflect the decision.
- Check for existing ADRs that this decision may supersede or relate to.

If the user provides minimal input, ask clarifying questions:

| Missing Information | Suggested Question |
|--------------------|-------------------|
| No alternatives | "What other options did you consider before choosing this approach?" |
| No context | "What problem or requirement led to this decision?" |
| No consequences | "What are the trade-offs of this choice? What becomes easier, and what becomes harder?" |
| No status | "Is this decision final, or is it still being evaluated?" |

## Step 2: Determine ADR Number and Filename

Use `filesystem` to list existing ADR files in the ADR directory.

ADR files follow the naming convention: `NNNN-title-in-kebab-case.md`

- Parse existing filenames to find the highest sequence number.
- Increment by one for the new ADR.
- Convert the decision title to kebab-case for the filename.
- Limit the filename to 60 characters (excluding the number prefix and extension).

Examples:
- `0001-use-postgresql-for-primary-data-store.md`
- `0002-adopt-event-driven-architecture.md`
- `0003-migrate-from-rest-to-grpc.md`

If this is the first ADR, start at `0001`. Also check whether an ADR template or index file exists that should be updated.

## Step 3: Research Technical Context

Use codebase analysis to enrich the ADR with concrete technical details.

**For technology selection decisions** (choosing a database, framework, library):
- Use `filesystem` to read dependency manifests and identify what is currently in use.
- Check for existing usage of the chosen technology or competing alternatives in the codebase.
- Use `git` to find when the technology was introduced (first commit adding the dependency).

**For architectural pattern decisions** (monolith vs microservices, event-driven, etc.):
- Analyze the current code structure to describe the starting state.
- Identify which components are most affected by the decision.
- Check for configuration files that reflect the pattern (message queue configs, API gateway configs, service mesh configs).

**For migration decisions** (language migration, database migration, etc.):
- Quantify the scope: number of files, lines of code, or services affected.
- Identify dependencies on the technology being migrated away from.
- Check for dual-use patterns (both old and new technology in use during migration).

Record all findings as potential content for the Context and Consequences sections.

## Step 4: Evaluate Alternatives

For each alternative the user mentions, document its strengths and weaknesses.

Structure the comparison:

| Criterion | Option A | Option B | Option C (Chosen) |
|-----------|----------|----------|-------------------|
| Performance | <assessment> | <assessment> | <assessment> |
| Complexity | <assessment> | <assessment> | <assessment> |
| Team familiarity | <assessment> | <assessment> | <assessment> |
| Ecosystem/community | <assessment> | <assessment> | <assessment> |
| Cost | <assessment> | <assessment> | <assessment> |
| Migration effort | <assessment> | <assessment> | <assessment> |

Not all criteria apply to every decision. Select the criteria most relevant to the specific decision being documented.

If the user provides only the chosen option, suggest common alternatives based on the decision type:

| Decision Type | Common Alternatives |
|--------------|-------------------|
| Database selection | PostgreSQL, MySQL, MongoDB, DynamoDB, SQLite |
| Message queue | RabbitMQ, Kafka, SQS, Redis Streams, NATS |
| API protocol | REST, GraphQL, gRPC, WebSocket |
| Frontend framework | React, Vue, Angular, Svelte, HTMX |
| Deployment model | Kubernetes, ECS, Lambda, VMs, PaaS |
| Programming language | Based on team expertise and project requirements |
| Authentication | Build custom, Auth0, Keycloak, Cognito, Firebase Auth |

## Step 5: Identify Consequences

Document both positive and negative consequences of the decision.

**Positive consequences** (what becomes easier or better):
- Performance improvements.
- Reduced operational complexity.
- Better developer experience.
- Improved scalability.
- Cost reduction.
- Alignment with team expertise.

**Negative consequences** (what becomes harder or worse):
- Learning curve for the team.
- Migration effort required.
- New operational burden.
- Vendor lock-in risk.
- Reduced flexibility in certain areas.
- Additional infrastructure requirements.

**Neutral consequences** (changes that are neither good nor bad):
- Different monitoring requirements.
- Changed deployment process.
- New testing patterns needed.

For each consequence, note whether it is short-term (during adoption) or long-term (ongoing trade-off).

## Step 6: Link Related Decisions

Use `filesystem` to read existing ADR files and identify relationships.

Check for:

- **Supersedes**: This ADR replaces a previous decision. Update the status of the superseded ADR to "Superseded by ADR-NNNN."
- **Amends**: This ADR modifies a previous decision without fully replacing it. Reference the amended ADR.
- **Related**: This ADR is connected to other decisions (e.g., a database choice that relates to a caching strategy choice). Cross-reference related ADRs.
- **Depends on**: This decision assumes a previous decision is in effect. If the dependency is reversed, this decision may need revisiting.

For each superseded ADR, use `filesystem` to read the file and update its status section. Add a note: "Superseded by [ADR-NNNN](NNNN-title.md) on YYYY-MM-DD."

Use `markdown` to format the cross-references as relative links.

## Step 7: Draft the ADR Document

Assemble the collected information into the standard ADR format.

Use `git` to determine the current date for the ADR timestamp.

```markdown
# NNNN. Title of Decision

**Date**: YYYY-MM-DD

**Status**: Accepted | Proposed | Deprecated | Superseded

**Deciders**: <names or roles if provided>

## Context

<Description of the situation, forces at play, and the problem
or opportunity that prompted this decision. Include technical
constraints, business requirements, and team considerations.>

## Decision

<The specific choice that was made. State it clearly and
unambiguously. Use active voice: "We will use X" rather than
"X was chosen.">

## Alternatives Considered

### Alternative 1: <Name>

<Description of the alternative, its strengths, and why it
was not chosen.>

### Alternative 2: <Name>

<Description of the alternative, its strengths, and why it
was not chosen.>

## Consequences

### Positive

- <Positive consequence 1>
- <Positive consequence 2>

### Negative

- <Negative consequence 1>
- <Negative consequence 2>

### Neutral

- <Neutral consequence>

## Related Decisions

- [ADR-XXXX](XXXX-title.md): <relationship description>

## References

- <Link to relevant documentation, RFC, blog post, or benchmark>
```

## Step 8: Review and Validate

Before writing the file, review the draft for quality.

Check:

1. **Completeness**: All sections have substantive content. No placeholder text remains.
2. **Clarity**: The decision is stated unambiguously. A reader unfamiliar with the context can understand what was decided and why.
3. **Objectivity**: Alternatives are described fairly, not dismissed without rationale.
4. **Actionability**: The consequences section helps future engineers understand the implications of this decision.
5. **Consistency**: The ADR follows the same format as existing ADRs in the project.
6. **Links**: All references to other ADRs use correct numbers and relative paths.
7. **Length**: The ADR is thorough but not excessive. Most ADRs should be 50-150 lines. Longer ADRs may indicate a decision that should be split.

Present the draft to the user for review before writing.

## Step 9: Write and Index the ADR

Use `filesystem` to write the ADR file to the determined path.

After writing:

1. Check for an ADR index file (`README.md`, `index.md`, or `000-index.md` in the ADR directory). If one exists, add the new ADR to it.
2. Update any superseded ADRs (from Step 6).
3. If no index exists and there are more than 5 ADRs, suggest creating one for navigability.

Index format:

```markdown
# Architecture Decision Records

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [0001](0001-use-postgresql.md) | Use PostgreSQL for primary data store | Accepted | 2025-01-15 |
| [0002](0002-adopt-event-driven.md) | Adopt event-driven architecture | Accepted | 2025-02-20 |
| [NNNN](NNNN-new-title.md) | New decision title | Accepted | YYYY-MM-DD |
```

## Step 10: Suggest Follow-Up Actions

Based on the decision documented, suggest concrete follow-up actions.

| Decision Type | Follow-Up Actions |
|--------------|-------------------|
| Technology adoption | Create migration plan, set up development environment, update CI/CD |
| Architecture change | Update architecture diagrams, schedule team briefing, identify affected services |
| Deprecation | Create deprecation timeline, add deprecation warnings, plan removal |
| Policy change | Update contributing guidelines, configure linters, update documentation |

Present the follow-up actions as a checklist the user can track.

## Edge Cases

- **Reversing a previous decision**: If the ADR documents a reversal (e.g., "Move back to REST from GraphQL"), clearly state why the original decision is being reversed. Update the original ADR's status and add a reference to the reversal.
- **Group decisions**: If a single discussion produced multiple related decisions, create separate ADRs for each distinct decision and cross-reference them rather than bundling multiple decisions into one ADR.
- **Evolving decisions**: If a decision is being refined over time (multiple amendments), consider whether it is cleaner to supersede the original with a consolidated ADR rather than chaining amendments.
- **No alternatives**: Some decisions have no realistic alternatives (e.g., regulatory requirements dictating a specific approach). Document the constraint as the context and note that alternatives were not applicable.
- **Template customization**: If the project uses a custom ADR template (MADR, Y-Statements, Nygard format), adapt the output to match the existing template rather than imposing the default format.
- **Team review process**: Some teams require ADRs to be reviewed and approved before acceptance. If the project uses pull request-based ADR review, set the initial status to "Proposed" and note that it requires review before moving to "Accepted."

## Related Skills

- **decision-framework** (eskill-intelligence): Run decision-framework before this skill to structure the decision analysis that the ADR will record.
- **knowledge-transfer-guide** (eskill-intelligence): Follow up with knowledge-transfer-guide after this skill to include ADRs in the knowledge transfer package.
