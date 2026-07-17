# Leakage-safe pipeline pattern

## The rule

Any transformation that **learns from data** (mean/std for scaling, category encodings,
imputation values, feature-selection scores, target encoding) must be fit **only on the
training fold**, inside the CV loop — never on the full dataset before splitting.

## Pattern (tabular classification/regression)

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.linear_model import LogisticRegression

numeric_features = [...]
categorical_features = [...]

preprocess = ColumnTransformer([
    ("num", Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ]), numeric_features),
    ("cat", Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore")),
    ]), categorical_features),
])

pipeline = Pipeline([
    ("preprocess", preprocess),
    ("model", LogisticRegression(max_iter=1000, random_state=SEED)),
])

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
scores = cross_validate(pipeline, X, y, cv=cv, scoring=["f1_macro", "roc_auc_ovr"],
                         return_train_score=True)
```

`cross_validate` refits `preprocess` fresh inside every fold — that's what makes this
leakage-safe. `pipeline.fit(X_train, y_train)` once more on the full training set only
happens *after* CV has already told you the honest estimate, for the final artifact you
persist.

## Common leakage traps (all of these fail the `verify` gate)

1. **Fit-before-split**: calling `scaler.fit(X)` on the whole dataset, then splitting.
   Fix: put the scaler inside the `Pipeline`.
2. **Target encoding fit on all data**: category → target-mean encodings computed before CV.
   Fix: use a CV-aware target encoder, or compute it inside a custom `Pipeline` step with
   `fit`/`transform` semantics.
3. **Feature selection before split**: picking "top-k correlated with target" features using
   the whole dataset. Fix: wrap selection in the pipeline (e.g., `SelectKBest` as a step).
4. **Time-series shuffling**: using `KFold(shuffle=True)` or a random train/test split on
   temporal data lets the model see the future. Fix: `TimeSeriesSplit` / expanding window,
   never shuffle.
5. **Duplicate/near-duplicate rows across train and test** (common in NLP/CV after
   augmentation, or tabular data with repeated entities). Fix: group-aware splitting
   (`GroupKFold` keyed by entity/document/user id).
6. **Post-outcome features**: a column that's only known *after* the target is realized
   (flagged in `eda`'s data dictionary) — must be dropped, not just deprioritized.
7. **Global imputation statistics**: filling NaNs with the full-dataset mean/median before
   splitting. Fix: `SimpleImputer` inside the pipeline, same as scaling.

## Non-tabular notes

- **NLP**: `TfidfVectorizer` fit inside the pipeline too — vocabulary/IDF weights are
  data-derived and must not leak from val/test into train.
- **Time-series**: lag/rolling features computed per-fold using only past data relative to
  that fold's cutoff — recompute inside `TimeSeriesSplit`, don't precompute globally.
- **GenAI/RAG**: no CV loop, but the equivalent leakage trap is eval questions whose answers
  appear verbatim in the retrieval corpus used to *build* the prompts/few-shot examples —
  keep the eval set held out from prompt engineering.
