# FastAPI serving pattern

## Structure

```
serve/app.py       # FastAPI app: load model once, expose /predict + /health
```

## Pattern

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
import joblib

MODEL = None
MODEL_VERSION = "unset"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global MODEL
    MODEL = joblib.load("models/pipeline.joblib")  # persisted by `modeling`
    yield

app = FastAPI(lifespan=lifespan)

class PredictRequest(BaseModel):
    # mirror schema.py's feature contract — one field per model input feature
    ...

class PredictResponse(BaseModel):
    prediction: float | str
    model_version: str

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": MODEL is not None}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    x = [[*req.model_dump().values()]]
    pred = MODEL.predict(x)[0]
    return PredictResponse(prediction=pred, model_version=MODEL_VERSION)
```

Check Context7 for the current FastAPI lifespan/pydantic-v2 idioms before writing this — the
lifespan-context pattern replaced `@app.on_event("startup")` and pydantic v1→v2 changed
`BaseModel` defaults; don't reach for the older pattern from memory.

## Rules

- **Request schema mirrors `schema.py`** (the pandera contract from the `+ml` tier) — the
  same feature names/types the model was trained on, not a hand-drifted copy.
- **Load the model once at startup**, not per-request — reuse `MODEL` across requests.
- **`/health`** must reflect real state (model loaded, not just "the process is up").
- **Version the response** — `model_version` should trace back to the MLflow registry version
  or the provenance manifest's git commit, so a caller can tell which model answered.
- **Validate input** via pydantic — reject malformed requests with a 422 before they ever
  reach `MODEL.predict`, don't let a bad request 500.
- Load-testing this endpoint is explicitly out of scope (v1) — functional correctness only.
