# Academic vs industrial profile

Captured once in the interview (`state.json.profile`), read by every downstream skill.
Ask again only if the user explicitly changes direction mid-project.

## What "academic / research" emphasizes

- **Rigor over speed.** Cross-validation *and* multi-seed repetition (`experiment` skill) —
  every headline number is mean ± std across seeds, not a single lucky run.
- **Statistical honesty.** Significance tests, confidence intervals, effect sizes
  (`scripts/stats.py`) before claiming model A beats model B.
- **Reproducibility as a first-class artifact.** Seeds, library versions, data hash, git
  commit recorded per result (`scripts/provenance.py`); the paper's numbers must be
  regenerable from the repo alone.
- **Ablations.** Modeling should show what happens with a component removed/varied, not just
  the best config.
- **Publication-ready output.** `document` renders the academic report template: abstract →
  intro → data → method → experiments → results (tables/figures) → discussion →
  references/BibTeX. Figures follow academic conventions (readable at print size, captioned,
  no chartjunk).
- **Baseline + ablation table**, not just a leaderboard.

## What "industrial / production" emphasizes

- **Decision-relevance over completeness.** Metrics tie to a business KPI or decision
  threshold (cost of false positive vs false negative), not just accuracy/F1 in the abstract.
- **Deployment path.** The `+mlops` tier is more likely to be selected; `modeling` favors
  models that are easy to serve and monitor over marginal accuracy gains.
- **Stakeholder-legible output.** `document` renders the industrial report template: exec
  summary → problem → data → approach → results → business impact → next steps, plus a PPTX
  deck for a non-technical audience.
- **Monitoring over ablation.** `mlops` (drift detection, retraining triggers) matters more
  than proving a component's marginal contribution.
- **Time-to-value.** A single strong CV run with a clear variance estimate is often enough;
  multi-seed repetition is optional unless the user asks for it.

## Shared regardless of profile

Leakage-safety, the smoke gate, the baseline-must-beat-Dummy rule, explainability, and the
fairness/bias check are **not** profile-gated — every project gets them (design spec §10).
The profile changes *emphasis and report shape*, not whether quality gates run.

## Where this steers each skill

| Skill | Academic | Industrial |
|---|---|---|
| `modeling` | favors interpretable/ablatable configs, logs every variant | favors deployable, low-latency models |
| `experiment` | CV + multi-seed mandatory, `stats.py` significance tests | single robust CV run acceptable; business-KPI framing |
| `mlops` | optional, only if asked | more likely selected; monitoring emphasized |
| `document` | academic report template + BibTeX | industrial report template + deck + business impact |
