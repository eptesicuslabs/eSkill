---
name: report-builder
description: "Compiles structured markdown reports from multiple data sources with diagrams, tables, and cross-references. Use when assembling a status report, analysis summary, or document that combines narrative with data. Also applies when: build a report, create project summary, write status update."
---

# Report Builder

This skill compiles structured reports by gathering data from multiple sources, generating
supporting diagrams and tables, and assembling everything into a well-organized markdown
document with cross-references and a table of contents.

## Prerequisites

The following eMCP tools are required:

- `spreadsheet_read` -- read data from spreadsheets for inclusion in reports
- `sql_query` -- query databases for report data
- `diagram_render` -- generate diagrams for embedding in reports
- `diagram_render_file` -- render and save diagram images
- `markdown_headings` -- validate heading structure in the report
- `markdown_links` -- validate all links and references in the report
- `filesystem_write` -- write the final report file
- `filesystem_read` -- read template files or existing report drafts

Optional tools for specific data sources:

- `git_log` -- gather commit history and contributor statistics
- `log_stats` -- analyze log files for error rates, performance metrics
- `pdf_read_text` -- extract content from PDF source documents

## Procedure

### Step 1: Define Report Structure

Work with the user to establish the report framework:

1. **Title and metadata**: Report title, author, date, version, distribution list.
2. **Purpose**: A one-sentence statement of what the report communicates.
3. **Sections**: Identify the sections needed. A standard report structure includes:
   - Executive Summary
   - Introduction / Background
   - Methodology (if applicable)
   - Findings / Results
   - Data and Analysis
   - Recommendations
   - Appendices
4. **Data sources**: For each section that requires data, identify the source:
   - Spreadsheet files (path and sheet name)
   - Database queries (database path and SQL)
   - Log files (path and metric type)
   - Git repositories (path and date range)
   - Other documents (paths)
5. **Diagrams**: Identify where diagrams are needed and what they should show.

If the user provides a minimal brief (e.g., "create a project status report"), propose
a standard structure and confirm before proceeding.

### Step 2: Gather Data from Sources

Collect data from each identified source:

**Spreadsheet data:**
1. Use `spreadsheet_read` to load the specified file and sheet.
2. Extract relevant rows and columns based on the report requirements.
3. Compute summary statistics if needed: totals, averages, min/max, counts.

**Database data:**
1. Use `sql_query` to execute the specified queries.
2. Format results as tables or extract specific values for narrative sections.
3. If multiple queries are needed, run them in sequence and label each result set.

**Log file analysis:**
1. Use `log_stats` to gather metrics: error counts, response times, throughput.
2. Summarize trends over the reporting period.

**Git history:**
1. Use `git_log` to retrieve commits in the reporting period.
2. Compute: number of commits, contributors, files changed, lines added/removed.
3. Identify key milestones (tagged releases, merge commits to main).

**Document sources:**
1. Use `pdf_read_text` or `filesystem_read` to extract relevant passages.
2. Attribute and quote source material properly.

Store all gathered data in a structured intermediate format before assembling the report.
This allows the user to verify the data before it is woven into narrative.

### Step 3: Generate Diagrams

For each diagram identified in the report plan:

1. Determine the diagram type: bar chart (as Mermaid), flow diagram, architecture diagram,
   timeline, or pie chart.
2. Generate the diagram source code in Mermaid syntax. Common patterns:

   **Status distribution (pie chart):**
   ```
   pie title Task Status
       "Complete" : 45
       "In Progress" : 30
       "Not Started" : 25
   ```

   **Timeline (Gantt chart):**
   ```
   gantt
       title Project Timeline
       dateFormat YYYY-MM-DD
       section Phase 1
       Design           :done, 2025-01-01, 2025-02-01
       Implementation   :active, 2025-02-01, 2025-04-01
       section Phase 2
       Testing          :2025-04-01, 2025-05-01
       Deployment       :2025-05-01, 2025-05-15
   ```

   **Architecture (flowchart):**
   ```
   graph TB
       Client --> API[API Gateway]
       API --> Auth[Auth Service]
       API --> Core[Core Service]
       Core --> DB[(Database)]
       Core --> Cache[(Redis Cache)]
   ```

3. Render each diagram using `diagram_render_file` to produce SVG files.
4. Save both the diagram source and the rendered image.
5. Generate a relative path for embedding in the report markdown.

### Step 4: Build Report Sections

Assemble each section of the report in markdown:

**Title block:**
```markdown
# Report Title

**Author:** Name
**Date:** YYYY-MM-DD
**Version:** 1.0
**Status:** Draft / Final
```

**Executive Summary:**
- Write 3-5 sentences summarizing the key findings and recommendations.
- This section should stand alone -- a reader who only reads this section should understand
  the main points.
- Include the single most important metric or finding.

**Findings / Results:**
- Present data as markdown tables where tabular presentation is appropriate.
- Use bullet points for lists of findings.
- Reference diagrams using markdown image syntax: `![Description](path/to/diagram.svg)`
- Include specific numbers and dates rather than vague language.

**Data and Analysis:**
- Embed data tables formatted as markdown pipe tables.
- For tables with more than 10 rows, consider summarizing in the main body and placing
  the full table in an appendix.
- Add brief analytical commentary after each table or diagram explaining what the data
  shows and why it matters.

**Recommendations:**
- Number each recommendation for easy reference.
- Tie each recommendation to a specific finding.
- Include priority and estimated effort where applicable.

**Appendices:**
- Full data tables
- Raw query results
- Diagram source code
- Methodology details

### Step 5: Generate Table of Contents

Build a table of contents from the heading structure:

1. Scan all headings in the report (## through ####).
2. Generate a linked TOC using markdown anchor syntax:
   ```markdown
   ## Table of Contents

   1. [Executive Summary](#executive-summary)
   2. [Introduction](#introduction)
   3. [Findings](#findings)
      1. [Performance Metrics](#performance-metrics)
      2. [Error Analysis](#error-analysis)
   4. [Recommendations](#recommendations)
   5. [Appendices](#appendices)
   ```
3. Use `markdown_headings` to validate that the heading structure is consistent and
   there are no skipped levels.
4. Place the TOC immediately after the title block and before the Executive Summary.

### Step 6: Add Cross-References

Link related sections and data points within the report:

1. When a finding is referenced in the recommendations, link back to the finding:
   `(see [Finding 3](#finding-3-performance-degradation))`.
2. When a summary table is derived from detailed data in an appendix, link to the
   appendix: `(full data in [Appendix A](#appendix-a-raw-data))`.
3. When a diagram illustrates a point in the narrative, reference it:
   `As shown in [Figure 1](#figure-1-system-architecture)...`.
4. Number figures and tables sequentially throughout the report for easy reference.

### Step 7: Validate Links and References

Before finalizing the report:

1. Use `markdown_links` to extract all links in the document.
2. Verify that all internal anchor links resolve to existing headings.
3. Verify that all image paths point to files that exist.
4. Verify that any external URLs are properly formatted.
5. Report any broken links or references to the user for correction.

### Step 8: Write Final Report

1. Assemble all sections into a single markdown document in the defined order.
2. Ensure consistent formatting throughout:
   - Two blank lines before each `##` heading.
   - One blank line after each heading before content.
   - Consistent table alignment.
   - No trailing whitespace.
3. Write the file using `filesystem_write` to the specified output path.
4. Report to the user:
   - Output file path and size
   - Number of sections, tables, diagrams, and cross-references
   - Any validation warnings (broken links, missing data)

## Report Template

The following template serves as a starting point. Adapt it to the specific report type.

```markdown
# [Report Title]

**Author:** [Name]
**Date:** [YYYY-MM-DD]
**Version:** [X.Y]

---

## Table of Contents

[Auto-generated]

---

## Executive Summary

[3-5 sentence summary of key findings and recommendations]

## Introduction

[Background context, scope of the report, reporting period]

## Findings

### [Finding Category 1]

[Narrative with supporting data]

| Metric | Value | Change |
|--------|-------|--------|
| ...    | ...   | ...    |

![Description](diagrams/figure-1.svg)
*Figure 1: [Caption]*

### [Finding Category 2]

[Narrative with supporting data]

## Recommendations

1. **[Recommendation 1]** -- [Description]. Priority: [High/Medium/Low].
   Related finding: [link].
2. **[Recommendation 2]** -- [Description]. Priority: [High/Medium/Low].
   Related finding: [link].

## Appendices

### Appendix A: Raw Data

[Full data tables]

### Appendix B: Methodology

[How data was collected and analyzed]

### Appendix C: Diagram Source

[Mermaid/Graphviz source code for all diagrams]
```

## Edge Cases

- **Missing data sources**: If a referenced file or database is unavailable, note the
  gap in the report with a placeholder and a warning to the user. Do not fail the entire
  report because one source is missing.
- **Stale data**: If data files have timestamps, note the data currency in the report.
  Warn if data is older than the reporting period.
- **Large datasets**: Summarize in the body, full data in appendices. Do not embed tables
  with more than 50 rows in the main report body.
- **Conflicting data**: If different sources provide contradictory numbers for the same
  metric, flag the discrepancy in the report and note which source was used.

## Related Skills

- **diagram-from-code** (eskill-office): Run diagram-from-code before this skill to generate diagrams that can be embedded in the report.
- **data-pipeline** (eskill-office): Run data-pipeline before this skill to prepare the data that the report will present.
