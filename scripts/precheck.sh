#!/bin/bash
echo '=== 1. État des conteneurs ==='
docker compose ps

echo '=== 2. Services ==='
curl -sf http://localhost:9090/-/healthy >/dev/null && echo '[OK] Prometheus' || echo '[ERREUR] Prometheus'
curl -sf http://localhost:3001/api/health >/dev/null && echo '[OK] Grafana' || echo '[ERREUR] Grafana'
curl -sf http://localhost:3100/ready >/dev/null && echo '[OK] Loki' || echo '[INFO] Loki absent ou pas prêt'
curl -sf http://localhost:8000/health >/dev/null && echo '[OK] API' || echo '[ERREUR] API (adapter le chemin /health)'

echo '=== 3. Cibles Prometheus ==='
curl -s http://localhost:9090/api/v1/targets | jq -r '.data.activeTargets[] | [.labels.job, .health] | @tsv'

echo '=== 4. Ports publiés hors loopback ==='
docker compose ps --format '{{.Service}} {{.Ports}}' | grep -E '0[.]0[.]0[.]0|:::' || echo 'Aucun port public'
