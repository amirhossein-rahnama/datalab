---
name: mlops
description: Use for productionizing a model — Docker, CI, DVC, MLflow tracking/registry, FastAPI serving, and Evidently drift monitoring.
---

# MLOps

> **Bundled scripts live in the plugin, not the user's project.** Invoke datalab's
> Python scripts with the plugin path, e.g. `python "$CLAUDE_PLUGIN_ROOT/scripts/<name>.py"`.
> If `$CLAUDE_PLUGIN_ROOT` is unset, find the datalab plugin folder (the one containing
> `.claude-plugin/plugin.json`). The working directory is the user's own project. If a bundled script errors because a package
> is missing, run `python "$CLAUDE_PLUGIN_ROOT/scripts/setup.py"` once to install core deps.

Wires up the production pieces the `+mlops` tier scaffolded: containerization, CI, data/
pipeline versioning, experiment tracking + registry, serving, and drift monitoring. Runs
after `modeling`/`experiment` produced a model worth deploying; requires the `+mlops` tier.

## Step 0 — Confirm tier, then freshness

Check `.datalab/state.json.tier` includes `"mlops"`. If not, delegate back to `scaffold` to
render the tier first — don't hand-create `Dockerfile`/`serve/app.py` etc. ad hoc.

Before writing FastAPI/MLflow/Evidently/DVC code: Context7 `resolve-library-id` +
`query-docs` for whichever of these you're about to touch — all four move fast enough that
memorized patterns risk being stale.

## Step 1 — Reproducibility backbone (DVC + provenance)

Wire `dvc.yaml` stages to mirror `pipeline.py`'s steps (data → preprocess → train → eval), so
`dvc repro` reproduces a result the same way `pipeline.py` does. Pattern and how this ties to
seeds/`config.yaml`/`scripts/provenance.py`: `references/repro.md`.

## Step 2 — Tracking + registry (MLflow)

Wire experiment logging (params, metrics, artifacts, seed) into `modeling`/`experiment`'s
training runs, and register the winning model in the MLflow model registry. If `modeling` was
already logging to `experiments/` flat files, MLflow becomes the durable backend going
forward — don't drop the existing records, migrate/mirror them. Details: `references/repro.md`.

## Step 3 — Serving (FastAPI)

Fill `serve/app.py`: load the registered/best model once at startup, expose `/predict`
(request schema matching the feature contract from `schema.py`) and `/health`. Pattern,
schema design, versioning: `references/serving.md`.

## Step 4 — CI

Fill `.github/workflows/ci.yml`: lint (ruff) + test (`pytest -q` / `tasks.py test`) on every
push/PR at minimum; optionally build the Docker image as a further stage. Pattern:
`references/ci.md`.

## Step 5 — Containerization

Fill `Dockerfile`/`.dockerignore` so the serving app builds into a runnable image. Base it on
the project's actual `requirements.txt`/`pyproject.toml` (don't hand-pin different versions).
Docker build is best-effort to verify (no daemon guaranteed in this environment) — if you
can't build, say so explicitly rather than claiming it was verified.

## Step 6 — Drift monitoring (Evidently)

Fill `monitoring/`: a reference dataset (the training data, or a held-out slice) vs. current/
incoming data drift report. Pattern, scheduling notes, and what to do when drift is flagged:
`references/monitoring.md`.

## Step 7 — Hand off to verify

Gate A (smoke): the FastAPI app imports and starts, CI YAML is syntactically valid, DVC
pipeline YAML is valid. Fix and re-verify (bounded retries, ~3) before setting
`phases.mlops = "done"`.

## Boundaries

- Don't retrain or change the model here — `mlops` wires infrastructure around whatever
  `modeling`/`experiment` already produced.
- Don't skip Step 0's tier check "because the files are easy to write anyway" — an
  ungoverned `+mlops` addition breaks the non-clobbering contract `scaffold` relies on.
- Load-testing serving and cloud-specific deploy targets are explicitly out of scope (v1) —
  don't improvise them.
