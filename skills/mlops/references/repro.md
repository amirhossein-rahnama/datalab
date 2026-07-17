# Reproducibility backbone: DVC + seeds + provenance

## DVC pipeline

`dvc.yaml` stages should mirror `pipeline.py` 1:1 so there's exactly one definition of the
pipeline shape, not two that can drift apart:

```yaml
stages:
  data:
    cmd: python -m src.<pkg>.data.load --config config.yaml
    deps: [src/<pkg>/data/load.py, data/raw]
    outs: [data/interim]
  preprocess:
    cmd: python -m src.<pkg>.features.build --config config.yaml
    deps: [src/<pkg>/features, data/interim]
    outs: [data/processed]
  train:
    cmd: python -m src.<pkg>.models.train --config config.yaml --params params.yaml
    deps: [src/<pkg>/models/train.py, data/processed, params.yaml]
    outs: [models]
    metrics: [experiments/metrics.json]
  evaluate:
    cmd: python -m src.<pkg>.models.predict --config config.yaml --evaluate
    deps: [src/<pkg>/models/predict.py, models, data/processed]
    metrics: [reports/results.json]
```

`dvc repro` should reproduce the same result `pipeline.py`/`tasks.py run` produces — if they
diverge, that's a bug to fix, not two valid paths.

## Seeds + config

Every stage that has any randomness reads `SEED` from `config.yaml` — never a bare literal
buried in a training script. Multi-seed academic runs (from `experiment`) are a *sweep* over
this same config, not a separate code path.

## Provenance chain

`scripts/provenance.py` writes, per result: seed(s) used, resolved library versions (from the
active environment, not just `requirements.txt`'s version *ranges*), data hash (of the input
under DVC's tracking, or a content hash if DVC isn't tracking that path yet), and the git
commit. This manifest is what lets someone regenerate the exact reported number later — treat
missing provenance on a "final" result as a `verify` smoke-gate-level defect, not optional.

## MLflow tracking + registry

- **Tracking**: log params, metrics, and artifacts (model file, key figures) for every
  training run — from `modeling`'s iterations and `experiment`'s full runs alike, tagged with
  which phase produced them.
- **Registry**: register the winning pipeline as a versioned model; promote it (e.g., to a
  "staging"/"production" alias) only after it passed `verify`'s model-quality gate — never
  register a model that hasn't cleared the gate.
- If Optuna tuning ran (`skills/modeling/references/tuning.md`), point its study storage at
  the same tracking backend so the tuning history and the final registered model are
  traceable to the same run.
