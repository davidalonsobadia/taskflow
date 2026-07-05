# Design references

Design mockups (JPG/PNG screenshots, PDFs, HTML prototypes) that ground a specific
GitHub issue's UI work. Committed here — not linked externally — so every pipeline
agent (Planner, Implementer, Reviewer) can `Read` them directly from the checkout;
none of them have web access (`WebFetch`/`WebSearch` are intentionally disallowed
for all three — see `CLAUDE.md`).

## Convention

```
design/refs/<key>/<descriptive-name>.<ext>
```

- `<key>` — normally the GitHub issue number (task or epic issue — no special case
  needed, epics are just issues). For a reference that doesn't belong to one
  specific issue yet (a backlog entry, or one shared by sibling tasks with no
  common epic), use a short descriptive slug instead, e.g.
  `design/refs/checkout-flow/`.
- Allowed types: `.png`, `.jpg`/`.jpeg`, `.pdf`, `.html`.
- **The `## Design references` link in the issue body is authoritative** — the
  `<key>` folder is just the default place a human drops files for the common case
  where the mockup lives under the same issue that will be implemented. Whenever
  the Planner creates new task issues from an idea/epic that already has a
  reference, it links the real path explicitly rather than relying on the new
  issue number matching.
- Shared across issues (e.g. one epic, several child tasks): store the file once
  under the epic's or slug's folder and link that same path from every consuming
  issue — never duplicate the binary.

## Example

```
design/refs/
└── 42/
    ├── dashboard-mockup.png       # full-page screenshot from Figma
    ├── empty-state.jpg
    └── spec.pdf                   # multi-page spec (Read supports page ranges)
```

Issue #42's body would include:

```
## Design references
- design/refs/42/dashboard-mockup.png
- design/refs/42/empty-state.jpg
- design/refs/42/spec.pdf
```

## HTML mockups

Read as markup/CSS source, not rendered to pixels — a structural/style reference,
not a pixel-perfect image. (Pre-rendering HTML mockups to PNG in CI is a possible
future enhancement, not built today.)

## Deliberately out of scope

No auto-download of GitHub issue attachments, no headless-browser rendering, no Git
LFS, no new tool permissions (`WebFetch`/`WebSearch` stay disallowed for all three
agents). See `CLAUDE.md` §6.
