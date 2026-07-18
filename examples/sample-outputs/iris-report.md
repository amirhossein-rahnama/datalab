# Iris Classification — Results Report

## Problem
Classify iris flowers into three species from four measurements.

## Data
150 samples, 4 numeric features, target `species` (3 balanced classes).

## Method
Leakage-safe scikit-learn pipeline: `StandardScaler` then `LogisticRegression`,
fit inside a stratified 70/30 split with a fixed seed (42).

## Results
- Test accuracy: 0.911
- 5-fold cross-validation: 0.960 (std 0.039)
- Dummy baseline: 0.333 — the model clearly beats it
- Fit diagnosis: good fit (no over/underfitting)

## Most important features
petal_width and petal_length dominate, as expected for Iris.

## Conclusion
A simple, well-validated linear model separates the species reliably.
