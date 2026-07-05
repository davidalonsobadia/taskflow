# Backlog

Features listed here are picked up automatically by the Planner agent.

**How to trigger planning:**
- **Single push**: add a new `##` section below and push to `main` — the Planner
  reads the diff, creates ordered GitHub issues for each new entry, and stops.
  It will not re-process entries that already have a matching issue.
- **Manual full-pass**: run the `Agent - Plan` workflow manually via the Actions UI
  and point it at this file to process all entries (with deduplication).
- **Ad-hoc idea**: open a GitHub issue with your idea, add the `plan` label — the
  Planner reads that issue and creates sub-issues from it.

After the Planner runs, review the created issues and add the `auto` label to each
one (in dependency order) to hand it off to the Implementer.

---

<!-- Add new features below. Use a ## heading per feature and describe the goal,
     the target user, and what "done" looks like. Be as specific or as vague as you
     like — the Planner will ask clarifying questions before creating issues if the
     idea is too ambiguous to decompose safely. If a feature has a design mockup,
     commit it under `design/refs/<slug>/` (see `design/refs/README.md`) and mention
     that path in the entry — the Planner will read it and link it into the task
     issue(s) it creates. -->
