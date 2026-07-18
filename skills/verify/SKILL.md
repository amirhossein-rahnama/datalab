---
name: verify
description: Use to verify generated work and model quality — smoke tests (imports, pytest, notebook execution) plus over/underfitting, leakage, imbalance, baseline, error analysis, and fairness checks before claiming done.
---

# Verify

> **Bundled scripts live in the plugin, not the user's project.** Invoke datalab's
> Python scripts with the plugin path, e.g. `python "$CLAUDE_PLUGIN_ROOT/scripts/<name>.py"`.
> If `$CLAUDE_PLUGIN_ROOT` is unset, find the datalab plugin folder (the one containing
> `.claude-plugin/plugin.json`). The working directory is the user's own project. If a bundled script errors because a package
> is missing, run `python "$CLAUDE_PLUGIN_ROOT/scripts/setup.py"` once to install core deps.

The gate every other phase skill calls before it's allowed to report success. **Read-mostly**:
verify reports pass/fail with concrete, actionable findings — it does not edit the owning
skill's files itself. The calling skill applies fixes and re-invokes verify. Never let a red
gate be reported as "done" upstream, regardless of how the calling skill frames it.

## Gate A — Code smoke gate (after any code generation)

Run, in order, stopping at the first failure to report:

1. **Imports resolve** — every new/modified module imports cleanly (`python -c "import ..."`
   or equivalent for scripts; for a package, `python -c "import <pkg>"`).
2. **Tests pass** — `pytest -q` (or `python tasks.py test`) across `tests/`, especially
   `tests/test_smoke.py`.
3. **Notebooks execute** — every notebook touched this phase runs top-to-bottom via
   `nbclient` with no raised exceptions.
4. **Lint** — `ruff` clean-ish; treat this as a **warning**, not a blocker, unless it's
   flagging an actual bug (undefined name, unused import shadowing a real one).

On any red result in 1–3: report the exact error (file, line, message) and route back to the
skill that generated the file — don't attempt the fix yourself. Re-run Gate A after the fix.
Bounded retries: ~3 attempts; if still red, escalate to the user with the concrete error
instead of looping indefinitely.

## Gate B — Model-quality gate (whenever a model was trained: `modeling`, `experiment`)

Run:
```
python "$CLAUDE_PLUGIN_ROOT/scripts/diagnostics.py" ...
python "$CLAUDE_PLUGIN_ROOT/scripts/explain.py" ...
```
Checks (full rubric and heuristics: `references/model-quality.md`):

- **Overfitting** — train/val gap, learning curve shape
- **Underfitting** — both train and val score poor relative to baseline
- **Leakage** — target leakage, preprocessing fit outside CV folds, temporal leakage (see
  also `skills/modeling/references/pipelines.md` for the traps this is checking for)
- **CV rigor** — correct CV strategy for the task, reasonable fold count, score spread
  reported
- **Class imbalance** — flagged, and metric choice adjusted accordingly
- **Metric appropriateness** — block plain accuracy as the headline metric on imbalanced
  classification
- **Baseline** — the model must beat Dummy/naive; if it doesn't, that's a hard fail, not a
  note
- **Error analysis** — confusion-matrix deep dive, worst-case/failure-slice examples, not
  just aggregate metrics
- **Model-comparison leaderboard** — more than one candidate was actually compared
- **Explainability** — SHAP/feature-importance/PDP present and sane (e.g., importances
  aren't dominated by an obvious leakage feature — cross-check against the leakage check)
- **Fairness** — subgroup performance breakdown + bias flag on any sensitive/protected-like
  column present in the data dictionary

Outputs (diagnostics + explain results) feed the model card in `document`.

## Reporting format

For each gate: **PASS** or **FAIL**, and for FAIL, a list of concrete findings — each with
what's wrong, where (file/metric), and the recommended fix. Never a bare "FAIL" with no
detail; the calling skill needs enough to act without re-deriving the diagnosis.

## Boundaries

- Verify does not train models, does not edit pipelines, does not rewrite notebooks — it
  reports. If asked to "just fix it", redirect to the owning skill (`modeling` for pipeline
  issues, `scaffold` for skeleton issues, `eda` for notebook issues).
- Verify does not decide whether to proceed after a bounded-retry failure — that's an
  escalation to the user, not a silent downgrade to "done with known issues".
