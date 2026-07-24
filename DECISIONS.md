# Decisions

Append-only log of non-obvious choices. Newest entries at the bottom.

- **2026-07-24 — mypy strict mode enabled globally.** `strict = true` in
  `pyproject.toml` instead of per-flag config, so `make typecheck`, CI, and
  pre-commit all enforce the same check as `mypy --strict`. Documented
  per-module overrides (aiogram handlers, alembic versions) remain as escape
  hatches.
- **2026-07-24 — pre-commit mypy runs as a local hook, not mirrors-mypy.**
  Strict mode needs the real project dependencies (aiogram, sqlalchemy) to
  type decorators and query results; the isolated mirrors-mypy env lacks them
  and reports false "untyped decorator" errors. `uv run mypy app` via
  `language: system` matches CI exactly.
- **2026-07-24 — coverage gate raised 70% → 80%.** Actual full-suite coverage
  is ~89.8%; a round threshold below it catches regressions without flaking
  on minor refactors.
