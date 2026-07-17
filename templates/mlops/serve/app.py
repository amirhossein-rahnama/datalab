"""FastAPI serving stub for {{project}}.

Run locally:  uvicorn serve.app:app --reload
Docker:       see ../Dockerfile (CMD runs this app on port 8000)
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="{{project}} API", version="0.1.0")

_pipeline = None  # lazy-loaded on first request; see _get_pipeline()


class PredictRequest(BaseModel):
    features: dict[str, Any]


class PredictResponse(BaseModel):
    prediction: Any


def _get_pipeline():
    """Load the trained pipeline once and cache it. TODO: confirm the model path."""
    global _pipeline
    if _pipeline is None:
        import joblib

        model_path = Path(__file__).resolve().parents[1] / "models" / "pipeline.joblib"
        _pipeline = joblib.load(model_path)
    return _pipeline


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    import pandas as pd

    pipeline = _get_pipeline()
    df = pd.DataFrame([request.features])
    pred = pipeline.predict(df)[0]
    return PredictResponse(prediction=pred)
