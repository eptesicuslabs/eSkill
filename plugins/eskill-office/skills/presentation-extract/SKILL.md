---
name: presentation-extract
description: "Extracts slide content, speaker notes, and metadata from PPTX files into organized markdown. Use when converting a presentation to a readable document or pulling out speaker notes. Also applies when: extract slides from PowerPoint, get speaker notes, read this pptx file."
---

# Presentation Extraction

This skill extracts the full content of PowerPoint (PPTX) files -- including slide text,
speaker notes, and structural metadata -- into organized markdown documents. It supports
multiple output modes: a single combined document, separate content and notes files, or
individual per-slide files.

## Prerequisites

The following eMCP tools are required:

- `pptx_read_metadata` -- retrieve presentation metadata (title, author, slide count)
- `pptx_read_slides` -- extract slide content including titles, body text, and speaker notes
- `filesystem_write` -- write output markdown files
- `filesystem_list_dir` -- check output directory existence

## Procedure

### Step 1: Read Presentation Metadata

Begin by extracting the presentation-level metadata:

1. Call `pptx_read_metadata` with the path to the PPTX file.
2. Record the following fields:
   - **Title**: The presentation title from document properties.
   - **Author**: The author field from document properties.
   - **Subject**: The subject or description if present.
   - **Created date**: When the presentation was created.
   - **Modified date**: When the presentation was last modified.
   - **Slide count**: Total number of slides in the presentation.
3. If the title is empty in the metadata, derive a title from the filename (strip the
   extension, replace hyphens and underscores with spaces, apply title case).
4. Report the metadata to the user as a summary before proceeding with full extraction.

### Step 2: Read All Slides

Extract the content of every slide in the presentation:

1. Call `pptx_read_slides` with the file path.
2. For each slide, the tool returns:
   - Slide number (1-based index)
   - Slide title (from the title placeholder, if present)
   - Body text (all text content from non-title placeholders)
   - Speaker notes (text from the notes pane)
3. Store the extracted data in an ordered list, preserving slide sequence.
4. Count and report to the user:
   - Total slides processed
   - Slides with titles vs. slides without titles
   - Slides with speaker notes vs. slides without speaker notes
   - Slides with no extractable text content (likely image-only or blank slides)

### Step 3: Process Individual Slides

For each slide, parse and structure the content:

1. **Title extraction**: Use the slide title as-is if provided. If the title placeholder
   is empty, attempt to use the first line of the body text as the title (if it appears
   to be a heading -- short, no trailing punctuation). Otherwise, leave the title as
   "Slide N" where N is the slide number.

2. **Body text processing**:
   - Identify bullet points: lines that begin with bullet characters, dashes, or are
     returned as list items by the tool. Convert to markdown unordered lists.
   - Identify numbered items: lines starting with digits followed by a period or
     parenthesis. Convert to markdown ordered lists.
   - Identify sub-bullets: indented list items become nested markdown lists (indent with
     four spaces).
   - Plain text paragraphs are separated by blank lines.

3. **Text box ordering**: If the slide contains multiple text boxes, they may be returned
   in an arbitrary order. Sort them by their position on the slide: top-to-bottom first,
   then left-to-right. If positional data is not available, preserve the order returned
   by the tool.

4. **Special content detection**:
   - Tables: If structured table data is present, format as a markdown pipe table.
   - Code snippets: If a text box uses a monospace font or contains code-like content,
     wrap in a fenced code block.
   - URLs: Detect bare URLs and convert to markdown links.

5. **Speaker notes processing**:
   - Preserve the full text of the speaker notes.
   - Apply the same list and paragraph formatting as body text.
   - Do not merge speaker notes into the slide body; keep them separate.

### Step 4: Structure as Markdown

Assemble the processed slides into a markdown document:

1. **Document header**: Start with a level-1 heading using the presentation title:
   ```markdown
   # Presentation Title

   **Author:** Author Name
   **Date:** YYYY-MM-DD
   **Slides:** N
   ```

2. **Slide sections**: Each slide becomes a level-2 section:
   ```markdown
   ## Slide 1: Introduction

   Welcome to the quarterly review. This presentation covers:

   - Financial performance
   - Product milestones
   - Team updates

   > **Speaker Notes:** Begin by thanking the team for their work this quarter.
   > Mention the record revenue figure early to set a positive tone.
   ```

3. **Slides without titles**:
   ```markdown
   ## Slide 5

   [Slide content here]
   ```

4. **Blank or image-only slides**:
   ```markdown
   ## Slide 8: [Visual Content]

   [This slide contains visual content (images, charts, or diagrams) that cannot be
   extracted as text.]
   ```

5. Use horizontal rules (`---`) between slides for visual separation in the rendered
   output.

### Step 5: Handle Speaker Notes

Offer the user a choice of how to present speaker notes:

**Option A: Inline as blockquotes (default)**

Speaker notes appear directly beneath each slide's content as blockquotes:
```markdown
> **Speaker Notes:** The speaker notes text goes here. Multiple paragraphs
> in the notes are preserved as separate blockquote paragraphs.
```

**Option B: Separate companion document**

Create two files:
- `presentation-content.md` -- slide content only, no speaker notes
- `presentation-notes.md` -- speaker notes only, organized by slide number:
  ```markdown
  # Speaker Notes: Presentation Title

  ## Slide 1: Introduction
  Begin by thanking the team...

  ## Slide 2: Financial Overview
  Emphasize the year-over-year growth...
  ```

**Option C: Footnotes**

Speaker notes appear as footnotes at the end of the document:
```markdown
## Slide 1: Introduction

Content here.[^slide1-notes]

[^slide1-notes]: Begin by thanking the team for their work this quarter.
```

Apply the user's chosen format consistently throughout the document.

### Step 6: Create Table of Contents

Generate a table of contents from the slide titles:

```markdown
## Table of Contents

1. [Introduction](#slide-1-introduction)
2. [Financial Overview](#slide-2-financial-overview)
3. [Product Milestones](#slide-3-product-milestones)
4. [Team Updates](#slide-4-team-updates)
5. [Q&A](#slide-5-qa)
```

Place the TOC after the document header and before the first slide section. Anchor links
should use the standard markdown heading-to-anchor conversion: lowercase, spaces to
hyphens, strip special characters.

For presentations with more than 20 slides, the TOC provides essential navigation. For
shorter presentations (5 or fewer slides), the TOC is optional -- ask the user if they
want one.

### Step 7: Note Non-Extractable Visual Elements

Track and report all content that cannot be extracted as text:

1. **Charts and graphs**: Note the slide number and the type of chart if identifiable.
   Insert a placeholder: `[Chart: {type} on Slide N]`.
2. **Images and photographs**: Insert `[Image on Slide N]`. If alt text is available in
   the PPTX, include it: `[Image: {alt text} on Slide N]`.
3. **SmartArt and shapes**: Insert `[SmartArt/Shape diagram on Slide N]`.
4. **Embedded videos and audio**: Insert `[Embedded media on Slide N]`.
5. **Animations and transitions**: These have no textual content. Silently skip them but
   note in the document footer: "Note: Slide animations and transitions are not
   represented in this document."

At the end of the document, add a summary section:

```markdown
## Visual Elements Summary

The following slides contain visual elements that could not be extracted:

| Slide | Element Type | Description |
|-------|-------------|-------------|
| 3     | Chart       | Bar chart   |
| 7     | Image       | Team photo  |
| 12    | SmartArt    | Process flow|
```

### Step 8: Write Output

Write the output based on the user's preferred mode:

**Single combined document (default):**
1. Write everything to a single `.md` file.
2. Name it based on the source file: `presentation-name.md`.

**Separate content and notes:**
1. Write slide content to `presentation-name-content.md`.
2. Write speaker notes to `presentation-name-notes.md`.

**Per-slide files:**
1. Create a directory named after the presentation.
2. Write each slide to its own file: `slide-01.md`, `slide-02.md`, etc.
3. Write an `index.md` file with the TOC linking to each slide file.

After writing:
1. Report the output file path(s) to the user.
2. Provide a summary:
   - Slides processed and total text extracted (approximate word count).
   - Number of slides with speaker notes.
   - Number of visual elements that could not be extracted.
   - Any issues encountered during extraction.

## Edge Cases

- **Password-protected presentations**: Cannot be processed. Inform the user and exit.
- **Corrupted PPTX files**: If the eMCP tool returns an error, relay the error and
  suggest verifying the file.
- **Very large presentations** (100+ slides): Process all slides but warn the user that
  the output document may be very long. Suggest per-slide output mode for easier
  navigation.
- **Presentations with no text**: Some presentations are entirely visual (e.g., photo
  slideshows). Produce a document with placeholders for each slide and the visual elements
  summary. Inform the user that no text content was available.
- **Non-Latin text**: UTF-8 output handles all scripts. No special handling is required.
- **Master slide and layout text**: Text from slide masters (e.g., footer text, company
  name) may repeat on every slide. Detect repeated text that appears identically on
  multiple slides and either deduplicate or note it once in the document header.

## Related Skills

- **document-to-markdown** (eskill-office): Follow up with document-to-markdown after this skill to convert extracted presentation content into structured markdown.
- **report-builder** (eskill-office): Follow up with report-builder after this skill to reorganize extracted slides into a written report.
