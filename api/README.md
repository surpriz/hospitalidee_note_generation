# 🏥 Hospitalidée IA API

**API REST Ultra-Simple pour génération automatique de notes d'avis patients**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/hospitalidee/ia-api)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)](https://fastapi.tiangolo.com/)
[![Mistral AI](https://img.shields.io/badge/Mistral%20AI-powered-orange.svg)](https://mistral.ai/)

## 🎯 **Qu'est-ce que c'est ?**

Cette API permet d'analyser automatiquement des avis de patients et de générer des notes objectives sur 5. Elle combine :

- **🤖 Intelligence Artificielle Mistral** pour l'analyse de sentiment
- **📊 Questionnaires structurés** pour l'évaluation quantitative  
- **⚖️ Calcul hybride** pour une note finale précise
- **🚀 Une seule API** ultra-simple à utiliser

### **UN SEUL APPEL = RÉSULTAT COMPLET**

```javascript
// Envoyez ça...
{
  "type_evaluation": "etablissement",
  "avis_text": "Séjour excellent, personnel attentif...",
  "questionnaire_etablissement": {
    "medecins": 4, "personnel": 5, "accueil": 3,
    "prise_en_charge": 4, "confort": 3
  }
}

// ...recevez ça !
{
  "note_finale": 4.2,
  "sentiment": "positif",
  "confiance": 0.85,
  "titre_suggere": "Excellent séjour - personnel attentif"
}
```

---

## 🚀 **Installation Ultra-Rapide**

### Option 1: Installation automatique (recommandée)

```bash
# 1. Décompressez l'archive
unzip hospitalidee-ia-api.zip
cd hospitalidee-ia-api

# 2. Lancez l'installation automatique
chmod +x scripts/install.sh
./scripts/install.sh

# 3. Configurez votre clé API Mistral dans .env
# (le script vous guidera)

# C'est tout ! L'API est accessible sur http://localhost:8000
```

### Option 2: Installation manuelle avec Docker

```bash
# 1. Configuration
cp config.env.example .env
# Éditez .env et ajoutez votre MISTRAL_API_KEY

# 2. Démarrage
docker-compose up -d

# L'API est prête !
```

### Option 3: Installation Python

```bash
# 1. Environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# 2. Dépendances
pip install -r requirements.txt

# 3. Configuration
cp config.env.example .env
# Éditez .env et ajoutez votre MISTRAL_API_KEY

# 4. Démarrage
python main.py
```

### ⚡ Installation rapide sur VPS

Pour installer l'API sur votre VPS et la rendre accessible depuis internet :

```bash
# 1. Transférez l'archive sur votre VPS
scp hospitalidee-ia-api.zip root@VOTRE_IP_VPS:/root/

# 2. Sur le VPS, installez
ssh root@VOTRE_IP_VPS
cd /root && unzip hospitalidee-ia-api.zip
cd hospitalidee-ia-api && ./scripts/install.sh

# 3. Configurez pour accès externe
nano .env  # Mettez API_HOST=0.0.0.0
sudo ufw allow 8000/tcp  # Ouvrez le port

# 4. Votre API est accessible sur http://VOTRE_IP_VPS:8000
```

📖 **Guide complet VPS :** Consultez `DEPLOIEMENT_VPS.md` pour tous les détails.

---

## 🔑 **Configuration de la clé API Mistral**

1. **Créez un compte sur [Mistral AI](https://console.mistral.ai/)**
2. **Générez une clé API**
3. **Ajoutez-la dans le fichier `.env`** :

```bash
MISTRAL_API_KEY=your_actual_mistral_api_key_here
```

**⚠️ IMPORTANT :** Sans cette clé, l'API fonctionnera en mode dégradé uniquement.

---

## 📖 **Utilisation Simple**

### Accès à l'API

#### 💻 En développement local
- **🎯 API principale :** http://localhost:8000
- **📚 Documentation interactive :** http://localhost:8000/docs  
- **🏥 Health check :** http://localhost:8000/health

#### 🌐 Sur votre VPS (production)
- **🎯 API principale :** http://VOTRE_IP_VPS:8000
- **📚 Documentation interactive :** http://VOTRE_IP_VPS:8000/docs  
- **🏥 Health check :** http://VOTRE_IP_VPS:8000/health

> **📖 IMPORTANT :** Pour installer sur VPS, consultez **DEPLOIEMENT_VPS.md**

### Exemple complet (JavaScript)

```javascript
// Configuration de l'URL selon votre environnement
const API_URL = 'http://localhost:8000';          // 💻 Développement local
// const API_URL = 'http://VOTRE_IP_VPS:8000';    // 🌐 VPS production
// const API_URL = 'https://api.votre-site.com';  // 🔒 VPS avec domaine SSL

// Fonction pour évaluer un avis
async function evaluerAvis() {
    const response = await fetch(`${API_URL}/evaluate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            type_evaluation: "etablissement",
            avis_text: "Excellent séjour dans cet hôpital. Personnel très professionnel et attentif. Quelques soucis avec les repas mais globalement très satisfait.",
            questionnaire_etablissement: {
                medecins: 4,
                personnel: 5,
                accueil: 4,
                prise_en_charge: 4,
                confort: 2
            },
            generer_titre: true,
            analyse_detaillee: true
        })
    });
    
    const result = await response.json();
    
    console.log(`Note finale: ${result.note_finale}/5`);
    console.log(`Sentiment: ${result.sentiment}`);
    console.log(`Titre suggéré: ${result.titre_suggere}`);
    
    return result;
}

// Utilisation
evaluerAvis().then(result => {
    // Utilisez la note finale dans votre application
    document.getElementById('note').textContent = result.note_finale;
});
```

### Exemple PHP

```php
<?php
// Configuration de l'URL selon votre environnement
$API_URL = 'http://localhost:8000';          // 💻 Développement local
// $API_URL = 'http://VOTRE_IP_VPS:8000';    // 🌐 VPS production
// $API_URL = 'https://api.votre-site.com';  // 🔒 VPS avec domaine SSL

function evaluerAvis($type, $avis, $questionnaire, $apiUrl) {
    $data = [
        'type_evaluation' => $type,
        'avis_text' => $avis,
        $type === 'etablissement' ? 'questionnaire_etablissement' : 'questionnaire_medecin' => $questionnaire
    ];
    
    $response = file_get_contents($apiUrl . '/evaluate', false, stream_context_create([
        'http' => [
            'method' => 'POST',
            'header' => 'Content-Type: application/json',
            'content' => json_encode($data)
        ]
    ]));
    
    return json_decode($response, true);
}

// Utilisation
$result = evaluerAvis("etablissement", 
    "Personnel très gentil, locaux propres, mais attente un peu longue",
    ["medecins" => 4, "personnel" => 5, "accueil" => 3, "prise_en_charge" => 4, "confort" => 4],
    $API_URL
);

echo "Note: " . $result['note_finale'] . "/5\n";
echo "Sentiment: " . $result['sentiment'] . "\n";
?>
```

### Exemple Python

```python
import requests

# Configuration de l'URL selon votre environnement
API_URL = 'http://localhost:8000'          # 💻 Développement local
# API_URL = 'http://VOTRE_IP_VPS:8000'     # 🌐 VPS production  
# API_URL = 'https://api.votre-site.com'   # 🔒 VPS avec domaine SSL

def evaluer_avis(type_eval, avis, questionnaire):
    data = {
        'type_evaluation': type_eval,
        'avis_text': avis,
        f'questionnaire_{type_eval}': questionnaire
    }
    
    response = requests.post(f'{API_URL}/evaluate', json=data)
    return response.json()

# Utilisation
result = evaluer_avis("medecin", 
    "Dr Martin excellent, très à l'écoute et explications claires",
    {
        "explications": "Excellentes",
        "confiance": "Confiance totale", 
        "motivation": "Très motivé",
        "respect": "Très respectueux"
    }
)

print(f"Note: {result['note_finale']}/5")
print(f"Sentiment: {result['sentiment']}")
```

---

## 📊 **Endpoints disponibles**

### 🎯 `/evaluate` - Endpoint principal

**POST** `/evaluate` - Évaluation complète (questionnaire + avis → note finale)

```json
{
  "type_evaluation": "etablissement|medecin",
  "avis_text": "Texte de l'avis patient...",
  "questionnaire_etablissement": { /* si type=etablissement */ },
  "questionnaire_medecin": { /* si type=medecin */ },
  "generer_titre": true,
  "analyse_detaillee": true
}
```

**Réponse :**
```json
{
  "note_finale": 4.2,
  "confiance": 0.85,
  "sentiment": "positif",
  "intensite_emotionnelle": 0.7,
  "titre_suggere": "Excellent séjour - personnel attentif",
  "timestamp": "2024-01-15T14:30:00Z",
  "duree_traitement_ms": 2500,
  "mode_degrade": false
}
```

### 📊 `/sentiment` - Analyse de sentiment seule

**POST** `/sentiment` - Analyse rapide du sentiment

### 🏥 `/health` - Vérification de l'API

**GET** `/health` - Status de l'API et des services

### 📚 `/docs` - Documentation interactive

**GET** `/docs` - Interface Swagger pour tester l'API

---

## ⚙️ **Configuration avancée**

### Variables d'environnement

Éditez le fichier `.env` pour personnaliser :

```bash
# === OBLIGATOIRE ===
MISTRAL_API_KEY=your_key_here

# === OPTIONNEL ===
MISTRAL_MODEL=mistral-small-latest    # Modèle IA à utiliser
MISTRAL_TEMPERATURE=0.3               # Créativité (0=strict, 1=créatif)
API_PORT=8000                         # Port de l'API
LOG_LEVEL=INFO                        # Niveau de logs
DEBUG_MODE=false                      # Mode debug
MAX_RESPONSE_TIME=30.0                # Timeout en secondes
```

### Questionnaires

#### Établissement
```json
{
  "medecins": 1-5,        // Relation avec médecins
  "personnel": 1-5,       // Relation avec personnel  
  "accueil": 1-5,         // Qualité accueil
  "prise_en_charge": 1-5, // Prise en charge globale
  "confort": 1-5          // Confort chambres/repas
}
```

#### Médecin
```json
{
  "explications": "Très insuffisantes|Insuffisantes|Correctes|Bonnes|Excellentes",
  "confiance": "Aucune confiance|Peu de confiance|Confiance modérée|Bonne confiance|Confiance totale",
  "motivation": "Aucune motivation|Peu motivé|Moyennement motivé|Bien motivé|Très motivé", 
  "respect": "Pas du tout|Peu respectueux|Modérément respectueux|Respectueux|Très respectueux"
}
```

---

## 🔧 **Gestion et maintenance**

### Commandes utiles

```bash
# === DÉMARRAGE ===
./scripts/start.sh           # Démarre l'API
docker-compose up -d         # Avec Docker Compose
python main.py               # Avec Python direct

# === ARRÊT ===
./scripts/stop.sh            # Arrête l'API
docker-compose down          # Avec Docker Compose

# === MONITORING ===
docker-compose logs -f       # Voir les logs en temps réel
./scripts/test.sh            # Tester que tout fonctionne
curl http://localhost:8000/health  # Check rapide

# === MISE À JOUR ===
docker-compose pull          # Mettre à jour les images
docker-compose up -d --build # Reconstruire et redémarrer
```

### Logs

Les logs sont disponibles dans :
- **Docker :** `docker-compose logs`
- **Fichier :** `./logs/hospitalidee_api.log`

### Surveillance

Surveillez ces métriques :
- **Health check :** http://localhost:8000/health
- **Temps de réponse :** < 30 secondes par évaluation
- **Mémoire :** ~200-500 MB selon usage
- **CPU :** Pics pendant les appels Mistral

---

## 🐛 **Résolution de problèmes**

### L'API ne démarre pas

```bash
# 1. Vérifiez la configuration
cat .env | grep MISTRAL_API_KEY

# 2. Vérifiez les logs
docker-compose logs

# 3. Testez Mistral directement
curl -H "Authorization: Bearer YOUR_KEY" https://api.mistral.ai/v1/models
```

### Erreur "clé API invalide"

- Vérifiez que `MISTRAL_API_KEY` est correctement configurée dans `.env`
- Testez votre clé sur https://console.mistral.ai/
- Redémarrez l'API après modification

### Réponses lentes

- Normal : Mistral AI peut prendre 5-30 secondes
- En mode dégradé : réponse instantanée mais moins précise
- Vérifiez votre connexion internet

### Mode dégradé activé

L'API fonctionne en mode dégradé si :
- Clé Mistral manquante/invalide
- Mistral AI indisponible
- Timeout réseau

En mode dégradé, l'API utilise des algorithmes locaux (moins précis mais fonctionnels).

### Port déjà utilisé

```bash
# Changer le port dans .env
echo "API_PORT=8001" >> .env

# Ou arrêter le processus qui utilise le port 8000
sudo lsof -i :8000
sudo kill -9 PID
```

---

## 🔒 **Sécurité et production**

### Recommandations production

1. **Changez le port par défaut**
2. **Configurez un reverse proxy (Nginx)**
3. **Activez HTTPS**
4. **Limitez les CORS origins**
5. **Surveillez les logs**

### Configuration sécurisée

```bash
# .env production
ENVIRONMENT=production
DEBUG_MODE=false
CORS_ORIGINS=https://votre-site.com
RATE_LIMIT_ENABLED=true
ANONYMIZE_DATA=true
```

### Reverse proxy Nginx

```nginx
server {
    listen 80;
    server_name votre-api.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🆘 **Support et contact**

### En cas de problème

1. **Consultez cette documentation**
2. **Vérifiez les logs :** `docker-compose logs`
3. **Testez l'API :** `./scripts/test.sh`
4. **Vérifiez votre clé Mistral**

### Informations système

```bash
# Informations pour le support
echo "=== SYSTÈME ==="
uname -a
docker --version
docker-compose --version

echo "=== API ==="
curl -s http://localhost:8000/health | jq .

echo "=== CONFIGURATION ==="
cat .env | grep -v "API_KEY"
```

---

## 📋 **Spécifications techniques**

### Prérequis système
- **OS :** Linux, macOS, Windows
- **RAM :** 1 GB minimum, 2 GB recommandé  
- **CPU :** 1 cœur minimum
- **Stockage :** 500 MB
- **Réseau :** Accès internet pour Mistral AI

### Performances
- **Démarrage :** < 30 secondes
- **Réponse :** 2-30 secondes par évaluation
- **Débit :** 10-50 évaluations/minute
- **Disponibilité :** 99.9% (dépend de Mistral AI)

### Technologies
- **API :** FastAPI (Python 3.11)
- **IA :** Mistral AI (mistral-small-latest)
- **Déploiement :** Docker + Docker Compose
- **Documentation :** Swagger/OpenAPI automatique

---

## 📜 **Licence et crédits**

**Développé par Hospitalidée**

- Version : 1.0.0
- License : Propriétaire Hospitalidée
- IA : Powered by Mistral AI
- Framework : FastAPI
- Containerisation : Docker

---

## 🎉 **Félicitations !**

Votre API Hospitalidée IA est maintenant prête ! 

🚀 **Prochaines étapes :**
1. Testez avec vos premiers avis patients
2. Intégrez dans votre site web  
3. Surveillez les performances
4. Profitez de l'automatisation !

**Besoin d'aide ?** Consultez la documentation interactive sur http://localhost:8000/docs