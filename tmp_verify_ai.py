import sys
from pathlib import Path

root = Path(__file__).resolve().parent

# Validate anomaly detector
anomaly_dir = root / 'services' / 'anomaly-detector'
sys.path.insert(0, str(anomaly_dir))
from app.model import AnomalyDetector
from app.main import app as anomaly_app

ad = AnomalyDetector()
normal = ad.predict({'amount': 18.5, 'timestamp': '2026-10-20T14:00:00Z', 'frequency': 1.0})
anomaly = ad.predict({'amount': 5200, 'timestamp': '2026-10-20T02:00:00Z', 'frequency': 9.0})
print('ANOMALY_APP_TITLE=', anomaly_app.title)
print('NORMAL_RESULT=', normal)
print('ANOMALY_RESULT=', anomaly)

# Validate RAG assistant
rag_dir = root / 'services' / 'rag-assistant'
sys.path.insert(0, str(rag_dir))
from app.retriever import KnowledgeRetriever
from app.main import app as rag_app

retriever = KnowledgeRetriever()
match = retriever.retrieve('sécurité du service de paiement', top_k=1)[0]
print('RAG_APP_TITLE=', rag_app.title)
print('MATCH_TITLE=', match['title'])
