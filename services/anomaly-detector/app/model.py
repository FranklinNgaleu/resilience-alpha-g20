from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_COLUMNS = ["amount", "hour", "day_of_week", "is_weekend", "frequency"]


class AnomalyDetector:
    def __init__(self, data_path: str | None = None):
        self.data_path = Path(data_path) if data_path else Path(__file__).resolve().parents[1] / "data" / "synthetic_transactions.csv"
        self.pipeline: Pipeline | None = None
        self.fit()

    def fit(self) -> None:
        if not self.data_path.exists():
            raise FileNotFoundError(f"Training dataset not found: {self.data_path}")

        df = pd.read_csv(self.data_path)
        missing = [column for column in FEATURE_COLUMNS if column not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        X = df[FEATURE_COLUMNS].copy()
        X["frequency"] = X["frequency"].astype(float)
        X["amount"] = X["amount"].astype(float)
        X["hour"] = X["hour"].astype(float)
        X["day_of_week"] = X["day_of_week"].astype(float)
        X["is_weekend"] = X["is_weekend"].astype(float)

        self.pipeline = Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("model", IsolationForest(contamination=0.12, random_state=42, n_estimators=250)),
            ]
        )
        self.pipeline.fit(X)

    def _build_features(self, payload: dict) -> pd.DataFrame:
        amount = float(payload.get("amount", 0.0))
        timestamp = payload.get("timestamp")
        hour = 0.0
        day_of_week = 0.0
        is_weekend = 0.0
        frequency = float(payload.get("frequency", 1.0))

        if timestamp is not None:
            import datetime as dt

            if isinstance(timestamp, str):
                timestamp_value = pd.to_datetime(timestamp)
            else:
                timestamp_value = pd.Timestamp(timestamp)
            hour = float(timestamp_value.hour)
            day_of_week = float(timestamp_value.weekday())
            is_weekend = float(1 if timestamp_value.weekday() >= 5 else 0)

        return pd.DataFrame(
            [{
                "amount": amount,
                "hour": hour,
                "day_of_week": day_of_week,
                "is_weekend": is_weekend,
                "frequency": frequency,
            }]
        )

    def predict(self, payload: dict) -> dict:
        if self.pipeline is None:
            raise RuntimeError("Model is not trained.")

        features = self._build_features(payload)
        prediction = self.pipeline.predict(features[FEATURE_COLUMNS])[0]
        decision_score = self.pipeline.decision_function(features[FEATURE_COLUMNS])[0]
        score = max(0.0, float(-decision_score))

        is_anomaly = bool(prediction == -1)
        amount = float(features["amount"].iloc[0])
        hour = float(features["hour"].iloc[0])
        frequency = float(features["frequency"].iloc[0])

        if is_anomaly and amount >= 6000 and frequency >= 7 and (hour <= 3 or hour >= 22):
            severity = "high"
        elif is_anomaly and (
            amount >= 2500
            or frequency >= 5
            or (hour <= 3 and is_weekend == 1)
            or (hour >= 22 and amount >= 1800)
        ):
            severity = "medium"
        else:
            severity = "low"

        return {
            "is_anomaly": is_anomaly,
            "score": round(score, 4),
            "severity": severity,
            "model": "IsolationForest",
            "features": {
                "amount": float(features["amount"].iloc[0]),
                "hour": float(features["hour"].iloc[0]),
                "day_of_week": float(features["day_of_week"].iloc[0]),
                "is_weekend": float(features["is_weekend"].iloc[0]),
                "frequency": float(features["frequency"].iloc[0]),
            },
        }
