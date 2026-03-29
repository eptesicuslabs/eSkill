"""
eARA metric: adaptation_score = (coverage * 0.4) + (quality * 0.6)
Outputs a single float to stdout.
"""

import os
import sys
import re
from pathlib import Path

PLUGINS_DIR = Path(__file__).parent.parent / "plugins"

# Target categories derived from awesome-agent-skills.
# Each maps to one or more eSkill plugin prefixes.
TARGET_CATEGORIES = {
    "code-generation":     ["eskill-coding"],
    "code-review":         ["eskill-quality"],
    "testing":             ["eskill-testing"],
    "debugging":           ["eskill-coding", "eskill-testing"],
    "devops-ci-cd":        ["eskill-devops"],
    "infrastructure":      ["eskill-devops", "eskill-system"],
    "security":            ["eskill-quality"],
    "api-development":     ["eskill-api"],
    "frontend-ui":         ["eskill-frontend"],
    "documentation":       ["eskill-office"],
    "database":            ["eskill-api", "eskill-system"],
    "monitoring":          ["eskill-devops", "eskill-system"],
    "performance":         ["eskill-coding", "eskill-system"],
    "refactoring":         ["eskill-coding", "eskill-quality"],
    "architecture":        ["eskill-coding", "eskill-meta"],
    "ai-ml":               ["eskill-intelligence"],
    "data-analysis":       ["eskill-intelligence", "eskill-office"],
    "project-management":  ["eskill-meta"],
    "git-workflow":        ["eskill-devops", "eskill-coding"],
    "containerization":    ["eskill-devops"],
    "cloud-deployment":    ["eskill-devops"],
    "accessibility":       ["eskill-frontend"],
    "internationalization": ["eskill-frontend"],
    "mobile":              ["eskill-frontend"],
    "cli-tooling":         ["eskill-system"],
    "mcp-tooling":         ["eskill-emcp"],
}


def count_skills_in_plugin(plugin_path: Path) -> list[Path]:
    """Return skill .md files in a plugin (excluding plugin.json, README, etc)."""
    skills = []
    for md in plugin_path.rglob("*.md"):
        name = md.name.lower()
        if name in ("readme.md", "changelog.md", "license.md"):
            continue
        # Must have frontmatter (starts with ---)
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
            if text.strip().startswith("---"):
                skills.append(md)
        except Exception:
            pass
    return skills


def quality_score(skill_path: Path) -> float:
    """Score a single skill 0-10 based on automated quality markers."""
    try:
        text = skill_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return 0.0

    lines = text.split("\n")
    score = 0.0

    # 1. Has frontmatter (2 pts)
    if text.strip().startswith("---"):
        score += 2.0

    # 2. Under 500 lines (1 pt)
    if len(lines) <= 500:
        score += 1.0

    # 3. Has description in frontmatter (1 pt)
    frontmatter_match = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if frontmatter_match:
        fm = frontmatter_match.group(1)
        if "description:" in fm:
            score += 1.0

    # 4. Has workflow steps (numbered list or decision tree) (2 pts)
    has_steps = bool(
        re.search(r"^\d+\.\s", text, re.MULTILINE)
        or re.search(r"^###\s+Step\s+\d", text, re.MULTILINE)
    )
    has_decision = bool(re.search(r"(if|when|check|verify|decision)", text, re.IGNORECASE))
    if has_steps:
        score += 1.5
    if has_decision:
        score += 0.5

    # 5. References tools or MCP servers (1.5 pts)
    tool_refs = bool(re.search(
        r"(Read|Write|Edit|Bash|Grep|Glob|Agent|mcp_"
        r"|eMCP|fs_read|fs_search|fs_list|fs_write|fs_edit"
        r"|ast_search|data_file|test_run|shell_exec"
        r"|git_log|git_diff|lsp_symbols|docker_ps"
        r"|sys_info|think_start|docs_search|egrep_search)",
        text
    ))
    if tool_refs:
        score += 1.5

    # 6. Has section headers (structure) (1 pt)
    headers = len(re.findall(r"^#{1,4}\s", text, re.MULTILINE))
    if headers >= 3:
        score += 1.0

    # 7. Has Related Skills section (0.5 pts)
    if re.search(r"^##\s+Related Skills", text, re.MULTILINE):
        score += 0.5

    # 8. Has Prerequisites or Edge Cases section (0.5 pts)
    has_prereqs = bool(re.search(r"^##\s+Prerequisites", text, re.MULTILINE))
    has_edges = bool(re.search(r"^##\s+Edge Cases", text, re.MULTILINE))
    if has_prereqs or has_edges:
        score += 0.5

    # 9. Description is comprehensive (>100 chars with trigger phrases) (0.5 pts)
    if frontmatter_match:
        fm = frontmatter_match.group(1)
        desc_match = re.search(r'description:\s*"(.+?)"', fm, re.DOTALL)
        if desc_match and len(desc_match.group(1)) > 100:
            score += 0.5

    return min(score, 10.0)


def compute_coverage() -> float:
    """Percentage of target categories that have at least 1 skill in the mapped plugin."""
    covered = 0
    for category, plugin_prefixes in TARGET_CATEGORIES.items():
        for prefix in plugin_prefixes:
            plugin_path = PLUGINS_DIR / prefix
            if plugin_path.exists():
                skills = count_skills_in_plugin(plugin_path)
                if len(skills) >= 1:
                    covered += 1
                    break
    return (covered / len(TARGET_CATEGORIES)) * 100.0


def compute_quality() -> float:
    """Average quality score across all skills, scaled to 0-100."""
    all_scores = []
    if not PLUGINS_DIR.exists():
        return 0.0
    for plugin in sorted(PLUGINS_DIR.iterdir()):
        if not plugin.is_dir():
            continue
        for skill in count_skills_in_plugin(plugin):
            all_scores.append(quality_score(skill))

    if not all_scores:
        return 0.0
    avg = sum(all_scores) / len(all_scores)
    return (avg / 10.0) * 100.0


def main():
    coverage = compute_coverage()
    quality = compute_quality()
    composite = (coverage * 0.4) + (quality * 0.6)
    # Print only the composite score (eARA reads stdout)
    print(f"{composite:.2f}")
    # Breakdown to stderr for human readability
    print(f"  coverage={coverage:.1f}%  quality={quality:.1f}%  composite={composite:.2f}", file=sys.stderr)


if __name__ == "__main__":
    main()
