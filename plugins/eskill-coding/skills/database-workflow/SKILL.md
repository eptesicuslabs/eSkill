---
name: database-workflow
description: "Plans and validates database schema changes with migration scripts and rollback strategies. Use when modifying database schemas, planning migrations, creating new tables, or reviewing existing schema structure."
---

# Database Workflow

This skill guides the process of planning, writing, validating, and applying database schema changes. It emphasizes safety through forward and rollback migration pairs, validation in test environments, and careful review of data loss risks.

## Prerequisites

- A database schema to modify (SQLite via eMCP, or other databases for script generation).
- Understanding of the desired schema change.
- For eMCP-managed databases: access to the sql tools (sql_list_tables, sql_describe_table, sql_execute).

## Workflow

### Step 1: Inspect the Current Schema

Before making changes, understand the existing schema.

**For SQLite databases via eMCP**:
- Use `sql_list_tables` to get all table names.
- Use `sql_describe_table` for each relevant table to see columns, types, constraints, and indexes.

**For other databases or migration-based projects**:
- Read existing migration files using `filesystem` tools to reconstruct the schema history.
- Look for migration directories: `migrations/`, `db/migrate/`, `alembic/versions/`, `prisma/migrations/`.
- Read the schema definition file if one exists: `schema.prisma`, `models.py`, `schema.rb`.

Document the current state of the tables being modified. This serves as the "before" snapshot for review.

### Step 2: Define the Desired Change

Clearly specify the schema change. Common operations:

| Operation            | Description                                    | Risk Level |
|----------------------|------------------------------------------------|------------|
| Add table            | Create a new table                             | Low        |
| Add column           | Add a column to an existing table              | Low        |
| Add column NOT NULL  | Add a non-nullable column without a default    | High       |
| Drop column          | Remove a column from a table                   | High       |
| Drop table           | Remove an entire table                         | Critical   |
| Rename column        | Change a column name                           | Medium     |
| Rename table         | Change a table name                            | Medium     |
| Change type          | Modify a column's data type                    | High       |
| Add index            | Create an index on column(s)                   | Low        |
| Drop index           | Remove an index                                | Low        |
| Add constraint       | Add a foreign key, unique, or check constraint | Medium     |
| Add default          | Set a default value for an existing column     | Low        |

Identify the risk level and plan accordingly. High and critical operations require special care in Steps 3 and 4.

### Step 3: Generate the Forward Migration

Write the SQL for the forward (up) migration. Follow these guidelines:

**Adding tables**:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

**Adding columns**:
```sql
ALTER TABLE users ADD COLUMN last_login TIMESTAMP;
```

**Adding NOT NULL columns to populated tables**:
```sql
-- Step 1: Add column as nullable
ALTER TABLE users ADD COLUMN role TEXT;
-- Step 2: Backfill existing rows
UPDATE users SET role = 'member' WHERE role IS NULL;
-- Step 3: In databases that support it, alter to NOT NULL
-- (SQLite does not support ALTER COLUMN; a table rebuild is needed)
```

**Dropping columns** (when the database supports it):
```sql
ALTER TABLE users DROP COLUMN legacy_field;
```

**Creating indexes on large tables**:
```sql
-- Use CONCURRENTLY if available (PostgreSQL) to avoid locking
CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders(user_id);
```

Include comments in the SQL explaining the rationale for each statement.

### Step 4: Generate the Rollback Migration

Write the SQL for the rollback (down) migration that reverses the forward migration:

**For table creation**: Drop the table.
```sql
DROP TABLE IF EXISTS users;
```

**For column addition**: Drop the column.
```sql
ALTER TABLE users DROP COLUMN last_login;
```

**For column removal**: This is the difficult case. The rollback must re-add the column, but the data is lost. Document this clearly:
```sql
-- WARNING: Data in the dropped column cannot be restored.
ALTER TABLE users ADD COLUMN legacy_field TEXT;
```

**For type changes**: Reverse the type change. Note that data loss may occur if the types are incompatible.

For every rollback, include a comment about whether data loss occurs.

### Step 5: Validate the Forward Migration

Test the migration against a database instance.

**For SQLite via eMCP**:
- Use `sql_execute` to run the forward migration statements.
- Use `sql_describe_table` to verify the schema matches expectations.
- Run a few sample queries to confirm the migration works with existing data patterns.

**For other databases**:
- Generate the migration script as a file.
- If a test database is available, execute against it using shell tools.
- If no test database is available, review the SQL manually and note that production validation is pending.

Check for:
- Syntax errors.
- Constraint violations with existing data.
- Index creation on large tables (estimate time based on row count).

### Step 6: Validate the Rollback

After applying the forward migration, test the rollback:

- Apply the rollback migration using `sql_execute`.
- Use `sql_describe_table` to verify the schema matches the original state from Step 1.
- Compare the "before" snapshot from Step 1 with the post-rollback state.

If the rollback does not restore the schema exactly, document the discrepancies (e.g., data loss from dropped columns, auto-increment counters that do not reset).

### Step 7: Review for Risks

Evaluate the migration for common risks:

**Data loss**:
- Does the migration drop any column or table that contains data?
- Does a type change truncate or lose precision?
- Is there a backfill step that may overwrite existing data?

**Performance on large tables**:
- Adding a column with a default value may rewrite the entire table (database-dependent).
- Creating an index on a large table may lock it for an extended period.
- Backfilling data may generate significant write I/O.

**Index considerations**:
- Are queries that filter on the new column going to need an index?
- Does the migration remove an index that existing queries depend on?
- Are there composite index opportunities?

**Constraint implications**:
- Adding a NOT NULL constraint may fail if existing rows contain NULL.
- Adding a UNIQUE constraint may fail if duplicates exist.
- Adding a FOREIGN KEY requires the referenced table and column to exist.

Document each risk and its mitigation in the migration review.

### Step 8: Write Migration Files

Save the migration following the project's migration framework conventions:

| Framework     | File Pattern                                      |
|---------------|---------------------------------------------------|
| Raw SQL       | `migrations/NNNN_description.sql`                 |
| Knex          | `migrations/YYYYMMDDHHMMSS_description.js`        |
| Sequelize     | `migrations/YYYYMMDDHHMMSS-description.js`        |
| Alembic       | `alembic/versions/xxxx_description.py`            |
| Django        | `app/migrations/NNNN_description.py`              |
| Rails         | `db/migrate/YYYYMMDDHHMMSS_description.rb`        |
| Prisma        | `prisma/migrations/YYYYMMDDHHMMSS_name/migration.sql` |
| Flyway        | `sql/V{N}__description.sql`                       |
| Diesel        | `migrations/YYYY-MM-DD-HHMMSS_name/up.sql` and `down.sql` |

Read existing migration files to detect the project's naming convention and numbering scheme. Follow the established pattern.

If the project uses an ORM with model definitions (Prisma, Django, Sequelize), generate the model change in addition to or instead of raw SQL, as appropriate.

## Note on Database Compatibility

This skill works directly with SQLite via the eMCP sql tools. For PostgreSQL, MySQL, SQL Server, and other databases, it generates SQL scripts for manual review and execution. The generated SQL follows ANSI SQL where possible, with database-specific notes where syntax differs (e.g., `AUTOINCREMENT` vs `SERIAL`, `CONCURRENTLY` index creation).
