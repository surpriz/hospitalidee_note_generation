#!/bin/bash
# ============================================
# 🏥 Hospitalidée IA API - Script d'installation
# ============================================
# Script d'installation automatique pour VPS Ubuntu/Debian

set -e  # Arrêt en cas d'erreur

echo "🏥 Installation Hospitalidée IA API..."
echo "==========================================="

# Vérification OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "✅ OS Linux détecté"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "✅ macOS détecté"
else
    echo "❌ OS non supporté: $OSTYPE"
    exit 1
fi

# Fonction pour vérifier si une commande existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Installation Docker si absent
echo -e "\n📦 Vérification Docker..."
if command_exists docker; then
    echo "✅ Docker déjà installé: $(docker --version)"
else
    echo "🔧 Installation Docker..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y ca-certificates curl gnupg lsb-release
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io
        sudo usermod -aG docker $USER
        echo "✅ Docker installé"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "❌ Veuillez installer Docker Desktop manuellement sur macOS"
        exit 1
    fi
fi

# 2. Installation Docker Compose si absent
echo -e "\n📦 Vérification Docker Compose..."
if command_exists docker-compose; then
    echo "✅ Docker Compose déjà installé: $(docker-compose --version)"
else
    echo "🔧 Installation Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installé"
fi

# 3. Configuration du fichier .env
echo -e "\n⚙️ Configuration..."
if [ ! -f ".env" ]; then
    if [ -f "config.env.example" ]; then
        cp config.env.example .env
        echo "✅ Fichier .env créé depuis config.env.example"
        echo ""
        echo "🔑 IMPORTANT: Vous devez configurer votre clé API Mistral !"
        echo "Éditez le fichier .env et remplissez MISTRAL_API_KEY"
        echo ""
        echo "Commandes:"
        echo "  nano .env"
        echo "  # ou"
        echo "  vim .env"
        echo ""
        echo "Récupérez votre clé API sur: https://console.mistral.ai/"
        echo ""
        read -p "Appuyez sur Entrée une fois la clé API configurée..."
    else
        echo "❌ Fichier config.env.example non trouvé"
        exit 1
    fi
else
    echo "✅ Fichier .env déjà présent"
fi

# 4. Vérification de la clé API
echo -e "\n🔑 Vérification clé API..."
if grep -q "your_mistral_api_key_here" .env; then
    echo "❌ Clé API Mistral non configurée dans .env"
    echo "Éditez le fichier .env et remplacez 'your_mistral_api_key_here' par votre vraie clé"
    exit 1
fi

if grep -q "^MISTRAL_API_KEY=" .env && ! grep -q "^MISTRAL_API_KEY=$" .env; then
    echo "✅ Clé API Mistral configurée"
else
    echo "❌ Clé API Mistral manquante ou vide dans .env"
    exit 1
fi

# 5. Build de l'image Docker
echo -e "\n🏗️ Construction de l'image Docker..."
docker build -t hospitalidee-ia-api .
echo "✅ Image Docker construite"

# 6. Création des répertoires nécessaires
echo -e "\n📁 Création des répertoires..."
mkdir -p logs
echo "✅ Répertoires créés"

# 7. Test de démarrage
echo -e "\n🚀 Test de démarrage..."
docker-compose up -d
echo "✅ Conteneurs démarrés"

# 8. Attente démarrage complet
echo -e "\n⏳ Attente démarrage complet (30s)..."
sleep 30

# 9. Test de santé
echo -e "\n🏥 Test de l'API..."
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo "✅ API fonctionnelle !"
    echo ""
    echo "🎉 INSTALLATION TERMINÉE AVEC SUCCÈS !"
    echo "==========================================="
    echo ""
    echo "📊 Votre API est accessible sur:"
    echo "  • API: http://localhost:8000"
    echo "  • Documentation: http://localhost:8000/docs"
    echo "  • Health check: http://localhost:8000/health"
    echo ""
    echo "🔧 Commandes utiles:"
    echo "  • Voir les logs: docker-compose logs -f"
    echo "  • Arrêter: docker-compose down"
    echo "  • Redémarrer: docker-compose restart"
    echo "  • Mettre à jour: ./scripts/update.sh"
    echo ""
    echo "📖 Consultez README.md pour l'utilisation"
else
    echo "❌ API non accessible"
    echo "Vérifiez les logs: docker-compose logs"
    exit 1
fi