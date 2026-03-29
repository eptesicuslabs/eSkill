---
name: e-graphql
description: "Reviews GraphQL schemas for naming conventions, type composition, query complexity, and deprecation handling. Use when designing GraphQL APIs, reviewing schema changes, or auditing implementations. Also applies when: 'review GraphQL schema', 'check schema best practices', 'GraphQL naming conventions', 'schema complexity'."
---

# GraphQL Schema Review

This skill reviews GraphQL schemas against naming conventions, type composition patterns, complexity considerations, and deprecation best practices. It produces an actionable report of findings grouped by category and severity.

## Prerequisites

- A GraphQL schema defined in `.graphql`/`.gql` files or in code (e.g., type-graphql, Nexus, Pothos, Strawberry, gqlgen).
- The eMCP filesystem, ast_search, and data_file_read servers available.

## Workflow

### Step 1: Locate Schema Definitions

Search the project for GraphQL schema sources. Use `filesystem` tools to find files by extension and convention:

| Source Type          | File Patterns                              |
|----------------------|--------------------------------------------|
| SDL files            | `*.graphql`, `*.gql`                       |
| Schema-first         | `schema.graphql`, `schema.gql`             |
| Code-first (JS/TS)   | Files importing `graphql-tag`, `@ObjectType`, `objectType`, `builder.queryType` |
| Code-first (Python) | Files importing `strawberry`, `graphene`, `ariadne` |
| Code-first (Go)     | `graph/schema.resolvers.go`, `*.graphqls`  |
| Generated            | `generated/schema.graphql`, `schema.generated.ts` |

For code-first schemas, use `egrep_search` to quickly locate files containing GraphQL decorator imports or schema builder patterns, then use `ast_search` to extract class decorators (type-graphql), builder patterns (Nexus, Pothos), or schema definition calls (graphene, Strawberry).

If a generated SDL file exists alongside code-first definitions, prefer reviewing the generated SDL as it represents the actual served schema.

### Step 2: Parse the Schema

Read each schema file using `data_file_read` or `filesystem` tools. Build an inventory of all schema elements:

**Types to catalog**:
- Object types (including Query, Mutation, Subscription root types)
- Input types
- Enum types
- Interface types
- Union types
- Scalar types (custom scalars)
- Directive definitions

For each type, record:
- Name
- Fields (with types, arguments, nullability)
- Description (if present)
- Deprecation annotations
- Interfaces implemented
- Directives applied

### Step 3: Check Naming Conventions

Validate naming against GraphQL community conventions:

| Element           | Convention         | Valid Example           | Invalid Example        |
|-------------------|--------------------|------------------------|------------------------|
| Object types      | PascalCase         | `UserProfile`          | `userProfile`, `user_profile` |
| Input types       | PascalCase + Input | `CreateUserInput`      | `CreateUser`, `createUserInput` |
| Enum types        | PascalCase         | `OrderStatus`          | `orderStatus`          |
| Enum values       | UPPER_SNAKE_CASE   | `IN_PROGRESS`          | `inProgress`, `in-progress` |
| Fields            | camelCase          | `firstName`            | `first_name`, `FirstName` |
| Arguments         | camelCase          | `userId`               | `user_id`              |
| Mutations         | camelCase verb     | `createUser`           | `userCreate`, `CreateUser` |
| Queries           | camelCase noun     | `user`, `users`        | `getUser`, `fetchUsers` |
| Subscriptions     | camelCase event    | `userCreated`          | `onUserCreated`        |
| Interfaces        | PascalCase         | `Node`, `Connection`   | `INode`, `node`        |
| Custom scalars    | PascalCase         | `DateTime`, `JSON`     | `dateTime`             |

Report deviations with the element location and the expected convention.

### Step 4: Analyze Type Composition

Review the schema's structural design for common patterns and anti-patterns:

**Relay connection pattern**: For paginated lists, check whether the schema follows the Relay specification:
- Connection types with `edges` and `pageInfo` fields.
- Edge types with `node` and `cursor` fields.
- PageInfo with `hasNextPage`, `hasPreviousPage`, `startCursor`, `endCursor`.
- If some list fields use connections and others return bare arrays, flag the inconsistency.

**Input type usage**:
- Mutations should accept input types rather than flat argument lists exceeding 3 arguments.
- Input types should not be reused across unrelated mutations if they have different required fields.
- Check for input types that duplicate object types field-for-field. These may indicate missing abstraction.

**Nullable vs non-nullable**:
- ID fields should be non-nullable (`ID!`).
- Required creation fields in input types should be non-nullable.
- List fields should clarify both list and item nullability (e.g., `[User!]!` vs `[User]`).
- Flag fields that are nullable without a clear reason, as overly permissive nullability complicates client code.

**Interface and union usage**:
- Types that share 3 or more identical fields may benefit from an interface.
- Union types should have at least 2 members.
- Check that all interface implementations include all interface fields.

### Step 5: Check for Missing Descriptions

GraphQL descriptions serve as API documentation. Check description coverage:

- Every object type should have a description.
- Every field on root types (Query, Mutation, Subscription) should have a description.
- Every argument should have a description.
- Every enum type and its values should have descriptions.
- Input type fields should have descriptions, especially for non-obvious fields.

Calculate coverage percentages:

| Element        | Described | Total | Coverage |
|----------------|-----------|-------|----------|
| Object types   | 12        | 15    | 80%      |
| Query fields   | 8         | 10    | 80%      |
| Mutation fields| 3         | 8     | 38%      |
| Enum values    | 20        | 30    | 67%      |
| Arguments      | 15        | 40    | 38%      |

Flag any root-level query or mutation field missing a description as an error.

### Step 6: Detect Circular References and Deep Nesting

Analyze the type graph for problematic patterns:

**Circular references**: Trace field types to detect cycles (e.g., User -> posts -> [Post] -> author -> User). Circular references are valid in GraphQL but require attention:
- Record all detected cycles and their depth.
- Flag cycles that lack a clear pagination or depth-limiting mechanism.

**Query depth potential**: Starting from each Query field, calculate the maximum possible nesting depth through object type fields. Flag paths that allow unbounded depth without pagination.

**Field fan-out**: Identify types with a large number of fields (more than 20). These may benefit from splitting into sub-types or using interfaces.

Present the findings as a reference table:

| Cycle Path                          | Depth | Pagination |
|-------------------------------------|-------|------------|
| User -> posts -> Post -> author     | 2     | Yes (Connection) |
| Comment -> replies -> Comment       | 1     | No         |
| Order -> items -> Product -> orders | 3     | Yes (limit arg) |

### Step 7: Analyze Query Complexity Considerations

Review whether the schema supports query complexity management:

- **Depth limiting**: Check if the server configuration or schema directives include depth limits.
- **Cost directives**: Check for `@cost` or `@complexity` directives on fields that trigger expensive operations (database joins, external API calls).
- **List size arguments**: Verify that list fields accept a `first`/`last` or `limit` argument to bound result sizes. Flag unbounded list fields.
- **Computed fields**: Identify fields that likely require computation or aggregation (e.g., `totalCount`, `averageRating`). These should be flagged for potential complexity impact.

### Step 8: Check Deprecation Handling

Review deprecated elements in the schema:

- Every `@deprecated` directive should include a `reason` argument explaining the deprecation.
- The reason should reference the replacement field or operation.
- Deprecated fields should not be used by other non-deprecated fields in the schema.
- Check for fields that appear abandoned (no description, generic names) but lack deprecation markers.

Report deprecation status:

| Deprecated Element       | Reason                              | Replacement          |
|--------------------------|-------------------------------------|----------------------|
| User.name                | "Use firstName and lastName instead"| User.firstName       |
| Query.allUsers           | "Use users connection instead"      | Query.users          |
| Mutation.removeUser      | No reason provided                  | Unknown              |

### Step 9: Generate Review Report

Produce a structured review report:

```
## GraphQL Schema Review

### Schema Overview
- Source: schema.graphql (SDL)
- Object types: 18
- Input types: 9
- Enum types: 5
- Interfaces: 2
- Unions: 1
- Custom scalars: 3
- Query fields: 12
- Mutation fields: 15
- Subscription fields: 3

### Naming Issues (7 findings)
1. ERROR: Input type "CreateUser" should be "CreateUserInput"
2. WARNING: Enum value "inProgress" on OrderStatus should be "IN_PROGRESS"
3. WARNING: Query field "getUsers" should be "users" (drop verb prefix)
...

### Composition Issues (4 findings)
1. WARNING: Query.users returns [User] but Query.orders uses OrderConnection.
   Standardize pagination approach.
2. INFO: Mutation createOrder accepts 5 arguments. Consider wrapping in
   CreateOrderInput.
...

### Description Coverage
| Element        | Coverage |
|----------------|----------|
| Object types   | 80%      |
| Query fields   | 80%      |
| Mutation fields| 38%      |
| Arguments      | 38%      |

### Complexity Concerns (2 findings)
1. WARNING: Comment.replies allows unbounded recursion with no depth limit
2. INFO: Product.reviews returns unbounded list (no limit argument)

### Deprecations (1 finding)
1. ERROR: Mutation.removeUser is @deprecated without a reason

### Summary
| Severity | Count |
|----------|-------|
| Error    | 3     |
| Warning  | 5     |
| Info     | 3     |
```

## Edge Cases

- **Schema stitching/federation**: For Apollo Federation or schema stitching setups, review each subgraph schema individually. Flag `@key`, `@external`, and `@provides` directives for correctness but do not treat them as naming violations.
- **Code-first without generated SDL**: If the schema is defined purely in code with no generated SDL, extract type information using `ast_search` on decorators and builder calls. The review will be less precise than SDL analysis.
- **Large schemas (100+ types)**: For very large schemas, focus the report on root type fields, recently changed types (via git history), and the highest-severity findings. Offer to deep-dive into specific areas on request.
- **Schema extensions**: Handle `extend type` directives by merging them with the base type before analysis.
- **Custom directives**: Do not flag custom directive usage as errors. Catalog them and note whether they have descriptions.

## Notes

- This skill reviews the schema definition. It does not execute queries or test resolvers. For resolver testing, use the e-contract skill.
- For REST API specifications, use the e-openapi skill instead.
- Schema review findings are recommendations, not rules. Some projects intentionally deviate from conventions (e.g., snake_case fields to match database columns). The user decides which findings to act on.

## Related Skills

- **e-surface** (eskill-coding): Run e-surface before this skill to identify all GraphQL endpoints and their usage patterns.
- **e-lint** (eskill-quality): Run e-lint alongside this skill to enforce naming and structural conventions in the GraphQL schema.
