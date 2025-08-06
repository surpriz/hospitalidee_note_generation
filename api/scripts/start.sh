#!/bin/bash
# ============================================
# 🏥 Hospitalidée IA API - Script de démarrage
# ============================================
# Démarre l'API (avec ou sans Docker)

set -e

echo "🚀 Démarrage Hospitalidée IA API..."

# Vérification du fichier .env
if [ ! -f ".env" ]; then
    echo "❌ Fichier .env manquant"
    echo "Copiez config.env.example vers .env et configurez votre clé API Mistral"
    exit 1
fi

# Vérification de la clé API
if grep -q "your_mistral_api_key_here" .env; then
    echo "❌ Clé API Mistral non configurée dans .env"
    echo "Éditez le fichier .env et remplacez 'your_mistral_api_key_here' par votre vraie clé"
    exit 1
fi

# Fonction pour vérifier si une commande existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Option 1: Docker Compose (recommandé)
if command_exists docker-compose && [ -f "docker-compose.yml" ]; then
    echo "🐳 Démarrage avec Docker Compose..."
    docker-compose up -d
    
    echo "⏳ Attente démarrage (15s)..."
    sleep 15
    
    if curl -f -s http://localhost:8000/health > /dev/null; then
        echo "✅ API démarrée avec succès !"
        echo ""
        echo "📊 Accès:"
        echo "  • API: http://localhost:8000"
        echo "  • Documentation: http://localhost:8000/docs"
        echo ""
        echo "🔧 Commandes:"
        echo "  • Logs: docker-compose logs -f"
        echo "  • Arrêt: docker-compose down"
    else
        echo "❌ Erreur de démarrage, vérifiez les logs:"
        docker-compose logs
        exit 1
    fi

# Option 2: Docker simple
elif command_exists docker && [ -f "Dockerfile" ]; then
    echo "🐳 Démarrage avec Docker..."
    
    # Build si nécessaire
    if ! docker images | grep -q hospitalidee-ia-api; then
        echo "🏗️ Construction de l'image..."
        docker build -t hospitalidee-ia-api .
    fi
    
    # Arrêt conteneur existant
    docker stop hospitalidee-ia-api 2>/dev/null || true
    docker rm hospitalidee-ia-api 2>/dev/null || true
    
    # Démarrage
    docker run -d \
        --name hospitalidee-ia-api \
        --env-file .env \
        -p 8000:8000 \
        hospitalidee-ia-api
    
    echo "⏳ Attente démarrage (15s)..."
    sleep 15
    
    if curl -f -s http://localhost:8000/health > /dev/null; then
        echo "✅ API démarrée avec succès !"
        echo ""
        echo "📊 Accès:"
        echo "  • API: http://localhost:8000"
        echo "  • Documentation: http://localhost:8000/docs"
        echo ""
        echo "🔧 Commandes:"
        echo "  • Logs: docker logs -f hospitalidee-ia-api"
        echo "  • Arrêt: docker stop hospitalidee-ia-api"
    else
        echo "❌ Erreur de démarrage, vérifiez les logs:"
        docker logs hospitalidee-ia-api
        exit 1
    fi

# Option 3: Python direct
elif command_exists python3; then
    echo "🐍 Démarrage avec Python..."
    
    # Vérification des dépendances
    if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
        echo "📦 Création environnement virtuel..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        echo "📦 Activation environnement virtuel..."
        if [ -d "venv" ]; then
            source venv/bin/activate
        else
            source .venv/bin/activate
        fi
    fi
    
    # Chargement variables d'environnement
    export $(cat .env | xargs)
    
    # Démarrage
    echo "🚀 Lancement API..."
    python main.py &
    API_PID=$!
    
    echo "⏳ Attente démarrage (10s)..."
    sleep 10
    
    if curl -f -s http://localhost:8000/health > /dev/null; then
        echo "✅ API démarrée avec succès !"
        echo ""
        echo "📊 Accès:"
        echo "  • API: http://localhost:8000"
        echo "  • Documentation: http://localhost:8000/docs"
        echo ""
        echo "🔧 Pour arrêter: kill $API_PID"
        echo ""
        echo "L'API fonctionne en arrière-plan (PID: $API_PID)"
    else
        echo "❌ Erreur de démarrage"
        kill $API_PID 2>/dev/null || true
        exit 1
    fi

else
    echo "❌ Aucune méthode de démarrage disponible"
    echo ""
    echo "Installez une des options suivantes:"
    echo "  • Docker + Docker Compose (recommandé)"
    echo "  • Docker seul"
    echo "  • Python 3.8+"
    echo ""
    echo "Ou utilisez le script d'installation:"
    echo "  chmod +x scripts/install.sh"
    echo "  ./scripts/install.sh"
    exit 1
fi