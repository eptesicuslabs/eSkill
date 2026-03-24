---
name: learning-navigator
description: "Guides systematic exploration of unfamiliar codebases with progressive depth levels and structured learning paths. Use when joining a project, studying a new framework, or navigating complex code. Also applies when: I'm new to this codebase, onboarding, help me understand this project, explore unfamiliar code."
---

# Learning Navigator

This skill provides a structured methodology for exploring and understanding unfamiliar codebases or technologies. It uses progressive depth levels to build understanding incrementally, from high-level orientation through deep internals, recording findings at each level for future reference.

## Prerequisites

Identify the learning goal with the user before starting. The approach differs based on the goal type:

- **Codebase onboarding**: Understanding an existing project to contribute to it.
- **Framework learning**: Learning a new framework or library to use it in a project.
- **System study**: Understanding a complex system's design and behavior.
- **Open-source study**: Studying an open-source project to learn patterns or evaluate adoption.

Confirm the project root directory or repository URL. Determine how much time the user has available, as this affects how many depth levels to cover.

## Procedure

### Step 1: Identify the Learning Goal

Establish clear objectives for the exploration session.

- Define the primary goal in a single sentence. For example: "Understand the authentication and authorization system in this codebase well enough to add a new permission type."
- Define the scope: the entire codebase, a specific subsystem, or a specific feature.
- Define the success criteria: what should the learner be able to do or explain after completing the exploration?
- Identify any prior knowledge: what does the learner already know about the technology stack, domain, or codebase?
- Identify specific questions the learner wants answered. These provide focus for the exploration.
- Record the goal, scope, success criteria, prior knowledge, and questions as the learning plan.

### Step 2: Start with Orientation

Get the broadest possible view of the project before diving into details.

- Use `tree` from the eMCP filesystem server on the project root with depth 2-3 to see the directory structure. This provides the "map" for subsequent exploration.
- Read the root README file if one exists. Extract:
  - What the project does (purpose and scope).
  - How to set it up (prerequisites, installation, configuration).
  - How to run it (development server, test suite, build commands).
  - Project structure overview (if documented).
  - Contributing guidelines (coding standards, PR process).
- Read the primary configuration file (package.json, pyproject.toml, Cargo.toml, go.mod, etc.). Extract:
  - Project name and version.
  - Dependencies: list them and note which ones are unfamiliar. These represent learning opportunities or complexity.
  - Scripts/tasks: these reveal the project's workflow (build, test, lint, deploy).
- Read any .editorconfig, .prettierrc, .eslintrc, or similar files to understand coding conventions.
- Produce an orientation summary: "This is a [language] project using [framework] that does [purpose]. It has [N] top-level directories organized as [structure]. Key dependencies include [list]."

### Step 3: Identify Entry Points

Find the files where understanding should begin.

- **Main/index files**: Locate the application entry point. In web applications, this is often main.ts, index.ts, app.py, main.rs, or Main.java. Read this file to understand how the application bootstraps.
- **Route definitions**: For web applications, find where routes or endpoints are defined. These map URLs to handlers and reveal the application's public interface. Look in routes/, controllers/, or the main application file.
- **Test files**: Tests are underappreciated as learning resources. They demonstrate:
  - How components are instantiated and configured.
  - What inputs are valid and invalid.
  - What behavior is expected (tests as specifications).
  - Which edge cases the developers considered important.
  - Look for test directories: test/, tests/, __tests__/, spec/, and files matching *.test.*, *.spec.*.
- **Example files**: Look for examples/, demo/, or sample/ directories. These provide usage patterns.
- **Type definitions**: In typed languages, type definition files (*.d.ts, types.py, types.rs) reveal the data model without implementation noise.
- Rank entry points by their learning value: start with the file that provides the broadest understanding of the system.

### Step 4: Progressive Depth Exploration

Explore the codebase in layers of increasing depth. Each level builds on the previous one.

**Level 1: Directory Structure and File Organization (estimated 10 minutes)**

- Map each top-level directory to its purpose. Use naming conventions as guides:
  - src/ or lib/: source code.
  - test/ or tests/: test code.
  - docs/: documentation.
  - config/ or conf/: configuration.
  - scripts/: build and utility scripts.
  - public/ or static/: static assets.
  - migrations/: database migrations.
- Count files per directory to understand where the bulk of the code lives.
- Identify generated vs authored code (dist/, build/, node_modules/, vendor/).
- Record the directory map with purposes.
- Questions to answer at this level: Where does the code live? How is it organized? What is the rough size of each area?

**Level 2: Entry Points and Public API (estimated 20 minutes)**

- Read the main entry point file identified in Step 3. Trace the initialization sequence:
  - What is configured or loaded first?
  - What services or components are created?
  - What is the startup order?
- Read route or endpoint definitions. For each endpoint, note:
  - The URL pattern or event trigger.
  - The handler function or controller.
  - Any middleware applied.
- If it is a library, read the main export file (index.ts, __init__.py, lib.rs). Note what is publicly exposed.
- Read type definitions for the public API: request/response types, configuration types, return types.
- Record the public API surface: what can external consumers or users do with this system?
- Questions to answer at this level: What does the system expose? How do users or clients interact with it? What is the initialization flow?

**Level 3: Core Business Logic and Data Models (estimated 30 minutes)**

- Identify the core domain logic. This is typically in services/, domain/, core/, or the most-imported internal modules.
- Read the data models: database models, entity definitions, schema files. These reveal what the system is "about."
- For each core service or use case, read the implementation to understand:
  - What inputs does it accept?
  - What processing does it perform?
  - What data does it read or write?
  - What other services does it call?
  - What errors can it produce?
- Trace one complete user-facing flow from entry point to data store and back. This reveals how the layers connect. For a web application, follow a single HTTP request through the full stack.
- Read the database migration files (if they exist) in chronological order to understand how the data model evolved.
- Record the core domain: key entities, key operations, and the primary data flow.
- Questions to answer at this level: What does the system actually do? What data does it manage? How does a request flow through the system?

**Level 4: Infrastructure, Configuration, and Deployment (estimated 20 minutes)**

- Read configuration files and configuration loading code. Understand:
  - What configuration options exist.
  - How defaults are set.
  - How environment-specific configuration is managed (dev, staging, production).
- Read deployment configuration: Dockerfiles, docker-compose.yml, Kubernetes manifests, CI/CD pipelines (.github/workflows/, .gitlab-ci.yml, Jenkinsfile).
- Understand the deployment model: how is the application packaged, deployed, and run in production?
- Read infrastructure code if present: Terraform, CloudFormation, Pulumi files.
- Identify external service dependencies: databases, message queues, cache servers, third-party APIs.
- Record the infrastructure context: how the system is built, deployed, and operated.
- Questions to answer at this level: How is the system deployed? What external services does it depend on? How is it configured for different environments?

**Level 5: Edge Cases, Error Handling, and Advanced Features (as needed)**

- Read error handling code: global error handlers, custom error types, retry logic, circuit breakers.
- Read middleware: authentication, authorization, rate limiting, request validation, logging.
- Read advanced features that are not part of the core flow: background jobs, scheduled tasks, webhooks, event handlers.
- Study the test suite in more detail:
  - What scenarios are tested?
  - What edge cases are covered?
  - Are there integration tests that reveal system boundaries?
  - Are there performance tests that reveal scalability concerns?
- Read any monitoring or observability code: metrics, tracing, health checks.
- Record advanced findings: how the system handles failures, edge cases, and operational concerns.
- Questions to answer at this level: How does the system handle failure? What advanced behaviors exist beyond the happy path?

### Step 5: Use Appropriate Tools at Each Level

Select the right eMCP tools for the current exploration depth.

- **Level 1 (structure)**: Use filesystem tools (`tree`, `list_dir`) to map the directory structure. Use `search_files` to find specific file types.
- **Level 2 (API surface)**: Use filesystem `read_text` to read entry points and route files. Use `lsp_symbols` to extract exported symbols without reading entire files.
- **Level 3 (core logic)**: Use `ast_search` to trace function calls and data flow. Use `lsp_symbols` to understand class hierarchies and type definitions. Use filesystem `read_text` for detailed code reading.
- **Level 4 (infrastructure)**: Use filesystem `read_text` for configuration files. Use `data_file_read` for structured data files (YAML, JSON, TOML).
- **Level 5 (advanced)**: Use `ast_search` to find error handling patterns (try/catch blocks, Result handling). Use `search_files` to find TODO/FIXME comments. Use `git_log` to understand the history of specific files.

### Step 6: Record Findings in Memory

Persist discoveries in the eMCP memory graph as the exploration progresses.

- After each depth level, create entities for newly discovered components, services, and concepts using `create_entities`.
- Add observations using `add_observations` with what was learned at each level. Include the exploration level for context (e.g., "Level 2: This module exports three public functions for user management.").
- Create relations using `create_relations` as dependencies and connections are discovered.
- Use consistent entity naming across levels so that deeper exploration enriches existing entities rather than creating duplicates.
- Before creating a new entity, use `search_nodes` to check if a similar entity already exists from a previous session or skill run.

### Step 7: Summarize Each Level

After completing each exploration level, produce a level summary.

The summary should contain:

- **What was explored**: Files read, tools used, areas covered.
- **Key insights**: The most important things learned at this level.
- **Mental model update**: How does this level's information change or refine the understanding from previous levels?
- **Questions answered**: Which of the initial questions (from Step 1) have been answered?
- **New questions**: What new questions arose during this level's exploration? These feed into the next level.
- **Confidence assessment**: How confident is the understanding? What remains uncertain?

Present the summary to the user before proceeding to the next level. The user may want to adjust focus, skip a level, or dive deeper into a specific area.

### Step 8: Generate Learning Journal

Produce a comprehensive learning journal documenting the full exploration.

The journal should include:

1. **Learning Goal**: The original objective and scope.

2. **Orientation Summary**: Project type, technology stack, and high-level purpose.

3. **Exploration Path**: What was explored at each level, in order. This serves as a "guided tour" that another developer could follow.

4. **Key Insights**: The most important discoveries, organized by topic:
   - Architecture and structure.
   - Core concepts and domain model.
   - Design patterns and conventions.
   - Notable implementation choices.

5. **Answered Questions**: The questions from Step 1 with their answers.

6. **Remaining Questions**: Questions that were not fully answered, with notes on where to look for answers.

7. **Recommended Reading Order**: For someone new to this codebase, what files should be read in what order to build understanding efficiently? List 10-15 files with a one-line description of what each teaches.

8. **Gotchas and Surprises**: Anything unexpected or non-obvious discovered during exploration. These are especially valuable for onboarding: they save time by flagging things that might confuse a newcomer.

9. **Suggested Next Steps**: What to explore next based on the learning goal. If the goal was onboarding, suggest a first task. If the goal was framework learning, suggest a practice exercise.

## Reading Patterns

These are effective strategies for understanding code. Apply them during exploration.

**Follow the Data Flow**: Start with where data enters the system (API endpoint, message consumer, CLI command) and trace it through processing, storage, and response. This reveals the system's purpose and structure.

**Follow the Request Lifecycle**: For web applications, trace a single request from receipt through routing, middleware, handler, service, data access, and response. This reveals the layer structure and cross-cutting concerns.

**Read Tests as Specifications**: Tests describe intended behavior. Read test names as a specification: "it should return 401 when token is expired" tells you about the authentication behavior without reading the implementation. Test setup code shows how components are configured and composed.

**Read Interfaces Before Implementations**: In typed codebases, read the interfaces, traits, or abstract classes first. These define the contracts between components. Then read specific implementations when you need to understand behavior.

**Read Chronologically**: For understanding why something is the way it is, use `git_log` on specific files to see how they evolved. The commit messages and diffs reveal the reasoning behind the current design.

**Read the Exceptions**: Error handling code reveals what can go wrong. Custom error types catalog the failure modes. Recovery logic reveals operational assumptions.

## Notes

- Adjust the time estimates for each level based on project size and complexity. A 10-file project does not need 20 minutes for Level 2. A 10,000-file project may need more time at Level 1.
- Not every project warrants all five levels. For a quick orientation, Levels 1 and 2 may suffice. For contributing to a specific feature, focus Levels 3-5 on the relevant subsystem.
- If the project has excellent documentation, leverage it. Read the docs before reading the code. If documentation is sparse, the code and tests are the documentation.
- Resist the urge to understand everything. Focus on understanding enough to achieve the learning goal. Complete understanding of a large codebase is neither necessary nor practical.
- Take notes continuously. Insights that seem obvious during exploration are easily forgotten. The learning journal serves as persistent memory.
- When encountering unfamiliar technologies or patterns, note them for separate study rather than derailing the current exploration. The research-workflow skill can be used for deep dives into specific technologies.

## Related Skills

- **codebase-cartography** (eskill-intelligence): Run codebase-cartography before this skill to map the codebase structure that learning paths will traverse.
- **knowledge-graph-build** (eskill-intelligence): Run knowledge-graph-build before this skill to provide the concept relationships that inform learning sequences.
