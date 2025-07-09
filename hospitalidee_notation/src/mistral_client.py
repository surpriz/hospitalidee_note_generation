"""
Client Mistral AI pour l'extension Hospitalidée
Implémentation selon les Cursor rules avec gestion robuste des erreurs
"""

import json
import time
import hashlib
from typing import Dict, Any, Optional
from functools import lru_cache
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

from config.settings import settings
from config.prompts import (
    SENTIMENT_ANALYSIS_PROMPT, 
    RATING_CALCULATION_PROMPT,
    COHERENCE_CHECK_PROMPT,
    TITLE_GENERATION_PROMPT
)


class MistralClient:
    """Client pour l'API Mistral AI avec gestion d'erreurs et cache"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le client Mistral AI
        
        Args:
            api_key: Clé API Mistral. Si None, utilise settings.mistral_api_key
        """
        self.api_key = api_key or settings.mistral_api_key
        self.base_url = "https://api.mistral.ai/v1/chat/completions"
        self.model = settings.mistral_model
        
        # Configuration des paramètres selon Cursor rules
        self.default_params = {
            "temperature": settings.mistral_temperature,
            "max_tokens": settings.mistral_max_tokens,
            "top_p": settings.mistral_top_p,
            "presence_penalty": settings.mistral_presence_penalty,
            "frequency_penalty": settings.mistral_frequency_penalty
        }
        
        # Configuration session avec retry
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Headers par défaut
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        self.logger = logging.getLogger(__name__)
    
    def _generate_cache_key(self, prompt: str, **kwargs) -> str:
        """Génère une clé de cache basée sur le prompt et les paramètres"""
        content = f"{prompt}_{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    @lru_cache(maxsize=100)
    def _cached_api_call(self, cache_key: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Appel API avec cache LRU"""
        return self._make_api_call(prompt, **kwargs)
    
    def _make_api_call(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Fait un appel à l'API Mistral AI
        
        Args:
            prompt: Le prompt à envoyer
            **kwargs: Paramètres additionnels pour l'API
            
        Returns:
            dict: Réponse de l'API Mistral
            
        Raises:
            Exception: En cas d'erreur API ou de timeout
        """
        start_time = time.time()
        
        # Préparation de la requête
        params = {**self.default_params, **kwargs}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            **params
        }
        
        try:
            # Appel API avec timeout selon Cursor rules
            response = self.session.post(
                self.base_url,
                json=payload,
                timeout=settings.max_response_time
            )
            response.raise_for_status()
            
            # Vérification du temps de réponse
            elapsed_time = time.time() - start_time
            if elapsed_time > settings.max_response_time:
                self.logger.warning(f"Appel API lent: {elapsed_time:.2f}s")
            
            result = response.json()
            
            # Extraction du contenu
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                try:
                    # Tentative de parsing JSON avec gestion des balises markdown
                    return self._parse_json_response(content)
                except json.JSONDecodeError:
                    self.logger.error(f"Réponse non-JSON: {content}")
                    return {"error": "Invalid JSON response", "raw_content": content}
            else:
                raise Exception("Aucune réponse dans le résultat Mistral")
                
        except requests.exceptions.Timeout:
            self.logger.error("Timeout de l'API Mistral")
            raise Exception("Timeout de l'API Mistral")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erreur réseau: {e}")
            raise Exception(f"Erreur réseau: {e}")
        except Exception as e:
            self.logger.error(f"Erreur inattendue: {e}")
            raise
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response en gérant les formats markdown"""
        try:
            # Nettoyer le contenu des balises markdown potentielles
            content = content.strip()
            
            # Supprimer les balises ```json et ``` si présentes
            if content.startswith('```json'):
                content = content[7:]  # Enlever ```json
            if content.startswith('```'):
                content = content[3:]   # Enlever ``` simple
            if content.endswith('```'):
                content = content[:-3]  # Enlever ``` de fin
                
            content = content.strip()
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            logging.warning(f"Réponse non-JSON: {content}")
            return {"error": "Invalid JSON response", "raw_content": content}
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyse le sentiment d'un texte d'avis patient
        
        Args:
            text: Texte de l'avis à analyser
            
        Returns:
            dict: Résultat de l'analyse de sentiment
        """
        prompt = SENTIMENT_ANALYSIS_PROMPT.format(text=text)
        cache_key = self._generate_cache_key(prompt)
        
        try:
            result = self._cached_api_call(cache_key, prompt)
            
            # Validation du format de réponse selon Cursor rules
            required_fields = ["sentiment", "confidence", "emotional_intensity"]
            if not all(field in result for field in required_fields):
                self.logger.error(f"Champs manquants dans la réponse: {result}")
                raise Exception("Format de réponse invalide")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse de sentiment: {e}")
            # Mode dégradé selon Cursor rules
            return {
                "sentiment": "neutre",
                "confidence": 0.0,
                "emotional_intensity": 0.5,
                "positive_indicators": [],
                "negative_indicators": [],
                "key_themes": [],
                "error": str(e)
            }
    
    def calculate_rating(self, sentiment_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule une note sur 5 basée sur l'analyse de sentiment
        
        Args:
            sentiment_analysis: Résultat de l'analyse de sentiment
            
        Returns:
            dict: Note suggérée avec justification
        """
        prompt = RATING_CALCULATION_PROMPT.format(
            sentiment_analysis=json.dumps(sentiment_analysis, ensure_ascii=False)
        )
        cache_key = self._generate_cache_key(prompt)
        
        try:
            result = self._cached_api_call(cache_key, prompt)
            
            # Validation de la note selon Cursor rules (1-5)
            if "suggested_rating" in result:
                rating = result["suggested_rating"]
                if not (1 <= rating <= 5):
                    self.logger.warning(f"Note hors limites: {rating}")
                    result["suggested_rating"] = max(1, min(5, rating))
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul de note: {e}")
            # Mode dégradé selon Cursor rules
            sentiment = sentiment_analysis.get("sentiment", "neutre")
            fallback_rating = 3  # Neutre par défaut
            if sentiment == "positif":
                fallback_rating = 4
            elif sentiment == "negatif":
                fallback_rating = 2
                
            return {
                "suggested_rating": fallback_rating,
                "confidence": 0.0,
                "justification": "Calcul en mode dégradé suite à une erreur",
                "rating_factors": {
                    "sentiment_impact": 0.5,
                    "intensity_impact": 0.5,
                    "content_richness": 0.5
                },
                "error": str(e)
            }
    
    def check_coherence(self, partial_ratings: Dict[str, int], verbatim: str) -> Dict[str, Any]:
        """
        Vérifie la cohérence entre notes partielles et verbatim
        
        Args:
            partial_ratings: Notes partielles (médecins, personnel, etc.)
            verbatim: Texte de l'avis
            
        Returns:
            dict: Résultat de la vérification de cohérence
        """
        moyenne = sum(partial_ratings.values()) / len(partial_ratings)
        
        prompt = COHERENCE_CHECK_PROMPT.format(
            medecins=partial_ratings.get("medecins", 0),
            personnel=partial_ratings.get("personnel", 0),
            prise_en_charge=partial_ratings.get("prise_en_charge", 0),
            hotellerie=partial_ratings.get("hotellerie", 0),
            moyenne=moyenne,
            verbatim=verbatim
        )
        cache_key = self._generate_cache_key(prompt)
        
        try:
            result = self._cached_api_call(cache_key, prompt)
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification de cohérence: {e}")
            # Mode dégradé selon Cursor rules
            return {
                "is_coherent": True,
                "coherence_score": 0.5,
                "discrepancies": [],
                "suggested_adjustments": [],
                "global_rating_suggestion": moyenne,
                "confidence": 0.0,
                "explanation": "Vérification en mode dégradé",
                "error": str(e)
            }
    
    def generate_title(self, sentiment_analysis: Dict[str, Any], rating: float, text: str) -> Dict[str, Any]:
        """
        Génère un titre suggéré pour l'avis
        
        Args:
            sentiment_analysis: Analyse de sentiment
            rating: Note calculée
            text: Texte original
            
        Returns:
            dict: Titre suggéré et alternatives
        """
        prompt = TITLE_GENERATION_PROMPT.format(
            sentiment_analysis=json.dumps(sentiment_analysis, ensure_ascii=False),
            rating=rating,
            text=text
        )
        cache_key = self._generate_cache_key(prompt)
        
        try:
            result = self._cached_api_call(cache_key, prompt)
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de titre: {e}")
            # Mode dégradé selon Cursor rules
            sentiment = sentiment_analysis.get("sentiment", "neutre")
            fallback_title = f"Avis {sentiment} sur mon séjour"
            
            return {
                "suggested_title": fallback_title,
                "alternative_titles": [
                    "Mon expérience à l'hôpital",
                    "Retour sur ma prise en charge"
                ],
                "main_theme": "general",
                "confidence": 0.0,
                "error": str(e)
            } 