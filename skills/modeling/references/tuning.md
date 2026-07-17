# Optuna hyperparameter tuning

Only after Steps 1–4 in `SKILL.md` (baseline beaten, pipeline is leakage-safe). Tuning a leaky
or worse-than-baseline pipeline just wastes compute overfitting harder.

## Step 0 — Context7

`resolve-library-id("optuna")` → `query-docs` for the `create_study`/`Trial` API before
writing the objective — the `suggest_*` API and pruner defaults have changed across Optuna
versions.

## Pattern

```python
import optuna
from sklearn.model_selection import cross_val_score

def objective(trial: optuna.Trial) -> float:
    params = {
        "model__n_estimators": trial.suggest_int("n_estimators", 100, 800),
        "model__max_depth": trial.suggest_int("max_depth", 3, 12),
        "model__learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
    }
    pipeline.set_params(**params)
    scores = cross_val_score(pipeline, X, y, cv=cv, scoring="f1_macro", n_jobs=-1)
    return scores.mean()

study = optuna.create_study(
    direction="maximize",
    sampler=optuna.samplers.TPESampler(seed=SEED),
    pruner=optuna.pruners.MedianPruner(),
)
study.optimize(objective, n_trials=50, show_progress_bar=False)
```

## Rules

- **The objective must reuse the same leakage-safe `Pipeline`** and the same CV strategy as
  the untuned comparison — tuning changes hyperparameters, not the validation protocol.
- **Seed the sampler** (`TPESampler(seed=SEED)`) so the search itself is reproducible, on top
  of seeding the model/CV splitter.
- **Budget**: default to `n_trials=50` or a wall-clock timeout, whichever is more appropriate
  for the dataset size — don't silently run an unbounded search.
- **Log every trial**, not just the best one, to `experiments/` — the leaderboard should show
  the tuning history, not just the winner.
- **Save the winning params** to `params.yaml` (not buried in a notebook cell) so
  `experiment` and `mlops` can load them without re-running the search.
- If the `+mlops` tier is present, Optuna's study storage can point at the same tracking
  backend as MLflow (see `skills/mlops/references/repro.md`) so tuning history survives the
  session.
