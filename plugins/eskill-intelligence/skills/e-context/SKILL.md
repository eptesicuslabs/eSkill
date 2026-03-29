---
name: e-context
description: "Exports project context from memory into a portable markdown document for handoffs or onboarding. Use when ending a session, transferring work to another developer, or creating a project brief. Also applies when: save context for later, hand off to another developer, export project knowledge, create handoff document."
---

# Context Export

This skill extracts accumulated project knowledge from the eMCP docs index and reasoning chains, combined with recent activity, then formats it into a self-contained markdown document that can be used for session handoffs, developer onboarding, or project status summaries. The exported document should enable someone with no prior context to understand the current project state.

## Prerequisites

This skill is most effective when used after other eskill-intelligence skills have populated the docs index and reasoning chains with project knowledge. It can also work with sparse indexed content, producing a thinner but still useful summary. Confirm with the user what the intended use of the export is (session handoff, onboarding, status report) so the emphasis can be adjusted accordingly.

## Procedure

### Step 1: Query Indexed Knowledge

Retrieve the full knowledge state from the eMCP docs and reasoning servers.

- Call `docs_list_libraries` to get an overview of all indexed documentation libraries.
- Use `docs_search` with broad queries to survey what knowledge is available across these categories:
  - Architecture topics: project overview, modules, layers, components, patterns.
  - Knowledge topics: terms, API endpoints, configuration options, data models, processes, external dependencies.
  - Decision topics: decisions, options, research findings.
  - Finding topics: findings, sources.
- Use `think_replay` to review existing reasoning chains and their observations.
- If the docs index is empty and no reasoning chains exist, inform the user and suggest running e-carto or e-graph first. Proceed with what is available, supplementing with direct filesystem analysis.
- Record the knowledge statistics: total indexed libraries, topics covered, reasoning chains available.

### Step 2: Search for Topic-Relevant Content

If the export is focused on a specific topic, narrow the scope.

- Use `docs_search` to find indexed content related to the export topic. For example, if the user wants context about the authentication system, search for "auth", "authentication", "authorization", "login", "session", "JWT", "token".
- If the export is a general project overview, skip targeted search and include all indexed content.
- For each search result, record the topic name, type, and relevance to the export topic.
- Sort results by relevance. Topics referenced across multiple documents or reasoning chains are generally more important to include.
- Identify the core topics (high relevance, frequently referenced) that must be in the export and peripheral topics (lower relevance) that can be summarized briefly or omitted.

### Step 3: Expand Key Topics

Retrieve detailed information for each topic to be included in the export.

- Use `think_replay` to get full reasoning chain details including all observations and relationship steps for core topics.
- Use `docs_search` with specific queries to retrieve indexed documentation content for each core topic.
- For each topic, extract:
  - All observations: definitions, descriptions, source attributions, code references, constraints, examples, status.
  - All relationships: what depends on this topic, what it depends on, how it connects to other topics.
- Organize the expanded information by topic type. Group all components together, all decisions together, and so forth.
- For peripheral topics, extract only the name and primary description.
- Note the total volume of information extracted. If it is very large, plan to summarize rather than include everything verbatim.

### Step 4: Organize by Category

Structure the extracted knowledge into logical sections.

Organize entities into the following categories:

**Architecture**:
- Project overview: language, framework, build system, architectural pattern.
- Module structure: major modules, their purposes, and their relationships.
- Layer organization: presentation, business logic, data access, infrastructure.
- Key abstractions: important classes, interfaces, types.

**Decisions**:
- Accepted decisions: active ADRs and their consequences.
- Proposed decisions: decisions under consideration.
- Deprecated decisions: decisions that have been superseded (include for historical context).

**Components**:
- Major components with their responsibilities and interfaces.
- Component dependencies and communication patterns.
- Component status: active, deprecated, experimental.

**APIs**:
- External APIs exposed by the project.
- Internal APIs between components.
- Third-party APIs consumed by the project.

**Open Questions**:
- Unresolved technical questions.
- Known unknowns identified during previous analysis.
- Areas flagged for further investigation.

Adjust the emphasis based on the export purpose:
- **Session handoff**: Emphasize recent work, open questions, and next steps.
- **Onboarding**: Emphasize architecture, key components, and development setup.
- **Status report**: Emphasize decisions, progress, and blockers.

### Step 5: Summarize Entity Observations

Transform raw observations into readable prose for each entity.

- For each core entity, write a paragraph that synthesizes its observations into a coherent description. Do not simply list observations; weave them into a narrative.
- Include source attributions where available: "According to the API documentation, the authentication endpoint requires..."
- For numerical or structured data (configuration options, API parameters), use tables or lists rather than prose.
- For code references, include file paths but not full code blocks unless they are essential for understanding. The reader can look up the code.
- For decisions, include the context, the chosen option, and the key reasons in a condensed form. Reference the full ADR if it exists.
- For peripheral entities, write a single sentence summary.
- Aim for clarity and density: every sentence should convey useful information.

### Step 6: Generate Relationship Section

Document the important relationships between entities.

- Identify the most important relationships: dependencies between components, data flows between modules, decisions that affect components.
- Present relationships in a structured format:
  - Dependency lists: "Component A depends on: Component B, Component C, External Service X."
  - Data flow descriptions: "User requests flow from the API gateway through the auth middleware to the request handler, which queries the database via the repository layer."
  - Decision impact maps: "Decision ADR-003 (adopt PostgreSQL) affects: user-service, order-service, analytics-pipeline."
- For complex relationship networks, consider using an indented hierarchy or a textual adjacency list.
- Highlight any concerning relationships: circular dependencies, overly coupled components, single points of failure.

### Step 7: Include Recent Git Activity

Add work-in-progress context from recent version control activity.

- Use `git_log` to retrieve the last 20-30 commits (or commits from the last week, whichever is more appropriate).
- Summarize recent activity:
  - What areas of the codebase have been actively modified?
  - What features or fixes are in progress?
  - Are there any incomplete branches or work-in-progress commits?
- Group commits by topic or feature if possible (look for common prefixes, issue numbers, or affected directories).
- If the project uses conventional commits, leverage the commit types (feat, fix, refactor, docs, chore) to categorize activity.
- Include the current branch name and its relationship to the main branch.
- Note any uncommitted changes in the working directory (from git status) as active work.

### Step 8: Include Open Tasks and Known Issues

Document any tracked tasks or issues that provide context about the project state.

- Check for task tracking files: TODO.md, TASKS.md, or similar.
- Search for TODO, FIXME, HACK, and XXX comments in the codebase using filesystem search. Count occurrences and list the most significant ones.
- If the project uses issue references in commits (e.g., #123), note recently referenced issues.
- If the docs index or reasoning chains contain entries related to tasks or issues, include them.
- Organize into: active tasks (in progress), blocked tasks (waiting on something), and backlog items (planned but not started).

### Step 9: Format as Self-Contained Markdown

Assemble all gathered information into a single, well-structured markdown document.

The document should follow this structure:

```markdown
# Project Context: [Project Name]

Generated: [date]
Purpose: [session handoff | onboarding | status report]

## Overview

[2-3 paragraph project summary: what it is, what it does, key technologies,
current state of development.]

## Architecture

### System Structure
[Module map, layer organization, architectural pattern.]

### Key Components
[Major components with their responsibilities.]

### Dependencies
[Important internal and external dependencies.]

## Key Decisions

[Summary of active architectural decisions with their rationale.]

## Current State

### Recent Activity
[Summary of recent git activity and what areas are being worked on.]

### Work in Progress
[Active tasks, uncommitted changes, in-progress features.]

### Known Issues
[Significant TODOs, FIXMEs, or tracked issues.]

## Open Questions

[Unresolved technical questions and areas needing further investigation.]

## Quick Reference

### Entry Points
[Key files to start reading.]

### Configuration
[How to configure and run the project.]

### Key Contacts
[Team members or owners of specific areas, if known.]
```

- Adjust section depth and detail based on the export purpose and the amount of information available.
- Omit sections that have no content rather than including empty sections.
- Keep the total document length reasonable: aim for 2-5 pages for a session handoff, 5-10 pages for onboarding, 1-3 pages for a status report.

### Step 10: Validate Completeness

Review the exported document for completeness and usability.

- Read through the document from the perspective of the intended audience. Would someone with no prior context understand the project state?
- Check for:
  - Missing context: are there references to concepts that are not explained?
  - Stale information: are there dates or version numbers that seem outdated?
  - Broken references: are there file paths or links that may not resolve?
  - Jargon: are there project-specific terms that need definition?
- If gaps are identified, attempt to fill them from the docs index, reasoning chains, or filesystem.
- Add a "Limitations" note at the end if significant information is missing or uncertain.
- Present the final document to the user and ask if any sections need expansion or if additional topics should be covered.

## Notes

- The export is a snapshot in time. Include the generation date prominently so readers know the currency of the information.
- For session handoffs, focus on "what I was doing, what I learned, and what comes next." The reader needs to continue the work, not understand the full architecture.
- For onboarding, focus on "how the system works, how to set it up, and where to start reading." The reader needs to become productive, not make decisions.
- For status reports, focus on "what was decided, what changed, and what is blocked." The reader needs to understand progress and risks.
- If the docs index and reasoning chains are sparse, supplement with direct filesystem and git analysis. A useful context export can be produced even without prior knowledge graph construction, though it will be less rich.
- Avoid including sensitive information (credentials, internal URLs, personal data) in the export. Scan the output for common patterns (.env values, API keys, passwords) before finalizing.

## Edge Cases

- **Empty or very short sessions**: A session with no code changes and few decisions still has value if it captures research or investigation results. Export the learning even if no artifacts were produced.
- **Sensitive information in context**: Session context may reference credentials, internal URLs, or personal data. Scan the exported document for common sensitive patterns before finalizing.
- **Multiple projects touched in one session**: If the session worked across multiple repositories, generate separate context documents per project rather than one mixed document.
- **Stale context from long-running sessions**: Sessions spanning multiple days accumulate context that may become outdated. Include timestamps per section so readers can judge currency.
- **Context export for non-technical audience**: When the target audience is a product manager or stakeholder, adjust terminology and omit implementation details in favor of decisions and outcomes.

## Related Skills

- **e-recap** (eskill-meta): Run e-recap before this skill to summarize the session context that will be exported.
- **e-transfer** (eskill-intelligence): Follow up with e-transfer after this skill to build a comprehensive handoff package from exported context.
