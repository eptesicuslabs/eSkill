---
name: e-retro
description: "Generates sprint or milestone retrospectives from git history, quality trends, and velocity metrics. Use at sprint ends, milestones, or project phases. Also applies when: 'sprint retrospective', 'what did we accomplish', 'milestone summary', 'team velocity report'."
---

# Retrospective Report

This skill generates data-driven retrospective reports for sprints, milestones, or project phases by analyzing git history, test results, code quality trends, and delivery metrics. It produces a structured retrospective document that facilitates team discussion by grounding observations in measurable data.

## Prerequisites

Determine the retrospective period with the user:

| Period Type | How to Determine Boundaries |
|------------|---------------------------|
| Sprint | Start and end dates, or branch creation/merge dates |
| Milestone | Git tags marking the milestone start and end |
| Calendar period | Specific date range (e.g., "last month", "Q4 2025") |
| Release cycle | From one release tag to the next |

Use `git` to identify the commit range corresponding to the period. Store the starting and ending commit references.

## Step 1: Collect Commit Statistics

Use `git` to retrieve all commits within the retrospective period.

Extract and aggregate:

| Metric | Method |
|--------|--------|
| Total commits | Count commits in range |
| Commits per author | Group by author |
| Commits per day | Group by date |
| Merge commits | Filter for merge commits |
| Direct pushes to main | Commits on main without merge |

Analyze commit patterns:

- **Commit distribution**: Calculate commits per day. Identify peaks (crunch days) and valleys (idle days). Uneven distribution may indicate planning issues or last-minute rushes.
- **Commit size**: Use `git_diff` statistics to calculate average lines changed per commit. Very large commits (500+ lines) suggest infrequent integration. Very small commits (1-5 lines) in bulk may indicate automated changes.
- **Commit messages**: Check adherence to conventional commit format. Calculate the percentage of commits following the convention. Flag commits with non-descriptive messages ("fix", "update", "wip").

Present as a summary table:

| Author | Commits | Lines Added | Lines Removed | Net Change |
|--------|---------|-------------|---------------|------------|
| <name> | <N> | <N> | <N> | <N> |
| <name> | <N> | <N> | <N> | <N> |
| **Total** | **<N>** | **<N>** | **<N>** | **<N>** |

## Step 2: Analyze Delivery Metrics

Examine what was delivered during the period.

**Features and changes**: Categorize commits by type using conventional commit prefixes.

| Category | Count | Percentage |
|----------|-------|------------|
| Features (`feat`) | <N> | <X%> |
| Bug fixes (`fix`) | <N> | <X%> |
| Refactoring (`refactor`) | <N> | <X%> |
| Documentation (`docs`) | <N> | <X%> |
| Tests (`test`) | <N> | <X%> |
| CI/CD (`ci`) | <N> | <X%> |
| Chores (`chore`) | <N> | <X%> |
| Other / uncategorized | <N> | <X%> |

**File change analysis**: Use `git` to identify:
- Most modified files (by commit count and line changes).
- New files created during the period.
- Files deleted during the period.
- Directories with the most activity.

The ratio of feature work to maintenance work (bugs, refactoring, chores) indicates how much capacity went to forward progress versus keeping the lights on.

## Step 3: Evaluate Code Quality Trends

Use `test_run` to capture current test results and compare with the period start.

**Test metrics**:

| Metric | Period Start | Period End | Change |
|--------|-------------|-----------|--------|
| Total tests | <N> | <N> | <+/- N> |
| Passing | <N> | <N> | <+/- N> |
| Failing | <N> | <N> | <+/- N> |
| Skipped | <N> | <N> | <+/- N> |
| Coverage % | <X%> | <X%> | <+/- X%> |

Calculate the test-to-code ratio: how many test lines were added per lines of production code.

**Lint and type checking**: If possible, compare linter output at the start and end of the period.

**Debt indicators**: Use `filesystem` to count TODO, FIXME, and HACK annotations at the end of the period. Compare with the start (using `git` to check the state at the starting commit).

| Debt Indicator | Period Start | Period End | Change |
|---------------|-------------|-----------|--------|
| TODO count | <N> | <N> | <+/- N> |
| FIXME count | <N> | <N> | <+/- N> |
| HACK count | <N> | <N> | <+/- N> |
| Lint warnings | <N> | <N> | <+/- N> |

## Step 4: Measure Review and Collaboration Metrics

Analyze how the team collaborated during the period.

Use `git` to extract:

- **Merge request frequency**: How many branches were merged, indicating completed work items.
- **Branch lifetime**: Average time from branch creation to merge. Long-lived branches indicate integration risk.
- **Co-authorship**: Commits with `Co-authored-by` trailers indicating pair programming or collaboration.
- **Review turnaround**: If PR metadata is available from the git history, estimate review latency.

Use `data_file_read` to check CI configuration for review requirements (required approvals, status checks).

| Collaboration Metric | Value | Assessment |
|---------------------|-------|-----------|
| Branches merged | <N> | <context> |
| Average branch lifetime | <N> days | Under 3 days is good |
| Longest-lived branch | <N> days | Over 7 days is a risk |
| Co-authored commits | <N> | Indicates pair work |

## Step 5: Identify Accomplishments

Distill the commit history into a narrative of what was accomplished.

For each significant feature or improvement:

1. Identify the commits that constitute the feature (by conventional commit scope, branch merge, or file grouping).
2. Summarize the feature in one sentence.
3. Note the primary contributor(s).
4. Quantify the scope (files changed, lines of code).

Organize accomplishments by category:

```
### Delivered

#### Features
- <Feature 1>: <description> (<contributor>)
- <Feature 2>: <description> (<contributor>)

#### Improvements
- <Improvement 1>: <description>
- <Improvement 2>: <description>

#### Bug Fixes
- <Fix 1>: <description> (closes #<issue>)
- <Fix 2>: <description>

#### Infrastructure
- <Change 1>: <description>
```

## Step 6: Identify Challenges and Pain Points

Analyze the data for signals of difficulty during the period.

**Indicators of challenges**:

| Signal | Detection Method | Interpretation |
|--------|-----------------|----------------|
| Reverted commits | Search for "revert" in commit messages | Feature instability or rushed work |
| Hotfix branches | Branches named `hotfix/` or `fix/` merged to main | Production issues |
| Force pushes | Unusual git history patterns | History rewrites, possibly lost work |
| Long-lived branches | Branches open for more than 5 days | Integration difficulty |
| Test failures | Tests that were added and then modified | Flaky or poorly designed tests |
| Repeated changes to same files | Files changed in 5+ commits | Churn indicating unclear requirements |
| Late-period commit spikes | Disproportionate commits in last 20% of period | Deadline pressure |

For each challenge identified, note:
- What the data shows.
- Possible root causes (for the team to discuss, not to assume).
- Potential process improvements.

## Step 7: Analyze Focus Areas

Determine where the team spent its time by mapping commits to areas of the codebase.

Use `git` to group file changes by top-level directory:

| Directory | Commits | Lines Changed | Contributors | Interpretation |
|-----------|---------|---------------|-------------|----------------|
| src/auth/ | 45 | 1200 | 2 | Heavy auth work |
| src/api/ | 30 | 800 | 3 | API development |
| tests/ | 25 | 600 | 3 | Test investment |
| docs/ | 5 | 200 | 1 | Minimal docs |
| infra/ | 10 | 300 | 1 | Infrastructure |

Calculate the percentage of work in each area. Compare with the team's stated priorities for the period. Misalignment between planned focus and actual focus is a discussion point.

## Step 8: Generate Velocity Metrics

If the team tracks velocity across periods, provide comparative data.

| Metric | This Period | Previous Period | Trend |
|--------|------------|----------------|-------|
| Commits | <N> | <N> | Up/Down/Stable |
| Features delivered | <N> | <N> | Up/Down/Stable |
| Bugs fixed | <N> | <N> | Up/Down/Stable |
| Lines of code (net) | <N> | <N> | Up/Down/Stable |
| Test count change | <+N> | <+N> | Up/Down/Stable |
| Average commit size | <N> lines | <N> lines | Up/Down/Stable |

To calculate previous period metrics, use `git` with the appropriate date range for the prior sprint or milestone.

Note: Velocity metrics should inform discussion, not drive judgment. Lines of code and commit counts are imperfect proxies for productivity. Emphasize outcomes (features delivered, bugs fixed, quality improved) over volume.

## Step 9: Draft Retrospective Discussion Points

Based on the data analysis, generate structured discussion points for the team retrospective.

**What went well** (supported by data):
- Features delivered on time or ahead of schedule.
- Test coverage improvements.
- Successful collaboration patterns.
- Clean merge history indicating good branch management.

**What could be improved** (supported by data):
- Areas with high churn or reverts.
- Test coverage gaps.
- Documentation not keeping pace with code.
- Imbalanced workload across team members.
- Increasing debt indicators.

**Action items to consider**:
- Specific, measurable process changes.
- Tooling improvements.
- Knowledge sharing sessions for concentrated knowledge areas.
- Debt reduction targets for the next period.

Frame each point as a discussion starter, not a conclusion. The data shows what happened; the team determines why and what to do about it.

## Step 10: Assemble and Deliver the Report

Use `filesystem` and `markdown` to produce the final report.

The report should include: period metadata (dates, duration, team), executive summary (3-5 sentences), delivery summary (from Step 5), metrics dashboard (commit activity from Step 1, delivery breakdown from Step 2, quality trends from Step 3, collaboration from Step 4, focus areas from Step 7, velocity from Step 8), challenges observed (from Step 6), discussion points (what went well, what could be improved, proposed action items as checklist), and an appendix with detailed statistics.

Present the report to the user. Offer to write it to a file (default: `docs/retrospectives/<YYYY-MM-DD>-retro.md`).

## Edge Cases

- **Solo developer**: For single-person projects, focus on delivery metrics, quality trends, and time management patterns rather than collaboration metrics. The retrospective becomes a personal review.
- **Very short sprints** (less than 1 week): There may be insufficient data for meaningful trends. Focus on accomplishments and blockers rather than statistical analysis.
- **Very long periods** (over 2 months): Break the analysis into sub-periods (monthly or bi-weekly) to show progression within the period.
- **Multiple repositories**: If the team works across repositories, the retrospective should note this limitation and focus on the current repository. Suggest aggregating retrospectives from all repositories for a complete picture.
- **No conventional commits**: If the team does not use conventional commit format, categorization will be best-effort based on commit message keywords and file paths. Note the limitation and recommend adopting conventional commits.
- **Incomplete period**: If the retrospective is generated mid-sprint, clearly label it as a progress report rather than a retrospective, and note which planned work is still in progress.

## Related Skills

- **e-recap** (eskill-meta): Run e-recap before this skill to collect the session summaries that feed into the retrospective.
- **e-health** (eskill-meta): Follow up with e-health after this skill to track whether retrospective action items improve project metrics.
