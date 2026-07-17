---
description: "Continue or complete an existing data science project"
---

# datalab work

Load and follow the datalab **orchestrator** skill (`skills/orchestrator/SKILL.md`) on its
**existing-project path**: detect the current stack, resume from `.datalab/state.json`
(reconstructing it from what's on disk if the file is missing), profile any data present, run
a gap analysis (dependencies, reproducibility, tests, data versioning, model tracking, schema
contract, pre-commit, PII, vulnerable deps), present prioritized next steps, and — on approval —
delegate to the relevant phase skill(s), each gated by the **verify** skill. Never redo work
already recorded as complete in the state file.

Treat the user's arguments as scope/goal:

$ARGUMENTS
