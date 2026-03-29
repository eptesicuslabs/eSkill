# Media and Visual Servers

## @emcp/server-image (6 tools)

Image inspection, manipulation, and OCR. The `image_ocr` tool was merged from the former standalone OCR server. Resize/convert require `allowWrite`. OCR requires Tesseract installed.

### image_info

Get dimensions, format, and color space.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Image file path |

### image_metadata

Read detailed EXIF and ICC profile metadata.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Image file path |

### image_resize

Resize an image. Requires `allowWrite`.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Source image path |
| `outputPath` | string | yes | | Output path |
| `width` | number | no | | Target width |
| `height` | number | no | | Target height |
| `fit` | "cover" \| "contain" \| "fill" \| "inside" \| "outside" | no | "inside" | Resize strategy |

### image_convert

Convert format. Requires `allowWrite`.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Source image path |
| `outputPath` | string | yes | | Output path |
| `format` | "png" \| "jpeg" \| "webp" \| "avif" \| "tiff" | yes | | Target format |
| `quality` | number | no | 80 | Compression quality (1-100) |

### image_ocr

Extract text from an image. Requires Tesseract.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Image file path |
| `language` | string | no | | Tesseract language code |

Replaces the legacy `ocr_image` from the removed `@emcp/server-ocr`.

### image_ocr_languages

List available Tesseract languages.

No parameters.

---

## @emcp/server-media (5 tools)

Audio/video operations using ffmpeg/ffprobe. All conversion tools require `allowWrite`.

### media_info

Get codec, duration, resolution, and stream info.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Media file path |

### media_convert

Convert between formats.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Source file path |
| `outputFormat` | string | yes | | Target format (mp4, mp3, wav, etc.) |
| `filename` | string | no | | Custom output filename |

### media_trim

Trim to a time range.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Source file path |
| `start` | string | yes | | Start timestamp (HH:MM:SS or seconds) |
| `duration` | string | yes | | Duration |
| `filename` | string | no | | Custom output filename |

### media_extract_audio

Extract audio track from video.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Video file path |
| `format` | string | no | "mp3" | Output audio format |
| `filename` | string | no | | Custom output filename |

### media_extract_frame

Extract a single frame from video.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Video file path |
| `timestamp` | string | yes | | Timestamp to extract |
| `filename` | string | no | | Custom output filename |

---

## @emcp/server-diagram (3 tools)

Render diagrams from text using Mermaid, Graphviz DOT, or PlantUML.

### diagram_render

Render from source text.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `source` | string | yes | | Diagram source text |
| `engine` | "mermaid" \| "graphviz" \| "plantuml" | no | "mermaid" | Rendering engine |
| `format` | "svg" \| "png" | no | "svg" | Output format |
| `filename` | string | no | | Custom output filename |

### diagram_render_file

Render from a file.

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `path` | string | yes | | Diagram source file |
| `engine` | "mermaid" \| "graphviz" \| "plantuml" | yes | | Rendering engine |
| `format` | "svg" \| "png" | no | "svg" | Output format |
| `filename` | string | no | | Custom output filename |

### diagram_formats

List available engines and output formats.

No parameters.

---

## @emcp/server-browser (18 tools)

Full browser automation via Playwright. Supports search, navigation, interaction, screenshots, JS evaluation, console/network capture, multi-tab management, and dialog handling.

### Navigation and Search

| Tool | Description | Key Parameters |
|---|---|---|
| `browser_search` | Search the web | `query` (required), `engine`: "duckduckgo" \| "startpage" |
| `browser_navigate` | Navigate to URL | `url` (required), `waitUntil`: "domcontentloaded" \| "networkidle" \| "load" \| "commit" |
| `browser_navigate_back` | Go back in history | (none) |

### Page Interaction

| Tool | Description | Key Parameters |
|---|---|---|
| `browser_click` | Click element or position | `selector` or `position: {x, y}`, `button`: "left" \| "right" \| "middle" |
| `browser_type` | Type into element | `selector`, `text` (required), `submit`, `clear`, `delay` |
| `browser_press_key` | Press a key | `key` (required) |
| `browser_hover` | Hover over element | `selector` (required) |
| `browser_select_option` | Select dropdown option | `selector`, `values` (required) |
| `browser_file_upload` | Upload files | `selector`, `paths` (required) |

### Inspection

| Tool | Description | Key Parameters |
|---|---|---|
| `browser_snapshot` | Accessibility tree snapshot | (none) |
| `browser_take_screenshot` | Screenshot page or element | `path`, `selector`, `format`, `quality` |
| `browser_eval` | Evaluate JavaScript | `expression` (required) |
| `browser_console` | Drain console messages | (none) |
| `browser_network` | Drain network requests | (none) |

### Management

| Tool | Description | Key Parameters |
|---|---|---|
| `browser_tabs` | List/new/switch/close tabs | `action` (required), `index` |
| `browser_dialog` | List/configure dialogs | `action` (required), `behavior` |
| `browser_wait_for` | Wait for condition | `text`, `textGone`, `selector`, `timeout` |
| `browser_close` | Close browser session | (none) |

---

## @emcp/server-computer-use (21 tools)

Full desktop automation with Anthropic computer_20251124 parity. Cross-platform: Windows (PowerShell/.NET), macOS (cliclick/screencapture), Linux (xdotool/xdg). DPI-aware coordinate scaling.

### Screen Capture

| Tool | Description | Key Parameters |
|---|---|---|
| `screen_screenshot` | Full screenshot (base64 PNG) | (none) |
| `screen_zoom` | Capture region at native resolution | `x`, `y`, `width`, `height` (all required) |
| `screen_cursor_position` | Get cursor coordinates | (none) |

### Mouse

| Tool | Description | Key Parameters |
|---|---|---|
| `screen_mouse_move` | Move cursor | `x`, `y` (required) |
| `screen_left_click` | Left click | `x`, `y` (required) |
| `screen_right_click` | Right click | `x`, `y` (required) |
| `screen_middle_click` | Middle click | `x`, `y` (required) |
| `screen_double_click` | Double click | `x`, `y` (required) |
| `screen_triple_click` | Triple click (select line) | `x`, `y` (required) |
| `screen_left_click_drag` | Drag | `startX`, `startY`, `endX`, `endY` (required) |
| `screen_left_mouse_down` | Press and hold | `x`, `y` (required) |
| `screen_left_mouse_up` | Release | `x`, `y` (required) |

### Keyboard

| Tool | Description | Key Parameters |
|---|---|---|
| `screen_type` | Type text | `text` (required) |
| `screen_key` | Key combo (e.g., "ctrl+c") | `key` (required) |
| `screen_hold_key` | Hold key for duration | `key` (required), `durationSeconds` (max 30) |

### Other

| Tool | Description | Key Parameters |
|---|---|---|
| `screen_scroll` | Scroll at position | `direction`, `amount`, optional `x`/`y` |
| `screen_wait` | Pause | `durationSeconds` (max 30) |
| `screen_windows_list` | List visible windows | (none) |
| `screen_window_focus` | Focus window | `title` or `pid` |
| `screen_window_resize` | Resize/reposition window | `title`/`pid`, `x`/`y`/`width`/`height`/`state` |
| `screen_app_launch` | Launch application | `app` (required), `waitMs` |
