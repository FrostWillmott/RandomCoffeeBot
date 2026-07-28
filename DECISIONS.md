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
- **2026-07-28 — coverage badge moved from a committed SVG to
  `py-cov-action/python-coverage-comment-action`.** The genbadge SVG had to be
  committed back to `master` on every run, which polluted history and needed a
  `paths-ignore` guard to avoid CI loops. The action keeps badge data on its
  own `python-coverage-comment-action-data` branch and adds a coverage diff
  comment on PRs. Rejected Codecov (extra external account), a Gist badge
  (needs a PAT secret), and a hand-rolled shields.io endpoint script (same
  result, more code to own) — this works with the default `GITHUB_TOKEN` and
  requires the repo to stay public. Needs `relative_files = true` in
  `.coveragerc`. Skipped the companion `workflow_run` workflow the docs
  suggest: it only buys comments on dependabot and fork PRs, where a coverage
  diff is noise, and the action exits 0 without it. The README reads the
  action's `endpoint.json` through shields.io rather than its `badge.svg`, so
  the badge matches the other four and is served by an actual image CDN.
  Known cost: the action appends a commit per master push to the data branch,
  each carrying a full `htmlcov/` (~1.7 MB, not disableable). Squash the
  branch with an orphan force-push if it ever gets heavy.
