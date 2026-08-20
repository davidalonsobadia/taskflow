# Automated Agent Pipeline

This document describes the full automated pipeline that takes a GitHub issue from
creation to a merged PR — and then advances to the next issue — without human
intervention in the happy path.

---

## Overview

```
Human: merge PR #2 (one-time kick-off)
              │
              ▼
   ┌─────────────────────┐
   │   advance-queue     │  fires on every claude/issue-* merge
   │   (agent-advance-   │  finds next open issue → adds `auto` label
   │    queue.yml)       │
   └──────────┬──────────┘
              │ `auto` label added to issue #N
              ▼
   ┌─────────────────────┐
   │    Implementer      │  reads issue + all comments (incl. failure context)
   │  (agent-implement   │  writes code + tests, runs checks on runner
   │   .yml / Opus)      │  opens PR → arms auto-merge
   └──────────┬──────────┘
              │ PR opened on branch claude/issue-N
              ▼
   ┌──────────────────────────────────────┐
   │  CI                  Agent - Review  │  run in parallel
   │  (ci.yml)            (agent-review   │
   │  ruff, alembic,      .yml / Sonnet)  │
   │  pytest, eslint,     PASS or BLOCK   │
   │  next build          verdict         │
   └──────────────────────────────────────┘
              │
        ┌─────┴──────┐
        │            │
      PASS         FAIL ──────────────────────────────┐
        │                                              │
        ▼                                              │
   ┌─────────────────────┐                             │
   │     Agent - QA      │  boots Postgres+Redis+API   │
   │  (agent-qa.yml /     │  (+frontend if touched),    │
   │   Sonnet)            │  runs the Tester agent      │
   │  PASS or BLOCK       │  end-to-end against the     │
   │  verdict             │  issue's acceptance criteria│
   └──────────┬───────────┘                             │
        ┌─────┴──────┐                                  │
        │            │                                  │
      PASS         FAIL ─────────────────────────────┐  │
        │                                             │  │
        ▼                                             ▼  ▼
   auto-merge                                   auto-retry
   (squash)                                     (agent-auto-
        │                                        retry.yml)
        │                                             │
        │                                      ┌──────┴───────┐
        │                                      │              │
        │                                  retry < 3      retry = 3
        │                                      │              │
        │                                      │          needs-human
        │                                      │          label added
        │                                      │          → pipeline
        │                                      │            pauses
        │                                      ▼
        │                               close PR, delete branch,
        │                               post failure context on issue,
        │                               re-add `auto` → implementer re-runs
        │
        ▼
   advance-queue fires
   → next issue labeled `auto`
   → cycle repeats
```

Note: `Agent - QA` polls the `review` check-run on the same commit and skips its own
heavy steps (booting the stack) unless Review already concluded `success` — booting
Postgres/Redis/the API/the frontend costs several minutes, and there's nothing for QA
to add if Review is already going to block the merge on its own.

---

## Workflows

| File | Trigger | Role |
|---|---|---|
| `agent-implement.yml` | `auto` label added to issue | Implements the issue, opens PR, arms auto-merge |
| `ci.yml` | PR opened / updated | Lint, migrations, tests, frontend build |
| `agent-review.yml` | PR opened / updated | Read-only code review — emits PASS or BLOCK |
| `agent-qa.yml` | PR opened / updated (after Review passes) | Boots the real stack and exercises the feature end-to-end — emits PASS or BLOCK |
| `agent-auto-retry.yml` | CI, Review, or QA workflow fails | Closes PR, posts failure context, re-triggers implementer |
| `agent-advance-queue.yml` | `claude/issue-*` PR merged | Labels the next open issue `auto` |
| `notify-merge.yml` | Any PR merged | Slack notification |

---

## Issue labels

| Label | Meaning |
|---|---|
| `auto` | Issue is in the pipeline — implementer will run (or is running) |
| `retry-1` / `retry-2` / `retry-3` | How many auto-retry attempts have been made |
| `needs-human` | Max retries (3) exceeded — pipeline paused, human action required |
| `no-auto` | Issue is excluded from the automated queue |
| `no-qa` | Issue/PR is excluded from the QA (Tester) stage — Review still runs |
| `epic` | Tracking issue — excluded from the automated queue |

---

## Issue selection order

`agent-advance-queue.yml` picks issues in **ascending numeric order**, excluding:

- Issues already labeled `auto` (in progress)
- Issues labeled `needs-human`, `epic`, or `no-auto`
- Issues whose title starts with `Epic:` (catches epic tracking issues without a label)

---

## GitHub Setup (required before first run)

### 1. Repository secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | What it is | How to create |
|---|---|---|
| `PIPELINE_PAT` | Personal Access Token used to re-add the `auto` label so it fires the `issues:labeled` workflow trigger | See note below |
| `CLAUDE_CODE_OAUTH_TOKEN` | OAuth token that authenticates the Claude Code GitHub Action | Generate at [claude.ai/settings](https://claude.ai/settings) under **Claude Code → GitHub Actions** |
| `SLACK_WEBHOOK_URL` | Incoming webhook URL for merge/pipeline notifications | Create an Incoming Webhook app in your Slack workspace |

#### Why `PIPELINE_PAT` is required (not just `GITHUB_TOKEN`)

GitHub **silently suppresses** workflow triggers caused by the built-in `GITHUB_TOKEN`. When `advance-queue` or `auto-retry` add the `auto` label using `GITHUB_TOKEN`, the `issues:labeled` event is never dispatched — so `agent-implement.yml` never fires. A PAT belonging to a real user (or a dedicated machine user) bypasses this restriction and correctly triggers the downstream workflow.

**Required PAT scopes:**
- `repo` — full repository access (needed to add/remove labels and trigger events)

**Recommended:** create a dedicated GitHub machine account (e.g. `your-org-bot`), grant it write access to the repo, and generate the PAT from that account so pipeline actions are not tied to a personal account.

### 2. Repository settings

- **Settings → General → Pull Requests**: enable **Allow auto-merge**
- **Settings → Branches → main**: add a branch protection rule with required status checks:
  - `backend` (from `ci.yml`)
  - `frontend` (from `ci.yml`)
  - `review` (from `agent-review.yml`)
  - `qa` (from `agent-qa.yml`)

### 3. Issue labels

Create these labels in **Issues → Labels** (the workflows expect them to exist):

| Label | Suggested color |
|---|---|
| `auto` | `#0075ca` (blue) |
| `retry-1` | `#e4e669` (yellow) |
| `retry-2` | `#e4a232` (orange) |
| `retry-3` | `#d93f0b` (red) |
| `needs-human` | `#b60205` (dark red) |
| `no-auto` | `#cccccc` (grey) |
| `no-qa` | `#c5def5` (light blue) |
| `epic` | `#7057ff` (purple) |

---

## How to start the pipeline

1. Complete the GitHub Setup steps above.

2. Merge the current open PR to kick off the first advance-queue run.

3. Watch Slack — each issue will be announced as it triggers.

---

## Handling a `needs-human` escalation

When an issue hits 3 consecutive failures:

1. The issue gets a `needs-human` label and a comment with the full failure history.
2. The pipeline stops for that issue.

To resume:

1. Read the failure context comments on the issue.
2. Either fix the issue description (clarify requirements) or push a manual fix to the
   branch (if you want to salvage the partial work).
3. Remove the `needs-human` label.
4. Re-add the `auto` label — the implementer will run again (retry count resets because
   the auto-retry counter only increments on consecutive failures without a human touch).

---

## Excluding an issue from the queue

Add the `no-auto` label to any issue you want to skip in the automated run. You can
re-add `auto` manually whenever you want to process it.

---

## Excluding a PR from QA

Add the `no-qa` label to the issue (or its PR — they share the same label API) if the
change has nothing observable to run — a docs-only change, a config tweak, a pure
refactor with no behavior change. `Agent - QA`'s required check still reports (so it
doesn't hang the merge), it just skips booting the stack and running the Tester agent.
Review still runs regardless.

---

## Architecture notes

- **Concurrency**: `agent-auto-retry.yml` uses a concurrency group keyed on the branch
  name (`auto-retry-claude/issue-N`). If CI and the Reviewer both fail simultaneously,
  the second retry run is queued rather than racing. The second run finds no open PR
  (already closed by the first) and exits gracefully.
- **Failure context**: Retry comments are posted on the **issue** (not the PR) so the
  Implementer can read them on the next run via `gh issue view --comments`.
- **Branch lifecycle**: Each implementer run creates `claude/issue-N` from `main`.
  On failure, the retry workflow closes the PR and deletes the branch before re-triggering,
  so the implementer always starts from a clean branch off the latest `main`.
- **Auto-merge arm**: The implementer runs `gh pr merge --auto --squash --delete-branch`
  after opening the PR. This arms auto-merge but does not merge — CI, the Reviewer, and
  QA still have to pass. The branch is deleted by GitHub on merge.
- **Why `agent-qa.yml` polls instead of using `workflow_run`**: a workflow triggered by
  `workflow_run` executes against the default branch and does not automatically appear
  as a status check on the PR that triggered the upstream workflow — attaching it would
  need extra Checks-API plumbing. `agent-qa.yml` instead triggers directly on the same
  `pull_request` events as `agent-review.yml` (so it naturally attaches as the `qa`
  check) and polls the `review` check-run on the same commit via the Checks API to get
  the sequencing without that plumbing. `agent-auto-retry.yml` still uses `workflow_run`
  for its own trigger, which is fine there — that workflow only *reacts* to a completed
  run, it never needs to appear as a check itself.
