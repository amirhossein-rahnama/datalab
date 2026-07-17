# Interview: questions + routing

Ask only what Step 3 (data inspection) and the existing `state.json` didn't already answer.
Present each as multiple choice. Keep it to one message, not five round-trips, when possible.

## Questions

1. **Profile** — "Is this an academic/research project or an industrial/production one?"
   `academic | industrial`. Drives report template and rigor emphasis — see
   `references/profiles.md`.

2. **Goal / task type** — "What are you trying to do?"
   `EDA only | classification | regression | clustering | time-series | NLP |
   computer-vision | recommendation | production-pipeline | GenAI/RAG`.
   If `profile_data.py` proposed a task type with high confidence, present it as the default
   choice ("Looks like classification, target=`species` — correct?") instead of an open
   question.

3. **Data** — "Where's your dataset?" Accept a path, a glob, or "I don't have one yet" (in
   which case `scaffold` will offer `scripts/sample_data.py` to generate a synthetic one for
   the chosen task type).

4. **Deliverable** — "What do you need out of this?" Multi-select:
   `notebook | trained model | PDF report | PPTX deck | model/data cards | dashboard |
   production API`. Maps directly to which of `document`/`mlops` run later.

5. **Environment** — "Package manager and Python version?" Default `uv` + Python 3.11 —
   confirm rather than ask outright unless the project directory already pins something else
   (existing `pyproject.toml`/`.python-version` wins).

## New-vs-existing signal table

| Signal | Conclusion |
|---|---|
| `.datalab/state.json` present | existing — resume from it |
| No state file, but `src/`, `pipeline.py`, `.git`, or non-empty `data/` present | existing-unmanaged — reconstruct state, say so |
| No state file, directory empty or docs-only | new |

## Task type → tier routing table

| Task type | Tier(s) added on top of `base` |
|---|---|
| EDA only | none (base is enough) |
| classification / regression / clustering / time-series / NLP / computer-vision / recommendation | `+ml` |
| production-pipeline | `+ml` `+mlops` |
| GenAI/RAG | `+genai` (see `templates/genai/`) |
| any, if deliverable includes "dashboard" | add `+dashboard` |
| any, if deliverable includes "production API" or "monitoring" | add `+mlops` |

## Reconstruction heuristics (existing-unmanaged projects)

When `.datalab/state.json` is missing but the project looks real, infer:

| On-disk evidence | Infer |
|---|---|
| `notebooks/01_eda.ipynb` has executed cells/outputs | `phases.eda = done` |
| `src/*/models/train.py` or `models/*.joblib`/`.pkl` exists | `phases.modeling` at least `in_progress` |
| `reports/results.md` or `reports/figures/*` populated | `phases.experiment = done` |
| `Dockerfile` + `serve/app.py` present | tier includes `mlops`, `phases.mlops` at least `in_progress` |
| `reports/report.pdf` or `reports/deck.pptx` present | `phases.docs = done` |

Always tell the user which fields were inferred vs read, and write a fresh
`.datalab/state.json` once reconstructed so the next `/datalab:work` doesn't repeat the work.

## Routing after the interview

- **New** → delegate to `scaffold` with `{profile, task_type, target, tier, environment}`.
  After scaffold + its own `verify` pass, offer `eda` immediately (auto-EDA).
- **Existing** → run gap analysis (design spec §9), present prioritized next steps, then
  delegate to phase skills one at a time in dependency order:
  `scaffold gaps → eda → modeling → experiment → mlops → document`, skipping any phase
  already `done` and not affected by the gap analysis.
