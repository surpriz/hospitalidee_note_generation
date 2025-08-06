#!/bin/bash
# ============================================
# 🏥 Hospitalidée IA API - Script d'arrêt
# ============================================
# Arrête l'API proprement

set -e

echo "🛑 Arrêt Hospitalidée IA API..."

# Fonction pour vérifier si une commande existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

STOPPED_SOMETHING=false

# Option 1: Docker Compose
if command_exists docker-compose && [ -f "docker-compose.yml" ]; then
    echo "🐳 Arrêt Docker Compose..."
    if docker-compose ps | grep -q "Up"; then
        docker-compose down
        echo "✅ Docker Compose arrêté"
        STOPPED_SOMETHING=true
    else
        echo "ℹ️ Docker Compose déjà arrêté"
    fi
fi

# Option 2: Docker simple
if command_exists docker; then
    echo "🐳 Arrêt conteneur Docker..."
    if docker ps | grep -q hospitalidee-ia-api; then
        docker stop hospitalidee-ia-api
        docker rm hospitalidee-ia-api
        echo "✅ Conteneur Docker arrêté"
        STOPPED_SOMETHING=true
    else
        echo "ℹ️ Aucun conteneur Docker en cours"
    fi
fi

# Option 3: Processus Python
if command_exists pgrep; then
    echo "🐍 Arrêt processus Python..."
    PIDS=$(pgrep -f "main.py" || true)
    if [ ! -z "$PIDS" ]; then
        echo "Arrêt des processus: $PIDS"
        kill $PIDS
        sleep 2
        # Vérification si forcé nécessaire
        REMAINING=$(pgrep -f "main.py" || true)
        if [ ! -z "$REMAINING" ]; then
            echo "Arrêt forcé des processus restants: $REMAINING"
            kill -9 $REMAINING
        fi
        echo "✅ Processus Python arrêtés"
        STOPPED_SOMETHING=true
    else
        echo "ℹ️ Aucun processus Python main.py en cours"
    fi
fi

# Vérification finale
echo ""
echo "🔍 Vérification finale..."
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️ L'API semble encore accessible sur le port 8000"
    echo "Il peut y avoir un autre processus utilisant ce port"
    
    if command_exists lsof; then
        echo "Processus utilisant le port 8000:"
        lsof -i :8000 || echo "Aucun processus trouvé avec lsof"
    fi
elif [ "$STOPPED_SOMETHING" = true ]; then
    echo "✅ API complètement arrêtée"
else
    echo "ℹ️ Aucun service API détecté en cours d'exécution"
fi

echo ""
echo "🏁 Arrêt terminé"