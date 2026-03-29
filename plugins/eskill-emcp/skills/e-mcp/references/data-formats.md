# Data Formats Servers

## @emcp/server-data-file (4 tools)

Read, query, modify, and convert structured data files (JSON, YAML, TOML).

### data_file_read

Read and parse a data file.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Path to JSON, YAML, or TOML file |

### data_file_query

Query a dot-path within a data file.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Path to data file |
| `query` | string | yes | | Dot-path (e.g., "scripts.build", "dependencies.react") |

### data_file_set

Set a value at a dot-path. Requires `allowWrite`.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Path to data file |
| `query` | string | yes | | Dot-path |
| `value` | any | yes | | Value to set |

### data_file_convert

Convert between JSON, YAML, and TOML formats.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Source file path |
| `targetFormat` | "json" \| "yaml" \| "toml" | yes | | Output format |

---

## @emcp/server-sqlite (4 tools)

Query and modify SQLite databases. Read operations are always available; write operations require `allowWrite`.

### sql_list_tables

List all tables and views in a database.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `database` | string | yes | | Database name (must be in configured databases) |

### sql_describe_table

Describe columns, types, and constraints.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `database` | string | yes | | Database name |
| `table` | string | yes | | Table name |

### sql_query

Run a read-only SQL query (SELECT, WITH, PRAGMA, EXPLAIN).

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `database` | string | yes | | Database name |
| `sql` | string | yes | | SQL query |
| `params` | (string\|number\|null)[] | no | [] | Bind parameters |

### sql_execute

Execute a write SQL statement (INSERT, UPDATE, DELETE, CREATE, DROP). Requires `allowWrite`.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `database` | string | yes | | Database name |
| `sql` | string | yes | | SQL statement |
| `params` | (string\|number\|null)[] | no | [] | Bind parameters |

---

## @emcp/server-log (4 tools)

Parse and search log files. Auto-detects JSONL, syslog, and generic log formats.

### log_parse

Parse a log file into structured entries.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Log file path |
| `maxLines` | number | no | | Maximum lines to parse |

### log_errors

Extract only error/fatal/critical entries.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Log file path |
| `maxLines` | number | no | | Maximum lines to scan |

### log_stats

Get statistics: line counts by level, time range.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Log file path |

### log_search

Search log entries by regex, optionally filtered by level.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Log file path |
| `pattern` | string | yes | | Regex search pattern |
| `level` | string | no | | Filter by log level |
| `maxResults` | number | no | 100 | Maximum results |

---

## @emcp/server-spreadsheet (5 tools)

Read and query spreadsheet files (XLSX, XLS, CSV, TSV).

### spreadsheet_read

Read all data from a worksheet.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Spreadsheet file path |
| `sheet` | string | no | | Worksheet name (defaults to first sheet) |
| `maxRows` | number | no | | Maximum rows to return |

### spreadsheet_list_sheets

List all worksheet names and dimensions.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Spreadsheet file path |

### spreadsheet_query

Filter rows by column value (case-insensitive contains).

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Spreadsheet file path |
| `sheet` | string | no | | Worksheet name |
| `column` | string | yes | | Column header to filter |
| `value` | string | yes | | Value to search for |
| `maxRows` | number | no | | Maximum rows |

### spreadsheet_read_csv

Read CSV/TSV with custom delimiter.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | CSV/TSV file path |
| `delimiter` | string | no | "," | Field delimiter |
| `maxRows` | number | no | | Maximum rows |

### spreadsheet_read_range

Read a specific cell range using A1 notation.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Spreadsheet file path |
| `sheet` | string | no | | Worksheet name |
| `range` | string | yes | | A1 range (e.g., "B2:D10") |

---

## @emcp/server-markdown (6 tools)

Parse and extract structure from markdown files.

### markdown_to_html

Convert markdown to HTML.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Markdown file path |

### markdown_headings

Extract all headings with depth.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Markdown file path |

### markdown_links

Extract all links.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Markdown file path |

### markdown_code_blocks

Extract fenced code blocks.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Markdown file path |

### markdown_front_matter

Parse YAML front matter.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Markdown file path |

### markdown_read_section

Extract content under a specific heading.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Markdown file path |
| `heading` | string | yes | | Heading text to extract under |
