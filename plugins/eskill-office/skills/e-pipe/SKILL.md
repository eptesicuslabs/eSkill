---
name: e-pipe
description: "Imports spreadsheet and CSV data into SQLite for querying, transformation, and export. Use when loading tabular data for SQL analysis or joining multiple sources. Also applies when: import CSV, analyze spreadsheet data, ETL, convert Excel to database, load data into SQLite."
---

# Data Pipeline: Spreadsheet to SQLite

This skill imports tabular data from spreadsheets (XLSX, XLS) and delimited text files
(CSV, TSV) into a SQLite database, enabling SQL-based querying, transformation, joining,
and export. It bridges the gap between spreadsheet-oriented data and relational database
operations.

## Prerequisites

The following eMCP tools are required:

- `spreadsheet_read` -- read data from XLSX and XLS files
- `spreadsheet_read_range` -- read a specific cell range in A1 notation (e.g., "B2:D10")
- `spreadsheet_read_csv` -- read data from CSV and TSV files
- `pdf_extract_tables` -- extract tabular data from PDF files for import
- `docx_read_tables` -- extract tables from DOCX files as structured arrays
- `pptx_extract_tables` -- extract tables embedded in PPTX slides
- `sql_execute` -- execute DDL and DML statements against a SQLite database
- `sql_query` -- execute SELECT queries and return results
- `fs_write` -- write exported results to files

## Procedure

### Step 1: Read Source Data

Determine the file type from the extension and read accordingly:

- For `.xlsx` or `.xls` files: use `spreadsheet_read` with the file path. If the workbook
  contains multiple sheets, ask the user which sheet to import or import all sheets as
  separate tables. When the user needs only a specific region of data (e.g., a named range
  or a known cell block), use `spreadsheet_read_range` with A1 notation like "B2:D10" to
  read just that range. This is more efficient for large spreadsheets where only a subset
  of data is relevant.
- For `.csv` files: use `spreadsheet_read_csv` with the file path. Assume comma delimiter
  unless the user specifies otherwise.
- For `.tsv` files: use `spreadsheet_read_csv` with the file path and tab delimiter.
- For `.pdf` files containing tables: use `pdf_extract_tables` to extract tabular data.
  PDF tables are converted to structured arrays suitable for direct import into SQLite.
- For `.docx` files containing tables: use `docx_read_tables` to extract tables as
  structured arrays. Each table in the document becomes a separate importable dataset.
- For `.pptx` files containing tables: use `pptx_extract_tables` to extract tables
  embedded in slides. Each slide table becomes a separate importable dataset.

When reading the data:

1. Treat the first row as column headers by default. If the first row contains data rather
   than headers, generate synthetic column names (column_1, column_2, etc.) and include
   that row in the data.
2. Note the total number of rows and columns read.
3. Preview the first 5 rows to confirm the data looks correct before proceeding.
4. Report the shape of the data to the user: row count, column count, and column names.

Handle multiple source files by reading each one independently. Each source file will
become a separate table in the SQLite database unless the user requests otherwise.

### Step 2: Analyze Column Types and Suggest Schema

For each column in the dataset, inspect the values to infer an appropriate SQL type:

1. **INTEGER**: All non-null values parse as integers (no decimal point). Examples: row
   counts, IDs, years, quantities.
2. **REAL**: All non-null values parse as floating-point numbers. Examples: prices,
   percentages, measurements.
3. **DATE**: Values match common date patterns (YYYY-MM-DD, MM/DD/YYYY, DD-Mon-YYYY, etc.).
   Store as TEXT in SQLite but note the detected format for later parsing.
4. **TEXT**: The default type when values do not fit the above categories.

Type inference rules:

- If more than 90% of non-null values in a column parse as a given type, assign that type.
  The remaining values are likely data quality issues.
- Columns with fewer than 10 distinct values may be categorical. Note this for the user
  but still store as TEXT.
- Columns named "id", "key", or ending in "_id" are likely primary or foreign keys. Suggest
  adding appropriate constraints.

Present the inferred schema to the user for confirmation before creating the table. Format
the schema as a CREATE TABLE statement so the user can review and modify it.

### Step 3: Create SQLite Table

Build and execute a CREATE TABLE statement based on the confirmed schema:

```sql
CREATE TABLE IF NOT EXISTS table_name (
    column1 TYPE CONSTRAINT,
    column2 TYPE CONSTRAINT,
    ...
);
```

Naming conventions:

- Derive the table name from the source filename, sanitized for SQL (replace spaces and
  special characters with underscores, lowercase).
- Column names should also be sanitized: lowercase, underscores for spaces, no leading
  digits (prefix with underscore if needed).
- Preserve the original column names as comments in the CREATE TABLE statement for
  reference.

Execute the statement using `sql_execute`. If a table with the same name already exists,
ask the user whether to drop and recreate, append data, or abort.

### Step 4: Insert Data

Insert the data into the created table:

1. Build INSERT statements in batches. For datasets under 1000 rows, a single batch is
   acceptable. For larger datasets, use batches of 500 rows.
2. Use parameterized values to handle special characters, quotes, and NULL values correctly.
3. Apply type coercion during insertion:
   - Trim leading and trailing whitespace from all text values.
   - Convert empty strings to NULL.
   - Parse numeric strings to their appropriate types.
   - Normalize date formats to ISO 8601 (YYYY-MM-DD) where a date type was inferred.
4. Track any rows that fail to insert due to constraint violations. Report these to the
   user with the row number and the reason for failure.

For large datasets (over 10,000 rows), report progress at regular intervals (every 2,000
rows).

### Step 5: Verify Data Integrity

After insertion, verify that the data was loaded correctly:

1. Compare the row count in the SQLite table to the number of rows read from the source:
   ```sql
   SELECT COUNT(*) FROM table_name;
   ```
2. Spot-check values: query the first 5 and last 5 rows and compare them against the
   source data.
3. Check for unexpected NULLs:
   ```sql
   SELECT column_name, COUNT(*) AS null_count
   FROM table_name
   WHERE column_name IS NULL
   GROUP BY column_name;
   ```
4. Report a summary: rows inserted, rows skipped (if any), null counts per column.

If the row counts do not match, investigate and report the discrepancy. Common causes
include duplicate primary key values, encoding issues, or constraint violations.

### Step 6: Query and Transform

Once the data is in SQLite, the user can run queries using `sql_query`. Support the
following common patterns:

**Aggregation queries:**
```sql
SELECT category, COUNT(*) AS count, SUM(amount) AS total, AVG(amount) AS average
FROM table_name
GROUP BY category
ORDER BY total DESC;
```

**Filtering and search:**
```sql
SELECT * FROM table_name
WHERE date_column BETWEEN '2025-01-01' AND '2025-12-31'
  AND status = 'active';
```

**Joining multiple tables:**
```sql
SELECT a.name, b.total_orders, c.region
FROM customers a
JOIN orders b ON a.customer_id = b.customer_id
JOIN regions c ON a.region_id = c.region_id;
```

**Pivoting data** (using CASE expressions in SQLite):
```sql
SELECT product,
  SUM(CASE WHEN quarter = 'Q1' THEN revenue ELSE 0 END) AS q1,
  SUM(CASE WHEN quarter = 'Q2' THEN revenue ELSE 0 END) AS q2,
  SUM(CASE WHEN quarter = 'Q3' THEN revenue ELSE 0 END) AS q3,
  SUM(CASE WHEN quarter = 'Q4' THEN revenue ELSE 0 END) AS q4
FROM sales
GROUP BY product;
```

**Window functions** (SQLite 3.25+):
```sql
SELECT name, department, salary,
  RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rank
FROM employees;
```

**Creating derived tables:**
```sql
CREATE TABLE monthly_summary AS
SELECT strftime('%Y-%m', order_date) AS month,
  COUNT(*) AS order_count,
  SUM(total) AS revenue
FROM orders
GROUP BY month;
```

Offer these patterns proactively when the user describes what they want to accomplish but
does not provide specific SQL.

### Step 7: Export Results

Export query results or transformed tables back to files:

**CSV export:**

1. Run the query or SELECT from the table.
2. Format the results as CSV with a header row.
3. Write to the specified output path using `fs_write`.

**Markdown table export:**

1. Run the query.
2. Format as a markdown pipe table with header and alignment rows.
3. For large result sets (over 50 rows), warn the user that the markdown table may be
   unwieldy and suggest CSV instead.

**Summary export:**

1. Run aggregation queries.
2. Format results as a markdown document with headings, summary statistics, and data tables.

Always include the query that produced the results as a code block in exported documents
for reproducibility.

## Edge Cases and Troubleshooting

- **Mixed types in a column**: If a column contains both numbers and text (e.g., "N/A"
  mixed with numeric values), default to TEXT. Suggest the user clean the data or create
  a view that casts the numeric values.
- **NULL handling**: Empty cells, "N/A", "null", "NULL", "-", and blank strings are all
  treated as NULL during import. Document this behavior for the user.
- **Date parsing**: Dates in ambiguous formats (e.g., 01/02/2025 could be Jan 2 or Feb 1)
  should be flagged. Ask the user to confirm the date format (MM/DD/YYYY vs DD/MM/YYYY)
  before proceeding.
- **Large files** (over 100,000 rows): SQLite handles this well, but import will take
  longer. Use batch inserts and report progress. Warn the user before starting.
- **Character encoding**: If the CSV contains non-UTF-8 characters, attempt to detect the
  encoding (common alternatives: Latin-1, Windows-1252). Notify the user if re-encoding
  is applied.
- **Duplicate column names**: If the source has duplicate column headers, append a numeric
  suffix (e.g., `amount`, `amount_2`, `amount_3`).
- **Extremely wide tables** (50+ columns): These are valid but may be difficult to work
  with. Suggest the user select specific columns rather than using `SELECT *`.

## Related Skills

- **e-sheet** (eskill-office): Run e-sheet before this skill to ensure input data quality before pipeline processing.
- **e-report** (eskill-office): Follow up with e-report after this skill to present pipeline output in a formatted report.
