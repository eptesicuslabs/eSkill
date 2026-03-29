---
name: e-visual
description: "Configures visual regression testing by identifying UI components, generating baselines, and setting up comparison workflows. Use when adding visual testing, preventing UI regressions, or validating design changes. Also applies when: 'set up visual regression', 'screenshot testing', 'prevent visual bugs', 'compare UI changes'."
---

# Visual Regression Setup

This skill configures visual regression testing for a project by detecting the UI framework, selecting an appropriate screenshot comparison tool, identifying components and pages to capture, generating baseline scripts, and integrating the workflow into CI.

## Prerequisites

- A web application with renderable UI components or pages.
- A browser automation tool available or installable (Playwright, Puppeteer, or Selenium).
- A development server that can be started for screenshot capture.

## Workflow

### Step 1: Detect the UI Framework and Rendering Strategy

Identify how the UI is built to determine the capture strategy. Use `filesystem` tools (fs_list, fs_read) to scan the project:

| File / Dependency            | Framework       | Rendering              |
|------------------------------|-----------------|------------------------|
| `next.config.*`              | Next.js         | SSR/SSG + client       |
| `nuxt.config.*`              | Nuxt            | SSR/SSG + client       |
| `svelte.config.*`            | SvelteKit       | SSR + client           |
| `angular.json`               | Angular         | Client-side            |
| `vite.config.*` + react      | React (Vite)    | Client-side            |
| `storybook` in package.json  | Any + Storybook | Component isolation    |
| `astro.config.*`             | Astro           | Static + islands       |
| `remix.config.*`             | Remix           | SSR + client           |

Also detect existing browser automation:

| Dependency            | Tool        | Screenshot Capability       |
|-----------------------|-------------|----------------------------|
| `@playwright/test`    | Playwright  | Built-in, per-test         |
| `puppeteer`           | Puppeteer   | page.screenshot()          |
| `selenium-webdriver`  | Selenium    | driver.takeScreenshot()    |
| `cypress`             | Cypress     | cy.screenshot()            |

Use `ast_search` from the eMCP AST server to examine existing test files for screenshot usage patterns.

### Step 2: Select the Visual Comparison Tool

Choose a tool based on the project's existing infrastructure and requirements:

| Tool                  | Type        | Requires Service | Best For                      |
|-----------------------|-------------|------------------|-------------------------------|
| Playwright screenshots| Built-in    | No               | Projects already using Playwright |
| pixelmatch            | Library     | No               | Custom comparison pipelines   |
| Percy                 | SaaS        | Yes (cloud)      | Teams needing a review UI     |
| Chromatic             | SaaS        | Yes (cloud)      | Storybook-based projects      |
| reg-suit              | Self-hosted | No               | CI integration, S3 storage    |
| BackstopJS            | Standalone  | No               | Page-level regression testing |
| Loki                  | Standalone  | No               | Storybook screenshot testing  |

Decision logic:
1. If the project uses Playwright, use Playwright's built-in visual comparison (no additional dependencies).
2. If the project uses Storybook and wants cloud review, recommend Chromatic.
3. If the project uses Storybook and wants local-only, recommend Loki.
4. If no browser automation exists, recommend Playwright for both E2E and visual tests.
5. If the project requires no SaaS dependencies (per eSkill design principles), prefer Playwright or BackstopJS.

### Step 3: Identify Components and Pages to Test

Determine what to capture. Use `ast_search` and `filesystem` tools to inventory:

**Page-level targets**: Scan the router configuration to find all routes:

| Framework  | Router File                          | Route Pattern                |
|------------|--------------------------------------|------------------------------|
| Next.js    | `app/` or `pages/` directory         | File-based routing           |
| Nuxt       | `pages/` directory                   | File-based routing           |
| React      | Route definitions in JSX             | `<Route path="..." />`      |
| Angular    | `*-routing.module.ts`                | `{ path: '...' }`           |
| SvelteKit  | `routes/` directory                  | File-based routing           |

**Component-level targets**: If Storybook is present, use its story files as the component inventory:
```
*.stories.tsx
*.stories.ts
*.stories.jsx
```

Use `filesystem` tools to list all story files and extract component names with `ast_search`.

If no Storybook exists, identify key components by scanning for:
- Layout components (Header, Footer, Sidebar, Nav).
- Form components (LoginForm, CheckoutForm, SearchBar).
- Data display components (Table, Card, List, Chart).
- Modal and dialog components.

Build a capture manifest:

| Target             | Type      | URL / Path                    | Viewport(s)        |
|--------------------|-----------|-------------------------------|---------------------|
| Home page          | Page      | `/`                           | Desktop, Mobile     |
| Login page         | Page      | `/login`                      | Desktop, Mobile     |
| Dashboard          | Page      | `/dashboard`                  | Desktop             |
| Header             | Component | Storybook: `Header--default`  | Desktop, Mobile     |
| UserCard           | Component | Storybook: `UserCard--filled` | Desktop             |

### Step 4: Configure Viewport and Browser Settings

Define the viewports and browser settings for consistent captures. Use `filesystem` tools to write the configuration:

| Viewport Name | Width  | Height | Use Case                     |
|---------------|--------|--------|------------------------------|
| Desktop       | 1280   | 720    | Standard desktop             |
| Tablet        | 768    | 1024   | iPad portrait                |
| Mobile        | 375    | 667    | iPhone SE                    |
| Wide          | 1920   | 1080   | Full HD monitor              |

Browser settings that affect visual output:

| Setting                 | Value              | Reason                              |
|-------------------------|--------------------|-------------------------------------|
| Color scheme            | light              | Consistent baseline                 |
| Animations              | Disabled           | Prevent mid-animation captures      |
| Font loading            | Wait for complete  | Prevent FOUT/FOIT differences       |
| Scroll position         | Top (0,0)          | Consistent starting position        |
| Device scale factor     | 1                  | Avoid DPI-dependent differences     |
| Timezone                | UTC                | Consistent date/time rendering      |

For Playwright, configure these in `playwright.config.ts`:
```typescript
use: {
  viewport: { width: 1280, height: 720 },
  colorScheme: 'light',
  timezoneId: 'UTC',
  locale: 'en-US',
}
```

### Step 5: Generate Baseline Capture Scripts

Create the visual test files that capture screenshots and compare against baselines.

**Playwright visual tests** (write to `tests/visual/`):

```typescript
import { test, expect } from '@playwright/test';

test.describe('Visual Regression', () => {
  test('home page', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('home.png', {
      maxDiffPixelRatio: 0.01,
    });
  });

  test('login page', async ({ page }) => {
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveScreenshot('login.png', {
      maxDiffPixelRatio: 0.01,
    });
  });
});
```

**BackstopJS configuration** (write to `backstop.json`):
```json
{
  "viewports": [
    { "label": "desktop", "width": 1280, "height": 720 },
    { "label": "mobile", "width": 375, "height": 667 }
  ],
  "scenarios": [
    {
      "label": "Home Page",
      "url": "http://localhost:3000/",
      "delay": 1000,
      "misMatchThreshold": 0.1
    }
  ],
  "engine": "playwright"
}
```

Use `filesystem` tools to write the test files and configuration. Use `data_file` tools (data_file_write) for JSON configuration files.

### Step 6: Handle Dynamic Content

Pages with dynamic content produce false positives. Identify and mask dynamic elements:

| Dynamic Element       | Masking Strategy                           | Implementation                      |
|-----------------------|--------------------------------------------|-------------------------------------|
| Timestamps            | Replace with fixed text via JS injection   | `page.evaluate()`                   |
| User avatars          | CSS overlay or fixed test image            | `page.addStyleTag()`               |
| Advertisements        | Hide the container                         | `page.locator('.ad').evaluate(hide)`|
| Animations            | Disable via CSS                            | `*, *::before, *::after { animation: none !important; transition: none !important; }` |
| Carousels / sliders   | Pin to first slide                         | `page.evaluate()` to stop rotation |
| Loading spinners      | Wait for completion                        | `page.waitForLoadState('networkidle')` |
| Random content        | Seed or mock the data source               | Intercept API responses             |

Generate a helper function for dynamic content masking:

```typescript
async function stabilizePage(page: Page): Promise<void> {
  // Disable animations
  await page.addStyleTag({
    content: `*, *::before, *::after {
      animation-duration: 0s !important;
      transition-duration: 0s !important;
    }`
  });
  // Wait for fonts
  await page.evaluate(() => document.fonts.ready);
  // Wait for images
  await page.waitForFunction(() => {
    const images = Array.from(document.images);
    return images.every(img => img.complete);
  });
}
```

Use `ast_search` to scan existing page components for dynamic content patterns that need masking.

### Step 7: Generate Initial Baselines

Run the visual tests for the first time to create baseline screenshots.

Use `shell` tools (shell_exec) from the eMCP shell server:

| Tool         | Baseline Command                              | Baseline Location                   |
|--------------|-----------------------------------------------|-------------------------------------|
| Playwright   | `npx playwright test --update-snapshots`      | `tests/visual/*.png` (co-located)   |
| BackstopJS   | `npx backstop reference`                      | `backstop_data/bitmaps_reference/`  |
| Loki         | `npx loki update`                             | `.loki/reference/`                  |
| reg-suit     | First run stores in configured bucket         | S3 or local directory               |

After generation, verify baselines are reasonable:
1. Use `filesystem` tools to confirm the screenshot files were created.
2. Check file sizes: empty or very small files indicate capture failures.
3. List all generated baselines and their dimensions.

Commit baselines to version control. Note that screenshot files can be large; recommend Git LFS if the project has many baselines:
```
git lfs track "*.png"
git lfs track "backstop_data/bitmaps_reference/**"
```

### Step 8: Set Up CI Integration

Configure the CI pipeline to run visual regression tests on pull requests.

Use `filesystem` tools to read and update CI configuration files.

**GitHub Actions** (add to `.github/workflows/visual.yml`):
```yaml
name: e-visual
on: [pull_request]
jobs:
  visual:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test tests/visual/
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: visual-diffs
          path: test-results/
```

Use `docker` tools from the eMCP Docker server if the application requires services running during visual tests. Add a Docker Compose step before the test run.

Key CI considerations:

| Factor                | Configuration                              | Reason                           |
|-----------------------|--------------------------------------------|----------------------------------|
| Browser version       | Pin in Playwright config                   | Rendering consistency            |
| OS                    | Use same OS as baselines                   | Font rendering differs by OS     |
| Screen size           | Set in viewport config                     | Avoid runner-dependent sizing    |
| Artifact upload       | Upload diffs on failure                    | Enable visual review             |
| Threshold             | Set maxDiffPixelRatio                      | Tolerate anti-aliasing diffs     |

## Edge Cases

- **Font rendering differences**: Different OSes render fonts differently. Generate baselines on the same OS as CI (typically Linux). If baselines were generated on macOS, expect false positives on Linux runners. Use Docker for consistent rendering.
- **Responsive breakpoints**: Test at exact breakpoint widths (e.g., 768px) to catch off-by-one CSS issues where elements jump between layouts.
- **Dark mode**: If the application supports dark mode, generate separate baselines for light and dark themes. Use Playwright's `colorScheme` option to switch.
- **Internationalization**: If the UI supports multiple languages, text length differences can cause layout shifts. Test the longest language (often German) alongside the default.
- **Sub-pixel rendering**: Anti-aliasing produces small per-pixel differences across runs. Set `maxDiffPixelRatio` to 0.01 (1%) to avoid false positives while still catching real regressions.
- **Large baseline sets**: If the project has hundreds of components and multiple viewports, visual test runs become slow. Prioritize critical user-facing pages and component states. Run the full visual suite nightly rather than on every PR.
- **Merge conflicts on baselines**: Binary PNG files cannot be merged. When two branches update the same baseline, the second to merge must regenerate its baselines. Document this in contributing guidelines.

## Related Skills

- **e-stories** (eskill-frontend): Run e-stories before this skill to create the component stories that visual regression tests will capture.
- **e-e2e** (eskill-testing): Follow up with e-e2e after this skill to include visual checks in end-to-end test workflows.
