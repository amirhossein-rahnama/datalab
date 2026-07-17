# What each tier renders

Source of truth is `templates/stacks.yaml` (task-type → package set + recipe); this is the
human-readable map of what lands on disk per tier, for sanity-checking scaffold output.

## Base (always)

```
README.md
requirements.txt              # + optional pyproject.toml
tasks.py                      # setup / lab / test / lint / report / run — no `make`
config.yaml                   # + SEED
pipeline.py                   # end-to-end runner, load→...→evaluate
.pre-commit-config.yaml       # ruff + nbstripout
.gitignore
.env.example
data/{raw,interim,processed,external}/
notebooks/01_eda.ipynb
src/<pkg>/{config,data,features,models,visualization}/
tests/test_smoke.py
reports/figures/
.datalab/state.json
```

Base alone is enough for `task_type = eda-only`.

## +ML/DL (modeling task types)

Adds, on top of base:
```
schema.py                     # pandera data-contract for the target dataset
src/<pkg>/models/{train,predict}.py
params.yaml                   # hyperparameters, tracked separately from config.yaml
configs/                      # per-experiment config variants
experiments/                  # one record per run (params, metrics, seed)
```
Extra deps come from `stacks.yaml` keyed by `task_type` — e.g. `+xgboost` for tabular
classification/regression, `+torch` or `+tensorflow` if the recipe calls for deep learning;
NLP/CV recipes pull their own extras (e.g. transformers, torchvision) the same way.

## +MLOps (deploy/production/monitoring deliverables)

Adds:
```
Dockerfile
.dockerignore
.github/workflows/ci.yml
dvc.yaml
mlflow/                       # tracking + registry config
serve/app.py                  # FastAPI serving
monitoring/                   # Evidently drift detection
```
See `skills/mlops/SKILL.md` and its references for how these get wired up (this skill only
renders the skeleton; the `mlops` skill fills in the logic).

## GenAI/RAG (task_type = genai-rag)

Adds:
```
rag/
  loader.py                   # document ingestion
  chunker.py
  embeddings.py
  vectorstore.py              # Chroma/FAISS
  retriever.py
  generator.py
eval/                         # ragas: faithfulness, answer-relevance, context-precision
prompts/
```
Plus LLM cost/latency logging hooks in `pipeline.py`. Context7 must be consulted for current
SDK APIs (embeddings/vector-store/LLM clients change fast) — that happens in the `modeling`
or a GenAI-specific build step, not here; scaffold only lays out the directories and stub
files.

## Dashboard deliverable

Adds `templates/dashboard/app.py` (Streamlit or Gradio, per `stacks.yaml` default) wired to
load the trained model/pipeline once it exists. If modeling hasn't run yet, the stub still
renders with a "no model yet" placeholder — don't block scaffold on modeling being done.

## Non-clobber contract

`scaffold_render.py` must never overwrite an existing file. Directories are created as
needed; individual files that already exist are left untouched and reported as "skipped".
This is what makes `scaffold` safe to re-run when a tier is added later to an existing
project (e.g., adding `+mlops` after the model already exists).
