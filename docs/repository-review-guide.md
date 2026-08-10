# Repository Review Tool — User Guide

This guide explains how to use `scripts/review_repositories.py`, the interactive CLI tool for classifying and prioritizing every repository in your GitHub account as part of the **GitHub Recovery** project.

---

## What this tool does

The tool reads your repository list from `reports/repository-inventory.md` and walks you through each repository one at a time. For each repo you assign:

- **Category** — what should happen to it (Showcase, Keep, Archive, etc.)
- **Priority** — when you should improve it (P1, P2, P3)
- **Notes** — quick tags or custom comments

Your progress is saved after every repository. When you finish all 93 repositories, the tool automatically updates `reports/repository-inventory.md` with your decisions.

---

## Before you start

### Requirements

- **Python 3** installed on your computer
- The **GitHub-Recovery** project folder on your machine
- The inventory file: `reports/repository-inventory.md`

### Open a terminal in the project folder

From the `GitHub-Recovery` folder, run all commands below. On Windows PowerShell:

```powershell
cd D:\2026\08_August\Github-Recovery
```

---

## Quick start

Start or resume a review session:

```bash
python scripts/review_repositories.py
```

Check how far you've gotten:

```bash
python scripts/review_repositories.py --status
```

That's it for the basics. The sections below explain everything in detail.

---

## Commands reference

| Command | What it does |
|---------|--------------|
| `python scripts/review_repositories.py` | Start or resume reviewing repositories |
| `python scripts/review_repositories.py --status` | Show progress (e.g. 24 / 93 reviewed) |
| `python scripts/review_repositories.py --edit` | Edit a previously reviewed repository |
| `python scripts/review_repositories.py --reset` | Clear all progress and start over |
| `python scripts/review_repositories.py --sort created` | Review oldest repositories first **(default)** |
| `python scripts/review_repositories.py --sort alphabetical` | Review in A–Z order by name |
| `python scripts/review_repositories.py help` | Show built-in help in the terminal |
| `python scripts/review_repositories.py --help` | Show command-line options |

---

## The review workflow

### 1. Start the tool

```bash
python scripts/review_repositories.py
```

You'll see a startup banner with:

- Inventory file path
- Progress file path
- How many repositories you've already reviewed

### 2. Review each repository

For each repository the tool shows:

```
Repository 12 / 93
Name:        little-lemon
Created:
2023-04-19
Visibility:  Public
Fork:        No
...
```

Then it asks three questions:

1. **Category** — what should happen to this repo?
2. **Priority** — when should you improve it?
3. **Notes** — optional tags or comments

After each repository you'll see:

```
✔ Saved
Progress: 12 / 93 repositories reviewed
Remaining: 81
```

### 3. Stop anytime

Press **Ctrl+C** to quit. Your progress is already saved — just run the tool again later to continue.

### 4. Finish

When all repositories are reviewed, the tool updates `reports/repository-inventory.md` automatically and shows a completion screen.

---

## Category options

**Question:** *What is the final status of this repository?*

| # | Category | When to use it |
|---|----------|----------------|
| 1 | ⭐ Showcase | Portfolio-quality — you'd proudly show recruiters |
| 2 | ✅ Keep | Useful repo, keep public, no major work planned |
| 3 | 📦 Archive | Keep for history, archive on GitHub |
| 4 | 🔒 Private | Should not be public |
| 5 | 🗑 Delete | Safe to permanently remove |
| 6 | 🍴 Fork Cleanup | Review the fork — keep, archive, unfork, or delete |
| 0 | Skip | Leave blank for now |

Before each category prompt you'll see a reminder:

> *"If a recruiter opened this repository today, would it help me get an interview?"*

---

## Priority options

**Question:** *When should I spend time improving this repository?*

| # | Priority | Meaning | Examples |
|---|----------|---------|----------|
| 1 | P1 | Work on soon | FreshHireAI, company-atlas, GitHub-Recovery |
| 2 | P2 | Improve later | Portfolio, React-Basics, OOP-Learning |
| 3 | P3 | Low priority | Tutorials, Hacktoberfest repos, old experiments |
| 0 | Skip | Leave blank | — |

---

## Notes options

You can select **multiple notes** using comma-separated numbers.

| # | Note |
|---|------|
| 1 | Needs README |
| 2 | Organize Files/Folders |
| 3 | Add Screenshots |
| 4 | Rename Repository |
| 5 | Add Topics |
| 6 | Improve Documentation |
| 7 | Remove Unnecessary Files |
| 8 | Custom Note (type your own text) |
| 0 | No Notes |

**Examples:**

```
Choice: 1,3,5
```
→ Saves as: `Needs README; Add Screenshots; Add Topics`

```
Choice: 1,8
Enter custom note: fix broken deploy link
```
→ Saves as: `Needs README; fix broken deploy link`

---

## Keyboard shortcuts during review

| Input | Action |
|-------|--------|
| `help` | Show the guide for the current prompt (category, priority, or notes) |
| `back` | Go back one repository to fix a mistake (only one step back) |
| `Ctrl+C` | Stop safely — progress is already saved |

---

## Review order

By default, repositories are reviewed **oldest first** (by creation date). This helps you follow your learning timeline.

```bash
# Oldest first (default)
python scripts/review_repositories.py

# Alphabetical A–Z
python scripts/review_repositories.py --sort alphabetical
```

**Important:** Changing the sort order does **not** affect your saved progress. Progress is stored by **repository name**, not by position in the list.

---

## Checking progress

```bash
python scripts/review_repositories.py --status
```

Example output:

```
Reviewed:
24 / 93

Remaining:
69

Current inventory:
reports/repository-inventory.md

Progress file:
reports/.review-progress.json
```

---

## Editing a previous review

Made a mistake on a repository you already reviewed? Use edit mode:

```bash
python scripts/review_repositories.py --edit
```

1. Type part of the repository name (case-insensitive)
2. If multiple matches appear, pick the correct one from the numbered list
3. See the current category, priority, and notes
4. Choose which fields to update (Y/N for each)
5. Changes are saved immediately

**Example:**

```
Repository name:
> portfolio

Matches:

1 Portfolio
2 Portfolio-Updated

> 1
```

---

## Files the tool uses

| File | Purpose |
|------|---------|
| `reports/repository-inventory.md` | Master list of all repositories (input and final output) |
| `reports/.review-progress.json` | Your saved progress between sessions |

### Progress file format

Progress is stored **by repository name**, not by list position:

```json
{
  "version": 2,
  "reviews": {
    "Website-pep": {
      "category": "📦 Archive",
      "priority": "P3",
      "notes": "Old HTML learning project"
    },
    "FreshHireAI": {
      "category": "⭐ Showcase",
      "priority": "P1",
      "notes": "Needs README; Add Topics"
    }
  },
  "completed": false
}
```

You normally do not need to edit this file by hand — the tool manages it.

---

## Common scenarios

### "I reviewed 20 repos yesterday and want to continue"

```bash
python scripts/review_repositories.py
```

The tool picks up where you left off automatically.

---

### "I chose the wrong category for the last repo"

While reviewing the **next** repository, type `back` at any prompt. You'll return to the previous repository and can re-enter your choices.

Or use edit mode later:

```bash
python scripts/review_repositories.py --edit
```

---

### "I want to start completely over"

```bash
python scripts/review_repositories.py --reset
```

This clears all saved progress. Your inventory file is not deleted, but category/priority/notes columns will only update again after you finish a new full review.

---

### "I finished all 93 repos — what's next?"

The tool updates `reports/repository-inventory.md` with all your categories, priorities, and notes. Suggested next steps:

1. **Repository Classification** — verify every repo has exactly one category
2. **Showcase Selection** — pick repos for your GitHub profile
3. **Portfolio Improvements** — polish your Showcase repositories

---

## Tips for efficient reviewing

1. **Use creation-date order** (default) to understand your learning journey chronologically.
2. **Don't overthink Skip (0)** — you can always edit later with `--edit`.
3. **Use notes liberally** — quick tags like `1,5` (Needs README + Add Topics) save time later.
4. **Check status regularly** — `--status` takes two seconds and keeps you oriented.
5. **Review in short sessions** — 10–15 repos at a time is easier than all 93 at once.
6. **Type `help` anytime** — contextual guides appear without leaving the session.

---

## Troubleshooting

### `python` is not recognized

Try:

```bash
py scripts/review_repositories.py
```

Or install Python from [python.org](https://www.python.org/downloads/) and ensure "Add to PATH" is checked during installation.

### Inventory not found

Run the command from the **GitHub-Recovery** project root, not from inside `scripts/`.

### Progress file error

The tool can usually migrate older progress formats automatically. If you see an error, check that `reports/.review-progress.json` is valid JSON. As a last resort, rename it (to keep a backup) and use `--reset` to start fresh.

### Review already completed

You've finished all repositories. Use `--edit` to change individual repos, or `--reset` to start a full review again.

---

## Built-in help

For a quick reference inside the terminal:

```bash
python scripts/review_repositories.py help
```

---

## Related project files

- `reports/repository-inventory.md` — the inventory report
- `docs/roadmap.md` — GitHub Recovery phases
- `prompts/create-issue.md` — how issues are structured in this project
