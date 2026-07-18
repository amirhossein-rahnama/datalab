# Iris Classification
- Goal: predict species from 4 measurements
- 150 samples, 3 balanced classes

# Method
- Leakage-safe pipeline: StandardScaler -> LogisticRegression
- Stratified 70/30 split, seed 42

# Results
- Test accuracy 0.911
- 5-fold CV 0.960 +/- 0.039
- Beats dummy baseline (0.333)

# Conclusion
- Simple validated model separates species reliably
