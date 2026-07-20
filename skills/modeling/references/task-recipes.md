# Task recipes

Model families to try, default metric(s), and CV strategy per task type. Start from here,
adapt to data characteristics found in `eda` (e.g., swap accuracy for PR-AUC if imbalanced).

| Task type | Try (2–3 families) | Default metric | CV strategy |
|---|---|---|---|
| classification | LogisticRegression, RandomForest/GradientBoosting (or XGBoost if in `stacks.yaml`), a linear SVM or kNN as a contrast | F1/PR-AUC if imbalanced, accuracy only if classes are balanced and cost-symmetric | Stratified k-fold (k=5) |
| regression | Ridge/Lasso, RandomForest/GradientBoosting, ElasticNet | RMSE + MAE + R² (report all three, optimize one) | k-fold (k=5), shuffle |
| clustering | KMeans, DBSCAN/HDBSCAN, Agglomerative | Silhouette + Davies-Bouldin (no labels: use internal metrics); ARI/NMI if any ground-truth labels exist for validation | No CV in the supervised sense — stability check via repeated runs with different seeds/subsamples |
| time-series | Seasonal-naive baseline, ARIMA/ETS, gradient-boosted trees with lag features | MAE/MAPE/RMSE appropriate to scale | **Time-series split only** (`TimeSeriesSplit` or expanding-window) — never shuffle |
| NLP | TF-IDF + linear model as baseline, then a transformer embedding + classifier if `stacks.yaml` includes it | F1 (macro if multi-class), accuracy secondary | Stratified k-fold; watch for near-duplicate documents leaking across folds |
| computer-vision | Simple CNN or transfer-learning head (per `stacks.yaml` extras) | Accuracy/F1 for classification, IoU/mAP for detection/segmentation | Stratified split by class; ensure no augmented-duplicate leakage across train/val |
| recommendation | Popularity baseline, matrix factorization (implicit/explicit), a content-based fallback for cold-start | Precision@k / Recall@k / NDCG@k | User-based split (never leak a user's future interactions into train) |
| production-pipeline | Reuse whichever recipe matches the underlying task type; the distinguishing work is in `mlops`, not the model family | same as underlying task type | same as underlying task type |
| GenAI/RAG | Retriever (embedding model + vector store) + generator (LLM); no sklearn CV loop | ragas: faithfulness, answer-relevance, context-precision | Held-out eval question set, not k-fold |

## Notes

- These are starting points, not a mandate — if `eda` surfaced something specific (heavy
  skew, extreme cardinality, strong seasonality), let that override the default pick.
- Always include at least one **fast/simple** model in the comparison (linear/logistic,
  seasonal-naive, popularity baseline) even when you expect a boosted-tree/deep model to win —
  it's the leaderboard's second reference point after Dummy, and sometimes it *does* win.

## Bundled helpers (import these — they are libraries, not CLIs)

Add `$CLAUDE_PLUGIN_ROOT/scripts` to `sys.path`, then import the helper for your task. All are
leakage-safe and run on core deps (heavy libs are lazy-imported / optional):

| Task | Import | What it gives you |
|---|---|---|
| classification / regression | `from model_zoo import bake_off, best_model, leaderboard_markdown` · `from tune import tune` | ranked multi-model bake-off (LogReg→RF→GBM→SVM→kNN→MLP→XGBoost) + Optuna tuning |
| clustering | `from clustering import auto_k, cluster_metrics, fit_kmeans` | pick k by silhouette; internal metrics (silhouette/DB/CH) |
| anomaly detection | `from anomaly import detect_anomalies` | IsolationForest / LOF, with scores |
| time-series | `from timeseries import chronological_split, seasonal_naive_forecast, moving_average_forecast, forecast_metrics` | no-leak split + baselines + MAE/RMSE/MAPE |
| NLP (text) | `from nlp import train_text_classifier, predict_texts` | TF-IDF + linear baseline (CV) |
| GenAI / RAG | `from vectorstore import VectorStore, build_store_from_texts, embed_texts` | cosine retrieval now; embeddings via the `--genai` extra |
| big data | `from bigdata import count_rows, sample_csv, read_chunked, read_fast` | stratified sampling, chunked reads, polars fast-read |
| deep learning | `from neural import mlp_baseline, torch_tabular_template` | sklearn-MLP baseline (no extra deps) + a PyTorch template for real DL |
