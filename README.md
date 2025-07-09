# 🏥 Extension IA Hospitalidée - Génération Automatique de Notes

> **TripAdvisor du monde de la santé** - Solution d'IA franco-française pour automatiser la génération de réponses aux avis patients via Mistral AI.

## 📋 Description

Cette extension IA développée pour [Hospitalidée](https://www.hospitalidee.fr/) automatise la génération de notes d'avis patients en analysant le sentiment et en proposant des notes sur 5. Le projet implémente les **Besoins #1** (Génération Automatique) et **#1bis** (Processus de Validation) selon les spécifications techniques définies.

### 🎯 Fonctionnalités Principales

- **Analyse de sentiment** en temps réel avec Mistral AI
- **Calcul automatique de notes** sur 5 avec justification
- **Interface Streamlit** intuitive en 5 étapes
- **Validation croisée** entre calculs IA et règles locales
- **Détection d'incohérences** entre notes et verbatims
- **Export des résultats** en JSON pour intégration

## 🏗️ Architecture

```
hospitalidee_notation/
├── README.md                    # Cette documentation
├── requirements.txt             # Dépendances Python
├── .env.example                # Variables d'environnement
├── config/                     # Configuration centralisée
│   ├── settings.py             # Paramètres avec Pydantic
│   └── prompts.py              # Prompts Mistral AI standardisés
├── src/                        # Modules core
│   ├── mistral_client.py       # Client Mistral AI avec cache
│   ├── sentiment_analyzer.py   # Analyse de sentiment
│   ├── rating_calculator.py    # Calcul de notes
│   └── utils.py                # Utilitaires
├── streamlit_apps/             # Interfaces utilisateur
│   ├── besoin_1_notation_auto.py  # Génération automatique
│   ├── besoin_1bis_validation.py  # Processus validation
│   └── main_app.py            # Page d'accueil
├── tests/                      # Tests unitaires
└── data/                       # Échantillons et cas de test
```

## 🚀 Installation

### Prérequis

- Python 3.8+
- Clé API Mistral AI (obligatoire - solution franco-française)
- Git

### Installation rapide

```bash
# Cloner le projet
git clone <repo-url>
cd hospitalidee_notation

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env
# Éditer .env avec votre clé API Mistral
```

### Configuration

1. **Obtenir une clé API Mistral** sur [console.mistral.ai](https://console.mistral.ai/)
2. **Configurer les variables d'environnement** dans `.env` :

```bash
# API Mistral AI (obligatoire)
MISTRAL_API_KEY=your_mistral_api_key_here

# Configuration optionnelle
STREAMLIT_PORT=8501
LOG_LEVEL=INFO
MAX_RESPONSE_TIME=3.0
REQUIRED_PRECISION=0.85
REQUIRED_COHERENCE=0.90
```

## 🎮 Usage

### Lancement de l'interface Streamlit

```bash
# Besoin #1 : Génération Automatique de Notes
streamlit run streamlit_apps/besoin_1_notation_auto.py --server.port 8501

# Interface principale avec navigation
streamlit run streamlit_apps/main_app.py
```

### Utilisation Programmatique

```python
from src.sentiment_analyzer import analyze_sentiment
from src.rating_calculator import calculate_rating_from_text

# Analyse d'un avis patient
avis = "Excellent accueil, personnel très professionnel et à l'écoute..."

# 1. Analyse de sentiment
sentiment_result = analyze_sentiment(avis)
print(f"Sentiment: {sentiment_result['sentiment']}")
print(f"Confiance: {sentiment_result['confidence']:.1%}")

# 2. Calcul de note automatique
rating_result = calculate_rating_from_text(avis, sentiment_result)
print(f"Note suggérée: {rating_result['suggested_rating']}/5")
print(f"Justification: {rating_result['justification']}")
```

## 📊 Interface Utilisateur - Besoin #1

L'interface Streamlit guide l'utilisateur à travers **5 étapes** :

### 1. 📝 Saisie d'avis
- Zone de texte libre pour l'avis patient
- **Analyse en temps réel** pendant la frappe
- Indicateurs visuels (sentiment, confiance)

### 2. 🔍 Analyse complète
- Résultats détaillés de l'analyse Mistral AI
- Aspects positifs/négatifs détectés
- Graphiques de répartition sentiment

### 3. ⭐ Proposition de note
- Note suggérée avec justification IA
- Facteurs de calcul (sentiment, intensité, contenu)
- Validation croisée avec calcul local

### 4. ✅ Validation
- Possibilité d'ajuster la note proposée
- Récapitulatif complet de l'analyse
- Raison optionnelle d'ajustement

### 5. 🎉 Résultat final
- Avis finalisé avec note validée
- **Export JSON** des résultats complets
- Génération de titre suggéré

## 🔧 Configuration Avancée

### Paramètres Mistral AI

Les paramètres sont configurés dans `config/settings.py` :

```python
MISTRAL_PARAMS = {
    "model": "mistral-small-latest",
    "temperature": 0.3,        # Précision pour l'analyse
    "max_tokens": 1000,
    "top_p": 0.9,
    "presence_penalty": 0.0,
    "frequency_penalty": 0.0
}
```

### Seuils de Performance

- **Temps de réponse** : < 3 secondes par analyse
- **Précision requise** : 85% de notes correctement prédites
- **Cohérence requise** : 90% de détection des incohérences
- **Cache** : LRU cache avec TTL de 1 heure

## 🧪 Tests

### Lancement des tests

```bash
# Tests unitaires complets
pytest tests/ -v

# Tests avec couverture
pytest tests/ --cov=src --cov-report=html

# Tests spécifiques
pytest tests/test_sentiment.py
pytest tests/test_rating.py
```

### Cas de test inclus

Le projet inclut des cas de test standardisés dans `data/test_cases.json` :

- **Tests positifs** : Avis très satisfaits (note attendue 4-5)
- **Tests négatifs** : Avis très déçus (note attendue 1-2)
- **Tests incohérents** : Contradiction texte/notes partielles
- **Tests edge cases** : Textes courts, multilingues, etc.

## 📈 Métriques et Monitoring

### KPIs Trackés

- **Précision des notes** : % de prédictions à ±0.5 point
- **Temps de réponse** : Latence moyenne des appels Mistral
- **Taux de cohérence** : % d'incohérences détectées
- **Satisfaction utilisateur** : Taux d'acceptation des suggestions

### Logging

Configuration dans `.env` :

```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
ENABLE_LOGGING=true
```

Les logs incluent :
- Appels API Mistral avec timing
- Erreurs et fallbacks
- Métriques de performance
- **Aucune donnée patient** (compliance RGPD)

## 🔒 Sécurité et RGPD

### Contraintes Respectées

- **Anonymisation** : Pas de stockage d'avis personnels
- **Chiffrement** : Variables sensibles chiffrées
- **TTL obligatoire** : Cache avec expiration automatique
- **Logs sanitizés** : Aucune donnée patient dans les logs

### Mode Dégradé

En cas d'erreur API Mistral, le système bascule automatiquement en **mode dégradé** :

- Calcul de notes basé sur règles locales
- Sentiment analysé par mots-clés
- Fonctionnalité maintenue avec confiance réduite

## 🚀 Déploiement

### Environment Production

```bash
# Variables production
MISTRAL_API_KEY=<production_key>
LOG_LEVEL=WARNING
STREAMLIT_PORT=8501
CACHE_DURATION=7200  # 2 heures
```

### Docker (optionnel)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8501
CMD ["streamlit", "run", "streamlit_apps/main_app.py"]
```

## 🔗 Intégration avec Hospitalidée

Cette extension s'intègre dans l'écosystème Hospitalidée :

- **Backend Python** → API Flask pour intégration
- **Frontend Streamlit** → Demo et validation client  
- **Production NodeJS** → Équipe interne Hospitalidée

## 🤝 Contribution

### Standards de Code

- **Type hints obligatoires** sur toutes les fonctions
- **Docstrings Google style** pour fonctions publiques
- **Tests unitaires** pour chaque module (couverture 90%+)
- **Linting** avec pylint et black

### Architecture des Prompts

Tous les prompts Mistral sont centralisés dans `config/prompts.py` :

- `SENTIMENT_ANALYSIS_PROMPT` : Analyse de sentiment
- `RATING_CALCULATION_PROMPT` : Calcul de notes
- `COHERENCE_CHECK_PROMPT` : Vérification cohérence
- `TITLE_GENERATION_PROMPT` : Génération de titres

## 📞 Support

### Documentation Technique

- **Mistral AI** : [docs.mistral.ai](https://docs.mistral.ai/)
- **Streamlit** : [docs.streamlit.io](https://docs.streamlit.io/)
- **Context complet** : Voir `hospitalidee_cursor_context.md`

### Dépannage Courant

```bash
# Erreur "Module not found"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Erreur API Mistral
echo $MISTRAL_API_KEY  # Vérifier la clé

# Port Streamlit occupé  
streamlit run app.py --server.port 8502
```

---

## 📄 Licence

**Propriétaire** - Développé pour Hospitalidée  
Contact : [Hospitalidée](https://www.hospitalidee.fr/)

---

**🏥 Extension IA Hospitalidée** - Automatisation intelligente pour l'expérience patient française 🇫🇷 