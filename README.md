# PROJECT RESILIENCE-ALPHA — socle de développement

Démonstrateur pédagogique : **données fictives uniquement**. Cette version est un socle de travail, **pas** une plateforme sécurisée ni une reprise autonome complète.

## Pré-requis
- Git, Docker Desktop (WSL2 sur Windows), Docker Compose v2
- Python 3 pour le test local (facultatif)

## Démarrage (PowerShell)
```powershell
Copy-Item .env.example .env
# Modifier .env : choisir deux mots de passe forts différents
 docker compose up -d --build
 docker compose ps
 python tests/smoke_test.py
```
- Page de démarrage : http://localhost:3000
- API FastAPI : http://localhost:8000/docs
- Métriques : http://localhost:8000/metrics
- Prometheus : http://localhost:9090
- Grafana : http://localhost:3001 (identifiants dans `.env`)
- Anomaly Detector : http://localhost:8001/docs
- RAG Assistant : http://localhost:8002/docs
- Ollama : http://localhost:11434

### Lancement complet du projet
```powershell
cd "C:\Users\steph\OneDrive\Desktop\resilience-alpha-g20"
Copy-Item .env.example .env
# Modifier .env avec des mots de passe sécurisés

docker compose up -d --build

docker compose ps
python tests/smoke_test.py
```

### Vérification rapide de la partie IA/Data
```powershell
curl.exe http://localhost:8001/health
curl.exe http://localhost:8002/health
curl.exe -X POST "http://localhost:8001/detect" -H "Content-Type: application/json" --data-raw '{"amount":6500,"currency":"EUR","timestamp":"2026-10-20T02:00:00Z","merchant_id":"ecommerce","frequency":8}'
curl.exe -X POST "http://localhost:8002/ask" -H "Content-Type: application/json" --data-raw '{"question":"Quelles sont les mesures de sécurité à mettre en place pour les transactions ?"}'
```

### Commandes utiles
```powershell
docker compose logs -f rag-assistant
docker compose logs -f anomaly-detector
docker compose up -d --build anomaly-detector rag-assistant ollama
docker compose down
```

Tous les ports publiés sont liés à `127.0.0.1` pour le développement local. Pour la démonstration depuis le PC Attaquant, prévoir **un accès réseau explicitement autorisé et limité** (proxy WAF exposé sur l'interface Hotspot), jamais la base ou Grafana par défaut.

## Commandes utiles
```powershell
 docker compose logs -f payment-service
 docker compose up -d --build payment-service
 docker compose down
```
**Ne pas lancer `docker compose down -v`** sauf si vous voulez supprimer les volumes et les transactions fictives.

## Git en équipe
1. `main` = stable ; `develop` = intégration ; `feature/...` = travail individuel.
2. Une Pull Request vers `develop`, revue par un autre membre.
3. Ne jamais pousser `.env`, secrets ou fichiers de clés.
4. Avant de fusionner : `docker compose up -d --build` puis `python tests/smoke_test.py`.
5. Faire une PR de `develop` vers `main` uniquement après validation collective.

## Responsabilités
- DEV : remplacer le frontend statique par React/Tailwind ; ajouter auth-service, API métier et tests.
- INFRA : Ansible, Loki, provisioning Grafana, réseau et orchestration de remédiation.
- IA : anomaly-detector, Ollama, LangChain, RAG et métriques ML.
- CYBER : WAF, SIEM/SOC, SOPS, scénarios de test strictement autorisés.
- GOUVERNANCE : EBIOS RM, PCA/PRA, NIS2/DORA, documentation et preuves.

## Partie IA & Data – modèle ML
- La partie IA/Data inclut un modèle de machine learning pour la détection d’anomalies sur les transactions.
- Le modèle de référence retenu est un `IsolationForest` de scikit-learn, appliqué sur des features de transaction : montant, heure, jour, week-end et fréquence.
- La couche IA comprend également un module de recherche documentaire basé sur le principe RAG, avec un moteur de retrieval en `TF-IDF + cosine similarity`.
- La génération de réponse est connectée à Ollama via LangChain, avec repli sûr sur le contexte récupéré si le modèle local n’est pas disponible.
- Les métriques ML sont exposées via Prometheus avec les compteurs de prédictions et d’anomalies détectées.
- Les données de démonstration sont synthétiques, sans usage de données réelles, et sont stockées dans les services dédiés à l’IA/Data.
- Les sorties attendues sont des scores d’anomalie, des niveaux de sévérité, des métriques de suivi et des réponses contextuelles sur la documentation projet.

## Contrats d'intégration initiaux
- `GET /health` : 200 si l'API **et** PostgreSQL fonctionnent.
- `POST /payments` : `{ "amount": "12.50", "currency": "EUR" }` ; retourne id + status.
- `GET /payments/{id}` : vérification de persistance.
- `GET /metrics` : métriques Prometheus.
- Convention future : alertes JSON `{ "incident_id": "...", "source": "...", "severity": "...", "timestamp": "..." }` à préciser en équipe.

## Limites connues
- L'API de paiement n'est pas encore authentifiée : **ne pas exposer directement sur un réseau non maîtrisé**.
- Le frontend actuel est une page statique temporaire, pas encore React.
- Pas encore de WAF, Loki, SIEM, ML, RAG, moteur de remédiation ou Ansible opérationnels.
- Les images et dépendances sont fixées à des versions de départ ; revoir et auditer avant toute utilisation autre que pédagogique.
