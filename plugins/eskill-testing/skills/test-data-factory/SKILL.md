---
name: test-data-factory
description: "Generates test data factory functions and fixture files from schema analysis with realistic, consistent data per entity type. Use when setting up test data, creating seed scripts, or establishing fixture conventions. Also applies when: 'generate test fixtures', 'create test data', 'seed the database', 'factory functions for tests'."
---

# Test Data Factory

This skill analyzes database schemas and model definitions to generate factory functions that produce realistic, consistent test data. Factories handle entity relationships, enforce constraints, and support both unit test fixtures and database seed scripts.

## Prerequisites

- A project with defined data models (ORM schemas, database migrations, or raw SQL table definitions).
- A test framework in place (or a target test framework identified).

## Workflow

### Step 1: Locate Schema Definitions

Identify where data models are defined. Use `filesystem` tools (list_directory) to scan for schema files, then use `ast_search` from the eMCP AST server to extract model structures:

| Schema Type       | File Pattern                        | Search Strategy                     |
|-------------------|-------------------------------------|-------------------------------------|
| Prisma            | `prisma/schema.prisma`              | Read file directly                  |
| Django            | `*/models.py`                       | ast_search for class definitions    |
| SQLAlchemy        | `*/models.py`, `*/models/*.py`      | ast_search for class definitions    |
| TypeORM           | `*/entity/*.ts`, `*/*.entity.ts`    | ast_search for @Entity decorators   |
| Sequelize         | `*/models/*.js`                     | ast_search for define() calls       |
| Drizzle           | `*/schema.ts`, `*/schema/*.ts`      | ast_search for table definitions    |
| Raw SQL           | `migrations/*.sql`, `schema.sql`    | Parse CREATE TABLE statements       |
| Mongoose          | `*/models/*.ts`, `*/schemas/*.ts`   | ast_search for Schema definitions   |

Use `lsp_symbols` from the eMCP LSP server to get a structural overview of model files: class names, field names, and type annotations.

### Step 2: Extract Entity Definitions

For each model, extract the complete field specification. Use `ast_search` to parse field definitions and `sql` tools (sql_list_tables, sql_describe_table) if a live database is available.

Build an entity map with the following information per field:

| Property       | Source                                  | Example                     |
|----------------|-----------------------------------------|-----------------------------|
| Name           | Field name in model                     | `email`                     |
| Type           | Type annotation or column type          | `string`, `varchar(255)`    |
| Required       | Nullable annotation or NOT NULL         | `true`                      |
| Unique         | Unique constraint or annotation         | `true`                      |
| Default        | Default value if specified              | `now()`                     |
| Max length     | Length constraint                       | `255`                       |
| Enum values    | Enum type definition                    | `['active', 'inactive']`   |
| Foreign key    | Relation annotation or FK constraint    | `userId -> User.id`         |
| Validation     | Validators or check constraints         | `min: 0, max: 100`         |

For Prisma schemas, read the file with `filesystem` tools and parse model blocks:
```prisma
model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  role      Role     @default(USER)
  posts     Post[]
  createdAt DateTime @default(now())
}
```

For Django models, use `ast_search` to find class attributes that are Field instances:
```python
class User(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
```

### Step 3: Map Relationships

Identify all relationships between entities using the foreign key and relation information from Step 2.

Build a relationship table:

| Parent Entity | Child Entity | Relationship | FK Field       | Cascade Rule |
|---------------|-------------|--------------|----------------|--------------|
| User          | Post        | One-to-Many  | post.authorId  | CASCADE      |
| Post          | Comment     | One-to-Many  | comment.postId | CASCADE      |
| User          | Profile     | One-to-One   | profile.userId | CASCADE      |
| Post          | Tag         | Many-to-Many | post_tags join | --           |

Determine the creation order: entities with no foreign keys first, then entities that depend on them. This is a topological sort of the dependency graph.

Use `ast_search` to find relation annotations (@ManyToOne, ForeignKey, references, etc.) and `lsp_references` to trace cross-model references.

### Step 4: Design Factory Output Format

Determine the factory format based on the project's language and existing test conventions:

| Language | Factory Pattern                    | Library               |
|----------|------------------------------------|-----------------------|
| TS/JS    | Function returning typed object    | None or @faker-js     |
| TS/JS    | fishery or factory.ts class        | fishery               |
| Python   | factory_boy Factory class          | factory_boy           |
| Python   | Function returning dict            | Faker                 |
| Rust     | Builder pattern struct             | fake crate            |
| Go       | Function returning struct          | gofakeit              |
| Java     | Builder class or Instancio         | Instancio             |

Check for existing factory patterns in the test directory using `filesystem` tools. If the project already uses a factory library, generate factories that match the existing style. If no factories exist, use a plain function pattern that has no external dependencies beyond an optional faker library.

### Step 5: Generate Realistic Data Generators

Map each field type to an appropriate data generator. Use field names and types together for semantic matching:

| Field Name Pattern   | Field Type    | Generator                       | Example Output            |
|----------------------|---------------|---------------------------------|---------------------------|
| email                | string        | faker.internet.email()          | `jane.doe@example.com`   |
| name, firstName      | string        | faker.person.firstName()        | `Jane`                    |
| lastName, surname    | string        | faker.person.lastName()         | `Doe`                     |
| phone, tel           | string        | faker.phone.number()            | `+1-555-0123`            |
| url, website         | string        | faker.internet.url()            | `https://example.com`    |
| address, street      | string        | faker.location.streetAddress()  | `123 Main St`            |
| city                 | string        | faker.location.city()           | `Portland`               |
| zip, postalCode      | string        | faker.location.zipCode()        | `97201`                  |
| price, amount, cost  | number/decimal| faker.number.float(min,max,2)   | `29.99`                  |
| age                  | integer       | faker.number.int(18,99)         | `34`                     |
| quantity, count      | integer       | faker.number.int(1,100)         | `5`                      |
| description, bio     | text          | faker.lorem.paragraph()         | (paragraph text)          |
| title, subject       | string        | faker.lorem.sentence()          | (sentence text)           |
| createdAt, updatedAt | datetime      | faker.date.recent()             | `2025-03-20T10:30:00Z`  |
| isActive, isPublished| boolean       | true (default for happy path)   | `true`                   |
| slug                 | string        | Derived from title field        | `my-first-post`          |
| uuid, id (uuid type) | uuid          | faker.string.uuid()             | `a1b2c3d4-...`           |
| enum fields          | enum          | First enum value                | `'active'`               |

For fields with no semantic match, fall back to type-based defaults: random string for string, random integer for int, current date for datetime.

### Step 6: Handle Relationships in Factories

Factories must produce valid related data. Implement these strategies:

**Inline creation**: For required one-to-one or many-to-one relations, the child factory calls the parent factory:
```typescript
function createPost(overrides?: Partial<Post>): Post {
  return {
    id: faker.number.int(),
    title: faker.lorem.sentence(),
    authorId: createUser().id,   // creates a User automatically
    ...overrides,
  };
}
```

**Override support**: Allow callers to provide a specific related entity:
```typescript
const author = createUser({ name: 'Alice' });
const post = createPost({ authorId: author.id });
```

**Collection factories**: For one-to-many, provide a helper to create N related entities:
```typescript
function createUserWithPosts(postCount = 3): User & { posts: Post[] } {
  const user = createUser();
  const posts = Array.from({ length: postCount }, () =>
    createPost({ authorId: user.id })
  );
  return { ...user, posts };
}
```

**Many-to-many**: Generate join records separately:
```typescript
function createPostWithTags(tagCount = 2): { post: Post; tags: Tag[] } {
  const post = createPost();
  const tags = Array.from({ length: tagCount }, () => createTag());
  return { post, tags };
}
```

### Step 7: Generate Seed Scripts

Create database seed scripts that use the factories to populate a development or test database.

Use `filesystem` tools to write the seed file in the appropriate location:

| Framework  | Seed Location                  | Execution Command              |
|------------|--------------------------------|--------------------------------|
| Prisma     | `prisma/seed.ts`               | `npx prisma db seed`           |
| Django     | `management/commands/seed.py`  | `python manage.py seed`        |
| SQLAlchemy | `scripts/seed.py`              | `python scripts/seed.py`       |
| TypeORM    | `src/seeds/seed.ts`            | `npx ts-node src/seeds/seed.ts`|
| Rails      | `db/seeds.rb`                  | `rails db:seed`                |

The seed script should:
1. Clear existing test data (with a safety check for production databases).
2. Create entities in dependency order (users before posts before comments).
3. Create a realistic but small dataset (10-50 records per entity type).
4. Log what was created for verification.

### Step 8: Write Factory Files

Use `filesystem` tools to write the factory files to the project. Place them according to project conventions:

| Convention                  | Path                                |
|-----------------------------|-------------------------------------|
| Dedicated factories dir     | `test/factories/user.factory.ts`    |
| Co-located with tests       | `test/helpers/factories.ts`         |
| Python test package         | `tests/factories/user_factory.py`   |
| Single factory file         | `test/factory.ts`                   |

Use `data_file` tools (data_file_write) for JSON fixture files if the project uses static fixtures rather than dynamic factories.

Include a barrel export file (index.ts or __init__.py) that re-exports all factories for convenient importing.

## Edge Cases

- **Circular references**: If entity A references entity B and B references A, break the cycle by making one reference optional and defaulting it to null in the factory. Document the cycle for the developer.
- **Unique constraints**: For fields with unique constraints (email, username, slug), use sequential counters or UUID suffixes to avoid collisions when creating multiple entities: `user-1@test.com`, `user-2@test.com`.
- **Polymorphic models**: If a model uses single-table inheritance or discriminator columns, create separate factory variants per subtype.
- **JSON or JSONB fields**: Generate a sensible default object structure based on any TypeScript interface or Python TypedDict that describes the field's shape. If no type information exists, default to an empty object.
- **Encrypted or hashed fields**: For password fields, use a pre-computed hash of a known test password (e.g., `password123`) rather than calling the hash function in the factory. Document the test password.
- **Large text or blob fields**: Use short placeholder content in factories. Tests that need specific large content should override the field explicitly.
- **Database-generated fields**: Omit auto-increment IDs, timestamps with database defaults, and computed columns from the factory output unless the caller explicitly provides them.

## Related Skills

- **integration-test-generation** (eskill-coding): Follow up with integration-test-generation after this skill to use the generated test data in integration test scenarios.
- **e2e-orchestration** (eskill-testing): Follow up with e2e-orchestration after this skill to supply test data to end-to-end test workflows.
