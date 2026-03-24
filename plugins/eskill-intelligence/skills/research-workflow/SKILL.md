---
name: research-workflow
description: "Conducts structured technical research by gathering sources, analyzing findings, and producing cited summaries. Use when evaluating libraries, comparing approaches, or investigating an unfamiliar API. Also applies when: research this topic, compare these options, what library should I use, evaluate alternatives."
---

# Research Workflow

This skill provides a structured methodology for conducting technical research. It guides the process from question formulation through source gathering, analysis, and synthesis, producing a research report with citations and actionable recommendations.

## Prerequisites

The user should provide a clear research topic or question. If the question is vague, begin by refining it into a specific, answerable form before proceeding.

## Procedure

### Step 1: Define the Research Question

Formulate a precise research question that guides the investigation.

- Work with the user to refine a broad topic into one or more specific questions. For example, transform "What database should we use?" into "Which database engine best supports our requirements for time-series data with sub-second query latency at 10M rows per day ingestion rate?"
- Identify the type of research needed:
  - **Evaluation**: Comparing options to make a choice (library selection, tool comparison).
  - **Investigation**: Understanding how something works (API behavior, framework internals).
  - **Feasibility**: Determining whether something is possible and practical (can we do X with Y?).
  - **Survey**: Gathering a broad understanding of a topic area (state of the art, best practices).
- Define the scope: what is in scope and what is explicitly out of scope.
- Define the success criteria: what information would constitute a complete answer?
- Record the research question, type, scope, and success criteria before proceeding.

### Step 2: Search for Relevant Documentation

Identify and access documentation sources relevant to the research question.

- **Local documentation**: Use `docs_search` to search any previously indexed project documentation that may be relevant.
- **Web documentation**: Use `fetch_url` to retrieve official documentation pages for the technologies being researched. Target the most authoritative sources:
  - Official project websites and documentation portals.
  - GitHub repository READMEs and wiki pages.
  - Official API references and specification documents.
  - Published benchmarks and comparison articles from reputable sources.
- **Search for sources**: If the relevant URLs are not known, use web search to identify authoritative documentation pages. Prefer primary sources (official docs, RFCs, specifications) over secondary sources (blog posts, tutorials).
- For each source accessed, record:
  - URL or file path.
  - Title and author/publisher.
  - Date of publication or last update (to assess currency).
  - Relevance to the research question (high, medium, low).
  - A brief note on what information it provides.

### Step 3: Clone and Index Library Documentation

For research involving specific libraries or frameworks, set up local searchable documentation.

- Use `docs_clone` to clone documentation repositories for the libraries being evaluated. This enables efficient full-text search across their documentation.
- After cloning, use `docs_search` to run targeted queries against the indexed documentation.
- Common documentation sources to clone:
  - GitHub repository docs/ directories.
  - Official documentation sites (many are open source and clonable).
  - API reference generated documentation.
- For each cloned documentation set, verify the index by searching for known topics.
- If documentation cannot be cloned (private, unavailable), fall back to `fetch_url` for individual pages.

### Step 4: Extract Key Information

Process each source to extract the information relevant to the research question.

- Use `extract_text` to pull clean text content from fetched web pages when needed.
- For each source, extract:
  - **Facts**: Concrete, verifiable information (version numbers, supported features, performance numbers, compatibility lists).
  - **Claims**: Statements made by the source that may need verification (performance claims, ease-of-use assertions).
  - **Examples**: Code examples, configuration examples, or usage patterns that demonstrate capabilities.
  - **Limitations**: Documented limitations, known issues, unsupported features, or caveats.
  - **Requirements**: Dependencies, system requirements, minimum versions, or prerequisites.
- Organize extracted information by topic rather than by source. Group all performance-related findings together, all compatibility findings together, and so forth.
- For numerical data (benchmarks, sizes, limits), record the exact figures with their measurement conditions and source.

### Step 5: Structure the Analysis with Reasoning

Use the eMCP reasoning server to organize and analyze findings systematically.

- Call `think_start` with the research question as the goal. This begins a structured reasoning chain.
- For each major finding or topic area, call `think_step` with type "thought" to record the finding and its implications:
  - What does this finding mean for our question?
  - How does it interact with other findings?
  - What weight should it carry in the analysis?
- Use `think_branch` to explore different perspectives on contentious or ambiguous findings:
  - Branch 1: Optimistic interpretation (best case scenario).
  - Branch 2: Pessimistic interpretation (worst case scenario).
  - Branch 3: Most likely interpretation based on evidence.
- For evaluation-type research, create a branch for each option being evaluated. Within each branch, step through the evaluation criteria.
- Document any assumptions made during analysis. These should be explicitly stated in the final report.

### Step 6: Cross-Reference Findings

Verify findings by comparing information across sources.

- For each key fact or claim, check whether multiple sources corroborate it.
  - **Corroborated**: Multiple independent sources agree. High confidence.
  - **Single source**: Only one source mentions this. Medium confidence. Note the source's authority.
  - **Contradicted**: Sources disagree. Flag the contradiction and investigate further if possible.
- Pay special attention to:
  - Version-specific information: a finding may be true for version X but not version Y. Record the applicable version.
  - Date-sensitive information: a limitation reported two years ago may have been resolved. Check for more recent information.
  - Context-dependent information: performance benchmarks depend heavily on hardware, configuration, and workload. Note the conditions.
- When sources contradict each other, attempt to determine the reason:
  - Different versions of the software.
  - Different configurations or environments.
  - One source is outdated.
  - Different measurement methodologies.
- Record the confidence level for each key finding: high (multiple corroborating sources), medium (single authoritative source), low (uncorroborated or contradicted).

### Step 7: Synthesize Findings

Combine all findings into a coherent analysis that answers the research question.

- Organize findings into themes or categories that align with the research question.
- For evaluation research, construct a comparison matrix:
  - Rows: evaluation criteria.
  - Columns: options being compared.
  - Cells: how each option rates on each criterion, with supporting evidence.
- For investigation research, construct an explanation:
  - What is the mechanism or behavior?
  - What are the edge cases or exceptions?
  - What are the practical implications?
- For feasibility research, construct an assessment:
  - Is it possible? What are the requirements?
  - Is it practical? What is the effort and risk?
  - What are the alternatives if it is not feasible?
- For survey research, construct a landscape overview:
  - What are the main approaches or solutions?
  - How do they differ?
  - What are the trends?
- Identify trade-offs explicitly. Most technical decisions involve trade-offs; make these visible.
- Formulate a recommendation based on the analysis. State the recommendation clearly and explain the reasoning.

### Step 8: Store Findings in Memory

Persist the research findings in the eMCP memory graph for future reference.

- Create entities using `create_entities`:
  - Entity type "research": the research question itself.
  - Entity type "option": each option evaluated (for evaluation research).
  - Entity type "finding": each key finding.
  - Entity type "source": each source consulted.
- Add observations using `add_observations`:
  - To the research entity: the conclusion and recommendation.
  - To option entities: pros, cons, scores on criteria.
  - To finding entities: the evidence and confidence level.
  - To source entities: URL, date, authority, relevance.
- Create relations using `create_relations`:
  - "investigates": research entity investigates options or topics.
  - "supports": finding supports or contradicts an option.
  - "sourced_from": finding is sourced from a specific source.
  - "recommends": research entity recommends a specific option.

### Step 9: Generate Research Report

Produce a structured research report with citations.

The report should include:

1. **Research Question**: The specific question investigated, with scope and context.

2. **Executive Summary**: A 2-3 paragraph summary of the findings and recommendation for readers who will not read the full report.

3. **Sources Consulted**: A numbered list of all sources with title, URL/path, date, and relevance. These numbers serve as citation references throughout the report.

4. **Findings**: The detailed findings organized by topic. Each finding should cite its source(s) using the numbered reference. Include:
   - Key facts and their evidence.
   - Contradictions found and their resolution.
   - Confidence levels for important claims.

5. **Analysis**: The synthesis of findings into an answer to the research question. For evaluations, include the comparison matrix. For investigations, include the explanation. For feasibility assessments, include the assessment.

6. **Trade-offs**: An explicit discussion of the trade-offs involved in the recommendation.

7. **Recommendation**: The recommended course of action with clear reasoning.

8. **Open Questions**: Questions that could not be answered during this research and may need further investigation.

9. **Appendices**: Raw data, extended comparisons, or detailed technical information that supports the analysis but is too detailed for the main report.

## Library Evaluation Checklist

When evaluating a library or tool, ensure the following are assessed:

- **License**: Is the license compatible with the project? Is it permissive (MIT, Apache 2.0) or copyleft (GPL)?
- **Maintenance activity**: When was the last release? When was the last commit? Are issues being responded to? How many open issues vs closed?
- **Documentation quality**: Is the documentation comprehensive? Are there getting-started guides, API references, and examples? Is the documentation up to date with the current version?
- **Community size**: How many GitHub stars, npm downloads, PyPI downloads, or crates.io downloads? Are there active discussion forums, Discord servers, or Stack Overflow tags?
- **Breaking change history**: How often does the library make breaking changes? Does it follow semantic versioning? Are there migration guides for major version upgrades?
- **Type support**: Does it provide TypeScript types, Python type hints, or equivalent for the project's language?
- **Bundle size or dependency weight**: How large is the library? How many transitive dependencies does it pull in?
- **Performance**: Are there published benchmarks? How does it compare to alternatives?
- **Security**: Are there known vulnerabilities? Is there a security policy? How quickly are security issues addressed?
- **Testing**: Does the library have a comprehensive test suite? What is the test coverage?

## Notes

- Time-box research to avoid diminishing returns. For most questions, 80% of the value comes from the first few authoritative sources.
- When web sources are unavailable or rate-limited, note this in the report and suggest the user follow up manually.
- Be explicit about what was not investigated. Unknown unknowns are a risk; naming the boundaries of the research helps the user understand what they still need to verify.
- For rapidly evolving topics, include the research date prominently so readers know the findings may become outdated.

## Related Skills

- **decision-framework** (eskill-intelligence): Follow up with decision-framework after this skill to structure research findings into a decision analysis.
- **tech-debt-tracker** (eskill-intelligence): Follow up with tech-debt-tracker after this skill to log technical debt items discovered during research.
