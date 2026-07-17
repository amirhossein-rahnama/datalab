# Changelog

All notable changes to datalab are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/).

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
