---
name: knowledge-graph-build
description: "Builds a local knowledge graph from project documentation, code comments, configuration files, and README content. Use when organizing scattered project knowledge, creating searchable project context, or preparing comprehensive onboarding materials."
---

# Knowledge Graph Build

This skill constructs a structured knowledge graph from all available project documentation, code comments, configuration files, and other textual knowledge sources. The graph is stored in eMCP memory for persistent querying and is summarized as a knowledge map document.

## Prerequisites

Confirm the project root directory with the user. Determine whether the user wants a full knowledge extraction or a focused extraction on a specific subsystem or topic.

## Procedure

### Step 1: Identify Knowledge Sources

Survey the project for all files that contain human-readable knowledge.

- **README files**: Search for README.md, README.rst, README.txt, and README (no extension) in the project root and subdirectories. These are the primary knowledge sources and typically contain project overview, setup instructions, and usage examples.
- **Documentation directories**: Look for directories named docs/, doc/, documentation/, wiki/, guides/, manuals/. Enumerate all files within these directories.
- **Inline code comments**: Identify files with significant comment blocks. Focus on files that contain docstrings (Python), JSDoc comments (JavaScript/TypeScript), Rustdoc comments (Rust), Javadoc comments (Java), or XML documentation comments (C#).
- **Configuration files**: Gather all configuration files that contain documentation or explanatory comments. These include .env.example, docker-compose.yml, nginx.conf, application.yml, settings.py, and similar.
- **Changelog**: Look for CHANGELOG.md, CHANGES.md, HISTORY.md, or RELEASES.md. These provide temporal context about project evolution.
- **Contributing guide**: Look for CONTRIBUTING.md, CODE_OF_CONDUCT.md, DEVELOPMENT.md. These describe development practices and conventions.
- **Architecture decision records**: Look for an adr/ or decisions/ directory containing numbered decision documents.
- **API documentation**: Look for openapi.yaml, swagger.json, api.md, or files in an api-docs/ directory.
- **Runbooks and playbooks**: Look for runbooks/, playbooks/, or operations/ directories.

Use `search_files` with patterns like `*.md`, `*.rst`, `*.txt` to find documentation files. Use `list_dir` to explore documentation directories.

Record all identified sources in a manifest with: file path, type (readme, docs, config, changelog, adr, api-spec, runbook), and estimated size.

### Step 2: Read Documentation Files

Systematically read each identified documentation file using the eMCP filesystem server.

- Use `read_text` for each documentation file.
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

For markdown documentation files, use `markdown_headings` to extract the document hierarchy.

- Build a heading tree for each document showing the nesting structure (h1, h2, h3, etc.).
- Use the heading structure to understand how concepts are organized within documents.
- Identify sections that describe the same concept across different documents (e.g., "Authentication" section in both README and API docs).
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

### Step 6: Create Entities in Memory

Use `create_entities` in the eMCP memory server to persist each concept as a graph node.

Entity types and their attributes:

- **component**: name, description, layer (if known), status (active, deprecated, planned).
- **api_endpoint**: name, method (GET, POST, etc.), path, description, authentication required.
- **config_option**: name, type, default value, description, required (yes/no).
- **data_model**: name, description, fields summary, storage location.
- **process**: name, description, triggers, steps summary.
- **external_dependency**: name, type (service, library, database), purpose, documentation URL.
- **decision**: name, status (accepted, proposed, deprecated), date, summary.
- **term**: name, definition, related concepts.
- **document**: name, path, type, summary.

Create entities in batches grouped by type. Use consistent naming conventions: lowercase with hyphens for entity names (e.g., "user-authentication", "database-migration-process").

### Step 7: Add Observations to Entities

Use `add_observations` to attach detailed information to each entity.

For each entity, add observations covering:

- **Definition**: The most complete definition or description found across all sources.
- **Source attribution**: Which documentation file(s) describe this entity, with section references.
- **Code references**: Relevant file paths, function names, or class names from code examples.
- **Configuration**: Any configuration options related to this entity.
- **Constraints**: Limitations, requirements, or prerequisites mentioned in documentation.
- **Examples**: Brief usage examples extracted from documentation.
- **Status**: Whether the documentation indicates this is current, deprecated, experimental, or planned.

Observations should be factual and traceable to their source. Include the source file path in each observation for auditability.

### Step 8: Create Relations Between Entities

Use `create_relations` to establish connections between entities in the knowledge graph.

Relation types to create:

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

- Use `docs_index` to index each documentation file. Provide the file path and content.
- For large documentation sets, index files in batches.
- After indexing, verify the index by running a few test searches with `docs_search` using terms that should appear in the documentation.
- If the project has external documentation that is referenced but not local, use `docs_clone` to fetch and index it if the URL is available and the user approves.
- Record the total number of indexed documents and the topics covered.

### Step 10: Generate Knowledge Map Summary

Produce a comprehensive summary of the knowledge graph.

The summary document should contain:

1. **Knowledge Sources**: A table of all documentation files found with their type, location, and a brief summary.

2. **Entities by Type**: For each entity type, list all entities with their name and brief description. Include counts.
   - Components: N entities
   - API Endpoints: N entities
   - Configuration Options: N entities
   - Data Models: N entities
   - Processes: N entities
   - External Dependencies: N entities
   - Decisions: N entities
   - Terms: N entities

3. **Key Relationships**: A summary of the most important relationships in the graph. Focus on the connections that reveal system structure: which components depend on which, how data flows, what processes connect components.

4. **Coverage Analysis**: Identify gaps in documentation.
   - List components found in code (from codebase-cartography if available) that have no corresponding documentation.
   - List documentation topics that reference components not yet analyzed.
   - Rate overall documentation coverage: well-documented, partially documented, or sparsely documented.

5. **Knowledge Clusters**: Group related entities into clusters. Each cluster represents a coherent topic area (e.g., "Authentication and Authorization", "Data Pipeline", "API Layer"). These clusters help newcomers understand which concepts belong together.

6. **Recommendations**: Suggest documentation improvements based on the analysis. Identify the highest-value documentation that is missing.

## Notes

- Knowledge extraction is inherently imperfect. Mark uncertain extractions with a confidence note.
- Avoid creating duplicate entities. Before creating an entity, check if a similar entity already exists in memory using `search_nodes`.
- Entity names should be normalized: use consistent casing and naming to avoid near-duplicates like "UserAuth" and "user-authentication".
- For very large projects with extensive documentation, prioritize depth over breadth. Focus on the most referenced and most connected concepts first.
- The knowledge graph is additive. Running this skill again on the same project should update existing entities rather than create duplicates. Use `search_nodes` to find existing entities before creating new ones.
