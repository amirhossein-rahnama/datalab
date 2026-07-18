---
name: orchestrator
description: Use when starting, continuing, or planning any data science project — runs the data-aware interview, detects new vs existing, captures the academic/industrial profile, picks the tier, and routes to the right phase skill.
---

# Orchestrator

> **Bundled scripts live in the plugin, not the user's project.** Invoke datalab's
> Python scripts with the plugin path, e.g. `python "$CLAUDE_PLUGIN_ROOT/scripts/<name>.py"`.
> If `$CLAUDE_PLUGIN_ROOT` is unset, find the datalab plugin folder (the one containing
> `.claude-plugin/plugin.json`). The working directory is the user's own project.

Entry point for `/datalab:new` and `/datalab:work`, and for any free-text request to start,
continue, or plan a data science project. The orchestrator **never writes project code or
notebooks itself** — it detects state, interviews the user, decides scope, and delegates to
the phase skill that owns the work (`scaffold`, `eda`, `modeling`, `experiment`, `mlops`,
`document`), each of which hands off to `verify` before reporting success.

## Step 0 — Ensure datalab's dependencies (one-time, automatic)

The user should never have to run `/datalab:setup` by hand. Before Step 1, check the
environment and self-heal if needed:
```
python "$CLAUDE_PLUGIN_ROOT/scripts/doctor.py"
```
If any **core** package is missing (ignore the optional/feature-gated ones), install the core
set once, then continue:
```
python "$CLAUDE_PLUGIN_ROOT/scripts/setup.py"
```
If doctor is already healthy, skip silently — never reinstall. Only the small core set is
installed automatically; heavy/optional libraries stay on demand (offer `--full` / `--genai`
later, only when a feature actually needs them).

## Step 1 — Detect new vs existing

Check, in order:
1. Does `.datalab/state.json` exist? -> **existing**, resume (go to Step 2).
2. Is there a `.git` repo, a `src/`, `pipeline.py`, or a populated `data/` dir but no
   `.datalab/state.json`? -> **existing-unmanaged**: a real project datalab hasn't scaffolded.
   Treat like existing but reconstruct state from what's on disk (see
   `references/interview.md`, reconstruction table) instead of loading it.
3. Otherwise -> **new**: empty or near-empty directory.

## Step 2 — Load or reconstruct state (existing projects)

Read `.datalab/state.json` (schema below). If it's missing but the project looks real
(case 2 above), reconstruct a best-effort state by inspecting the tree (presence of
`notebooks/`, `src/`, `Dockerfile`, `dvc.yaml`, `reports/report.pdf`, etc. imply completed
phases) and tell the user you're inferring state, not reading ground truth.

Any `phases.*` already `"done"` must **not** be redone — treat `/datalab:work` as a resume,
not a restart. If a phase is `"in_progress"`, resume it in place.

## Step 3 — Inspect data

If any dataset is present (`data/raw/*`, or a path the user names), run:
```
python "$CLAUDE_PLUGIN_ROOT/scripts/profile_data.py" --input <path>
```
It prints JSON profiling the data and *proposing* a target column and task type — treat both
as defaults for the interview, never as final answers. If the script's flags differ from
this, run it with `--help` first. If no data exists yet, note that and offer
`scripts/sample_data.py` during scaffold.

## Step 4 — Interview (ask only what's unknown)

Multiple choice, data-aware, profile-aware. Never re-ask something already in `state.json` or
confidently inferable from Step 3. Full question list and routing table:
`references/interview.md`. What each profile changes downstream: `references/profiles.md`.

Minimum captured fields: **profile** (academic/industrial), **goal/task type**, **data**
(path or "generate sample"), **deliverable** (notebook/model/report/deck/dashboard/API,
multi-select), **environment** (package manager — `uv` default; Python — 3.11 default).

## Step 5 — Choose tier

- `base` — always.
- `+ml` — task type is a modeling task (classification/regression/clustering/time-series/
  NLP/computer-vision/recommendation).
- `+mlops` — deliverable includes deploy/production/API/monitoring.
- `+genai` — task type is GenAI/RAG.
- `+dashboard` — deliverable includes a dashboard.

## Step 6 — Route

**New project:** delegate to `scaffold` (renders tiers, inits state + provenance) -> after its
`verify` smoke pass, offer `eda` immediately (instant value) -> stop and report; do not
silently continue into modeling.

**Existing project — gap analysis** (design spec §9): check requirements/env pinning, tests,
reproducibility (seed/config/provenance present), data versioning, model tracking, README,
`.gitignore` for data, schema contract, pre-commit, over/underfitting risk in any existing
model, PII exposure, vulnerable deps. Present a prioritized list of next steps; on approval,
delegate to phase skills **one at a time**, each gated by `verify` before moving to the next.

## `.datalab/state.json` schema (canonical)

```json
{
  "profile": "academic | industrial",
  "task_type": "classification | regression | clustering | time-series | nlp | computer-vision | recommendation | production-pipeline | genai-rag | eda-only",
  "target": "column name or null",
  "tier": ["base", "ml", "mlops", "genai", "dashboard"],
  "environment": { "manager": "uv", "python": "3.11" },
  "deliverables": ["notebook", "model", "report", "deck", "dashboard", "api"],
  "phases": {
    "scaffold": "pending | in_progress | done",
    "eda": "pending | in_progress | done",
    "modeling": "pending | in_progress | done",
    "experiment": "pending | in_progress | done",
    "mlops": "pending | in_progress | done",
    "docs": "pending | in_progress | done"
  },
  "created": "ISO-8601 timestamp",
  "updated": "ISO-8601 timestamp"
}
```

`scaffold` creates this file. Every phase skill updates its own `phases.<name>` entry
(`in_progress` on start, `done` only after `verify` passes) and bumps `updated`. The
orchestrator updates `profile`/`task_type`/`target`/`tier`/`deliverables` after the interview,
but does not touch `phases`.

## Boundaries

- Never edit files under `src/`, `notebooks/`, `templates/`, or write model code — delegate.
- Never mark a phase `"done"` in state — only the owning phase skill does that, and only
  after `verify` passes.
- If the user's ask spans multiple phases ("build and ship a churn model"), decompose into a
  routed sequence and say so before delegating to the first skill.
