---
description: "Install datalab's Python dependencies (core by default; --full / --genai for optional tiers)"
---

# datalab setup

Install datalab's Python dependencies for the user so they never have to type `pip` themselves.

## Steps

1. Locate the plugin root (the directory containing `.claude-plugin/plugin.json`).
2. Run: `python scripts/setup.py` from the plugin root. This installs only the CORE
   dependencies needed for scaffolding, EDA, modeling, verification, and PDF/PPTX docs
   (`scripts/requirements.txt`) — enough to start any project with near-zero setup.
3. If the user's goal touches explainability, data validation, hyperparameter tuning, drift
   monitoring, dependency scanning, or MLOps serving/tracking (SHAP, pandera, Optuna,
   Evidently, pip-audit, DVC, MLflow, FastAPI/uvicorn), re-run with
   `python scripts/setup.py --full` to also install `scripts/requirements-optional.txt`.
4. If the user's goal is the GenAI/RAG task type (LangChain, ChromaDB, sentence-transformers,
   ragas), re-run with `python scripts/setup.py --genai` to also install
   `scripts/requirements-genai.txt`. Combine both with `--full --genai` to install everything.
5. Read the command's output and report back to the user:
   - which dependency group(s) installed successfully
   - any group that failed, with the exact `pip install -r ...` command to retry by hand
6. Default to core-only unless the user's task clearly needs an optional or GenAI feature —
   don't preemptively install heavy dependencies nobody asked for.
7. Suggest `/datalab:doctor` afterward to verify the environment is healthy.

Arguments (optional: hints about which tier to install, e.g. "full" or "genai"): $ARGUMENTS
