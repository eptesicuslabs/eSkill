---
name: e-bundle
description: "Analyzes JavaScript and CSS bundle composition to identify large dependencies, duplicate modules, tree-shaking opportunities, and estimated Core Web Vitals risk factors. Use when optimizing load times, reducing bundle size, investigating slow page loads, or assessing performance budgets. Also applies when: 'analyze bundle size', 'why is the bundle so large', 'find large dependencies', 'optimize load time', 'bundle performance impact', 'lighthouse budget'."
---

# Bundle Analysis

This skill analyzes the composition of JavaScript and CSS bundles to identify large dependencies, duplicate modules, dead code, and tree-shaking opportunities. It connects bundle findings to user-facing performance impact through Core Web Vitals thresholds and produces prioritized recommendations for reducing bundle size and improving load times.

## Prerequisites

- A frontend project with a JavaScript bundler (webpack, Vite, Rollup, esbuild, Parcel, or Next.js).
- The project must be buildable (dependencies installed, build command functional).

## Workflow

### Step 1: Detect the Bundler

Use `filesystem` tools (fs_read, fs_list) to determine which bundler the project uses:

| Indicator                          | Bundler    |
|------------------------------------|------------|
| `webpack.config.*` in root         | webpack    |
| `vite.config.*` in root            | Vite       |
| `rollup.config.*` in root          | Rollup     |
| `next.config.*` in root            | Next.js    |
| `esbuild` in package.json scripts  | esbuild    |
| `.parcelrc` or `parcel` in scripts | Parcel     |
| `turbopack` in next.config         | Turbopack  |

Read `package.json` to confirm the bundler version and check for bundle analysis plugins already installed.

### Step 2: Generate Bundle Stats

Run the appropriate analysis command using `shell_exec` from the eMCP shell server.

**webpack**:
```
npx webpack --json > stats.json
```
Or if webpack-bundle-analyzer is installed:
```
npx webpack-bundle-analyzer stats.json --mode json --report-filename report.json
```

**Vite**:
```
npx vite build --mode production
npx rollup-plugin-visualizer
```
Or install and use vite-bundle-visualizer:
```
npx vite-bundle-visualizer --output stats.html
```

**Next.js**:
```
ANALYZE=true npx next build
```
Requires `@next/bundle-analyzer` in next.config. If not installed, use:
```
npx next build
```
Then analyze the `.next/` output directory.

**Rollup**:
```
npx rollup -c --environment ANALYZE:true
```
With rollup-plugin-visualizer configured.

**Generic (source-map-explorer)**:
```
npx source-map-explorer build/static/js/*.js --json > sme-report.json
```
Requires source maps to be enabled in the production build.

If the stats generation command fails, read the error output and report the issue to the user. Common problems: missing dependencies, build errors, or source maps disabled.

### Step 3: Parse Bundle Composition

Read the generated stats file using `filesystem` tools (fs_read) and extract:

**Per-chunk breakdown**:
- Chunk name (main, vendor, async chunks).
- Chunk size (raw and gzipped).
- List of modules in each chunk with individual sizes.

**Dependency sizes**:
Build a table of third-party dependencies sorted by their contribution to total bundle size:

| Dependency           | Raw Size  | Gzipped  | % of Total | Entry Chunk |
|---------------------|-----------|----------|------------|-------------|
| react-dom           | 128 KB    | 42 KB    | 18%        | vendor      |
| lodash              | 72 KB     | 26 KB    | 10%        | vendor      |
| moment              | 67 KB     | 22 KB    | 9%         | vendor      |
| chart.js            | 58 KB     | 20 KB    | 8%         | main        |

Focus on the top 10 dependencies by size. These are the primary optimization targets.

### Step 4: Identify Duplicate Modules

Search the stats for modules that appear in multiple chunks or modules that are included more than once due to version conflicts.

**Cross-chunk duplication**:
Modules bundled into both the main chunk and an async chunk, causing the user to download the same code twice.

**Version duplication**:
Read `package-lock.json` or `yarn.lock` to find packages with multiple installed versions. Use `shell_exec` to check:
```
npm ls <package-name>
```

Common duplication sources:

| Scenario                          | Detection Method                       |
|-----------------------------------|----------------------------------------|
| Multiple lodash versions          | `npm ls lodash` shows nested versions  |
| CJS and ESM copies of same lib    | Same module appears twice in stats     |
| Transitive dependency conflicts   | Lock file shows multiple version resolutions |

### Step 5: Analyze Tree-Shaking Effectiveness

Check whether the project is getting the benefit of tree-shaking (dead code elimination):

**Barrel file imports**:
Use `egrep_search` to rapidly locate import statements that pull from barrel files across the codebase, or use `ast_search` from the eMCP AST server for structured parsing:
```
import { Button } from './components';        // Barrel import
import { Button } from './components/Button'; // Direct import
```
Barrel imports can prevent effective tree-shaking, especially with CommonJS modules or side-effectful modules.

**Full library imports**:
Search for import patterns that pull entire libraries:
```
import _ from 'lodash';           // Imports entire lodash
import { debounce } from 'lodash'; // Still imports entire lodash (CJS)
```

Versus tree-shakeable alternatives:
```
import debounce from 'lodash/debounce'; // Only imports debounce
import { debounce } from 'lodash-es';   // ESM, tree-shakeable
```

**Side effects configuration**:
Read `package.json` for the `sideEffects` field. If absent, the bundler may not tree-shake the project's own code effectively. Check key dependencies for `sideEffects` in their own `package.json`.

### Step 6: Check Code Splitting

Evaluate whether the project uses code splitting effectively:

**Route-based splitting**:
Use `ast_search` to find dynamic imports in route definitions:
```javascript
const Page = lazy(() => import('./pages/Page'));       // React
const Page = () => import('./pages/Page.vue');          // Vue
const routes = [{ path: '/', loadComponent: () => import('./page.component') }]; // Angular
```

If routes are imported statically, all page code lands in the initial bundle.

**Component-level splitting**:
Check if large components or features use dynamic imports:
```javascript
const HeavyChart = lazy(() => import('./HeavyChart'));
```

**Vendor splitting**:
Check the bundler config for `splitChunks` (webpack) or `manualChunks` (Vite/Rollup) configuration that separates vendor code from application code.

Report which routes or features are split and which are bundled into the initial load.

### Step 7: Suggest Dependency Alternatives

For the largest dependencies identified in Step 3, suggest lighter alternatives:

| Heavy Dependency   | Size   | Alternative            | Size   | Savings |
|--------------------|--------|------------------------|--------|---------|
| moment             | 67 KB  | date-fns (tree-shake)  | ~5 KB  | 92%     |
| moment             | 67 KB  | dayjs                  | 7 KB   | 89%     |
| lodash (full)      | 72 KB  | lodash-es (tree-shake) | ~5 KB  | 93%     |
| axios              | 14 KB  | fetch (native)         | 0 KB   | 100%    |
| uuid               | 8 KB   | crypto.randomUUID()    | 0 KB   | 100%    |
| classnames         | 1 KB   | clsx                   | <1 KB  | 50%     |
| numeral            | 16 KB  | Intl.NumberFormat       | 0 KB   | 100%    |

Only suggest alternatives that are API-compatible or require minimal refactoring. Note the migration effort for each suggestion.

### Step 8: Analyze CSS Bundle

If the project has a separate CSS bundle or CSS extracted from JS, analyze its size:

**Unused CSS**:
Use `shell_exec` to check for tools that detect unused CSS:
```
npx purgecss --css build/static/css/*.css --content build/static/js/*.js --output purged/
```

Compare the purged output size against the original to estimate unused CSS volume.

**CSS duplication**:
Search for repeated property declarations across the stylesheet. Common sources:
- Utility classes generated for unused breakpoints.
- Duplicate component styles from multiple CSS-in-JS renders.
- Reset styles applied multiple times through nested imports.

### Step 9: Generate the Analysis Report

Compile all findings into a prioritized report:

```
## Bundle Analysis Report

### Overview
- Total bundle size: 1.2 MB (380 KB gzipped)
- JavaScript: 980 KB (310 KB gzipped)
- CSS: 220 KB (70 KB gzipped)
- Chunks: 8 (1 entry, 2 vendor, 5 async)

### Top Optimization Opportunities
| Priority | Action | Estimated Savings | Effort |
|----------|--------|-------------------|--------|
| 1 | Replace moment with date-fns | 62 KB gzipped | Medium |
| 2 | Use lodash-es with direct imports | 21 KB gzipped | Low |
| 3 | Code-split Settings page | 15 KB gzipped | Low |
| 4 | Remove unused CSS | 12 KB gzipped | Low |
| 5 | Deduplicate core-js versions | 8 KB gzipped | Medium |

### Dependency Breakdown
[Table from Step 3]

### Duplicate Modules
[Findings from Step 4]

### Tree-Shaking Issues
[Findings from Step 5]

### Code Splitting Status
[Findings from Step 6]
```

### Step 10: Assess Core Web Vitals Impact

Connect bundle findings to user-facing performance metrics. The current Core Web Vitals (as of March 2024, when INP replaced FID) are:

| Metric | Good | Needs Improvement | Poor | What It Measures |
|--------|------|-------------------|------|------------------|
| LCP (Largest Contentful Paint) | < 2.5s | 2.5s - 4.0s | > 4.0s | Time until the largest visible element renders |
| INP (Interaction to Next Paint) | < 200ms | 200ms - 500ms | > 500ms | Latency from user interaction to visual response |
| CLS (Cumulative Layout Shift) | < 0.1 | 0.1 - 0.25 | > 0.25 | Visual stability throughout the page lifecycle |

These thresholds are assessed at the 75th percentile of page loads.

**Bundle size to LCP mapping**: Large JavaScript bundles block rendering because the browser must download, parse, and execute scripts before painting. As a rough heuristic, each 100 KB of uncompressed JavaScript adds approximately 50-100ms to parse time on mid-range mobile devices. This estimate varies significantly by JavaScript engine version, code complexity, and device generation. Map the top optimization opportunities from Step 9 to estimated LCP improvement.

**Bundle size to INP mapping**: Heavy main-thread JavaScript execution blocks the browser from responding to user input. Dependencies that run synchronous work on the main thread (large utility libraries, synchronous state management) directly increase INP. Flag any dependency over 50 KB that executes synchronously on interaction.

**Code splitting to CLS mapping**: If large components are loaded lazily without layout reservation (no explicit width/height or skeleton), they cause layout shift when they render. Check that code-split components have sized containers.

**Lighthouse CI regression checking**: If the project uses Lighthouse CI (`@lhci/cli` in devDependencies or a `lighthouserc.*` config file), read the configuration and report the current performance budgets. If no Lighthouse CI is configured, note it as a gap.

Lighthouse collects lab (synthetic) data only. It cannot accurately measure INP because it cannot simulate realistic user interaction timing. CLS measurement in lab mode misses post-load layout shifts from lazy-loaded content and user scrolling. CPU throttling uses a simulated 4x multiplier that is relative to the host machine's hardware, not an absolute performance target. Lab data is useful for regression detection but should not be treated as equivalent to field performance data from real users.

## Edge Cases

- **Monorepo with shared packages**: Bundle stats may include internal packages that appear as external dependencies. Distinguish between third-party and internal packages when calculating dependency sizes.
- **Server-side bundles**: Next.js and Nuxt produce both client and server bundles. Focus the analysis on client bundles unless the user specifically asks about server bundle size.
- **Source maps disabled**: If production builds have source maps disabled, source-map-explorer will not work. Fall back to analyzing the raw stats.json output or suggest enabling source maps temporarily.
- **Dynamic imports with variables**: Dynamic imports using template literals (``import(`./pages/${page}`)`` ) create catch-all chunks that bundle every possible match. Flag these as a code-splitting concern.
- **CSS-in-JS runtime cost**: Libraries like styled-components and Emotion add runtime overhead that does not appear in static bundle analysis. Note this as a separate consideration when these libraries are detected.
- **Micro-frontends**: If the project uses module federation or micro-frontend architecture, each remote has its own bundle. Analyze each remote separately and check for shared dependency duplication across remotes.

## Related Skills

- **e-deadcode** (eskill-coding): Run e-deadcode before this skill to identify unused code contributing to bundle bloat.
- **e-css** (eskill-frontend): Follow up with e-css after this skill to reduce CSS file sizes in the bundle.
- **e-render** (eskill-frontend): Use e-render after this skill to validate that bundle optimizations (code splitting, lazy loading) do not degrade the rendered user experience.
- **e-perf** (eskill-coding): e-perf profiles runtime performance (CPU, memory, I/O). This skill profiles the bundle (download size, parse cost, dependency weight). Use both for a complete performance picture.
