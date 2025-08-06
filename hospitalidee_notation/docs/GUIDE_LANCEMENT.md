# 🏥 Guide de Lancement - Hospitalidée Extension IA

## ✅ Installation et Configuration

### 1. Vérification des Dépendances
```bash
# Vérifier que Python est installé
python --version  # Doit être >= 3.8

# Installer toutes les dépendances
pip install -r requirements.txt
```

### 2. Configuration de la Clé API Mistral

1. **Obtenir une clé API Mistral** :
   - Aller sur [https://console.mistral.ai/](https://console.mistral.ai/)
   - Créer un compte et obtenir une clé API

2. **Configurer les variables d'environnement** :
   ```bash
   # Copier le fichier d'exemple
   cp .env.example .env
   
   # Éditer le fichier .env
   nano .env  # ou votre éditeur préféré
   ```

3. **Contenu du fichier .env** :
   ```bash
   # API Mistral AI (OBLIGATOIRE)
   MISTRAL_API_KEY=votre_cle_api_mistral_ici
   
   # Configuration optionnelle
   MISTRAL_MODEL=mistral-small-latest
   MISTRAL_TEMPERATURE=0.3
   MAX_RESPONSE_TIME=3.0
   
   # Interface Streamlit
   STREAMLIT_PORT=8501
   STREAMLIT_THEME_PRIMARY_COLOR=#FF6B35
   ```

## 🚀 Lancement de l'Application

### Méthode 1 : Script de Lancement (Recommandé)
```bash
python run_streamlit.py
```

### Méthode 2 : Commande Directe
```bash
streamlit run streamlit_apps/besoin_1_notation_auto.py --server.port 8501
```

### Méthode 3 : Via le Browser
Une fois lancée, l'application sera accessible à :
- **URL locale** : http://localhost:8501
- **URL réseau** : http://[votre-ip]:8501

## 🧪 Tests et Validation

### Test des Imports
```bash
python test_imports.py
```

### Test avec Exemples
L'application fonctionne même sans clé API (mode dégradé), mais pour tester complètement :

1. **Avec clé API** : Fonctionnalités complètes Mistral AI
2. **Sans clé API** : Mode dégradé avec algorithmes locaux

## 📋 Interface Utilisateur - 5 Écrans

### 📝 Écran 1 : Saisie du Texte
- Zone de texte pour l'avis patient
- Analyse en temps réel pendant la frappe
- Indicateurs de sentiment visuels

### 📊 Écran 2 : Analyse Complète
- Graphiques de sentiment
- Métriques détaillées
- Visualisations Plotly interactives

### 🎯 Écran 3 : Note Suggérée par IA
- Note sur 5 calculée par Mistral AI
- Justification détaillée
- Facteurs de notation

### ✅ Écran 4 : Validation Utilisateur
- Possibilité d'ajuster la note
- Commentaires sur les ajustements
- Validation finale

### 💾 Écran 5 : Résultat Final
- Note finale validée
- Export JSON pour intégration
- Historique de l'analyse

## 🔧 Résolution de Problèmes

### Problème : ImportError
```bash
# Solution 1 : Nettoyer le cache
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Solution 2 : Réinstaller les dépendances
pip install --force-reinstall -r requirements.txt

# Solution 3 : Vérifier l'environnement Python
which python
pip list | grep -E "(streamlit|mistral|pydantic)"
```

### Problème : API Mistral Non Accessible
- ✅ L'application fonctionne en mode dégradé
- ✅ Vérifier la clé API dans le fichier .env
- ✅ Vérifier la connexion internet

### Problème : Port Occupé
```bash
# Utiliser un port différent
streamlit run streamlit_apps/besoin_1_notation_auto.py --server.port 8502
```

## 📈 Performance et KPIs

### Objectifs selon Cursor Rules
- ⚡ **Performance** : < 3 secondes par analyse
- 🎯 **Précision** : 85% de précision sur les notes suggérées  
- 🔄 **Cohérence** : 90% de détection des incohérences
- 🇫🇷 **IA Française** : Mistral AI uniquement

### Monitoring en Temps Réel
L'interface affiche en continu :
- Temps de réponse des analyses
- Niveau de confiance des prédictions
- Statut de l'API Mistral
- Mode de fonctionnement (normal/dégradé)

## 🛡️ Sécurité et RGPD

### Conformité Automatique
- ✅ Aucun stockage d'avis personnels
- ✅ Anonymisation automatique des données
- ✅ Cache avec TTL (Time To Live)
- ✅ Logs sans données patients

### Données Traitées
- ✅ Texte de l'avis (anonymisé)
- ✅ Métriques de sentiment
- ✅ Notes calculées
- ❌ Aucune donnée personnelle stockée

## 📞 Support

### Logs et Debug
```bash
# Activer le mode debug
export DEBUG_MODE=true
export LOG_LEVEL=DEBUG

# Lancer avec logs détaillés
python run_streamlit.py
```

### Structure du Projet
```
hospitalidee_notation/
├── 📄 README.md                    # Documentation principale
├── 📄 GUIDE_LANCEMENT.md          # Ce guide
├── 📄 requirements.txt            # Dépendances Python
├── 📄 .env.example               # Configuration exemple
├── 🐍 run_streamlit.py           # Script de lancement
├── 🧪 test_imports.py             # Tests de validation
├── 📁 config/                    # Configuration
├── 📁 src/                       # Modules Python core
├── 📁 streamlit_apps/           # Interface utilisateur
└── 📁 tests/                     # Tests automatisés
```

---
**🏥 Extension IA Hospitalidée** - Génération automatique de notes d'avis patients  
*Solution 100% française avec Mistral AI* 