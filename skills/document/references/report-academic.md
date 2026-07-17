# Academic report template

Section order for `reports/report.md` when `profile == academic`. Each section is a `##`
heading in the Markdown that `generate_report.py` renders to PDF.

## Abstract
2-4 sentences: problem, approach, headline result (with the mean +/- std if multi-seed), and
the one-line takeaway. Write this **last**, after every other section is final.

## Introduction
Problem motivation, why it matters, what's novel or notable about this approach (even a
class project has a "why this dataset/method" worth a paragraph), and a roadmap sentence.

## Data
Dataset description, size, source, the data dictionary summary (pull from
`reports/data_dictionary.md`, don't restate every column -- summarize + link), known
limitations/biases in the data itself.

## Method
The modeling approach: pipeline structure (leakage-safe preprocessing + model family),
hyperparameter search process if tuned, CV protocol, multi-seed protocol. Enough detail that
someone could reproduce it from this section plus the repo.

## Experiments
What was actually run: the model-comparison leaderboard (baseline through final model), any
ablations, the exact metrics used and why (tie back to class balance / task characteristics
from `eda`).

## Results
Tables and figures from `reports/results.md` and `reports/figures/`. Every number here must
trace back to an actual run -- mean +/- std with n stated, significance test results when
claiming one model beats another (from `scripts/stats.py`). Include the error-analysis
findings (`verify`'s Gate B output), not just the win/loss numbers.

## Discussion
Interpretation: why these results, what the explainability output (SHAP/importance) suggests
about what the model actually learned, the fairness/subgroup findings, limitations, threats
to validity, and concrete next steps.

## References / BibTeX
Cite the dataset source, key methods/libraries if the project draws on a specific published
approach. Keep a `reports/references.bib` alongside if the user wants a real BibTeX file -- the
Markdown section can just list citations inline `[Author, Year]` style if that's simpler.

## Style notes
- Past tense, passive-light academic register, but don't over-hedge -- state findings plainly
  with the uncertainty already captured in the +/- and p-values, not repeated in every sentence.
- Figures/tables are numbered and referenced by number in text ("Figure 2 shows...").
