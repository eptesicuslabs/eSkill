---
name: e-doc
description: "Converts PDF, DOCX, and PPTX files to clean structured markdown. Use when migrating documents to a markdown-based system or extracting text for processing. Also applies when: convert this PDF to markdown, extract text from Word doc, turn slides into a document."
---

# Document to Markdown Conversion

This skill converts documents in PDF, DOCX, and PPTX formats into clean, well-structured
markdown files. It preserves document hierarchy, formatting, tables, and structural elements
while producing readable markdown output suitable for version control, static site generators,
and documentation platforms.

## Prerequisites

The following eMCP tools are required:

- `pdf_read_text` -- extract text content from PDF files with page range support
- `pdf_read_metadata` -- retrieve PDF document metadata (title, author, creation date)
- `pdf_search` -- search for specific text across pages with surrounding context
- `pdf_extract_tables` -- extract tabular data from PDF pages as structured arrays
- `docx_read_html` -- read DOCX content as structured HTML for accurate conversion
- `docx_read_text` -- read DOCX content as plain text (fallback)
- `docx_read_tables` -- extract tables from DOCX as structured arrays
- `docx_read_sections` -- extract content organized by heading hierarchy
- `pptx_read_slides` -- read slide content and speaker notes from PPTX files
- `pptx_read_slide` -- read specific slides by range (e.g., "3-5,8") for targeted extraction
- `fs_write` -- write the resulting markdown file to disk

## Procedure

### Step 1: Detect Document Format

Determine the document format by inspecting the file extension of the input path.

- `.pdf` -- route to the PDF extraction pipeline
- `.docx` -- route to the DOCX extraction pipeline
- `.pptx` -- route to the PPTX extraction pipeline
- Any other extension -- inform the user that the format is not supported and list the
  accepted formats

Normalize the file path to use forward slashes. Resolve relative paths against the current
working directory. Confirm that the file exists before proceeding.

### Step 2: PDF Extraction

For PDF documents, follow this sequence:

1. Call `pdf_read_metadata` on the source file to retrieve the document title, author,
   subject, creation date, and page count.
2. Call `pdf_read_text` to extract text content. If the document exceeds 20 pages, process
   it in batches of 20 pages at a time (e.g., pages "1-20", then "21-40") and concatenate
   the results.
3. Call `pdf_extract_tables` to extract any tabular data from the PDF. Tables extracted
   this way are more accurate than heuristic detection from raw text. Use the structured
   array output directly when converting tables to markdown pipe format.
4. If the user requests content from a specific section of a large PDF, use `pdf_search`
   to locate the relevant pages first, then extract only those pages. This avoids
   processing the entire document when only a portion is needed.
5. Use the metadata title as the top-level heading (`# Title`). If the metadata title is
   empty, derive a title from the filename.
6. Inspect the extracted text for structural cues:
   - Lines in ALL CAPS or larger font indicators often represent headings.
   - Numbered sequences (1., 2., 3.) indicate ordered lists.
   - Bullet characters or dashes at line starts indicate unordered lists.
   - Repeated delimiter patterns (pipes, dashes) suggest tables.
7. Apply heuristics to assign heading levels based on text patterns and positioning.

PDF-specific considerations:

- Scanned PDFs may yield no text from `pdf_read_text`. In that case, notify the user that
  OCR may be required and suggest using the `image_ocr` tool from the eMCP image server if available.
- Multi-column layouts may produce interleaved text. Look for abrupt topic changes mid-line
  as an indicator and attempt to separate columns.
- Headers and footers often repeat on every page. Identify and remove repeated lines that
  appear at consistent positions.
- Page numbers should be stripped from the output.

### Step 3: DOCX Extraction

For DOCX documents, follow this sequence:

1. Call `docx_read_sections` to extract the document content organized by heading hierarchy.
   This provides a pre-structured view of the document that maps directly to markdown
   heading levels, making conversion more accurate than parsing raw HTML.
2. Call `docx_read_tables` to extract all tables as structured arrays. Use these directly
   for markdown table generation rather than parsing table markup from HTML.
3. Call `docx_read_html` to obtain remaining content as structured HTML. This preserves
   bold, italic, links, and other inline formatting not captured by the section/table tools.
4. If all structured extraction tools fail or return empty content, fall back to
   `docx_read_text` for plain text extraction.
5. When using the HTML path, proceed to Step 6 for HTML-to-markdown conversion.
6. When using the plain text fallback, apply the same structural heuristics described in
   Step 2 for PDF content.

DOCX-specific considerations:

- Track changes and comments are not included in the extracted content. Notify the user if
  the document may contain tracked changes.
- Embedded objects (OLE objects, embedded spreadsheets) cannot be extracted. Note their
  approximate positions in the output.
- Custom styles in DOCX may not map directly to standard heading levels. Treat any paragraph
  styled as "Heading 1" through "Heading 6" as the corresponding markdown heading.

### Step 4: PPTX Extraction

For PPTX documents, follow this sequence:

1. Call `pptx_read_slides` to extract all slide content including titles, body text, and
   speaker notes. For targeted extraction of specific slides (e.g., a subset requested by
   the user), use `pptx_read_slide` with a range like "1-5" or "3,7,12" instead of reading
   the entire presentation.
2. Structure the output so that each slide becomes a markdown section. Use `## Slide N: Title`
   as the heading for each slide, where N is the slide number and Title is the slide title.
3. Render bullet points from slides as markdown unordered lists.
4. Include speaker notes as blockquotes beneath each slide section, prefixed with
   `> **Speaker Notes:**`.
5. If a slide has no title, use `## Slide N` as the heading.

PPTX-specific considerations:

- Charts and SmartArt cannot be extracted as text. Insert a placeholder note such as
  `[Chart: description not available]` or `[SmartArt: description not available]`.
- Animations and transitions have no textual representation and are silently skipped.
- Grouped text boxes may appear in an unexpected order. Attempt to sort text elements by
  their vertical position on the slide (top to bottom, left to right).

### Step 5: Clean and Normalize Content

Apply the following normalization steps to the extracted text regardless of source format:

1. Fix encoding issues: replace common mojibake sequences (e.g., `â€"` with an em dash,
   `â€™` with an apostrophe). Normalize all text to UTF-8.
2. Normalize whitespace:
   - Collapse runs of three or more blank lines into two blank lines.
   - Remove trailing whitespace from every line.
   - Ensure the file ends with a single newline character.
3. Normalize line breaks: convert `\r\n` to `\n` throughout.
4. Fix smart quotes: convert curly quotes to straight quotes if the user prefers ASCII-safe
   markdown, or preserve them if Unicode output is acceptable (default: preserve).
5. Standardize list markers: use `-` for unordered lists and `1.` for ordered lists.

### Step 6: Convert HTML Elements to Markdown

When working with HTML output from `docx_read_html`, convert elements as follows:

| HTML Element          | Markdown Equivalent               |
|-----------------------|-----------------------------------|
| `<h1>` through `<h6>` | `#` through `######`             |
| `<p>`                 | Plain paragraph with blank lines  |
| `<strong>`, `<b>`     | `**bold**`                        |
| `<em>`, `<i>`         | `*italic*`                        |
| `<ul>` / `<li>`       | `- item`                          |
| `<ol>` / `<li>`       | `1. item`                         |
| `<table>`             | Markdown pipe table               |
| `<a href="...">`      | `[text](url)`                     |
| `<code>`              | `` `inline code` ``               |
| `<pre>`               | Fenced code block with triple backticks |
| `<blockquote>`        | `> quoted text`                   |
| `<br>`                | Two trailing spaces or blank line |
| `<img>`               | `![alt](src)` or placeholder      |

For nested lists, indent child items with four spaces. For tables, ensure alignment
indicators are present in the separator row (`:---`, `:---:`, `---:`).

Strip all remaining HTML tags after conversion. Remove inline styles and class attributes
entirely.

### Step 7: Preserve Document Structure

Ensure the following structural elements are correctly represented in the output:

- **Headings**: Maintain the original heading hierarchy. Do not skip heading levels (e.g.,
  do not jump from `#` to `###`). If the source document has inconsistent heading levels,
  normalize them to a consistent hierarchy.
- **Lists**: Preserve nesting depth. Ordered lists should restart numbering where the source
  document does.
- **Tables**: Convert to markdown pipe tables. For wide tables (more than 5 columns or
  content exceeding 80 characters per cell), add a note suggesting the user view the table
  in a rendered markdown viewer.
- **Code blocks**: Preserve indentation and add language hints to fenced code blocks when
  the language is identifiable.
- **Emphasis**: Preserve bold and italic markers. Do not double-apply emphasis.
- **Horizontal rules**: Convert page breaks or section dividers to `---`.

### Step 8: Handle Images

Documents often contain embedded images that cannot be directly represented in markdown text.

1. For each image encountered, insert a placeholder at the image location:
   `[Image: {original_filename} at position {page/slide/section}]`
2. If the image has alt text in the source document, include it:
   `[Image: {alt_text} ({original_filename})]`
3. At the end of the document, add an "Images" appendix listing all images found with their
   positions and original filenames.
4. Inform the user that images must be manually exported and linked if they are needed in
   the markdown output.

### Step 9: Write Output

1. Determine the output filename by replacing the source file extension with `.md`.
   For example, `report.pdf` becomes `report.md`.
2. If the user specifies a custom output path, use that instead.
3. Write the final markdown content using `fs_write`.
4. Report a summary to the user:
   - Source file and format
   - Number of pages/slides processed
   - Number of headings, tables, and images found
   - Output file path
   - Any warnings (images skipped, OCR suggested, formatting lost)

## Edge Cases and Troubleshooting

- **Password-protected files**: These cannot be processed. Inform the user and exit.
- **Corrupted files**: If the eMCP tool returns an error, relay the error message and
  suggest the user verify the file integrity.
- **Very large documents** (100+ pages): Process in batches and stream output incrementally.
  Warn the user that conversion may take several minutes.
- **Mixed-language documents**: UTF-8 output handles multilingual content. No special
  handling is required, but right-to-left text may not render correctly in all markdown
  viewers.
- **Empty documents**: If no content is extracted, write a minimal markdown file with the
  title and a note that the document appeared to be empty.

## Related Skills

- **e-report** (eskill-office): Follow up with e-report after this skill to restructure the converted markdown into a formatted report.
- **e-graph** (eskill-intelligence): Follow up with e-graph after this skill to extract entities and relationships from the converted documents.
