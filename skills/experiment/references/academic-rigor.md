# Academic rigor protocol

Applies whenever `state.json.profile == "academic"`; recommended (lighter touch) for
industrial projects making a real deployment claim.

## Multi-seed protocol

1. Pick ≥5 seeds (default: `SEED, SEED+1, ..., SEED+4` from `config.yaml`, or a documented
   fixed list — never *random* seeds you didn't record).
2. For each seed: re-run the full CV training/evaluation with that seed controlling both the
   CV splitter and the model's own randomness.
3. Aggregate every headline metric as **mean ± std across the seeds** (report n).
4. Report the *distribution*, not just mean ± std, if it's notably non-normal (e.g., a
   boxplot or the min/max alongside).

## CV protocol

- Match the CV strategy to the data (`skills/modeling/references/task-recipes.md`) —
  stratified for classification, plain k-fold for regression, `TimeSeriesSplit` for
  time-series, group-aware if entities repeat.
- k=5 is the default; smaller datasets may need k=10 or leave-one-out — justify the choice in
  `reports/results.md`, don't just default silently on a 200-row dataset.
- Report the per-fold spread (std or min–max), not just the mean — a tight vs wide spread is
  itself a finding (see `skills/verify/references/model-quality.md` for what a too-tight or
  too-wide spread implies).

## Significance testing

- Compare two models on the **same folds/seeds** (paired), not independently-drawn samples —
  use a paired test: paired t-test (if the per-fold score differences are roughly normal) or
  Wilcoxon signed-rank (if not).
- Report a p-value **and** an effect size (e.g., Cohen's d on the paired differences) — a
  significant-but-tiny effect is worth saying is tiny.
- Report confidence intervals on headline metrics (bootstrap or the multi-seed std), not just
  point estimates.
- Never claim "model A is better" from a single point-estimate difference without this step.

## Reporting format

- `metric = 0.847 ± 0.012 (n=5 seeds, 5-fold CV)` — always state what's being averaged over.
- Ablation table: one row per component removed/varied, same metric, same protocol.
- State the baseline number in the same table, not just prose — the reader should see the
  full climb from Dummy to the final model at a glance.

## Reproducibility checklist

- [ ] All seeds used are recorded (not just "we used random seeds")
- [ ] `scripts/provenance.py` ran for this result — versions, data hash, git commit captured
- [ ] `config.yaml`/`params.yaml` alone (plus the recorded seed list) are enough to reproduce
      the reported numbers by re-running `pipeline.py`
- [ ] No manual notebook-only steps were required to reach the reported numbers

## Anti-patterns to avoid

- Reporting the best of N runs instead of the aggregate.
- Tuning hyperparameters on the test/held-out set (that's what CV/validation folds are for).
- Silently dropping seeds/folds that "didn't work" without disclosing it.
- Comparing models evaluated under different CV protocols or different data preprocessing.
