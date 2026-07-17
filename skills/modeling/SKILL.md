---
name: modeling
description: Use when building or training ML models — leakage-safe scikit-learn pipelines (all preprocessing inside CV folds), baseline-first iteration, and Optuna hyperparameter tuning with experiment tracking.
---

# Modeling

Builds and trains models for the project's `task_type`. Runs after `eda` (needs the data
dictionary's leakage flags and class-balance verdict). Produces trained pipelines + tracked
experiments; hands off to `verify`'s model-quality gate before anything is reported done.

## Step 0 — Freshness: consult Context7 first

Before writing any scikit-learn or Optuna code: `resolve-library-id` for `scikit-learn`
(and `optuna` if tuning), then `query-docs` for the specific API you're about to use
(`Pipeline`, `ColumnTransformer`, `cross_validate`, `optuna.create_study`, etc.). Use the
current API shape from Context7, not memorized patterns — sklearn and Optuna both move.

## Step 1 — Baseline first, always

Before any real model: fit `sklearn.dummy.DummyClassifier`/`DummyRegressor` (or a trivial
persistence/seasonal-naive baseline for time-series) with the same CV protocol you'll use for
real models. This number is the floor — `verify` will block anything that doesn't clear it.
Log it as the first row of the experiment leaderboard (`experiments/`).

## Step 2 — Leakage-safe pipeline

**All preprocessing that fits on data (imputation, scaling, encoding, feature selection)
must live inside an `sklearn.Pipeline`/`ColumnTransformer`, fit only within each CV fold** —
never fit once on the full dataset and reused. This is non-negotiable; `verify` explicitly
checks for it. Full pattern and the common traps: `references/pipelines.md`.

## Step 3 — Pick a recipe for the task type

`references/task-recipes.md` has the model families, default metric, and CV strategy per
task type (classification/regression/clustering/time-series/NLP/computer-vision/
recommendation/production-pipeline/GenAI-RAG). Start with 2–3 model families from the
recipe, not one — the model-comparison leaderboard (`verify` gate B) expects more than a
single candidate.

## Step 4 — Iterate

Each iteration = one pipeline variant, evaluated with the task's CV strategy, logged with its
params, metrics (mean ± std across folds), seed, and a short note on what changed. Don't
overwrite previous runs — append, so the leaderboard is real.

## Step 5 — Tune (optional, after a working baseline pipeline beats Dummy)

Use Optuna to search the best-performing family's hyperparameters. Pattern, search-space
guidance, pruning, and seed control: `references/tuning.md`. Save the winning config to
`params.yaml`. Never tune before Steps 1–4 establish that the pipeline is leakage-safe and
beats baseline — tuning a leaky pipeline just overfits harder.

## Step 6 — Track and persist

Log every run under `experiments/` (params, metrics, seed, timestamp; if the `+mlops` tier is
present, also log to MLflow — see `skills/mlops/references/repro.md`). Persist the winning
pipeline (joblib) under `src/<pkg>/models/` or `models/`, including the full preprocessing —
loading it later must not require re-fitting anything on new data.

## Step 7 — Hand off to verify

Delegate to `verify`'s model-quality gate (over/underfitting, leakage, CV spread, imbalance,
metric appropriateness, baseline comparison, error analysis, leaderboard, explainability,
fairness). Fix what it flags and re-submit — bounded retries (~3) — before setting
`phases.modeling = "done"`.

## Boundaries

- Don't hand-roll cross-validation loops when `cross_validate`/`cross_val_score` with a
  `Pipeline` does it correctly — reduces the chance of leaking preprocessing across folds.
- Don't skip the Dummy baseline "because the task is obviously not trivial" — run it anyway,
  it's cheap and it's the gate's reference point.
- Full experiment execution (multi-seed academic runs, final plots, written conclusions) is
  `experiment`'s job, not modeling's — modeling produces the winning pipeline, `experiment`
  runs it end-to-end for the record.
