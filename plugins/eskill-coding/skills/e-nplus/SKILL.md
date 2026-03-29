---
name: e-nplus
description: "Detects N+1 query patterns in ORM code by tracing loop structures containing database calls and suggests batch alternatives. Use when investigating slow queries, reviewing ORM code, or optimizing database access. Also applies when: 'find N+1 queries', 'why are there so many SQL queries', 'optimize database calls', 'detect query patterns'."
---

# N+1 Query Detector

This skill detects N+1 query patterns in ORM code by identifying loops that contain database calls, then suggests batch or eager-loading alternatives specific to the ORM in use. An N+1 pattern occurs when code executes one query to fetch a list of N items, then executes N additional queries (one per item) to fetch related data.

## Prerequisites

- A codebase using an ORM or database access layer.
- LSP server running for the project language (recommended).

## Core Pattern

The N+1 pattern has a consistent structure across all languages and ORMs:

```
items = query_all(Model)          -- 1 query
for item in items:                -- loop over N items
    related = query(Related,       -- N queries (1 per iteration)
                    where: item.id)
```

The fix is always one of:
1. **Eager loading**: Fetch related data in the original query using JOINs or subqueries.
2. **Batch loading**: Collect all IDs, then execute a single query with `WHERE id IN (...)`.
3. **Preloading**: Use the ORM's built-in preload/include mechanism.

## Workflow

### Step 1: Identify ORM and Database Access Layer

Use `fs_list` and `fs_read` to inspect manifest files and detect the ORM:

| File / Content                       | ORM             | Language   |
|--------------------------------------|-----------------|------------|
| package.json contains "@prisma/client"| Prisma          | TypeScript |
| package.json contains "sequelize"    | Sequelize       | JavaScript |
| package.json contains "typeorm"      | TypeORM         | TypeScript |
| package.json contains "drizzle-orm"  | Drizzle         | TypeScript |
| requirements.txt contains "SQLAlchemy"| SQLAlchemy     | Python     |
| Django project (settings.py INSTALLED_APPS) | Django ORM | Python     |
| Gemfile contains "activerecord"      | ActiveRecord    | Ruby       |
| go.mod contains "gorm.io/gorm"       | GORM            | Go         |
| Cargo.toml contains "diesel"         | Diesel          | Rust       |
| Cargo.toml contains "sqlx"          | SQLx            | Rust       |

Also detect raw database access patterns (direct SQL queries through database drivers) by using `egrep_search` from the eMCP egrep server to find `db.query`, `connection.execute`, `cursor.execute`, and similar patterns across the codebase. The trigram-indexed search is significantly faster than `fs_search` for this kind of cross-codebase pattern matching.

### Step 2: Search for Loop Structures

Use `ast_search` from the eMCP AST server to find all loop constructs in the target files:

**Patterns to search by language**:

| Language   | Loop Patterns                                        |
|------------|------------------------------------------------------|
| JavaScript | `for...of`, `for...in`, `forEach`, `.map(`, `.flatMap(` |
| TypeScript | Same as JavaScript                                   |
| Python     | `for ... in`, list comprehensions, generator expressions |
| Ruby       | `.each`, `.map`, `.collect`, `.flat_map`, `for...in` |
| Go         | `for _, item := range`                               |
| Rust       | `for item in`, `.iter().map(`, `.for_each(`          |

If the user specifies target files, search only those. Otherwise, use `egrep_search` to search the full codebase for ORM call patterns, prioritizing results in `services/`, `controllers/`, `handlers/`, `routes/`, and `resolvers/` directories, as these are the most common locations for data-fetching logic.

### Step 3: Detect Database Calls Inside Loops

For each loop found in Step 2, analyze the loop body to determine whether it contains a database call. Use `ast_search` and `lsp_references` to trace function calls within the loop body.

**ORM-specific database call patterns**:

| ORM          | Patterns Indicating a Query                          |
|--------------|------------------------------------------------------|
| Prisma       | `.findUnique(`, `.findFirst(`, `.findMany(`, `.count(` |
| Sequelize    | `.findOne(`, `.findAll(`, `.findByPk(`, `.count(`    |
| TypeORM      | `.findOne(`, `.find(`, `.findOneBy(`, `.createQueryBuilder(` |
| Drizzle      | `db.select(`, `db.query.`                            |
| SQLAlchemy   | `session.query(`, `session.execute(`, `select(`      |
| Django ORM   | `.objects.get(`, `.objects.filter(`, `.objects.all()` |
| ActiveRecord | `.find(`, `.where(`, `.find_by(`, `.pluck(`          |
| GORM         | `.First(`, `.Find(`, `.Where(`, `.Preload(`          |
| Diesel       | `.filter(`, `.find(`, `.load(`                       |
| Raw SQL      | `db.query(`, `cursor.execute(`, `connection.execute(` |

A match occurs when:
1. A loop iterates over a collection obtained from a database query.
2. The loop body contains a database call that uses data from the current iteration (e.g., `item.id`) as a filter parameter.

Also check for indirect N+1 patterns where the database call is inside a function called from the loop body. Use `lsp_references` to trace one level of function calls. Deeper call chains are noted as potential issues but not confirmed.

### Step 4: Classify Each Finding

For each detected N+1 pattern, determine:

| Attribute          | Description                                          |
|--------------------|------------------------------------------------------|
| Location           | File path, line number of the loop                   |
| Outer query        | The query that fetches the list (the "1" query)      |
| Inner query        | The query inside the loop (the "N" queries)          |
| Relationship       | How the inner query relates to the outer (FK, join key) |
| Estimated impact   | N times the inner query cost (based on collection size if determinable) |
| Confidence         | High (direct ORM call in loop), Medium (function call containing ORM call), Low (pattern match only) |

Confidence levels:

- **High**: The database call is directly visible in the loop body with the iteration variable used as a parameter.
- **Medium**: The loop body calls a function that contains a database call (traced via `lsp_references`).
- **Low**: The pattern matches structurally but the call chain could not be fully traced (e.g., dynamic dispatch, callbacks).

### Step 5: Generate ORM-Specific Fixes

For each finding, produce a fix using the ORM's native mechanism for batch loading.

**Prisma**:
```
Before (N+1):
  const users = await prisma.user.findMany();
  for (const user of users) {
    const posts = await prisma.post.findMany({ where: { authorId: user.id } });
  }

After (eager loading via include):
  const users = await prisma.user.findMany({
    include: { posts: true }
  });
```

**Sequelize**:
```
Before (N+1):
  const users = await User.findAll();
  for (const user of users) {
    const posts = await Post.findAll({ where: { authorId: user.id } });
  }

After (eager loading):
  const users = await User.findAll({ include: [Post] });
```

**SQLAlchemy**:
```
Before (N+1):
  users = session.query(User).all()
  for user in users:
      posts = session.query(Post).filter(Post.author_id == user.id).all()

After (joinedload):
  from sqlalchemy.orm import joinedload
  users = session.query(User).options(joinedload(User.posts)).all()

After (selectinload -- separate SELECT with IN clause):
  from sqlalchemy.orm import selectinload
  users = session.query(User).options(selectinload(User.posts)).all()
```

**Django ORM**:
```
Before (N+1):
  users = User.objects.all()
  for user in users:
      posts = Post.objects.filter(author=user)

After (prefetch_related -- separate query with IN):
  users = User.objects.prefetch_related('posts').all()

After (select_related -- JOIN, for ForeignKey/OneToOne only):
  posts = Post.objects.select_related('author').all()
```

**ActiveRecord**:
```
Before (N+1):
  users = User.all
  users.each do |user|
    posts = user.posts
  end

After (includes):
  users = User.includes(:posts).all
```

**GORM**:
```
Before (N+1):
  var users []User
  db.Find(&users)
  for _, user := range users {
      var posts []Post
      db.Where("author_id = ?", user.ID).Find(&posts)
  }

After (Preload):
  var users []User
  db.Preload("Posts").Find(&users)
```

**Batch loading (ORM-agnostic fallback)**:
```
Before:
  for item in items:
      related = query(where: id == item.related_id)

After:
  ids = [item.related_id for item in items]
  related_map = {r.id: r for r in query(where: id IN ids)}
  for item in items:
      related = related_map[item.related_id]
```

### Step 6: Check for Already-Optimized Patterns

Before reporting a finding, verify it is not already handled:

- **Eager loading already present**: If the outer query already includes `include`, `joinedload`, `prefetch_related`, `Preload`, or `includes` for the relationship in question, the loop access is not an N+1.
- **Dataloader pattern**: In GraphQL resolvers, a DataLoader batches requests automatically. If a DataLoader is registered for the relationship, the pattern is already optimized.
- **Caching layer**: If the loop body reads from a cache (Redis, in-memory map) rather than the database, it may not produce N+1 queries at the database level. Flag as low confidence.
- **Small fixed-size collections**: If the loop iterates over a small, fixed-size collection (e.g., an enum of 3-5 values), the N+1 has minimal impact. Report but mark as low priority.

Use `ast_search` to check for these patterns in the same scope as the detected loop.

### Step 7: Generate the Report

Produce a structured report listing all findings, sorted by estimated impact (highest first):

```
## N+1 Query Detection Report

### Summary
- Files scanned: 45
- N+1 patterns found: 7
- High confidence: 4
- Medium confidence: 2
- Low confidence: 1
- Estimated excess queries (per request): ~350

### Findings

#### 1. [HIGH] src/services/order-service.ts:45

Loop: `for (const order of orders)` (line 45-52)
Outer query: `prisma.order.findMany()` (line 43)
Inner query: `prisma.user.findUnique({ where: { id: order.userId } })` (line 47)
Relationship: Order.userId -> User.id (foreign key)
Estimated impact: ~100 extra queries (based on typical order count)

**Fix**:
```typescript
const orders = await prisma.order.findMany({
  include: { user: true }
});
```

#### 2. [HIGH] src/resolvers/post-resolver.py:23

Loop: `for post in posts` (line 23-28)
Outer query: `session.query(Post).all()` (line 21)
Inner query: `session.query(Comment).filter(Comment.post_id == post.id)` (line 25)
Relationship: Comment.post_id -> Post.id (foreign key)
Estimated impact: ~200 extra queries

**Fix**:
```python
posts = session.query(Post).options(selectinload(Post.comments)).all()
```

[... additional findings ...]
```

### Step 8: Suggest Monitoring

After fixes are applied, suggest ways to verify the improvement and prevent regressions:

**Query counting in tests**:
- Node.js: Use Prisma query events or Sequelize logging to count queries per test.
- Python: Use Django `assertNumQueries` or SQLAlchemy event listeners.
- Ruby: Use ActiveRecord query counter gems like `bullet`.
- Go: Use GORM logger in test mode to count queries.

**Runtime detection**:
- Recommend installing the `bullet` gem for Rails projects (detects N+1 at runtime).
- Recommend enabling query logging in test environments to catch regressions.
- For Django, suggest `django-debug-toolbar` or `nplusone` package.

## Edge Cases

- **Nested N+1**: A loop inside a loop, each containing a query (N*M+N+1 pattern). Report the inner loop as the primary finding with a note about the nesting depth.
- **Conditional queries**: A database call inside an `if` block within a loop. Report as N+1 but note that the actual query count depends on the condition frequency.
- **Async iteration**: `for await ... of` or async generators that yield database results. These are still N+1 if each iteration awaits a separate query.
- **ORM lazy loading**: Accessing a relationship attribute that triggers an implicit query (e.g., `user.posts` in Django/ActiveRecord without prefetching). Use `ast_search` to find attribute accesses on model instances inside loops, cross-referencing with the model's relationship definitions.

## Related Skills

- **e-perf** (eskill-coding): Follow up with e-perf after this skill to assess the broader performance impact of detected N+1 queries.
- **e-migrate** (eskill-coding): Follow up with e-migrate after this skill to apply query optimizations and schema changes that fix N+1 patterns.
