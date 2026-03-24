---
name: css-optimization
description: "Identifies CSS optimization opportunities including unused selectors, redundant properties, specificity conflicts, and missing modern alternatives. Use when cleaning up stylesheets, migrating CSS approaches, or optimizing rendering. Also applies when: 'optimize CSS', 'find unused CSS', 'clean up stylesheets', 'reduce CSS bloat'."
---

# CSS Optimization

This skill identifies optimization opportunities in CSS and SCSS codebases by scanning for unused selectors, redundant declarations, specificity conflicts, unnecessary vendor prefixes, and patterns that have modern CSS replacements. It produces a prioritized list of improvements with concrete refactoring suggestions.

## Prerequisites

- A frontend project with CSS, SCSS, or CSS-in-JS stylesheets.
- Target files or directories to analyze.

## Workflow

### Step 1: Inventory the Stylesheets

Use `filesystem` tools (list_directory) to catalog all stylesheet files in the project. Organize by type:

| File Type           | Extensions                  | Processing Notes           |
|---------------------|-----------------------------|----------------------------|
| Plain CSS           | `.css`                      | Direct analysis            |
| SCSS/Sass           | `.scss`, `.sass`            | Resolve imports/partials   |
| CSS Modules         | `.module.css`, `.module.scss`| Scope analysis per module |
| CSS-in-JS           | `.ts`, `.tsx` (styled-*)    | Extract template literals  |
| Tailwind utilities  | Component files             | Check for redundancy in utility classes |
| PostCSS config      | `postcss.config.*`          | Determines transforms applied |

Read `postcss.config.js` or `postcss.config.ts` if present to understand what PostCSS plugins run (autoprefixer, cssnano, etc.). This affects which optimizations are already handled automatically.

### Step 2: Detect Unused Selectors

Identify CSS selectors that do not match any element in the project's templates or components.

**For CSS/SCSS files**:
Extract all selectors from the stylesheets. For each selector, use `run_command` from the eMCP shell server to search component files for matching class names, IDs, or element references.

Build a cross-reference:

| Selector              | Defined In                  | Used In                    | Status   |
|-----------------------|-----------------------------|----------------------------|----------|
| `.btn-primary`        | src/styles/buttons.css:12   | src/components/Button.tsx  | Used     |
| `.btn-outline`        | src/styles/buttons.css:24   | (none found)               | Unused   |
| `.legacy-header`      | src/styles/layout.css:8     | (none found)               | Unused   |

**For CSS Modules**:
Use `ast_search` from the eMCP AST server to find all `styles.*` or `styles['*']` references in the component file that imports the module. Compare against the classes defined in the `.module.css` file.

**For Tailwind**:
Tailwind's purge/content configuration handles unused utilities at build time. Instead, check for Tailwind classes in component files that conflict or override each other on the same element (e.g., `text-red-500 text-blue-500`).

Note: A selector may appear unused because it targets dynamically generated class names, pseudo-elements in third-party libraries, or elements injected by JavaScript. Flag these as "possibly unused" rather than "confirmed unused."

### Step 3: Find Redundant Declarations

Scan for CSS declarations that are overridden, duplicated, or have no visual effect.

**Duplicate properties in the same rule**:
```css
.card {
  padding: 16px;
  margin: 8px;
  padding: 24px; /* Overrides the earlier padding */
}
```
The first `padding` has no effect. Flag it for removal.

**Overridden shorthand/longhand conflicts**:
```css
.card {
  margin: 16px;
  margin-top: 0; /* Intended override, but order matters */
}
```
Check whether shorthand and longhand properties interact correctly. Flag cases where a shorthand after a longhand silently resets the longhand value.

**No-effect declarations**:
Properties that have no visual effect given the element's display context:

| Declaration                | No Effect When                              |
|----------------------------|---------------------------------------------|
| `vertical-align`          | Parent is not `table-cell` or `inline`       |
| `float`                   | Element has `display: flex` or `display: grid` |
| `clear`                   | No floated siblings                          |
| `width`/`height` on inline| Element is `display: inline` (non-replaced)  |
| `margin-top`/`margin-bottom` on inline | Element is `display: inline`     |
| `overflow` on inline      | Element is `display: inline`                 |

Use `ast_search` or `run_command` to find these patterns in stylesheet files.

### Step 4: Analyze Specificity Conflicts

Scan for specificity issues that make styles difficult to maintain.

**High specificity selectors**:
Flag selectors with specificity above a threshold. Calculate specificity for each selector:

| Component      | Weight | Examples                        |
|----------------|--------|---------------------------------|
| Inline style   | 1000   | `style="..."` attribute         |
| ID selector    | 100    | `#header`, `#main-nav`          |
| Class/attr/pseudo-class | 10 | `.btn`, `[type="text"]`, `:hover` |
| Element/pseudo-element | 1 | `div`, `p`, `::before`          |

Flag selectors with specificity above (0, 1, 0, 0) -- that is, any selector using an ID. ID selectors make overrides difficult and indicate a specificity escalation pattern.

**`!important` usage**:
Search all stylesheets for `!important` declarations. Each occurrence is a specificity conflict indicator.

Categorize `!important` usage:

| Context                    | Assessment                                     |
|----------------------------|-------------------------------------------------|
| Utility class override     | Acceptable (e.g., `.hidden { display: none !important }`) |
| Component style            | Problematic; indicates specificity conflict      |
| Third-party override       | Understandable but should be isolated            |
| Multiple `!important` in same file | Indicates a specificity war                |

**Cascading order conflicts**:
Flag cases where the same property on the same selector appears in multiple files. The final value depends on stylesheet loading order, which is fragile.

### Step 5: Identify Vendor Prefix Redundancy

Search for vendor prefixes that are no longer necessary for the project's browser support targets.

Read the project's browser support configuration:
- `.browserslistrc` file.
- `browserslist` key in `package.json`.
- Default (last 2 versions, >0.5% market share) if not specified.

Common vendor prefixes that are unnecessary for modern browsers (2024+):

| Property                    | Prefix               | Supported Unprefixed Since |
|-----------------------------|----------------------|----------------------------|
| `display: flex`            | `-webkit-flex`        | All modern browsers        |
| `transform`                | `-webkit-transform`   | All modern browsers        |
| `transition`               | `-webkit-transition`  | All modern browsers        |
| `animation`                | `-webkit-animation`   | All modern browsers        |
| `border-radius`            | `-webkit-border-radius`| All modern browsers       |
| `box-shadow`               | `-webkit-box-shadow`  | All modern browsers        |
| `appearance`               | `-webkit-appearance`  | All modern browsers (with prefix still recommended) |
| `user-select`              | `-webkit-user-select` | Chrome 54+, Firefox 69+    |

If autoprefixer is configured in PostCSS, vendor prefixes in source files are fully redundant and should be removed. The build pipeline adds them as needed.

### Step 6: Suggest Modern CSS Alternatives

Identify legacy CSS patterns that have cleaner modern alternatives:

**Layout patterns**:

| Legacy Pattern                        | Modern Alternative                    |
|---------------------------------------|---------------------------------------|
| `float` for layout                    | `display: flex` or `display: grid`    |
| `display: inline-block` for alignment | `display: flex` with `align-items`    |
| Negative margin for gap               | `gap` property on flex/grid container |
| `calc(100% / 3)` for columns          | `grid-template-columns: repeat(3, 1fr)` |
| Clearfix hack (`.clearfix::after`)    | Remove; use flex or grid              |
| `position: absolute` centering hack   | `place-items: center` on grid         |

**Sizing and spacing**:

| Legacy Pattern                        | Modern Alternative                    |
|---------------------------------------|---------------------------------------|
| `max-width: Xpx; margin: 0 auto`     | `width: min(100%, Xpx); margin-inline: auto` |
| Media query for font size             | `clamp(min, preferred, max)` for fluid typography |
| `height: 100vh`                       | `height: 100dvh`                      |
| `overflow: hidden` on body for modal  | `<dialog>` element with `::backdrop`  |

**Selectors and features**:

| Legacy Pattern                        | Modern Alternative                    |
|---------------------------------------|---------------------------------------|
| `:nth-child` type hacks               | `:nth-child(n of .selector)` (CSS4)  |
| Complex sibling selectors             | `:has()` parent selector              |
| `@media (hover: hover)` only          | Pair with `@media (pointer: fine)`    |
| Separate dark mode stylesheets        | `@media (prefers-color-scheme: dark)` |
| Custom scroll styling (webkit-only)   | `scrollbar-color`, `scrollbar-width`  |

Use `run_command` to search for these patterns across the stylesheets.

### Step 7: Check for CSS Performance Issues

Identify patterns that affect rendering performance:

**Expensive selectors**:
- Universal selector in descendants: `* { }` or `.parent * { }`.
- Deep descendant selectors: `.a .b .c .d .e { }` (browsers match right-to-left).
- Attribute selectors with substring matching: `[class*="btn"]`.

**Paint-triggering properties**:
Properties that trigger layout recalculation or paint on change:

| Trigger Level | Properties                                      |
|---------------|-------------------------------------------------|
| Layout        | width, height, margin, padding, display, position |
| Paint         | color, background, border, box-shadow, outline   |
| Composite     | transform, opacity (GPU-accelerated, cheapest)   |

Flag animations or transitions that animate layout-triggering properties. Suggest using `transform` and `opacity` instead where possible.

**Large selector counts**:
If a single stylesheet contains more than 4000 selectors, older browsers (IE, legacy Edge) may ignore rules beyond that limit. Modern browsers handle this, but it indicates an oversized stylesheet that should be split.

### Step 8: Generate the Optimization Report

Compile all findings into a prioritized report:

```
## CSS Optimization Report

### Summary
- Stylesheets analyzed: 24
- Total selectors: 892
- Unused selectors: 47 (5.3%)
- Redundant declarations: 12
- Specificity issues: 8
- Vendor prefix removals: 31
- Modern alternatives available: 15

### High Impact
| File | Line | Issue | Recommendation |
|------|------|-------|----------------|
| styles/layout.css | 45 | Float-based grid | Replace with CSS Grid |
| styles/buttons.css | 12-18 | 6 unused selectors | Remove .btn-outline, .btn-ghost, ... |
| components/Modal.module.css | 8 | !important on 3 props | Restructure selector specificity |

### Medium Impact
| File | Line | Issue | Recommendation |
|------|------|-------|----------------|
| styles/global.css | 22 | Vendor prefix (-webkit-transform) | Remove; autoprefixer handles this |
| styles/typography.css | 15 | Manual responsive font sizes | Use clamp() for fluid typography |

### Low Impact
| File | Line | Issue | Recommendation |
|------|------|-------|----------------|
| styles/utils.css | 8 | Duplicate padding declaration | Remove first padding: 16px |

### Size Reduction Estimate
- Unused selector removal: ~2.4 KB
- Redundant declaration removal: ~0.3 KB
- Vendor prefix removal: ~1.1 KB
- Total estimated savings: ~3.8 KB (before gzip)
```

## Edge Cases

- **CSS-in-JS runtime styles**: Styled-components, Emotion, and similar libraries generate styles at runtime. Static analysis cannot fully detect unused styles in these systems. Flag this limitation in the report.
- **Dynamic class names**: Class names constructed with template literals or string concatenation (e.g., `btn-${variant}`) cannot be matched statically against stylesheet selectors. Exclude dynamically constructed classes from the unused selector list.
- **Third-party CSS**: Stylesheets imported from `node_modules` (e.g., normalize.css, library themes) should be analyzed separately. The project cannot modify these files directly, but can evaluate whether they are necessary.
- **Critical CSS extraction**: If the project uses critical CSS extraction (above-the-fold inlining), some selectors that appear unused in components may be referenced in the critical CSS pipeline. Check the critical CSS configuration before flagging.
- **Atomic CSS (Tailwind, UnoCSS)**: In atomic CSS projects, traditional unused-selector analysis does not apply. Focus the audit on conflicting utility classes, unnecessary arbitrary values, and Tailwind config bloat instead.
- **CSS custom property scoping**: Custom properties (CSS variables) defined on `:root` are global. Properties defined on specific selectors are scoped. Do not flag scoped custom properties as duplicates of root-level properties with similar names.

## Related Skills

- **design-system-audit** (eskill-frontend): Run design-system-audit before this skill to identify CSS patterns that deviate from the design system.
- **bundle-analysis** (eskill-frontend): Follow up with bundle-analysis after this skill to measure the size impact of CSS optimizations.
