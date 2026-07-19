---
name: experiment
description: Use to run a full experiment end-to-end and produce accurate results, plots, and conclusions (CV plus multi-seed mean±std for academic rigor).
---

# Experiment

> **Bundled scripts live in the plugin, not the user's project.** Invoke datalab's
> Python scripts with the plugin path, e.g. `python "$CLAUDE_PLUGIN_ROOT/scripts/<name>.py"`.
> If `$CLAUDE_PLUGIN_ROOT` is unset, find the datalab plugin folder (the one containing
> `.claude-plugin/plugin.json`). The working directory is the user's own project. If a bundled script errors because a package
> is missing, run `python "$CLAUDE_PLUGIN_ROOT/scripts/setup.py"` once to install core deps.

Runs the project's `pipeline.py` end-to-end for the record — this is what `/datalab:run`
calls. Produces the numbers, figures, and written conclusions that `document` will later turn
into a report/deck. Runs after `modeling` has a winning pipeline; re-runnable any time the
user wants a fresh full pass (e.g., after data changes).

## Step 1 — Execute the pipeline end-to-end

`pipeline.py` must run the full chain: load → validate (pandera `schema.py`) → preprocess
(the leakage-safe pipeline from `modeling`) → train (CV; **multi-seed with mean ± std if
`profile == academic`**) → evaluate → diagnostics → explain/fairness → figures → results.
Don't hand-run pieces of this in a notebook and call it done — `experiment`'s output must be
reproducible by re-running `pipeline.py` (or `python tasks.py run`) alone.

## Step 2 — Multi-seed protocol (academic) / single robust run (industrial)

Academic: re-run training across ≥5 seeds, aggregate every headline metric as
`mean ± std (n=<seeds>)`. Industrial: one CV run is acceptable unless the user asks for more;
frame results around the business KPI, not just the raw metric. Full protocol, significance
testing, and reporting format: `references/academic-rigor.md`.

## Step 3 — Diagnostics, explainability, fairness

`diagnostics.py` / `explain.py` are helper **libraries** — import and call them on your model:
```python
import os, sys
sys.path.insert(0, os.path.join(os.environ.get("CLAUDE_PLUGIN_ROOT", ""), "scripts"))
from diagnostics import classify_fit, cross_validate_summary, baseline_comparison  # over/underfit, CV, baseline
from explain import feature_importance, shap_summary, subgroup_performance          # importance/SHAP + fairness
```
These produce the artifacts `verify`'s model-quality gate will check and that `document`
will cite in the model card — generate them here as part of the run, don't wait for `verify`
to ask for them.

## Step 4 — Figures

```python
# same sys.path shim as Step 3; each function saves a PNG and returns its path
from plots import plot_confusion_matrix, plot_roc, plot_residuals, plot_learning_curve
```
Task-appropriate figure set (confusion matrix, ROC/PR, residuals, learning curves, feature
importance, SHAP summary, cluster/forecast plots — see `references/plots.md`), saved to
`reports/figures/`. Consult the `dataviz` skill for any figure `plots.py` doesn't standardize.

## Step 5 — Stats (academic emphasis, useful either way)

```python
# same sys.path shim as Step 3
from stats import confidence_interval, cohens_d, mean_std
```
Significance tests when comparing models (paired across CV folds/seeds — e.g., a paired
t-test or Wilcoxon signed-rank, not an unpaired test), confidence intervals on headline
metrics, effect sizes. Required for academic-profile claims like "model A beats model B";
recommended for industrial too before making a deployment recommendation.

## Step 6 — Write results + conclusions

Write `reports/results.md`: final metrics table (leaderboard, mean ± std for academic),
figures referenced, diagnostics summary, and a **conclusions** section in plain language —
what worked, what didn't, what's recommended next. Every number here must come from the
actual run output in Steps 1–5 — never fabricate, extrapolate, or "round to what looks right".

## Step 7 — Provenance

```
python "$CLAUDE_PLUGIN_ROOT/scripts/provenance.py"
```
Record seeds (all of them, for multi-seed runs), library versions, data hash, and git commit
for this result. Append, don't overwrite — a project can have multiple recorded experiments.

## Step 8 — Hand off to verify

Both gates apply here (code smoke — `pipeline.py` itself must import/run cleanly; model
quality — same rubric as `modeling`, since a full run can resurface issues a quick modeling
iteration didn't hit, e.g. CV spread across the full multi-seed set). Fix and re-verify
(bounded retries, ~3) before setting `phases.experiment = "done"`. Once verified, results are
ready for `document`.

## Boundaries

- Don't cherry-pick the best seed/fold and report it as "the" result — report the aggregate.
- Don't skip Step 5's significance testing for an academic profile just because model A's
  point estimate is higher — a difference within noise is not a claim.
- Writing the PDF/PPTX/cards is `document`'s job — `experiment` produces the source numbers
  and figures, not the rendered deliverables.
