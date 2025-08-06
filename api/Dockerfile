# ============================================
# 🏥 Hospitalidée IA API - Dockerfile 
# ============================================
# Image Docker ultra-simple pour déploiement
# Compatible avec tous les VPS et cloud providers

FROM python:3.11-slim

# Métadonnées
LABEL maintainer="Hospitalidée"
LABEL description="API REST pour génération automatique de notes d'avis patients"
LABEL version="1.0.0"

# Variables d'environnement par défaut
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Création utilisateur non-root pour la sécurité
RUN groupadd -r hospitalidee && useradd -r -g hospitalidee hospitalidee

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Création des répertoires nécessaires
RUN mkdir -p logs \
    && chown -R hospitalidee:hospitalidee /app

# Changement vers l'utilisateur non-root
USER hospitalidee

# Port exposé
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Commande par défaut
CMD ["python", "main.py"]