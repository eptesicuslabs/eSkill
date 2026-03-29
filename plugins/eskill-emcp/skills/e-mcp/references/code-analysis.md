# Code Analysis Servers

## @emcp/server-ast (2 tools)

Structural code search and rewriting using ast-grep. Matches AST patterns rather than text regex, avoiding false positives from comments and strings. Requires `ast-grep` installed on the system.

### ast_search

Search code using AST patterns.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `pattern` | string | yes | | ast-grep pattern (e.g., `console.log($$$)`) |
| `path` | string | yes | | File or directory to search |
| `language` | string | no | | Language hint (auto-detected from extension) |

Pattern syntax uses `$NAME` for single-node wildcards and `$$$` for multi-node wildcards. Example patterns:
- `console.log($$$)` — find all console.log calls
- `if ($COND) { return $X }` — find guard clauses
- `fetch($URL)` — find fetch calls

### ast_rewrite

Rewrite code matching an AST pattern.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `pattern` | string | yes | | AST pattern to match |
| `rewrite` | string | yes | | Replacement pattern (can reference captured names) |
| `path` | string | yes | | File or directory to rewrite |
| `language` | string | no | | Language hint |

Example: pattern=`console.log($MSG)` rewrite=`logger.info($MSG)` replaces all console.log with logger.info.

---

## @emcp/server-lsp (5 tools)

Language Server Protocol client. Connects to the project's configured language server for type-aware code intelligence. All tools operate on file positions (line/character are 0-based).

### lsp_symbols

List all symbols defined in a source file.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `file` | string | yes | | Source file path |

Returns functions, classes, variables, interfaces, etc. with their positions and kinds.

### lsp_definition

Jump to the definition of a symbol.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `file` | string | yes | | Source file path |
| `line` | number | yes | | Line number (0-based) |
| `character` | number | yes | | Column number (0-based) |

### lsp_references

Find all references to a symbol.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `file` | string | yes | | Source file path |
| `line` | number | yes | | Line number (0-based) |
| `character` | number | yes | | Column number (0-based) |

### lsp_hover

Get type and documentation information at a position.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `file` | string | yes | | Source file path |
| `line` | number | yes | | Line number (0-based) |
| `character` | number | yes | | Column number (0-based) |

### lsp_diagnostics

Get compiler/linter diagnostics for a file.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `file` | string | yes | | Source file path |

---

## @emcp/server-egrep (4 tools)

Trigram-indexed instant code search. Builds an in-memory trigram index at startup for sub-millisecond searches. Extracts literal trigrams from regex patterns to eliminate non-matching files before running the full regex.

### egrep_search

Search code instantly using the trigram index.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `pattern` | string | yes | | Regex pattern |
| `caseSensitive` | boolean | no | | Case-sensitive matching |
| `maxResults` | number | no | | Maximum results |
| `contextLines` | number | no | | Lines of context around matches |
| `fileGlob` | string | no | | Filter by file glob pattern |

### egrep_search_files

Search for files by name.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `pattern` | string | yes | | Regex pattern against file paths |
| `maxResults` | number | no | | Maximum results |

### egrep_status

Show index state: files indexed, trigram count, memory usage, build time.

No parameters.

### egrep_reindex

Rebuild the trigram index from scratch.

No parameters.

---

## @emcp/server-test-runner (3 tools)

Execute test suites using the project's configured test framework (vitest, jest, pytest, cargo test, go test, etc.). The test command is configured in server config.

### test_run

Run the full test suite or filter by pattern.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `cwd` | string | yes | | Project working directory |
| `pattern` | string | no | | Test name/file pattern filter |
| `extraArgs` | string[] | no | [] | Additional arguments to the test runner |

### test_run_file

Run tests in a specific file.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `cwd` | string | yes | | Project working directory |
| `file` | string | yes | | Test file path |
| `extraArgs` | string[] | no | [] | Additional arguments |

### test_list_files

List test files matching the configured pattern.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `cwd` | string | yes | | Project working directory |
| `pattern` | string | no | | Override the default test file pattern |
