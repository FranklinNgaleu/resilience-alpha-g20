"""
import concurrent.futures
import requests

# URL directe de l'endpoint POST /payments (et non l'interface Swagger /docs)
url = "http://localhost:8000/payments"

# Corps de la requête JSON requis par l'API de paiement[cite: 4]
payload = {
    "amount": 1,
    "currency": "EUR"
}

def send_request():
    try:
        # Utilisation de POST et transmission du payload JSON
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
    except Exception as e:
        print("Erreur de connexion")

# Envoi massif en parallèle
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    while True:
        executor.submit(send_request)





import concurrent.futures
import requests

url = "http://localhost:8000/payments"

# Payload malicieux ou corrompu pour provoquer une erreur 500 (ex: type de données invalide)
payload = {
    "amount": "dix",  # Devrait être un entier/float
    "currency": None                     # Valeur nulle inattendue
}

def send_request():
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
    except Exception as e:
        print("Erreur de connexion")

# Envoi du trafic d'anomalie
with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    for _ in range(100):
        executor.submit(send_request)




import concurrent.futures
import requests

url = "http://localhost:8000/payments"

# Payload valide pour que l'API tente de traiter chaque requête lourdement
payload = {
    "amount": 999999,
    "currency": "EUR"
}

def send_request():
    try:
        response = requests.post(url, json=payload, timeout=2)
        print(f"Status: {response.status_code}")
    except requests.exceptions.Timeout:
        print("Timeout - Le serveur ne répond plus (API Down/Saturée)")
    except requests.exceptions.ConnectionError:
        print("Erreur de connexion - Service inaccessible")
    except Exception as e:
        print(f"Erreur: {e}")

# Suture massive avec un grand nombre de threads en boucle infinie
with concurrent.futures.ThreadPoolExecutor(max_workers=500) as executor:
    while True:
        executor.submit(send_request)

"""



import threading
import requests
import time

url = "http://localhost:8000/payments"
loki_url = "http://localhost:3100/loki/api/v1/push"
payload = {
    "amount": 999999,
    "currency": "EUR"
}

def push_to_loki(message):
    try:
        timestamp_ns = str(int(time.time() * 1e9))
        loki_payload = {
            "streams": [
                {
                    "stream": {
                        "compose_service": "payment-service",
                        "level": "error"
                    },
                    "values": [[timestamp_ns, message]]
                }
            ]
        }
        requests.post(loki_url, json=loki_payload, timeout=0.5)
    except Exception:
        pass

def flood():
    while True:
        try:
            # Un timeout très court (0.1s) force l'abandon immédiat si le serveur tousse
            requests.post(url, json=payload, timeout=0.1)
        except requests.exceptions.Timeout:
            print("Timeout (Serveur saturé)")
            push_to_loki("Timeout (Serveur saturé)")
        except requests.exceptions.ConnectionError:
            print("Connexion refusée (API Down)")
            push_to_loki("Connexion refusée (API Down)")
        except Exception:
            pass

# Lancement de centaines de threads permanents non-stop
threads = []
for _ in range(1000): # Augmentez à 2000 ou 5000 si votre machine le supporte
    t = threading.Thread(target=flood)
    t.daemon = True
    threads.append(t)
    t.start()

# Maintient le script en vie
for t in threads:
    t.join()