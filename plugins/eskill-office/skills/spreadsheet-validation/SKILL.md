---
name: spreadsheet-validation
description: "Validates spreadsheet and CSV data against configurable rules and produces cell-level quality reports. Use when auditing data before import, checking for missing or malformed values, or verifying consistency. Also applies when: check this spreadsheet for errors, validate CSV data, audit data quality."
---

# Spreadsheet Validation

This skill validates the contents of spreadsheets and CSV files against a set of
configurable rules, producing detailed data quality reports with cell-level findings,
severity classifications, and suggested fixes. It is designed for pre-import auditing,
ongoing data quality monitoring, and compliance verification.

## Prerequisites

The following eMCP tools are required:

- `spreadsheet_read` -- read data from XLSX and XLS files
- `spreadsheet_read_csv` -- read data from CSV and TSV files
- `filesystem_write` -- write validation reports to disk
- `filesystem_read` -- read rule configuration files if provided

## Procedure

### Step 1: Read Spreadsheet Data

Load the data to be validated:

1. Determine the file type from the extension:
   - `.xlsx` or `.xls`: use `spreadsheet_read`
   - `.csv`: use `spreadsheet_read_csv` with comma delimiter
   - `.tsv`: use `spreadsheet_read_csv` with tab delimiter
2. Treat the first row as column headers by default. If the user specifies that headers
   are in a different row or absent, adjust accordingly.
3. Record the total number of rows and columns.
4. Preview the first 5 rows to confirm the data was read correctly.
5. Report the data shape to the user: row count, column count, column names, and a
   sample of values from each column.

If the spreadsheet contains multiple sheets, ask the user which sheet to validate or
validate all sheets sequentially.

### Step 2: Define Validation Rules

Validation rules can be provided by the user, loaded from a configuration file, or
inferred from the data. The following rule types are supported:

**Required fields (no nulls or blanks):**
- Specify which columns must have a value in every row.
- A cell is considered blank if it is null, empty, or contains only whitespace.
- Configuration: `required: [column_a, column_b, column_c]`

**Type constraints:**
- Specify the expected data type for each column.
- Supported types: `integer`, `float`, `number` (integer or float), `date`, `email`,
  `boolean`, `text`.
- A value violates the constraint if it cannot be parsed as the specified type.
- Configuration: `types: { column_a: integer, column_b: date, column_c: email }`

**Range constraints (minimum and maximum values):**
- For numeric columns: specify min and/or max values (inclusive).
- For date columns: specify earliest and/or latest dates.
- For text columns: specify min and/or max string length.
- Configuration: `ranges: { age: { min: 0, max: 150 }, hire_date: { min: "2000-01-01" } }`

**Uniqueness constraints:**
- Specify columns that must contain unique values (no duplicates).
- Can apply to single columns or combinations of columns (composite uniqueness).
- Configuration: `unique: [id]` or `unique: [[first_name, last_name, dob]]`

**Referential integrity:**
- Specify that values in a column must exist in a reference list or another column.
- The reference list can be provided inline or read from another sheet or file.
- Configuration: `references: { status: ["active", "inactive", "pending"] }`

**Format patterns (regular expressions):**
- Specify a regex pattern that values must match.
- Common patterns:
  - Phone: `^\+?[1-9]\d{1,14}$` (E.164 format)
  - Email: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
  - US ZIP code: `^\d{5}(-\d{4})?$`
  - ISO date: `^\d{4}-\d{2}-\d{2}$`
  - URL: `^https?://`
- Configuration: `patterns: { phone: "^\\+?[1-9]\\d{1,14}$" }`

**Custom cross-field rules:**
- Comparisons between columns: `end_date >= start_date`
- Conditional requirements: if column A has value X, then column B must not be blank
- Computed checks: `total = quantity * unit_price`

If no rules are provided, infer a basic set from the data:
1. Columns with no null values are assumed to be required.
2. Columns where all values parse as numbers are assumed to be numeric.
3. Columns where all values parse as dates are assumed to be date fields.
4. Columns named "id", "key", or "code" are assumed to require uniqueness.

Present the inferred rules to the user for confirmation before proceeding.

### Step 3: Apply Validation Rules

Execute each rule against every row in the dataset:

1. Iterate through each row (tracking the row number for reporting -- use 1-based indexing
   that matches the spreadsheet, accounting for the header row).
2. For each cell, apply all rules that pertain to that column.
3. When a rule is violated, create a violation record containing:
   - Row number (as it appears in the spreadsheet)
   - Column name
   - Cell value (the actual value found)
   - Rule that was violated (rule type and parameters)
   - Expected value or constraint (what was expected)
   - Severity level (see Step 4)
4. Continue processing all rows even if violations are found. Do not stop at the first
   error.

Performance considerations for large datasets:
- For files with more than 10,000 rows, report progress at regular intervals.
- Collect all violations in memory. If the number of violations exceeds 10,000, stop
  collecting detailed records and switch to counting violations by rule and column.
  Note this in the report.

### Step 4: Categorize Violation Severity

Assign a severity level to each violation:

**Error (data is unusable without correction):**
- Required field is missing
- Type constraint violated (e.g., text in a numeric field that will cause import failure)
- Uniqueness constraint violated (duplicate primary keys)
- Referential integrity violated (value not in allowed set)
- Cross-field validation failed (e.g., end date before start date)

**Warning (data is suspicious but may be intentional):**
- Value is outside the expected range but parseable (e.g., age = 200)
- Format pattern does not match but the value is not empty
- Unusual values that are statistical outliers (more than 3 standard deviations from the
  mean in numeric columns)
- Potential duplicates (values that differ only in whitespace or casing)

**Info (style or consistency issues):**
- Leading or trailing whitespace in text values
- Inconsistent casing (e.g., "Active", "active", "ACTIVE" in the same column)
- Inconsistent date formats within a column (e.g., "2025-01-15" and "01/15/2025")
- Trailing zeros in numeric values stored as text

The severity classification determines how violations are reported and whether they
block downstream processing.

### Step 5: Generate Summary Statistics

Compute and present an overview of data quality:

```markdown
## Validation Summary

| Metric                  | Value     |
|-------------------------|-----------|
| Total rows              | 1,500     |
| Total columns           | 12        |
| Valid rows (no errors)  | 1,342     |
| Rows with errors        | 158       |
| Rows with warnings      | 87        |
| Total violations        | 312       |
| Error count             | 198       |
| Warning count           | 76        |
| Info count              | 38        |
| Data quality score      | 89.5%     |
```

The data quality score is calculated as:
`(rows_without_errors / total_rows) * 100`

Break down violations by rule type:

```markdown
## Violations by Rule

| Rule Type           | Column       | Errors | Warnings | Info |
|---------------------|-------------|--------|----------|------|
| Required field      | email       | 45     | 0        | 0    |
| Type constraint     | age         | 23     | 0        | 0    |
| Range constraint    | salary      | 0      | 15       | 0    |
| Uniqueness          | employee_id | 12     | 0        | 0    |
| Format pattern      | phone       | 0      | 42       | 0    |
| Consistent casing   | status      | 0      | 0        | 22   |
```

Break down by column to identify the most problematic data fields:

```markdown
## Violations by Column

| Column      | Total Violations | Error | Warning | Info | % Invalid |
|-------------|-----------------|-------|---------|------|-----------|
| email       | 48              | 45    | 3       | 0    | 3.2%      |
| phone       | 42              | 0     | 42      | 0    | 2.8%      |
| age         | 28              | 23    | 5       | 0    | 1.9%      |
| status      | 22              | 0     | 0       | 22   | 1.5%      |
```

### Step 6: Generate Detailed Findings

Produce a detailed report listing each violation:

```markdown
## Detailed Findings

### Errors

| Row | Column      | Value        | Rule             | Expected              |
|-----|-------------|-------------|------------------|-----------------------|
| 15  | email       | (blank)     | Required field   | Non-empty value       |
| 23  | age         | "twenty"    | Type: integer    | Integer value         |
| 47  | employee_id | "E1001"     | Uniqueness       | Unique (dup of row 3) |
| 89  | end_date    | 2025-01-01  | Cross-field      | >= start_date (2025-03-15) |

### Warnings

| Row | Column | Value    | Rule            | Expected               |
|-----|--------|---------|-----------------|------------------------|
| 102 | age    | 250     | Range: 0-150    | Value between 0 and 150|
| 156 | phone  | 555-1234| Format: E.164   | +[country][number]     |

### Info

| Row | Column | Value    | Issue                  | Suggestion              |
|-----|--------|---------|------------------------|-------------------------|
| 12  | status | "Active "| Trailing whitespace   | Trim to "Active"        |
| 34  | status | "ACTIVE" | Inconsistent casing   | Normalize to "Active"   |
```

For large violation sets (over 100 violations of a single type), show the first 20
examples and summarize the rest: "... and 80 more violations of this type."

### Step 7: Suggest Fixes

For common violation patterns, provide actionable fix suggestions:

**Leading/trailing whitespace:**
- Affected rows: list row numbers
- Fix: trim all values in the affected column
- Estimated impact: N rows corrected

**Inconsistent casing:**
- Detected variants: list all case variants and their counts
- Most common variant: the value that appears most frequently
- Fix: normalize all values to the most common variant (or a specified standard)
- Estimated impact: N rows corrected

**Date format mismatches:**
- Detected formats: list all date formats found in the column with counts
- Dominant format: the format used by the majority of values
- Fix: convert all dates to ISO 8601 (YYYY-MM-DD) or the dominant format
- Estimated impact: N rows corrected

**Near-duplicate values:**
- Pairs of values that differ by whitespace, casing, or minor typos
- Example: "Jhon Smith" vs "John Smith" (potential typo)
- Fix: manual review recommended for each pair

**Numeric values stored as text:**
- Values that are numeric but stored with leading zeros, currency symbols, or
  thousand separators
- Fix: strip formatting characters and convert to numeric type
- Estimated impact: N rows corrected

Present fixes as a prioritized list, ordered by the number of rows affected (highest
first). Include the estimated data quality score improvement if all suggested fixes
are applied.

## Output Format

Write the validation report using `filesystem_write`. The default output path is the
source filename with a `-validation` suffix: `data.xlsx` produces `data-validation.md`.

The complete report structure:

```markdown
# Data Validation Report

**Source file:** path/to/file.xlsx
**Sheet:** Sheet1
**Validated on:** YYYY-MM-DD
**Rules applied:** N

---

## Validation Summary
[Summary statistics table]

## Violations by Rule
[Rule breakdown table]

## Violations by Column
[Column breakdown table]

## Detailed Findings
### Errors
[Error details table]

### Warnings
[Warning details table]

### Info
[Info details table]

## Suggested Fixes
[Prioritized fix list]

## Rules Applied
[Complete list of all validation rules that were checked]
```

## Edge Cases

- **Empty spreadsheet**: Report that the file contains no data rows. No validation
  rules can be applied. Exit with a summary noting zero rows.
- **Single-row spreadsheet**: Validate the single row normally. Note that uniqueness
  constraints are trivially satisfied.
- **All rows valid**: Report a clean bill of health with 100% data quality score.
  Still generate the summary to confirm that validation was performed.
- **Extremely wide spreadsheets** (50+ columns): Generate the report normally but
  warn the user that the detailed findings table may be very wide. Suggest focusing
  on specific columns if the output is unwieldy.
- **Mixed encoding**: If values contain unexpected byte sequences, flag them as
  encoding issues under the Info severity level.
- **Formulas in cells**: The eMCP tools read computed values, not formulas. Validation
  applies to the computed result. Note in the report that formula cells were evaluated
  to their current values.
- **Merged cells**: Merged cells may appear as a value in the first cell and blanks
  in the merged range. If a required-field rule flags blanks in a merged range, note
  this as a potential false positive.

## Related Skills

- **data-pipeline** (eskill-office): Follow up with data-pipeline after this skill to process the validated spreadsheet data.
- **report-builder** (eskill-office): Follow up with report-builder after this skill to summarize validation results in a formatted report.
