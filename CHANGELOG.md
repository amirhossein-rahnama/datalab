# Changelog

All notable changes to datalab are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- **Stronger, broader modeling:** a model bake-off (`model_zoo.py`) that CV-ranks many
  algorithms (LogReg → RandomForest → GradientBoosting → SVM → kNN → MLP → XGBoost),
  leakage-safe, plus Optuna hyperparameter tuning (`tune.py`).
- **New task-type helpers:** clustering (auto-k + internal metrics), anomaly detection
  (IsolationForest/LOF), time-series (no-leak split, baselines, MAE/RMSE/MAPE), NLP text
  classification, RAG retrieval (cosine + optional embeddings), big-data (sampling/chunked/
  polars), and a neural baseline (sklearn MLP + a PyTorch template). Imported per task via
  `modeling` + `references/task-recipes.md`; heavy libs (xgboost, polars, torch,
  sentence-transformers, faiss) are optional/lazy.
- More worked examples: regression, time-series, and GenAI/RAG (alongside classification).
- `/datalab:setup` and `/datalab:help`; zero-command install via `settings.json`.

### Changed
- `generate_deck.py` now embeds figures + renders tables (parity with the PDF report).
- `train.py` persists the fitted pipeline to `models/pipeline.joblib`; deps auto-install on
  first use; bundled scripts referenced via `$CLAUDE_PLUGIN_ROOT` so the plugin works installed.

### Testing
- Test suite grown from 61 to **137** — every new helper is covered; optional/heavy libs are
  lazy-imported so the core suite stays light.

## [0.1.0] - 2026-07-17

Initial release — a complete data science project builder for Claude Code.

### Added
- **Commands:** `/datalab:new`, `/datalab:work`, `/datalab:run`, `/datalab:docs`, `/datalab:doctor`.
- **8 skills:** orchestrator (data-aware interview, academic/industrial profiles, new-vs-existing
  routing), scaffold, eda, modeling (leakage-safe pipelines + Optuna), experiment (full end-to-end
  runs), verify (smoke gate + over/underfitting, leakage, imbalance, baseline, error analysis,
  fairness), mlops, document (PDF/PPTX + model/data cards + governance).
- **Adaptive tiered scaffolding** via `templates/` + `stacks.yaml` (base → ML/DL → MLOps, plus a
  GenAI/RAG task type, dashboard, and governance templates); non-clobbering renderer.
- **Bundled scripts:** doctor, profile_data, diagnostics, explain, plots, stats, privacy,
  provenance, sample_data, scaffold_render, generate_report (Markdown→PDF), generate_deck
  (outline→PPTX), nb_to_md.
- **Worked example:** `examples/iris-classification` (doubles as a test fixture).
- **61 unit tests** plus end-to-end validation (scaffold render, tier stacking, deliverables).
