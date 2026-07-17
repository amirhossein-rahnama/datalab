# Expected Result

Running `python src/iris_clf/train.py` (or `/datalab:run` against this project) trains a
`StandardScaler → LogisticRegression` pipeline with `seed=42` on a stratified 70/30 train/test
split of the 30-row `data/iris.csv` sample and should achieve **≥0.90 accuracy on the held-out
test set** — the Iris species are close to linearly separable on these four measurements
(setosa in particular is trivially separable from the other two), so a simple regularized
logistic regression typically scores at or near 1.00; treat any run scoring below 0.90 as a
smoke-check failure worth investigating (a broken train/test split, a leakage bug, or a
corrupted `data/iris.csv`) rather than as normal model variance.
