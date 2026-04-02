---
name: e-css
description: "Architecture-aware CSS audit that identifies unused rules, specificity conflicts, rendering-cost issues, and methodology-specific anti-patterns across Tailwind, CSS Modules, CSS-in-JS, and global CSS/SCSS. Use when cleaning up stylesheets, reviewing CSS architecture, or optimizing rendering performance. Also applies when: 'optimize CSS', 'find unused CSS', 'clean up stylesheets', 'CSS architecture review', 'specificity problems'."
---

# CSS Architecture Audit

This skill audits CSS codebases with awareness of the project's styling architecture. It identifies unused rules, redundant declarations, specificity conflicts, rendering-cost issues, and methodology-specific anti-patterns. The audit branches after architecture detection so that the checks applied match the system in use.

## Scope Boundaries

This skill owns CSS code quality and architecture. Adjacent concerns belong to other skills:

| Concern | Owner | Not This Skill |
|---------|-------|---------------|
| CSS code quality, specificity, unused rules, architecture anti-patterns | **e-css** | -- |
| Design token compliance (hardcoded values vs. tokens) | **e-tokens** | Do not duplicate token scanning here |
| Responsive breakpoint coverage and container queries | **e-responsive** | Do not duplicate breakpoint analysis here |
| CSS bundle size contribution to load time | **e-bundle** | Report removal counts; leave KB estimates and CWV mapping to e-bundle |
| Rendered visual correctness | **e-render** | Static analysis only; no browser rendering |

## Prerequisites

- A frontend project with CSS, SCSS, CSS Modules, Tailwind, or CSS-in-JS stylesheets.
- Target files or directories to analyze.

## Workflow

### Step 1: Detect the CSS Architecture

Use `filesystem` tools (fs_list, fs_read) to classify the project's styling approach. A project may use more than one; record all that apply.

| Signal | Architecture | Audit Branch |
|--------|-------------|-------------|
| `tailwindcss` in dependencies, `tailwind.config.*` | Tailwind / utility-first | Branch A |
| `*.module.css` or `*.module.scss` files | CSS Modules | Branch B |
| `styled-components` or `@emotion/react` in dependencies | CSS-in-JS (runtime) | Branch C |
| `vanilla-extract` or `@vanilla-extract/css` in dependencies | CSS-in-JS (zero-runtime) | Branch B (treat like CSS Modules) |
| `.css`, `.scss`, `.sass` files without module or utility patterns | Global CSS / SCSS | Branch D |

Read `postcss.config.*` if present. If autoprefixer is configured, vendor prefix checks (Step 5) can be skipped — the build pipeline handles them.

### Step 2: Detect Unused CSS

The detection method depends on the architecture.

**Branch D (Global CSS/SCSS)**: Extract all selectors from stylesheets. For each selector, use `egrep_search` to search component files for matching class names, IDs, or element references. Build a cross-reference table:

| Selector | Defined In | Used In | Status |
|----------|-----------|---------|--------|
| `.btn-primary` | src/styles/buttons.css:12 | src/components/Button.tsx | Used |
| `.btn-outline` | src/styles/buttons.css:24 | (none found) | Unused |

Flag "possibly unused" (not "confirmed unused") when selectors may target dynamically generated class names, pseudo-elements in third-party libraries, or elements injected by JavaScript.

**Branch B (CSS Modules)**: Use `ast_search` to find all `styles.*` or `styles['*']` references in the component that imports the module. Compare against classes defined in the `.module.css` file. Unused module exports are safe to remove because CSS Modules scope prevents external consumers.

**Branch A (Tailwind)**: Tailwind's content/purge configuration removes unused utilities at build time. Do not scan for unused utility classes. Instead, check for conflicting utilities on the same element (e.g., `text-red-500 text-blue-500` where the last one silently wins).

**Branch C (CSS-in-JS)**: Static analysis cannot fully detect unused styles in runtime CSS-in-JS because styles are generated at runtime. Flag this limitation. Check for styled components that are defined but never rendered by searching for export names with no import references using `egrep_search`.

### Step 3: Find Redundant Declarations

Scan for CSS declarations that are overridden, duplicated, or have no visual effect. This step applies to all architectures.

**Duplicate properties in the same rule**:
```css
.card {
  padding: 16px;
  margin: 8px;
  padding: 24px; /* overrides the earlier padding */
}
```

**Shorthand/longhand conflicts**:
```css
.card {
  margin: 16px;
  margin-top: 0; /* intended override, but a shorthand after this resets it */
}
```

**No-effect declarations** — properties that have no visual effect given the element's display context. These can only be detected when both the property and the display context appear in the same rule block. Cross-file or inherited display context is beyond static analysis:

| Co-occurrence in Same Rule | Why No Effect |
|---------------------------|--------------|
| `display: inline` + `width` or `height` | Width/height are ignored on non-replaced inline elements |
| `display: inline` + `margin-top` or `margin-bottom` | Vertical margins are ignored on inline elements |
| `display: flex` or `display: grid` + `float` | Float is ignored on flex/grid children by spec |
| `display: block` + `vertical-align` | vertical-align only applies to inline and table-cell contexts |

Use `egrep_search` to find rules containing both the display declaration and the no-effect property. Flag only same-rule co-occurrences; do not attempt cross-file inference.

### Step 4: Analyze Specificity Conflicts

**High specificity selectors**: Flag selectors using ID selectors (`#header`). ID selectors make overrides difficult and indicate a specificity escalation pattern.

**`!important` usage**: Search all stylesheets for `!important`. Categorize:

| Context | Assessment |
|---------|-----------|
| Utility class override (e.g., `.hidden { display: none !important }`) | Acceptable |
| Component style | Problematic — indicates specificity conflict |
| Third-party override | Understandable but should be isolated |
| Multiple `!important` in same file | Indicates a specificity war |

**Cross-file property conflicts**: Flag cases where the same property on the same selector appears in multiple files. The final value depends on stylesheet loading order, which is fragile.

**CSS `@layer` awareness**: If the project uses CSS cascade layers (`@layer`), specificity analysis must account for layer ordering. Within a lower-priority layer, even a high-specificity selector loses to a low-specificity selector in a higher-priority layer. Search for `@layer` declarations using `egrep_search`. If layers are present, report specificity findings within layer context rather than globally.

This step applies primarily to **Branches B and D**. In Tailwind (Branch A), specificity is managed by the framework. In CSS-in-JS (Branch C), specificity conflicts are rare because styles are scoped to components.

### Step 5: Architecture-Specific Anti-Patterns

Run the checks for the detected architecture(s) from Step 1.

#### Branch A: Tailwind Anti-Patterns

| Anti-Pattern | Detection | Why It Matters |
|-------------|-----------|---------------|
| Arbitrary value proliferation | `egrep_search` for `w-[`, `h-[`, `p-[`, `m-[`, `text-[`, `bg-[` patterns across component files. Count occurrences. | Tailwind's docs state arbitrary values are for "occasional, exceptional cases." High counts indicate the design system is being bypassed rather than extended via config. |
| `@apply` overuse | `egrep_search` for `@apply` in CSS files. Count occurrences. | Tailwind's docs state that using `@apply` for everything "throws away all of the workflow and maintainability advantages Tailwind gives you." The recommended reuse pattern is component abstraction. |
| Safelist bloat | Read `tailwind.config.*` for `safelist` entries. Count patterns. | The Tailwind team states safelist is "a last resort" and they "never need safelisting in any of their projects." The alternative for dynamic values is CSS custom properties. |
| Conflicting utilities | Use `ast_search` to extract class strings from JSX `className` attributes. Apply a hardcoded list of known contradictory pairs: `flex`/`inline`, `hidden`/`block`, `static`/`absolute`/`relative`/`fixed`/`sticky` (multiple position utilities), opposing `text-*` color utilities on the same element. | The last utility wins silently with no warning. The tool does not understand Tailwind semantics; the contradiction list must be maintained manually. |

#### Branch B: CSS Modules Anti-Patterns

| Anti-Pattern | Detection | Why It Matters |
|-------------|-----------|---------------|
| `:global()` overuse | `egrep_search` for `:global(` in `.module.css` files. Count occurrences. | `:global()` breaks module scoping. Legitimate uses: third-party library class targeting, browser resets. Anti-pattern: general escape mechanism to avoid scoping. |
| Multi-file `composes` chains | `egrep_search` for `composes:` with `from` in `.module.css` files. Trace chains across files. | The CSS Modules spec states: "when composing multiple classes from different files, the order of appliance is undefined." Multi-file composition chains produce fragile, order-dependent styles. |
| Unused module exports | Compare defined classes against `styles.*` references in the importing component (from Step 2). | Unlike global CSS, unused CSS Module classes are guaranteed unreachable because the module scope prevents external access. Safe to remove. |

#### Branch C: CSS-in-JS Anti-Patterns

| Anti-Pattern | Detection | Why It Matters |
|-------------|-----------|---------------|
| Styled components inside render | `ast_search` for `styled.*` calls inside function components or class render methods. | styled-components docs: defining inside render "creates a new component identity on every render. React discards and remounts the entire subtree, losing DOM state." |
| Dynamic interpolation explosion | `ast_search` for styled-components or Emotion template literals with `${props => ...}` interpolations. Count unique interpolation patterns. | Each unique interpolation result generates a new CSS class. At scale this produces hundreds of classes and style recalculation. The alternative is CSS custom properties with a single cached rule. |
| RSC incompatibility | Check `next.config.*` for app router usage. If present, check whether CSS-in-JS imports appear in files without `'use client'` directive. | Next.js docs: "CSS-in-JS libraries which require runtime JavaScript are not currently supported in Server Components." |

#### Branch D: Global CSS/SCSS Anti-Patterns

| Anti-Pattern | Detection | Why It Matters |
|-------------|-----------|---------------|
| Deep nesting (SCSS) | `egrep_search` for patterns with 4+ levels of nesting indentation in `.scss` files. | Deep nesting produces high-specificity selectors that are difficult to override and maintain. |
| Selector concatenation (`&__`, `&--`) abuse | `egrep_search` for BEM-style concatenation in SCSS. Check for selectors that cannot be found by searching for the full class name. | Concatenated selectors are invisible to `egrep_search` and IDE "find references" because the full class name never appears in the source. |
| Import order fragility | Check `@import` or `@use` chains in SCSS entry points. Flag files where the same selector is defined in multiple imported partials. | The cascade depends on import order. Reordering imports silently changes which declarations win. |

### Step 6: Suggest Modern CSS Alternatives

Identify legacy CSS patterns that have cleaner modern replacements:

| Legacy Pattern | Modern Alternative |
|---------------|-------------------|
| `float` for layout | `display: flex` or `display: grid` |
| `display: inline-block` for alignment | `display: flex` with `align-items` |
| Negative margin for gap | `gap` property on flex/grid container |
| `calc(100% / 3)` for columns | `grid-template-columns: repeat(3, 1fr)` |
| Clearfix hack (`.clearfix::after`) | Remove; use flex or grid |
| `position: absolute` + `top: 50%` + `left: 50%` + `transform: translate(-50%, -50%)` centering hack | `place-items: center` on grid |
| Media query for font size at each breakpoint | `clamp(min, preferred, max)` for fluid typography |
| `height: 100vh` | `height: 100dvh` |
| Complex sibling selectors for parent targeting | `:has()` parent selector |
| Webkit-only scroll styling | `scrollbar-color`, `scrollbar-width` |

Use `egrep_search` to search for these patterns across stylesheets.

### Step 7: Check CSS Rendering Cost

Identify CSS patterns that affect rendering performance. This step owns rendering-cost analysis at the CSS level. Bundle-level performance impact (download size, parse cost, Core Web Vitals mapping) belongs to e-bundle.

**Rendering cost tiers**: CSS properties divide into three cost tiers based on which stages of the browser's pixel pipeline they trigger:

| Tier | Pipeline Stages | Properties | Animation Cost |
|------|----------------|-----------|---------------|
| Layout | Style + Layout + Paint + Composite | width, height, margin, padding, display, position, flex, top/left/right/bottom | Expensive — triggers full recalculation |
| Paint | Style + Paint + Composite | color, background, border, box-shadow, outline | Moderate — skips layout |
| Composite | Composite only | transform, opacity | Cheap — GPU-accelerated |

Flag animations or transitions that animate layout-triggering properties. Suggest `transform` and `opacity` instead where possible.

**`will-change` misuse**: Search for `will-change` in stylesheets. MDN documents that `will-change` applied permanently in stylesheets (rather than dynamically via JavaScript before an animation starts) "will result in excessive memory use and will cause more complex rendering." It also creates a new stacking context, which can produce unintended visual layering. Flag `will-change` declarations in static CSS rules as a potential performance anti-pattern.

**CSS containment opportunities**: Search for `contain` and `content-visibility` usage. For large, complex pages, `contain: content` on independent subtrees (cards, list items, sections) lets the browser skip layout and paint for off-screen elements. `content-visibility: auto` implicitly applies containment and skips rendering for elements not in the viewport. Flag large repeated elements (list items, grid cards) that lack containment as optimization opportunities.

**Expensive selectors**:
- Universal selector in descendants: `* { }` or `.parent * { }`.
- Deep descendant selectors: `.a .b .c .d .e { }` (browsers match right-to-left).
- Attribute selectors with substring matching: `[class*="btn"]`.

### Step 8: Identify Vendor Prefix Redundancy

If autoprefixer is configured (detected in Step 1), skip this step — vendor prefixes in source files are fully redundant.

Otherwise, read the project's browserslist configuration (`.browserslistrc` or `browserslist` in `package.json`). Flag vendor prefixes that are unnecessary for the target browser range. Common removals for modern targets:

| Property | Prefix | Unprefixed Since |
|----------|--------|-----------------|
| `display: flex` | `-webkit-flex` | All modern browsers |
| `transform` | `-webkit-transform` | All modern browsers |
| `transition` | `-webkit-transition` | All modern browsers |
| `animation` | `-webkit-animation` | All modern browsers |
| `user-select` | `-webkit-user-select` | Chrome 54+, Firefox 69+ |

### Step 9: Generate the Optimization Report

Compile all findings into a report organized by impact:

```
## CSS Architecture Audit Report

### Architecture: [Tailwind | CSS Modules | CSS-in-JS | Global SCSS | Mixed]

### Summary
- Stylesheets analyzed: 24
- Architecture anti-patterns: 5
- Unused CSS: 47 selectors
- Redundant declarations: 12
- Specificity issues: 8
- Rendering cost issues: 3
- Modern alternative opportunities: 7

### Architecture Anti-Patterns
[Findings from Step 5, specific to the detected architecture]

### High Impact
| File | Line | Issue | Recommendation |
|------|------|-------|----------------|

### Medium Impact
| File | Line | Issue | Recommendation |
|------|------|-------|----------------|

### Removal Counts
- Unused rules: 47 selectors
- Redundant declarations: 12
- Use e-bundle to map these removals to download size and Core Web Vitals impact.
```

## Edge Cases

- **Mixed architectures**: Projects using both Tailwind and CSS Modules (or global CSS alongside CSS-in-JS) require running multiple architecture branches. Report findings grouped by architecture, not interleaved.
- **Dynamic class names**: Class names constructed with template literals or string concatenation cannot be matched statically. Exclude from unused-selector counts and flag the limitation.
- **Third-party CSS**: Stylesheets from `node_modules` should be analyzed separately. The project cannot modify them directly but can evaluate whether they are necessary.
- **Critical CSS extraction**: If the project uses critical CSS inlining, some selectors that appear unused in components may be referenced in the critical CSS pipeline. Check the configuration before flagging.
- **CSS custom property scoping**: Custom properties on `:root` are global; properties on specific selectors are scoped. Do not flag scoped properties as duplicates of root-level properties with similar names.
- **PostCSS transforms**: Some CSS patterns that look suboptimal in source files may be transformed by PostCSS plugins at build time (nesting, custom media queries). Check the PostCSS config before flagging these.

## Related Skills

- **e-tokens** (eskill-frontend): e-tokens validates design token compliance (hardcoded values vs. tokens). e-css validates CSS code quality and architecture. The two do not overlap: e-tokens checks what values are used, e-css checks how styles are structured. Run e-tokens before e-css.
- **e-bundle** (eskill-frontend): e-css reports removal counts and architecture findings. e-bundle maps those reductions to download impact and Core Web Vitals risk factors. Run e-css before e-bundle.
- **e-responsive** (eskill-frontend): e-responsive checks breakpoint coverage and container query usage. e-css checks CSS architecture quality. Run e-responsive alongside e-css.
- **e-design** (eskill-frontend): e-design produces CSS as part of implementation. Run e-css after e-design to audit the generated CSS for architecture conformance.
- **e-render** (eskill-frontend): e-css is static analysis. e-render validates rendered output in a browser. Use e-render when static analysis is insufficient to determine correctness.
- **e-lint** (eskill-quality): e-lint enforces coding standards and formatting rules. e-css audits CSS architecture and optimization. The two are complementary: e-lint catches style violations, e-css catches structural and performance issues.
