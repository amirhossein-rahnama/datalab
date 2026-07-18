# FAQ

## Do I need to memorize the seven commands, or can I just talk normally?

You can just talk normally. Every command is backed by a **skill**, and skills auto-activate from plain English too — "help me start a classification project," "run the experiment," "write this up as a report" will each trigger the right skill on their own. The commands exist so there's always an exact, discoverable way to trigger each phase, especially useful when you want to be explicit (e.g., you specifically want `/datalab:run`, not a broader "figure out what's next"). If you ever forget what's available, run `/datalab:help`.

## Does datalab work offline?

No — running any `/datalab:*` command or triggering a skill requires Claude Code itself to be running, which needs network access to reach the model. What *doesn't* require network access beyond that: your data stays local (the analysis scripts — `profile_data.py`, `diagnostics.py`, and so on — run on your machine), and once a project is scaffolded, its own code (`pipeline.py`, a trained model, `tasks.py run`) executes exactly like any local Python project, with no plugin-specific network calls of its own. The one coding-time exception is Context7 lookups (skills check current library docs before generating code using a library) and, if you build a GenAI/RAG project, whatever LLM API your own `generate.py` calls — that's your own integration, not something the plugin bundles.

## Can I use my own data?

Yes — that's the default path. Point `/datalab:new` at your data (a file path or a glob), or just have it sitting in the folder already and `datalab` will find and profile it before asking you anything. See [Workflow 1](WORKFLOWS.md#1-new-project-data-in-hand).

## What if I already have a project that wasn't started with datalab?

Run `/datalab:work` inside it. If there's no `.datalab/state.json` but the project looks real (a `.git`, a `src/`, a `pipeline.py`, data already present), `datalab` reconstructs a best-effort state by reading what's on disk, tells you plainly what it inferred versus knows for sure, runs a gap analysis, and proposes prioritized next steps before touching anything. See [Workflow 3](WORKFLOWS.md#3-picking-up-an-existing-or-unmanaged-project).

## Academic vs. industrial — which do I pick, and can I change later?

Pick **academic** if you need statistical rigor for its own sake — multi-seed repetition, significance tests, an ablation table, a paper-shaped report (this is also the right choice for a class project or thesis work, not just published research). Pick **industrial** if the point is a business decision — a single robust run is usually enough, and the report leads with business impact rather than a raw metric. The underlying quality bar (no leakage, must beat baseline, explainability, fairness) is identical either way — the profile only changes emphasis and report shape. You can switch later by telling Claude explicitly; it won't re-ask or flip on its own once it's captured your answer. Full comparison: [Workflow 7](WORKFLOWS.md#7-academic-vs-industrial-side-by-side).

## Is datalab autonomous — will it just start training models and deploying things on its own?

No. `datalab` is **interactive and guided by design** — it asks before it acts and keeps you in control at every phase transition; it is explicitly not an unattended autonomous agent. The interview happens before scaffolding, gap-analysis next-steps are presented before anything is touched on an existing project, and deploying is only ever something you asked for as a deliverable.

## Will it overwrite files I've already written?

No. Scaffolding is **non-clobbering** by contract — it never overwrites a file that already exists on disk, even when re-run or when a new tier is added later. You'll see an explicit **added vs. skipped** report; skipped means "this already existed, I left it alone," not a failure.

## What Python version and operating systems does it support?

Python 3.10 or newer. Windows, macOS, and Linux equally — the plugin's own tooling is pure Python with no system-level dependencies (no LaTeX, no pandoc, nothing to compile). See [Requirements & dependencies](../README.md#requirements--dependencies) and, if you're on Windows, [Windows-specific issues](TROUBLESHOOTING.md#windows-specific-issues).

## What if I don't have a dataset yet?

Answer "I don't have one yet" at the data question in the interview. `scaffold` will generate a synthetic sample dataset shaped for your chosen task type, so the whole pipeline — EDA, a trained baseline, a rendered report — works end to end immediately. Swap in your real data later and run `/datalab:work` to pick up where you left off. See [Workflow 2](WORKFLOWS.md#2-new-project-no-data-yet).

## What's the difference between `/datalab:run` and `/datalab:work`?

`/datalab:work` is the general "what should happen next on this project?" command — it can trigger scaffolding gaps, EDA, modeling, experiment, MLOps, or docs, depending on what's not done yet. `/datalab:run` is narrower and more specific: it always means "execute the full experiment pipeline end-to-end right now" (load → validate → preprocess → train → evaluate → diagnostics → figures → results), assuming a modeling pipeline already exists. Use `/datalab:work` when you're not sure what's next; use `/datalab:run` when you specifically want a fresh, complete, recorded run. See [`docs/COMMANDS.md`](COMMANDS.md).

## Can I use it for deep learning, NLP, computer vision, or GenAI — or just classic ML?

All of the above. The task-type list covers classification, regression, clustering, time-series, NLP, computer vision, recommendation, production pipelines, and GenAI/RAG — each with its own recipe (model families, default metric, CV strategy) and, where relevant, its own extra packages (PyTorch/TensorFlow for deep learning, spaCy/transformers for NLP, embeddings + a vector store + `ragas` for RAG). A GenAI/RAG project is the one case that calls out to an external LLM API directly (in the scaffolded `generate.py`) — that's your own API key and cost to manage, the plugin only scaffolds the integration point.

## How is this different from just asking Claude to "build me a model" without the plugin?

You'd have to remember, and explicitly ask for, every step yourself, every time: fit a baseline first, put every preprocessing step inside a `Pipeline` so nothing leaks across CV folds, check for class imbalance before trusting accuracy, run an explainability pass, check for a fairness gap, record the seed and library versions, and write it all up consistently. `datalab` bakes that checklist into the workflow itself — it's the same Claude, with a project-manager skill in front of it that won't let a phase report "done" until it's actually cleared that bar, and that leaves you with a consistent, resumable, documented project structure across every project you use it on instead of a one-off notebook only you know the history of.
