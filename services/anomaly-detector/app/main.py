from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from pydantic import BaseModel, Field

from app.model import AnomalyDetector

app = FastAPI(title="Resilience Alpha - Anomaly Detector", version="0.1.0")
detector = AnomalyDetector()

anomaly_counter = Counter("ml_anomaly_detected_total", "Number of transactions flagged as anomalies")
normal_counter = Counter("ml_anomaly_normal_total", "Number of transactions considered normal")
request_counter = Counter("ml_predictions_total", "Total predictions processed by the anomaly model")


class TransactionInput(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = Field(default="EUR")
    timestamp: datetime | None = None
    merchant_id: str | None = None
    frequency: float = Field(default=1.0, gt=0)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "model": "IsolationForest",
        "service": "anomaly-detector",
    }


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/detect")
def detect(transaction: TransactionInput) -> dict:
    payload = transaction.model_dump()
    result = detector.predict(payload)
    request_counter.inc()
    if result["is_anomaly"]:
        anomaly_counter.inc()
    else:
        normal_counter.inc()
    return result
