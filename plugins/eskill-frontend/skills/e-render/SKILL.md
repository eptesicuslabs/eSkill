---
name: e-render
description: "Renders frontend output in a browser and validates visual correctness against design intent. Use after building UI components or pages to verify they render correctly. Also applies when: 'check if it looks right', 'preview the page', 'does it render', 'visual check', 'screenshot the result', 'verify the design', 'does it match the mockup'."
---

# e-render

Validates frontend output by rendering it in a real browser and comparing the result against design intent. This skill bridges the gap between writing UI code and knowing it works visually. It uses eMCP browser and computer-use servers to launch, navigate, capture, and inspect rendered pages.

## Prerequisites

- Frontend code that can be served locally (static HTML, dev server, or build output).
- At least one of: eMCP browser server (`browser_navigate`, `browser_snapshot`, `browser_take_screenshot`) or eMCP computer-use server (`screen_screenshot`).
- A shell server to start a local dev server if one is not already running.

## Workflow

### Step 1: Determine Render Target

Identify what needs to be rendered and how to serve it.

1. Check if a dev server is already running. Use `shell_exec` to check common ports:
   - Port 3000 (React/Next.js), 5173 (Vite), 4200 (Angular), 8080 (Vue CLI), 4321 (Astro)
   - If a server is running, use its URL directly.

2. If no server is running, determine how to start one:
   - Check `data_file_read` on `package.json` for `scripts.dev` or `scripts.start`.
   - Use `shell_bg` to start the dev server in the background. Wait for the port to become available.
   - For static HTML files, use a simple server: `shell_bg` with `npx serve .` or `python -m http.server`.

3. Determine the target URL:
   - If the user specified a page or route, use that.
   - If working on a specific component, check if Storybook is configured and navigate to the component story.
   - If no route is specified, navigate to the root and look for the relevant page.

### Step 2: Render and Capture

Navigate to the target and capture the initial state.

1. Use `browser_navigate` with the target URL. Set `waitUntil: "networkidle"` to ensure all assets load.

2. Take a full-page screenshot with `browser_take_screenshot`. Save to a temporary path for reference.

3. Capture the accessibility tree with `browser_snapshot`. This provides the DOM structure as the browser sees it, which reveals rendering issues that screenshots alone miss:
   - Missing text content (blank renders).
   - Broken component hierarchy.
   - Missing interactive elements.
   - Accessibility violations (missing labels, roles).

4. Check the console for errors with `browser_console`. Rendering errors, hydration mismatches, and missing assets show up here. Flag any errors or warnings.

5. Check network requests with `browser_network` for failed asset loads (404s, CORS errors, missing fonts).

### Step 3: Validate Against Design Intent

Compare the rendered output against what was specified or designed.

**Layout verification**:
- Does the page structure match the intended layout? Check the accessibility snapshot for correct heading hierarchy, landmark regions, and content order.
- Use `browser_eval` to inspect computed styles on key elements:
  ```
  browser_eval("JSON.stringify(getComputedStyle(document.querySelector('.hero')).display)")
  ```
- Verify grid/flex layouts rendered correctly by checking dimensions of key containers.

**Typography verification**:
- Use `browser_eval` to check that intended fonts loaded:
  ```
  browser_eval("document.fonts.check('16px Expected Font Name')")
  ```
- Check font-size, line-height, and weight on heading and body text elements.

**Color verification**:
- Use `browser_eval` to sample background and text colors on key elements.
- Verify contrast ratios between text and background meet WCAG AA (4.5:1 for body, 3:1 for large text).

**Content verification**:
- Check that all expected text content appears in the accessibility snapshot.
- Verify images loaded (check for broken image placeholders in the screenshot).
- Confirm dynamic content populated if applicable.

### Step 4: Test Responsive Behavior

Validate the design at multiple viewport sizes.

1. Use `browser_eval` to resize the viewport:
   ```
   browser_eval("window.resizeTo(375, 812)")
   ```
   Or use the browser's device emulation if available.

2. Test at three breakpoints minimum:
   - Mobile: 375x812 (iPhone standard)
   - Tablet: 768x1024 (iPad)
   - Desktop: 1440x900 (standard laptop)

3. At each breakpoint:
   - Take a screenshot with `browser_take_screenshot`.
   - Check the accessibility snapshot for content that disappeared or reordered incorrectly.
   - Verify navigation transformed correctly (hamburger menu on mobile, full nav on desktop).
   - Check that touch targets are adequate on mobile (minimum 44x44px).

### Step 5: Test Interactive States

Verify that interactive elements respond correctly.

1. **Hover states**: Use `browser_hover` on buttons, links, and cards. Take a screenshot to verify visual feedback.

2. **Focus states**: Use `browser_press_key` with "Tab" to cycle through interactive elements. Verify visible focus rings appear in screenshots.

3. **Click interactions**: Use `browser_click` on key interactive elements (navigation links, buttons, toggles). Verify the expected state change occurs.

4. **Form behavior**: If forms are present, use `browser_type` to fill inputs and verify validation states render correctly.

5. **Modals and overlays**: If the design includes modals, trigger them and verify:
   - Backdrop renders correctly.
   - Content is visible and properly positioned.
   - Escape key dismisses the modal (use `browser_press_key` with "Escape").

### Step 6: Compare Against Reference

If a reference image or mockup was provided:

1. Place the reference screenshot and the rendered screenshot side by side for comparison.
2. Use `image_info` to get dimensions of both images for alignment.
3. Call out specific differences:
   - Spacing deviations.
   - Color mismatches.
   - Missing elements.
   - Font rendering differences.
   - Layout shifts.

If no reference was provided, evaluate against the design intent established in the `e-design` skill's Step 3 (visual direction):
- Does the typography match the defined scale and pairing?
- Does the color palette match the defined tokens?
- Does the spacing follow the defined rhythm?
- Do interactive states match the defined transition patterns?

### Step 7: Report Findings

Compile a validation report with:

1. **Pass/Fail summary**: Overall render status.
2. **Screenshots**: Paths to captured screenshots at each breakpoint.
3. **Console errors**: Any JavaScript errors or warnings.
4. **Network failures**: Any failed asset loads.
5. **Accessibility issues**: Missing labels, broken hierarchy, contrast failures.
6. **Responsive issues**: Breakpoints where layout breaks.
7. **Interactive issues**: States that don't render correctly.
8. **Recommendations**: Specific fixes for each issue found.

If all checks pass, report success with the screenshot paths as evidence.

If issues are found, provide actionable fixes with file paths and line numbers where possible. Use `fs_search` and `ast_search` to locate the relevant code for each issue.

### Step 8: Cleanup

1. If a dev server was started in Step 1, check if the user wants it kept running. If not, use `shell_kill` to stop it.
2. Close the browser session with `browser_close` if no further work is expected.

## Edge Cases

- **No browser server available**: Fall back to `screen_screenshot` from the computer-use server if the browser server is not configured. This provides visual validation without DOM inspection.
- **Server-side rendering**: For SSR frameworks (Next.js, Nuxt), the initial HTML may differ from the hydrated state. Capture both the initial load and post-hydration states.
- **Authentication**: If the page requires auth, guide the user to log in first or use `browser_type` to fill credentials if a test account is available.
- **Slow renders**: For pages with heavy data fetching, increase the `waitUntil` timeout and check `browser_network` for pending requests before capturing.
- **Dark mode**: Test both light and dark modes by toggling `prefers-color-scheme` via `browser_eval`:
  ```
  browser_eval("document.documentElement.setAttribute('data-theme', 'dark')")
  ```
- **Animations**: For animated content, capture multiple frames or disable animations via `browser_eval` before screenshot:
  ```
  browser_eval("document.querySelector('*').style.animation = 'none'")
  ```

## Related Skills

- **e-design** (eskill-frontend): Run e-render after e-design to validate the generated UI.
- **e-responsive** (eskill-frontend): Run e-responsive for static CSS analysis; run e-render for live browser verification.
- **e-a11y** (eskill-quality): Run e-a11y for AST-based accessibility scanning; e-render validates accessibility in the rendered DOM.
- **e-visual** (eskill-testing): Use e-visual to set up ongoing regression testing; use e-render for one-time validation.
- **e-tokens** (eskill-frontend): Run e-tokens for static token compliance; e-render verifies tokens resolve correctly in the browser.
