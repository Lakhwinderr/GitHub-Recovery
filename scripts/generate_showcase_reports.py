#!/usr/bin/env python3
"""
Generate showcase portfolio reports from reports/classification/showcase.md.

Tier assignments are recommendations only. They do not modify the inventory
or change Category, Priority, or Notes values.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SHOWCASE_REPORT = ROOT / "reports" / "classification" / "showcase.md"
DEFAULT_OUTPUT_DIR = ROOT / "reports" / "showcase"

# Tier recommendations: (repository name, rationale).
# Priority and Notes are read from showcase.md at generation time.
TIER_1 = [
    (
        "FreshHireAI",
        "Flagship project combining Python, AI, and a real-world job-search problem. "
        "Actively in development and strongest signal of current engineering direction.",
    ),
    (
        "Open-Source-Discovery",
        "Original open-source tool with community traction (5 stars). Demonstrates "
        "full-stack JavaScript skills and contribution to the OSS ecosystem.",
    ),
    (
        "GitHub-Recovery",
        "Meta-engineering project showing structured approach to portfolio improvement, "
        "documentation, automation, and project management.",
    ),
    (
        "LifeAnalysis",
        "Unique JavaScript project that analyzes personal search history. Shows "
        "initiative, data thinking, and ability to build practical tools.",
    ),
    (
        "little-lemon",
        "META Frontend Capstone project. Represents structured frontend training and "
        "a complete restaurant website application.",
    ),
    (
        "Databases-with-Appwrite--Lakhwinder-Hitlist",
        "Demonstrates backend skills with Appwrite. Strong full-stack signal beyond "
        "frontend-only tutorials.",
    ),
    (
        "Portfolio",
        "Primary portfolio website. Central to recruiter first impressions and should "
        "reflect current skills and project quality.",
    ),
    (
        "Lakhwinderr.github.io",
        "Personal blog and public presence. Supports personal brand and gives "
        "recruiters additional context beyond code repositories.",
    ),
    (
        "saucedemo-manual-testing",
        "Differentiates the profile with software testing and QA skills, a less "
        "common strength among frontend-focused candidates.",
    ),
]

TIER_2 = [
    (
        "Auth0-Project",
        "Authentication integration project worth polishing once core portfolio "
        "repositories are complete.",
    ),
    (
        "Fibery-Demo",
        "Scheduling demo with JavaScript. Useful supporting project after Tier 1 "
        "repositories are portfolio-ready.",
    ),
    (
        "InnovateHub",
        "HTML/CSS project that can be improved to demonstrate design and layout skills.",
    ),
    (
        "Github-Repo-Tracker",
        "Practical JavaScript tool aligned with GitHub workflow. Good follow-up "
        "project after core portfolio polish.",
    ),
    (
        "JavaScript30",
        "Collection of 30 small JavaScript exercises. Valuable as a skills archive, "
        "but not a primary portfolio centerpiece.",
    ),
    (
        "FreeCodeCamp-Responsive-Design",
        "Demonstrates responsive design fundamentals from FreeCodeCamp. Worth "
        "improving after flagship projects are done.",
    ),
    (
        "Timer-App",
        "Productivity timer with production potential. Strong candidate once Tier 1 "
        "work is complete.",
    ),
    (
        "cvless",
        "Jekyll theme exploration for online CVs. Useful later for personal branding, "
        "but lower urgency than active projects.",
    ),
]

TIER_3 = [
    (
        "50-HTML-CSS-JS-Project-Challenge",
        "Learning challenge collection. Showcase-worthy but low priority compared "
        "to career-defining projects.",
    ),
    (
        "Frontend-Mentor---Blog-preview-card",
        "Small Frontend Mentor exercise. Good practice piece, not a primary portfolio anchor.",
    ),
    (
        "Frontend-Mentor---QR-code-component",
        "Small Frontend Mentor exercise. Polished UI sample, but limited scope.",
    ),
    (
        "Frontend-Mentor---Social-links-profile",
        "Small Frontend Mentor exercise. Useful as a supporting example only.",
    ),
    (
        "Lakhwinderr",
        "GitHub profile configuration repository. Important for profile setup, but not "
        "a software project to polish for recruiters.",
    ),
    (
        "Lucky-Shrubs-Portfolio-Project",
        "Early HTML portfolio-style project. P2 priority and better suited for later cleanup.",
    ),
    (
        "SnakeGame2",
        "Beginner game project. Fun showcase of early JavaScript learning, but low "
        "recruiter impact compared to Tier 1 work.",
    ),
]

TIER_SECTIONS = [
    ("tier1", "Tier 1 — Immediate Portfolio Focus", TIER_1, "Why it belongs in Tier 1"),
    ("tier2", "Tier 2 — Future Portfolio Candidates", TIER_2, "Reason"),
    ("tier3", "Tier 3 — Showcase but Low Priority", TIER_3, "Reason"),
]

ROADMAP_STEPS = [
    "Review code quality",
    "Improve README",
    "Add screenshots",
    "Add topics",
    "Add license",
    "Clean repository",
    "Final portfolio review",
]


def parse_showcase_report(path: Path) -> dict[str, dict[str, str]]:
    """Parse repository name, priority, and notes from showcase.md."""
    repos: dict[str, dict[str, str]] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    in_table = False

    for line in lines:
        if line.startswith("| Repository Name |"):
            in_table = True
            continue
        if not in_table or not line.startswith("|"):
            continue
        if line.startswith("|---"):
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 3:
            continue

        name, priority, notes = cells
        repos[name] = {"name": name, "priority": priority, "notes": notes}

    if not repos:
        raise ValueError(f"No showcase repositories found in {path}")

    return repos


def validate_tier_coverage(showcase_repos: dict[str, dict[str, str]]) -> None:
    """Ensure every showcase repository appears in exactly one tier."""
    assigned: list[str] = []
    for _, _, tier_repos, _ in TIER_SECTIONS:
        assigned.extend(name for name, _ in tier_repos)

    showcase_names = set(showcase_repos)
    assigned_names = set(assigned)

    missing = sorted(showcase_names - assigned_names)
    extra = sorted(assigned_names - showcase_names)
    duplicates = sorted({name for name in assigned if assigned.count(name) > 1})

    errors: list[str] = []
    if missing:
        errors.append(f"Missing from tiers: {', '.join(missing)}")
    if extra:
        errors.append(f"Not in showcase.md: {', '.join(extra)}")
    if duplicates:
        errors.append(f"Duplicated in tiers: {', '.join(duplicates)}")

    if errors:
        raise ValueError("Tier validation failed:\n" + "\n".join(errors))


def format_tier_entry(
    name: str,
    rationale: str,
    repo: dict[str, str],
    rationale_label: str,
) -> list[str]:
    """Format a single repository entry for a tier section."""
    priority = repo.get("priority", "") or "(none)"
    notes = repo.get("notes", "") or "(none)"
    return [
        f"### {name}",
        "",
        f"- **{rationale_label}:** {rationale}",
        f"- **Current Priority:** {priority}",
        f"- **Existing Notes:** {notes}",
        "",
    ]


def write_portfolio_shortlist(
    output_dir: Path,
    showcase_repos: dict[str, dict[str, str]],
) -> Path:
    """Write the ranked portfolio shortlist."""
    output_path = output_dir / "portfolio-shortlist.md"
    lines = [
        "# Portfolio Shortlist",
        "",
        (
            "Ranked recommendations for Showcase repositories. Tier assignments are "
            "guidance only and do not change inventory Category, Priority, or Notes."
        ),
        "",
        f"**Total Showcase repositories:** {len(showcase_repos)}",
        "",
    ]

    for _, heading, tier_repos, rationale_label in TIER_SECTIONS:
        lines.extend([f"## {heading}", ""])
        for name, rationale in tier_repos:
            lines.extend(format_tier_entry(name, rationale, showcase_repos[name], rationale_label))

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def write_portfolio_roadmap(output_dir: Path) -> Path:
    """Write the Tier 1 improvement roadmap."""
    output_path = output_dir / "portfolio-roadmap.md"
    lines = [
        "# Portfolio Roadmap",
        "",
        "Recommended improvement workflow for Tier 1 repositories.",
        "",
        "This defines future work only. No implementation is included here.",
        "",
    ]

    tier1_names = [name for name, _ in TIER_1]
    for index, name in enumerate(tier1_names, start=1):
        lines.append(f"## {index}. {name}")
        lines.append("")
        workflow = [name, *ROADMAP_STEPS]
        for step_index, step in enumerate(workflow):
            lines.append(step)
            if step_index < len(workflow) - 1:
                lines.append("")
                lines.append("↓")
                lines.append("")
        lines.append("")
        lines.append("---")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def write_portfolio_summary(
    output_dir: Path,
    showcase_repos: dict[str, dict[str, str]],
) -> Path:
    """Write the showcase portfolio summary."""
    output_path = output_dir / "portfolio-summary.md"
    tier_counts = {key: len(tier) for key, _, tier, _ in TIER_SECTIONS}

    lines = [
        "# Portfolio Summary",
        "",
        "## Counts",
        "",
        f"- **Total Showcase repositories:** {len(showcase_repos)}",
        f"- **Tier 1 — Immediate Portfolio Focus:** {tier_counts['tier1']}",
        f"- **Tier 2 — Future Portfolio Candidates:** {tier_counts['tier2']}",
        f"- **Tier 3 — Showcase but Low Priority:** {tier_counts['tier3']}",
        "",
        "## Why Focus on Fewer Repositories?",
        "",
        (
            "A GitHub profile with a small number of excellent repositories creates a "
            "stronger impression than a large collection of uneven projects. Recruiters "
            "spend limited time reviewing profiles, so the goal is to guide them quickly "
            "to your best work."
        ),
        "",
        (
            "Tier 1 focuses polish on the repositories that best represent current skills, "
            "career direction, and project depth. Tier 2 and Tier 3 remain valuable, but "
            "they should be improved after the primary portfolio story is clear."
        ),
        "",
        "## Related Reports",
        "",
        "- [Portfolio Shortlist](portfolio-shortlist.md)",
        "- [Portfolio Roadmap](portfolio-roadmap.md)",
        "- [Showcase Classification](../classification/showcase.md)",
        "",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def generate_reports(showcase_path: Path, output_dir: Path) -> list[Path]:
    """Generate all showcase portfolio reports."""
    showcase_repos = parse_showcase_report(showcase_path)
    validate_tier_coverage(showcase_repos)

    output_dir.mkdir(parents=True, exist_ok=True)

    return [
        write_portfolio_shortlist(output_dir, showcase_repos),
        write_portfolio_roadmap(output_dir),
        write_portfolio_summary(output_dir, showcase_repos),
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate showcase portfolio reports from classification/showcase.md"
    )
    parser.add_argument(
        "--showcase",
        type=Path,
        default=DEFAULT_SHOWCASE_REPORT,
        help="Path to showcase classification report",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for generated showcase reports",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if not args.showcase.exists():
        print(f"Showcase report not found: {args.showcase}", file=sys.stderr)
        return 1

    try:
        created = generate_reports(args.showcase, args.output_dir)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    print(f"Generated {len(created)} reports in {args.output_dir}")
    for path in created:
        print(f"  - {path.name}")

    showcase_repos = parse_showcase_report(args.showcase)
    print(f"Verified {len(showcase_repos)} showcase repositories across 3 tiers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
