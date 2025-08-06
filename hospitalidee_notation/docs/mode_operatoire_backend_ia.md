# Mode Opératoire - Backend IA Hospitalidée avec Node.js

Ce document détaille l'intégration backend de la solution IA d'évaluation d'avis patients développée par Hospitalidée, adaptée pour l'environnement Node.js.

## Sommaire
1. [Prérequis](#prérequis)
2. [Configuration initiale](#configuration-initiale)
3. [Architecture du service](#architecture-du-service)
4. [Intégration API Mistral](#intégration-api-mistral)
5. [Analyse de sentiment](#analyse-de-sentiment)
6. [Calcul de notes hybrides](#calcul-de-notes-hybrides)
7. [Workflows séparés](#workflows-séparés)
8. [Gestion des erreurs](#gestion-des-erreurs)
9. [Tests et validation](#tests-et-validation)
10. [Bonnes pratiques](#bonnes-pratiques)

## Prérequis

- Environnement Node.js (v16+ recommandé)
- Clé API Mistral AI valide
- Framework Express.js
- Base de données pour le cache (Redis recommandé)

## Configuration initiale

### 1. Installation des dépendances

```bash
# Dépendances principales
npm install express dotenv axios redis winston cors helmet express-rate-limit

# Dépendances de développement
npm install --save-dev jest supertest nodemon
```

### 2. Structure du projet

```
hospitalidee-ia-backend/
├── config/
│   ├── settings.js          # Configuration centralisée
│   └── prompts.js           # Prompts Mistral standardisés
├── src/
│   ├── controllers/
│   │   ├── sentimentController.js
│   │   ├── ratingController.js
│   │   └── evaluationController.js
│   ├── services/
│   │   ├── mistralClient.js
│   │   ├── sentimentAnalyzer.js
│   │   └── ratingCalculator.js
│   ├── middleware/
│   │   ├── auth.js
│   │   ├── rateLimit.js
│   │   └── validation.js
│   └── utils/
│       ├── logger.js
│       └── cache.js
├── tests/
├── app.js
└── server.js
```

### 3. Configuration d'environnement

Créez un fichier `.env` :

```env
# API Mistral AI
MISTRAL_API_KEY=votre_clé_api_mistral
MISTRAL_MODEL=mistral-small-latest
MISTRAL_TEMPERATURE=0.3
MISTRAL_MAX_TOKENS=1000
MISTRAL_TIMEOUT=30000

# Serveur
PORT=3000
NODE_ENV=production

# Cache Redis
REDIS_URL=redis://localhost:6379
CACHE_DURATION=3600

# Sécurité
JWT_SECRET=votre_jwt_secret
RATE_LIMIT_WINDOW=900000
RATE_LIMIT_MAX=100

# Performance
MAX_RESPONSE_TIME=30000
REQUIRED_PRECISION=0.85
```

## Architecture du service

### Configuration centralisée (`config/settings.js`)

```javascript
const dotenv = require('dotenv');
dotenv.config();

const settings = {
  mistral: {
    apiKey: process.env.MISTRAL_API_KEY,
    model: process.env.MISTRAL_MODEL || 'mistral-small-latest',
    temperature: parseFloat(process.env.MISTRAL_TEMPERATURE) || 0.3,
    maxTokens: parseInt(process.env.MISTRAL_MAX_TOKENS) || 1000,
    timeout: parseInt(process.env.MISTRAL_TIMEOUT) || 30000
  },
  
  server: {
    port: parseInt(process.env.PORT) || 3000,
    nodeEnv: process.env.NODE_ENV || 'development'
  },
  
  cache: {
    redisUrl: process.env.REDIS_URL || 'redis://localhost:6379',
    duration: parseInt(process.env.CACHE_DURATION) || 3600
  },
  
  performance: {
    maxResponseTime: parseInt(process.env.MAX_RESPONSE_TIME) || 30000,
    requiredPrecision: parseFloat(process.env.REQUIRED_PRECISION) || 0.85
  }
};

module.exports = settings;
```

### Prompts Mistral (`config/prompts.js`)

```javascript
const prompts = {
  SENTIMENT_ANALYSIS: `
Tu es un expert en analyse de sentiment spécialisé dans les avis patients d'établissements de santé français.

Analyse le texte suivant et détermine:
1. Le sentiment global (positif/neutre/négatif)
2. L'intensité émotionnelle (0.0 à 1.0)
3. Les indicateurs positifs et négatifs
4. Le niveau de confiance de ton analyse

Critères spécifiques pour les établissements de santé:
- Mots-clés positifs : "excellent", "parfait", "recommande", "professionnel", "attentif"
- Mots-clés négatifs : "déçu", "attente", "problème", "inadmissible", "négligent"

Réponds UNIQUEMENT au format JSON strict:
{
  "sentiment": "positif|neutre|negatif",
  "confidence": 0.85,
  "emotional_intensity": 0.7,
  "positive_indicators": ["excellent service", "personnel attentif"],
  "negative_indicators": ["attente longue", "chambre bruyante"],
  "key_themes": ["accueil", "soins", "confort"]
}

Texte à analyser: {text}
  `,

  HYBRID_RATING_CALCULATION: `
Tu es un expert en évaluation d'établissements de santé. Tu dois calculer une note finale sur 5 en combinant intelligemment:

1. QUESTIONNAIRE STRUCTURÉ: {questionnaire_note}/5
   (Évaluation directe par questions fermées)

2. ANALYSE TEXTUELLE: {sentiment_analysis}
   (Analyse du sentiment et émotions dans l'avis écrit)

INSTRUCTIONS:
- Pondère les deux sources selon leur fiabilité et cohérence
- Si cohérentes: moyenne pondérée (40% questionnaire, 60% analyse textuelle)
- Si divergentes: explique pourquoi et privilégie la source la plus fiable
- Note finale OBLIGATOIREMENT entre 1 et 5

RÉPONSE au format JSON:
{
  "suggested_rating": 3.2,
  "confidence": 0.85,
  "justification": "Explication détaillée de la synthèse",
  "factors": {
    "questionnaire_weight": 0.4,
    "sentiment_weight": 0.3,
    "intensity_weight": 0.2,
    "content_weight": 0.1
  },
  "hybrid_approach": "Description de l'approche hybride utilisée"
}
  `
};

module.exports = prompts;
```

## Intégration API Mistral

### Client Mistral (`src/services/mistralClient.js`)

```javascript
const axios = require('axios');
const settings = require('../../config/settings');
const logger = require('../utils/logger');
const { getCachedResult, setCachedResult } = require('../utils/cache');

class MistralClient {
  constructor() {
    this.baseUrl = 'https://api.mistral.ai/v1/chat/completions';
    this.apiKey = settings.mistral.apiKey;
    
    // Configuration axios avec retry
    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: settings.mistral.timeout,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      }
    });

    // Intercepteur pour logging
    this.client.interceptors.request.use(
      (config) => {
        logger.info(`Mistral API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => Promise.reject(error)
    );
  }

  async makeRequest(prompt, options = {}) {
    const cacheKey = this._generateCacheKey(prompt, options);
    
    // Vérifier le cache
    try {
      const cachedResult = await getCachedResult(cacheKey);
      if (cachedResult) {
        logger.info('Result served from cache');
        return cachedResult;
      }
    } catch (cacheError) {
      logger.warn('Cache read error:', cacheError.message);
    }

    const payload = {
      model: settings.mistral.model,
      messages: [{ role: 'user', content: prompt }],
      temperature: settings.mistral.temperature,
      max_tokens: settings.mistral.maxTokens,
      ...options
    };

    try {
      const startTime = Date.now();
      const response = await this.client.post('', payload);
      const duration = Date.now() - startTime;

      logger.info(`Mistral API Response: ${response.status} in ${duration}ms`);

      if (response.status === 200 && response.data.choices?.length > 0) {
        const content = response.data.choices[0].message.content;
        const result = this._parseJsonResponse(content);
        
        // Mettre en cache
        try {
          await setCachedResult(cacheKey, result);
        } catch (cacheError) {
          logger.warn('Cache write error:', cacheError.message);
        }
        
        return result;
      }

      throw new Error('Invalid response from Mistral API');

    } catch (error) {
      logger.error('Mistral API Error:', error.message);
      
      if (error.code === 'ECONNABORTED') {
        throw new Error('Timeout de l\'API Mistral - veuillez réessayer');
      }
      
      if (error.response?.status === 429) {
        throw new Error('Limite de requêtes atteinte - veuillez patienter');
      }
      
      if (error.response?.status === 401) {
        throw new Error('Clé API Mistral invalide');
      }
      
      throw new Error(`Erreur API Mistral: ${error.message}`);
    }
  }

  _parseJsonResponse(content) {
    try {
      // Nettoyer les balises markdown
      content = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      return JSON.parse(content);
    } catch (error) {
      logger.error('JSON parsing error:', content);
      throw new Error('Réponse API invalide - format JSON attendu');
    }
  }

  _generateCacheKey(prompt, options) {
    const crypto = require('crypto');
    const data = JSON.stringify({ prompt, options });
    return crypto.createHash('md5').update(data).digest('hex');
  }
}

module.exports = MistralClient;
```

## Analyse de sentiment

### Service d'analyse (`src/services/sentimentAnalyzer.js`)

```javascript
const MistralClient = require('./mistralClient');
const prompts = require('../../config/prompts');
const logger = require('../utils/logger');

class SentimentAnalyzer {
  constructor() {
    this.mistralClient = new MistralClient();
  }

  async analyzeSentiment(text) {
    if (!text || text.trim().length < 5) {
      throw new Error('Texte trop court pour l\'analyse de sentiment');
    }

    try {
      const prompt = prompts.SENTIMENT_ANALYSIS.replace('{text}', text.trim());
      const result = await this.mistralClient.makeRequest(prompt);

      // Validation du résultat
      this._validateSentimentResult(result);
      
      // Enrichir avec analyse locale
      const localAnalysis = this._performLocalAnalysis(text);
      
      return {
        ...result,
        ...localAnalysis,
        text_length: text.length,
        word_count: text.split(/\s+/).length
      };

    } catch (error) {
      logger.error('Sentiment analysis error:', error.message);
      
      // Mode dégradé avec analyse locale
      return this._getFallbackSentiment(text, error.message);
    }
  }

  _validateSentimentResult(result) {
    const required = ['sentiment', 'confidence', 'emotional_intensity'];
    const missing = required.filter(field => !(field in result));
    
    if (missing.length > 0) {
      throw new Error(`Champs manquants dans la réponse: ${missing.join(', ')}`);
    }

    if (!['positif', 'negatif', 'neutre'].includes(result.sentiment)) {
      throw new Error('Sentiment invalide dans la réponse');
    }

    if (result.confidence < 0 || result.confidence > 1) {
      throw new Error('Confiance hors limites [0-1]');
    }
  }

  _performLocalAnalysis(text) {
    const textLower = text.toLowerCase();
    
    const positiveKeywords = [
      'excellent', 'parfait', 'recommande', 'professionnel', 'attentif',
      'efficace', 'rassurant', 'compétent', 'satisfait', 'merci'
    ];

    const negativeKeywords = [
      'déçu', 'problème', 'inadmissible', 'négligent', 'froid',
      'débordé', 'sale', 'bruyant', 'incompétent', 'insatisfait'
    ];

    const positiveCount = positiveKeywords.filter(word => textLower.includes(word)).length;
    const negativeCount = negativeKeywords.filter(word => textLower.includes(word)).length;

    return {
      local_positive_count: positiveCount,
      local_negative_count: negativeCount,
      local_sentiment_score: (positiveCount - negativeCount) / (positiveCount + negativeCount + 1)
    };
  }

  _getFallbackSentiment(text, error) {
    const localAnalysis = this._performLocalAnalysis(text);
    
    let sentiment = 'neutre';
    if (localAnalysis.local_sentiment_score > 0.2) sentiment = 'positif';
    if (localAnalysis.local_sentiment_score < -0.2) sentiment = 'negatif';

    return {
      sentiment,
      confidence: 0.0,
      emotional_intensity: Math.abs(localAnalysis.local_sentiment_score),
      positive_indicators: [],
      negative_indicators: [],
      key_themes: [],
      ...localAnalysis,
      error: error,
      fallback_mode: true
    };
  }
}

module.exports = SentimentAnalyzer;
```

## Calcul de notes hybrides

### Service de calcul de notes (`src/services/ratingCalculator.js`)

```javascript
const MistralClient = require('./mistralClient');
const SentimentAnalyzer = require('./sentimentAnalyzer');
const prompts = require('../../config/prompts');
const logger = require('../utils/logger');

class RatingCalculator {
  constructor() {
    this.mistralClient = new MistralClient();
    this.sentimentAnalyzer = new SentimentAnalyzer();
  }

  async calculateHybridRating(text, questionnaireNote, sentimentAnalysis = null) {
    // Validation des entrées
    if (!text || text.trim().length < 10) {
      throw new Error('Texte insuffisant pour le calcul de note');
    }

    if (questionnaireNote < 1 || questionnaireNote > 5) {
      throw new Error('Note questionnaire hors limites [1-5]');
    }

    try {
      // Obtenir l'analyse de sentiment si non fournie
      if (!sentimentAnalysis) {
        sentimentAnalysis = await this.sentimentAnalyzer.analyzeSentiment(text);
      }

      // Calcul avec Mistral AI
      const mistralResult = await this._calculateWithMistral(sentimentAnalysis, questionnaireNote);
      
      // Calcul local pour comparaison
      const localResult = this._calculateLocalRating(sentimentAnalysis, questionnaireNote);
      
      // Synthèse finale
      return this._synthesizeResults(mistralResult, localResult, questionnaireNote);

    } catch (error) {
      logger.error('Hybrid rating calculation error:', error.message);
      
      // Mode dégradé
      return this._getFallbackRating(questionnaireNote, error.message);
    }
  }

  async _calculateWithMistral(sentimentAnalysis, questionnaireNote) {
    const prompt = prompts.HYBRID_RATING_CALCULATION
      .replace('{sentiment_analysis}', JSON.stringify(sentimentAnalysis))
      .replace('{questionnaire_note}', questionnaireNote.toString());

    const result = await this.mistralClient.makeRequest(prompt);
    
    // Validation
    if (!result.suggested_rating || result.suggested_rating < 1 || result.suggested_rating > 5) {
      throw new Error('Note suggérée invalide');
    }

    return {
      ...result,
      hybrid_mode: true,
      mistral_calculation: true
    };
  }

  _calculateLocalRating(sentimentAnalysis, questionnaireNote) {
    const sentiment = sentimentAnalysis.sentiment;
    const intensity = sentimentAnalysis.emotional_intensity || 0.5;
    
    // Mapping sentiment → note de base
    const sentimentRatings = {
      'positif': 4.0,
      'neutre': 3.0,
      'negatif': 2.0
    };

    let baseRating = sentimentRatings[sentiment] || 3.0;
    
    // Ajustement par intensité
    if (sentiment === 'positif' && intensity > 0.8) {
      baseRating = Math.min(5.0, baseRating + 1.0);
    } else if (sentiment === 'negatif' && intensity > 0.8) {
      baseRating = Math.max(1.0, baseRating - 1.0);
    }

    // Moyenne pondérée avec questionnaire
    const hybridRating = (0.6 * baseRating + 0.4 * questionnaireNote);
    
    return {
      suggested_rating: Math.round(hybridRating * 10) / 10, // 1 décimale
      confidence: sentimentAnalysis.confidence || 0.5,
      justification: `Calcul local: sentiment ${sentiment} (${baseRating}) + questionnaire (${questionnaireNote})`,
      factors: {
        questionnaire_weight: 0.4,
        sentiment_weight: 0.6,
        intensity_weight: 0.0,
        content_weight: 0.0
      },
      local_calculation: true
    };
  }

  _synthesizeResults(mistralResult, localResult, questionnaireNote) {
    const mistralRating = mistralResult.suggested_rating;
    const localRating = localResult.suggested_rating;
    const difference = Math.abs(mistralRating - localRating);

    // Si les deux méthodes sont cohérentes, privilégier Mistral
    if (difference < 1.0) {
      return {
        ...mistralResult,
        local_comparison: localRating,
        coherence_score: 1 - (difference / 5),
        synthesis_applied: false
      };
    }

    // Si divergence importante, faire une moyenne pondérée
    const confidence = mistralResult.confidence || 0.5;
    const mistralWeight = 0.7 + (confidence * 0.3);
    const localWeight = 1.0 - mistralWeight;

    const synthesizedRating = (mistralRating * mistralWeight) + (localRating * localWeight);

    return {
      ...mistralResult,
      suggested_rating: Math.round(synthesizedRating * 10) / 10,
      local_comparison: localRating,
      coherence_score: 1 - (difference / 5),
      synthesis_applied: true,
      synthesis_weights: { mistral: mistralWeight, local: localWeight },
      adjustment_reason: `Écart important détecté (${difference.toFixed(1)}) - synthèse appliquée`
    };
  }

  _getFallbackRating(questionnaireNote, error) {
    return {
      suggested_rating: questionnaireNote,
      confidence: 0.0,
      justification: `Mode dégradé: utilisation de la note questionnaire (${questionnaireNote})`,
      factors: {
        questionnaire_weight: 1.0,
        sentiment_weight: 0.0,
        intensity_weight: 0.0,
        content_weight: 0.0
      },
      hybrid_mode: true,
      fallback_mode: true,
      error: error
    };
  }

  // Méthodes pour les calculs spécialisés établissement/médecin
  calculateEtablissementNote(scores) {
    const aspects = ['medecins', 'personnel', 'accueil', 'prise_en_charge', 'confort'];
    const validScores = aspects.map(aspect => {
      const score = scores[aspect];
      return (score >= 1 && score <= 5) ? score : 3; // Défaut à 3 si invalide
    });

    return {
      note_globale: validScores.reduce((a, b) => a + b) / validScores.length,
      details: Object.fromEntries(aspects.map((aspect, i) => [aspect, validScores[i]])),
      type: 'etablissement'
    };
  }

  calculateMedecinsNote(evaluations) {
    const criteria = ['explications', 'confiance', 'motivation', 'respect'];
    const textToRating = {
      // Explications
      'Très insuffisantes': 1, 'Insuffisantes': 2, 'Correctes': 3, 'Bonnes': 4, 'Excellentes': 5,
      // Confiance
      'Aucune confiance': 1, 'Peu de confiance': 2, 'Confiance modérée': 3, 'Bonne confiance': 4, 'Confiance totale': 5,
      // Motivation
      'Aucune motivation': 1, 'Peu motivé': 2, 'Moyennement motivé': 3, 'Bien motivé': 4, 'Très motivé': 5,
      // Respect
      'Pas du tout': 1, 'Peu respectueux': 2, 'Modérément respectueux': 3, 'Respectueux': 4, 'Très respectueux': 5
    };

    const scores = criteria.map(criterion => {
      const evaluation = evaluations[criterion];
      return textToRating[evaluation] || 3;
    });

    return {
      note_globale: scores.reduce((a, b) => a + b) / scores.length,
      details: Object.fromEntries(criteria.map((criterion, i) => [criterion, {
        evaluation: evaluations[criterion],
        note: scores[i]
      }])),
      type: 'medecins'
    };
  }
}

module.exports = RatingCalculator;
```

## Workflows séparés

### Contrôleur d'évaluation (`src/controllers/evaluationController.js`)

```javascript
const SentimentAnalyzer = require('../services/sentimentAnalyzer');
const RatingCalculator = require('../services/ratingCalculator');
const logger = require('../utils/logger');

class EvaluationController {
  constructor() {
    this.sentimentAnalyzer = new SentimentAnalyzer();
    this.ratingCalculator = new RatingCalculator();
  }

  // Workflow Établissement
  async evaluateEtablissement(req, res) {
    try {
      const { questionnaire, avis_text } = req.body;

      // Validation
      if (!questionnaire || !avis_text) {
        return res.status(400).json({
          status: 'error',
          message: 'Questionnaire établissement et avis requis'
        });
      }

      // 1. Calcul note questionnaire établissement
      const questionnaireResult = this.ratingCalculator.calculateEtablissementNote(questionnaire);
      
      // 2. Analyse sentiment
      const sentimentResult = await this.sentimentAnalyzer.analyzeSentiment(avis_text);
      
      // 3. Calcul note hybride
      const hybridResult = await this.ratingCalculator.calculateHybridRating(
        avis_text, 
        questionnaireResult.note_globale, 
        sentimentResult
      );

      // 4. Résultat final
      const finalResult = {
        type: 'etablissement',
        questionnaire: questionnaireResult,
        sentiment: sentimentResult,
        note_finale: hybridResult,
        avis_text: avis_text,
        timestamp: new Date().toISOString()
      };

      logger.info(`Évaluation établissement terminée - Note: ${hybridResult.suggested_rating}/5`);

      res.json({
        status: 'success',
        data: finalResult
      });

    } catch (error) {
      logger.error('Évaluation établissement error:', error.message);
      res.status(500).json({
        status: 'error',
        message: 'Erreur lors de l\'évaluation établissement',
        details: error.message
      });
    }
  }

  // Workflow Médecin
  async evaluateMedecin(req, res) {
    try {
      const { questionnaire, avis_text } = req.body;

      // Validation
      if (!questionnaire || !avis_text) {
        return res.status(400).json({
          status: 'error',
          message: 'Questionnaire médecin et avis requis'
        });
      }

      // 1. Calcul note questionnaire médecin
      const questionnaireResult = this.ratingCalculator.calculateMedecinsNote(questionnaire);
      
      // 2. Analyse sentiment
      const sentimentResult = await this.sentimentAnalyzer.analyzeSentiment(avis_text);
      
      // 3. Calcul note hybride
      const hybridResult = await this.ratingCalculator.calculateHybridRating(
        avis_text, 
        questionnaireResult.note_globale, 
        sentimentResult
      );

      // 4. Résultat final
      const finalResult = {
        type: 'medecin',
        questionnaire: questionnaireResult,
        sentiment: sentimentResult,
        note_finale: hybridResult,
        avis_text: avis_text,
        timestamp: new Date().toISOString()
      };

      logger.info(`Évaluation médecin terminée - Note: ${hybridResult.suggested_rating}/5`);

      res.json({
        status: 'success',
        data: finalResult
      });

    } catch (error) {
      logger.error('Évaluation médecin error:', error.message);
      res.status(500).json({
        status: 'error',
        message: 'Erreur lors de l\'évaluation médecin',
        details: error.message
      });
    }
  }

  // Analyse de sentiment seule
  async analyzeSentiment(req, res) {
    try {
      const { text } = req.body;

      if (!text) {
        return res.status(400).json({
          status: 'error',
          message: 'Texte requis pour l\'analyse'
        });
      }

      const result = await this.sentimentAnalyzer.analyzeSentiment(text);

      res.json({
        status: 'success',
        data: result
      });

    } catch (error) {
      logger.error('Sentiment analysis error:', error.message);
      res.status(500).json({
        status: 'error',
        message: 'Erreur lors de l\'analyse de sentiment',
        details: error.message
      });
    }
  }

  // Génération de titre suggéré
  async generateTitle(req, res) {
    try {
      const { text, sentiment, rating } = req.body;

      if (!text || !sentiment) {
        return res.status(400).json({
          status: 'error',
          message: 'Texte et sentiment requis'
        });
      }

      // Logique simple de génération de titre
      let title = "Avis patient";
      
      if (sentiment === 'positif' && rating >= 4) {
        title = "Expérience très positive";
      } else if (sentiment === 'positif') {
        title = "Expérience globalement satisfaisante";
      } else if (sentiment === 'negatif' && rating <= 2) {
        title = "Expérience décevante";
      } else if (sentiment === 'negatif') {
        title = "Points d'amélioration identifiés";
      } else {
        title = "Avis nuancé sur mon séjour";
      }

      res.json({
        status: 'success',
        data: {
          suggested_title: title,
          alternatives: [
            "Mon expérience de soins",
            "Retour sur ma prise en charge",
            "Avis sur l'établissement"
          ]
        }
      });

    } catch (error) {
      logger.error('Title generation error:', error.message);
      res.status(500).json({
        status: 'error',
        message: 'Erreur lors de la génération de titre',
        details: error.message
      });
    }
  }
}

module.exports = EvaluationController;
```

## Gestion des erreurs

### Middleware d'erreurs (`src/middleware/errorHandler.js`)

```javascript
const logger = require('../utils/logger');

// Middleware de gestion d'erreurs global
const errorHandler = (err, req, res, next) => {
  logger.error('Unhandled error:', {
    message: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method
  });

  // Erreurs spécifiques à l'IA
  if (err.message.includes('Mistral') || err.message.includes('sentiment')) {
    return res.status(503).json({
      status: 'error',
      message: 'Service IA temporairement indisponible',
      code: 'IA_SERVICE_ERROR',
      details: process.env.NODE_ENV === 'development' ? err.message : undefined
    });
  }

  // Erreurs de validation
  if (err.name === 'ValidationError') {
    return res.status(400).json({
      status: 'error',
      message: 'Données d\'entrée invalides',
      code: 'VALIDATION_ERROR',
      details: err.message
    });
  }

  // Erreurs de timeout
  if (err.code === 'ECONNABORTED' || err.message.includes('timeout')) {
    return res.status(408).json({
      status: 'error',
      message: 'Délai d\'attente dépassé',
      code: 'TIMEOUT_ERROR'
    });
  }

  // Erreur générique
  res.status(500).json({
    status: 'error',
    message: 'Erreur interne du serveur',
    code: 'INTERNAL_ERROR',
    details: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
};

// Handler pour routes non trouvées
const notFoundHandler = (req, res) => {
  res.status(404).json({
    status: 'error',
    message: `Route non trouvée: ${req.method} ${req.path}`,
    code: 'NOT_FOUND'
  });
};

module.exports = {
  errorHandler,
  notFoundHandler
};
```

## Tests et validation

### Tests d'intégration (`tests/evaluation.test.js`)

```javascript
const request = require('supertest');
const app = require('../app');

describe('Évaluation API', () => {
  
  test('Évaluation établissement complète', async () => {
    const payload = {
      questionnaire: {
        medecins: 4,
        personnel: 5,
        accueil: 3,
        prise_en_charge: 4,
        confort: 3
      },
      avis_text: "Séjour globalement satisfaisant. Personnel très attentif, chambres correctes."
    };

    const response = await request(app)
      .post('/api/evaluate/etablissement')
      .send(payload)
      .expect(200);

    expect(response.body.status).toBe('success');
    expect(response.body.data.type).toBe('etablissement');
    expect(response.body.data.questionnaire.note_globale).toBeCloseTo(3.8, 1);
    expect(response.body.data.sentiment.sentiment).toBe('positif');
    expect(response.body.data.note_finale.suggested_rating).toBeGreaterThan(0);
  });

  test('Évaluation médecin complète', async () => {
    const payload = {
      questionnaire: {
        explications: 'Bonnes',
        confiance: 'Bonne confiance',
        motivation: 'Bien motivé',
        respect: 'Très respectueux'
      },
      avis_text: "Dr Martin excellent, explications très claires et rassurantes."
    };

    const response = await request(app)
      .post('/api/evaluate/medecin')
      .send(payload)
      .expect(200);

    expect(response.body.status).toBe('success');
    expect(response.body.data.type).toBe('medecin');
    expect(response.body.data.questionnaire.note_globale).toBeCloseTo(4.25, 1);
    expect(response.body.data.sentiment.sentiment).toBe('positif');
  });

  test('Gestion d\'erreur avec texte vide', async () => {
    const payload = {
      questionnaire: { medecins: 3 },
      avis_text: ""
    };

    const response = await request(app)
      .post('/api/evaluate/etablissement')
      .send(payload)
      .expect(400);

    expect(response.body.status).toBe('error');
  });

});
```

## Bonnes pratiques

### 1. Performance et cache

```javascript
// Configuration Redis pour le cache
const redis = require('redis');
const settings = require('../config/settings');

const client = redis.createClient({ url: settings.cache.redisUrl });

client.on('error', (err) => {
  console.error('Redis Client Error', err);
});

// Fonctions utilitaires de cache
async function getCachedResult(key) {
  await client.connect();
  const result = await client.get(key);
  await client.disconnect();
  return result ? JSON.parse(result) : null;
}

async function setCachedResult(key, data) {
  await client.connect();
  await client.setEx(key, settings.cache.duration, JSON.stringify(data));
  await client.disconnect();
}
```

### 2. Limitation de débit

```javascript
const rateLimit = require('express-rate-limit');

const createRateLimit = (windowMs, max, message) => rateLimit({
  windowMs,
  max,
  message: { status: 'error', message },
  standardHeaders: true,
  legacyHeaders: false,
});

// Limitation pour l'IA (plus restrictive)
const aiRateLimit = createRateLimit(
  15 * 60 * 1000, // 15 minutes
  20, // 20 requêtes max
  'Trop de requêtes IA - veuillez patienter'
);

// Limitation générale
const generalRateLimit = createRateLimit(
  15 * 60 * 1000,
  100,
  'Trop de requêtes - veuillez patienter'
);
```

### 3. Monitoring et métriques

```javascript
const prometheus = require('prom-client');

// Métriques personnalisées
const httpRequestDuration = new prometheus.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status']
});

const mistralApiCalls = new prometheus.Counter({
  name: 'mistral_api_calls_total',
  help: 'Total number of Mistral API calls',
  labelNames: ['endpoint', 'status']
});

const evaluationResults = new prometheus.Counter({
  name: 'evaluation_results_total',
  help: 'Total evaluations by type and sentiment',
  labelNames: ['type', 'sentiment']
});

// Middleware de métriques
const metricsMiddleware = (req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestDuration
      .labels(req.method, req.route?.path || req.path, res.statusCode)
      .observe(duration);
  });

  next();
};
```

### 4. Configuration de l'application principale

```javascript
// app.js
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');

const settings = require('./config/settings');
const EvaluationController = require('./src/controllers/evaluationController');
const { errorHandler, notFoundHandler } = require('./src/middleware/errorHandler');
const logger = require('./src/utils/logger');

const app = express();
const evaluationController = new EvaluationController();

// Middleware de sécurité et performance
app.use(helmet());
app.use(compression());
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Logging des requêtes
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.path}`, {
    ip: req.ip,
    userAgent: req.get('User-Agent')
  });
  next();
});

// Routes API
app.post('/api/evaluate/etablissement', evaluationController.evaluateEtablissement.bind(evaluationController));
app.post('/api/evaluate/medecin', evaluationController.evaluateMedecin.bind(evaluationController));
app.post('/api/sentiment/analyze', evaluationController.analyzeSentiment.bind(evaluationController));
app.post('/api/title/generate', evaluationController.generateTitle.bind(evaluationController));

// Health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0'
  });
});

// Middleware d'erreurs (en dernier)
app.use(notFoundHandler);
app.use(errorHandler);

module.exports = app;
```

### 5. Script de démarrage

```javascript
// server.js
const app = require('./app');
const settings = require('./config/settings');
const logger = require('./src/utils/logger');

const port = settings.server.port;

const server = app.listen(port, () => {
  logger.info(`🏥 Hospitalidée IA Backend démarré sur le port ${port}`);
  logger.info(`📊 Environment: ${settings.server.nodeEnv}`);
  logger.info(`🤖 Mistral Model: ${settings.mistral.model}`);
});

// Gestion gracieuse de l'arrêt
process.on('SIGTERM', () => {
  logger.info('SIGTERM reçu - arrêt du serveur...');
  server.close(() => {
    logger.info('Serveur arrêté proprement');
    process.exit(0);
  });
});

process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});
```

---

## Résumé d'utilisation

### Endpoints principaux

- **POST** `/api/evaluate/etablissement` - Évaluation complète établissement
- **POST** `/api/evaluate/medecin` - Évaluation complète médecin  
- **POST** `/api/sentiment/analyze` - Analyse de sentiment seule
- **POST** `/api/title/generate` - Génération de titre suggéré

### Exemple d'utilisation

```javascript
// Évaluation établissement
const response = await fetch('/api/evaluate/etablissement', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    questionnaire: {
      medecins: 4,
      personnel: 5,
      accueil: 3,
      prise_en_charge: 4,
      confort: 3
    },
    avis_text: "Séjour satisfaisant, personnel attentif..."
  })
});

const result = await response.json();
// result.data.note_finale.suggested_rating = note hybride finale
```

Cette architecture backend permet une intégration flexible et robuste de l'IA d'évaluation d'avis patients dans l'environnement Node.js d'Hospitalidée, avec gestion d'erreurs avancée, cache, monitoring et workflows séparés.
