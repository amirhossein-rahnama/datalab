# Getting Started

A hand-holding walkthrough from "nothing installed" to "first PDF report in hand." It follows one concrete example end to end: predicting customer churn from a CSV. Every command shown is copy-pasteable as-is.

If you just want the fast version, see the [60-second quickstart in the README](../README.md#60-second-quickstart). This guide is the slow, explained version, for a first run.

## Prerequisites

- **Claude Code** installed and working.
- **Python 3.10 or newer** on your machine (check with `python --version` or `python3 --version`). That's the only thing you need pre-installed — everything else, `datalab` installs for you.

## Step 1 — Install the plugin

```
/plugin marketplace add https://github.com/amirhossein-rahnama/datalab
/plugin install datalab
/datalab:setup
```

The first two lines register and install the plugin itself (commands + skills — no Python involved yet). The third line, `/datalab:setup`, installs the small set of Python packages `datalab`'s own tooling needs — the report/deck generator, the doctor check, notebook helpers. You do **not** run `pip install` yourself for this part.

## Step 2 — Check your environment

```
/datalab:doctor
```

This prints a short health report: Python version, which packages are present, and whether the plugin itself is wired up correctly (its manifest file is readable). If anything's missing, it tells you exactly what to run to fix it — usually just re-running `/datalab:setup`. Full explanation of what each check means: [`docs/COMMANDS.md`](COMMANDS.md#datalabdoctor).

## Step 3 — Start a new project

Make a folder, put your data in it, and start the project from inside it:

```
mkdir churn-project
cd churn-project
# copy your customers.csv into this folder, e.g. into data/raw/customers.csv
```

Then:

```
/datalab:new predict which customers are about to churn
```

Because you gave it a data file, Claude runs a profiling pass on `customers.csv` first — row/column counts, per-column types, missing values — and *proposes* a target column and task type from that, rather than asking you to specify everything from scratch. You'll then get a short interview, usually something like:

> **"Is this an academic/research project or an industrial/production one?"**
> You're predicting churn for a real decision → answer **industrial**.
>
> **"Looks like classification, target = `churn` — correct?"**
> Claude inferred this from your data. Confirm, or correct it.
>
> **"What do you need out of this?"** *(pick any number: notebook / trained model / PDF report / PPTX deck / model & data cards / dashboard / production API)*
> For a first run, pick **notebook, trained model, PDF report**.

Environment (Python version, package manager) is confirmed rather than asked outright — `datalab` suggests sensible defaults (Python 3.11, `uv`) unless your folder already pins something else. Only questions it genuinely can't answer from your data or your folder get asked at all — a data-aware project like this is often just the two or three questions above.

## Step 4 — See what got created

Because your task type is classification (a modeling task), `datalab` renders the `base` tier plus `+ml`:

```
churn-project/
├── README.md
├── requirements.txt          # this project's own dependencies (pandas, scikit-learn, ...)
├── tasks.py                  # setup / lab / test / lint / report / run — no `make` needed
├── config.yaml                # seed + data paths
├── pipeline.py                 # end-to-end runner: load -> validate -> features -> train -> evaluate
├── schema.py                    # pandera data-contract for customers.csv
├── params.yaml                   # hyperparameters, tracked separately from config.yaml
├── configs/                       # per-experiment config variants
├── experiments/                    # one record per training run
├── data/{raw,interim,processed,external}/
├── notebooks/01_eda.ipynb
├── src/churn_project/{config,data,features,models,visualization}/
├── tests/test_smoke.py
├── reports/figures/
└── .datalab/state.json            # tracks what phase this project is in
```

You'll see a report distinguishing **added** from **skipped** files — `skipped` just means a file already existed and `datalab` left it alone (see [non-clobbering scaffolding](ARCHITECTURE.md#the-tier-system) — it never overwrites your work). Right after this, a smoke check runs automatically: your new package has to import cleanly, `pytest` has to pass on the starter test, and the starter notebook has to execute top to bottom. You won't be told the project is ready until that's green.

## Step 5 — Let it fill in the EDA

Right after scaffolding, Claude offers to run exploratory data analysis immediately — say yes (or if you skipped it, ask any time, or run `/datalab:work`). This fills `notebooks/01_eda.ipynb` with a real analysis of `customers.csv`: shape and dtypes, missingness, duplicate rows, class balance for `churn`, feature distributions, a correlation heatmap, outlier flags, and — importantly — a **leakage screen**, checking for any column that's suspiciously predictive or that couldn't actually be known at prediction time. It closes with a written findings cell and writes `reports/data_dictionary.md` (one row per column: type, missingness, and role — feature / target / id / drop-candidate).

## Step 6 — Build a model

Run:

```
/datalab:work
```

`datalab` reads `.datalab/state.json`, sees EDA is done and modeling is next, and starts building. It always fits a **naive baseline first** (a `DummyClassifier` under the same evaluation protocol) — that number is the floor everything else has to beat. Then it builds a real pipeline with every data-dependent step (scaling, encoding, imputation) wrapped inside a single `scikit-learn` `Pipeline`, fit only within cross-validation folds — never on the whole dataset up front — so the reported score can't be inflated by leakage. It tries 2–3 model families, logs each as a row in an experiment leaderboard, and only then (optionally) tunes the best one.

Before it reports this phase done, it hands off to the **model-quality gate**: does the model beat the baseline, is there any sign of overfitting or leakage, is the cross-validation setup right for this task, is `churn` imbalanced enough that plain accuracy would be misleading, does the error analysis show a pattern, is there an explainability read-out (which features actually drove predictions), and a fairness check across any sensitive-looking columns. Any failure comes back as a concrete, specific finding — not a bare "failed" — and gets fixed before moving on.

## Step 7 — Run the full experiment

```
/datalab:run
```

This executes `pipeline.py` end to end for the record: load → validate against `schema.py` → preprocess → train (with cross-validation) → evaluate → diagnostics → explainability/fairness → figures → a written results file at `reports/results.md`. Because this project is `industrial`, one solid cross-validated run is enough (an `academic` profile would instead re-run training across 5+ seeds and report every headline number as mean ± std). Every run also writes a provenance record — seeds, library versions, a hash of your data file, and the git commit if you're in a repo — so the result is traceable later.

## Step 8 — Generate your first PDF report

```
/datalab:docs
```

This gathers everything the earlier phases produced — the notebook, the results, the figures, the diagnostics, the provenance record — and assembles them into `reports/report.md`, then renders that to:

- **`reports/report.pdf`** — since this project is `industrial`, it follows the industrial template: executive summary → problem → data → approach → results → business impact → next steps.
- **`reports/deck.pptx`** — a condensed 6–12 slide version of the same report.
- **Model card and data card** — filled in from your actual metrics, explainability output, and fairness check, not placeholder text.

Nothing is reported finished until each file is confirmed to exist and be non-empty. Open `reports/report.pdf` — that's your first `datalab` deliverable, generated entirely from real numbers your project produced.

## What just happened

You went from a folder with one CSV in it to: a seeded, reproducible project skeleton; a real EDA with a data dictionary; a leakage-safe trained model that beat a baseline and passed a quality gate; a full experiment run with figures and provenance; and a PDF report, slide deck, and model/data cards — all without writing a single line of boilerplate yourself, and with every step checked before being called "done."

## Where to go next

| If you want to... | Read |
|---|---|
| See the full command reference | [`docs/COMMANDS.md`](COMMANDS.md) |
| See more scenarios (existing projects, adding a tier later, academic vs. industrial) | [`docs/WORKFLOWS.md`](WORKFLOWS.md) |
| Understand how the pieces fit together | [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) |
| Fix something that isn't working | [`docs/TROUBLESHOOTING.md`](TROUBLESHOOTING.md) |
| Get a quick answer to a specific question | [`docs/FAQ.md`](FAQ.md) |
