---
name: e-proptest
description: "Guides property-based testing across languages by identifying testable properties and generating PBT tests. Use when writing tests for serialization, parsing, normalization, or validation logic. Also applies when: 'property based test', 'roundtrip test', 'fuzz my code', 'idempotent test', 'generative testing', 'test with random inputs'."
---

# Property-Based Testing Guide

This skill identifies code patterns where property-based testing (PBT) provides stronger coverage than example-based tests, selects appropriate properties, and generates tests using the project's PBT library.

PBT generates hundreds of random inputs and checks that invariant properties always hold. Where example tests check "does f(3) return 9?", PBT checks "for ALL x, does f(f_inverse(x)) == x?". This catches edge cases that hand-picked examples miss.

## Prerequisites

- A codebase with testable pure functions, serialization pairs, or normalization logic.
- A PBT library installed or installable (Hypothesis, fast-check, proptest, jqwik, or equivalent).
- The eMCP filesystem, fs_search, ast_search, and test_run servers available.

## When to Use

Invoke this skill when you detect any of these patterns in code under test:

| Pattern | Property | Priority |
|---------|----------|----------|
| encode/decode, serialize/deserialize, toJSON/fromJSON | Roundtrip | HIGH |
| Pure functions (no side effects) | Multiple | HIGH |
| Validators (is_valid, validate, check_*) | Valid after normalize | MEDIUM |
| Sorting, ordering, comparators | Idempotence + ordering | MEDIUM |
| Normalization (normalize, sanitize, clean, format) | Idempotence | MEDIUM |
| Builder/factory patterns | Output invariants | LOW |

## When NOT to Use

- Simple CRUD without transformation logic
- UI/presentation logic
- Integration tests requiring external services
- Prototyping where requirements are fluid
- User explicitly requests example-based tests only

## Property Catalog

Use this reference to select the right property for the code pattern:

| Property | Formula | Use Case |
|----------|---------|----------|
| Roundtrip | `decode(encode(x)) == x` | Serialization, conversion pairs |
| Idempotence | `f(f(x)) == f(x)` | Normalization, formatting, sorting |
| Invariant | Property holds before and after | Any transformation |
| Commutativity | `f(a, b) == f(b, a)` | Binary/set operations |
| Associativity | `f(f(a,b), c) == f(a, f(b,c))` | Combining operations |
| Identity | `f(x, identity) == x` | Operations with neutral element |
| Inverse | `f(g(x)) == x` | encrypt/decrypt, compress/decompress |
| Oracle | `new_impl(x) == reference(x)` | Optimization, refactoring verification |
| Easy to verify | `is_sorted(sort(x))` | Complex algorithms |
| No exception | No crash on valid input | Baseline, weakest property |

**Strength hierarchy** (weakest to strongest):
No Exception < Type Preservation < Invariant < Idempotence < Roundtrip

Always push for the strongest applicable property. "No exception" alone is a smoke test, not a meaningful property test.

## Workflow

### Step 1: Identify Testable Patterns

Use `fs_search` from the eMCP search server and `ast_search` from the eMCP AST server to find candidate functions:

1. Search for serialization pairs:
   - Pattern: functions named `encode`/`decode`, `serialize`/`deserialize`, `toJSON`/`fromJSON`, `pack`/`unpack`, `marshal`/`unmarshal`
   - These are HIGH priority roundtrip candidates.

2. Search for normalization functions:
   - Pattern: functions named `normalize`, `sanitize`, `clean`, `canonicalize`, `format`, `trim`
   - These are MEDIUM priority idempotence candidates.

3. Search for validators:
   - Pattern: functions named `is_valid`, `validate`, `check_*`, `verify_*`
   - When paired with normalizers, test: `is_valid(normalize(x))` should always be true.

4. Search for pure functions:
   - Pattern: functions with no side effects (no I/O, no mutation of external state)
   - These accept multiple properties depending on their semantics.

Rank candidates by the priority table in "When to Use". Present the top 5-10 candidates to the user. Do not overwhelm with a complete list.

### Step 2: Detect Language and PBT Library

Use `filesystem` tools to check for existing PBT dependencies:

| Language | PBT Library | Detection |
|----------|------------|-----------|
| Python | Hypothesis | `hypothesis` in requirements.txt/pyproject.toml |
| JavaScript/TS | fast-check | `fast-check` in package.json |
| Rust | proptest | `proptest` in Cargo.toml |
| Java | jqwik | `jqwik` in pom.xml/build.gradle |
| Go | rapid | `rapid` in go.mod |
| C# | FsCheck | `FsCheck` in *.csproj |
| Haskell | QuickCheck | `QuickCheck` in *.cabal |

If the project already uses a PBT library, use it. If not, recommend the standard library for the language and present the install command. Wait for user confirmation before installing.

### Step 3: Select Properties for Each Candidate

For each candidate function from Step 1, select properties from the Property Catalog:

**Decision process:**

```
Is there a paired inverse function?
  YES -> Use Roundtrip property
  NO  -> Is the function idempotent (applying twice == applying once)?
    YES -> Use Idempotence property
    NO  -> Does the function preserve some measurable invariant?
      YES -> Use Invariant property (define the invariant)
      NO  -> Does a reference implementation exist?
        YES -> Use Oracle property
        NO  -> Use "Easy to verify" or "No exception" as baseline
```

For each selected property, write it as a one-line assertion before generating the test:
- Roundtrip: `assert decode(encode(x)) == x for all valid x`
- Idempotence: `assert normalize(normalize(s)) == normalize(s) for all strings s`
- Invariant: `assert len(sorted_list) == len(original_list) for all lists`

### Step 4: Design Input Generators

Most PBT libraries provide built-in generators for common types. Only create custom generators when built-in ones are insufficient.

**Built-in generators cover:**
- Integers (with range constraints)
- Strings (with alphabet/length constraints)
- Lists/arrays (with element type and size constraints)
- Floats (with NaN/infinity handling)
- Booleans
- Tuples/records of the above

**Custom generators are needed for:**
- Domain objects with construction invariants (e.g., a valid email address)
- Constrained combinations (e.g., a list and an index within its bounds)
- Recursive structures (e.g., trees, nested JSON)

When using custom generators, compose them from built-in generators using `map` and `filter` rather than writing random generation from scratch.

### Step 5: Generate the Test

Write the property-based test using the project's PBT library. Structure each test as:

1. **Arrange**: Define the generator (input strategy)
2. **Property**: State the invariant as a function that returns bool or asserts
3. **Settings**: Set example count (default: 100), max size, deadline

**Python (Hypothesis) example:**
```python
from hypothesis import given, strategies as st

@given(data=st.binary())
def test_roundtrip_encode_decode(data):
    assert decode(encode(data)) == data
```

**JavaScript (fast-check) example:**
```javascript
import fc from 'fast-check';

test('roundtrip encode/decode', () => {
  fc.assert(
    fc.property(fc.uint8Array(), (data) => {
      expect(decode(encode(data))).toEqual(data);
    })
  );
});
```

**Rust (proptest) example:**
```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn roundtrip_encode_decode(data: Vec<u8>) {
        assert_eq!(decode(&encode(&data)), data);
    }
}
```

Run the generated test with `test_run` from the eMCP test server to verify it passes. If it fails, proceed to Step 6.

### Step 6: Interpret Failures

When a property test fails, the library provides a minimal counterexample. Analyze it:

1. **Read the shrunk counterexample**: PBT libraries minimize failing inputs. The shrunk case is the simplest input that triggers the bug.
2. **Classify the failure**:
   - **Real bug**: The code violates the property. Fix the code.
   - **Property too strong**: The property assumes something the code does not guarantee (e.g., floating-point roundtrip with precision loss). Weaken the property.
   - **Generator produces invalid input**: The generator creates inputs outside the function's domain. Add `filter` or `assume` constraints.
3. **After fixing**: Re-run to confirm the fix and check that no new failures appear.

If the failure is a real bug, document it with the minimal counterexample before fixing.

### Step 7: Integrate into Test Suite

1. Place PBT tests alongside existing tests, following the project's test directory structure.
2. Add a comment linking the property to the code under test:
   ```
   # Property: roundtrip for MessageCodec.encode/decode
   # Any binary payload survives an encode-decode cycle unchanged.
   ```
3. Verify the full test suite still passes after adding PBT tests.
4. If PBT tests are slow (>30 seconds), consider:
   - Reducing the example count for CI (e.g., 50 instead of 100)
   - Using a fixed seed for deterministic CI runs
   - Running the full count only in nightly/extended test jobs

## Common Mistakes

- Testing trivial getters/setters with PBT (no value, use example tests)
- Writing "no exception" as the only property when stronger properties exist
- Missing paired operations (testing encode without decode)
- Ignoring type hints that make generator selection obvious
- Being pushy about PBT after the user declines
- Treating a failing property test as a bug without checking if the property itself is correct

## Rationalizations to Reject

Do not accept these shortcuts:

| Shortcut | Why it is wrong |
|----------|-----------------|
| "Example tests are good enough" | If serialization/parsing/normalization is involved, PBT finds edge cases examples miss |
| "The function is simple" | Simple functions with complex input domains (strings, floats, nested structures) benefit most |
| "We don't have time" | PBT tests are often shorter than comprehensive example suites |
| "It's too hard to write generators" | Most libraries have excellent built-in strategies; custom generators are rarely needed |
| "No crash means it works" | "No exception" is the weakest property; push for stronger guarantees |

## Edge Cases

- **Floating-point roundtrip**: Encode/decode cycles for floats may lose precision. Use approximate equality (`abs(a - b) < epsilon`) rather than exact equality for float-containing structures.
- **Non-deterministic serialization**: Some formats (JSON with unordered object keys, sets) do not guarantee byte-level roundtrip even when values are semantically equal. Compare deserialized values, not raw bytes.
- **Unicode edge cases in string generators**: Default string generators may produce surrogate pairs, null bytes, or RTL markers that the function under test does not handle. This is a feature, not a bug -- it exposes real edge cases. Only filter these if the function's contract explicitly excludes them.
- **Slow shrinking for complex types**: Custom generators for deeply nested structures can cause shrinking to take minutes. Set a `deadline` or `max_shrinks` limit to avoid CI timeouts while still getting a useful counterexample.
- **Stateful PBT for protocol testing**: For APIs with state (create -> update -> delete), stateless PBT is insufficient. Use stateful PBT (Hypothesis stateful testing, fast-check model-based) to test operation sequences.

## Related Skills

- **e-testgen** (eskill-coding): Use e-testgen to scaffold example-based tests first, then chain e-proptest to add property-based coverage for functions where PBT provides stronger guarantees.
- **e-mutate** (eskill-testing): Run e-mutate after e-proptest to verify that the generated property tests actually detect code mutations, confirming test effectiveness.
- **e-coverage** (eskill-testing): Run e-coverage after adding PBT tests to measure how much additional code coverage the property tests provide compared to example-based tests alone.
