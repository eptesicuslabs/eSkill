---
name: e-component
description: "Generates UI component scaffolds with props, state, styles, and test files following the project's existing patterns. Use when creating React, Vue, Angular, or Svelte components. Also applies when: 'create a component', 'scaffold a new component', 'add a React component', 'generate a Vue component'."
---

# Component Scaffold

This skill generates UI component files by detecting the project's frontend framework, analyzing existing component patterns, and producing a component file, styles, test, and index export that match the established conventions.

## Prerequisites

- A frontend project using React, Vue, Angular, or Svelte.
- At least one existing component in the project to use as a pattern reference.

## Workflow

### Step 1: Detect the Frontend Framework

Read the project's package manifest to determine the framework in use.

Use `filesystem` tools (fs_read) to read `package.json`. Check the `dependencies` and `devDependencies` fields against this table:

| Dependency               | Framework | Notes                          |
|--------------------------|-----------|--------------------------------|
| react                    | React     | Check for react-dom as well    |
| next                     | React     | Next.js implies React          |
| vue                      | Vue       | Check for @vue/compiler-sfc    |
| nuxt                     | Vue       | Nuxt implies Vue               |
| @angular/core            | Angular   | Check for @angular/cli         |
| svelte                   | Svelte    | Check for @sveltejs/kit        |

If multiple frameworks appear, ask the user which one the component targets.

Also check for TypeScript by looking for `typescript` in devDependencies or the presence of a `tsconfig.json` file. This determines whether to generate `.ts`/`.tsx` or `.js`/`.jsx` files.

### Step 2: Detect the Styling Approach

Scan the project to determine how styles are authored. Use `filesystem` tools (fs_list) on the component directories and check for these patterns:

| Pattern                  | Indicator                                    |
|--------------------------|----------------------------------------------|
| CSS Modules              | Files named `*.module.css` or `*.module.scss`|
| Tailwind CSS             | `tailwind.config.*` in project root          |
| styled-components        | `styled-components` in dependencies          |
| Emotion                  | `@emotion/react` in dependencies             |
| Plain CSS/SCSS           | `.css` or `.scss` files co-located with components |
| CSS-in-JS (other)        | Check imports in existing components         |
| Angular styles           | `styleUrls` in `@Component` decorator        |

Use `ast_search` from the eMCP AST server on two or three existing component files to confirm the styling approach by checking import statements and style references.

### Step 3: Analyze Existing Component Patterns

Find existing components to use as templates. Use `filesystem` tools to locate component directories (commonly `src/components/`, `src/app/`, `app/components/`, or `lib/components/`).

Read two or three representative component files using `filesystem` tools (fs_read) and extract these conventions:

**File structure**:
- Single file per component vs. directory per component (with index file).
- Whether styles, tests, and types live in the same directory or separate directories.

**Naming conventions**:
- PascalCase vs. kebab-case for file names.
- Whether the file name matches the component name exactly.
- Whether an `index.ts` or `index.js` barrel export exists per component directory.

**Code patterns**:
- Functional components vs. class components (React).
- Composition API vs. Options API (Vue).
- Whether props are defined with interfaces, type aliases, or PropTypes.
- Default export vs. named export.
- Whether components use forwardRef (React).

Use `ast_search` to extract the structure of existing components: imports, props interface, component body, and export statement.

### Step 4: Gather Component Requirements

Determine the new component's specification from the user's request:

- **Name**: The component name in PascalCase.
- **Props**: List of properties with types and whether they are optional.
- **State**: Any internal state the component manages.
- **Children**: Whether the component accepts children/slots.
- **Variants**: Named visual or behavioral variants (e.g., size, color).

If the user provides only a name, generate a minimal scaffold with a single `children` prop and no state. The developer fills in the details.

### Step 5: Generate the Component File

Produce the component file matching the detected framework and conventions.

**React (TypeScript)**:
```tsx
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

export function Button({ variant = 'primary', size = 'md', disabled = false, onClick, children }: ButtonProps) {
  return (
    <button
      className={styles.button}
      data-variant={variant}
      data-size={size}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

**Vue (Composition API)**:
```vue
<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
});

const emit = defineEmits<{
  click: [];
}>();
</script>

<template>
  <button
    :class="[$style.button, $style[props.variant], $style[props.size]]"
    :disabled="props.disabled"
    @click="emit('click')"
  >
    <slot />
  </button>
</template>
```

**Svelte**:
```svelte
<script lang="ts">
  export let variant: 'primary' | 'secondary' = 'primary';
  export let size: 'sm' | 'md' | 'lg' = 'md';
  export let disabled: boolean = false;
</script>

<button
  class="button {variant} {size}"
  {disabled}
  on:click
>
  <slot />
</button>
```

**Angular**:
```typescript
@Component({
  selector: 'app-button',
  templateUrl: './button.component.html',
  styleUrls: ['./button.component.scss'],
})
export class ButtonComponent {
  @Input() variant: 'primary' | 'secondary' = 'primary';
  @Input() size: 'sm' | 'md' | 'lg' = 'md';
  @Input() disabled = false;
  @Output() clicked = new EventEmitter<void>();
}
```

Adapt the generated code to match the exact conventions found in Step 3 (import style, export pattern, formatting).

### Step 6: Generate the Styles File

Based on the styling approach detected in Step 2:

- **CSS Modules**: Generate a `.module.css` file with class names matching the component structure.
- **Tailwind**: Embed utility classes directly in the component markup. No separate file needed.
- **styled-components/Emotion**: Generate styled wrappers within the component file or a separate `styles.ts` file, matching existing convention.
- **Plain CSS/SCSS**: Generate a co-located stylesheet with BEM or project-specific naming.
- **Angular**: Generate the component-scoped stylesheet.

Include base styles for the component root element, variant styles, size variants, and disabled state.

### Step 7: Generate the Test File

Use the test framework detection logic from the e-testgen skill (check `package.json` for vitest, jest, or the framework's testing library).

Generate a test file covering:

- Component renders without errors.
- Each prop variant renders correctly.
- Event handlers fire when triggered.
- Disabled state prevents interaction.
- Default prop values apply when props are omitted.

Match the test file placement convention detected in Step 3 (co-located `__tests__/`, separate `test/`, or `.test.tsx` suffix).

### Step 8: Generate the Index Export

If the project uses barrel exports (index files that re-export components), generate an `index.ts` or `index.js` file:

```typescript
export { Button } from './Button';
export type { ButtonProps } from './Button';
```

If the project does not use barrel exports, skip this step.

### Step 9: Verify File Placement

After generating all files, confirm the directory structure is consistent with existing components. Use `filesystem` tools (fs_list) to compare the new component directory layout against an existing component directory.

Report the generated files to the user with their paths.

## Edge Cases

- **Monorepo with multiple frameworks**: If the project contains both React and Vue packages, ask the user which package the component belongs to before generating.
- **No existing components**: If the project has no existing components to reference, use framework defaults (functional component, named export, co-located styles).
- **CSS-in-JS with theme**: If styled-components or Emotion uses a theme provider, include `useTheme()` or `${props => props.theme.*}` references in the generated styles.
- **Server components (Next.js/Nuxt)**: Check whether the target directory uses server or client components. Add `'use client'` directive at the top if the component uses state, effects, or event handlers.
- **Svelte 5 runes**: If the Svelte version is 5 or later, use the runes syntax (`$props`, `$state`) instead of the `export let` pattern.
- **Angular standalone components**: If the project uses Angular 14+ standalone components, add `standalone: true` to the `@Component` decorator and import dependencies directly.

## Related Skills

- **e-stories** (eskill-frontend): Follow up with e-stories after this skill to generate Storybook stories for the new components.
- **e-tokens** (eskill-frontend): Run e-tokens before this skill to ensure new components align with the design system.
