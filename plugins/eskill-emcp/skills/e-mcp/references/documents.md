# Document Servers

## @emcp/server-pdf (5 tools)

Extract text, metadata, tables, and search within PDF files.

### pdf_read_text

Extract text content from a PDF.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | PDF file path |
| `pages` | string | no | | Page range (e.g., "1-3,5") |

### pdf_read_metadata

Read document metadata (title, author, page count, dates).

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | PDF file path |

### pdf_count_pages

Count pages in a PDF.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | PDF file path |

### pdf_search

Search text across all pages, returning page numbers and context.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | PDF file path |
| `query` | string | yes | | Search text |
| `maxResults` | number | no | | Maximum results |

### pdf_extract_tables

Extract tabular data by analyzing text positions.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | PDF file path |
| `pages` | string | no | | Page range |

---

## @emcp/server-docx (5 tools)

Read content and structure from Word .docx documents.

### docx_read_text

Extract plain text.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | DOCX file path |

### docx_read_html

Convert to HTML preserving formatting.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | DOCX file path |

### docx_read_metadata

Get word count, paragraph count, file size.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | DOCX file path |

### docx_read_tables

Extract all tables as structured arrays.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | DOCX file path |

### docx_read_sections

Extract content under a heading, or list all sections with word counts.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | DOCX file path |
| `heading` | string | no | | Specific heading to extract (omit to list all) |

---

## @emcp/server-pptx (5 tools)

Read content, slides, and tables from PowerPoint .pptx files.

### pptx_read_text

Extract all text from a presentation.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | PPTX file path |

### pptx_read_slides

Read slide-by-slide content with speaker notes.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | PPTX file path |

### pptx_read_metadata

Get slide count, author, title, file size.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | PPTX file path |

### pptx_read_slide

Read specific slides by number or range.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | PPTX file path |
| `slides` | string | yes | | Slide range (e.g., "3-5,8") |

### pptx_extract_tables

Extract tables from slides.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | PPTX file path |
| `slide` | number | no | | Specific slide number (omit for all) |
