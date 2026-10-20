
import os
import sys
import uuid
import requests

AUTH_URL = os.getenv("AUTH_URL", "http://localhost:8001")
PAYMENT_URL = os.getenv("PAYMENT_URL", "http://localhost:8000")


def main():
    email = os.getenv("DEMO_EMAIL", "demo@resilience.local")
    password = os.getenv("DEMO_PASSWORD")

    if not password:
        sys.exit("ERREUR : variable DEMO_PASSWORD manquante")

    # 1. Authentification
    login = requests.post(
        f"{AUTH_URL}/auth/login",
        json={"email": email, "password": password},
        timeout=10,
    )
    login.raise_for_status()

    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("OK : authentification JWT")

    # 2. Refuser les paiements sans JWT
    unauthorized = requests.post(
        f"{PAYMENT_URL}/payments",
        json={"amount": "10.00", "currency": "EUR"},
        timeout=10,
    )
    assert unauthorized.status_code == 401, (
        f"Paiement sans JWT : HTTP {unauthorized.status_code}"
    )

    print("OK : paiement sans JWT refuse")

    # 3. Creer un paiement authentifie
    created = requests.post(
        f"{PAYMENT_URL}/payments",
        headers=headers,
        json={"amount": "25.50", "currency": "EUR"},
        timeout=10,
    )
    created.raise_for_status()
    assert created.status_code == 201

    payment = created.json()
    payment_id = payment["id"]
    uuid.UUID(payment_id)

    assert payment["status"] == "accepted"
    print(f"OK : paiement cree ({payment_id})")

    # 4. Recuperer le paiement
    fetched = requests.get(
        f"{PAYMENT_URL}/payments/{payment_id}",
        headers=headers,
        timeout=10,
    )
    fetched.raise_for_status()

    assert fetched.json()["id"] == payment_id
    print("OK : paiement retrouve")

    # 5. Verifier l'historique
    history = requests.get(
        f"{PAYMENT_URL}/payments",
        headers=headers,
        params={"limit": 100},
        timeout=10,
    )
    history.raise_for_status()

    assert isinstance(history.json(), list)
    print("OK : historique accessible")

    print("\nTOUS LES TESTS SONT PASSES")


if __name__ == "__main__":
    main()
