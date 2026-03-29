---
name: e-graph
description: "Builds a knowledge graph from project docs, code comments, configs, and READMEs using indexed search and structured reasoning. Use when organizing scattered project knowledge into a searchable structure or preparing onboarding context. Also applies when: index project knowledge, build a knowledge base, catalog project documentation."
---

# Knowledge Graph Build

This skill constructs a structured knowledge graph from all available project documentation, code comments, configuration files, and other textual knowledge sources. The graph is indexed in the eMCP docs server for persistent search and organized via the eMCP reasoning server for structured relationships, then summarized as a knowledge map document.

## Prerequisites

Confirm the project root directory with the user. Determine whether the user wants a full knowledge extraction or a focused extraction on a specific subsystem or topic.

## Procedure

### Step 1: Identify Knowledge Sources

Survey the project for all files that contain human-readable knowledge. Before starting, use `think_search` to find any related past reasoning chains (e.g., from previous e-carto or e-graph runs) that already contain project knowledge. Reuse existing observations rather than rediscovering what is already recorded.

- **README files**: Search for README.md, README.rst, README.txt, and README (no extension) in the project root and subdirectories. These are the primary knowledge sources and typically contain project overview, setup instructions, and usage examples.
- **Documentation directories**: Look for directories named docs/, doc/, documentation/, wiki/, guides/, manuals/. Enumerate all files within these directories.
- **Inline code comments**: Identify files with significant comment blocks. Focus on files that contain docstrings (Python), JSDoc comments (JavaScript/TypeScript), Rustdoc comments (Rust), Javadoc comments (Java), or XML documentation comments (C#).
- **Configuration files**: Gather all configuration files that contain documentation or explanatory comments. These include .env.example, docker-compose.yml, nginx.conf, application.yml, settings.py, and similar.
- **Changelog**: Look for CHANGELOG.md, CHANGES.md, HISTORY.md, or RELEASES.md. These provide temporal context about project evolution.
- **Contributing guide**: Look for CONTRIBUTING.md, CODE_OF_CONDUCT.md, DEVELOPMENT.md. These describe development practices and conventions.
- **Architecture decision records**: Look for an adr/ or decisions/ directory containing numbered decision documents.
- **API documentation**: Look for openapi.yaml, swagger.json, api.md, or files in an api-docs/ directory.
- **Runbooks and playbooks**: Look for runbooks/, playbooks/, or operations/ directories.

Use `fs_search` with patterns like `*.md`, `*.rst`, `*.txt` to find documentation files. Use `fs_list` to explore documentation directories.

Record all identified sources in a manifest with: file path, type (readme, docs, config, changelog, adr, api-spec, runbook), and estimated size.

### Step 2: Read Documentation Files

Systematically read each identified documentation file using the eMCP filesystem server.

- Use `fs_read` for each documentation file.
- For large files (over 500 lines), read in sections to avoid overwhelming context. Start with the first 100 lines to get the overview, then read subsequent sections as needed.
- For binary documentation (PDF, Word), note their existence but skip content extraction. Record them as entities with type "binary-doc" and a note that manual review is needed.
- Prioritize reading order:
  1. Root README (highest priority, project overview).
  2. Contributing guide (development practices).
  3. Architecture documents and ADRs.
  4. API documentation.
  5. Subdirectory READMEs.
  6. Other documentation files.
  7. Changelog (scan recent entries, not full history).

For each file read, extract a brief summary (2-3 sentences) of what the file covers.

### Step 3: Extract Key Concepts

From the documentation content, identify distinct concepts that should become nodes in the knowledge graph.

Categories of concepts to extract:

- **Components**: Named software components, services, modules, or subsystems mentioned in documentation. Look for headings, bold text, or capitalized terms that refer to system parts.
- **Technical terms**: Domain-specific vocabulary that someone new to the project would need to understand. Look for terms that are defined or explained in the documentation.
- **API endpoints**: REST endpoints, GraphQL queries/mutations, RPC methods, or CLI commands documented in the project.
- **Configuration options**: Environment variables, configuration keys, feature flags, or settings that affect system behavior.
- **Data models**: Entities, schemas, database tables, or data structures described in documentation.
- **Processes**: Workflows, pipelines, lifecycles, or procedures described in documentation (build process, deployment process, data migration process).
- **External dependencies**: Third-party services, APIs, databases, or tools that the project depends on.
- **Decisions**: Architectural or technical decisions documented in ADRs or elsewhere.

For each concept, record: name, category, source file, and a brief definition or description extracted from the documentation.

### Step 4: Parse Markdown Structure

For markdown documentation files, use `markdown_headings` to extract the document hierarchy and `markdown_read_section` to pull content under specific headings without reading entire files.

- Build a heading tree for each document showing the nesting structure (h1, h2, h3, etc.).
- Use `markdown_read_section` to extract content under specific headings of interest (e.g., "Architecture", "API", "Configuration") for targeted concept extraction rather than reading full documents.
- Use the heading structure to understand how concepts are organized within documents.
- Identify sections that describe the same concept across different documents (e.g., "Authentication" section in both README and API docs). Use `markdown_read_section` to compare the content of matching sections across documents directly.
- Map headings to concepts: each heading typically corresponds to a concept or a facet of a concept.
- Note the depth of coverage for each concept: a top-level heading with multiple subsections indicates a well-documented concept; a brief mention in a list indicates a concept with minimal documentation.

### Step 5: Extract Code References

Use `markdown_code_blocks` to find code examples and references within documentation.

- For each code block, identify:
  - The language (from the code fence language tag).
  - Whether it is an example, a configuration snippet, or a command.
  - Which concept it illustrates.
  - Whether the code references actual project files or is standalone example code.
- Link code examples to their corresponding concepts. A code block under an "Authentication" heading is a code reference for the authentication concept.
- For inline code references (backtick-wrapped text), identify whether they refer to file paths, function names, class names, environment variables, or commands.
- Record code references as observations on their parent concept entity.

### Step 6: Build Reasoning Chains for Concept Relationships

Use the eMCP reasoning server to organize concepts and their relationships into structured reasoning chains.

- Call `think_start` to create a reasoning chain for the knowledge graph, with the project name and scope as the goal.
- For each concept category, call `think_step` with type="observation" to record the concept and its attributes:
  - **component**: name, description, layer (if known), status (active, deprecated, planned).
  - **api_endpoint**: name, method (GET, POST, etc.), path, description, authentication required.
  - **config_option**: name, type, default value, description, required (yes/no).
  - **data_model**: name, description, fields summary, storage location.
  - **process**: name, description, triggers, steps summary.
  - **external_dependency**: name, type (service, library, database), purpose, documentation URL.
  - **decision**: name, status (accepted, proposed, deprecated), date, summary.
  - **term**: name, definition, related concepts.
  - **document**: name, path, type, summary.
- Use consistent naming conventions: lowercase with hyphens for concept names (e.g., "user-authentication", "database-migration-process").

### Step 7: Record Detailed Observations

For each concept, call `think_step` with type="observation" to attach detailed information.

For each concept, record observations covering:

- **Definition**: The most complete definition or description found across all sources.
- **Source attribution**: Which documentation file(s) describe this concept, with section references.
- **Code references**: Relevant file paths, function names, or class names from code examples.
- **Configuration**: Any configuration options related to this concept.
- **Constraints**: Limitations, requirements, or prerequisites mentioned in documentation.
- **Examples**: Brief usage examples extracted from documentation.
- **Status**: Whether the documentation indicates this is current, deprecated, experimental, or planned.

Observations should be factual and traceable to their source. Include the source file path in each observation for auditability.

### Step 8: Record Relations via Reasoning Steps

Use `think_step` with type="thought" and evidenceFor/evidenceAgainst links to establish connections between concepts in the reasoning chain.

Relation types to record:

- **depends_on**: Component A depends on Component B, or Component depends on External Dependency.
- **implements**: Component implements a Process or provides an API Endpoint.
- **configures**: Config Option configures a Component.
- **documents**: Document describes a Component, Process, or Decision.
- **contains**: Component contains sub-components or Data Models.
- **triggers**: Process A triggers Process B, or Event triggers Process.
- **replaces**: Decision or Component replaces a deprecated predecessor.
- **relates_to**: General association between concepts that share a context.
- **defines**: Document or section defines a Term.
- **exposes**: Component exposes an API Endpoint.
- **stores**: Component stores or manages a Data Model.

Derive relations from:

- Explicit mentions in documentation (e.g., "The auth service depends on the user database").
- Document structure (e.g., a subsection under a component heading describes a sub-component).
- Code references (e.g., an import statement in a code example links two components).
- Configuration (e.g., a config option that specifies a database connection string relates a component to a data store).

### Step 9: Index Documentation for Search

Use the eMCP docs server to index documentation content for full-text search capability.

- Use `docs_bootstrap` to bulk-index documentation from project dependencies (node_modules, vendor directories, or similar). This indexes library docs in a single call rather than cloning each dependency individually, and is the preferred approach when the project has installed dependencies with bundled documentation.
- Use `docs_index` to index each project-specific documentation file. Provide the file path and content.
- For large documentation sets, index files in batches.
- After indexing, verify the index by running a few test searches with `docs_search` using terms that should appear in the documentation.
- If the project has external documentation that is referenced but not local, use `docs_clone` to fetch and index it if the URL is available and the user approves.
- Record the total number of indexed documents and the topics covered.

### Step 10: Generate Knowledge Map Summary

Produce a comprehensive summary of the knowledge graph.

The summary document should contain:

1. **Knowledge Sources**: A table of all documentation files found with their type, location, and a brief summary.

2. **Concepts by Type**: For each concept type, list all concepts with their name and brief description. Include counts.
   - Components: N concepts
   - API Endpoints: N concepts
   - Configuration Options: N concepts
   - Data Models: N concepts
   - Processes: N concepts
   - External Dependencies: N concepts
   - Decisions: N concepts
   - Terms: N concepts

3. **Key Relationships**: A summary of the most important relationships in the graph. Focus on the connections that reveal system structure: which components depend on which, how data flows, what processes connect components.

4. **Coverage Analysis**: Identify gaps in documentation.
   - List components found in code (from e-carto if available) that have no corresponding documentation.
   - List documentation topics that reference components not yet analyzed.
   - Rate overall documentation coverage: well-documented, partially documented, or sparsely documented.

5. **Knowledge Clusters**: Group related concepts into clusters. Each cluster represents a coherent topic area (e.g., "Authentication and Authorization", "Data Pipeline", "API Layer"). These clusters help newcomers understand which concepts belong together.

6. **Recommendations**: Suggest documentation improvements based on the analysis. Identify the highest-value documentation that is missing.

## Notes

- Knowledge extraction is inherently imperfect. Mark uncertain extractions with a confidence note.
- Avoid duplicate concepts. Before recording a concept, use `docs_search` to check if similar content already exists in the docs index, use `think_search` to run full-text search across past reasoning chains for prior observations on the same topic, and use `think_replay` to review specific chains in detail when matches are found.
- Concept names should be normalized: use consistent casing and naming to avoid near-duplicates like "UserAuth" and "user-authentication".
- For very large projects with extensive documentation, prioritize depth over breadth. Focus on the most referenced and most connected concepts first.
- The knowledge graph is additive. Running this skill again on the same project should update existing indexed content and reasoning chains rather than create duplicates.

## Edge Cases

- **Projects with no documentation**: When README, docs/, and code comments are all absent, the knowledge graph must be built entirely from code structure and naming. Report the documentation gap as a primary finding.
- **Conflicting documentation and code**: Docs may describe behavior that the code no longer implements. Cross-reference doc claims with code reality and flag discrepancies.
- **Multiple natural languages in docs**: Projects with docs in English, Chinese, Japanese, etc. may have overlapping but non-identical content. Group by language and note where translations diverge.
- **Auto-generated documentation**: JSDoc/Sphinx-generated docs may be voluminous but shallow. Distinguish auto-generated API docs from hand-written conceptual documentation in the coverage analysis.
- **Knowledge graph growing stale**: The graph reflects the codebase at a point in time. Flag concepts whose source files have been significantly modified since the last graph build.

## Related Skills

- **e-carto** (eskill-intelligence): Run e-carto before this skill to provide the structural data that feeds into the knowledge graph.
- **e-context** (eskill-intelligence): Follow up with e-context after this skill to package the knowledge graph for sharing across sessions.
