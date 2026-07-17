# Iris Classification — datalab Worked Example

A small, real, end-to-end project used both as a demo of the `datalab` plugin and as a
smoke-test fixture for the plugin's own test suite.

## What's here

```
iris-classification/
├── README.md              # this file
├── config.yaml             # seed, task type, target column, data path
├── data/
│   └── iris.csv            # 30-row sample of the classic Iris dataset (10 per species)
├── notebooks/
│   └── 01_eda.ipynb        # minimal EDA: load the CSV, describe() the features
├── src/iris_clf/
│   ├── __init__.py
│   └── train.py             # leakage-safe StandardScaler + LogisticRegression pipeline
└── EXPECTED.md             # expected result, for smoke-checking
```

## The task

Classic multiclass classification: predict `species` (setosa / versicolor / virginica) from
four numeric measurements (`sepal_length`, `sepal_width`, `petal_length`, `petal_width`).
`config.yaml` pins `task_type: classification`, `target: species`, and `seed: 42` for
reproducibility.

## Reproduce it with datalab

This folder is intentionally already scaffolded, so the fastest way to explore it with the
plugin is to treat it as an **existing** project:

```
cd examples/iris-classification
/datalab:work
```

`/datalab:work` will detect the existing `config.yaml`, `data/`, `notebooks/`, and `src/`
layout (there's no `.datalab/state.json` yet, so it reconstructs state from what it finds on
disk), profile `data/iris.csv`, and propose next steps.

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
python -m pip install pandas scikit-learn
python src/iris_clf/train.py
```

See `EXPECTED.md` for the expected output range.

## Notes

- `data/iris.csv` is a small (30-row) representative sample, not the full 150-row dataset — it's
  meant to be a fast, readable fixture, not a benchmark dataset.
- `src/iris_clf/train.py` fits `StandardScaler` and `LogisticRegression` together inside a
  single `sklearn.pipeline.Pipeline`, and that pipeline is fit only on the training split, so
  no information from the held-out test rows leaks into preprocessing.
