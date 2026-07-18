---
name: scaffold
description: Use when creating a new data science project skeleton — renders the adaptive tiered structure (base/ML/MLOps/GenAI) from templates, non-clobbering, then initializes state + provenance.
---

# Scaffold

> **Bundled scripts live in the plugin, not the user's project.** Invoke datalab's
> Python scripts with the plugin path, e.g. `python "$CLAUDE_PLUGIN_ROOT/scripts/<name>.py"`.
> If `$CLAUDE_PLUGIN_ROOT` is unset, find the datalab plugin folder (the one containing
> `.claude-plugin/plugin.json`). The working directory is the user's own project.

Renders the tiered project skeleton from `templates/` for a new project, or adds a missing
tier to an existing one (e.g., an existing project gains `+mlops` later). Called by
`orchestrator` after the interview; never invoked directly on free-text without a decided
`{profile, task_type, target, tier, environment}`.

## Step 1 — Confirm inputs

You need, from the orchestrator's interview: `profile`, `task_type`, `target` (or null),
`tier` (list, e.g. `["base","ml"]`), `environment` (`manager`, `python`), and a project name
(default: current directory name). If any is missing, hand back to `orchestrator` — don't
guess a profile or task type yourself.

## Step 2 — Render templates

```
python "$CLAUDE_PLUGIN_ROOT/scripts/scaffold_render.py" --tier base,ml --task-type classification \
    --project <name> --python 3.11 --manager uv --dest .
```
(Check `--help` if flags differ.) This reads `templates/stacks.yaml` — the single source of
truth mapping task-type to package set + recipe — and substitutes `{{pkg}}`, `{{python}}`,
`{{project}}` placeholders into the rendered files.

**Non-clobbering is mandatory**: never overwrite a file that already exists on disk. The
renderer should skip existing paths; if you're placing any file by hand instead of via the
script, check existence first. Report **added vs skipped** explicitly to the user — skipped
files are not a failure, they mean the user already customized that file.

What each tier/task-type adds: `references/tiers.md`. Use it to sanity-check the renderer's
output before moving on — e.g., `+ml` must produce `schema.py`, `params.yaml`,
`experiments/`; `+mlops` must produce `Dockerfile`, `.github/workflows/ci.yml`, `dvc.yaml`,
`serve/app.py`, `monitoring/`.

If `task_type` has no data yet (`data` was "I don't have one" in the interview), also run
`scripts/sample_data.py` for that task type so the project isn't empty of data to EDA.

## Step 3 — Initialize state + provenance

Write `.datalab/state.json` using the schema in `skills/orchestrator/SKILL.md` (`orchestrator`
owns the schema; scaffold is just the first writer). Set `phases.scaffold = "in_progress"`
while rendering, `"done"` only after Step 4 passes.

Run `scripts/provenance.py` to record the initial manifest (seeds from `config.yaml`, library
versions from the rendered `requirements.txt`, git commit if `.git` exists, data hash if a
dataset is present).

## Step 4 — Hand off to verify (smoke gate only)

Delegate to `verify` for the **code smoke gate**: imports resolve, `tasks.py test` /
`pytest -q` passes on `tests/test_smoke.py`, `notebooks/01_eda.ipynb` executes (even if
empty of analysis, it must run). Nothing is "done" on a red gate — fix the rendered files and
re-verify (bounded retries, ~3) before reporting back to `orchestrator`.

## Step 5 — Report and offer auto-EDA

Report files added/skipped, tier(s) rendered, and state initialized. Set
`phases.scaffold = "done"`. Then — per the "deliver instant value" requirement — proactively
offer to run `eda` immediately if a dataset is present. Don't run it without offering first;
the user may want to inspect the skeleton before analysis starts.

## Boundaries

- Never invent a tier or task type not given by `orchestrator`.
- Never hand-write files that `templates/` already covers — render, don't improvise, so the
  project stays consistent with `stacks.yaml`.
- Model code, notebook analysis, and reports are out of scope here — that's `eda`,
  `modeling`, `experiment`, and `document`.
