# RAG Assistant

Ce service appartient à la partie IA/Data du projet. Il permet d’interroger la documentation du projet via une recherche intelligente et une réponse contextualisée.

## Principe

Le système utilise un modèle de retrieval basé sur :
- `TfidfVectorizer`
- `cosine_similarity`

Cela permet de faire une recherche sémantique légère sur les documents de la base de connaissances sans dépendre d’un modèle d’intégration lourd.

## Base de connaissances

La base de connaissances est stockée dans `data/knowledge_base.json`.

## Endpoints

- `GET /health`
- `POST /ask` : retourne les meilleurs passages et une réponse synthétique

## Exemple

```json
{
  "question": "Quelles sont les règles de sécurité pour l’API de paiement ?"
}
```

## Lancement

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

## Validation

```bash
python -m pytest tests/test_retriever.py -q
python demo.py
```
