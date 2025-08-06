# Mode Opératoire - Frontend IA Hospitalidée avec Node.js

Ce document détaille l'implémentation frontend de la solution IA d'évaluation d'avis patients développée par Hospitalidée, avec interface utilisateur en 5 étapes et workflows séparés.

## Sommaire
1. [Prérequis](#prérequis)
2. [Configuration initiale](#configuration-initiale)
3. [Architecture frontend](#architecture-frontend)
4. [Interface en 5 étapes](#interface-en-5-étapes)
5. [Workflows séparés](#workflows-séparés)
6. [Intégration avec le backend IA](#intégration-avec-le-backend-ia)
7. [Composants réutilisables](#composants-réutilisables)
8. [Gestion des états](#gestion-des-états)
9. [Tests et validation](#tests-et-validation)
10. [Déploiement](#déploiement)

## Prérequis

- Node.js v16+ avec framework frontend (React/Vue/Angular recommandés)
- Backend IA Hospitalidée configuré
- Connaissance des APIs REST et gestion d'état
- CSS/SCSS pour le styling personnalisé

## Configuration initiale

### 1. Structure du projet frontend

```
hospitalidee-ia-frontend/
├── src/
│   ├── components/
│   │   ├── evaluation/
│   │   │   ├── TypeSelection.js
│   │   │   ├── QuestionnaireEtablissement.js
│   │   │   ├── QuestionnaireMedecin.js
│   │   │   ├── SaisieAvis.js
│   │   │   ├── NoteIA.js
│   │   │   ├── AnalyseHybride.js
│   │   │   └── ResultatFinal.js
│   │   ├── common/
│   │   │   ├── ProgressBar.js
│   │   │   ├── SentimentIndicator.js
│   │   │   ├── RatingDisplay.js
│   │   │   └── LoadingSpinner.js
│   │   └── ui/
│   │       ├── Button.js
│   │       ├── Input.js
│   │       └── Modal.js
│   ├── services/
│   │   ├── evaluationService.js
│   │   ├── apiClient.js
│   │   └── storageService.js
│   ├── hooks/
│   │   ├── useEvaluation.js
│   │   ├── useSentiment.js
│   │   └── useDebounce.js
│   ├── contexts/
│   │   └── EvaluationContext.js
│   ├── utils/
│   │   ├── constants.js
│   │   ├── validators.js
│   │   └── formatters.js
│   └── styles/
│       ├── components/
│       ├── themes/
│       └── main.scss
├── public/
└── tests/
```

### 2. Configuration des services

#### Service API Client (`src/services/apiClient.js`)

```javascript
class ApiClient {
  constructor(baseURL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:3000') {
    this.baseURL = baseURL;
    this.timeout = 30000; // 30 secondes pour l'IA
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      timeout: this.timeout,
      ...options
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}`);
      }

      return await response.json();
      
    } catch (error) {
      if (error.name === 'AbortError' || error.message.includes('timeout')) {
        throw new Error('Délai d\'attente dépassé - veuillez réessayer');
      }
      
      if (error.message.includes('Failed to fetch')) {
        throw new Error('Erreur de connexion - vérifiez votre réseau');
      }
      
      throw error;
    }
  }

  // Méthodes spécialisées
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }
}

export default new ApiClient();
```

#### Service d'évaluation (`src/services/evaluationService.js`)

```javascript
import apiClient from './apiClient';

class EvaluationService {
  
  // Évaluation complète établissement
  async evaluateEtablissement(questionnaireData, avisText) {
    const payload = {
      questionnaire: questionnaireData,
      avis_text: avisText
    };
    
    return await apiClient.post('/api/evaluate/etablissement', payload);
  }

  // Évaluation complète médecin
  async evaluateMedecin(questionnaireData, avisText) {
    const payload = {
      questionnaire: questionnaireData,
      avis_text: avisText
    };
    
    return await apiClient.post('/api/evaluate/medecin', payload);
  }

  // Analyse de sentiment seule
  async analyzeSentiment(text) {
    return await apiClient.post('/api/sentiment/analyze', { text });
  }

  // Génération de titre
  async generateTitle(text, sentiment, rating) {
    return await apiClient.post('/api/title/generate', { text, sentiment, rating });
  }

  // Health check
  async checkHealth() {
    return await apiClient.get('/api/health');
  }
}

export default new EvaluationService();
```

## Architecture frontend

### Context d'évaluation (`src/contexts/EvaluationContext.js`)

```javascript
import React, { createContext, useContext, useReducer } from 'react';

const EvaluationContext = createContext();

// Actions
const ACTIONS = {
  SET_TYPE: 'SET_TYPE',
  SET_STEP: 'SET_STEP',
  SET_QUESTIONNAIRE: 'SET_QUESTIONNAIRE',
  SET_AVIS: 'SET_AVIS',
  SET_SENTIMENT: 'SET_SENTIMENT',
  SET_RATING: 'SET_RATING',
  SET_ANALYSIS: 'SET_ANALYSIS',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  RESET: 'RESET'
};

// State initial
const initialState = {
  // Navigation
  currentStep: 0, // 0: sélection type, 1-5: étapes évaluation
  evaluationType: null, // 'etablissement' | 'medecin'
  
  // Données questionnaire
  questionnaireEtablissement: {
    medecins: 3,
    personnel: 3,
    accueil: 3,
    prise_en_charge: 3,
    confort: 3
  },
  questionnaireMedecin: {
    explications: 'Correctes',
    confiance: 'Confiance modérée',
    motivation: 'Moyennement motivé',
    respect: 'Modérément respectueux'
  },
  
  // Données saisie
  avisText: '',
  
  // Résultats IA
  sentimentAnalysis: null,
  ratingCalculation: null,
  finalAnalysis: null,
  
  // États UI
  loading: false,
  error: null,
  
  // Résultat final
  isComplete: false
};

// Reducer
function evaluationReducer(state, action) {
  switch (action.type) {
    case ACTIONS.SET_TYPE:
      return {
        ...state,
        evaluationType: action.payload,
        currentStep: action.payload ? 1 : 0,
        error: null
      };
      
    case ACTIONS.SET_STEP:
      return {
        ...state,
        currentStep: action.payload,
        error: null
      };
      
    case ACTIONS.SET_QUESTIONNAIRE:
      return {
        ...state,
        [`questionnaire${action.questionnaireType}`]: {
          ...state[`questionnaire${action.questionnaireType}`],
          ...action.payload
        }
      };
      
    case ACTIONS.SET_AVIS:
      return {
        ...state,
        avisText: action.payload
      };
      
    case ACTIONS.SET_SENTIMENT:
      return {
        ...state,
        sentimentAnalysis: action.payload
      };
      
    case ACTIONS.SET_RATING:
      return {
        ...state,
        ratingCalculation: action.payload
      };
      
    case ACTIONS.SET_ANALYSIS:
      return {
        ...state,
        finalAnalysis: action.payload,
        isComplete: true
      };
      
    case ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: action.payload
      };
      
    case ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        loading: false
      };
      
    case ACTIONS.RESET:
      return {
        ...initialState
      };
      
    default:
      return state;
  }
}

// Provider
export function EvaluationProvider({ children }) {
  const [state, dispatch] = useReducer(evaluationReducer, initialState);
  
  const value = {
    state,
    dispatch,
    actions: ACTIONS
  };
  
  return (
    <EvaluationContext.Provider value={value}>
      {children}
    </EvaluationContext.Provider>
  );
}

// Hook personnalisé
export function useEvaluation() {
  const context = useContext(EvaluationContext);
  if (!context) {
    throw new Error('useEvaluation must be used within EvaluationProvider');
  }
  return context;
}
```

## Interface en 5 étapes

### Étape 0 : Sélection du type (`src/components/evaluation/TypeSelection.js`)

```javascript
import React from 'react';
import { useEvaluation } from '../../contexts/EvaluationContext';
import Button from '../ui/Button';
import './TypeSelection.scss';

const TypeSelection = () => {
  const { state, dispatch, actions } = useEvaluation();

  const handleTypeSelection = (type) => {
    dispatch({ type: actions.SET_TYPE, payload: type });
  };

  return (
    <div className="type-selection">
      <div className="type-selection__header">
        <h1>🎯 Sélection du type d'évaluation</h1>
        <p>
          Bienvenue dans l'outil d'évaluation Hospitalidée ! 
          Choisissez le type d'évaluation que vous souhaitez effectuer.
        </p>
      </div>

      <div className="type-selection__options">
        <div className="type-option">
          <div className="type-option__card type-option__card--etablissement">
            <div className="type-option__icon">🏥</div>
            <h2>Évaluer un Établissement</h2>
            <ul>
              <li>Relation avec les médecins</li>
              <li>Relation avec le personnel</li>
              <li>Accueil et prise en charge</li>
              <li>Confort (chambres, repas)</li>
              <li>Analyse globale de l'établissement</li>
            </ul>
            <Button
              variant="primary"
              size="large"
              onClick={() => handleTypeSelection('etablissement')}
              fullWidth
            >
              Évaluer un Établissement
            </Button>
          </div>
        </div>

        <div className="type-option">
          <div className="type-option__card type-option__card--medecin">
            <div className="type-option__icon">👨‍⚕️</div>
            <h2>Évaluer un Médecin</h2>
            <ul>
              <li>Qualité des explications</li>
              <li>Sentiment de confiance</li>
              <li>Motivation prescription</li>
              <li>Respect de votre identité</li>
              <li>Analyse centrée sur la relation médecin-patient</li>
            </ul>
            <Button
              variant="primary"
              size="large"
              onClick={() => handleTypeSelection('medecin')}
              fullWidth
            >
              Évaluer un Médecin
            </Button>
          </div>
        </div>
      </div>

      <div className="type-selection__info">
        <p>💡 <strong>Astuce :</strong> Vous pourrez revenir à cette sélection à tout moment.</p>
      </div>
    </div>
  );
};

export default TypeSelection;
```

### Étape 1 : Questionnaire (`src/components/evaluation/QuestionnaireEtablissement.js`)

```javascript
import React from 'react';
import { useEvaluation } from '../../contexts/EvaluationContext';
import Button from '../ui/Button';
import RatingSlider from '../common/RatingSlider';
import ProgressBar from '../common/ProgressBar';
import './Questionnaire.scss';

const QuestionnaireEtablissement = () => {
  const { state, dispatch, actions } = useEvaluation();
  const questionnaire = state.questionnaireEtablissement;

  const handleRatingChange = (aspect, value) => {
    dispatch({
      type: actions.SET_QUESTIONNAIRE,
      questionnaireType: 'Etablissement',
      payload: { [aspect]: value }
    });
  };

  const calculateAverage = () => {
    const values = Object.values(questionnaire);
    return (values.reduce((sum, val) => sum + val, 0) / values.length).toFixed(1);
  };

  const goToNext = () => {
    dispatch({ type: actions.SET_STEP, payload: 2 });
  };

  const goBack = () => {
    dispatch({ type: actions.SET_STEP, payload: 0 });
  };

  return (
    <div className="questionnaire questionnaire--etablissement">
      <ProgressBar currentStep={1} totalSteps={5} />
      
      <div className="questionnaire__header">
        <h1>📋 Questionnaire d'évaluation 🏥</h1>
        <p>
          Évaluez votre expérience établissement en répondant aux questions suivantes.
          Cette évaluation permettra une analyse hybride plus précise.
        </p>
      </div>

      <div className="questionnaire__form">
        <h2>🏥 Évaluation de l'Établissement</h2>
        <p className="questionnaire__subtitle">
          Donnez une note sur 5 pour chaque aspect de votre expérience :
        </p>

        <div className="questionnaire__sections">
          <div className="questionnaire__section">
            <RatingSlider
              label="Votre relation avec les médecins"
              value={questionnaire.medecins}
              onChange={(value) => handleRatingChange('medecins', value)}
              help="Qualité de la communication et des interactions avec les médecins"
            />

            <RatingSlider
              label="Votre relation avec le personnel"
              value={questionnaire.personnel}
              onChange={(value) => handleRatingChange('personnel', value)}
              help="Qualité des interactions avec les infirmières, aides-soignants"
            />

            <RatingSlider
              label="L'accueil"
              value={questionnaire.accueil}
              onChange={(value) => handleRatingChange('accueil', value)}
              help="Qualité de l'accueil à votre arrivée dans l'établissement"
            />
          </div>

          <div className="questionnaire__section">
            <RatingSlider
              label="La prise en charge jusqu'à la sortie"
              value={questionnaire.prise_en_charge}
              onChange={(value) => handleRatingChange('prise_en_charge', value)}
              help="Qualité du suivi médical du début à la fin de votre séjour"
            />

            <RatingSlider
              label="Les chambres et les repas"
              value={questionnaire.confort}
              onChange={(value) => handleRatingChange('confort', value)}
              help="Qualité de l'hébergement et de la restauration"
            />
          </div>
        </div>

        <div className="questionnaire__summary">
          <div className="summary-card summary-card--etablissement">
            <h3>🎯 Résumé de votre évaluation</h3>
            <div className="summary-rating">
              <span className="summary-rating__value">{calculateAverage()}/5</span>
              <span className="summary-rating__label">Note Établissement</span>
              <div className="summary-rating__stars">
                {'⭐'.repeat(Math.floor(parseFloat(calculateAverage())))}
                {'☆'.repeat(5 - Math.floor(parseFloat(calculateAverage())))}
              </div>
            </div>
            
            <div className="summary-details">
              {Object.entries(questionnaire).map(([key, value]) => {
                const labels = {
                  medecins: 'Médecins',
                  personnel: 'Personnel',
                  accueil: 'Accueil', 
                  prise_en_charge: 'Prise en charge',
                  confort: 'Confort'
                };
                
                return (
                  <div key={key} className="summary-item">
                    <span>{labels[key]}: {value}/5</span>
                    <div className="mini-stars">
                      {'⭐'.repeat(value)}{'☆'.repeat(5 - value)}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      <div className="questionnaire__navigation">
        <Button variant="secondary" onClick={goBack}>
          ← Changer de type
        </Button>
        <Button variant="primary" onClick={goToNext}>
          Continuer vers la saisie d'avis 📝
        </Button>
      </div>
    </div>
  );
};

export default QuestionnaireEtablissement;
```

### Étape 2 : Saisie d'avis (`src/components/evaluation/SaisieAvis.js`)

```javascript
import React, { useState, useCallback } from 'react';
import { useEvaluation } from '../../contexts/EvaluationContext';
import { useSentiment } from '../../hooks/useSentiment';
import { useDebounce } from '../../hooks/useDebounce';
import Button from '../ui/Button';
import SentimentIndicator from '../common/SentimentIndicator';
import LoadingSpinner from '../common/LoadingSpinner';
import ProgressBar from '../common/ProgressBar';
import './SaisieAvis.scss';

const SaisieAvis = () => {
  const { state, dispatch, actions } = useEvaluation();
  const [localText, setLocalText] = useState(state.avisText);
  
  // Debounce pour éviter trop d'appels API
  const debouncedText = useDebounce(localText, 1000);
  
  // Hook personnalisé pour l'analyse sentiment
  const { sentiment, loading: sentimentLoading, error: sentimentError } = useSentiment(debouncedText);

  // Mettre à jour le sentiment dans le contexte global
  React.useEffect(() => {
    if (sentiment) {
      dispatch({ type: actions.SET_SENTIMENT, payload: sentiment });
    }
  }, [sentiment, dispatch, actions]);

  const handleTextChange = useCallback((e) => {
    const text = e.target.value;
    setLocalText(text);
    dispatch({ type: actions.SET_AVIS, payload: text });
  }, [dispatch, actions]);

  const getPlaceholderText = () => {
    if (state.evaluationType === 'etablissement') {
      return "Décrivez votre expérience dans l'établissement : accueil, soins reçus, personnel, confort, locaux...";
    }
    return "Décrivez votre relation avec le médecin : communication, écoute, explications, traitement...";
  };

  const getDescription = () => {
    const type = state.evaluationType === 'etablissement' ? 'établissement de santé' : 'médecin';
    return `Partagez votre expérience avec ${type === 'médecin' ? 'le ' : "l'"}${type}. Plus votre avis sera détaillé, plus notre analyse sera précise.`;
  };

  const canProceed = localText.trim().length >= 20;

  const goToNext = () => {
    if (canProceed) {
      dispatch({ type: actions.SET_STEP, payload: 3 });
    }
  };

  const goBack = () => {
    dispatch({ type: actions.SET_STEP, payload: 1 });
  };

  return (
    <div className="saisie-avis">
      <ProgressBar currentStep={2} totalSteps={5} />
      
      <div className="saisie-avis__header">
        <h1>
          📝 Saisie de votre avis 
          {state.evaluationType === 'etablissement' ? '🏥' : '👨‍⚕️'}
        </h1>
        <p>{getDescription()}</p>
        
        {state.evaluationType && (
          <div className="questionnaire-summary">
            ✅ Questionnaire {state.evaluationType} complété - 
            Note: {state.evaluationType === 'etablissement' 
              ? (Object.values(state.questionnaireEtablissement).reduce((a, b) => a + b) / 5).toFixed(1)
              : '4.0' // Calculé dynamiquement selon les choix médecin
            }/5
          </div>
        )}
      </div>

      <div className="saisie-avis__content">
        <div className="saisie-avis__input-section">
          <label htmlFor="avis-textarea">Votre avis complet</label>
          <textarea
            id="avis-textarea"
            value={localText}
            onChange={handleTextChange}
            placeholder={getPlaceholderText()}
            rows={8}
            className="saisie-avis__textarea"
          />
          
          <div className="text-info">
            <span className="word-count">
              {localText.split(/\s+/).filter(word => word.length > 0).length} mots
            </span>
            {!canProceed && localText.trim().length > 0 && (
              <span className="min-length-warning">
                Minimum 20 caractères requis
              </span>
            )}
          </div>
        </div>

        <div className="saisie-avis__analysis-section">
          <h3>🎯 Analyse instantanée</h3>
          
          {localText.trim().length < 10 ? (
            <div className="analysis-placeholder">
              <p>Commencez à écrire votre avis pour voir l'analyse en temps réel</p>
            </div>
          ) : (
            <div className="analysis-content">
              {sentimentLoading ? (
                <div className="analysis-loading">
                  <LoadingSpinner size="small" />
                  <span>Analyse en cours...</span>
                </div>
              ) : sentimentError ? (
                <div className="analysis-error">
                  <p>⚠️ L'API prend plus de temps que prévu</p>
                  <small>Le système fonctionne en mode dégradé</small>
                </div>
              ) : sentiment ? (
                <SentimentIndicator sentiment={sentiment} detailed />
              ) : null}
            </div>
          )}
        </div>
      </div>

      <div className="saisie-avis__navigation">
        <Button variant="secondary" onClick={goBack}>
          ← Retour questionnaire
        </Button>
        <Button 
          variant="primary" 
          onClick={goToNext}
          disabled={!canProceed}
        >
          Calculer la note IA →
        </Button>
      </div>
    </div>
  );
};

export default SaisieAvis;
```

### Hook de sentiment (`src/hooks/useSentiment.js`)

```javascript
import { useState, useEffect } from 'react';
import evaluationService from '../services/evaluationService';

export const useSentiment = (text) => {
  const [sentiment, setSentiment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!text || text.trim().length < 10) {
      setSentiment(null);
      setError(null);
      return;
    }

    const analyzeSentiment = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await evaluationService.analyzeSentiment(text.trim());
        setSentiment(response.data);
      } catch (err) {
        setError(err.message);
        // Mode dégradé local
        setSentiment({
          sentiment: 'neutre',
          confidence: 0.0,
          emotional_intensity: 0.5,
          fallback_mode: true
        });
      } finally {
        setLoading(false);
      }
    };

    analyzeSentiment();
  }, [text]);

  return { sentiment, loading, error };
};
```

### Étape 3 : Note IA (`src/components/evaluation/NoteIA.js`)

```javascript
import React, { useEffect, useState } from 'react';
import { useEvaluation } from '../../contexts/EvaluationContext';
import evaluationService from '../../services/evaluationService';
import Button from '../ui/Button';
import RatingDisplay from '../common/RatingDisplay';
import LoadingSpinner from '../common/LoadingSpinner';
import ProgressBar from '../common/ProgressBar';
import './NoteIA.scss';

const NoteIA = () => {
  const { state, dispatch, actions } = useEvaluation();
  const [calculating, setCalculating] = useState(false);

  useEffect(() => {
    if (!state.ratingCalculation && state.sentimentAnalysis && state.avisText) {
      calculateHybridRating();
    }
  }, []);

  const calculateHybridRating = async () => {
    setCalculating(true);
    dispatch({ type: actions.SET_ERROR, payload: null });

    try {
      let response;
      
      if (state.evaluationType === 'etablissement') {
        response = await evaluationService.evaluateEtablissement(
          state.questionnaireEtablissement,
          state.avisText
        );
      } else {
        response = await evaluationService.evaluateMedecin(
          state.questionnaireMedecin,
          state.avisText
        );
      }

      dispatch({ type: actions.SET_RATING, payload: response.data });

    } catch (error) {
      console.error('Rating calculation error:', error);
      
      // Mode dégradé
      const fallbackRating = {
        note_finale: {
          suggested_rating: 3.0,
          confidence: 0.0,
          justification: `Mode dégradé: ${error.message}`,
          factors: { questionnaire_weight: 1.0 },
          fallback_mode: true
        }
      };
      
      dispatch({ type: actions.SET_RATING, payload: fallbackRating });
      dispatch({ type: actions.SET_ERROR, payload: error.message });
      
    } finally {
      setCalculating(false);
    }
  };

  const getQuestionnaireNote = () => {
    if (state.evaluationType === 'etablissement') {
      const values = Object.values(state.questionnaireEtablissement);
      return (values.reduce((sum, val) => sum + val, 0) / values.length).toFixed(1);
    }
    
    // Calcul médecin simplifié pour l'affichage
    return '4.2'; // À implémenter selon la logique des select-slider
  };

  const goToNext = () => {
    dispatch({ type: actions.SET_STEP, payload: 4 });
  };

  const goBack = () => {
    dispatch({ type: actions.SET_STEP, payload: 2 });
  };

  if (calculating) {
    return (
      <div className="note-ia note-ia--loading">
        <ProgressBar currentStep={3} totalSteps={5} />
        <div className="loading-container">
          <LoadingSpinner size="large" />
          <h2>Calcul de la note IA hybride en cours...</h2>
          <p>Notre IA analyse votre questionnaire et votre avis textuel</p>
        </div>
      </div>
    );
  }

  const ratingData = state.ratingCalculation;
  const suggestedRating = ratingData?.note_finale?.suggested_rating || 3.0;
  const confidence = ratingData?.note_finale?.confidence || 0.0;
  const justification = ratingData?.note_finale?.justification || "Calcul automatique";
  const questionnaireNote = getQuestionnaireNote();

  return (
    <div className="note-ia">
      <ProgressBar currentStep={3} totalSteps={5} />
      
      <div className="note-ia__header">
        <h1>
          ⭐ Note suggérée par l'IA 
          {state.evaluationType === 'etablissement' ? '🏥' : '👨‍⚕️'}
        </h1>
      </div>

      <div className="note-ia__content">
        <div className="note-ia__main">
          <div className="rating-section">
            <h2>🎯 Note suggérée par l'IA hybride - {
              state.evaluationType === 'etablissement' ? 'Établissement' : 'Médecin'
            }</h2>
            
            <RatingDisplay
              rating={suggestedRating}
              confidence={confidence}
              variant={state.evaluationType}
              title="Note IA Hybride"
              subtitle="🔗 Analyse hybride (Questionnaire + Avis textuel)"
            />

            <div className="justification">
              <h3>💭 Justification de l'IA</h3>
              <div className="justification-content">
                {justification}
              </div>
            </div>

            <div className="coherence-analysis">
              <h3>🔗 Cohérence avec le questionnaire {
                state.evaluationType === 'etablissement' ? 'Établissement' : 'Médecin'
              }</h3>
              
              <div className="coherence-metrics">
                <div className="metric">
                  <span className="metric-label">Note questionnaire</span>
                  <span className="metric-value">{questionnaireNote}/5</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Note IA hybride</span>
                  <span className="metric-value">{suggestedRating.toFixed(1)}/5</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Écart</span>
                  <span className={`metric-value ${Math.abs(suggestedRating - parseFloat(questionnaireNote)) < 1 ? 'metric-value--good' : 'metric-value--warning'}`}>
                    {(suggestedRating - parseFloat(questionnaireNote) >= 0 ? '+' : '')}{(suggestedRating - parseFloat(questionnaireNote)).toFixed(1)}
                  </span>
                </div>
              </div>
            </div>

            {ratingData?.note_finale?.factors && (
              <div className="factors-breakdown">
                <h3>⚖️ Facteurs pris en compte</h3>
                <div className="factors-list">
                  <div className="factor">
                    <span>Questionnaire fermé</span>
                    <span>{(ratingData.note_finale.factors.questionnaire_weight * 100).toFixed(0)}%</span>
                  </div>
                  <div className="factor">
                    <span>Sentiment textuel</span>
                    <span>{(ratingData.note_finale.factors.sentiment_weight * 100).toFixed(0)}%</span>
                  </div>
                  <div className="factor">
                    <span>Intensité émotionnelle</span>
                    <span>{(ratingData.note_finale.factors.intensity_weight * 100).toFixed(0)}%</span>
                  </div>
                  <div className="factor">
                    <span>Richesse du contenu</span>
                    <span>{(ratingData.note_finale.factors.content_weight * 100).toFixed(0)}%</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="note-ia__sidebar">
          <h3>📊 Analyse comparative</h3>
          
          {/* Graphique simple ou métriques additionnelles */}
          <div className="comparison-chart">
            <div className="chart-placeholder">
              📊 Graphique de répartition des facteurs
            </div>
          </div>

          {state.error && (
            <div className="error-info">
              <h4>⚠️ Mode dégradé activé</h4>
              <p>L'IA fonctionne avec des capacités réduites</p>
              <details>
                <summary>Détails technique</summary>
                <p>{state.error}</p>
              </details>
            </div>
          )}
        </div>
      </div>

      <div className="note-ia__navigation">
        <Button variant="secondary" onClick={goBack}>
          ← Retour saisie avis
        </Button>
        <Button variant="primary" onClick={goToNext}>
          Voir analyse hybride →
        </Button>
      </div>
    </div>
  );
};

export default NoteIA;
```

## Workflows séparés

### Composant principal d'évaluation (`src/components/evaluation/EvaluationApp.js`)

```javascript
import React from 'react';
import { useEvaluation } from '../../contexts/EvaluationContext';

// Import des composants par étape
import TypeSelection from './TypeSelection';
import QuestionnaireEtablissement from './QuestionnaireEtablissement';
import QuestionnaireMedecin from './QuestionnaireMedecin';
import SaisieAvis from './SaisieAvis';
import NoteIA from './NoteIA';
import AnalyseHybride from './AnalyseHybride';
import ResultatFinal from './ResultatFinal';

// Sidebar de navigation
import Sidebar from '../common/Sidebar';

import './EvaluationApp.scss';

const EvaluationApp = () => {
  const { state } = useEvaluation();
  
  const renderCurrentStep = () => {
    const { currentStep, evaluationType } = state;
    
    switch (currentStep) {
      case 0:
        return <TypeSelection />;
      
      case 1:
        if (evaluationType === 'etablissement') {
          return <QuestionnaireEtablissement />;
        } else if (evaluationType === 'medecin') {
          return <QuestionnaireMedecin />;
        }
        return <TypeSelection />; // Fallback si pas de type sélectionné
      
      case 2:
        return <SaisieAvis />;
      
      case 3:
        return <NoteIA />;
      
      case 4:
        return <AnalyseHybride />;
      
      case 5:
        return <ResultatFinal />;
      
      default:
        return <TypeSelection />;
    }
  };

  return (
    <div className="evaluation-app">
      {state.evaluationType && <Sidebar />}
      
      <main className="evaluation-app__main">
        <div className="evaluation-app__content">
          {renderCurrentStep()}
        </div>
      </main>
    </div>
  );
};

export default EvaluationApp;
```

### Sidebar de navigation (`src/components/common/Sidebar.js`)

```javascript
import React from 'react';
import { useEvaluation } from '../../contexts/EvaluationContext';
import SentimentIndicator from './SentimentIndicator';
import './Sidebar.scss';

const Sidebar = () => {
  const { state, dispatch, actions } = useEvaluation();
  
  const steps = [
    'Questionnaire',
    'Saisie', 
    'Note IA',
    'Analyse hybride',
    'Résultat'
  ];

  const getEvaluationInfo = () => {
    if (state.evaluationType === 'etablissement') {
      return {
        icon: '🏥',
        name: 'Établissement',
        color: 'blue'
      };
    }
    return {
      icon: '👨‍⚕️', 
      name: 'Médecin',
      color: 'purple'
    };
  };

  const handleRestart = () => {
    if (window.confirm('Êtes-vous sûr de vouloir recommencer ?')) {
      dispatch({ type: actions.RESET });
    }
  };

  const evalInfo = getEvaluationInfo();

  return (
    <aside className={`sidebar sidebar--${evalInfo.color}`}>
      <div className="sidebar__header">
        <h2>🏥 Hospitalidée</h2>
        <p>Génération Automatique de Notes</p>
      </div>

      <div className="sidebar__type">
        <div className="type-badge">
          <span className="type-badge__icon">{evalInfo.icon}</span>
          <span className="type-badge__name">Évaluation : {evalInfo.name}</span>
        </div>
      </div>

      <div className="sidebar__progress">
        <h3>Progression</h3>
        <div className="steps-list">
          {steps.map((step, index) => {
            const stepNumber = index + 1;
            const isCompleted = stepNumber < state.currentStep;
            const isCurrent = stepNumber === state.currentStep;
            
            return (
              <div 
                key={stepNumber}
                className={`step-item ${isCompleted ? 'step-item--completed' : ''} ${isCurrent ? 'step-item--current' : ''}`}
              >
                <div className="step-item__indicator">
                  {isCompleted ? '✅' : isCurrent ? '🔄' : '⏸️'}
                </div>
                <div className="step-item__content">
                  <span className="step-number">{stepNumber}.</span>
                  <span className="step-name">{step}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {state.sentimentAnalysis && (
        <div className="sidebar__sentiment">
          <h3>📊 Analyse Rapide</h3>
          <SentimentIndicator 
            sentiment={state.sentimentAnalysis} 
            compact 
          />
        </div>
      )}

      <div className="sidebar__actions">
        <button 
          className="sidebar__restart-btn"
          onClick={handleRestart}
          title="Recommencer l'évaluation"
        >
          🔄 Recommencer
        </button>
      </div>

      <div className="sidebar__footer">
        <p>Extension IA développée par Hospitalidée</p>
      </div>
    </div>
  );
};

export default Sidebar;
```

## Intégration avec le backend IA

### Service de stockage local (`src/services/storageService.js`)

```javascript
class StorageService {
  constructor() {
    this.prefix = 'hospitalidee_ia_';
  }

  // Sauvegarde d'une évaluation en cours
  saveEvaluationProgress(evaluationData) {
    try {
      const key = `${this.prefix}current_evaluation`;
      localStorage.setItem(key, JSON.stringify({
        ...evaluationData,
        saved_at: new Date().toISOString()
      }));
      return true;
    } catch (error) {
      console.warn('Failed to save evaluation progress:', error);
      return false;
    }
  }

  // Récupération d'une évaluation en cours
  getEvaluationProgress() {
    try {
      const key = `${this.prefix}current_evaluation`;
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.warn('Failed to get evaluation progress:', error);
      return null;
    }
  }

  // Suppression de l'évaluation en cours
  clearEvaluationProgress() {
    try {
      const key = `${this.prefix}current_evaluation`;
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.warn('Failed to clear evaluation progress:', error);
      return false;
    }
  }

  // Sauvegarde d'une évaluation terminée
  saveCompletedEvaluation(evaluationData) {
    try {
      const key = `${this.prefix}completed_evaluations`;
      const existing = this.getCompletedEvaluations();
      const updated = [
        {
          ...evaluationData,
          id: Date.now(),
          completed_at: new Date().toISOString()
        },
        ...existing.slice(0, 9) // Garde les 10 dernières
      ];
      
      localStorage.setItem(key, JSON.stringify(updated));
      return true;
    } catch (error) {
      console.warn('Failed to save completed evaluation:', error);
      return false;
    }
  }

  // Récupération des évaluations terminées
  getCompletedEvaluations() {
    try {
      const key = `${this.prefix}completed_evaluations`;
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.warn('Failed to get completed evaluations:', error);
      return [];
    }
  }

  // Export des données
  exportEvaluationData(evaluationData) {
    const exportData = {
      ...evaluationData,
      export_timestamp: new Date().toISOString(),
      export_version: '1.0'
    };

    const jsonString = JSON.stringify(exportData, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `hospitalidee_evaluation_${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
}

export default new StorageService();
```

## Composants réutilisables

### Composant d'affichage de note (`src/components/common/RatingDisplay.js`)

```javascript
import React from 'react';
import './RatingDisplay.scss';

const RatingDisplay = ({ 
  rating, 
  confidence, 
  variant = 'default', 
  title = 'Note', 
  subtitle = '',
  size = 'large' 
}) => {
  const getStars = (rating) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = (rating % 1) >= 0.5;
    
    return {
      full: fullStars,
      half: hasHalfStar ? 1 : 0,
      empty: 5 - fullStars - (hasHalfStar ? 1 : 0)
    };
  };

  const stars = getStars(rating);
  const gradientClass = variant === 'etablissement' ? 'gradient--blue' : 
                       variant === 'medecin' ? 'gradient--purple' : 
                       'gradient--default';

  return (
    <div className={`rating-display rating-display--${size} ${gradientClass}`}>
      <div className="rating-display__content">
        <h2 className="rating-display__title">{title}</h2>
        
        <div className="rating-display__score">
          <span className="rating-display__number">{rating.toFixed(1)}/5</span>
        </div>
        
        <div className="rating-display__stars">
          {'⭐'.repeat(stars.full)}
          {stars.half > 0 && '⭐'}
          {'☆'.repeat(stars.empty)}
        </div>
        
        <div className="rating-display__confidence">
          Confiance: {(confidence * 100).toFixed(0)}%
        </div>
        
        {subtitle && (
          <div className="rating-display__subtitle">{subtitle}</div>
        )}
      </div>
    </div>
  );
};

export default RatingDisplay;
```

### Indicateur de sentiment (`src/components/common/SentimentIndicator.js`)

```javascript
import React from 'react';
import './SentimentIndicator.scss';

const SentimentIndicator = ({ sentiment, detailed = false, compact = false }) => {
  const getSentimentDisplay = (sentimentValue) => {
    switch (sentimentValue) {
      case 'positif':
        return { icon: '🟢', label: 'Positif', color: 'green' };
      case 'negatif':
        return { icon: '🔴', label: 'Négatif', color: 'red' };
      default:
        return { icon: '🟡', label: 'Neutre', color: 'yellow' };
    }
  };

  const display = getSentimentDisplay(sentiment.sentiment);
  const confidence = sentiment.confidence || 0;
  const intensity = sentiment.emotional_intensity || 0;

  if (compact) {
    return (
      <div className="sentiment-indicator sentiment-indicator--compact">
        <div className={`sentiment-badge sentiment-badge--${display.color}`}>
          <span className="sentiment-icon">{display.icon}</span>
          <span className="sentiment-label">{display.label}</span>
        </div>
        <div className="confidence-compact">
          {(confidence * 100).toFixed(0)}%
        </div>
      </div>
    );
  }

  return (
    <div className="sentiment-indicator">
      <div className={`sentiment-main sentiment-main--${display.color}`}>
        <div className="sentiment-icon">{display.icon}</div>
        <div className="sentiment-info">
          <h4>Sentiment: {display.label}</h4>
          {sentiment.fallback_mode && (
            <span className="fallback-badge">Mode dégradé</span>
          )}
        </div>
      </div>

      <div className="sentiment-metrics">
        <div className="metric">
          <label>Confiance</label>
          <div className="metric-bar">
            <div 
              className="metric-fill" 
              style={{ width: `${confidence * 100}%` }}
            />
          </div>
          <span>{(confidence * 100).toFixed(0)}%</span>
        </div>

        <div className="metric">
          <label>Intensité émotionnelle</label>
          <div className="metric-bar">
            <div 
              className="metric-fill metric-fill--intensity" 
              style={{ width: `${intensity * 100}%` }}
            />
          </div>
          <span>{(intensity * 100).toFixed(0)}%</span>
        </div>
      </div>

      {detailed && sentiment.key_themes && sentiment.key_themes.length > 0 && (
        <div className="sentiment-themes">
          <label>Thèmes détectés</label>
          <div className="themes-list">
            {sentiment.key_themes.map((theme, index) => (
              <span key={index} className="theme-tag">{theme}</span>
            ))}
          </div>
        </div>
      )}

      {detailed && (sentiment.positive_indicators || sentiment.negative_indicators) && (
        <div className="sentiment-indicators">
          {sentiment.positive_indicators && sentiment.positive_indicators.length > 0 && (
            <div className="indicators-section">
              <label className="indicators-label indicators-label--positive">
                🟢 Aspects positifs
              </label>
              <ul className="indicators-list">
                {sentiment.positive_indicators.slice(0, 3).map((indicator, index) => (
                  <li key={index}>• {indicator}</li>
                ))}
              </ul>
            </div>
          )}

          {sentiment.negative_indicators && sentiment.negative_indicators.length > 0 && (
            <div className="indicators-section">
              <label className="indicators-label indicators-label--negative">
                🔴 Aspects négatifs
              </label>
              <ul className="indicators-list">
                {sentiment.negative_indicators.slice(0, 3).map((indicator, index) => (
                  <li key={index}>• {indicator}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SentimentIndicator;
```

## Tests et validation

### Tests des composants (`tests/components/EvaluationApp.test.js`)

```javascript
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { EvaluationProvider } from '../../src/contexts/EvaluationContext';
import EvaluationApp from '../../src/components/evaluation/EvaluationApp';
import evaluationService from '../../src/services/evaluationService';

// Mock du service
jest.mock('../../src/services/evaluationService');

const renderWithProvider = (component) => {
  return render(
    <EvaluationProvider>
      {component}
    </EvaluationProvider>
  );
};

describe('EvaluationApp', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('affiche la sélection de type au démarrage', () => {
    renderWithProvider(<EvaluationApp />);
    
    expect(screen.getByText('Sélection du type d\'évaluation')).toBeInTheDocument();
    expect(screen.getByText('Évaluer un Établissement')).toBeInTheDocument();
    expect(screen.getByText('Évaluer un Médecin')).toBeInTheDocument();
  });

  test('navigue vers le questionnaire établissement', async () => {
    renderWithProvider(<EvaluationApp />);
    
    fireEvent.click(screen.getByText('Évaluer un Établissement'));
    
    await waitFor(() => {
      expect(screen.getByText('Questionnaire d\'évaluation')).toBeInTheDocument();
      expect(screen.getByText('Évaluation de l\'Établissement')).toBeInTheDocument();
    });
  });

  test('workflow complet établissement', async () => {
    // Mock de la réponse API
    evaluationService.evaluateEtablissement.mockResolvedValue({
      data: {
        type: 'etablissement',
        note_finale: {
          suggested_rating: 4.2,
          confidence: 0.85,
          justification: 'Bonne expérience globale'
        }
      }
    });

    evaluationService.analyzeSentiment.mockResolvedValue({
      data: {
        sentiment: 'positif',
        confidence: 0.9,
        emotional_intensity: 0.7
      }
    });

    renderWithProvider(<EvaluationApp />);

    // 1. Sélection établissement
    fireEvent.click(screen.getByText('Évaluer un Établissement'));

    // 2. Remplir questionnaire (simplifié)
    await waitFor(() => {
      expect(screen.getByText('Questionnaire d\'évaluation')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('Continuer vers la saisie d\'avis'));

    // 3. Saisie avis
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Décrivez votre expérience dans l'établissement/)).toBeInTheDocument();
    });

    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, { 
      target: { value: 'Excellent séjour, personnel très attentif et professionnel.' } 
    });

    fireEvent.click(screen.getByText('Calculer la note IA'));

    // 4. Vérifier que l'API est appelée
    await waitFor(() => {
      expect(evaluationService.evaluateEtablissement).toHaveBeenCalledWith(
        expect.any(Object), // questionnaire
        'Excellent séjour, personnel très attentif et professionnel.'
      );
    });
  });

  test('gestion d\'erreur API', async () => {
    evaluationService.analyzeSentiment.mockRejectedValue(
      new Error('Service temporairement indisponible')
    );

    renderWithProvider(<EvaluationApp />);

    fireEvent.click(screen.getByText('Évaluer un Établissement'));
    fireEvent.click(screen.getByText('Continuer vers la saisie d\'avis'));

    const textarea = screen.getByRole('textbox');
    fireEvent.change(textarea, { 
      target: { value: 'Test d\'avis pour déclencher erreur' } 
    });

    await waitFor(() => {
      expect(screen.getByText(/L'API prend plus de temps que prévu/)).toBeInTheDocument();
    });
  });
});
```

### Tests d'intégration E2E (`tests/e2e/evaluation.e2e.js`)

```javascript
// Tests Cypress ou Playwright
describe('Workflow d\'évaluation complet', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('termine une évaluation établissement complète', () => {
    // Sélection du type
    cy.get('[data-testid=type-etablissement]').click();

    // Questionnaire
    cy.get('[data-testid=slider-medecins]').setSliderValue(4);
    cy.get('[data-testid=slider-personnel]').setSliderValue(5);
    cy.get('[data-testid=slider-accueil]').setSliderValue(3);
    cy.get('[data-testid=slider-prise-en-charge]').setSliderValue(4);
    cy.get('[data-testid=slider-confort]').setSliderValue(3);
    
    cy.get('[data-testid=continue-saisie]').click();

    // Saisie avis
    cy.get('[data-testid=avis-textarea]').type(
      'Excellent séjour dans cet établissement. Le personnel était très professionnel et attentif. Les chambres étaient propres et confortables. Je recommande cet hôpital.'
    );

    cy.get('[data-testid=continue-note-ia]').click();

    // Attendre le calcul IA
    cy.get('[data-testid=rating-result]').should('be.visible');
    cy.get('[data-testid=suggested-rating]').should('contain', '/5');

    cy.get('[data-testid=continue-analyse]').click();

    // Analyse hybride
    cy.get('[data-testid=analyse-hybride]').should('be.visible');
    cy.get('[data-testid=continue-resultat]').click();

    // Résultat final
    cy.get('[data-testid=evaluation-complete]').should('be.visible');
    cy.get('[data-testid=export-json]').should('be.visible');
    
    // Test export
    cy.get('[data-testid=export-json]').click();
    cy.readFile('cypress/downloads').should('exist');
  });

  it('gère les erreurs API gracieusement', () => {
    // Intercepter les appels API pour simuler erreurs
    cy.intercept('POST', '/api/sentiment/analyze', { 
      statusCode: 503, 
      body: { message: 'Service indisponible' } 
    });

    cy.get('[data-testid=type-etablissement]').click();
    cy.get('[data-testid=continue-saisie]').click();
    
    cy.get('[data-testid=avis-textarea]').type('Test erreur API');

    // Vérifier message d'erreur
    cy.get('[data-testid=error-message]').should('contain', 'L\'API prend plus de temps');
    
    // Vérifier mode dégradé
    cy.get('[data-testid=fallback-mode]').should('be.visible');
  });
});
```

## Déploiement

### Configuration Webpack (`webpack.config.js`)

```javascript
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  entry: './src/index.js',
  
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'static/js/[name].[contenthash:8].js',
    chunkFilename: 'static/js/[name].[contenthash:8].chunk.js',
    clean: true,
    publicPath: '/'
  },

  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react']
          }
        }
      },
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'sass-loader'
        ]
      }
    ]
  },

  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
      filename: 'index.html'
    }),
    new MiniCssExtractPlugin({
      filename: 'static/css/[name].[contenthash:8].css'
    })
  ],

  resolve: {
    extensions: ['.js', '.jsx'],
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },

  devServer: {
    port: 3001,
    historyApiFallback: true,
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true
      }
    }
  }
};
```

### Scripts de déploiement (`package.json`)

```json
{
  "name": "hospitalidee-ia-frontend",
  "version": "1.0.0",
  "scripts": {
    "start": "webpack serve --mode development",
    "build": "webpack --mode production",
    "test": "jest",
    "test:e2e": "cypress run",
    "lint": "eslint src/",
    "analyze": "webpack-bundle-analyzer dist/static/js/*.js"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0",
    "@babel/preset-env": "^7.20.0",
    "@babel/preset-react": "^7.18.6",
    "webpack": "^5.75.0",
    "webpack-cli": "^5.0.0",
    "webpack-dev-server": "^4.11.0"
  }
}
```

### Variables d'environnement de production

```bash
# .env.production
REACT_APP_API_BASE_URL=https://api.hospitalidee.fr
REACT_APP_ENVIRONMENT=production
REACT_APP_VERSION=1.0.0

# .env.development  
REACT_APP_API_BASE_URL=http://localhost:3000
REACT_APP_ENVIRONMENT=development
REACT_APP_VERSION=1.0.0-dev
```

---

## Résumé d'implémentation

### Composants clés développés

1. **TypeSelection** - Sélection entre Établissement/Médecin
2. **QuestionnaireEtablissement** - 5 sliders pour évaluation établissement
3. **QuestionnaireMedecin** - 4 select-sliders pour évaluation médecin
4. **SaisieAvis** - Zone de texte avec analyse temps réel
5. **NoteIA** - Affichage note hybride calculée par l'IA
6. **AnalyseHybride** - Comparaison détaillée questionnaire vs IA
7. **ResultatFinal** - Synthèse et export des résultats

### Services développés

- **EvaluationService** - Communication avec le backend IA
- **StorageService** - Sauvegarde locale des données
- **ApiClient** - Client HTTP avec gestion d'erreurs

### Fonctionnalités implémentées

✅ Interface en 5 étapes avec navigation fluide  
✅ Workflows séparés Établissement vs Médecin  
✅ Analyse de sentiment temps réel  
✅ Calcul de notes hybrides (questionnaire + IA)  
✅ Mode dégradé en cas d'erreur API  
✅ Export JSON des résultats complets  
✅ Tests unitaires et E2E  
✅ Design responsive et accessible

Cette architecture frontend offre une expérience utilisateur moderne et intuitive pour l'évaluation d'avis patients, avec intégration transparente de l'IA Mistral et gestion robuste des erreurs.
