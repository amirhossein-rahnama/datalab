# Iris Classification — Results Report
## Problem
Classify iris flowers into three species from four measurements.
## Data
150 samples, 4 numeric features, target `species` (3 balanced classes).
## Method
Leakage-safe scikit-learn pipeline: `StandardScaler` then `LogisticRegression`,
fit inside a stratified 70/30 split with a fixed seed (42).
## Results
| Metric | Value |
|--------|-------|
| Test accuracy | 0.911 |
| 5-fold CV accuracy | 0.960 (+/- 0.039) |
| Dummy baseline | 0.333 |
| Fit diagnosis | good fit |

![Confusion matrix](figures/confusion_matrix.png)
## Conclusion
A simple, well-validated linear model separates the species reliably, clearing the
baseline by a wide margin with no signs of over/underfitting.
