# Standardized figures

Generated via `scripts/plots.py`, saved to `reports/figures/<name>.png` (and `.svg` if the
script supports it — check `--help`). Before building any figure `plots.py` doesn't already
standardize, load the **`dataviz` skill** for palette/form/layout guidance so ad-hoc charts
still read as part of the same system as the standardized ones.

## Figure set by task type

| Task type | Figures |
|---|---|
| classification | confusion matrix, ROC curve, PR curve, calibration curve, class-balance bar |
| regression | predicted-vs-actual scatter, residual plot, residual histogram |
| clustering | 2D projection (PCA/UMAP) colored by cluster, silhouette plot |
| time-series | forecast-vs-actual over time, residuals over time, seasonal decomposition |
| NLP | confusion matrix (classification head), token/length distribution, top-feature/token importances |
| computer-vision | confusion matrix, sample grid of worst mispredictions, per-class accuracy bar |
| recommendation | precision@k/recall@k vs k curve, coverage/popularity bias plot |
| any modeling task | **learning curve** (train vs val score over training-set size — overfitting/underfitting signal), **feature importance / SHAP summary** |

## Conventions

- Every figure gets a caption (in `reports/results.md`, not just a bare filename) explaining
  what it shows and the one-sentence takeaway — a figure without a stated takeaway isn't
  finished.
- Consistent styling across all figures in a project (color palette, font size, figure size)
  — `plots.py` should be the only place that sets these, not ad-hoc `matplotlib` calls
  scattered across skills.
- Readable at report/print size — avoid tiny legend text or overlapping labels; this matters
  more for the academic PDF template than a dashboard.
- Academic profile: figures should be self-contained (a reader flipping straight to the
  figure, without the surrounding text, should understand the axes and what's plotted).
- Industrial profile: favor a small number of decision-relevant figures over an exhaustive
  set — the deck audience wants the 3–5 that matter, not all of them.
