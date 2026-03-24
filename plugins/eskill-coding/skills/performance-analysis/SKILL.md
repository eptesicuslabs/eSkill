---
name: performance-analysis
description: "Guides performance investigation via profiling, benchmarking, and bottleneck identification. Use when an endpoint is slow, memory usage is high, or you need a baseline. Also applies when: 'why is this slow', 'profile this code', 'find the bottleneck', 'optimize performance', 'benchmark this'."
---

# Performance Analysis

This skill provides a structured approach to identifying and resolving performance problems. It covers profiling, benchmarking, bottleneck analysis, and optimization verification across multiple languages and runtime environments.

## Prerequisites

- A reproducible performance concern (slow endpoint, high memory usage, slow build, etc.).
- Access to the codebase and ability to run the application or its components.
- Profiling tools installed or installable for the target runtime.

## Workflow

### Step 1: Define the Performance Concern

Clearly articulate what is slow or resource-intensive:

| Concern Type    | Examples                                              | Key Metric          |
|-----------------|-------------------------------------------------------|---------------------|
| Latency         | Slow API endpoint, slow page load                     | Response time (ms)  |
| Throughput      | Low requests per second under load                    | RPS                 |
| Memory          | High memory usage, memory leaks                       | RSS, heap size      |
| CPU             | High CPU usage, process pegging cores                 | CPU percentage      |
| Build time      | Slow compilation, slow bundling                       | Wall clock time     |
| Startup time    | Slow application boot                                 | Time to ready       |
| I/O             | Slow file operations, slow database queries           | IOPS, query time    |

Document:
- What is the current performance (measured, not perceived)?
- What is the target performance?
- When did the problem start (if regression)?
- What is the reproduction scenario?

### Step 2: Establish a Baseline Measurement

Before making any changes, measure the current performance. This baseline is essential for verifying that optimizations have the intended effect.

Use shell tools from the eMCP shell server to run measurement commands:

**For HTTP endpoints**:
```
curl -o /dev/null -s -w "%{time_total}\n" http://localhost:3000/api/endpoint
```
Or use a benchmarking tool:
```
wrk -t2 -c10 -d10s http://localhost:3000/api/endpoint
ab -n 100 -c 10 http://localhost:3000/api/endpoint
```

**For scripts or functions**:
```
time node script.js
time python script.py
hyperfine 'node script.js'
```

**For memory**:
```
node --max-old-space-size=512 --expose-gc script.js
/usr/bin/time -v python script.py
```

Record the baseline numbers. Run measurements multiple times and note the median, min, and max to account for variance.

### Step 3: Profile Node.js Applications

For Node.js performance concerns, use the following profiling approaches:

**CPU profiling with --prof**:
```
node --prof app.js
# Exercise the slow path
node --prof-process isolate-*.log > processed.txt
```
The processed output shows a breakdown of time spent in each function.

**CPU profiling with clinic.js**:
```
npx clinic doctor -- node app.js
npx clinic flame -- node app.js
npx clinic bubbleprof -- node app.js
```
- `doctor`: General health check, identifies event loop delays and I/O issues.
- `flame`: Flame graph for CPU-intensive workloads.
- `bubbleprof`: Visualizes async operations for I/O-bound workloads.

**Heap profiling**:
```
node --inspect app.js
```
Connect Chrome DevTools to take heap snapshots and record allocation timelines.

**0x flame graphs**:
```
npx 0x app.js
```
Generates an interactive flame graph SVG.

### Step 4: Profile Python Applications

For Python performance concerns:

**CPU profiling with cProfile**:
```
python -m cProfile -o output.prof script.py
python -m pstats output.prof
```
In pstats, use `sort cumulative` and `stats 20` to find the top 20 functions by cumulative time.

**Live profiling with py-spy**:
```
py-spy top --pid <PID>
py-spy record -o profile.svg --pid <PID>
```
`py-spy` attaches to a running process without restarting it.

**Memory profiling with memory_profiler**:
```
python -m memory_profiler script.py
```
Requires `@profile` decorator on functions of interest.

**Line-level profiling with line_profiler**:
```
kernprof -l -v script.py
```
Requires `@profile` decorator. Shows time spent on each line.

### Step 5: Parse Profiling Output

Process the profiling results to extract actionable information.

Use `log_parse` from the eMCP data-file server if the profiling output is structured. Otherwise, read the output using `filesystem` tools and parse manually.

Identify the hot functions: the functions where the most time is spent. Sort by:
1. **Self time**: Time spent in the function itself (excluding callees). High self time indicates the function's own code is expensive.
2. **Cumulative time**: Time spent in the function and everything it calls. High cumulative time may indicate an orchestration function calling many expensive subroutines.

Focus on the top 5-10 functions by self time. These are the primary optimization targets.

### Step 6: Understand Hot Code Paths

For each hot function identified in Step 5, use LSP and AST tools to understand the code:

- Use `lsp_hover` to see the function's type signature and documentation.
- Use `lsp_references` to see who calls this function and how frequently.
- Use `ast_search` to examine the function body for patterns that indicate inefficiency.

Build a call chain from the entry point (e.g., HTTP handler) down to the hot function. This helps understand why the function is called so frequently or with such expensive inputs.

### Step 7: Identify Common Performance Patterns

Check for these frequent causes of performance problems:

**N+1 queries**:
- A loop that makes one database query per iteration instead of a batch query.
- Pattern: `for item in items: db.query("SELECT ... WHERE id = ?", item.id)`
- Fix: Use `WHERE id IN (...)` or a JOIN.

**Unnecessary allocations**:
- Creating large objects or arrays inside hot loops.
- String concatenation in loops (use StringBuilder or join).
- Pattern: repeated `[...array, newItem]` spread operations.

**Synchronous I/O in async contexts**:
- Using `fs.readFileSync` in a Node.js request handler.
- Blocking the event loop with CPU-intensive computation.
- Pattern: any `*Sync` function call in a request path.

**Missing caching**:
- Repeated computation of the same result.
- Repeated fetching of data that does not change frequently.
- Pattern: identical function calls with identical arguments in the same request lifecycle.

**Inefficient algorithms**:
- O(n^2) or worse algorithms on large datasets.
- Linear search where a hash map lookup would suffice.
- Pattern: nested loops over the same or related collections.

**Unindexed database queries**:
- Queries filtering on columns without indexes.
- Full table scans on large tables.
- Pattern: slow queries identified via `EXPLAIN` or `EXPLAIN ANALYZE`.

**Large payload serialization**:
- Serializing large objects to JSON on every request.
- Sending more data than the client needs.
- Pattern: `JSON.stringify` on large objects in hot paths.

### Step 8: Suggest Targeted Optimizations

For each identified bottleneck, propose a specific optimization:

Structure each suggestion as:

```
## Bottleneck: [Description]

### Location
File: src/services/data.ts, function: processRecords (line 45-92)

### Current Behavior
Iterates over all records and makes a database query for each one.
Average time: 850ms for 100 records.

### Proposed Change
Batch the queries using a single SELECT ... WHERE id IN (...).
Expected improvement: ~90% reduction (850ms -> ~85ms).

### Implementation Notes
- Collect all IDs first, then execute a single query.
- Restructure the result into a map for O(1) lookup in the loop.
- Ensure the batch size does not exceed database parameter limits.
```

Prioritize suggestions by expected impact. A single optimization that reduces latency by 50% is more valuable than five that each reduce it by 2%.

### Step 9: Verify Improvements

After implementing optimizations, re-measure using the same methodology from Step 2:

- Run the same benchmark or measurement commands.
- Compare against the baseline recorded in Step 2.
- Ensure the optimization did not introduce regressions in other areas.

Report the results:

```
## Performance Improvement Summary

### Baseline
- Endpoint: GET /api/records
- Median latency: 850ms
- P99 latency: 1200ms

### After Optimization
- Median latency: 95ms (88% reduction)
- P99 latency: 150ms (87% reduction)

### Changes Made
1. Batched database queries in processRecords (850ms -> 85ms)
2. Added Redis cache for getConfig (repeated call, 50ms -> 2ms)

### Side Effects
- Memory usage increased by ~5MB due to caching (acceptable)
- No test regressions
```

If the improvement is insufficient, return to Step 5 and look for the next bottleneck. Performance optimization is iterative.

## General Guidelines

- Always measure before and after. Do not assume an optimization helps without numbers.
- Optimize the biggest bottleneck first. Do not micro-optimize code that accounts for 1% of execution time.
- Consider the tradeoffs: caching uses memory, batching adds complexity, parallelism adds concurrency concerns.
- Document the performance baseline and improvements for future reference.

## Related Skills

- **n-plus-one-detector** (eskill-coding): Run n-plus-one-detector before this skill to identify database query bottlenecks contributing to performance issues.
- **bundle-analysis** (eskill-frontend): Run bundle-analysis alongside this skill to assess frontend asset sizes as part of the performance review.
