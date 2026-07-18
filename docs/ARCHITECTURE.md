# Architecture

How `datalab` is actually built, for anyone extending it or just curious what's running when you type a command.

## The big idea: a hybrid orchestrator

`datalab` is not one giant prompt that tries to do everything. It's a small **orchestrator** skill that behaves like a project manager — it never writes your project's code itself — plus a **specialist skill per phase** that does the actual work, and a **`verify`** skill every specialist has to pass through before it's allowed to say "done." "Hybrid" refers to the two layers working together: thin, explicit **commands** for discoverability (so `/datalab:run` is always exactly `/datalab:run`), and smart **skills** underneath for the actual logic (so the same behavior also triggers from plain English).

## The three layers

| Layer | Where | Role |
|---|---|---|
| **Commands** | `commands/*.md` | Thin, explicit entry points. Each one just says "load skill X and follow it on path Y." They exist so the plugin is discoverable once published — typing `/datalab:` and looking at the list is a valid way to learn the tool. |
| **Skills** | `skills/*/SKILL.md` (+ `references/*.md`) | Where the logic actually lives. Skills **auto-activate from natural language**, not just from commands — a skill's frontmatter `description` is what Claude matches against what you type. `references/*.md` files are loaded on demand (progressive disclosure) rather than crammed into the main skill file. |
| **Assets** | `templates/`, `scripts/`, `examples/` | Non-code inputs the skills use: project skeleton templates (+ the declarative `stacks.yaml`), pure-Python utility scripts (profiling, diagnostics, report rendering, ...), and a worked example project. |

## How a request flows through the system

```
                        you: /datalab:*  or plain English
                                    │
                                    ▼
                     ┌────────────────────────────┐
                     │        commands/*.md         │  thin dispatchers:
                     │  ds-new · ds-work · ds-run    │  "load skill X, follow
                     │  ds-docs · ds-doctor           │  it on path Y"
                     │  ds-setup · ds-help             │
                     └──────────────┬───────────────┘
                                    │ loads
                                    ▼
                     ┌────────────────────────────┐
                     │     orchestrator (skill)     │  detect new/existing ·
                     │                                │  load/reconstruct state ·
                     │                                │  inspect data · interview ·
                     │                                │  choose tier · route
                     └──────────────┬───────────────┘
           ┌──────────┬─────────────┼─────────────┬───────────┐
           ▼          ▼             ▼             ▼           ▼
      ┌─────────┐ ┌───────┐   ┌──────────┐  ┌────────────┐┌───────┐
      │scaffold │ │  eda  │   │ modeling │  │ experiment ││ mlops │
      └────┬────┘ └───┬───┘   └────┬─────┘  └─────┬──────┘└───┬───┘
           │          │            │              │           │
           └──────────┴─────┬──────┴──────────────┴───────────┘
                             ▼
                      ┌─────────────┐
                      │   verify    │  Gate A (code smoke): imports resolve ·
                      │  (skill)    │  pytest passes · notebooks execute · lint (warn)
                      └──────┬──────┘  Gate B (model quality, whenever a model was
                             │          trained): over/underfit · leakage · CV rigor ·
                     pass ───┤          imbalance · baseline · error analysis ·
                             │          leaderboard · explainability · fairness
                             │
                       fail: exact finding (file, line, message) routed back to the
                       owning skill; fix; re-verify — bounded retries (~3), then
                       escalate to you instead of looping forever
                             │
                             ▼ (on pass)
              phases.<name> = "done" in .datalab/state.json
                             │
                             ▼
                      ┌─────────────┐
                      │  document   │  only runs once `experiment` has real
                      │  (skill)    │  results; gathers → assembles → renders →
                      └──────┬──────┘  confirms every file exists & is non-empty
                             ▼
           reports/report.pdf · reports/deck.pptx · model/data cards

   every skill above reads/writes: templates/ (+ stacks.yaml) · scripts/*.py ·
                                     .datalab/state.json · examples/

   /datalab:doctor ─► scripts/doctor.py       deterministic env/deps/wiring check,
                                                no skill involved
   /datalab:setup  ─► installs scripts/requirements.txt (core, or --full / --genai)
   /datalab:help   ─► prints the command/skill map + a state.json summary
```

`document` is drawn separately from the `verify` loop above because it runs its own lighter check (every requested deliverable file exists and is non-empty) rather than `verify`'s two gates — there's no "code" or "model" to smoke-test at that stage, only artifacts to confirm.

## The orchestrator, in detail

The orchestrator's whole job is **state, not code**:

1. **Detect** new vs. existing vs. existing-but-unmanaged (see [`docs/WORKFLOWS.md`](WORKFLOWS.md#3-picking-up-an-existing-or-unmanaged-project) for the exact signal table).
2. **Load or reconstruct** `.datalab/state.json`.
3. **Inspect data**, if any is present, via `scripts/profile_data.py`.
4. **Interview** — but only for what Steps 1–3 didn't already answer.
5. **Choose the tier(s)**.
6. **Route** to exactly one phase skill at a time, never running two phases concurrently on the same project.

It never edits files under `src/`, `notebooks/`, or `templates/`, and it never marks a `phases.*` entry `"done"` itself — only the owning phase skill does that, and only after `verify` passes.

## Lifecycle state: `.datalab/state.json`

Every `datalab`-scaffolded project carries one state file that the orchestrator reads to decide what happens next, and that every phase skill updates as it works:

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

Rules that keep this file trustworthy:
- `scaffold` creates it.
- Each phase skill sets its own `phases.<name>` to `"in_progress"` when it starts and `"done"` only once `verify` has passed — never before.
- The orchestrator updates `profile`/`task_type`/`target`/`tier`/`deliverables` right after the interview, but never touches `phases`.
- `/datalab:work` treats any `"in_progress"` phase as **interrupted**, not failed, and resumes it in place.

## The tier system

The single source of truth for "what does a tier install" is `templates/stacks.yaml` — a declarative file with three sections:

| Section | Meaning |
|---|---|
| `base.packages` | Installed into *every* scaffolded project's `requirements.txt`: `pandas`, `numpy`, `matplotlib`, `seaborn`, `scikit-learn`, `jupyter`, `pytest`, `ruff`, `pyyaml`. |
| `tasks.<task_type>` | Per task type, extra packages plus a one-line recipe string — e.g. `classification` adds `xgboost` and the recipe *"Stratified train/test + CV, class-weighted baseline, ROC/PR curves + confusion matrix, beat a Dummy baseline."* Covers `eda`, `classification`, `regression`, `clustering`, `timeseries`, `nlp`, `cv`, `recommendation`, `genai_rag`. |
| `tiers.<tier>` | Per tier, extra packages — `ml` adds `xgboost`, `optuna`, `mlflow`; `dl` adds `torch`; `mlops` adds `dvc`, `mlflow`, `fastapi`, `uvicorn`, `evidently`. |

Adding a new task type or tier is a config edit to this one file — no code changes needed elsewhere. `scripts/scaffold_render.py` reads it and substitutes `{{pkg}}` / `{{python}}` / `{{project}}` placeholders into the rendered files.

**The non-clobbering contract** is what makes tiers safe to add at any time (see [Workflow 6](WORKFLOWS.md#6-adding-a-tier-later)): the renderer must never overwrite a file that already exists on disk. It skips existing paths and reports **added vs. skipped** explicitly — a skipped file isn't a failure, it means you already customized that file and `datalab` is leaving it alone.

## Verify-before-done

`verify` is **read-mostly** — it reports pass/fail with concrete findings; it never edits another skill's files itself. The calling skill applies the fix and re-invokes `verify`.

**Gate A — code smoke gate**, run after any code generation, in order, stopping at the first failure:

| # | Check | On failure |
|---|---|---|
| 1 | Imports resolve (every new/modified module) | Hard stop — reported with file/line/message |
| 2 | `pytest -q` passes (especially `tests/test_smoke.py`) | Hard stop |
| 3 | Every touched notebook executes top-to-bottom via `nbclient` | Hard stop |
| 4 | `ruff` is clean-ish | Warning only, unless it's flagging a real bug |

**Gate B — model-quality gate**, run whenever a model was trained (`modeling`, `experiment`), via `scripts/diagnostics.py` + `scripts/explain.py`:

| Check | What it catches |
|---|---|
| Overfitting | Train/validation gap, learning-curve shape |
| Underfitting | Both scores poor and close together, near baseline |
| Leakage | Target leakage, preprocessing fit outside CV folds, temporal leakage, near-duplicate train/test rows |
| CV rigor | Right strategy for the task, reasonable fold count, reported score spread |
| Class imbalance | Flags a minority class below ~20%; blocks plain accuracy as the headline metric if so |
| Metric appropriateness | Blocks a misleading metric choice for the task/data |
| Baseline | **Hard fail** if the model doesn't beat Dummy/naive |
| Error analysis | Confusion-matrix deep dive, worst-case examples, failure slices |
| Model-comparison leaderboard | **Hard fail** if fewer than 2 real candidates were actually compared |
| Explainability | SHAP / feature importance / partial dependence present and sane |
| Fairness | Subgroup performance breakdown on any sensitive-looking column, with any gap surfaced regardless of outcome |

Any red result on either gate is reported with **what's wrong, where, and the recommended fix** — never a bare "FAIL." The owning skill gets bounded retries (~3); if it's still red after that, `verify` escalates to you with the concrete error rather than looping indefinitely or quietly reporting "done, mostly."

## Skill boundaries

Every skill has an explicit "never do this" list, so responsibilities don't blur:

| Skill | Owns | Never |
|---|---|---|
| `orchestrator` | Detection, interview, tier choice, routing | Writing project code/notebooks; marking a phase `"done"` |
| `scaffold` | Rendering the tiered skeleton (non-clobbering), initial state + provenance | Inventing a tier/task type; hand-writing what a template already covers |
| `eda` | Filling the EDA notebook, the data dictionary | Real modeling (a Dummy/quick correlation check is fine); silently cleaning data in place |
| `modeling` | Leakage-safe pipelines, baseline-first iteration, tuning, experiment tracking | Hand-rolled CV loops instead of `Pipeline` + `cross_validate`; skipping the Dummy baseline; full end-to-end runs (that's `experiment`) |
| `experiment` | The full recorded run, multi-seed protocol (academic), figures, written conclusions | Cherry-picking the best seed/fold; skipping significance testing for an academic claim; rendering the PDF/PPTX itself |
| `verify` | Pass/fail + concrete findings for both gates | Editing another skill's files; deciding to proceed past a bounded-retry failure |
| `mlops` | Docker, CI, DVC, MLflow, FastAPI serving, drift monitoring | Retraining/changing the model; skipping the `+mlops` tier check; load-testing or cloud-specific deploy (out of scope for v1) |
| `document` | Assembling deliverables from real, already-produced sources | Running new experiments to fill a gap; hand-writing PDF/PPTX bytes directly (always goes through `generate_report.py`/`generate_deck.py`) |

## Two kinds of dependencies

Easy to conflate, worth keeping separate:

| | Plugin tooling | Your project's dependencies |
|---|---|---|
| Lives in | `scripts/requirements.txt` (core) + `scripts/requirements-optional.txt` (`--full`) + `scripts/requirements-genai.txt` (`--genai`) | Rendered into *your* project's own `requirements.txt` from `templates/stacks.yaml` |
| Examples | Core: `reportlab`, `python-pptx`, `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `pyyaml`, `nbformat`, `nbclient`. Optional: `shap`, `pandera`, `optuna`, `evidently`, `pip-audit`, `dvc`, `mlflow`, `fastapi`, `uvicorn`. GenAI: `langchain`, `chromadb`, `sentence-transformers`, `ragas`. | `pandas`, `numpy`, `scikit-learn`, plus whatever your task type/tier need (e.g. `xgboost`, `torch`, `dvc`, `fastapi`) |
| Installed by | `python scripts/setup.py` (i.e. `/datalab:setup`) — default = core only; `--full` / `--genai` add the rest; `--dry-run` previews the `pip` commands without installing | `python tasks.py setup` (plain `pip install -r requirements.txt`) run **inside your scaffolded project** |
| Used by | The plugin's own scripts (doctor, report/deck generation, diagnostics, profiling, ...) | Your project's own code (`pipeline.py`, `src/<pkg>/`, notebooks) |

`scripts/doctor.py`'s **healthy/unhealthy** verdict depends only on the **core** packages (`reportlab`, `python-pptx`, `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `pyyaml`, `nbformat`, `nbclient`) plus a valid `plugin.json`. It also reports every **optional** package's presence informationally — each tagged with the feature it unlocks — so you always know exactly what `/datalab:setup --full` / `--genai` would add before you actually need it; a missing optional package never flips the verdict to unhealthy.

## Reproducibility & provenance

Every scaffolded project is seeded from `config.yaml` (`SEED`, default 42), and every recorded result — from a single modeling iteration to a full `/datalab:run` — appends a provenance manifest via `scripts/provenance.py`: the seed(s) used, installed library versions, a hash of the input data, and the current git commit if the project is a repo. Academic-profile runs record every seed in a multi-seed batch, not just one. This is what lets a reported number be regenerated later from the repo alone.

## Repository file structure

```
data-science-claude-plugin/
├── .claude-plugin/
│   ├── plugin.json              # name=datalab, version, skills[]
│   └── marketplace.json         # single-plugin marketplace entry
├── commands/
│   ├── ds-new.md                # /datalab:new
│   ├── ds-work.md               # /datalab:work
│   ├── ds-run.md                # /datalab:run
│   ├── ds-docs.md               # /datalab:docs
│   ├── ds-doctor.md             # /datalab:doctor
│   ├── ds-setup.md              # /datalab:setup
│   └── ds-help.md               # /datalab:help
├── skills/
│   ├── orchestrator/SKILL.md          (+ references/{profiles,interview}.md)
│   ├── scaffold/SKILL.md              (+ references/tiers.md)
│   ├── eda/SKILL.md                   (+ references/checklist.md)
│   ├── modeling/SKILL.md              (+ references/{task-recipes,pipelines,tuning}.md)
│   ├── experiment/SKILL.md            (+ references/{academic-rigor,plots}.md)
│   ├── verify/SKILL.md                (+ references/model-quality.md)
│   ├── mlops/SKILL.md                 (+ references/{repro,serving,ci,monitoring}.md)
│   └── document/SKILL.md              (+ references/{cards,report-academic,report-industrial}.md)
├── templates/
│   ├── stacks.yaml              # task-type -> package set + recipe (single source of truth)
│   ├── base/                    # tasks.py, requirements.txt, config.yaml, pipeline.py,
│   │                             # .pre-commit-config.yaml, .gitignore, notebooks/, src/, tests/
│   ├── ml/                      # schema.py, src/{{pkg}}/models/{train,predict}.py, params.yaml
│   ├── mlops/                   # Dockerfile, ci.yml, dvc.yaml, serve/app.py, monitoring/drift.py
│   ├── genai/                   # rag/{loader,chunk,embed,store,retrieve,generate}.py, eval/, prompts/
│   ├── dashboard/                # app.py (Streamlit/Gradio stub)
│   └── governance/                # MODEL_CARD.md, DATA_CARD.md, COMPLIANCE_CHECKLIST.md
├── scripts/
│   ├── requirements.txt          # core plugin-tooling dependencies (installed by default)
│   ├── requirements-optional.txt # heavy, feature-gated deps — installed by --full
│   ├── requirements-genai.txt    # GenAI/RAG deps — installed by --genai
│   ├── setup.py                   # installs the dependency groups above (/datalab:setup)
│   ├── doctor.py                   # env + core/optional deps + plugin-wiring health check
│   ├── profile_data.py              # profile + data dictionary + target/task guess
│   ├── scaffold_render.py            # renders templates/ + stacks.yaml, non-clobbering
│   ├── sample_data.py                 # synthetic/sample dataset generation
│   ├── diagnostics.py                  # over/underfit, CV, leakage, imbalance, baseline
│   ├── explain.py                       # SHAP / importance / partial-dependence + fairness
│   ├── plots.py                          # standardized publication-quality figures
│   ├── stats.py                           # significance tests, CIs, effect sizes
│   ├── provenance.py                       # writes the manifest: seeds, versions, hash, commit
│   ├── privacy.py                           # PII scan of datasets
│   ├── nb_to_md.py                           # notebook -> Markdown
│   ├── generate_report.py                     # Markdown -> PDF (reportlab)
│   └── generate_deck.py                        # outline -> PPTX (python-pptx)
├── examples/
│   ├── iris-classification/      # worked end-to-end project — demo AND test fixture
│   └── sample-outputs/           # that project's real, already-rendered PDF/PPTX/figures
├── tests/                        # the plugin's own pytest suite (manifest, scripts, scaffold render)
├── .github/                      # issue/PR templates + CI workflow (plugin-repo housekeeping)
├── docs/
│   ├── specs/                    # design spec (locked)
│   ├── plans/                    # build plans
│   ├── GETTING_STARTED.md · COMMANDS.md · WORKFLOWS.md
│   └── ARCHITECTURE.md · TROUBLESHOOTING.md · FAQ.md
├── README.md · CONTRIBUTING.md · CHANGELOG.md · LICENSE
```

## Testing strategy

The plugin has its own `pytest` suite under `tests/`, independent of anything it generates for your project: it validates that `plugin.json`/`marketplace.json` are well-formed and every listed skill directory exists with a valid `SKILL.md`, that `doctor.py` correctly identifies missing packages and bad Python versions, that `generate_report.py`/`generate_deck.py` produce valid non-empty PDF/PPTX files, that `nb_to_md.py` round-trips a notebook correctly, and that `scaffold_render.py` renders the base tier into a real directory tree whose `requirements.txt` parses and whose `tasks.py test` actually runs. `examples/iris-classification` doubles as an end-to-end fixture for this suite and as the worked example in the docs.
