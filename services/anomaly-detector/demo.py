from app.model import AnomalyDetector

model = AnomalyDetector()

samples = [
    {"amount": 18.5, "timestamp": "2026-10-20T14:00:00Z", "frequency": 1.0},
    {"amount": 2400, "timestamp": "2026-10-20T02:00:00Z", "frequency": 6.0},
    {"amount": 8500, "timestamp": "2026-10-21T00:30:00Z", "frequency": 11.0},
]

for sample in samples:
    print(model.predict(sample))
