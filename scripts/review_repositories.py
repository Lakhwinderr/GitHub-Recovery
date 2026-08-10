#!/usr/bin/env python3
"""
GitHub Recovery — Repository Review Tool

Interactive CLI to classify and prioritize repositories listed in
reports/repository-inventory.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INVENTORY = ROOT / "reports" / "repository-inventory.md"
DEFAULT_PROGRESS = ROOT / "reports" / ".review-progress.json"

BANNER_WIDTH = 58
REVIEW_BACK = "__BACK__"

COLUMNS = [
    "name",
    "created",
    "visibility",
    "fork",
    "archived",
    "language",
    "description",
    "topics",
    "stars",
    "category",
    "priority",
    "notes",
]

# Maps menu selection to inventory Category column value.
CATEGORY_MENU = {
    "1": "⭐ Showcase",
    "2": "✅ Keep",
    "3": "📦 Archive",
    "4": "🔒 Private",
    "5": "🗑 Delete",
    "6": "🍴 Fork Cleanup",
    "0": "",
}

# Maps menu selection to inventory Priority column value.
PRIORITY_MENU = {
    "1": "P1",
    "2": "P2",
    "3": "P3",
    "0": "",
}

# Predefined note options (multi-select supported).
NOTES_PREDEFINED = {
    "1": "Needs README",
    "2": "Organize Files/Folders",
    "3": "Add Screenshots",
    "4": "Rename Repository",
    "5": "Add Topics",
    "6": "Improve Documentation",
    "7": "Remove Unnecessary Files",
}

NOTES_CUSTOM_KEY = "8"
NOTES_SKIP_KEY = "0"
NOTES_SEPARATOR = "; "

# Legacy label kept so older progress entries remain readable.
LEGACY_NOTE_LABELS = {
    "Needs Cleanup": "Organize Files/Folders",
}

SORT_CREATED = "created"
SORT_ALPHABETICAL = "alphabetical"
SORT_CHOICES = (SORT_CREATED, SORT_ALPHABETICAL)

PROGRESS_VERSION = 2
PROGRESS_RESERVED_KEYS = {
    "reviews",
    "completed",
    "version",
    "last_index",
    "reviewed_indices",
    "reviewed_numbers",
    "reviewed_repos",
    "review_order",
}
REVIEW_FIELDS = frozenset({"category", "priority", "notes"})


class ProgressFormatError(Exception):
    """Raised when a progress file cannot be read or migrated."""


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def display_path(path: Path) -> str:
    """Show a project-relative path when possible."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def print_rule(char: str = "=", width: int = BANNER_WIDTH) -> None:
    print(char * width)


def display_field(label: str, value: str) -> None:
    """Print a labeled field, using '(none)' for empty values."""
    print(f"{label}")
    print(value if value else "(none)")
    print()


# ---------------------------------------------------------------------------
# Help and guides
# ---------------------------------------------------------------------------


def print_help() -> None:
    """Print full tool documentation."""
    print_rule()
    print("GitHub Recovery Repository Review Tool")
    print_rule()
    print()
    print("PURPOSE")
    print("  Classify and prioritize every repository in your GitHub account")
    print("  inventory as part of the GitHub Recovery project.")
    print()
    print("WORKFLOW")
    print("  1. Review each repository one at a time")
    print("  2. Assign a category, priority, and optional notes")
    print("  3. Progress is saved after every repository")
    print("  4. Resume anytime if you stop midway")
    print("  5. Inventory report updates automatically when finished")
    print()
    print("COMMANDS")
    print("  python scripts/review_repositories.py")
    print("      Start or resume the interactive review session.")
    print()
    print("  python scripts/review_repositories.py help")
    print("  python scripts/review_repositories.py --help")
    print("      Show this help screen.")
    print()
    print("  python scripts/review_repositories.py --status")
    print("  python scripts/review_repositories.py status")
    print("      Show review progress and file locations.")
    print()
    print("  python scripts/review_repositories.py --edit")
    print("  python scripts/review_repositories.py edit")
    print("      Edit a previously reviewed repository.")
    print()
    print("  python scripts/review_repositories.py --reset")
    print("      Clear saved progress and start from the beginning.")
    print()
    print("  python scripts/review_repositories.py --sort created")
    print("      Review in creation-date order, oldest first (default).")
    print()
    print("  python scripts/review_repositories.py --sort alphabetical")
    print("      Review in alphabetical order by repository name.")
    print()
    print("  python scripts/review_repositories.py --inventory PATH")
    print("      Use a custom inventory markdown file.")
    print()
    print("  python scripts/review_repositories.py --progress PATH")
    print("      Use a custom progress JSON file.")
    print()
    print("REVIEW SHORTCUTS")
    print("  help  Show contextual guidance during prompts.")
    print("  back  Reopen the previous repository (one step back).")
    print()
    print("RESUME")
    print("  Progress is stored by repository name in reports/.review-progress.json.")
    print("  Review order does not affect saved progress — only repository names are used.")
    print("  Re-run the tool to continue where you left off.")
    print("  Press Ctrl+C at any time — the last saved repository is kept.")
    print()
    print("OUTPUT FILES")
    print(f"  Inventory : {display_path(DEFAULT_INVENTORY)}")
    print(f"  Progress  : {display_path(DEFAULT_PROGRESS)}")
    print()
    print_category_guide()
    print_priority_guide()
    print_notes_guide()


def print_category_guide() -> None:
    """Explain category options."""
    print_rule("-")
    print("Category = What should happen to the repository?")
    print_rule("-")
    print()
    print('This answers: "What is the final status of this repository?"')
    print()
    print("  1  ⭐ Showcase")
    print("     Portfolio-quality repository.")
    print("     One of the repositories I would proudly show recruiters.")
    print()
    print("  2  ✅ Keep")
    print("     Keep public. Useful repository. No major improvements planned.")
    print()
    print("  3  📦 Archive")
    print("     Keep for historical purposes. Archive on GitHub.")
    print()
    print("  4  🔒 Private")
    print("     Move to private visibility.")
    print()
    print("  5  🗑 Delete")
    print("     Safe to permanently remove.")
    print()
    print("  6  🍴 Fork Cleanup")
    print("     Review the fork. Decide whether to keep, archive, unfork, or delete.")
    print()
    print("  0  Skip")
    print("     Leave unchanged for now.")
    print()


def print_priority_guide() -> None:
    """Explain priority options."""
    print_rule("-")
    print("Priority = When should I spend time improving this repository?")
    print_rule("-")
    print()
    print('This answers: "When should I spend time improving this repository?"')
    print()
    print("  1  P1 — Highest priority. Work on soon.")
    print("     Examples: FreshHireAI, company-atlas, Arduino, GitHub-Recovery")
    print()
    print("  2  P2 — Medium priority. Improve later.")
    print("     Examples: Portfolio, React-Basics, OOP-Learning")
    print()
    print("  3  P3 — Low priority.")
    print("     Examples: Tutorials, Hacktoberfest repos, course exercises, old experiments")
    print()
    print("  0  Skip — Leave priority blank.")
    print()


def print_notes_guide() -> None:
    """Explain quick-notes options."""
    print_rule("-")
    print("Notes — Quick tags or custom comments")
    print_rule("-")
    print()
    print("  Enter one or more numbers, separated by commas (e.g. 1,3,5).")
    print("  Select 8 to add a custom note alongside predefined tags.")
    print()
    for key in sorted(NOTES_PREDEFINED, key=lambda value: int(value)):
        print(f"  {key}  {NOTES_PREDEFINED[key]}")
    print(f"  {NOTES_CUSTOM_KEY}  Custom Note")
    print(f"  {NOTES_SKIP_KEY}  No Notes")
    print()
    print("  Stored in the inventory as semicolon-separated values.")
    print()


def print_recruiter_reminder() -> None:
    """Prompt the reviewer to think like a recruiter."""
    print_rule("-")
    print()
    print("Ask yourself:")
    print()
    print('"If a recruiter opened this repository today,')
    print(' would it help me get an interview?"')
    print()
    print_rule("-")
    print()


def print_startup_banner(
    inventory_path: Path,
    progress_path: Path,
    reviewed_count: int,
    total: int,
) -> None:
    """Display the session banner."""
    print()
    print_rule()
    print("GitHub Recovery Repository Review Tool")
    print_rule()
    print()
    print("Workflow")
    print()
    print("Review")
    print("→ Save Progress")
    print("→ Resume Anytime")
    print("→ Update Inventory Report")
    print()
    print(f"Inventory:\n{display_path(inventory_path)}")
    print()
    print(f"Progress File:\n{display_path(progress_path)}")
    print()
    print(f"Repositories Reviewed:\n{reviewed_count} / {total}")
    print()
    print_rule()
    print()


def print_progress_saved(reviewed_count: int, total: int) -> None:
    """Show save confirmation and remaining work."""
    remaining = total - reviewed_count
    print()
    print("✔ Saved")
    print()
    print("Progress:")
    print(f"{reviewed_count} / {total} repositories reviewed")
    print()
    print("Remaining:")
    print(remaining)
    print()


def print_status(inventory_path: Path, progress_path: Path) -> int:
    """Display current review progress using repository names."""
    if not inventory_path.exists():
        print(f"Inventory not found: {inventory_path}", file=sys.stderr)
        return 1

    _, repos = parse_inventory(inventory_path)
    repo_names = [repo["name"] for repo in repos]
    try:
        progress = load_progress(progress_path, repo_names, migrate=True)
    except ProgressFormatError as exc:
        print(f"Progress file error: {exc}", file=sys.stderr)
        return 1

    reviews = get_reviews(progress)
    total = len(repos)
    done = count_reviewed(repos, reviews)
    remaining = total - done

    print()
    print("Reviewed:")
    print(f"{done} / {total}")
    print()
    print("Remaining:")
    print(remaining)
    print()
    print("Current inventory:")
    print(display_path(inventory_path))
    print()
    print("Progress file:")
    print(display_path(progress_path))
    print()
    return 0


def print_completion_screen(inventory_path: Path) -> None:
    """Display the final summary when all repositories are reviewed."""
    print()
    print_rule()
    print()
    print("Repository Review Complete")
    print()
    print("✔ Inventory updated")
    print()
    print("Output:")
    print()
    print(display_path(inventory_path))
    print()
    print("Progress file can now be deleted if desired.")
    print()
    print("Next Suggested Workflow")
    print()
    print("Repository Classification")
    print("↓")
    print()
    print("Showcase Selection")
    print("↓")
    print()
    print("Portfolio Improvements")
    print()
    print_rule()
    print()


def sort_repositories(repos: list[dict[str, str]], sort_mode: str) -> list[dict[str, str]]:
    """
    Return repositories in review order.

    Progress is keyed by repository name, so sort order does not affect resume.
    """
    if sort_mode == SORT_ALPHABETICAL:
        return sorted(repos, key=lambda repo: repo["name"].lower())

    def created_sort_key(repo: dict[str, str]) -> tuple[int, datetime, str]:
        created = repo.get("created", "").strip()
        try:
            parsed = datetime.strptime(created, "%Y-%m-%d")
            return (0, parsed, repo["name"].lower())
        except ValueError:
            # Repositories without a valid date are reviewed last.
            return (1, datetime.max, repo["name"].lower())

    return sorted(repos, key=created_sort_key)


# ---------------------------------------------------------------------------
# Inventory I/O
# ---------------------------------------------------------------------------


def split_table_row(line: str) -> list[str]:
    """Split a markdown table row, respecting escaped pipe characters."""
    line = line.strip()
    if not line.startswith("|"):
        return []

    content = line[1:]
    if content.endswith("|"):
        content = content[:-1]

    cells: list[str] = []
    current: list[str] = []
    i = 0
    while i < len(content):
        if content[i] == "\\" and i + 1 < len(content) and content[i + 1] == "|":
            current.append("|")
            i += 2
            continue
        if content[i] == "|":
            cells.append("".join(current).strip())
            current = []
            i += 1
            continue
        current.append(content[i])
        i += 1

    cells.append("".join(current).strip())
    return cells


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|")


def parse_inventory(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Return preamble lines and parsed repository rows."""
    lines = path.read_text(encoding="utf-8").splitlines()
    preamble: list[str] = []
    repos: list[dict[str, str]] = []
    in_table = False

    for line in lines:
        if line.startswith("| Repository Name |"):
            preamble.append(line)
            in_table = True
            continue

        if in_table:
            if line.startswith("|---"):
                preamble.append(line)
                continue
            if line.startswith("|"):
                cells = split_table_row(line)
                if len(cells) != len(COLUMNS):
                    raise ValueError(
                        f"Expected {len(COLUMNS)} columns, got {len(cells)} in row: {line}"
                    )
                repos.append(dict(zip(COLUMNS, cells)))
                continue
            in_table = False

        if not repos:
            preamble.append(line)

    return preamble, repos


def format_row(repo: dict[str, str]) -> str:
    values = [escape_cell(repo[col]) for col in COLUMNS]
    return "| " + " | ".join(values) + " |"


def write_inventory(path: Path, preamble: list[str], repos: list[dict[str, str]]) -> None:
    lines = preamble + [format_row(repo) for repo in repos]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_progress(
    path: Path,
    repo_names: list[str] | None = None,
    migrate: bool = True,
) -> dict:
    """
    Load review progress keyed by repository name.

    Progress is never stored by list index or position. Repository names are
    the only identifiers used for resume, edit, and status reporting.
    """
    if not path.exists():
        return empty_progress()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProgressFormatError(
            f"Progress file is not valid JSON: {path}"
        ) from exc

    if not isinstance(data, dict):
        raise ProgressFormatError("Progress file must contain a JSON object.")

    names = repo_names or []
    progress, migrated = normalize_progress(data, names)

    if migrate and migrated:
        save_progress(path, progress)
        print("Migrated progress file to name-based format.")

    return progress


def empty_progress() -> dict:
    """Return a new, empty progress document."""
    return {
        "version": PROGRESS_VERSION,
        "reviews": {},
        "completed": False,
    }


def is_review_record(value: object) -> bool:
    """Return True when a value looks like a saved repository review."""
    return isinstance(value, dict) and REVIEW_FIELDS.intersection(value.keys())


def normalize_review_record(value: object) -> dict[str, str]:
    """Normalize a review record to the expected field set."""
    if not isinstance(value, dict):
        return {"category": "", "priority": "", "notes": ""}

    return {
        "category": str(value.get("category", "")),
        "priority": str(value.get("priority", "")),
        "notes": normalize_legacy_notes(str(value.get("notes", ""))),
    }


def normalize_progress(data: dict, repo_names: list[str]) -> tuple[dict, bool]:
    """
    Normalize progress data to the canonical name-based format.

    Supports:
    - Current format: {"reviews": {"repo-name": {...}}}
    - Flat format: {"repo-name": {"category": ...}}
    - Legacy index format: {"reviewed_indices": [0, 1, 2]}
    """
    migrated = False
    reviews: dict[str, dict[str, str]] = {}
    name_set = set(repo_names)

    if isinstance(data.get("reviews"), dict):
        for name, review in data["reviews"].items():
            reviews[name] = normalize_review_record(review)

    for key, value in data.items():
        if key in PROGRESS_RESERVED_KEYS:
            continue
        if is_review_record(value):
            reviews[key] = normalize_review_record(value)
            migrated = True

    legacy_indices = data.get("reviewed_indices")
    if isinstance(legacy_indices, list) and repo_names:
        for index in legacy_indices:
            if isinstance(index, int) and 0 <= index < len(repo_names):
                name = repo_names[index]
                reviews.setdefault(
                    name,
                    {"category": "", "priority": "", "notes": ""},
                )
                migrated = True

    legacy_numbers = data.get("reviewed_numbers")
    if isinstance(legacy_numbers, list) and repo_names:
        for number in legacy_numbers:
            if isinstance(number, int):
                index = number - 1
                if 0 <= index < len(repo_names):
                    name = repo_names[index]
                    reviews.setdefault(
                        name,
                        {"category": "", "priority": "", "notes": ""},
                    )
                    migrated = True

    legacy_names = data.get("reviewed_repos")
    if isinstance(legacy_names, list):
        for name in legacy_names:
            if isinstance(name, str):
                reviews.setdefault(name, {"category": "", "priority": "", "notes": ""})
                migrated = True

    unknown_keys = [
        key
        for key in data
        if key not in PROGRESS_RESERVED_KEYS
        and key not in reviews
        and key not in name_set
        and not is_review_record(data[key])
    ]
    if unknown_keys and not reviews and "reviews" not in data:
        raise ProgressFormatError(
            "Unrecognized progress file format. "
            "Expected repository names as keys or a 'reviews' object. "
            f"Found unexpected keys: {', '.join(unknown_keys[:5])}"
        )

    progress = {
        "version": PROGRESS_VERSION,
        "reviews": reviews,
        "completed": bool(data.get("completed", False)),
    }
    return progress, migrated


def save_progress(path: Path, progress: dict) -> None:
    """Save progress using repository names as the only review identifiers."""
    progress["version"] = PROGRESS_VERSION
    progress.setdefault("reviews", {})
    path.write_text(json.dumps(progress, indent=2) + "\n", encoding="utf-8")


def get_reviews(progress: dict) -> dict[str, dict[str, str]]:
    """Return the name-keyed review map from progress data."""
    reviews = progress.setdefault("reviews", {})
    if not isinstance(reviews, dict):
        raise ProgressFormatError("Progress 'reviews' field must be an object.")
    return reviews


def is_reviewed(repo_name: str, reviews: dict[str, dict[str, str]]) -> bool:
    """Return True when a repository already has saved progress."""
    return repo_name in reviews


def count_reviewed(
    repos: list[dict[str, str]],
    reviews: dict[str, dict[str, str]],
) -> int:
    """Count how many inventory repositories have been reviewed."""
    return sum(1 for repo in repos if is_reviewed(repo["name"], reviews))


def get_unreviewed_repos(
    review_repos: list[dict[str, str]],
    reviews: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    """Return repositories without saved progress, preserving review order."""
    return [repo for repo in review_repos if not is_reviewed(repo["name"], reviews)]


def set_review(
    progress: dict,
    repo_name: str,
    review: dict[str, str],
) -> None:
    """Create or update a repository review by name."""
    reviews = get_reviews(progress)
    reviews[repo_name] = {
        "category": review.get("category", ""),
        "priority": review.get("priority", ""),
        "notes": review.get("notes", ""),
    }


def find_repo_index(repos: list[dict[str, str]], repo_name: str) -> int:
    """Find a repository's position in a sorted review list (display only)."""
    for index, repo in enumerate(repos):
        if repo["name"] == repo_name:
            return index
    raise ValueError(f"Repository not found: {repo_name}")


def find_next_unreviewed_index(
    review_repos: list[dict[str, str]],
    reviews: dict[str, dict[str, str]],
    start_index: int = 0,
) -> int:
    """Find the next repository without saved progress."""
    for index in range(start_index, len(review_repos)):
        if not is_reviewed(review_repos[index]["name"], reviews):
            return index
    return len(review_repos)


def normalize_legacy_notes(notes: str) -> str:
    """Map legacy note labels to current names without breaking saved progress."""
    if not notes:
        return notes

    parts = [part.strip() for part in notes.split(NOTES_SEPARATOR)]
    normalized: list[str] = []
    for part in parts:
        if not part:
            continue
        normalized.append(LEGACY_NOTE_LABELS.get(part, part))
    return NOTES_SEPARATOR.join(normalized)


def apply_review(repo: dict[str, str], review: dict[str, str]) -> None:
    repo["category"] = review.get("category", "")
    repo["priority"] = review.get("priority", "")
    repo["notes"] = normalize_legacy_notes(review.get("notes", ""))


def sync_repos_from_reviews(repos: list[dict[str, str]], reviewed: dict[str, dict[str, str]]) -> None:
    """Apply saved reviews to in-memory repository rows."""
    for repo in repos:
        if repo["name"] in reviewed:
            apply_review(repo, reviewed[repo["name"]])


def get_review_for_repo(
    repo: dict[str, str],
    reviewed: dict[str, dict[str, str]],
) -> dict[str, str]:
    """Return the current review data for a repository."""
    if repo["name"] in reviewed:
        review = reviewed[repo["name"]]
        return {
            "category": review.get("category", ""),
            "priority": review.get("priority", ""),
            "notes": normalize_legacy_notes(review.get("notes", "")),
        }

    return {
        "category": repo.get("category", ""),
        "priority": repo.get("priority", ""),
        "notes": normalize_legacy_notes(repo.get("notes", "")),
    }


def save_review(
    repo: dict[str, str],
    review: dict[str, str],
    progress: dict,
    progress_path: Path,
    repos: list[dict[str, str]],
    preamble: list[str],
    inventory_path: Path,
) -> None:
    """Persist a review by repository name to progress, memory, and inventory."""
    set_review(progress, repo["name"], review)
    apply_review(repo, review)
    save_progress(progress_path, progress)

    if progress.get("completed"):
        sync_repos_from_reviews(repos, get_reviews(progress))
        write_inventory(inventory_path, preamble, repos)


def finalize_inventory(
    inventory_path: Path,
    progress_path: Path,
    preamble: list[str],
    repos: list[dict[str, str]],
    progress: dict,
) -> None:
    """Merge name-keyed reviews into the inventory and mark the session complete."""
    sync_repos_from_reviews(repos, get_reviews(progress))
    write_inventory(inventory_path, preamble, repos)
    progress["completed"] = True
    save_progress(progress_path, progress)


# ---------------------------------------------------------------------------
# Interactive prompts
# ---------------------------------------------------------------------------


def prompt_yes_no(message: str) -> bool:
    """Prompt for a yes/no answer."""
    while True:
        answer = input(f"{message} ").strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Invalid input. Enter Y or N.")


def display_repo(repo: dict[str, str], position: int, total: int) -> None:
    """Show repository details for the current review step."""
    print()
    print_rule()
    print(f"Repository {position} / {total}")
    print_rule()
    print(f"Name:        {repo['name']}")
    print()
    print("Created:")
    print(repo["created"] or "(unknown)")
    print()
    print(f"Visibility:  {repo['visibility']}")
    print(f"Fork:        {repo['fork']}")
    print(f"Archived:    {repo['archived']}")
    print(f"Language:    {repo['language'] or '(none)'}")
    print(f"Description: {repo['description'] or '(none)'}")
    print(f"Topics:      {repo['topics'] or '(none)'}")
    print()


def display_current_review(repo_name: str, review: dict[str, str]) -> None:
    """Show the saved category, priority, and notes for a repository."""
    print()
    print("Repository:")
    print(repo_name)
    print()
    display_field("Current Category:", review.get("category", ""))
    display_field("Current Priority:", review.get("priority", ""))

    notes = review.get("notes", "")
    print("Current Notes:")
    if notes:
        for note in [part.strip() for part in notes.split(NOTES_SEPARATOR) if part.strip()]:
            print(note)
    else:
        print("(none)")
    print()


def prompt_menu_key(
    label: str,
    valid_keys: set[str],
    option_labels: dict[str, str],
    help_callback: Callable[[], None] | None = None,
    allow_back: bool = False,
) -> str:
    """
    Prompt for a numbered menu choice and return the selected key.

    Type 'help' to show contextual guidance.
    Type 'back' to return to the previous repository during review.
    """
    while True:
        print(label)
        for key in sorted(valid_keys, key=lambda value: (value == "0", value)):
            print(f"  {key} {option_labels.get(key, key)}")
        print()
        print("  Type 'help' for guidance.")
        if allow_back:
            print("  Type 'back' to reopen the previous repository.")
        print()

        choice = input("Choice: ").strip().lower()
        if choice == "help" and help_callback:
            help_callback()
            continue
        if allow_back and choice == "back":
            return REVIEW_BACK
        if choice in valid_keys:
            return choice
        valid = ", ".join(sorted(valid_keys))
        extra = ", back, or help" if allow_back else " or help"
        print(f"Invalid choice. Enter one of: {valid}{extra}.")


def prompt_category(allow_back: bool = False) -> str:
    """Collect the repository category."""
    print_recruiter_reminder()
    key = prompt_menu_key(
        "Category:",
        set(CATEGORY_MENU),
        {
            "1": "⭐ Showcase",
            "2": "✅ Keep",
            "3": "📦 Archive",
            "4": "🔒 Private",
            "5": "🗑 Delete",
            "6": "🍴 Fork Cleanup",
            "0": "Skip",
        },
        help_callback=print_category_guide,
        allow_back=allow_back,
    )
    if key == REVIEW_BACK:
        return REVIEW_BACK
    return CATEGORY_MENU[key]


def prompt_priority(allow_back: bool = False) -> str:
    """Collect the repository priority."""
    key = prompt_menu_key(
        "Priority:",
        set(PRIORITY_MENU),
        {
            "1": "P1",
            "2": "P2",
            "3": "P3",
            "0": "Skip",
        },
        help_callback=print_priority_guide,
        allow_back=allow_back,
    )
    if key == REVIEW_BACK:
        return REVIEW_BACK
    return PRIORITY_MENU[key]


def format_notes(selected_keys: list[str], custom_note: str = "") -> str:
    """Build the semicolon-separated notes string for the inventory."""
    notes: list[str] = []

    for key in selected_keys:
        if key in NOTES_PREDEFINED:
            notes.append(NOTES_PREDEFINED[key])

    custom_note = custom_note.strip()
    if custom_note:
        notes.append(custom_note)

    return NOTES_SEPARATOR.join(notes)


def parse_notes_input(raw_input: str) -> tuple[list[str], bool]:
    """
    Parse comma-separated note selections.

    Returns selected keys and whether a custom note was requested.
    """
    if not raw_input.strip():
        return [], False

    keys = [part.strip() for part in raw_input.split(",") if part.strip()]

    if not keys or keys == [NOTES_SKIP_KEY]:
        return [], False

    if NOTES_SKIP_KEY in keys and len(keys) > 1:
        keys = [key for key in keys if key != NOTES_SKIP_KEY]

    valid_keys = set(NOTES_PREDEFINED) | {NOTES_CUSTOM_KEY, NOTES_SKIP_KEY}
    invalid = [key for key in keys if key not in valid_keys]
    if invalid:
        raise ValueError(
            f"Invalid choice(s): {', '.join(invalid)}. "
            f"Use: {', '.join(sorted(valid_keys - {NOTES_SKIP_KEY}))}, or {NOTES_SKIP_KEY}."
        )

    wants_custom = NOTES_CUSTOM_KEY in keys
    selected = [key for key in keys if key in NOTES_PREDEFINED]
    return selected, wants_custom


def prompt_notes(allow_back: bool = False) -> str:
    """Collect one or more quick-note tags and an optional custom note."""
    while True:
        print("Notes:")
        for key in sorted(NOTES_PREDEFINED, key=lambda value: int(value)):
            print(f"  {key} {NOTES_PREDEFINED[key]}")
        print(f"  {NOTES_CUSTOM_KEY} Custom Note")
        print(f"  {NOTES_SKIP_KEY} No Notes")
        print()
        print("  Enter one or more numbers, separated by commas (e.g. 1,3,5).")
        print("  Type 'help' for guidance.")
        if allow_back:
            print("  Type 'back' to reopen the previous repository.")
        print()

        raw = input("Choice: ").strip().lower()
        if raw == "help":
            print_notes_guide()
            continue
        if allow_back and raw == "back":
            return REVIEW_BACK

        try:
            selected_keys, wants_custom = parse_notes_input(raw)
        except ValueError as exc:
            print(exc)
            continue

        custom_note = ""
        if wants_custom:
            custom_note = input("Enter custom note: ").strip()

        return format_notes(selected_keys, custom_note)


def collect_review_inputs(allow_back: bool) -> dict[str, str] | str:
    """Collect category, priority, and notes for a repository."""
    category = prompt_category(allow_back=allow_back)
    if category == REVIEW_BACK:
        return REVIEW_BACK

    priority = prompt_priority(allow_back=allow_back)
    if priority == REVIEW_BACK:
        return REVIEW_BACK

    notes = prompt_notes(allow_back=allow_back)
    if notes == REVIEW_BACK:
        return REVIEW_BACK

    return {
        "category": category,
        "priority": priority,
        "notes": notes,
    }


def collect_selective_review(current: dict[str, str]) -> dict[str, str]:
    """Edit only the fields the user chooses to change."""
    updated = dict(current)

    if prompt_yes_no("Edit Category? (Y/N)"):
        category = prompt_category()
        updated["category"] = category

    if prompt_yes_no("Edit Priority? (Y/N)"):
        priority = prompt_priority()
        updated["priority"] = priority

    if prompt_yes_no("Edit Notes? (Y/N)"):
        notes = prompt_notes()
        updated["notes"] = notes

    return updated


def show_initial_guides() -> None:
    """Show category and priority guides before the first repository."""
    print_category_guide()
    print_priority_guide()


# ---------------------------------------------------------------------------
# Repository lookup
# ---------------------------------------------------------------------------


def find_repositories(query: str, repos: list[dict[str, str]]) -> list[dict[str, str]]:
    """Return repositories whose names partially match the query."""
    needle = query.lower()
    return [repo for repo in repos if needle in repo["name"].lower()]


def select_repository_interactive(repos: list[dict[str, str]]) -> dict[str, str] | None:
    """Prompt for a repository name and return the selected repository."""
    while True:
        print()
        print("Repository name:")
        query = input("> ").strip()
        if not query:
            print("Enter a repository name.")
            continue

        matches = find_repositories(query, repos)
        if not matches:
            print("No matches found. Try again.")
            continue

        if len(matches) == 1:
            return matches[0]

        print()
        print("Matches:")
        print()
        for index, repo in enumerate(matches, start=1):
            print(f"{index} {repo['name']}")
        print()

        while True:
            choice = input("> ").strip()
            if choice.isdigit():
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(matches):
                    return matches[selected_index]
            print(f"Invalid selection. Enter a number from 1 to {len(matches)}.")


def repo_index_by_name(repos: list[dict[str, str]], name: str) -> int:
    """Find the list index for a repository name (display/navigation only)."""
    return find_repo_index(repos, name)


# ---------------------------------------------------------------------------
# Review session
# ---------------------------------------------------------------------------


def run_edit(inventory_path: Path, progress_path: Path) -> int:
    """Edit a previously reviewed repository."""
    if not inventory_path.exists():
        print(f"Inventory not found: {inventory_path}", file=sys.stderr)
        return 1

    preamble, repos = parse_inventory(inventory_path)
    repo_names = [repo["name"] for repo in repos]
    try:
        progress = load_progress(progress_path, repo_names, migrate=True)
    except ProgressFormatError as exc:
        print(f"Progress file error: {exc}", file=sys.stderr)
        return 1

    reviews = get_reviews(progress)

    print()
    print_rule()
    print("Edit Repository Review")
    print_rule()

    repo = select_repository_interactive(repos)
    if repo is None:
        return 1

    current = get_review_for_repo(repo, reviews)
    display_current_review(repo["name"], current)
    updated = collect_selective_review(current)

    save_review(
        repo,
        updated,
        progress,
        progress_path,
        repos,
        preamble,
        inventory_path,
    )

    print()
    print("✔ Saved")
    print()
    print(f"Updated review for {repo['name']}.")
    print()
    return 0


def run_review(
    inventory_path: Path,
    progress_path: Path,
    reset: bool,
    sort_mode: str = SORT_CREATED,
) -> int:
    if not inventory_path.exists():
        print(f"Inventory not found: {inventory_path}", file=sys.stderr)
        return 1

    preamble, repos = parse_inventory(inventory_path)
    repo_names = [repo["name"] for repo in repos]
    review_repos = sort_repositories(repos, sort_mode)

    if reset:
        progress = empty_progress()
    else:
        try:
            progress = load_progress(progress_path, repo_names, migrate=True)
        except ProgressFormatError as exc:
            print(f"Progress file error: {exc}", file=sys.stderr)
            return 1

    if progress.get("completed") and not reset:
        print("Review already completed.")
        print(f"Inventory updated at: {display_path(inventory_path)}")
        print("Use --reset to start over, or --edit to change a repository.")
        return 0

    reviews = get_reviews(progress)
    total = len(repos)
    done = count_reviewed(repos, reviews)
    pending = get_unreviewed_repos(review_repos, reviews)

    # All repositories reviewed but inventory not yet written (e.g. interrupted).
    if not pending:
        finalize_inventory(inventory_path, progress_path, preamble, repos, progress)
        print_completion_screen(inventory_path)
        return 0

    print_startup_banner(inventory_path, progress_path, done, total)

    guides_shown = False
    review_history: list[str] = []
    repo_index = find_next_unreviewed_index(review_repos, reviews)

    try:
        while repo_index < len(review_repos):
            repo = review_repos[repo_index]
            name = repo["name"]

            if is_reviewed(name, reviews):
                repo_index = find_next_unreviewed_index(review_repos, reviews, repo_index + 1)
                continue

            if not guides_shown:
                show_initial_guides()
                guides_shown = True

            display_repo(repo, repo_index + 1, total)

            allow_back = bool(review_history)
            result = collect_review_inputs(allow_back=allow_back)
            if result == REVIEW_BACK:
                if not review_history:
                    print("No previous repository to go back to.")
                    continue

                previous_name = review_history.pop()
                del reviews[previous_name]
                done -= 1
                save_progress(progress_path, progress)
                repo_index = repo_index_by_name(review_repos, previous_name)
                print()
                print(f"Reopened {previous_name} for review.")
                continue

            set_review(progress, name, result)
            apply_review(repo, result)
            save_progress(progress_path, progress)
            review_history.append(name)
            done += 1
            print_progress_saved(done, total)
            repo_index = find_next_unreviewed_index(review_repos, reviews, repo_index + 1)
    except KeyboardInterrupt:
        print()
        print("Stopped. Progress saved.")
        print(f"Resume with: python scripts/{Path(__file__).name}")
        return 0

    finalize_inventory(inventory_path, progress_path, preamble, repos, progress)
    print_completion_screen(inventory_path)
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="GitHub Recovery repository review tool.",
        add_help=True,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Run 'python scripts/review_repositories.py help' for the full guide, "
            "including category and priority meanings."
        ),
    )
    parser.add_argument(
        "command",
        nargs="?",
        default=None,
        help="Optional command: help, status, or edit.",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=DEFAULT_INVENTORY,
        help="Path to repository inventory markdown file",
    )
    parser.add_argument(
        "--progress",
        type=Path,
        default=DEFAULT_PROGRESS,
        help="Path to review progress JSON file",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear saved progress and start from the beginning",
    )
    parser.add_argument(
        "--edit",
        action="store_true",
        help="Edit a previously reviewed repository",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current review progress",
    )
    parser.add_argument(
        "--sort",
        choices=SORT_CHOICES,
        default=SORT_CREATED,
        help="Review order: created (oldest first, default) or alphabetical",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "help":
        print_help()
        return 0

    if args.command == "status" or args.status:
        return print_status(args.inventory, args.progress)

    if args.command == "edit" or args.edit:
        return run_edit(args.inventory, args.progress)

    if args.command is not None:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        print("Run 'python scripts/review_repositories.py help' for usage.", file=sys.stderr)
        return 1

    return run_review(args.inventory, args.progress, args.reset, args.sort)


if __name__ == "__main__":
    raise SystemExit(main())
