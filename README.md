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
