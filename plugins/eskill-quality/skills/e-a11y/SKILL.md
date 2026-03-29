---
name: e-a11y
description: "Scans HTML, JSX, Vue, and Svelte files for WCAG accessibility violations. Use when auditing web accessibility, preparing for a11y reviews, or checking new components for issues. Also applies when: 'check accessibility', 'missing alt tags', 'a11y audit', 'WCAG compliance', 'screen reader support'."
---

# Accessibility Scanner

This skill scans frontend code for accessibility violations by matching structural patterns in HTML, JSX, Vue, Svelte, and other template formats against WCAG 2.1 success criteria. It identifies missing attributes, incorrect ARIA usage, keyboard navigation gaps, and semantic structure issues.

## Prerequisites

- A project containing frontend markup files (HTML, JSX, TSX, Vue, Svelte, or template engine files).
- The eMCP filesystem, fs_search, and egrep_search servers available for scanning and pattern matching.
- Knowledge of the target WCAG level (A, AA, or AAA) or willingness to default to WCAG 2.1 AA.

## Step 1: Identify Frontend Files

Locate all files containing markup that will be rendered in a browser.

1. Use `filesystem` to search for files matching these patterns:
   - HTML files: `**/*.html`, `**/*.htm`
   - React/JSX files: `**/*.jsx`, `**/*.tsx`
   - Vue single-file components: `**/*.vue`
   - Svelte components: `**/*.svelte`
   - Angular templates: `**/*.component.html`
   - Template engine files: `**/*.ejs`, `**/*.hbs`, `**/*.pug`, `**/*.njk`, `**/*.jinja2`
   - Markdown with embedded HTML: `**/*.mdx`
2. Exclude files in dependency directories (`node_modules/`, `vendor/`), build output (`dist/`, `build/`), and test fixtures unless explicitly included.
3. Record the total count of frontend files to scan.
4. If no frontend files are found, report that the project does not appear to have frontend code and exit.

## Step 2: Scan for Common Accessibility Violations

Use `ast_search` to find structural patterns that indicate accessibility violations. Execute each pattern check across all identified frontend files.

### Images Without Alt Attributes

WCAG 1.1.1 (Level A): Non-text Content.

- Search for `<img>` elements and `<Image>` components that do not have an `alt` attribute.
- In JSX: search for `JSXOpeningElement` with name `img` or `Image` that lacks a `JSXAttribute` named `alt`.
- In HTML: search for `<img` tags without `alt=`.
- Note: decorative images should have `alt=""` (empty alt), not a missing alt attribute. Both missing alt and absent alt attribute are violations.
- Also check for `<input type="image">` elements without alt text.
- Flag: each image element missing the alt attribute, with file and line number.

### Form Inputs Without Labels

WCAG 1.3.1 (Level A): Info and Relationships. WCAG 3.3.2 (Level A): Labels or Instructions.

- Search for `<input>`, `<select>`, `<textarea>` elements.
- For each, verify that it has one of:
  - An associated `<label>` element (matching `for` attribute to the input's `id`).
  - An `aria-label` attribute directly on the element.
  - An `aria-labelledby` attribute referencing a visible label element.
  - A wrapping `<label>` element (the input is a child of a `<label>`).
- Exclude `<input type="hidden">` (hidden inputs do not need labels).
- Exclude `<input type="submit">` and `<input type="button">` (these use the `value` attribute as their label).
- Flag each input without any labeling mechanism.

### Missing ARIA Roles on Interactive Elements

WCAG 4.1.2 (Level A): Name, Role, Value.

- Search for elements that have event handlers (onClick, onKeyDown, onChange) but are not natively interactive HTML elements.
- Non-interactive elements with handlers: `<div>`, `<span>`, `<p>`, `<li>`, `<td>`, `<section>`, `<article>`.
- These must have:
  - An appropriate `role` attribute (e.g., `role="button"`, `role="link"`, `role="tab"`).
  - Keyboard event support (`onKeyDown` or `onKeyPress` in addition to `onClick`).
  - A `tabIndex` attribute to make them focusable (`tabIndex={0}` or `tabIndex="0"`).
- Flag elements with click handlers that lack role, keyboard support, or focusability.

### Click Handlers on Non-Interactive Elements

WCAG 2.1.1 (Level A): Keyboard.

- Search for `<div>`, `<span>`, and other non-interactive elements with `onClick` handlers.
- Verify that each also has:
  - `role="button"` (or another appropriate interactive role).
  - `tabIndex={0}` to enable keyboard focus.
  - `onKeyDown` or `onKeyPress` handler that responds to Enter and Space keys.
- If any of these are missing, the element is not keyboard accessible.
- Suggest replacing with a native `<button>` element where appropriate.

### Missing Skip Navigation Links

WCAG 2.4.1 (Level A): Bypass Blocks.

- Search for the main page template or layout component.
- Check for a skip navigation link at the beginning of the document body:
  - An `<a>` element with `href="#main-content"` or similar anchor linking to the main content area.
  - The link should be one of the first focusable elements in the DOM order.
- Check that the target of the skip link exists (an element with the matching `id`).
- Flag if no skip navigation mechanism is found in the main layout.

### Empty Links and Buttons

WCAG 2.4.4 (Level A): Link Purpose. WCAG 4.1.2 (Level A): Name, Role, Value.

- Search for `<a>` elements that have no text content and no `aria-label` or `aria-labelledby` attribute.
- Search for `<button>` elements that have no text content and no `aria-label` or `aria-labelledby` attribute.
- Icon-only buttons must have an `aria-label` describing the action.
- Links that contain only an image must have alt text on the image to serve as the link text.
- Flag each empty interactive element.

### Auto-Playing Media

WCAG 1.4.2 (Level A): Audio Control.

- Search for `<video>` and `<audio>` elements with `autoplay` attribute.
- If `autoplay` is present, verify that:
  - `muted` attribute is also present (for video), or
  - A mechanism to pause/stop the media is immediately available.
- Search for embedded players (iframes to YouTube, Vimeo) and check for autoplay parameters in the URL.
- Flag auto-playing media without user control.

### Missing Language Attribute

WCAG 3.1.1 (Level A): Language of Page.

- Search the main HTML template for the `<html>` element.
- Verify that it has a `lang` attribute set to a valid language code (e.g., `lang="en"`, `lang="fr"`).
- If the project is a SPA (single-page application), check the index.html or equivalent entry point.
- Flag if the `lang` attribute is missing from the root HTML element.

### Color-Only Information Indicators

WCAG 1.4.1 (Level A): Use of Color.

- Search for CSS class names or inline styles that conditionally apply color-based styling based on state (e.g., `className={error ? 'text-red' : 'text-green'}`).
- Check whether a text alternative or icon accompanies the color change.
- This check is heuristic and may produce false positives. Flag for manual review rather than as definitive violations.

### Inaccessible Custom Components

WCAG 4.1.2 (Level A): Name, Role, Value.

- Search for custom dropdown, modal, dialog, and tab components.
- For modals/dialogs: check for `role="dialog"` or `role="alertdialog"`, `aria-modal="true"`, and focus trap implementation.
- For custom dropdowns: check for `role="listbox"` or `role="combobox"`, `aria-expanded`, and keyboard navigation support.
- For tab components: check for `role="tablist"`, `role="tab"`, `role="tabpanel"`, and `aria-selected` usage.
- Flag custom interactive components that lack appropriate ARIA roles and keyboard support.

## Step 3: Search Across All Frontend Files

Execute each pattern from Step 2 against the complete set of frontend files identified in Step 1.

1. Run `ast_search` queries for structural patterns (missing attributes, incorrect element usage).
2. Use `egrep_search` for patterns that are more easily caught with regex (autoplay attributes, lang attributes, ARIA attribute presence). The trigram index makes `egrep_search` faster than `fs_search` for scanning all frontend files for `aria-*` attributes, `role=` patterns, `tabIndex`, and other accessibility markers across the entire codebase.
3. Collect all matches with file path and line number.
4. De-duplicate findings that may be flagged by multiple pattern checks.

## Step 4: Validate ARIA Attribute Usage

Check that ARIA attributes, when present, are used correctly.

1. Search for all elements with `aria-*` attributes using `egrep_search` for fast pattern matching (e.g., `aria-hidden`, `aria-label`, `aria-expanded`, `role=`) or `ast_search` for structural validation.
2. Validate common correctness rules:
   - `aria-hidden="true"` should not be on focusable elements (elements with `tabIndex`, `<a>`, `<button>`, `<input>`). This makes the element invisible to assistive technology while still being focusable, which is confusing.
   - `role="presentation"` or `role="none"` should not be on elements that have semantic meaning needed for accessibility.
   - `aria-labelledby` and `aria-describedby` should reference IDs that actually exist in the document.
   - `aria-expanded`, `aria-checked`, `aria-selected` should have boolean or valid values, not always be static.
   - `aria-live` regions should use appropriate politeness settings (`polite` for non-urgent, `assertive` for urgent).
3. Flag incorrect ARIA usage. Incorrect ARIA is often worse than no ARIA at all, as it provides misleading information to assistive technology.

## Step 5: Verify Heading Hierarchy

WCAG 1.3.1 (Level A): Info and Relationships. WCAG 2.4.6 (Level AA): Headings and Labels.

1. For each page template or route component, extract all heading elements (`h1` through `h6`) using `ast_search`.
2. Record the heading level and order of appearance.
3. Check the hierarchy rules:
   - There should be exactly one `h1` per page (or per route in a SPA).
   - Heading levels should not skip: `h1` followed by `h3` (skipping `h2`) is a violation.
   - Heading levels should form a logical outline of the page content.
4. For SPA frameworks (React, Vue, Angular): check each route-level component for its heading structure.
5. Flag pages with no `h1`, multiple `h1` elements, or skipped heading levels.
6. Report the heading outline for each page to help developers visualize the structure.

## Step 6: Check Keyboard Navigation Support

WCAG 2.1.1 (Level A): Keyboard.

1. Search for `tabIndex` usage across all frontend files:
   - `tabIndex` values greater than 0 are problematic (they disrupt the natural tab order). Flag these.
   - `tabIndex={-1}` is acceptable for programmatic focus management.
   - `tabIndex={0}` is acceptable for making custom elements focusable.
2. Search for focus management in JavaScript/TypeScript code:
   - Calls to `.focus()` method: verify they are used for appropriate focus management (e.g., after dialog open, after navigation).
   - Focus trap implementations in modals: verify that focus does not escape the modal when it is open.
3. Check for visible focus indicators:
   - Search CSS for `outline: none` or `outline: 0` without a replacement focus style.
   - If focus outlines are removed, verify that a custom focus indicator is provided (e.g., box-shadow, border change).
   - Flag blanket removal of focus outlines without replacement as a keyboard accessibility issue.

## Step 7: Categorize Findings by WCAG Level

Assign each finding to a WCAG conformance level to help prioritize remediation.

### Level A (Must Fix)

These are the minimum requirements for accessibility. Failure to meet these creates significant barriers:
- Missing alt text on images.
- Form inputs without labels.
- Missing keyboard access (click handlers without keyboard support).
- Auto-playing media without controls.
- Missing page language.
- Empty links and buttons.
- Missing skip navigation.

### Level AA (Should Fix)

These are the standard target for most organizations and often legally required:
- Heading hierarchy violations.
- Insufficient color contrast (noted for manual verification).
- Focus indicator removal without replacement.
- Incorrect ARIA usage.

### Level AAA (Enhancement)

These represent the highest level of accessibility and are aspirational for most projects:
- Sign language interpretation for video.
- Extended audio description.
- Reading level considerations.

## Step 8: Generate the Accessibility Report

Structure the report for both developers and accessibility reviewers.

### Report Header

- Project name and scan timestamp.
- Total frontend files scanned.
- Frameworks and template languages detected.
- Total findings count by WCAG level.

### Findings by Category

For each type of violation found, create a section:
- **Category name** (e.g., "Images Without Alt Attributes").
- **WCAG criterion**: the specific success criterion violated (e.g., "1.1.1 Non-text Content").
- **WCAG level**: A, AA, or AAA.
- **Finding count** in this category.
- **For each finding**:
  - File path (absolute, forward slashes).
  - Line number.
  - Code snippet showing the violation.
  - Description of the issue.
  - Suggested fix with corrected code example.

### Categories Checked with No Findings

List categories that were scanned but produced no findings, confirming they were checked.

## Step 9: Generate the Summary

Provide an actionable overview at the top of the report.

- Total findings by WCAG level (A, AA, AAA).
- Most common violation type.
- Top 5 most affected files or components.
- Estimated effort to remediate (based on finding count and complexity).
- Recommended priority order:
  1. Level A violations (must fix for basic accessibility).
  2. Incorrect ARIA usage (can make things worse than no ARIA).
  3. Keyboard navigation gaps.
  4. Level AA violations.
  5. Level AAA enhancements.
- Overall accessibility posture: a brief narrative assessment.

## Reference: WCAG 2.1 Success Criteria for Common Violations

| Criterion | Level | Description                                    | Common Violation                        |
|-----------|-------|------------------------------------------------|-----------------------------------------|
| 1.1.1     | A     | Non-text Content                               | Images without alt attributes           |
| 1.3.1     | A     | Info and Relationships                         | Form inputs without labels, headings    |
| 1.4.1     | A     | Use of Color                                   | Color-only status indicators            |
| 1.4.2     | A     | Audio Control                                  | Auto-playing media                      |
| 1.4.3     | AA    | Contrast (Minimum)                             | Insufficient text contrast              |
| 2.1.1     | A     | Keyboard                                       | Click-only interactive elements         |
| 2.4.1     | A     | Bypass Blocks                                  | Missing skip navigation                 |
| 2.4.4     | A     | Link Purpose (In Context)                      | Empty or ambiguous links                |
| 2.4.6     | AA    | Headings and Labels                            | Skipped heading levels                  |
| 3.1.1     | A     | Language of Page                               | Missing lang attribute                  |
| 3.3.2     | A     | Labels or Instructions                         | Unlabeled form controls                 |
| 4.1.2     | A     | Name, Role, Value                              | Custom widgets without ARIA             |

## Edge Cases

- **Dynamically rendered content**: Components that render different markup based on state or props may have accessibility violations only in certain states. Check all significant render paths, not just the default.
- **Third-party component libraries**: Components from Material UI, Ant Design, or Chakra UI may handle ARIA internally. Avoid flagging violations that are the library's responsibility unless the wrapper overrides accessible behavior.
- **SVG icons without text alternatives**: Inline SVGs used as icons need `role="img"` and `aria-label` or a visually hidden text label. Purely decorative SVGs need `aria-hidden="true"`.
- **Single-page app route changes**: SPA navigation does not trigger a page load, so screen readers may not announce route changes. Check for focus management and live region announcements on route transitions.
- **Accessible names from CSS content**: Elements styled with `content: "text"` in CSS are not exposed to the accessibility tree in all browsers. Flag reliance on CSS-generated content for meaningful text.

## Related Skills

- **e-tokens** (eskill-frontend): Run e-tokens alongside this skill to check that design system components meet accessibility standards.
- **e-lint** (eskill-quality): Run e-lint alongside this skill to enforce accessibility-related coding conventions.
