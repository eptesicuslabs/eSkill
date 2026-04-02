---
name: e-stories
description: "Generates Storybook story files with controls, interaction tests, and accessibility checks from component analysis. Use when adding components to Storybook, building component documentation, or setting up interaction testing. Also applies when: 'create stories', 'add to Storybook', 'generate Storybook stories', 'document this component', 'add play functions'."
---

# Storybook Story Generation

This skill generates Storybook story files by analyzing component props via AST, detecting the project's Storybook configuration, and producing stories with controls, args, play functions for interaction testing, and accessibility addon integration. Stories serve a dual role: component documentation and executable test.

## Prerequisites

- A frontend project with Storybook installed or planned for installation.
- One or more components to generate stories for.

## Workflow

### Step 1: Detect Storybook Configuration

Use `filesystem` tools (fs_list, fs_read) to determine the Storybook setup:

**Version detection**:
Read `package.json` and check for Storybook packages:

| Package                  | Version Range | Story Format        |
|--------------------------|---------------|---------------------|
| @storybook/react         | 7.x+          | CSF 3 (recommended) |
| @storybook/vue3          | 7.x+          | CSF 3               |
| @storybook/angular       | 7.x+          | CSF 3               |
| @storybook/svelte        | 7.x+          | CSF 3               |
| @storybook/react         | 6.x           | CSF 2 or CSF 3      |
| storybook (standalone)   | 8.x+          | CSF 3               |

**Configuration files**:
Check for `.storybook/main.ts` (or `.js`). Read it to determine:
- Framework addon (e.g., `@storybook/react-vite`, `@storybook/nextjs`).
- Story file glob patterns (e.g., `../src/**/*.stories.@(ts|tsx)`).
- Addons installed (controls, actions, docs, a11y).

**Existing story conventions**:
Find existing story files using `egrep_search_files` to locate files matching `*.stories.tsx` or `*.stories.ts` patterns. Read two or three representative files to extract:
- File naming pattern (`*.stories.tsx`, `*.stories.ts`, `*.stories.js`).
- Whether stories use CSF 2 (`export const Story = Template.bind({})`) or CSF 3 (`export const Story = { args: {} }`).
- Whether stories are co-located with components or in a separate `stories/` directory.
- Whether a custom render function or decorators are used.

### Step 2: Analyze Component Props

For the target component, extract its full prop interface using `ast_search` from the eMCP AST server.

**TypeScript/React**:
Search for `interface *Props` or `type *Props` in the component file. Extract:
- Property name.
- Type (string, number, boolean, union, enum, function, ReactNode).
- Whether optional (marked with `?`).
- Default value (from destructuring defaults or defaultProps).

**Vue**:
Search for `defineProps` or `props:` in the component. Extract prop names, types, required status, and defaults.

**Angular**:
Search for `@Input()` decorators. Extract property names, types, and default values.

**Svelte**:
Search for `export let` declarations (Svelte 4) or `$props()` (Svelte 5). Extract variable names, types, and defaults.

Build a prop catalog:

| Prop       | Type                          | Required | Default     |
|------------|-------------------------------|----------|-------------|
| variant    | 'primary' \| 'secondary'      | No       | 'primary'   |
| size       | 'sm' \| 'md' \| 'lg'          | No       | 'md'        |
| disabled   | boolean                       | No       | false       |
| onClick    | () => void                    | No       | undefined   |
| children   | ReactNode                     | Yes      | -           |

### Step 3: Identify Story Scenarios

From the prop catalog, determine which stories to generate:

**Default story**:
A story with all default prop values. This is the baseline rendering.

**Per-variant stories**:
For each prop with a union or enum type, generate one story per value:
- `variant: 'primary'` -> Primary story.
- `variant: 'secondary'` -> Secondary story.

**Boolean prop stories**:
For each boolean prop, generate the `true` state as a story (the `false` state is typically the default):
- `disabled: true` -> Disabled story.
- `loading: true` -> Loading story.

**Combination stories**:
For meaningful combinations of props, generate composite stories:
- `variant: 'primary', size: 'lg'` -> LargePrimary story.
- `variant: 'secondary', disabled: true` -> DisabledSecondary story.

Do not generate a story for every possible combination. Focus on combinations that represent real use cases.

**State stories**:
If the component has internal state (hover, focus, active, error), generate stories that demonstrate each state using Storybook's `play` function or decorators.

### Step 4: Generate the Meta Object

Produce the story file's default export (the meta object) following CSF 3 format:

```typescript
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary'],
      description: 'Visual style variant',
      table: {
        defaultValue: { summary: 'primary' },
      },
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
      description: 'Size of the button',
      table: {
        defaultValue: { summary: 'md' },
      },
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the button is disabled',
    },
    onClick: {
      action: 'clicked',
    },
  },
  args: {
    variant: 'primary',
    size: 'md',
    disabled: false,
    children: 'Button',
  },
};

export default meta;
type Story = StoryObj<typeof meta>;
```

**Title convention**: Determine the story title hierarchy from existing stories. Common patterns:
- `Components/Button` (flat).
- `Design System/Atoms/Button` (atomic design).
- `Features/Auth/LoginButton` (feature-based).

**Control types**: Map prop types to Storybook controls:

| Prop Type              | Control Type | Configuration                   |
|------------------------|--------------|---------------------------------|
| string                 | text         | `{ control: 'text' }`          |
| number                 | number       | `{ control: 'number' }`        |
| boolean                | boolean      | `{ control: 'boolean' }`       |
| Union of strings       | select       | `{ control: 'select', options: [...] }` |
| Union of numbers       | select       | `{ control: 'select', options: [...] }` |
| Function/callback      | action       | `{ action: 'eventName' }`      |
| ReactNode / slot       | text         | `{ control: 'text' }` (simplified) |
| Complex object         | object       | `{ control: 'object' }`        |

### Step 5: Generate Individual Stories

Produce named exports for each story scenario identified in Step 3:

```typescript
export const Default: Story = {};

export const Primary: Story = {
  args: {
    variant: 'primary',
  },
};

export const Secondary: Story = {
  args: {
    variant: 'secondary',
  },
};

export const Small: Story = {
  args: {
    size: 'sm',
  },
};

export const Large: Story = {
  args: {
    size: 'lg',
  },
};

export const Disabled: Story = {
  args: {
    disabled: true,
  },
};
```

For stories requiring user interaction, use play functions with `@storybook/test`. Play functions run after the story renders and serve as both interactive documentation and executable tests. The `@storybook/test` package provides `expect` (from Vitest), `userEvent`, `within`, and `fn` — use these instead of importing testing utilities directly.

```typescript
import { expect, userEvent, within, fn } from '@storybook/test';

export const ClickInteraction: Story = {
  args: {
    onClick: fn(),
  },
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');
    await userEvent.click(button);
    await expect(args.onClick).toHaveBeenCalledOnce();
  },
};

export const Focused: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');
    await button.focus();
    await expect(button).toHaveFocus();
  },
};

export const FormFilled: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const input = canvas.getByRole('textbox');
    await userEvent.clear(input);
    await userEvent.type(input, 'test@example.com');
    await expect(input).toHaveValue('test@example.com');
  },
};
```

### Step 6: Generate Documentation

If the project uses the Storybook docs addon (check `.storybook/main.*` for `@storybook/addon-docs`), enhance the meta object with documentation:

Add `tags: ['autodocs']` to enable automatic documentation generation.

If the project uses MDX documentation, generate a companion `.mdx` file that imports `Canvas`, `Meta`, and `Controls` from `@storybook/blocks`, renders a `<Canvas>` for the default story, a `<Controls />` table, and a `<Canvas>` for each variant. Check existing stories for MDX usage before generating. Only produce MDX if the project already uses it.

### Step 7: Add Decorators and Context

If the component requires providers or wrappers to render correctly, add decorators to the meta object. Common decorators:

- **Theme provider**: Wrap with `ThemeProvider` if the component consumes a theme.
- **Router context**: Wrap with a router provider if the component uses links or navigation.
- **Store context**: Wrap with the store provider and seed initial state if the component reads from a global store.

Check existing stories for decorator patterns using `ast_search`. Reuse the same decorators for consistency.

**Accessibility addon configuration**: If `@storybook/addon-a11y` is installed (check `.storybook/main.*` addons list), configure accessibility test behavior on the meta object. The addon runs axe-core against the rendered story DOM. Three test modes are available via `parameters.a11y.test`:

| Mode | Behavior | CI Impact |
|------|----------|-----------|
| `'error'` | Violations cause test failures | Blocks CI |
| `'todo'` | Violations shown as warnings in sidebar | Does not block CI |
| `'off'` | Accessibility checks disabled for this story | No checks |

Set the default to `'error'` for component stories where accessibility is expected. Use `'todo'` for work-in-progress components. Use `'off'` only for stories that intentionally demonstrate inaccessible states (e.g., a "before fix" example).

```typescript
const meta: Meta<typeof Button> = {
  component: Button,
  parameters: {
    a11y: {
      test: 'error',
    },
  },
};
```

Note: axe-core detects structural violations in the rendered DOM (missing labels, contrast issues, ARIA errors). It does not assess cognitive accessibility, meaningful alt text content, or keyboard trap behavior. Deque reports that axe-core detects up to 57% of accessibility issues by volume (Deque, 2023).

### Step 8: Place the Story File

Follow the project's story file placement convention detected in Step 1:

| Convention                        | Example Path                          |
|-----------------------------------|---------------------------------------|
| Co-located with component         | `src/components/Button/Button.stories.tsx` |
| Separate stories directory        | `stories/components/Button.stories.tsx` |
| Within __stories__ subdirectory   | `src/components/Button/__stories__/Button.stories.tsx` |

Match the file extension to the project convention (`.stories.tsx`, `.stories.ts`, `.stories.jsx`, `.stories.js`).

Verify the file path matches the glob pattern in `.storybook/main.*` so Storybook discovers the story automatically.

### Step 9: Verify the Generated Story

After writing the story file, validate it:

- Check that all imported components and types resolve correctly.
- Verify the story file path matches the Storybook glob pattern.
- Confirm the meta title does not conflict with existing stories.
- Ensure all argTypes reference props that exist on the component.

Report the generated file path and a summary of stories created.

## Edge Cases

- **Components with no props**: Generate a single Default story with no args. The story still provides value by documenting the component's existence and default rendering.
- **Components with complex object props**: For props that accept deeply nested objects, provide a representative default value in args rather than trying to map every field to a control.
- **Higher-order components**: If the component is wrapped in a HOC (memo, forwardRef, connect), analyze the inner component's props, not the wrapper's.
- **Render props and compound components**: Components that use render props or compound patterns (e.g., `<Tabs><Tab>`) need custom render functions in their stories. Generate a render function that demonstrates the composition pattern.
- **Storybook not installed**: If Storybook is not detected in the project, inform the user and offer to generate the story file anyway using CSF 3 with React as the default. Note that `npx storybook@latest init` can set up Storybook.
- **Vue and Angular templates**: For Vue SFC and Angular components, the story render function syntax differs from React. Use the appropriate framework-specific render pattern detected from existing stories or Storybook docs.

## Related Skills

- **e-component** (eskill-frontend): Run e-component before this skill to create the components that stories will document and test.
- **e-visual** (eskill-testing): Follow up with e-visual after this skill to add visual regression tests that capture story baselines. Stories provide the component isolation that visual regression needs.
- **e-a11y** (eskill-quality): e-a11y scans source code for structural violations; this skill's accessibility addon integration catches rendered-DOM violations via axe-core. The two are complementary, not redundant.
- **e-tokens** (eskill-frontend): Run e-tokens to verify that components used in stories reference design tokens rather than hardcoded values.
