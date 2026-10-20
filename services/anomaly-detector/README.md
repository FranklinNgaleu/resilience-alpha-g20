# Anomaly Detector

Ce service correspond à la partie IA/Data du projet. Il implémente un modèle de machine learning dédié à la détection d’anomalies sur les transactions.

## Modèle ML utilisé

Le modèle principal est un `IsolationForest` de scikit-learn.

Pourquoi ce choix :
- adapté aux données non étiquetées
- performant pour détecter des valeurs extrêmes ou inhabituelles
- léger à déployer dans un environnement de démonstration

Les features utilisées sont :
- montant de la transaction
- heure de la transaction
- jour de la semaine
- week-end / jour ouvré
- fréquence de transaction

## Données de formation

Le modèle est entraîné sur un jeu synthétique localisé dans `data/synthetic_transactions.csv`.

## Points d’entrée

- `GET /health` : vérifie que le service est en ligne
- `POST /detect` : reçoit une transaction et retourne le niveau d’anomalie

## Exemple de requête

```json
{
  "amount": 2250,
  "currency": "EUR",
  "timestamp": "2026-10-20T03:12:00Z",
  "merchant_id": "m-42",
  "frequency": 3.0
}
```

## Sortie

```json
{
  "is_anomaly": true,
  "score": 0.72,
  "severity": "high",
  "model": "IsolationForest"
}
```

## Lancement

```bash
pip install -r requirements.txt
python generate_data.py
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## Validation

```bash
python -m pytest tests/test_model.py -q
python demo.py
```
