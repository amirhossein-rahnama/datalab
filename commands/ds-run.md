---
description: "Run the full experiment end-to-end (results, plots, conclusions)"
---

# datalab run

Load and follow the datalab **experiment** skill (`skills/experiment/SKILL.md`) to run the
project's pipeline end-to-end: load data → validate against the schema → preprocess
(leakage-safe) → train (with cross-validation; multi-seed mean±std for academic-profile
projects) → evaluate → diagnostics → explainability/fairness → publication-quality plots →
final results and conclusions. Record the provenance manifest and hand off to the **verify**
skill before reporting the run as done.

Treat the user's arguments as scope/goal:

$ARGUMENTS
