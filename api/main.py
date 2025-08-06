"""
🏥 Hospitalidée IA - API REST Ultra-Simple
===========================================

API complète pour génération automatique de notes d'avis patients.
UN SEUL ENDPOINT POUR TOUT FAIRE !

Utilisation:
  python main.py

API disponible sur: http://localhost:8000
Documentation: http://localhost:8000/docs

Auteur: Hospitalidée
Version: 1.0.0
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Union
import traceback

# FastAPI imports
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Ajout du chemin pour les imports locaux
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import des modules IA
from src.mistral_client import MistralClient
from src.sentiment_analyzer import SentimentAnalyzer  
from src.rating_calculator import RatingCalculator
from config.settings import settings

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hospitalidee_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialisation FastAPI
app = FastAPI(
    title="🏥 Hospitalidée IA API",
    description="""
    **API Ultra-Simple pour génération automatique de notes d'avis patients**
    
    🎯 **UN SEUL ENDPOINT POUR TOUT** - `/evaluate`
    
    Envoyez un questionnaire + avis textuel → Recevez une note sur 5 !
    
    ✅ **Fonctionnalités:**
    - Analyse de sentiment avec Mistral AI
    - Calcul de notes hybrides (questionnaire + IA)
    - Workflows séparés Établissement/Médecin
    - Mode dégradé en cas d'erreur
    - Génération de titres automatique
    
    🚀 **Ultra-simple à utiliser:** 1 appel API = résultat complet
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - Autorise tous les domaines (à restreindre en production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation des services IA (une seule fois au démarrage)
mistral_client = None
sentiment_analyzer = None
rating_calculator = None

@app.on_event("startup")
async def startup_event():
    """Initialisation des services IA au démarrage"""
    global mistral_client, sentiment_analyzer, rating_calculator
    
    try:
        logger.info("🚀 Démarrage Hospitalidée IA API...")
        
        # Vérification clé API Mistral
        if not settings.mistral_api_key:
            logger.error("❌ MISTRAL_API_KEY manquante ! Configurez votre .env")
            raise ValueError("MISTRAL_API_KEY requise")
        
        # Initialisation services
        mistral_client = MistralClient()
        sentiment_analyzer = SentimentAnalyzer(mistral_client)
        rating_calculator = RatingCalculator(mistral_client)
        
        logger.info("✅ Services IA initialisés avec succès")
        logger.info(f"📊 Modèle Mistral: {settings.mistral_model}")
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation: {str(e)}")
        raise

# ============== MODÈLES DE DONNÉES ==============

class QuestionnaireEtablissement(BaseModel):
    """Questionnaire d'évaluation pour un établissement de santé"""
    medecins: int = Field(..., ge=1, le=5, description="Relation avec les médecins (1=très mauvais, 5=excellent)")
    personnel: int = Field(..., ge=1, le=5, description="Relation avec le personnel (1=très mauvais, 5=excellent)")
    accueil: int = Field(..., ge=1, le=5, description="Qualité de l'accueil (1=très mauvais, 5=excellent)")
    prise_en_charge: int = Field(..., ge=1, le=5, description="Prise en charge jusqu'à la sortie (1=très mauvais, 5=excellent)")
    confort: int = Field(..., ge=1, le=5, description="Confort des chambres et repas (1=très mauvais, 5=excellent)")

    class Config:
        schema_extra = {
            "example": {
                "medecins": 4,
                "personnel": 5, 
                "accueil": 3,
                "prise_en_charge": 4,
                "confort": 3
            }
        }


class QuestionnaireMedecin(BaseModel):
    """Questionnaire d'évaluation pour un médecin"""
    explications: str = Field(..., description="Qualité des explications données")
    confiance: str = Field(..., description="Sentiment de confiance inspiré")
    motivation: str = Field(..., description="Motivation dans les prescriptions")
    respect: str = Field(..., description="Respect de votre identité de patient")

    class Config:
        schema_extra = {
            "example": {
                "explications": "Bonnes",
                "confiance": "Bonne confiance", 
                "motivation": "Bien motivé",
                "respect": "Très respectueux"
            }
        }


class EvaluationRequest(BaseModel):
    """Requête complète d'évaluation - UN SEUL APPEL POUR TOUT !"""
    
    type_evaluation: str = Field(
        ..., 
        regex="^(etablissement|medecin)$", 
        description="Type d'évaluation: 'etablissement' ou 'medecin'"
    )
    
    avis_text: str = Field(
        ..., 
        min_length=20, 
        max_length=5000,
        description="Texte de l'avis patient (minimum 20 caractères)"
    )
    
    questionnaire_etablissement: Optional[QuestionnaireEtablissement] = Field(
        None, 
        description="Questionnaire établissement (requis si type_evaluation='etablissement')"
    )
    
    questionnaire_medecin: Optional[QuestionnaireMedecin] = Field(
        None,
        description="Questionnaire médecin (requis si type_evaluation='medecin')"
    )
    
    # Options
    generer_titre: bool = Field(default=True, description="Générer un titre suggéré pour l'avis")
    analyse_detaillee: bool = Field(default=True, description="Inclure l'analyse détaillée dans la réponse")

    class Config:
        schema_extra = {
            "example": {
                "type_evaluation": "etablissement",
                "avis_text": "Séjour globalement satisfaisant dans cet établissement. Le personnel était très attentif et professionnel. Les médecins ont pris le temps d'expliquer les traitements. Seul bémol, l'attente aux urgences était un peu longue.",
                "questionnaire_etablissement": {
                    "medecins": 4,
                    "personnel": 5,
                    "accueil": 3, 
                    "prise_en_charge": 4,
                    "confort": 3
                },
                "generer_titre": True,
                "analyse_detaillee": True
            }
        }


class EvaluationResponse(BaseModel):
    """Réponse complète de l'évaluation - TOUT EN UN !"""
    
    # === RÉSULTAT PRINCIPAL ===
    note_finale: float = Field(..., description="Note finale sur 5 (résultat principal)")
    confiance: float = Field(..., ge=0, le=1, description="Niveau de confiance de l'IA (0-1)")
    
    # === ANALYSE SENTIMENT ===
    sentiment: str = Field(..., description="Sentiment global: 'positif', 'neutre' ou 'negatif'")
    intensite_emotionnelle: float = Field(..., ge=0, le=1, description="Intensité émotionnelle (0-1)")
    
    # === EXTRAS ===
    titre_suggere: Optional[str] = Field(None, description="Titre suggéré pour l'avis")
    
    # === DÉTAILS (optionnel) ===
    analyse_detaillee: Optional[Dict[str, Any]] = Field(None, description="Analyse complète détaillée")
    
    # === MÉTADONNÉES ===
    timestamp: str = Field(..., description="Horodatage de l'évaluation")
    type_evaluation: str = Field(..., description="Type d'évaluation effectuée")
    duree_traitement_ms: int = Field(..., description="Durée du traitement en millisecondes")
    
    # === MODE DÉGRADÉ ===
    mode_degrade: bool = Field(default=False, description="True si l'IA fonctionne en mode dégradé")
    
    class Config:
        schema_extra = {
            "example": {
                "note_finale": 3.8,
                "confiance": 0.85,
                "sentiment": "positif",
                "intensite_emotionnelle": 0.7,
                "titre_suggere": "Séjour globalement satisfaisant",
                "timestamp": "2024-01-15T14:30:00Z",
                "type_evaluation": "etablissement",
                "duree_traitement_ms": 2500,
                "mode_degrade": False
            }
        }


# ============== ENDPOINT PRINCIPAL ==============

@app.post("/evaluate", response_model=EvaluationResponse, tags=["🎯 Évaluation principale"])
async def evaluer_avis_complet(request: EvaluationRequest) -> EvaluationResponse:
    """
    🎯 **ENDPOINT PRINCIPAL - TOUT EN UN !**
    
    Analyse complète d'un avis patient en une seule requête :
    
    1. **Questionnaire fermé** → note de base  
    2. **Avis textuel** → analyse sentiment avec Mistral AI
    3. **Calcul hybride** → note finale pondérée
    4. **Génération titre** (optionnel)
    
    **USAGE ULTRA-SIMPLE :**
    ```javascript
    const response = await fetch('/evaluate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            type_evaluation: "etablissement",
            avis_text: "Séjour excellent, personnel attentif...",
            questionnaire_etablissement: {
                medecins: 4, personnel: 5, accueil: 3,
                prise_en_charge: 4, confort: 3
            }
        })
    });
    const result = await response.json();
    console.log(`Note: ${result.note_finale}/5`);
    ```
    
    **RETOURNE :** Note finale + sentiment + analyse complète
    """
    
    start_time = datetime.now()
    
    try:
        logger.info(f"🏥 Nouvelle évaluation {request.type_evaluation} - Texte: {len(request.avis_text)} caractères")
        
        # ===== 1. VALIDATION STRICTE =====
        if request.type_evaluation == "etablissement" and not request.questionnaire_etablissement:
            raise HTTPException(
                status_code=400, 
                detail="questionnaire_etablissement requis pour type_evaluation='etablissement'"
            )
        
        if request.type_evaluation == "medecin" and not request.questionnaire_medecin:
            raise HTTPException(
                status_code=400,
                detail="questionnaire_medecin requis pour type_evaluation='medecin'"
            )
        
        # ===== 2. CALCUL NOTE QUESTIONNAIRE =====
        if request.type_evaluation == "etablissement":
            q = request.questionnaire_etablissement
            note_questionnaire = (q.medecins + q.personnel + q.accueil + 
                                q.prise_en_charge + q.confort) / 5.0
            details_questionnaire = q.dict()
        else:
            note_questionnaire = _convert_medecin_questionnaire_to_rating(request.questionnaire_medecin)
            details_questionnaire = request.questionnaire_medecin.dict()
        
        logger.info(f"📊 Note questionnaire: {note_questionnaire:.1f}/5")
        
        # ===== 3. ANALYSE SENTIMENT AVEC MISTRAL IA =====
        logger.info("🔍 Analyse sentiment en cours...")
        try:
            sentiment_result = sentiment_analyzer.analyze_sentiment(request.avis_text)
            logger.info(f"😊 Sentiment: {sentiment_result.get('sentiment', 'inconnu')}")
        except Exception as e:
            logger.warning(f"⚠️ Erreur sentiment, mode dégradé: {str(e)}")
            sentiment_result = _analyze_sentiment_fallback(request.avis_text)
        
        # ===== 4. CALCUL NOTE HYBRIDE AVEC MISTRAL IA =====
        logger.info("⚖️ Calcul note hybride en cours...")
        try:
            rating_result = rating_calculator.calculate_rating_from_text(
                text=request.avis_text,
                sentiment_analysis=sentiment_result,
                questionnaire_context=note_questionnaire
            )
            logger.info(f"🎯 Note hybride: {rating_result.get('suggested_rating', 0):.1f}/5")
        except Exception as e:
            logger.warning(f"⚠️ Erreur calcul hybride, mode dégradé: {str(e)}")
            rating_result = _calculate_rating_fallback(note_questionnaire, sentiment_result)
        
        # ===== 5. GÉNÉRATION TITRE (optionnel) =====
        titre_suggere = None
        if request.generer_titre:
            titre_suggere = _generer_titre_intelligent(
                sentiment_result.get('sentiment', 'neutre'),
                rating_result.get('suggested_rating', note_questionnaire),
                request.type_evaluation,
                request.avis_text
            )
        
        # ===== 6. COMPILATION ANALYSE DÉTAILLÉE =====
        analyse_detaillee = None
        if request.analyse_detaillee:
            duree_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            analyse_detaillee = {
                "questionnaire": {
                    "note": round(note_questionnaire, 1),
                    "details": details_questionnaire
                },
                "sentiment": sentiment_result,
                "calcul_hybride": rating_result,
                "performance": {
                    "duree_traitement_ms": duree_ms,
                    "modele_mistral": settings.mistral_model,
                    "timestamp_debut": start_time.isoformat()
                }
            }
        
        # ===== 7. RÉPONSE FINALE =====
        note_finale = rating_result.get('suggested_rating', note_questionnaire)
        mode_degrade = (sentiment_result.get('fallback_mode', False) or 
                       rating_result.get('fallback_mode', False))
        
        duree_totale_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        response = EvaluationResponse(
            note_finale=round(float(note_finale), 1),
            confiance=float(rating_result.get('confidence', 0.8)),
            sentiment=sentiment_result.get('sentiment', 'neutre'),
            intensite_emotionnelle=float(sentiment_result.get('emotional_intensity', 0.5)),
            titre_suggere=titre_suggere,
            analyse_detaillee=analyse_detaillee,
            timestamp=datetime.now().isoformat(),
            type_evaluation=request.type_evaluation,
            duree_traitement_ms=duree_totale_ms,
            mode_degrade=mode_degrade
        )
        
        logger.info(f"✅ Évaluation terminée - Note: {response.note_finale}/5 - Sentiment: {response.sentiment} - Durée: {duree_totale_ms}ms")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur critique: {str(e)}")
        logger.error(traceback.format_exc())
        
        # MODE DÉGRADÉ ULTIME
        try:
            duree_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            note_fallback = 3.0
            if 'note_questionnaire' in locals():
                note_fallback = note_questionnaire
                
            return EvaluationResponse(
                note_finale=note_fallback,
                confiance=0.0,
                sentiment=_analyze_sentiment_simple(request.avis_text),
                intensite_emotionnelle=0.5,
                titre_suggere=f"Avis {request.type_evaluation}" if request.generer_titre else None,
                analyse_detaillee={"erreur": str(e)} if request.analyse_detaillee else None,
                timestamp=datetime.now().isoformat(),
                type_evaluation=request.type_evaluation,
                duree_traitement_ms=duree_ms,
                mode_degrade=True
            )
        except:
            raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


# ============== ENDPOINTS BONUS ==============

@app.post("/sentiment", tags=["📊 Analyse seule"])
async def analyser_sentiment_seul(text: str = Field(..., min_length=10)):
    """
    Analyse de sentiment rapide (sans questionnaire)
    Utile pour tests ou analyse temps réel
    """
    try:
        result = sentiment_analyzer.analyze_sentiment(text)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Erreur sentiment: {str(e)}")
        return {"status": "error", "message": str(e), "data": _analyze_sentiment_fallback(text)}


@app.get("/health", tags=["🔧 Système"])
async def verifier_sante():
    """
    Vérification que l'API et l'IA fonctionnent correctement
    Utile pour monitoring et tests d'installation
    """
    try:
        # Test basique Mistral
        test_sentiment = sentiment_analyzer.analyze_sentiment("Test de fonctionnement de l'API")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "mistral_api": "ok",
                "sentiment_analyzer": "ok", 
                "rating_calculator": "ok"
            },
            "config": {
                "modele_mistral": settings.mistral_model,
                "version": "1.0.0"
            },
            "test_result": test_sentiment.get('sentiment', 'ok')
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "services": {
                "mistral_api": "error",
                "sentiment_analyzer": "degraded",
                "rating_calculator": "degraded"
            }
        }


@app.get("/", tags=["📖 Documentation"])
async def accueil():
    """Page d'accueil de l'API"""
    return {
        "message": "🏥 Bienvenue sur l'API Hospitalidée IA !",
        "description": "API pour génération automatique de notes d'avis patients",
        "documentation": "/docs",
        "endpoint_principal": "/evaluate",
        "health_check": "/health",
        "version": "1.0.0"
    }


# ============== FONCTIONS UTILITAIRES ==============

def _convert_medecin_questionnaire_to_rating(questionnaire: QuestionnaireMedecin) -> float:
    """Convertit les réponses texte du questionnaire médecin en note numérique"""
    
    mapping = {
        # Explications
        "Très insuffisantes": 1, "Insuffisantes": 2, "Correctes": 3, "Bonnes": 4, "Excellentes": 5,
        # Confiance
        "Aucune confiance": 1, "Peu de confiance": 2, "Confiance modérée": 3, 
        "Bonne confiance": 4, "Confiance totale": 5,
        # Motivation  
        "Aucune motivation": 1, "Peu motivé": 2, "Moyennement motivé": 3,
        "Bien motivé": 4, "Très motivé": 5,
        # Respect
        "Pas du tout": 1, "Peu respectueux": 2, "Modérément respectueux": 3,
        "Respectueux": 4, "Très respectueux": 5
    }
    
    scores = [
        mapping.get(questionnaire.explications, 3),
        mapping.get(questionnaire.confiance, 3),
        mapping.get(questionnaire.motivation, 3), 
        mapping.get(questionnaire.respect, 3)
    ]
    
    return sum(scores) / len(scores)


def _generer_titre_intelligent(sentiment: str, rating: float, type_eval: str, texte: str) -> str:
    """Génère un titre intelligent basé sur l'analyse"""
    
    # Analyse de mots-clés dans le texte
    texte_lower = texte.lower()
    
    if sentiment == "positif" and rating >= 4.5:
        if "excellent" in texte_lower or "parfait" in texte_lower:
            return f"Expérience exceptionnelle - {type_eval} recommandé"
        return f"Très satisfait de cet {type_eval}"
    
    elif sentiment == "positif" and rating >= 3.5:
        if "satisfait" in texte_lower:
            return f"Expérience satisfaisante dans cet {type_eval}"
        return f"Bon {type_eval} - expérience positive"
    
    elif sentiment == "negatif" and rating <= 2:
        if "déçu" in texte_lower or "problème" in texte_lower:
            return f"Expérience décevante - {type_eval} à éviter"
        return f"Nombreux points d'amélioration pour cet {type_eval}"
    
    elif sentiment == "negatif":
        return f"Avis mitigé sur cet {type_eval}"
    
    else:
        if "correct" in texte_lower or "bien" in texte_lower:
            return f"Avis nuancé sur cet {type_eval}"
        return f"Retour d'expérience sur cet {type_eval}"


def _analyze_sentiment_fallback(text: str) -> Dict[str, Any]:
    """Analyse de sentiment en mode dégradé (sans IA)"""
    sentiment_simple = _analyze_sentiment_simple(text)
    
    return {
        "sentiment": sentiment_simple,
        "confidence": 0.0,
        "emotional_intensity": 0.5,
        "positive_indicators": [],
        "negative_indicators": [],
        "key_themes": [],
        "fallback_mode": True,
        "error": "IA Mistral indisponible - analyse locale"
    }


def _analyze_sentiment_simple(text: str) -> str:
    """Analyse sentiment locale très simple"""
    text_lower = text.lower()
    
    positive_words = ["excellent", "parfait", "recommande", "satisfait", "content", "bien", "bon", "super", "génial", "formidable"]
    negative_words = ["déçu", "problème", "mauvais", "nul", "inadmissible", "froid", "décevant", "catastrophe", "horrible"]
    
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        return "positif"
    elif neg_count > pos_count:
        return "negatif"
    else:
        return "neutre"


def _calculate_rating_fallback(questionnaire_note: float, sentiment_result: Dict[str, Any]) -> Dict[str, Any]:
    """Calcul de note en mode dégradé"""
    sentiment = sentiment_result.get('sentiment', 'neutre')
    
    # Ajustement simple basé sur le sentiment
    if sentiment == "positif":
        note_finale = min(5.0, questionnaire_note + 0.5)
    elif sentiment == "negatif":
        note_finale = max(1.0, questionnaire_note - 0.5)
    else:
        note_finale = questionnaire_note
    
    return {
        "suggested_rating": note_finale,
        "confidence": 0.0,
        "justification": f"Mode dégradé: questionnaire ({questionnaire_note}) ajusté selon sentiment ({sentiment})",
        "factors": {
            "questionnaire_weight": 0.8,
            "sentiment_weight": 0.2,
            "intensity_weight": 0.0,
            "content_weight": 0.0
        },
        "fallback_mode": True
    }


# ============== GESTION D'ERREURS GLOBALE ==============

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire d'erreurs global pour éviter les crashes"""
    logger.error(f"Erreur non gérée: {str(exc)}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erreur interne du serveur",
            "message": str(exc) if settings.debug_mode else "Une erreur inattendue s'est produite",
            "timestamp": datetime.now().isoformat()
        }
    )


# ============== DÉMARRAGE ==============

if __name__ == "__main__":
    print("🏥 Démarrage Hospitalidée IA API...")
    print(f"📊 Modèle Mistral: {settings.mistral_model}")
    print(f"🔑 API Key configurée: {'✅' if settings.mistral_api_key else '❌'}")
    print("📖 Documentation disponible sur: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
        access_log=True
    )