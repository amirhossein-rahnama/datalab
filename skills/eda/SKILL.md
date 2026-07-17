---
name: eda
description: Use for exploratory data analysis — load, profile, clean, and visualize a dataset; fills the EDA notebook and produces a data dictionary.
---

# EDA

Fills `notebooks/01_eda.ipynb` with a real analysis of the project's dataset(s) and produces
a data dictionary. Runs after `scaffold` (often auto-offered right after it) or on demand via
`/datalab:work` when `phases.eda` is `pending`.

## Step 1 — Locate and profile the data

Find the dataset under `data/raw/` (or wherever the interview pointed). Run:
```
python scripts/profile_data.py --input data/raw/<file>
```
Use its output (shape, per-column dtype/missingness/cardinality, target guess, task-type
guess) as the backbone of the notebook — don't re-derive these by hand in pandas when the
script already computed them; do use pandas *in the notebook* to show the work, not just
paste the JSON.

## Step 2 — Fill the notebook, not a script

Edit `notebooks/01_eda.ipynb` directly (it's JSON — add cells with `nbformat`-compatible
structure, or via the notebook editing tool if available). Follow `references/checklist.md`
section order: load → shape/dtypes → missingness → duplicates → target/class balance →
univariate distributions → bivariate/correlation → outliers → (task-specific: datetime
parsing for time-series, text stats for NLP, image sanity checks for CV) → leakage screen →
findings summary (markdown cell, plain language).

Every code cell must actually run against the real data — no placeholder `# TODO` cells left
behind; that's what `verify`'s notebook-execution check will catch anyway.

## Step 3 — Visualize

Use `scripts/plots.py` for standardized figures (distribution plots, correlation heatmap,
class-balance bar, missingness matrix) saved to `reports/figures/`. Consult the `dataviz`
skill for palette/layout guidance if you're building any ad-hoc chart in the notebook that
`plots.py` doesn't cover.

## Step 4 — Data dictionary

Write `reports/data_dictionary.md`: one row per column — name, dtype, non-null %, unique
count, short description (inferred from name/values; flag if genuinely ambiguous), and role
(`feature` / `target` / `id` / `drop-candidate`). Flag any column that looks like a leakage
risk (near-perfect correlation with target, a column that couldn't exist at prediction time,
an ID-like column) so `modeling` doesn't rediscover it the hard way.

## Step 5 — Findings summary

Close the notebook with a markdown cell: dataset shape, target/task-type confirmation or
correction, class balance verdict, top data-quality issues (missingness, duplicates,
outliers), and a recommendation for `modeling` (e.g., "imbalanced 1:12 — don't use accuracy").

## Step 6 — Hand off to verify, then update state

`verify` (smoke gate): notebook executes end-to-end with `nbclient`, no errors. Only then set
`phases.eda = "done"` in `.datalab/state.json` and report back.

## Boundaries

- No modeling here — a Dummy baseline or quick correlation check is fine as a data-quality
  signal, but training real models is `modeling`'s job.
- Don't silently fix bad data (drop rows/impute) inside the EDA notebook as if it were
  final — note the issue and the recommended treatment; the actual cleaning step belongs in
  the leakage-safe pipeline (`modeling`), so it's applied inside CV folds, not globally here.
