# GitHub Recovery

Transform a GitHub account from a collection of learning repositories into a professional engineering portfolio.

## Overview

This project treats GitHub cleanup as an engineering effort — with planning, issues, milestones, automation, and AI-assisted workflows — rather than ad-hoc edits.

## Structure

```
GitHub-Recovery/
├── docs/          # Vision, roadmap, and planning documents
├── prompts/       # Reusable prompts for Cursor agents
├── reports/       # Generated inventory and analysis reports
│   ├── classification/  # Category-grouped reports from inventory review
│   └── showcase/        # Portfolio shortlist and roadmap from Showcase repos
├── scripts/       # Automation scripts (inventory, scoring, cleanup)
└── .cursor/       # Cursor rules and project-specific AI guidance
```

## Roadmap

- Sprint 0 — Environment Setup ✅
- Sprint 1 — Project Initialization
- Sprint 2 — Repository Inventory
- Sprint 3 — Repository Classification
- Sprint 4 — Repository Cleanup
- Sprint 5 — Portfolio Optimization

## Workflow

```
You → Cursor Agent → GitHub MCP → GitHub
```

Cursor inspects repositories, drafts changes, and generates reports. You review and approve every permanent change.

## Getting Started

1. Review [docs/vision.md](docs/vision.md) for project goals.
2. Review [docs/roadmap.md](docs/roadmap.md) for phases and milestones.
3. Review [docs/portfolio-improvement-workflow.md](docs/portfolio-improvement-workflow.md) for the Sprint 3 execution framework.
4. Connect Cursor to the GitHub MCP for repository operations.
5. Use `prompts/` for repeatable agent tasks and `reports/` for output.

## Reports

| Report | Description |
|--------|-------------|
| `reports/repository-inventory.md` | Master inventory of all repositories with category, priority, and notes |
| `reports/classification/` | Grouped reports generated from the completed inventory review |
| `reports/showcase/portfolio-shortlist.md` | Ranked Tier 1–3 recommendations for Showcase repositories |
| `reports/showcase/portfolio-roadmap.md` | Per-repository improvement workflow for Tier 1 repositories |
| `reports/showcase/portfolio-summary.md` | Tier counts and portfolio focus guidance |
| `reports/showcase/portfolio-analysis.md` | Rich analysis of each Tier 1 repository (technology, audience, effort) |
| `reports/showcase/common-improvement-checklist.md` | Standard checklist every portfolio repository should complete |

Regenerate classification reports after inventory changes:

```bash
python scripts/generate_classification_reports.py
```

Regenerate showcase portfolio reports after classification changes:

```bash
python scripts/generate_showcase_reports.py
```

See [docs/repository-review-guide.md](docs/repository-review-guide.md) for the repository review tool.

## Safety

- All GitHub write operations require explicit approval.
- No automatic file deletion or repository changes without review.
- Read-only inventory and analysis first; edits second.
