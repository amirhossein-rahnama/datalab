# Workflows

A cookbook of complete scenarios. If [`GETTING_STARTED.md`](GETTING_STARTED.md) is the one guided tour, this page is the set of routes you'll actually use once you know your way around. Two running examples appear throughout:

- **Project A — "churn"**: an **industrial** classification project (predict which customers churn from `data/customers.csv`).
- **Project B — "dropout"**: an **academic** classification project (a university research question — which factors predict student dropout — from a survey dataset).

They're the same *kind* of task (classification) so you can see exactly where the **profile** — academic vs. industrial — changes what `datalab` does.

## Contents

1. [New project, data in hand](#1-new-project-data-in-hand)
2. [New project, no data yet](#2-new-project-no-data-yet)
3. [Picking up an existing or unmanaged project](#3-picking-up-an-existing-or-unmanaged-project)
4. [Running a full experiment](#4-running-a-full-experiment)
5. [Generating deliverables](#5-generating-deliverables)
6. [Adding a tier later](#6-adding-a-tier-later)
7. [Academic vs. industrial, side by side](#7-academic-vs-industrial-side-by-side)
8. [A full project timeline](#8-a-full-project-timeline)

---

## 1. New project, data in hand

You have a dataset already. This is the most common path.

```
cd churn-project        # empty folder, data/raw/customers.csv already in it
/datalab:new predict customer churn
```

`datalab` profiles `customers.csv` before asking you anything, so the interview leans on confirmation ("Looks like classification, target = `churn` — correct?") instead of open questions. It captures: **profile** (industrial), **goal/task type** (classification), **data** (the path it found), **deliverables** (whatever you pick), **environment** (confirmed defaults). It then picks tier `base + ml`, delegates to `scaffold`, and — once the smoke check passes — offers EDA immediately.

**Result:** a scaffolded project, `.datalab/state.json` with `phases.scaffold = "done"`, and (if you accepted) `phases.eda = "done"` too.

## 2. New project, no data yet

You know what you want to build but don't have data in hand.

```
mkdir dropout-study
cd dropout-study
/datalab:new academic project on student dropout prediction, no data yet
```

At the **data** question, answer *"I don't have one yet."* `scaffold` notices this and runs `scripts/sample_data.py` for your chosen task type, so the project isn't empty — you get a synthetic dataset shaped like a real one for that task, enough to exercise the whole pipeline (EDA runs, a model trains, a report renders) before you swap in real data. When your real dataset shows up, drop it into `data/raw/` and run `/datalab:work` — it re-profiles and picks up from there.

## 3. Picking up an existing or unmanaged project

Two sub-cases, handled the same way by `/datalab:work`:

**3a. A `datalab`-scaffolded project, resuming.** `.datalab/state.json` exists — `datalab` reads it and continues exactly where it left off, never re-running a phase marked `"done"`.

**3b. A project you built yourself, or inherited.** No state file, but there's real content — a `.git`, a `src/`, a `pipeline.py`, or a non-empty `data/`. `datalab` reconstructs a best-effort state by reading the tree:

| What's on disk | Inferred |
|---|---|
| `notebooks/01_eda.ipynb` has executed cells/outputs | EDA done |
| `src/*/models/train.py` or a saved `.joblib`/`.pkl` model | Modeling at least in progress |
| `reports/results.md` or populated `reports/figures/` | Experiment done |
| `Dockerfile` + `serve/app.py` | `mlops` tier present, at least in progress |
| `reports/report.pdf` or `reports/deck.pptx` | Docs done |

You're always told which parts were inferred vs. read from a real state file — and a fresh `.datalab/state.json` gets written once reconstructed, so the *next* `/datalab:work` doesn't have to re-guess.

```
cd examples/iris-classification   # a real, un-managed-by-datalab project
/datalab:work
```

`datalab` then runs a **gap analysis** — pinned dependencies, tests, reproducibility (is there a seed? a config? a provenance record?), data versioning, model tracking, a schema contract, pre-commit hooks, over/underfitting risk in any model already there, exposed PII, vulnerable dependencies — and presents a prioritized list before touching anything.

## 4. Running a full experiment

```
/datalab:run
```

executes `pipeline.py` end to end. What differs by profile:

**Project A (industrial, churn):** one solid cross-validated run. Results are framed around the business decision — e.g., "reduces false declines by 12%," not just "F1 = 0.87." A single robust run is acceptable unless you ask for more.

**Project B (academic, dropout):** training re-runs across **five or more seeds**, and every headline number is reported as **mean ± std (n=5 seeds)** rather than a single number. Comparing two models triggers a paired significance test (paired t-test or Wilcoxon signed-rank across the same folds/seeds) plus an effect size and confidence interval — never just "model A's point estimate was higher."

Both write `reports/results.md`, `reports/figures/*`, and a provenance manifest; both pass through the same code-smoke and model-quality gates — rigor requirements differ by profile, but the underlying quality bar (beat baseline, no leakage, explainability, fairness) does not.

## 5. Generating deliverables

```
/datalab:docs
```

Once `/datalab:run` has produced real results, `document` assembles them into a profile-specific report:

**Project A (industrial)** gets: executive summary → problem → data → approach → results → business impact → next steps, plus a PPTX deck built for a non-technical stakeholder.

**Project B (academic)** gets: abstract → introduction → data → method → experiments → results (tables/figures, with significance tests) → discussion → references/BibTeX, written in an academic register.

Both also get a model card, a data card, and a compliance checklist — those aren't profile-gated, every project gets the governance bundle.

## 6. Adding a tier later

Say Project A started as pure modeling (`base + ml`) and, weeks later, you decide to actually deploy it.

```
/datalab:work I need to deploy this as an API with monitoring
```

The interview (or the gap analysis, for an existing project) sees "deploy" and "monitoring" in your deliverables and adds the `+mlops` tier. `scaffold` is re-invoked to render **only the new tier's files** — `Dockerfile`, `.github/workflows/ci.yml`, `dvc.yaml`, MLflow config, `serve/app.py`, `monitoring/` — and, because scaffolding is non-clobbering, every file you already have (your trained model, your notebook, your `config.yaml`) is left completely untouched. Then the `mlops` skill wires the new files up to your existing model: DVC stages mirror `pipeline.py`'s steps, MLflow starts tracking your training runs, `serve/app.py` loads your actual trained pipeline and exposes `/predict` + `/health`, and `monitoring/` is set up to compare incoming data against your training-data snapshot.

## 7. Academic vs. industrial, side by side

Captured once, in the interview, as `state.json.profile`. It changes **emphasis and report shape** — the underlying quality bar (leakage-safety, the smoke gate, "must beat baseline," explainability, fairness) applies to every project regardless of profile.

| | Academic / research | Industrial / production |
|---|---|---|
| **Priority** | Rigor over speed | Decision-relevance over completeness |
| **Evaluation** | Cross-validation **and** multi-seed repetition (≥5 seeds), every headline number as mean ± std | A single robust CV run is usually enough |
| **Claims** | Require significance tests + confidence intervals + effect sizes before saying "model A beats model B" | A clear variance estimate is usually enough unless a claim is being made for a big decision |
| **Modeling favors** | Interpretable / ablatable configs; every variant logged | Deployable, low-latency models |
| **Deployment (`+mlops`)** | Optional, only if asked | More likely selected; monitoring emphasized |
| **Report template** | Abstract → intro → data → method → experiments → results → discussion → references/BibTeX | Exec summary → problem → data → approach → results → business impact → next steps |
| **Extra artifact** | Ablation table (what happens with a component removed/varied) | PPTX deck for a non-technical stakeholder |
| **Reproducibility** | A first-class deliverable — the numbers must be regenerable from the repo alone | Still recorded (provenance manifest every run), but less often the point of the deliverable |

You can change your mind mid-project — just tell `datalab` explicitly ("actually, let's treat this as academic now") and it updates `state.json.profile`; it won't re-ask on its own once it's captured.

## 8. A full project timeline

What a complete run through every phase looks like, command by command:

| You run | Skill invoked | `state.json` phase change | You get |
|---|---|---|---|
| `/datalab:new ...` | `orchestrator` → `scaffold` | `scaffold: pending → done` | Project skeleton, seeded config, non-clobbering report |
| *(auto-offered)* | `eda` | `eda: pending → done` | Filled notebook, figures, data dictionary |
| `/datalab:work` | `orchestrator` → `modeling` | `modeling: pending → done` | Baseline + trained pipeline(s), experiment leaderboard, passed quality gate |
| `/datalab:run` | `experiment` | `experiment: pending → done` | `reports/results.md`, figures, provenance manifest |
| `/datalab:work` *(if `+mlops`)* | `orchestrator` → `mlops` | `mlops: pending → done` | Docker, CI, DVC, MLflow, FastAPI serving, drift monitoring |
| `/datalab:docs` | `document` | `docs: pending → done` | PDF report, PPTX deck, model/data cards |

At any point, `/datalab:help` shows you exactly where a project sits in this table, and `/datalab:work` always knows what the next unstarted row is.
