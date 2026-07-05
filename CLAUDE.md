# CLAUDE.md

Guidance for Claude Code (and any AI agent) working in this repository.

## 0. Language policy (non-negotiable)

**Everything produced in this repository is written in English** — code, identifiers,
comments, docstrings, commit messages, PR titles and descriptions, issue replies,
documentation and log messages. This holds **even when the human writes to you in
Spanish or any other language**: understand the request in their language, but
produce all artifacts in English. The only exception is direct quotes of a user's
words when strictly necessary.

## 1. Project overview

TaskFlow is a monorepo with three parts:

- **`backend/`** — FastAPI (Python 3.12) REST API. SQLAlchemy ORM, Pydantic v2,
  Alembic migrations, JWT auth, API-key gateway, Celery + Redis for async tasks.
- **`frontend/`** — Next.js 16 (App Router, React 19, TypeScript 5, Tailwind 4,
  shadcn/ui + Radix). Package manager is **pnpm**.
- **PostgreSQL 15** is the database; **Redis 7** is the Celery broker. The full
  stack runs via [`docker-compose.yml`](docker-compose.yml).

Production deployment is intentionally out of scope for now.

## 2. Commands

Run backend commands from `backend/`, frontend commands from `frontend/`.

### Backend (Python 3.12, pip)
```bash
pip install -r requirements.txt          # install dependencies
ruff check .                             # lint (config: backend/ruff.toml)
ruff check . --fix                       # auto-fix lint issues
TESTING=1 DATABASE_URL=sqlite:///./test.db SECRET_KEY=test-secret python run_tests.py
                                         # run the test suite (SQLite, no external services)
alembic upgrade head                     # apply DB migrations (needs DATABASE_URL)
alembic revision --autogenerate -m "..." # generate a migration after model changes
```

### Frontend (pnpm)
```bash
pnpm install --frozen-lockfile           # install dependencies
pnpm lint                                # eslint (config: frontend/eslint.config.mjs)
pnpm build                               # next build (standalone output)
pnpm dev                                 # local dev server
```

> If you add or change a dependency, update the lockfile in the same change:
> `pnpm install` for the frontend; `requirements.txt` for the backend.

## 3. Testing conventions

- Tests live under `backend/tests/` (pytest). They are written **alongside the
  feature they cover** — when you implement or change behavior, add or update its
  tests in the same PR.
- Tests run against **SQLite**, not Postgres: the runner sets
  `DATABASE_URL=sqlite:///./test.db` and `TESTING=1`. `TESTING=1` disables the
  API-key middleware and Sentry, so tests can hit endpoints directly.
- pytest markers available (see `backend/pyproject.toml`): `unit`, `integration`,
  `slow`, `auth`.
- The frontend has no test framework yet; add one (and its CI step) only when a
  task explicitly calls for frontend tests.

## 4. Backend conventions (follow the existing patterns)

Code is organized by **domain** under `app/domains/<domain>/`, each with up to four
files. Mirror this layout for any new domain:

```
app/domains/<domain>/
├── models.py     # SQLAlchemy models (Base from app.db.base)
├── schemas.py    # Pydantic v2 request/response models
├── service.py    # business logic as a <Domain>Service class
└── router.py     # FastAPI APIRouter wiring HTTP to the service
```

- **Routers**: `router = APIRouter(prefix="/<domain>", tags=["<domain>"])`. Inject
  `db: Session = Depends(get_db)` and the current user via
  `current_user: User = Depends(get_verified_user)`. Set `response_model=` and add a
  docstring per endpoint. Keep routers thin — delegate to the service.
- **Services**: a class `class <Domain>Service:` with `__init__(self, db: Session)`.
  Methods raise `fastapi.HTTPException(status_code=..., detail="...")` on errors and
  **enforce ownership** (e.g. verify the resource belongs to `user_id`) before acting.
- **Schemas**: Pydantic v2. Use `Model.model_validate(orm_obj)` to serialize and
  `data.model_dump(exclude_unset=True)` for partial updates. Response models read
  from ORM objects via `from_attributes = True` (or `ConfigDict(from_attributes=True)`).
- **Database**: get sessions through `app.db.session.get_db`; models inherit
  `app.db.base.Base`. Never write raw SQL for schema changes — use Alembic. After
  changing a model, run `alembic revision --autogenerate` and review the migration.
- **Config**: all settings come from `app.core.config.settings` (pydantic-settings,
  reads `.env`). Add new config as typed fields with safe defaults; never hardcode
  secrets.
- **Auth & API key**: every `/api/...` route requires the `x-api-key` header (SHA-256
  hashed, checked in `app/core/middleware/api_key.py`); exempt paths are listed there
  (e.g. `/api/v1/health`, `/docs`). The middleware is skipped when `TESTING=1`.
- **Logging**: use `from app import logger` (`logger.info(...)`), not bare `print`.

## 5. Frontend conventions (follow the existing patterns)

```
frontend/
├── app/<route>/page.tsx   # App Router pages and route handlers
├── features/<domain>/     # feature modules: api.ts + *-dialog.tsx, *-item.tsx, etc.
├── components/            # shared UI (shadcn/ui + Radix); components/ui/* is generated
├── lib/                  # api-client.ts, auth.ts, config.ts, types.ts, utils.ts
└── hooks/                # shared React hooks
```

- **Two API layers — do not mix them:**
  - `lib/api-client.ts` exports `apiFetch`, a **server-only** wrapper that talks to
    the FastAPI backend and injects the `x-api-key` header. Use it in route handlers
    and server components only (it throws if run on the client).
  - `features/<domain>/api.ts` are **client-side** helpers that call the Next.js
    route handlers under `/api/...` (never the backend directly).
- Use the `@/*` path alias for imports (maps to the frontend root).
- UI uses shadcn/ui + Radix and Tailwind 4. Reuse `components/ui/*`; do not hand-roll
  primitives that already exist.
- Note: `next.config.mjs` sets `typescript.ignoreBuildErrors: true`, so `pnpm build`
  will **not** fail on type errors. Do not rely on the build to catch them — keep
  types correct and run `pnpm lint`.

## 6. Design references for UI issues

When a task should match a specific visual design (a mockup, screenshot, PDF spec,
or HTML prototype), commit the file(s) into the repo under `design/refs/<key>/`
rather than only linking an external URL or GitHub's issue-attachment CDN link —
none of the pipeline agents have web access (`WebFetch`/`WebSearch` are
intentionally disallowed for Planner, Implementer, and Reviewer), but
`actions/checkout@v4` already gives every agent run the full repo, so a committed
file is directly readable via the `Read` tool (which natively opens PNG/JPG and
PDF, and reads `.html` as markup/CSS source).

- Allowed types: `.png`, `.jpg`/`.jpeg`, `.pdf`, `.html`.
- Link the exact path(s) under a `## Design references` section in the issue
  body — this is the **authoritative** pointer agents follow; `design/refs/<issue-
  number>/` is only the default drop location for the common case. See
  `design/refs/README.md` for the full convention, epic/shared-reference handling,
  and an example.
- The Implementer treats a linked reference as the source of truth for visual
  detail (layout, spacing, colors, copy, visible states) over its own
  interpretation — see `.claude/agents/implementer.md`.
- No auto-download of issue attachments, no headless-browser rendering, no Git
  LFS — deliberately out of scope. Pre-rendering HTML mockups to PNG for pixel
  fidelity is a possible future enhancement, not built now.

## 7. Git & PR conventions (for autonomous agents)

- One issue → one branch (`claude/issue-<n>`) → one Pull Request. Keep changes
  **scoped to the issue**; do not bundle unrelated refactors.
- The PR description must include `Closes #<n>` so merging closes the issue.
- Commit messages and PR text in English, imperative mood (e.g. "Add task priority
  filter"). Conventional-commit prefixes (`feat:`, `fix:`, `chore:`) are welcome.
- Before opening a PR, run the relevant checks locally on the runner: backend
  `ruff check .` + tests; frontend `pnpm lint` + `pnpm build`.
- `main` is protected: nothing merges unless CI passes.

## 8. Secrets

- The real `backend/.env` and `frontend/.env` are git-ignored and must never be
  committed. Use `.env.example` for documenting non-sensitive defaults.
- In CI and agents, secrets come from **GitHub Secrets**, scoped to the job that
  needs them. Tests use throwaway, non-sensitive values (`SECRET_KEY=test-secret`,
  SQLite URL). Never print secret values to logs.
