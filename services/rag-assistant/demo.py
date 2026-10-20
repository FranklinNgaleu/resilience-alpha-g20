from app.retriever import KnowledgeRetriever

retriever = KnowledgeRetriever()
questions = [
    "Quelles sont les règles de sécurité pour le service de paiement ?",
    "Que faut-il faire sur les secrets et les mots de passe ?",
    "Comment est organisée la gouvernance du projet ?",
]

for question in questions:
    print("QUESTION:", question)
    print(retriever.retrieve(question, top_k=2))
    print("---")
