#!/usr/bin/env python3
"""
Generate classification reports from reports/repository-inventory.md.

Reads reviewed Category, Priority, and Notes values and writes grouped
Markdown reports to reports/classification/.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INVENTORY = ROOT / "reports" / "repository-inventory.md"
DEFAULT_OUTPUT_DIR = ROOT / "reports" / "classification"

# Category values exactly as stored in the inventory.
CATEGORY_SHOWCASE = "⭐ Showcase"
CATEGORY_KEEP = "✅ Keep"
CATEGORY_ARCHIVE = "📦 Archive"
CATEGORY_PRIVATE = "🔒 Private"
CATEGORY_DELETE = "🗑 Delete"
CATEGORY_FORK_REVIEW = "🍴 Fork Cleanup"

CATEGORY_REPORTS = [
    (CATEGORY_SHOWCASE, "showcase.md", "Showcase Repositories", "Showcase"),
    (CATEGORY_KEEP, "keep.md", "Keep Repositories", "Keep"),
    (CATEGORY_ARCHIVE, "archive.md", "Archive Repositories", "Archive"),
    (CATEGORY_PRIVATE, "private.md", "Private Repositories", "Private"),
    (CATEGORY_DELETE, "delete.md", "Delete Repositories", "Delete"),
    (CATEGORY_FORK_REVIEW, "fork-review.md", "Fork Review Repositories", "Fork Review"),
]

KNOWN_CATEGORIES = {category for category, *_ in CATEGORY_REPORTS}


def import_inventory_parser():
    """Import inventory parsing from the review tool."""
    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from review_repositories import parse_inventory

    return parse_inventory


def escape_table_cell(value: str) -> str:
    """Escape pipe characters for markdown tables."""
    return value.replace("|", "\\|").replace("\n", " ")


def format_repo_table(repos: list[dict[str, str]]) -> str:
    """Format repositories as a markdown table."""
    lines = [
        "| Repository Name | Priority | Notes |",
        "|---|---|---|",
    ]
    for repo in repos:
        name = escape_table_cell(repo["name"])
        priority = escape_table_cell(repo.get("priority", ""))
        notes = escape_table_cell(repo.get("notes", ""))
        lines.append(f"| {name} | {priority} | {notes} |")
    return "\n".join(lines)


def write_category_report(
    output_dir: Path,
    filename: str,
    title: str,
    count_label: str,
    repos: list[dict[str, str]],
) -> Path:
    """Write a single category report."""
    output_path = output_dir / filename
    repos_sorted = sorted(repos, key=lambda repo: repo["name"].lower())

    lines = [
        f"# {title}",
        "",
        f"Total {count_label} repositories: {len(repos_sorted)}",
        "",
    ]

    if repos_sorted:
        lines.append(format_repo_table(repos_sorted))
    else:
        lines.append("_No repositories in this category._")

    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def write_summary_report(
    output_dir: Path,
    repos: list[dict[str, str]],
    grouped: dict[str, list[dict[str, str]]],
) -> Path:
    """Write the classification summary overview."""
    output_path = output_dir / "summary.md"

    priority_counts = {"P1": 0, "P2": 0, "P3": 0}
    with_notes = 0
    without_notes = 0
    unclassified: list[dict[str, str]] = []

    for repo in repos:
        priority = repo.get("priority", "").strip()
        if priority in priority_counts:
            priority_counts[priority] += 1

        notes = repo.get("notes", "").strip()
        if notes:
            with_notes += 1
        else:
            without_notes += 1

        category = repo.get("category", "").strip()
        if category not in KNOWN_CATEGORIES:
            unclassified.append(repo)

    lines = [
        "# Classification Summary",
        "",
        "Overview of repository classifications from the completed inventory review.",
        "",
        "## Totals",
        "",
        f"- **Total repositories:** {len(repos)}",
        f"- **Showcase:** {len(grouped[CATEGORY_SHOWCASE])}",
        f"- **Keep:** {len(grouped[CATEGORY_KEEP])}",
        f"- **Archive:** {len(grouped[CATEGORY_ARCHIVE])}",
        f"- **Private:** {len(grouped[CATEGORY_PRIVATE])}",
        f"- **Delete:** {len(grouped[CATEGORY_DELETE])}",
        f"- **Fork Review:** {len(grouped[CATEGORY_FORK_REVIEW])}",
        f"- **Unclassified repositories:** {len(unclassified)}",
        "",
        "## Priority Totals",
        "",
        f"- **P1:** {priority_counts['P1']}",
        f"- **P2:** {priority_counts['P2']}",
        f"- **P3:** {priority_counts['P3']}",
        "",
        "## Notes",
        "",
        f"- **Repositories with notes:** {with_notes}",
        f"- **Repositories without notes:** {without_notes}",
        "",
        "## Category Reports",
        "",
        "- [Showcase](showcase.md)",
        "- [Keep](keep.md)",
        "- [Archive](archive.md)",
        "- [Private](private.md)",
        "- [Delete](delete.md)",
        "- [Fork Review](fork-review.md)",
        "",
    ]

    if unclassified:
        lines.extend(
            [
                "## Unclassified",
                "",
                (
                    "The following repositories have no recognized category in the "
                    "inventory. They are listed here for visibility only."
                ),
                "",
                format_repo_table(sorted(unclassified, key=lambda repo: repo["name"].lower())),
                "",
            ]
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def group_repositories(repos: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    """Group repositories by category value."""
    grouped = {category: [] for category, *_ in CATEGORY_REPORTS}

    for repo in repos:
        category = repo.get("category", "").strip()
        if category in grouped:
            grouped[category].append(repo)

    return grouped


def generate_reports(inventory_path: Path, output_dir: Path) -> list[Path]:
    """Generate all classification reports."""
    parse_inventory = import_inventory_parser()
    _, repos = parse_inventory(inventory_path)
    grouped = group_repositories(repos)

    output_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []

    for category, filename, title, count_label in CATEGORY_REPORTS:
        created.append(
            write_category_report(
                output_dir,
                filename,
                title,
                count_label,
                grouped[category],
            )
        )

    created.append(write_summary_report(output_dir, repos, grouped))
    return created


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate classification reports from repository-inventory.md"
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=DEFAULT_INVENTORY,
        help="Path to repository inventory markdown file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for generated classification reports",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if not args.inventory.exists():
        print(f"Inventory not found: {args.inventory}", file=sys.stderr)
        return 1

    created = generate_reports(args.inventory, args.output_dir)
    print(f"Generated {len(created)} reports in {args.output_dir}")
    for path in created:
        print(f"  - {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
