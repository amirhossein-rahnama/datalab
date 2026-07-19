# datalab examples

Four end-to-end worked examples — one per project shape. Each is a real, runnable project that
also doubles as a test fixture. Point datalab at any of them with `/datalab:work`, or run its
script directly.

| Example | Task type | Dataset | Run it | Result |
|---------|-----------|---------|--------|--------|
| [iris-classification](iris-classification/) | Classification | Iris (150×5) | `python examples/iris-classification/src/iris_clf/train.py` | ~0.91 accuracy |
| [diabetes-regression](diabetes-regression/) | Regression | Diabetes (442×11) | `python examples/diabetes-regression/src/diabetes_reg/train.py` | R² ≈ 0.45, beats mean baseline |
| [sales-forecasting](sales-forecasting/) | Time-series | Synthetic monthly sales (72 mo) | `python examples/sales-forecasting/src/sales_ts/forecast.py` | beats seasonal-naive baseline |
| [rag-knowledge-base](rag-knowledge-base/) | GenAI / RAG | 6-doc SaaS knowledge base | `python examples/rag-knowledge-base/src/rag_demo/run.py` | retrieves the right doc (offline TF-IDF) |

All examples use **core dependencies only** (pandas, numpy, scikit-learn) — no API keys, no
heavy libraries — so they run anywhere after `/datalab:setup`. Each demonstrates a datalab
best practice: leakage-safe pipelines, a baseline comparison, a **chronological** backtest for
time-series (no future leakage), and grounded retrieval for RAG.

The RAG example's **retrieval is real** (TF-IDF); its **generation step is stubbed** — wire in
an LLM via the GenAI tier (`/datalab:setup --genai`) and an API key for real answers.

See [sample-outputs/](sample-outputs/) for the deliverables datalab generates from a project:
a PDF report (with tables + embedded figures), a PPTX deck, and a model card.
