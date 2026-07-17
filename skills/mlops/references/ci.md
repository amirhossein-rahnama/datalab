# CI pattern (GitHub Actions)

## `.github/workflows/ci.yml` skeleton

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install deps
        run: pip install -r requirements.txt -r scripts/requirements.txt
      - name: Lint
        run: ruff check .
      - name: Test
        run: pytest -q
      - name: Notebook smoke
        run: python tasks.py test
```

Adjust the notebook-execution step to whatever `tasks.py test` already wires up (per
`scaffold`'s base tier) rather than duplicating logic — CI should call the same commands a
human runs locally (`tasks.py lint`, `tasks.py test`), not a parallel, hand-written version.

## Rules

- **Lint failures**: keep as a real CI failure (unlike `verify`'s local Gate A, which treats
  lint as a warning) — CI is the last line of defense before merge, be stricter there.
- **Test + notebook execution are blocking** — this mirrors `verify`'s Gate A so nothing that
  would fail locally can pass CI.
- **Optional Docker build stage**: add only if the `+mlops` tier's `Dockerfile` exists and the
  team wants image-build-on-push; keep it a separate job so a slow Docker build doesn't block
  fast unit-test feedback.
- **Don't invent secrets/deploy steps** — CI here is build+test only; actual deployment is
  out of scope for this skill/tier (v1).
