---
name: e-testgen
description: "Generates test file skeletons by inspecting source code via LSP and AST. Use when adding tests to untested files, bootstrapping a test suite, or expanding coverage. Also applies when: 'scaffold tests for this file', 'generate test stubs', 'create unit tests', 'need tests for this code'."
---

# Test Scaffolding

This skill generates test file skeletons by inspecting the code under test via LSP and AST tools, detecting the project's test framework, and producing well-structured test cases following project conventions.

## Prerequisites

- Source file(s) to generate tests for.
- A test framework installed in the project (or a preference for one).

## Workflow

### Step 1: Identify the Target File(s)

Determine which source files need test scaffolds. Acceptable inputs:

- A single file path (e.g., `src/services/auth.ts`).
- A directory (e.g., `src/services/` -- generate scaffolds for all files in the directory).
- A list of files (e.g., files changed in a recent commit).

For directories, use `fs_list` to enumerate files. Filter out non-source files (configs, assets, type definitions that contain no logic).

### Step 2: Extract Exported Symbols with LSP

For each target file, use `lsp_symbols` from the eMCP LSP server to extract the public interface:

- **Functions**: Name, parameters, return type.
- **Classes**: Name, constructor parameters, public methods.
- **Constants/Variables**: Name, type, whether exported.
- **Type aliases and interfaces**: Name and structure (for understanding parameter types).

Focus on exported symbols. Private/internal functions should only be tested indirectly through the public API unless the user explicitly requests otherwise.

### Step 3: Analyze Function Signatures with AST

Use `ast_search` from the eMCP AST server to get detailed information that LSP may not fully expose:

- **Parameter types and defaults**: Understand what inputs each function expects.
- **Return type**: Determine what the test should assert against.
- **Thrown exceptions**: Search for throw statements to know what error cases to test.
- **Conditional branches**: Count branches to estimate the number of test cases needed.
- **Dependencies**: Identify imported modules that may need mocking.

### Step 4: Detect the Test Framework

Use the following decision table to detect the test framework:

| Check                                         | Framework   |
|-----------------------------------------------|-------------|
| package.json contains "vitest"                | Vitest      |
| package.json contains "jest"                  | Jest        |
| package.json contains "mocha"                 | Mocha       |
| package.json contains "@playwright/test"      | Playwright  |
| pyproject.toml contains "pytest"              | pytest      |
| requirements.txt contains "pytest"            | pytest      |
| Cargo.toml exists                             | Rust #[test]|
| go.mod exists                                 | Go testing  |
| build.gradle or pom.xml contains "junit"      | JUnit       |
| No framework detected                         | Ask user    |

Read the appropriate manifest file using `data_file_read` from the eMCP data-file server or `fs_read`.

Also check for test configuration files that indicate additional settings:
- `jest.config.*` or `vitest.config.*` for JS/TS.
- `pytest.ini`, `pyproject.toml [tool.pytest]`, or `conftest.py` for Python.
- `Cargo.toml [dev-dependencies]` for Rust.

### Step 5: Generate the Test File Structure

Produce a test file with the following structure:

**Imports section**:
- Import the test framework utilities (describe, it, expect, test, etc.).
- Import the module under test.
- Import any mocking utilities needed.

**Describe blocks**:
- One `describe` block per class or logical group of functions.
- Nested `describe` for methods within a class.

**Test cases**:
- One or more `it`/`test` blocks per function, covering the categories in Step 6.

**Setup and teardown**:
- Add `beforeEach`/`afterEach` if the class requires instantiation or cleanup.
- Add `beforeAll`/`afterAll` if shared resources are needed.

Example structure for a TypeScript file using Vitest:

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { AuthService } from '../src/services/auth';

describe('AuthService', () => {
  let service: AuthService;

  beforeEach(() => {
    service = new AuthService();
  });

  describe('authenticate', () => {
    it('should return a token for valid credentials', () => {
      // Arrange
      // Act
      // Assert
    });

    it('should throw AuthError for invalid credentials', () => {
      // Arrange
      // Act & Assert
    });

    it('should handle empty username', () => {
      // Arrange
      // Act & Assert
    });
  });
});
```

### Step 6: Generate Test Cases per Function

For each function, generate test cases in these categories:

**Happy path**:
- Call the function with valid, typical inputs.
- Assert the expected return value or side effect.

**Edge cases**:
- Null or undefined parameters.
- Empty strings, empty arrays, empty objects.
- Boundary values (0, -1, MAX_INT, empty collections).
- Single-element collections.

**Error cases**:
- Invalid input types (if the language is dynamically typed).
- Inputs that should trigger thrown exceptions.
- Network or I/O failures (if the function performs external calls -- mock the dependency to simulate failure).

**Async behavior** (if applicable):
- Verify the function returns a promise.
- Test resolved and rejected cases.
- Test timeout behavior if relevant.

Mark each generated test body with a `// TODO: implement` comment to indicate that the developer must fill in the actual assertions.

### Step 7: Place the Test File

Follow the project's existing test file convention. Determine placement by checking for existing patterns:

| Pattern                         | Example                              |
|---------------------------------|--------------------------------------|
| Co-located `__tests__/` dir     | `src/services/__tests__/auth.test.ts`|
| Separate `test/` directory      | `test/services/auth.test.ts`         |
| Co-located with `.test.` suffix | `src/services/auth.test.ts`          |
| Co-located with `.spec.` suffix | `src/services/auth.spec.ts`          |
| Python `tests/` directory       | `tests/test_auth.py`                 |
| Rust inline `#[cfg(test)]`      | Same file, `mod tests` block         |
| Go `_test.go` suffix            | `auth_test.go` in same package       |

Search for existing test files using `fs_search` (filename mode) and `fs_list` to detect which convention the project uses. If multiple conventions exist, prefer the one used most recently (by file modification date).

If no existing test files are found, default to a `__tests__/` directory for JavaScript/TypeScript, `tests/` for Python, and co-located for Go and Rust.

## Notes

- The generated scaffold is a starting point. Developers must fill in the actual test logic.
- For complex functions with many dependencies, the scaffold includes mock setup boilerplate but does not guess mock return values.
- If the source file has no exports, report this to the user and suggest testing through the module's public entry point instead.

## Edge Cases

- **Files with no exports**: A file that executes side effects on import (e.g., registering global middleware) has no testable exports. Report this and suggest testing through the module that imports it.
- **Heavily mocked functions**: Functions with 5+ dependencies require extensive mock setup. Generate the mock boilerplate but flag the function as a candidate for refactoring to reduce coupling.
- **Generic and overloaded functions**: TypeScript generics or Python overloads need multiple test cases covering different type instantiations. Generate one test per significant type variant.
- **Async generators and iterators**: Async generator functions require special test patterns (collecting yielded values, testing early termination). Detect these and generate appropriate async iteration test scaffolds.
- **Private/unexported functions**: Functions not exported from the module cannot be tested directly. Suggest testing them indirectly through the public API or recommending export if they warrant direct testing.

## Related Skills

- **e-integ** (eskill-coding): Follow up with e-integ after this skill to extend unit test scaffolds into integration tests.
- **e-threshold** (eskill-coding): Follow up with e-threshold after this skill to verify the new tests meet project coverage targets.
