# Diabetes Regression — datalab Worked Example

A small, real, end-to-end project used both as a demo of the `datalab` plugin and as a
smoke-test fixture for the plugin's own test suite.

## What's here

```
diabetes-regression/
├── README.md              # this file
├── config.yaml             # seed, task type, target column, data path
├── data/
│   └── diabetes.csv        # the full scikit-learn "diabetes" dataset (442 patients)
├── src/diabetes_reg/
│   ├── __init__.py
│   └── train.py             # leakage-safe StandardScaler + Ridge pipeline
└── EXPECTED.md             # expected result, for smoke-checking
```

## The task

Single-target regression: predict `target`, a quantitative measure of diabetes disease
progression one year after baseline, from ten baseline variables (`age`, `sex`, `bmi`, `bp`,
and six blood serum measurements `s1`-`s6`). `config.yaml` pins `task_type: regression`,
`target: target`, and `seed: 42` for reproducibility.

The ten feature columns are scikit-learn's standard `load_diabetes` encoding: each has
already been mean-centered and scaled by the standard deviation times `sqrt(n_samples)`, so
e.g. `age` and `bmi` show up as small floats centered on 0, not raw years or kg/m². The
`StandardScaler` step in the pipeline re-standardizes on the training split only — mostly
redundant given the already-scaled inputs, but it keeps the pipeline shaped the same as any
other feature set (and correct if this example is ever pointed at raw, unscaled data).

## Reproduce it with datalab

This folder is intentionally already scaffolded, so the fastest way to explore it with the
plugin is to treat it as an **existing** project:

```
cd examples/diabetes-regression
/datalab:work
```

`/datalab:work` will detect the existing `config.yaml`, `data/`, and `src/` layout (there's
no `.datalab/state.json` yet, so it reconstructs state from what it finds on disk), profile
`data/diabetes.csv`, and propose next steps.

Run the full experiment end-to-end (train/test split, fit the pipeline, evaluate, plots,
conclusions):

```
/datalab:run
```

Generate documentation and deliverables (report, deck, model/data cards) once results exist:

```
/datalab:docs
```

You can also run the training script directly, without the plugin, to sanity-check the data
and pipeline:

```
python -m pip install pandas numpy scikit-learn
python src/diabetes_reg/train.py
```

See `EXPECTED.md` for the expected output range.

## Result (one line)

`StandardScaler -> Ridge` scores **R2 = 0.4541 / RMSE = 53.78** on the held-out 20% test
split, clearly ahead of the `DummyRegressor(strategy="mean")` baseline's **R2 = -0.0120**.

## Notes

- `data/diabetes.csv` is the full 442-row scikit-learn "diabetes" dataset
  (`sklearn.datasets.load_diabetes(as_frame=True).frame`), not a sample — it's small enough
  already to be a fast, readable fixture.
- `src/diabetes_reg/train.py` fits `StandardScaler` and `Ridge` together inside a single
  `sklearn.pipeline.Pipeline`, and that pipeline is fit only on the training split, so no
  information from the held-out test rows leaks into preprocessing.
- `train.py` also fits a `DummyRegressor(strategy="mean")` baseline on the identical
  train/test split, purely for comparison — it never leaks into the Ridge pipeline's own fit
  or predictions. Comparing against it is what turns "R2 = 0.45" from an arbitrary number into
  evidence the model learned real signal.
