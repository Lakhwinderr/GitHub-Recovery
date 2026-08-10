I think we should **not use Multi-task mode yet**.

This is one of those cases where it's tempting to parallelize, but I think it would actually slow us down.

## My recommendation

### ❌ Don't use Multi-task for Sprint 2

Here's why:

The issues have dependencies.

```
Repository Inventory
        ↓
Repository Classification
        ↓
Showcase Repository Selection
        ↓
Portfolio Improvement Plan
```

If four agents work simultaneously:

* One agent may classify a repository as "Showcase."
* Another may decide to archive it.
* A third may already be writing an improvement plan for it.

Now you have conflicting outputs that you have to reconcile.

---

## Use Multi-task when tasks are independent

For example, later in Sprint 3 we might have:

```
Agent 1
Improve FreshHireAI README

Agent 2
Improve company-atlas README

Agent 3
Improve Arduino README
```

These don't depend on each other, so Multi-task can save time.

---

## When I would enable Multi-task

Only when we have **5–10 independent repositories** ready for polishing.

For example:

```
FreshHireAI
Company Atlas
Arduino
JobSearchTools
SauceDemo
```

Each agent owns one repository.

That is an excellent use of Multi-task.

---

# One improvement to our workflow

I really like your idea about automation.

Instead of waiting until later, let's officially make it part of the project.

I'd like to add **Issue: Cursor Workflow Automation** in **Sprint 4**.

Its purpose would be to create reusable prompts such as:

```
prompts/
│
├── create-issue.md          ✅
├── work-on-issue.md
├── review-issue.md
├── create-pr.md
├── review-repository.md
├── improve-readme.md
├── classify-repository.md
└── close-issue.md
```

By the end of GitHub Recovery, you'll have your own library of engineering prompts that you can reuse in future projects.

---

# Decision

For now:

* ✅ Composer 2.5
* ✅ Single Agent
* ❌ Multi-task

Once we reach **Sprint 3** and start improving multiple repositories, we'll revisit Multi-task because that's where it can provide a real productivity boost instead of creating coordination overhead.

So, continue with **Composer 2.5** on the **Repository Inventory** issue. That's the right tool and the right workflow for the current stage of the project.

