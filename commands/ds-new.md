---
description: "Scaffold a new data science project (interview + adaptive tiers)"
---

# datalab new

Load and follow the datalab **orchestrator** skill (`skills/orchestrator/SKILL.md`) on its
**new-project path**: detect that this is a fresh target (no `.datalab/state.json`), inspect
any data already present, run the data-aware interview (profile — academic/industrial —
goal/task type, data, deliverable, environment), choose the adaptive tier (base / +ML-DL /
+MLOps), then delegate to the **scaffold** skill to generate the non-clobbering project
skeleton and kick off the auto-EDA pass.

Treat the user's arguments as scope/goal:

$ARGUMENTS
