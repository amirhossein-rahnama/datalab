# datalab

**Turn an empty folder into a finished, reproducible data science project — scaffolded, run, quality-checked, and documented, without leaving Claude Code.**

`datalab` is a [Claude Code](https://claude.com/claude-code) plugin. It adds seven `/datalab:*` commands and eight background skills that turn Claude Code into a disciplined data scientist: one that interviews you before it codes, never skips a baseline comparison, never reports a leaky pipeline as "done," and always leaves you with a documented, reproducible project.

## What is datalab?

A Claude Code **plugin** is a bundle of commands and skills that teaches Claude a workflow. `datalab`'s workflow is "build, run, and complete a data science project" — for **any** kind of project:

- **Analysis**: exploratory data analysis (EDA)
- **Classic ML**: classification, regression, clustering, time-series, recommendation
- **Deep learning**: NLP, computer vision
- **Production**: end-to-end pipelines with deployment and monitoring
- **GenAI**: retrieval-augmented generation (RAG)

It works whether you're starting from a completely empty folder, a folder with just a CSV in it, or a half-finished project you started six months ago and forgot about.

## Why

Doing a data science project *properly* — not just "make a notebook that runs" — means remembering a long list of things every single time: split before you scale, compare against a baseline, check for class imbalance, watch for leakage, explain what the model actually learned, check it's not systematically worse for some subgroup, write it all up, make the slides. It's easy to skip steps under deadline pressure, and easy to forget which projects you actually did this rigorously for.

`datalab` bakes that checklist into the tool itself:

- You go from an **empty folder** (or an existing one) to a **scaffolded, reproducible project skeleton** in one command.
- Running the full experiment produces **real results** — not a notebook that only works if you run the cells in the right order once.
- Nothing is reported "done" until it passes a **quality gate**: code that imports and runs, a model that beats a naive baseline, no signs of data leakage, and an explainability + fairness pass.
- You end with **actual deliverables** — a PDF report, a slide deck, a model card, a data card — generated from your real results, not hand-written from memory the night before a deadline.

## Install

```
/plugin marketplace add https://github.com/amirhossein-rahnama/datalab
/plugin install datalab
/datalab:setup
```

1. **`/plugin marketplace add ...`** — registers this repository as a plugin source.
2. **`/plugin install datalab`** — installs the `datalab` plugin (commands + skills) into Claude Code.
3. **`/datalab:setup`** — installs the small set of Python packages the plugin's own tooling needs (report generation, doctor, notebook helpers). **You never run `pip install` by hand** — `/datalab:setup` does it for you, and it only installs what's needed. Heavier, feature-specific libraries (SHAP, Optuna, Evidently, pandera, GenAI/RAG libraries) install on demand later — see [Requirements & dependencies](#requirements--dependencies).

That's it — you're ready. Requires **Python 3.10+**; nothing else to install on your system (no LaTeX, no pandoc, no compiled toolchains).

Sanity-check any time with:

```
/datalab:doctor
```

## 60-second quickstart

Say you have `data/customers.csv` and want to know which customers are about to churn.

```
/datalab:new
```

Claude looks at your CSV, proposes "classification, target = `churn`," and asks a couple of quick multiple-choice questions — typically just:

1. *"Academic/research or industrial/production?"*
2. *"Looks like classification, target=`churn` — correct?"*
3. *"What do you need out of this: notebook, trained model, PDF report, PPTX deck, model/data cards, dashboard, production API?"* (pick any number)

Anything it can already infer (data path, environment, package manager) it confirms instead of asking. Answer those three, and you get a full project skeleton, seeded and ready to go — then:

```
/datalab:run
```

runs the full pipeline end-to-end: load → validate → preprocess (leakage-safe) → train → evaluate → diagnostics → explain/fairness → figures → a written results file. Then:

```
/datalab:docs
```

turns those results into a PDF report, a PPTX deck, and a model card + data card, all generated from your actual numbers.

Want to see this exact flow already run for you, with no setup of your own data required? Jump to [`examples/iris-classification`](examples/iris-classification) — `cd` into it and run `/datalab:work`.

## Commands

All commands accept free-text arguments as extra context (e.g. `/datalab:new predict customer churn from data/customers.csv`).

| Command | What it does | Example |
|---|---|---|
| `/datalab:new` | Scaffold a new project via a short, data-aware interview | `/datalab:new build a churn classifier from data/customers.csv` |
| `/datalab:work` | Continue or complete an existing project — resumes from `.datalab/state.json`, or reconstructs it if missing | `/datalab:work` |
| `/datalab:run` | Run the full experiment end-to-end: results, plots, and written conclusions | `/datalab:run` |
| `/datalab:docs` | Generate documentation: PDF report, PPTX deck, model card, data card, compliance checklist | `/datalab:docs` |
| `/datalab:doctor` | Health check — Python version, installed packages, plugin wiring | `/datalab:doctor` |
| `/datalab:setup` | Install datalab's own Python dependencies (core by default) | `/datalab:setup --full` or `/datalab:setup --genai` |
| `/datalab:help` | Show an overview of all commands, skills, and (if inside a project) current status | `/datalab:help` |

You don't have to memorize these — plain English works too ("help me start a classification project," "run the experiment," "write up the results") because the skills behind each command auto-activate from natural language. The commands exist so there's always a reliable, discoverable, exact way to trigger each phase. Full reference: [`docs/COMMANDS.md`](docs/COMMANDS.md).

## Walkthrough — a new project

1. **Start in an empty (or near-empty) folder** and run `/datalab:new`.
2. **Claude detects "new"** (no `.datalab/state.json`, nothing on disk yet) and, if you already have data sitting in the folder, profiles it — inferring shape, column types, missingness, and a *proposed* task type and target column.
3. **You answer a short interview** — profile (academic/industrial), goal/task type, where your data is (or "I don't have any yet"), what deliverables you want, and environment (Python version / package manager — sensible defaults are suggested, not demanded).
4. **Claude picks a tier** automatically from your answers: `base` always, `+ml` if you're modeling, `+mlops` if you need deployment/monitoring, `+genai` for RAG, `+dashboard` if you asked for one. See [Project tiers explained](#project-tiers-explained).
5. **The project is scaffolded** — every file is rendered from a template, nothing pre-existing is ever overwritten. You'll see a report like:
   ```
   Added:   config.yaml, pipeline.py, tasks.py, src/churn/, tests/test_smoke.py, schema.py, ...
   Skipped: README.md (already existed)
   ```
6. **A smoke check runs automatically** — imports resolve, `pytest` passes, the starter notebook executes top to bottom. Nothing is reported finished on a red check.
7. **Claude offers to run EDA immediately** so you get value right away — accept it, and `notebooks/01_eda.ipynb` gets filled in for real (distributions, missingness, correlations, a leakage screen) along with a data dictionary and saved figures.
8. From here, `/datalab:run` trains and evaluates, and `/datalab:docs` writes it all up.

## Walkthrough — an existing project

1. Run `/datalab:work` inside a project you already have — whether it was scaffolded by `datalab` before, or it's a project you built by hand.
2. **If `.datalab/state.json` exists**, Claude resumes exactly where it left off and never redoes a phase already marked `done`.
3. **If it doesn't exist but the project looks real** (there's a `.git`, a `src/`, a `pipeline.py`, or data already in `data/`), Claude reconstructs a best-effort state by reading what's on disk — and tells you plainly which parts are inferred versus known.
4. **Claude runs a gap analysis**: pinned dependencies, tests, reproducibility (seed/config/provenance present?), data versioning, a schema contract, pre-commit hooks, whether any existing model looks over/underfit, exposed PII, vulnerable dependencies.
5. **You get a prioritized list of next steps** — nothing happens without your go-ahead.
6. **On approval**, Claude works through the phases one at a time (`scaffold gaps → eda → modeling → experiment → mlops → document`), gated by `verify` after each one, skipping anything already done.

## Project tiers explained

`datalab` scaffolds only what your project actually needs, layered on top of a common base — and layering is **non-destructive**: adding a tier later (e.g., you decide to deploy a project that started as pure EDA) never touches files you already have.

| Tier | Added when... | What you get |
|---|---|---|
| `base` (always) | every project | `README.md`, `requirements.txt`, `tasks.py` (setup/lab/test/lint/report/run), `config.yaml` + seed, `pipeline.py`, pre-commit config, `.gitignore`, `data/{raw,interim,processed,external}/`, `notebooks/01_eda.ipynb`, `src/<pkg>/`, `tests/test_smoke.py`, `reports/figures/`, `.datalab/state.json` |
| `+ml` | your goal is classification, regression, clustering, time-series, NLP, computer vision, or recommendation | `schema.py` (data-contract validation), `src/<pkg>/models/{train,predict}.py`, `params.yaml`, `configs/`, `experiments/`, plus task-specific packages (e.g. XGBoost for tabular, PyTorch/TensorFlow for deep learning) |
| `+mlops` | your deliverables include deployment, a production API, or monitoring | `Dockerfile`, `.github/workflows/ci.yml`, `dvc.yaml`, MLflow tracking/registry, `serve/app.py` (FastAPI), `monitoring/` (drift detection) |
| `+genai` | your task type is GenAI/RAG | a full retrieval pipeline (`loader → chunk → embed → vector store → retrieve → generate`), a `ragas`-based eval harness, prompt templates, LLM cost/latency logging |
| `+dashboard` | you asked for a dashboard | a Streamlit/Gradio app stub wired to your trained model |

Tiers stack — a typical production ML project ends up `base + ml + mlops`.

## What you get

| Deliverable | File(s) | Produced by |
|---|---|---|
| Filled EDA notebook + data dictionary | `notebooks/01_eda.ipynb`, `reports/data_dictionary.md` | `/datalab:new` (auto-EDA) or `/datalab:work` |
| Standardized figures | `reports/figures/*` | `eda` and `experiment` |
| Trained pipeline(s) + experiment leaderboard | `experiments/`, `src/<pkg>/models/` | `/datalab:work` (modeling) |
| Final results + written conclusions | `reports/results.md` | `/datalab:run` |
| PDF report (academic or industrial template) | `reports/report.pdf` | `/datalab:docs` |
| PPTX slide deck | `reports/deck.pptx` | `/datalab:docs` |
| Model card, data card, compliance checklist | `templates/governance/*.md` (filled) | `/datalab:docs` |
| Provenance manifest (seeds, library versions, data hash, git commit) | recorded per result | every run |
| Optional: dashboard | `templates/dashboard/app.py` (wired to your model) | `/datalab:docs` |
| Optional: production wiring | `Dockerfile`, CI, DVC, MLflow, FastAPI serving, drift monitoring | `mlops` (via `/datalab:work`) |

Want to see all of this already produced, with zero setup? [`examples/iris-classification`](examples/iris-classification) is a small, real, end-to-end project bundled with the plugin — both a demo and the plugin's own test fixture; `cd examples/iris-classification && /datalab:work` and follow along. Want to see the actual output files first, with no commands at all? [`examples/sample-outputs`](examples/sample-outputs) has the real generated PDF report, PPTX deck, and a figure from that same project, reflecting an actual run — test accuracy **0.911**, 5-fold CV **0.960 ± 0.039**, comfortably beating a 0.333 dummy baseline.

## How it works

`datalab` isn't one big pass trying to do everything at once. It's an **orchestrator** skill acting like a project manager, plus a **specialist skill per phase**:

```
you  →  /datalab:*  or plain English
              │
              ▼
        orchestrator        "what's the state of this project, and what happens next?"
              │
   ┌────┬─────┼──────┬───────┬─────────┐
   ▼    ▼     ▼      ▼       ▼         ▼
scaffold eda modeling experiment mlops document
   │    │     │        │        │
   └────┴─────┴───┬────┴────────┘
                   ▼
                verify        code smoke gate + model-quality gate —
                              never reports "done" on a red result
```

The **orchestrator** never writes project code itself — it figures out new-vs-existing, asks only what it can't infer, picks the tier, and delegates. Each **phase skill** (`scaffold`, `eda`, `modeling`, `experiment`, `mlops`) does its work and then hands off to **`verify`** before it's allowed to claim success: imports have to resolve, tests have to pass, notebooks have to execute top to bottom — and for anything that trains a model, it also has to beat a naive baseline, show no signs of leakage, and get an explainability + fairness pass. On a failure, the owning skill gets the exact error back and fixes it (a few bounded attempts) — nothing is silently downgraded to "done, mostly." `document` turns the accumulated results into deliverables once `experiment` has produced real numbers.

Full architecture, the tier system, and the state file schema: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Requirements & dependencies

- **Python 3.10+** — the only hard requirement.
- **Pure pip, no system dependencies** — no LaTeX, no pandoc, no compiled toolchains. Works the same on Windows, macOS, and Linux.

There are two separate layers of dependencies, and `/datalab:setup` only ever touches the first one:

| Layer | For | Installed by |
|---|---|---|
| Core plugin tooling (`scripts/requirements.txt`) | doctor, scaffolding, EDA helpers, PDF/PPTX/notebook conversion, baseline modeling support | `/datalab:setup` (default, automatic) |
| Optional heavy plugin tooling (`scripts/requirements-optional.txt`: SHAP, pandera, Optuna, Evidently, pip-audit, DVC, MLflow, FastAPI, uvicorn) | explainability, schema validation, hyperparameter tuning, drift monitoring, dependency auditing, MLOps serving/tracking | `/datalab:setup --full` |
| GenAI/RAG plugin tooling (`scripts/requirements-genai.txt`: LangChain, ChromaDB, sentence-transformers, ragas) | embeddings, vector store client, RAG evaluation | `/datalab:setup --genai` |
| **Your project's own dependencies** | whatever your scaffolded project's code needs (pandas, scikit-learn, XGBoost, PyTorch, ...) | rendered into *your* project's `requirements.txt` by `scaffold`; install with `python tasks.py setup` inside your project |

You only ever install the optional plugin tooling if a feature you're using actually needs it — `datalab` tells you when that's the case, rather than front-loading every possible library on day one.

## Troubleshooting

Most issues are a missing optional package or a stale Claude Code plugin cache — `/datalab:doctor` diagnoses both. Full guide, including new-Python-version wheel issues, Windows path notes, and notebook kernel errors: [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md).

## Contributing

This plugin is under active development. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for dev setup, how to run the test suite, the repo layout, and coding conventions. The design lives in [`docs/specs/`](docs/specs/) and build plans in [`docs/plans/`](docs/plans/) — read those before proposing a structural change. The single most sensitive contract in the codebase is **non-clobbering**: `scaffold` must never overwrite a file that already exists on disk. Issues and pull requests: [github.com/amirhossein-rahnama/datalab](https://github.com/amirhossein-rahnama/datalab).

## Documentation

| Doc | What's in it |
|---|---|
| [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md) | Hand-holding first-project tutorial, install to first PDF report |
| [`docs/COMMANDS.md`](docs/COMMANDS.md) | Full command reference |
| [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md) | End-to-end scenarios, including academic vs. industrial |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | How the plugin is built |
| [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) | Common issues and fixes |
| [`docs/FAQ.md`](docs/FAQ.md) | Quick answers to common questions |

## License

MIT — see [`LICENSE`](LICENSE). Copyright (c) 2026 Amir.
