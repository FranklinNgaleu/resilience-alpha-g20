import json
import urllib.request

base = "http://localhost:8000"
with urllib.request.urlopen(base + "/health") as response:
    assert json.load(response)["status"] == "ok"
request = urllib.request.Request(base + "/payments", data=json.dumps({"amount": "12.50", "currency": "EUR"}).encode(), headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(request) as response:
    payment = json.load(response)
assert payment["status"] == "accepted"
with urllib.request.urlopen(base + "/payments/" + payment["id"]) as response:
    assert json.load(response)["id"] == payment["id"]
print("Smoke test OK:", payment["id"])
