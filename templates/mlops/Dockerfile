# {{project}} — production image for the FastAPI serving stub (serve/app.py).
FROM python:{{python}}-slim AS base

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY serve/ ./serve/
COPY config.yaml pipeline.py ./

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uvicorn", "serve.app:app", "--host", "0.0.0.0", "--port", "8000"]
