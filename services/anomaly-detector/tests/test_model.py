import sys
from pathlib import Path

SERVICE_DIR = Path(__file__).resolve().parents[1]
if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))

from app.model import AnomalyDetector


def test_normal_transaction_is_not_anomaly():
    detector = AnomalyDetector()
    result = detector.predict({"amount": 18.5, "timestamp": "2026-10-20T14:00:00Z", "frequency": 1.0})
    assert result["is_anomaly"] is False


def test_abnormal_transaction_is_detected():
    detector = AnomalyDetector()
    result = detector.predict({"amount": 5200, "timestamp": "2026-10-20T02:00:00Z", "frequency": 9.0})
    assert result["is_anomaly"] is True


def test_high_risk_transaction_is_tagged_high_severity():
    detector = AnomalyDetector()
    result = detector.predict({"amount": 7800, "timestamp": "2026-10-20T02:10:00Z", "frequency": 8.0})
    assert result["is_anomaly"] is True
    assert result["severity"] == "high"
