---
name: e-tokens
description: "Audits UI code for design system consistency by checking color tokens, spacing values, typography, and component usage against project standards. Use when enforcing design system adoption, reviewing UI PRs, or assessing visual consistency. Also applies when: 'check design system', 'are we using the right colors', 'audit design tokens', 'find hardcoded styles'."
---

# Design System Audit

This skill audits frontend code for design system consistency by identifying hardcoded values that should use design tokens, detecting unauthorized color and spacing values, and reporting typography and component usage violations.

## Prerequisites

- A frontend project with an established design system or token set (CSS custom properties, Tailwind config, theme file, or token JSON).
- Source files to audit (components, stylesheets, or an entire directory).

## Workflow

### Step 1: Locate Design Token Definitions

Use `filesystem` tools (fs_list, fs_read) to search for design token sources. Check these locations in order:

| Token Source               | Common Paths                                    |
|----------------------------|-------------------------------------------------|
| CSS custom properties      | `src/styles/variables.css`, `src/styles/tokens.css`, `:root` blocks in global CSS |
| Tailwind config            | `tailwind.config.js`, `tailwind.config.ts`      |
| Theme file (JS/TS)         | `src/theme.ts`, `src/styles/theme.ts`, `src/tokens/index.ts` |
| Design token JSON          | `tokens.json`, `src/tokens/*.json`, `.tokens/`  |
| SCSS variables             | `src/styles/_variables.scss`, `src/styles/_tokens.scss` |
| Styled-components theme    | `src/theme.ts`, `src/styles/theme.ts`           |
| CSS-in-JS constants        | `src/constants/styles.ts`, `src/styles/constants.ts` |

Read each token source and build a reference catalog organized by category:

- **Colors**: Background, text, border, shadow colors.
- **Spacing**: Margin, padding, gap values.
- **Typography**: Font families, sizes, weights, line heights.
- **Breakpoints**: Media query thresholds.
- **Borders**: Radius, width values.
- **Shadows**: Box shadow definitions.
- **Z-index**: Layer ordering values.

### Step 2: Establish the Token Vocabulary

From the token catalog built in Step 1, compile a lookup table mapping raw values to their token names.

Example for CSS custom properties:
```
#1a1a2e -> --color-background-primary
#e94560 -> --color-accent-error
4px     -> --spacing-xs
8px     -> --spacing-sm
16px    -> --spacing-md
```

Example for Tailwind:
```
#1a1a2e -> bg-primary (from theme.extend.colors.primary)
4px     -> p-1 (from default spacing scale)
```

This lookup table is the reference for detecting violations in subsequent steps.

### Step 3: Scan for Color Violations

Search the target files for hardcoded color values that should use tokens.

Use `ast_search` from the eMCP AST server to find string literals in style-related code. Additionally, use `shell_exec` from the eMCP shell server to run targeted searches:

**Hex colors**:
Search for patterns matching `#[0-9a-fA-F]{3,8}` in CSS, SCSS, JS, TS, JSX, and TSX files.

**RGB/RGBA/HSL values**:
Search for `rgb(`, `rgba(`, `hsl(`, `hsla(` function calls.

**Named colors**:
Search for CSS named colors (`red`, `blue`, `white`, `black`, etc.) used as property values. Exclude occurrences inside comments, variable names, and string content unrelated to styles.

For each match, check whether the value exists in the token lookup table from Step 2. If it does, record it as a violation with the recommended token. If it does not match any token, record it as an unknown value that may indicate a missing token or an unauthorized color.

Categorize each violation:

| Category          | Description                                      |
|-------------------|--------------------------------------------------|
| Token available   | A token exists for this value; use it            |
| Token missing     | No token matches; may need a new token defined   |
| Likely intentional| Value is in a test file, mock data, or SVG asset |

### Step 4: Scan for Spacing Violations

Search for hardcoded spacing values in style properties.

Target properties: `margin`, `padding`, `gap`, `top`, `right`, `bottom`, `left`, `width`, `height`, `max-width`, `min-height`, and their longhand variants.

Search for pixel values (`12px`, `15px`, `20px`) and rem values (`0.75rem`, `1.25rem`) that do not align with the project's spacing scale.

For Tailwind projects, use `ast_search` to find inline `style` attributes or `sx` props that bypass the utility class system with raw pixel values.

Record each spacing violation with:
- File path and line number.
- The hardcoded value found.
- The nearest token value (e.g., `15px` is close to `--spacing-md` at `16px`).
- Whether the mismatch is likely intentional (e.g., SVG coordinates, animation keyframes).

### Step 5: Scan for Typography Violations

Check for font-related properties that bypass the design system:

**Font families**:
Search for `font-family` declarations that do not reference a token or CSS variable. Common violation: directly specifying `'Inter', sans-serif` instead of `var(--font-family-body)`.

**Font sizes**:
Search for `font-size` values that do not match the type scale. Flag values like `13px` or `15px` that fall between defined scale steps.

**Font weights**:
Search for numeric font weights (`font-weight: 500`) that do not correspond to a named weight token.

**Line heights**:
Search for `line-height` values that deviate from the type scale's paired line heights.

For Tailwind projects, search for arbitrary values in font-related classes (e.g., `text-[13px]`, `font-[500]`) that bypass the configured type scale.

### Step 6: Scan for Component Usage Violations

Check whether the project's shared components are being used instead of raw HTML elements for common UI patterns.

Use `ast_search` to find raw HTML elements in component files that the design system provides as components:

| Raw Element Pattern           | Expected Component           |
|-------------------------------|------------------------------|
| `<button>` with custom styles | `<Button>` from design system|
| `<input>` with custom styles  | `<Input>` or `<TextField>`   |
| `<a>` styled as button        | `<LinkButton>` or `<Button as="a">` |
| `<select>` with custom styles | `<Select>` or `<Dropdown>`   |
| `<table>` with custom styles  | `<DataTable>` or `<Table>`   |
| `<dialog>` or custom modal    | `<Modal>` or `<Dialog>`      |

First, identify what shared components the design system provides by reading the component library's index file or export barrel. Then search source files for raw elements that duplicate that functionality.

### Step 7: Generate the Audit Report

Compile all findings into a structured report:

```
## Design System Audit Report

### Summary
- Files scanned: 47
- Total violations: 23
- Color violations: 8
- Spacing violations: 7
- Typography violations: 4
- Component violations: 4

### Critical Violations (token available but not used)
| File | Line | Property | Value | Recommended Token |
|------|------|----------|-------|-------------------|
| src/components/Card.tsx | 12 | color | #1a1a2e | var(--color-text-primary) |
| src/pages/Home.tsx | 45 | padding | 15px | var(--spacing-md) (16px) |

### Warnings (potential missing tokens)
| File | Line | Property | Value | Notes |
|------|------|----------|-------|-------|
| src/components/Badge.tsx | 8 | background | #ff6b35 | No matching token exists |

### Component Usage
| File | Line | Raw Element | Suggested Component |
|------|------|-------------|---------------------|
| src/pages/Settings.tsx | 23 | <button> | <Button> |

### Recommendations
1. Replace 8 hardcoded colors with existing tokens.
2. Add a new color token for #ff6b35 if this color is intentional.
3. Align 5 spacing values to the nearest scale step.
4. Replace 4 raw HTML elements with design system components.
```

### Step 8: Provide Automated Fix Suggestions

For each violation categorized as "token available," provide the exact code change needed:

- For CSS/SCSS: Replace the literal value with `var(--token-name)`.
- For Tailwind: Replace the arbitrary value class with the correct utility class.
- For JS/TS theme references: Replace the literal with the theme accessor.

Group fixes by file so the developer can apply them efficiently.

## Severity Classification

Assign a severity level to each violation to help the developer prioritize fixes:

| Severity | Criteria                                                   | Action               |
|----------|------------------------------------------------------------|----------------------|
| Critical | Hardcoded value contradicts an existing token by name      | Fix immediately      |
| High     | Token exists for the exact value but is not used           | Fix in current sprint|
| Medium   | Value is close to a token but not an exact match           | Fix or define new token |
| Low      | Value is in a non-user-facing file (tests, mocks, scripts)| Fix opportunistically|
| Info     | Value is in a third-party override or intentional exception| Document and skip    |

Apply these severity levels in the audit report to guide triage.

## Edge Cases

- **Multiple themes (light/dark)**: If the project defines separate token sets for light and dark themes, check that components reference the semantic token (e.g., `--color-background`) rather than a mode-specific value (e.g., `--color-white`).
- **Third-party component overrides**: Styles applied to override third-party components (e.g., `.MuiButton-root`) may intentionally use raw values to match the library's internal API. Flag but do not treat as violations.
- **SVG and icon files**: Color values inside SVG files or icon components may be intentional and not subject to token constraints. Exclude SVG `fill` and `stroke` attributes from violation counts unless the user requests otherwise.
- **Animation and transition values**: Duration, easing, and keyframe values may not have corresponding tokens. Flag only if the project defines animation tokens.
- **Legacy code**: If the project is migrating to a design system, the audit may produce hundreds of violations. Offer to scope the report to specific directories or recently modified files.
- **Tailwind with custom theme**: If Tailwind's config extends the default theme, ensure both default and extended values are included in the token vocabulary.
- **Design token formats**: Token files may use the W3C Design Tokens Community Group format, Style Dictionary format, or a custom schema. Detect the format before parsing to avoid misreading token structures.

## Related Skills

- **e-css** (eskill-frontend): Follow up with e-css after this skill to clean up CSS inconsistencies found during the audit.
- **e-a11y** (eskill-quality): Run e-a11y alongside this skill to verify design system components meet accessibility standards.
