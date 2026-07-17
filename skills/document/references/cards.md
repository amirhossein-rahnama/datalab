# Model card / data card / compliance checklist

Filled from `templates/governance/{MODEL_CARD.md,DATA_CARD.md,COMPLIANCE_CHECKLIST.md}` using
real output from `eda`, `modeling`/`experiment`, and `verify`'s Gate B — never placeholder
text. This bundle is what makes the project EU-AI-Act-aware/governance-ready (design spec
§13).

## Model card — field guidance

- **Model details**: task type, algorithm family, version, training date, owning
  project/team. Pull from `state.json` and the provenance manifest.
- **Intended use**: what decision this model supports, and explicitly, what it's **not**
  validated for (out-of-scope use) — this matters as much as the intended use.
- **Training data**: summary + link to the data card (don't duplicate the full data card
  here).
- **Metrics**: the leaderboard's winning row, with the CV/multi-seed protocol stated (mean ±
  std, n) — pull directly from `reports/results.md`, don't re-derive.
- **Evaluation — error analysis**: summarize `verify` Gate B's error-analysis findings
  (failure slices, worst cases).
- **Explainability**: summarize the SHAP/importance findings — what the model actually
  relies on.
- **Fairness**: the subgroup performance breakdown and any flagged gap, stated plainly even
  if the finding is "no concerning gap found in the subgroups checked" — absence of a check
  is different from a clean result, don't conflate them.
- **Caveats and recommendations**: known limitations, and what should be monitored/revisited
  post-deployment (ties to `mlops`'s drift monitoring if that tier exists).

## Data card — field guidance

- **Dataset summary**: source, size, collection method/date if known.
- **Data dictionary**: link/summarize `reports/data_dictionary.md`.
- **Preprocessing**: what transformations happen before modeling (high-level — detailed
  leakage-safe steps live in the pipeline code, not restated here).
- **Known biases/limitations**: anything `eda` flagged (skew, missingness patterns,
  demographic imbalance if applicable).
- **PII**: result of the privacy scan (`scripts/privacy.py`, run during `scaffold`/`eda`) —
  state explicitly whether PII was found and how it was handled, not just "N/A" by default.
- **Licensing/usage restrictions**: if known from the data source.

## Compliance checklist — field guidance

Frame around EU AI Act transparency/governance expectations (design spec §13):
- [ ] Model card complete and current
- [ ] Data card complete and current
- [ ] Provenance manifest recorded for the reported results (seeds, versions, data hash, git
      commit)
- [ ] Fairness/subgroup check performed and documented (regardless of outcome)
- [ ] Explainability artifacts produced and reviewed
- [ ] PII scan performed and documented
- [ ] Dependency vulnerability scan performed (`pip-audit` — see `scripts/requirements.txt`
      tooling) and any high-severity findings addressed or explicitly accepted
- [ ] Known limitations documented (model card "caveats" section, not left implicit)
- [ ] Human-in-the-loop / deployment decision owner identified (who approves this model going
      to production — a name/role, not "the team")

## Rendering

Keep the Markdown versions in `templates/governance/*.md` (filled in place, or copied to
`reports/` if the template originals should stay as templates for the next project) as the
source of truth; optionally render a PDF copy via `generate_report.py` the same way the main
report is rendered, using the card's Markdown as input.
