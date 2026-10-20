from __future__ import annotations

import csv
from pathlib import Path

rows = []

# Transactions normales
for i in range(1, 121):
    amount = 10 + (i % 30) * 4 + (i % 5) * 1.5
    hour = (8 + i) % 24
    day = i % 7
    weekend = 1 if day in (5, 6) else 0
    frequency = 1 + (i % 4)
    rows.append({
        "amount": round(amount, 2),
        "hour": hour,
        "day_of_week": day,
        "is_weekend": weekend,
        "frequency": frequency,
        "label": "normal",
    })

# Transactions anormales
anomalies = [
    (3500, 2, 1, 0, 7),
    (4800, 1, 6, 1, 9),
    (6200, 0, 3, 0, 11),
    (7900, 3, 4, 0, 12),
    (9200, 0, 0, 0, 14),
    (11500, 1, 2, 0, 18),
    (6400, 4, 5, 1, 10),
    (5200, 2, 6, 1, 8),
    (8800, 3, 2, 0, 13),
    (15000, 0, 1, 0, 20),
]

for amount, hour, day, weekend, freq in anomalies:
    rows.append({
        "amount": round(amount, 2),
        "hour": hour,
        "day_of_week": day,
        "is_weekend": weekend,
        "frequency": freq,
        "label": "anomaly",
    })

output = Path(__file__).resolve().parent / "data" / "synthetic_transactions.csv"
output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["amount", "hour", "day_of_week", "is_weekend", "frequency", "label"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Dataset generated: {len(rows)} rows -> {output}")
