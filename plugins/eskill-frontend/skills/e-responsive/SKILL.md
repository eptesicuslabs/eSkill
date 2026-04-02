---
name: e-responsive
description: "Analyzes CSS and component code for responsive design issues including missing breakpoints, container query opportunities, fixed widths, and overflow-prone patterns. Use when reviewing responsive layouts, auditing mobile support, or fixing layout bugs. Also applies when: 'check responsive design', 'mobile layout issues', 'does this work on mobile', 'find overflow problems', 'container queries'."
---

# Responsive Layout Check

This skill analyzes CSS and component code to identify responsive design problems. It detects fixed dimensions that cause overflow on small screens, missing breakpoints, container query opportunities, viewport-unit misuse, and layout patterns that break across device sizes.

## Prerequisites

- A frontend project with CSS, SCSS, Tailwind, or CSS-in-JS stylesheets.
- Target files or directories to analyze.

## Workflow

### Step 1: Identify the Project's Responsive Strategy

Before scanning for issues, determine what responsive mechanisms the project uses. Use `filesystem` tools (fs_read) to check these sources:

**Media query breakpoints**:

| Source                     | How to Extract Breakpoints                     |
|----------------------------|-------------------------------------------------|
| Tailwind config            | Read `theme.screens` from `tailwind.config.*`   |
| SCSS variables             | Search `_variables.scss` for `$breakpoint-*`     |
| CSS custom properties      | Search for `--breakpoint-*` in global CSS        |
| Media query constants (JS) | Search for exported breakpoint objects in theme files |
| CSS `@custom-media`        | Search for `@custom-media` rules                 |

If no explicit breakpoint system is found, use the common defaults as reference:

| Name   | Min Width | Typical Use           |
|--------|-----------|------------------------|
| sm     | 640px     | Large phones landscape |
| md     | 768px     | Tablets portrait       |
| lg     | 1024px    | Tablets landscape      |
| xl     | 1280px    | Desktops               |
| 2xl    | 1536px    | Large desktops         |

**Container queries**: Use `egrep_search` to search for `container-type`, `@container`, and `container-name` in stylesheets. Container queries (CSS `@container`) have been baseline-stable since February 2023 with ~95% global browser support (Chrome 106+, Firefox 110+, Safari 16+, Edge 106+). They provide component-level responsive behavior based on the container's dimensions rather than the viewport.

The distinction matters for this audit:
- **Media queries**: correct for viewport-level layout decisions (page grid, navigation collapse, overall structure).
- **Container queries**: correct for component-level responsive behavior (a card that adapts when placed in a sidebar vs. a main content area).

If the project uses neither media queries nor container queries on layout-affecting components, flag it. If the project uses container queries appropriately on components, do not flag those components as "missing breakpoints."

Note: CSS container style queries for custom properties are supported in Chromium-based browsers (Chrome 111+, Edge 111+) but not yet in Firefox or Safari. Style queries on standard CSS properties beyond custom properties have limited support. Size container queries are universally stable across all major browsers.

### Step 2: Scan for Fixed Width Issues

Search for CSS properties that set fixed widths likely to cause horizontal overflow on small screens.

Use `egrep_search` to search stylesheets and component files for these patterns:

**Fixed pixel widths on containers**:
- `width: [value]px` where value exceeds 320px on non-icon, non-image elements.
- `min-width: [value]px` where value exceeds 320px.

**Fixed widths in inline styles**:
- Use `ast_search` from the eMCP AST server to find JSX/TSX `style` attributes containing `width` with pixel values.

For each match, record:

| Field       | Value                                      |
|-------------|---------------------------------------------|
| File        | Path to the file                            |
| Line        | Line number                                 |
| Property    | The CSS property (width, min-width, etc.)   |
| Value       | The fixed value found                       |
| Context     | The selector or component name              |
| Severity    | High (>768px), Medium (>480px), Low (>320px)|

Exclude these from violations:
- Max-width declarations (these constrain, not force, width).
- Width on known fixed-size elements (icons, avatars, logos) identified by class name or context.
- Width inside `@media` queries that already scope to larger screens.

### Step 3: Scan for Missing Breakpoints

Analyze components that have layout styling but no responsive adjustments.

Use `ast_search` to find component files that contain layout-related CSS (flexbox, grid, multi-column) but have no media query references.

Check for these layout properties without corresponding breakpoint adjustments:

| Layout Property         | Why It Needs Breakpoints                          |
|-------------------------|---------------------------------------------------|
| `display: flex` with `flex-direction: row` | Row layout may need to stack on mobile |
| `display: grid` with fixed `grid-template-columns` | Column count may need to reduce |
| `columns` property      | Multi-column text may be unreadable on mobile      |
| Fixed `gap` values      | Large gaps waste space on small screens            |
| `flex-basis` with pixel values | Fixed basis may overflow containers         |

For Tailwind projects, check for responsive prefixes. A component using `flex` and `gap-8` without any `sm:`, `md:`, or `lg:` variants on layout-affecting classes may need responsive adjustments.

For CSS/SCSS projects, check whether the file or its imported partials contain any `@media` or `@container` rules. A layout stylesheet with neither is a likely candidate for responsive issues.

**Container query opportunities**: Flag components that use media queries for behavior that depends on the component's own container rather than the viewport. Signs that a component should use container queries instead of media queries:
- The same component is rendered in containers of different widths (sidebar, main content, modal).
- The media query breakpoint does not correspond to a viewport width but to a content-width threshold.
- The component's layout change is contextual, not global.

### Step 4: Scan for Overflow-Prone Patterns

Search for CSS patterns known to cause horizontal or vertical overflow:

**Horizontal overflow triggers**:
- `white-space: nowrap` without `overflow: hidden` or `text-overflow: ellipsis` on the same element.
- `overflow-x: visible` (or no overflow-x) on elements with children that may exceed container width.
- `flex-shrink: 0` on elements inside a flex container without `overflow` handling on the container.
- Tables without `overflow-x: auto` on a wrapper.
- Pre-formatted text (`<pre>`, `<code>`) without overflow handling.

**Content overflow triggers**:
- Long words or URLs without `overflow-wrap: break-word` or `word-break: break-word`.
- Images without `max-width: 100%` or equivalent constraint.
- Iframes or embeds with fixed dimensions and no responsive wrapper.

Use `egrep_search` to search for these patterns in CSS and component files. For each match, note the file, line, pattern, and a brief explanation of the risk.

### Step 5: Check Viewport Unit Usage

Scan for viewport unit misuse that causes problems on mobile browsers:

**`100vh` on mobile**:
The `100vh` value does not account for mobile browser chrome (address bar, toolbar). On iOS Safari and Android Chrome, this causes content to be hidden behind the browser UI.

Search for `height: 100vh` and `min-height: 100vh`. Flag occurrences and recommend alternatives:
- `height: 100dvh` (dynamic viewport height — adjusts when mobile browser chrome appears/disappears).
- `height: 100svh` (small viewport height — the viewport size when browser chrome is fully visible, the safe minimum).
- `height: 100lvh` (large viewport height — the viewport size when browser chrome is fully hidden).
- `min-height: -webkit-fill-available` as a fallback for older browsers that lack `dvh`/`svh`/`lvh` support.

**`vw` without overflow protection**:
The `100vw` value includes the scrollbar width on desktop, causing horizontal overflow. Search for `width: 100vw` and `calc(100vw - ...)` patterns.

### Step 6: Check Image Responsiveness

Scan for image elements and styles that may cause layout issues:

Use `ast_search` to find `<img>` elements in component files and check for:

| Issue                        | What to Check                                |
|------------------------------|----------------------------------------------|
| Missing width/height attrs   | `<img>` without `width` and `height` causes layout shift |
| Fixed dimensions only        | `<img width="800">` without CSS `max-width: 100%` |
| Missing `sizes` attribute    | `<img srcset="...">` without `sizes` loads wrong image |
| No responsive source         | Large images served to mobile without srcset  |
| Background images            | `background-size: cover` without responsive variants |

Also check for CSS rules on images:
- `img` elements missing `max-width: 100%` or `width: 100%` in global or component styles.
- Fixed `height` on images without `object-fit` (causes distortion on different screen sizes).

### Step 7: Check Touch Target Sizes

Scan interactive elements for touch target sizes that are too small for mobile use:

WCAG 2.5.8 (Level AA) requires a minimum touch target of 24x24px. The recommended target is 44x44px (WCAG 2.5.5, Level AAA) or 48x48dp (Material Design). Flag targets below 24px as violations and targets between 24px and 44px as warnings.

Search for:
- Buttons, links, and inputs with explicit height or padding that result in targets smaller than 44px.
- Icon-only buttons without sufficient padding.
- Close buttons or action icons with small click areas.

Use `ast_search` to find interactive elements in component files, then check their associated styles for sizing.

### Step 8: Generate the Responsive Audit Report

Compile all findings into a structured report:

```
## Responsive Layout Audit

### Summary
- Files scanned: 32
- Total issues: 18
- Fixed width issues: 5
- Missing breakpoints: 4
- Overflow-prone patterns: 3
- Viewport unit issues: 2
- Image issues: 2
- Touch target issues: 2

### High Priority
| File | Line | Issue | Details |
|------|------|-------|---------|
| src/components/Sidebar.tsx | 15 | Fixed width | width: 800px causes overflow below 800px |
| src/pages/Dashboard.tsx | 42 | No breakpoints | Grid with 4 fixed columns, no responsive variant |

### Medium Priority
| File | Line | Issue | Details |
|------|------|-------|---------|
| src/components/Table.tsx | 8 | No overflow wrapper | Table may overflow container on mobile |
| src/layouts/Main.tsx | 22 | 100vh usage | height: 100vh hides content on mobile browsers |

### Recommendations
1. Replace fixed widths with max-width or responsive classes.
2. Add breakpoint variants to grid layouts (stack on mobile).
3. Wrap tables in overflow-x: auto containers.
4. Replace 100vh with 100dvh and add -webkit-fill-available fallback.
```

## Priority Classification

Assign priority levels to each issue based on its impact on usability:

| Priority | Criteria                                                    | Example                          |
|----------|-------------------------------------------------------------|----------------------------------|
| Critical | Content is inaccessible or hidden on common screen sizes    | Fixed 1200px width on main content |
| High     | Layout breaks or overflows on mobile devices                | Table without overflow wrapper    |
| Medium   | Layout is functional but suboptimal on some screen sizes    | No breakpoint adjustment on grid  |
| Low      | Minor visual issue that does not affect content access      | Touch target 40px instead of 44px |

Apply these priority levels in the audit report to guide triage.

## Edge Cases

- **Server-rendered content**: Pages with server-rendered HTML may have responsive styles in a global stylesheet rather than co-located with components. Check global CSS files and `<style>` blocks in layout templates.
- **Container queries**: If the project uses CSS container queries (`@container`) for component-level responsiveness, do not flag those components as missing breakpoints. Container queries and media queries are complementary, not interchangeable. A component using `@container` for its own layout and `@media` for viewport-level concerns is correctly implemented.
- **Print stylesheets**: Fixed widths in `@media print` blocks are intentional and should be excluded from the scan.
- **Email templates**: HTML email templates have different responsive constraints. If the target files are in an email template directory, adjust expectations (tables for layout are expected, viewport units are unsupported).
- **Canvas and WebGL**: Elements using `<canvas>` or WebGL renderers manage their own sizing. Exclude them from fixed-width checks.
- **Tailwind arbitrary values**: Tailwind classes like `w-[800px]` are equivalent to fixed pixel widths and should be flagged the same as inline styles.
- **CSS-in-JS responsive patterns**: Styled-components and Emotion use JavaScript template literals for media queries. Search for `@media` inside tagged template literals, not just in CSS files.

## Related Skills

- **e-tokens** (eskill-frontend): Run e-tokens before this skill to verify responsive breakpoints match design system guidelines.
- **e-css** (eskill-frontend): Follow up with e-css after this skill to address responsive CSS issues detected during layout checks.
- **e-render** (eskill-frontend): Use e-render to validate responsive behavior in a real browser at multiple viewport sizes. This skill analyzes code statically; e-render validates rendered output.
- **e-visual** (eskill-testing): Use e-visual to capture baselines at multiple viewport sizes for ongoing responsive regression detection.
