# Command Reference

`datalab` ships **seven** commands. Each is a thin, discoverable entry point that loads one of the plugin's skills (or, for `/datalab:doctor`, runs a deterministic script) — see [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) for why it's built this way. Every command accepts free-text after it as extra context — that text is passed straight through as your scope/goal, so `/datalab:new build a churn classifier from data/customers.csv` works exactly as you'd expect.

## At a glance

| Command | Drives | Typical point in the project |
|---|---|---|
| [`/datalab:new`](#datalabnew) | `orchestrator` → `scaffold` | Start of a project |
| [`/datalab:work`](#datalabwork) | `orchestrator` (existing-project path) | Any time after that |
| [`/datalab:run`](#datalabrun) | `experiment` | Once a model exists |
| [`/datalab:docs`](#datalabdocs) | `document` | Once real results exist |
| [`/datalab:doctor`](#datalabdoctor) | `scripts/doctor.py` | Right after install, or when something's broken |
| [`/datalab:setup`](#datalabsetup) | dependency installer | Right after install, or on demand |
| [`/datalab:help`](#datalabhelp) | reference | Any time |

You never have to use these by name — every skill behind them also auto-activates from plain English ("help me start a classification project," "run the experiment," "write this up"). The commands exist so there's always an exact, memorable way to trigger each one.

---

## `/datalab:new`

**Scaffold a new project via a data-aware interview.**

### When to use it
You're starting a project that doesn't have a `.datalab/state.json` yet — an empty folder, or a folder with just a dataset dropped in.

### What happens
Loads the **`orchestrator`** skill on its new-project path:
1. Confirms there's no existing state to resume (checks for `.datalab/state.json`, then for signs of an unmanaged project — `.git`, `src/`, `pipeline.py`, a populated `data/`).
2. If you have data already, profiles it (shape, per-column dtype/missingness, a *proposed* target and task type) so the interview can confirm instead of ask from scratch.
3. Asks only what it can't infer: project profile (academic/industrial), goal/task type, where your data is, what deliverables you want, and your environment (Python version, package manager) — with sensible defaults it confirms rather than demands.
4. Picks the tier(s) — `base` always, plus `+ml`, `+mlops`, `+genai`, `+dashboard` as your answers imply.
5. Delegates to **`scaffold`**, which renders the project (never overwriting anything already on disk), initializes `.datalab/state.json` and a provenance manifest, and runs a smoke check before reporting success.
6. Offers to run EDA immediately.

### Example

```
/datalab:new
/datalab:new build a customer-churn classifier from data/raw/customers.csv
/datalab:new start an academic project clustering this survey data
```

### Output
A full project skeleton on disk (see [Project tiers explained](../README.md#project-tiers-explained)), `.datalab/state.json`, a provenance manifest, and (if accepted) a filled EDA notebook.

### Related
[`/datalab:work`](#datalabwork) (everything after this), [`/datalab:doctor`](#datalabdoctor) (if setup isn't done yet).

---

## `/datalab:work`

**Continue or complete an existing project.**

### When to use it
Any time after `/datalab:new` — this is the command you come back to, repeatedly, as a project progresses. It's also the right command for a project `datalab` never scaffolded in the first place.

### What happens
Loads the **`orchestrator`** skill on its existing-project path:
1. Reads `.datalab/state.json`. If it's missing but the project looks real, reconstructs a best-effort state from what's on disk (a filled notebook implies EDA is done, a `Dockerfile` + `serve/app.py` implies the `mlops` tier, etc.) and **tells you plainly what was inferred versus read**.
2. Re-profiles any data present.
3. Runs a **gap analysis**: dependency pinning, tests, reproducibility (seed/config/provenance present?), data versioning, model tracking, a schema contract, pre-commit hooks, over/underfitting risk in any existing model, PII exposure, vulnerable dependencies.
4. Presents a prioritized list of next steps and waits for your go-ahead.
5. On approval, delegates to the relevant phase skill(s) **one at a time** (`scaffold gaps → eda → modeling → experiment → mlops → document`), each gated by **`verify`** before moving to the next, and **never redoes a phase already marked `done`**.

### Example

```
/datalab:work
/datalab:work focus on the modeling phase, skip mlops for now
```

### Output
Varies by what phase runs — could be a filled notebook, a trained pipeline, wired-up MLOps files, or deliverables. `.datalab/state.json` is updated to reflect the new phase status either way.

### Related
[`/datalab:run`](#datalabrun) and [`/datalab:docs`](#datalabdocs) are more specific — use them when you specifically want "run the full experiment" or "generate deliverables" rather than "figure out what's next."

---

## `/datalab:run`

**Run the full experiment end-to-end — results, plots, conclusions.**

### When to use it
Once `modeling` has produced a candidate pipeline — or any time later you want a fresh, complete run (e.g., your data changed, or you want an official recorded result instead of a quick modeling iteration).

### What happens
Loads the **`experiment`** skill, which executes `pipeline.py` for real, start to finish:

```
load → validate (schema.py) → preprocess (leakage-safe) → train (CV; multi-seed
mean±std if profile == academic) → evaluate → diagnostics → explain/fairness →
publication-quality figures → reports/results.md
```

It also runs significance testing and confidence intervals (`scripts/stats.py`) before claiming one model beats another, and records a provenance manifest (seeds, library versions, data hash, git commit). Both the code smoke gate and the model-quality gate apply here — a full run can resurface issues a quick modeling pass didn't hit (e.g., cross-validation spread across a full multi-seed set).

### Example

```
/datalab:run
/datalab:run re-run now that I've added the new feature columns
```

### Output
`reports/results.md` (final metrics table + written conclusions), `reports/figures/*`, an updated provenance manifest. `phases.experiment` is only set to `"done"` after `verify` passes.

### Related
[`/datalab:work`](#datalabwork) (to build/rebuild the model first), [`/datalab:docs`](#datalabdocs) (turns these results into a report).

---

## `/datalab:docs`

**Generate documentation, PDF report, PPTX deck, and model/data cards.**

### When to use it
After `/datalab:run` has produced real results — this command never fabricates numbers, so if a result is missing, it says so instead of guessing.

### What happens
Loads the **`document`** skill:
1. Gathers real sources only — your `README.md`, notebook output (converted via `nb_to_md.py`), `reports/results.md`, `reports/figures/*`, `reports/data_dictionary.md`, diagnostics/explainability output, and the provenance manifest.
2. Assembles `reports/report.md` following the template for your project's profile — **academic** (abstract → intro → data → method → experiments → results → discussion → references/BibTeX) or **industrial** (executive summary → problem → data → approach → results → business impact → next steps).
3. Renders `reports/report.pdf` and a condensed `reports/deck.pptx` (6–12 slides, not a slide-per-paragraph dump). Both **embed your figures and render metrics tables** — the PDF and the deck each show the confusion-matrix/ROC figures and the results table, not just bullet text.
4. Fills the **governance bundle** — model card, data card, compliance checklist — from real metrics, explainability, fairness, and provenance output.
5. Optionally wires up a dashboard stub if you asked for one.
6. Confirms every requested file exists and is non-empty before reporting done; if a script fails because of a missing dependency, it tells you the exact fix (or points at `/datalab:doctor`) rather than silently skipping a deliverable.

### Example

```
/datalab:docs
/datalab:docs just the PDF report, skip the deck this time
```

### Output
`reports/report.pdf`, `reports/deck.pptx`, filled `templates/governance/{MODEL_CARD.md,DATA_CARD.md,COMPLIANCE_CHECKLIST.md}`, and optionally a dashboard stub.

### Related
[`/datalab:run`](#datalabrun) must have produced results first.

---

## `/datalab:doctor`

**Health check — Python, dependencies, and plugin wiring.**

### When to use it
Right after installing, or any time something isn't behaving — it's always the first thing to run when in doubt.

### What happens
Runs `scripts/doctor.py` and interprets the result:
1. Confirms your Python version is 3.10 or newer.
2. Checks that the plugin's own manifest (`.claude-plugin/plugin.json`) exists and is valid — if not, your install may be corrupted.
3. Checks that the **core** packages `datalab`'s tooling needs are importable — this is what determines the overall healthy/unhealthy verdict.
4. Also reports, informationally, every **optional** feature-gated package (SHAP, pandera, Optuna, Evidently, pip-audit, DVC, MLflow, FastAPI, uvicorn) — present or not, each tagged with the feature it unlocks (explainability, data validation, hyperparameter tuning, drift monitoring, dependency scanning, MLOps). A missing optional package is never a failure, just information about what a given feature would need.
5. If a **core** package is missing, tells you the exact fix — normally, that just means running [`/datalab:setup`](#datalabsetup) (or, as a fallback, the literal `pip install ...` line the check prints). If an **optional** one is missing, it points you at `/datalab:setup --full` or `--genai`.
6. Summarizes: healthy, or the specific fixes needed.

### Example

```
/datalab:doctor
```

### Output
A pass/fail report per check, plus a concrete fix line if anything failed. Doesn't modify any files.

### Related
[`/datalab:setup`](#datalabsetup) is almost always the fix for anything `/datalab:doctor` flags.

---

## `/datalab:setup`

**Install datalab's own dependencies — no manual `pip install` required.**

### When to use it
Right after `/plugin install datalab` (this is step 3 of installation), and again any time a feature tells you it needs a package you don't have yet.

### What happens
Installs Python packages for the plugin's **own tooling** — not your project's dependencies (those are separate; see [Requirements & dependencies](../README.md#requirements--dependencies)). Three modes:

| Invocation | Installs |
|---|---|
| `/datalab:setup` | **Core set** (`scripts/requirements.txt`) — just enough for scaffolding, doctor, EDA helpers, baseline modeling support, and PDF/PPTX/notebook generation. This is what most projects need, always. |
| `/datalab:setup --full` | Core set **plus** `scripts/requirements-optional.txt`: SHAP (explainability), pandera (schema validation), Optuna (hyperparameter tuning), Evidently (drift monitoring), pip-audit (dependency vulnerability scanning), and DVC, MLflow, FastAPI, uvicorn (MLOps serving/tracking). |
| `/datalab:setup --genai` | Core set **plus** `scripts/requirements-genai.txt` — GenAI/RAG-specific libraries (LangChain, ChromaDB, sentence-transformers, `ragas`) — only needed if you're building a `genai-rag` project. |
| `/datalab:setup --full --genai` | Everything — both optional groups at once. |

Add `--dry-run` to any of the above to print the exact `pip install` commands without installing anything — useful if you'd rather run them by hand, or you're on a restricted network. It's always safe to re-run `/datalab:setup` — it only installs what's missing, and one group failing (say, a GenAI library) never blocks the others from installing. You don't need to guess which mode you need up front: `datalab` tells you (via `/datalab:doctor` or inline, when a skill hits a missing package) exactly when to re-run with `--full` or `--genai`.

### Example

```
/datalab:setup
/datalab:setup --full
/datalab:setup --genai
/datalab:setup --full --dry-run
```

### Output
Packages installed into your active Python environment. No project files are touched.

### Related
[`/datalab:doctor`](#datalabdoctor) tells you whether you need to run this (again).

---

## `/datalab:help`

**Show an overview of commands, skills, and current project status.**

### When to use it
Any time you forget what's available, or want a quick refresher on where a project stands without digging through `.datalab/state.json` yourself.

### What happens
Gives you a short, conversational overview — not a wall of text: what `datalab` is in one line; all seven commands, each with a one-line description; the typical workflow (`/datalab:setup → /datalab:new` (or `/datalab:work`) `→ /datalab:run → /datalab:docs`); a reminder that skills also auto-activate from plain English, without needing an explicit command; and where to go for more (the README for install steps and the full command reference, `docs/specs/` for the design spec, `docs/plans/` for build plans). If you name a specific command or topic, it focuses the overview on that instead of repeating everything.

### Example

```
/datalab:help
```

### Output
Reference text only — no files are created or changed.

### Related
Everything — this is the map back to all the others.
