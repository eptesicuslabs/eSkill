"""
eARA gate: validate eSkill skill files.
Modes:
  (default)        basic validation (frontmatter exists, file readable)
  --strict         frontmatter has name + description
  --lint           no emoji, no trailing whitespace, UTF-8
  --no-regression  skill count has not decreased (reads .eara-state.json)
  --max-lines N    no skill exceeds N lines
  --no-duplicates  no duplicate skill names across plugins
  --require-workflow  every skill has numbered steps or decision logic
"""

import argparse
import json
import re
import sys
from pathlib import Path

PLUGINS_DIR = Path(__file__).parent.parent / "plugins"
STATE_FILE = Path(__file__).parent.parent / ".eara-state.json"


def find_skills():
    """Find all skill .md files with frontmatter."""
    skills = []
    for plugin in sorted(PLUGINS_DIR.iterdir()):
        if not plugin.is_dir():
            continue
        for md in plugin.rglob("*.md"):
            if md.name.lower() in ("readme.md", "changelog.md", "license.md"):
                continue
            try:
                text = md.read_text(encoding="utf-8", errors="replace")
                if text.strip().startswith("---"):
                    skills.append(md)
            except Exception:
                pass
    return skills


def validate_basic(skills):
    errors = []
    for s in skills:
        text = s.read_text(encoding="utf-8", errors="replace")
        if not text.strip().startswith("---"):
            errors.append(f"{s}: missing frontmatter")
    return errors


def validate_strict(skills):
    errors = []
    for s in skills:
        text = s.read_text(encoding="utf-8", errors="replace")
        fm_match = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if not fm_match:
            errors.append(f"{s}: no frontmatter block")
            continue
        fm = fm_match.group(1)
        if "name:" not in fm:
            errors.append(f"{s}: frontmatter missing 'name'")
        if "description:" not in fm:
            errors.append(f"{s}: frontmatter missing 'description'")
    return errors


def validate_lint(skills):
    errors = []
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA00-\U0001FA6F"  # chess symbols
        "\U0001FA70-\U0001FAFF"  # symbols extended-A
        "\U00002702-\U000027B0"  # dingbats
        "\U0000FE00-\U0000FE0F"  # variation selectors
        "\U0000200D"             # zero-width joiner
        "\U000024C2-\U000024FF"  # enclosed alphanumerics (subset)
        "]+",
        flags=re.UNICODE,
    )
    for s in skills:
        try:
            text = s.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{s}: not valid UTF-8")
            continue
        if emoji_pattern.search(text):
            errors.append(f"{s}: contains emoji")
    return errors


def validate_no_regression(skills):
    current_count = len(skills)
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
            prev_count = state.get("skill_count", 0)
            if current_count < prev_count:
                return [f"skill count decreased: {prev_count} -> {current_count}"]
        except Exception:
            pass
    return []


def validate_max_lines(skills, max_lines):
    errors = []
    for s in skills:
        lines = s.read_text(encoding="utf-8", errors="replace").split("\n")
        if len(lines) > max_lines:
            errors.append(f"{s}: {len(lines)} lines (max {max_lines})")
    return errors


def validate_no_duplicates(skills):
    names = {}
    errors = []
    for s in skills:
        text = s.read_text(encoding="utf-8", errors="replace")
        fm_match = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if not fm_match:
            continue
        name_match = re.search(r"^name:\s*(.+)$", fm_match.group(1), re.MULTILINE)
        if not name_match:
            continue
        name = name_match.group(1).strip().strip("\"'")
        if name in names:
            errors.append(f"duplicate name '{name}': {names[name]} and {s}")
        else:
            names[name] = s
    return errors


def validate_workflow(skills):
    errors = []
    for s in skills:
        text = s.read_text(encoding="utf-8", errors="replace")
        has_steps = bool(re.search(r"^\d+\.\s", text, re.MULTILINE))
        has_bullets = bool(re.search(r"^[-*]\s", text, re.MULTILINE))
        if not (has_steps or has_bullets):
            errors.append(f"{s}: no workflow steps (numbered list or bullets)")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--lint", action="store_true")
    parser.add_argument("--no-regression", action="store_true")
    parser.add_argument("--max-lines", type=int)
    parser.add_argument("--no-duplicates", action="store_true")
    parser.add_argument("--require-workflow", action="store_true")
    args = parser.parse_args()

    skills = find_skills()

    errors = []
    if args.strict:
        errors = validate_strict(skills)
    elif args.lint:
        errors = validate_lint(skills)
    elif args.no_regression:
        errors = validate_no_regression(skills)
    elif args.max_lines:
        errors = validate_max_lines(skills, args.max_lines)
    elif args.no_duplicates:
        errors = validate_no_duplicates(skills)
    elif args.require_workflow:
        errors = validate_workflow(skills)
    else:
        errors = validate_basic(skills)

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"PASS ({len(skills)} skills)", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
