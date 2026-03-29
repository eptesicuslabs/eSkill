---
name: e-design
description: "Creates distinctive, production-grade frontend interfaces with high visual craft. Use when building UI components, pages, layouts, or applications where design quality matters. Also applies when: 'build a landing page', 'create a dashboard', 'design a component', 'make a UI', 'style this page', 'make it look good', 'build a form', 'create a modal'."
---

# Frontend Design

This skill produces frontend interfaces that are visually distinctive and production-ready. It treats design quality as a first-class engineering concern — not an afterthought. The workflow moves from design intent through visual direction to refined implementation, using eMCP tools for codebase analysis and file generation.

## Core Design Philosophy

Generic AI-generated UI has a recognizable signature: safe blues, oversized padding, stock illustrations, rounded-everything, gradient buttons. This skill exists to avoid that. Every design decision should be intentional and traceable to a specific goal — brand tone, information hierarchy, user task flow, or aesthetic direction.

**Principles**:

1. **Opinionated by default.** Pick a clear visual direction rather than hedging with safe neutrals. A bold choice that serves the content is better than a bland choice that offends nobody.
2. **Typography is structure.** Font selection, scale, weight contrast, and line height do more work than color. Get type right first.
3. **Density is a feature.** Generous whitespace is one tool, not the only tool. Dense UIs (dashboards, data tables, admin panels) serve power users. Match density to the audience.
4. **Motion is communication.** Transitions signal relationships. A 150ms ease-out on hover tells the user "this is interactive." An entrance animation on a modal establishes hierarchy. If motion doesn't communicate, remove it.
5. **Color is meaning.** Every color should earn its place. Use the minimum palette that communicates hierarchy, state, and brand. One accent color used consistently outperforms five used loosely.

## Prerequisites

- A frontend project with at least one framework (React, Vue, Angular, Svelte, Astro, or plain HTML/CSS).
- A target destination (new page, new component, or modification of existing UI).

## Workflow

### Step 1: Understand Design Intent

Before writing any code, establish what the interface needs to accomplish.

Extract from the user's request:

| Dimension        | Question                                                      |
|------------------|---------------------------------------------------------------|
| **Purpose**      | What task does this UI serve? What does the user accomplish?  |
| **Audience**     | Consumer-facing (polish, delight) or internal (density, speed)? |
| **Content**      | What data/content will this display? How much of it?          |
| **Tone**         | Playful, corporate, minimal, technical, editorial, brutalist? |
| **Constraints**  | Must it match an existing design system, brand, or style?     |
| **Scope**        | Full page, isolated component, layout shell, or single widget?|

If the user provides a reference image or screenshot, use `image_metadata` to inspect dimensions, format, and EXIF data. Use `image_convert` to convert between formats if needed for the target platform. If they provide a URL, use `fetch_url` from the eMCP fetch server to retrieve the page content and `browser_navigate` to capture a visual reference.

If the request is ambiguous (e.g., "make it look good"), do not ask for clarification. Instead, analyze the existing codebase for visual direction cues and make a decisive choice. State the direction you chose and why.

### Step 2: Analyze the Existing Project

Use `filesystem` tools (fs_list, fs_read) to survey the project structure. Determine:

**Framework and tooling**:

| Signal                     | Implication                                   |
|----------------------------|-----------------------------------------------|
| `react` in dependencies    | JSX components                                |
| `next` in dependencies     | React with file-based routing, RSC awareness  |
| `vue` in dependencies      | SFC templates                                 |
| `nuxt` in dependencies     | Vue with file-based routing                   |
| `@angular/core`            | Angular component model                       |
| `svelte` in dependencies   | Svelte component model                        |
| `astro` in dependencies    | Island architecture, multi-framework           |
| `tailwindcss`              | Utility-first CSS                             |
| `styled-components`        | CSS-in-JS                                     |
| `@emotion/react`           | CSS-in-JS (Emotion)                           |
| `*.module.css` files       | CSS Modules                                   |
| `sass` in dependencies     | SCSS preprocessing                            |
| `vanilla-extract`          | Zero-runtime CSS-in-TS                        |
| `open-props` or `pollen`   | CSS custom property frameworks                |

**Visual baseline**: Read two or three existing pages or components using `ast_search` from the eMCP AST server and `filesystem` tools. Extract:

- Color palette in use (CSS variables, Tailwind config colors, or hardcoded values).
- Typography stack (font families, size scale, weight usage).
- Spacing rhythm (common margin/padding values, grid gaps).
- Component patterns (card structures, button variants, form layouts).
- Layout approach (CSS Grid, Flexbox, container queries, or framework-specific layout).
- Animation patterns (transitions, keyframes, or animation libraries in use).

Use `ast_search` to check for existing component libraries (imports from a shared components directory) and whether there is a theme or token file.

If this is a greenfield project with no existing styles, skip to Step 3 with full creative freedom.

### Step 3: Establish Visual Direction

Define the design language for this implementation. This is the critical step that separates craft from generic output.

**Typography**:

Select a type system. If the project already has fonts, respect them. If starting fresh, choose a pairing that matches the tone:

| Tone          | Heading                     | Body                       | Character                    |
|---------------|-----------------------------|----------------------------|------------------------------|
| Technical     | JetBrains Mono, Space Grotesk | Inter, IBM Plex Sans     | Precise, engineered          |
| Editorial     | Playfair Display, Lora       | Source Serif Pro, Charter | Literary, authoritative      |
| Minimal       | Inter, Helvetica Neue        | Inter, System UI          | Clean, invisible             |
| Playful       | Sora, Outfit                 | Nunito, DM Sans           | Friendly, approachable       |
| Corporate     | Montserrat, Poppins          | Open Sans, Noto Sans      | Professional, trustworthy    |
| Brutalist     | Space Mono, JetBrains Mono   | System UI, monospace      | Raw, unpolished              |
| Dashboard     | Geist, Inter                 | Geist, Inter              | Data-dense, scannable        |

Define the type scale. Use a modular scale (1.125 minor second through 1.333 perfect fourth) or a custom scale that serves the content density:

```
--text-xs:   0.75rem    /* 12px — captions, labels */
--text-sm:   0.875rem   /* 14px — secondary text, table cells */
--text-base: 1rem       /* 16px — body text */
--text-lg:   1.125rem   /* 18px — large body, lead text */
--text-xl:   1.25rem    /* 20px — section headings */
--text-2xl:  1.5rem     /* 24px — page subheadings */
--text-3xl:  1.875rem   /* 30px — page headings */
--text-4xl:  2.25rem    /* 36px — hero text */
--text-5xl:  3rem       /* 48px — display text */
```

Adjust the scale to match content density. Data-heavy UIs compress the scale; marketing pages expand it.

**Color palette**:

Build a minimal, purposeful palette. Start with surface and text colors, then add accent.

```
Surface:  Background → Surface → Elevated (3 levels of depth)
Text:     Primary → Secondary → Muted (3 levels of emphasis)
Border:   Default → Subtle (structural lines)
Accent:   Primary action color (one, used sparingly)
Semantic: Success → Warning → Error → Info (functional states)
```

Color rules:
- Dark text on light surfaces needs >= 4.5:1 contrast ratio (WCAG AA).
- Adjacent surfaces need enough contrast to establish depth without borders.
- Accent appears only on interactive elements and active states.
- If the project has an existing palette, use it. If it has partial tokens, extend them consistently.

For dark mode: do not just invert. Reduce surface lightness, lower text brightness slightly, and desaturate accent colors by 10-15% to reduce eye strain.

**Spacing and layout**:

Use a consistent spacing scale based on a base unit (typically 4px or 8px):

```
--space-1:  0.25rem   /* 4px */
--space-2:  0.5rem    /* 8px */
--space-3:  0.75rem   /* 12px */
--space-4:  1rem      /* 16px */
--space-6:  1.5rem    /* 24px */
--space-8:  2rem      /* 32px */
--space-12: 3rem      /* 48px */
--space-16: 4rem      /* 64px */
--space-24: 6rem      /* 96px */
```

Layout rules:
- Group related elements with tight spacing; separate groups with generous spacing.
- Content width: 65-75ch for reading, unconstrained for data tables, 1200-1400px max for pages.
- Use CSS Grid for two-dimensional layouts, Flexbox for one-dimensional alignment.
- Prefer container queries over media queries for component-level responsiveness when browser support allows.

**Interaction and motion**:

Define transition defaults:

```
--duration-fast:   100ms   /* hover states, toggles */
--duration-normal: 200ms   /* panels, dropdowns */
--duration-slow:   300ms   /* page transitions, modals */
--easing-default:  cubic-bezier(0.4, 0, 0.2, 1)   /* standard */
--easing-enter:    cubic-bezier(0, 0, 0.2, 1)       /* deceleration */
--easing-exit:     cubic-bezier(0.4, 0, 1, 1)       /* acceleration */
```

Interaction rules:
- Every interactive element needs a visible hover state and focus ring.
- Focus rings: 2px solid with offset, using the accent color at reduced opacity.
- Disabled states: reduce opacity to 0.5 and set `cursor: not-allowed`.
- Loading states: use skeleton screens or subtle pulse animations, not spinners.

### Step 4: Build the Component Structure

Design the component hierarchy before writing markup.

Map the interface to a component tree. For each component, define:

- **Responsibility**: What this component renders and controls.
- **Props/inputs**: External data and configuration.
- **Internal state**: What the component manages itself.
- **Children/slots**: What content flows through it.
- **Variants**: Named visual variations (size, color, emphasis).

Use `ast_search` from the eMCP AST server to check whether similar components already exist in the project. If a match exists, reuse or extend it rather than creating a duplicate.

For complex interfaces, sketch the layout with a comment block first:

```
/* Layout structure:
   ┌─────────────────────────────────┐
   │ Header (sticky)                 │
   ├────────┬────────────────────────┤
   │ Sidebar│ Main content           │
   │ (nav)  │ ┌────────┐ ┌────────┐ │
   │        │ │ Card 1 │ │ Card 2 │ │
   │        │ └────────┘ └────────┘ │
   │        │ ┌────────────────────┐ │
   │        │ │ Data table         │ │
   │        │ └────────────────────┘ │
   ├────────┴────────────────────────┤
   │ Footer                          │
   └─────────────────────────────────┘
*/
```

### Step 5: Implement the Interface

Write the component code, styles, and layout. Follow the conventions detected in Step 2 and the visual direction from Step 3.

**Markup priorities**:
1. Semantic HTML elements (`<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`) over generic `<div>`.
2. Landmark roles where framework components obscure native semantics.
3. `aria-label` on icon-only buttons and non-text interactive elements.
4. `aria-live` regions for dynamic content updates.

**Styling priorities**:
1. Design tokens over hardcoded values — always.
2. Logical properties (`margin-inline`, `padding-block`) for RTL support.
3. `clamp()` for fluid typography and spacing where appropriate.
4. Relative units (`rem`, `em`, `%`, `ch`, `vw/vh`) over absolute `px` for scalable layouts. Use `px` only for borders, shadows, and outlines.
5. `prefers-reduced-motion` media query wrapping all animations and transitions.
6. `prefers-color-scheme` if the project supports system theme detection.

**Component code quality**:
- Props that affect appearance use enums or literal unions, not open strings.
- Default prop values produce a usable component with no configuration.
- Event handlers are optional. Components render correctly without them.
- Children/slots have sensible fallback content or render nothing cleanly.
- Components do not fetch data. They receive data via props and render it.

**Accessibility baseline** (non-negotiable):
- All images have `alt` text (descriptive for content images, empty for decorative).
- Form controls have associated `<label>` elements or `aria-label`.
- Color is never the sole indicator of state (always pair with icon, text, or pattern).
- Tab order follows visual order. No `tabindex` greater than 0.
- Interactive elements are keyboard-operable (Enter/Space to activate, Escape to dismiss).
- Modals trap focus and return focus on close.

Use `filesystem` tools (fs_write, fs_edit) to create or modify files. Write each component to its own file following the project's file organization convention.

### Step 6: Refine Visual Details

After the structure is built, apply craft-level refinements that separate polished UI from prototype quality.

**Shadows and elevation**:
Use layered shadows for realistic depth. A single `box-shadow` looks flat. Multiple shadows create natural light:

```css
/* Subtle elevation (cards, dropdowns) */
--shadow-sm:
  0 1px 2px rgba(0, 0, 0, 0.04),
  0 1px 3px rgba(0, 0, 0, 0.06);

/* Medium elevation (popovers, floating panels) */
--shadow-md:
  0 2px 4px rgba(0, 0, 0, 0.04),
  0 4px 8px rgba(0, 0, 0, 0.06),
  0 8px 16px rgba(0, 0, 0, 0.04);

/* High elevation (modals, command palettes) */
--shadow-lg:
  0 4px 8px rgba(0, 0, 0, 0.04),
  0 8px 16px rgba(0, 0, 0, 0.06),
  0 16px 32px rgba(0, 0, 0, 0.08),
  0 32px 64px rgba(0, 0, 0, 0.04);
```

**Micro-interactions**:
- Buttons: subtle scale (`transform: scale(0.98)`) on active, background color shift on hover.
- Inputs: border color transitions on focus, label animation for floating labels.
- Cards: slight shadow elevation on hover if the card is clickable.
- Toggles: smooth track and thumb color transitions.
- Tooltips: fade in with slight upward translate for perceived lightness.

**Empty states**:
Design empty states as first-class views, not afterthoughts. An empty table, an empty search result, or a zero-data dashboard should show:
- A clear description of why it is empty.
- A specific action to populate it (if applicable).
- An illustration or icon that matches the visual tone (not a generic sad face).

**Loading states**:
- Skeleton screens that match the layout shape of the loaded content.
- Pulse animation: `opacity` oscillating between 0.4 and 1.0 with `--duration-slow` and `--easing-default`.
- Skeleton color: slightly lighter than the surface background.
- Never show a blank screen. The first paint should show structure.

**Error states**:
- Inline validation with specific messages (not "invalid input").
- Error borders and text using the semantic error color.
- Error messages appear below the input, not in alerts or toasts.
- Form-level errors summarized at the top with anchor links to each invalid field.

### Step 7: Responsive Implementation

Implement responsive behavior as part of the design, not as a separate pass.

**Breakpoint strategy**:

Use the project's existing breakpoints if defined. Otherwise, use content-driven breakpoints:

```css
/* Mobile-first breakpoints */
--bp-sm:  640px    /* Large phones, small tablets */
--bp-md:  768px    /* Tablets */
--bp-lg:  1024px   /* Small desktops, landscape tablets */
--bp-xl:  1280px   /* Standard desktops */
--bp-2xl: 1536px   /* Large screens */
```

**Responsive patterns**:
- Navigation: full horizontal nav on desktop, hamburger or bottom tab bar on mobile.
- Sidebars: visible on desktop, collapsible drawer on tablet, hidden behind toggle on mobile.
- Grids: reduce columns as viewport narrows. `grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))` handles most card grids.
- Tables: horizontal scroll on mobile with sticky first column, or restructure to card layout.
- Typography: use `clamp()` for fluid scaling. Heading at `clamp(1.5rem, 2vw + 1rem, 2.25rem)` scales smoothly without breakpoint jumps.
- Touch targets: minimum 44x44px on mobile for all interactive elements (WCAG 2.5.5).

Use `e-responsive` from eskill-frontend to verify the responsive implementation.

### Step 8: Validate Output

Before reporting completion, verify the implementation:

1. **Token compliance**: Run `e-tokens` from eskill-frontend to confirm no hardcoded values bypass the design system.
2. **Accessibility**: Run `e-a11y` from eskill-quality to verify WCAG compliance.
3. **CSS quality**: Run `e-css` from eskill-frontend to catch redundancy or specificity issues.
4. **File integrity**: Use `filesystem` tools (fs_list) to confirm all generated files are in the correct locations.
5. **Import verification**: Use `ast_search` to confirm all imports resolve (no broken references to generated components).
6. **Visual check**: If `browser_navigate` from the eMCP browser server is available, navigate to the rendered output and verify visual correctness.

Report the implementation to the user with:
- Files created or modified (paths and purpose).
- Design decisions made and rationale.
- Any tradeoffs or compromises noted.
- Suggested follow-up refinements.

## Edge Cases

- **No framework (static HTML/CSS)**: Generate vanilla HTML with a `<style>` block or linked CSS file. Use CSS custom properties for tokens. No build step required.
- **Multiple frameworks in monorepo**: Ask the user which package the UI targets. Do not guess.
- **Existing design system with incomplete tokens**: Extend the token set for gaps. Add new tokens in the same file, following the existing naming convention. Flag the additions.
- **Dark mode requirement**: Implement using CSS custom properties that switch values based on `[data-theme="dark"]` attribute or `prefers-color-scheme` media query, whichever the project uses.
- **RTL language support**: Use CSS logical properties (`inline-start`/`inline-end` instead of `left`/`right`). Set `dir="auto"` on text containers if content language is dynamic.
- **Performance-sensitive context**: For pages with many DOM nodes (long lists, data tables), note where virtualization would be needed. Do not implement virtualization unless requested, but flag it.
- **Server components (Next.js, Nuxt)**: Default to server components. Add `'use client'` only when the component uses state, effects, event handlers, or browser APIs.
- **Email templates**: HTML email requires inline styles, table-based layouts, and no CSS custom properties. Switch to a completely different rendering approach.
- **Print styles**: Add `@media print` rules if the content is likely to be printed (reports, invoices, documentation). Hide navigation, reduce color usage, and ensure page breaks fall between logical sections.

## Anti-Patterns to Avoid

These patterns produce the generic "AI-generated" look. Avoid them unless the design direction specifically calls for them:

| Anti-Pattern                        | Instead                                            |
|-------------------------------------|----------------------------------------------------|
| Gradient buttons as default         | Solid color with subtle hover state                |
| Oversized border-radius on cards    | Match radius to content density (4-8px for data, 12-16px for marketing) |
| Blue as default accent color        | Choose accent from brand or content context        |
| Excessive whitespace everywhere     | Match spacing density to audience and content type |
| Drop shadows on every element       | Shadows only where elevation communicates hierarchy|
| Stock illustration placeholders     | Icons or empty states that match the visual tone   |
| Center-aligned body text            | Left-align body text (or right-align for RTL)      |
| Rainbow semantic colors             | Restrained palette; let one accent color dominate  |
| Generic sans-serif everywhere       | Intentional type pairing that sets the tone        |
| Rounded pill buttons by default     | Match button shape to the design system's character|

## Related Skills

- **e-component** (eskill-frontend): Use e-component for generating boilerplate component files. Use e-design when the visual design and interaction quality of the component matters.
- **e-tokens** (eskill-frontend): Run e-tokens after e-design to verify token compliance.
- **e-responsive** (eskill-frontend): Run e-responsive after e-design to verify responsive behavior.
- **e-css** (eskill-frontend): Run e-css after e-design to clean up generated CSS.
- **e-a11y** (eskill-quality): Run e-a11y after e-design to verify WCAG compliance.
- **e-stories** (eskill-frontend): Follow up with e-stories to generate Storybook stories for new components.
