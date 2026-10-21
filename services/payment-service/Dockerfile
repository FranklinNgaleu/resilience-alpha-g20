FROM python:3.12-slim

WORKDIR /app

# Création d'un utilisateur non-root dédié
RUN useradd -u 1000 -m appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Attribution des permissions à l'utilisateur non-root
RUN chown -R appuser:appuser /app

# Basculement vers l'utilisateur sécurisé
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

#FROM python:3.12-slim
#WORKDIR /app
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#COPY app ./app
#EXPOSE 8000
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 