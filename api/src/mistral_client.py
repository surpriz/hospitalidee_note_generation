"""
Client Mistral AI pour l'API Hospitalidée
Implémentation selon les Cursor rules avec gestion robuste des erreurs
Version optimisée pour l'API REST
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
    HYBRID_RATING_CALCULATION_PROMPT,
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
        self.logger = logging.getLogger(__name__)
        
        # Configuration des paramètres selon Cursor rules
        self.default_params = {
            "temperature": settings.mistral_temperature,
            "max_tokens": settings.mistral_max_tokens,
            "top_p": settings.mistral_top_p,
            "presence_penalty": settings.mistral_presence_penalty,
            "frequency_penalty": settings.mistral_frequency_penalty
        }
        
        # Configuration session avec retry améliorée
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "POST"],
            backoff_factor=1,
            respect_retry_after_header=True
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Headers par défaut
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Hospitalidee-IA-API/1.0.0'
        })
        
        # Cache simple en mémoire pour éviter les appels répétés
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    def _get_cache_key(self, prompt: str, params: Dict[str, Any]) -> str:
        """Génère une clé de cache pour un prompt et des paramètres"""
        cache_data = f"{prompt}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Vérifie si une entrée de cache est encore valide"""
        return (time.time() - cache_entry['timestamp']) < self._cache_ttl
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Récupère un résultat du cache s'il est valide"""
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if self._is_cache_valid(entry):
                self.logger.debug("Résultat servi depuis le cache")
                return entry['result']
            else:
                # Nettoie l'entrée expirée
                del self._cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Sauvegarde un résultat dans le cache"""
        self._cache[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }
        
        # Nettoyage périodique du cache (garde les 100 dernières entrées)
        if len(self._cache) > 100:
            # Supprime les entrées les plus anciennes
            sorted_entries = sorted(
                self._cache.items(), 
                key=lambda x: x[1]['timestamp']
            )
            # Garde les 50 plus récentes
            self._cache = dict(sorted_entries[-50:])
    
    def _make_api_request(self, prompt: str, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Effectue une requête vers l'API Mistral AI
        
        Args:
            prompt: Le prompt à envoyer
            custom_params: Paramètres personnalisés pour cette requête
            
        Returns:
            dict: Réponse parsée de l'API
            
        Raises:
            Exception: En cas d'erreur API ou de parsing
        """
        # Préparation des paramètres
        params = self.default_params.copy()
        if custom_params:
            params.update(custom_params)
        
        # Vérification du cache
        cache_key = self._get_cache_key(prompt, params)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Préparation de la requête
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            **params
        }
        
        try:
            start_time = time.time()
            self.logger.info("🤖 Envoi requête Mistral AI...")
            
            response = self.session.post(
                self.base_url,
                json=payload,
                timeout=settings.max_response_time
            )
            
            duration = time.time() - start_time
            self.logger.info(f"⏱️ Réponse Mistral reçue en {duration:.2f}s")
            
            # Vérification du status code
            if response.status_code == 200:
                response_data = response.json()
                
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    content = response_data['choices'][0]['message']['content']
                    
                    # Parsing du JSON retourné par Mistral
                    result = self._parse_mistral_response(content)
                    
                    # Mise en cache
                    self._save_to_cache(cache_key, result)
                    
                    return result
                else:
                    raise Exception("Réponse Mistral vide ou malformée")
            
            elif response.status_code == 401:
                raise Exception("Clé API Mistral invalide")
            elif response.status_code == 429:
                raise Exception("Limite de taux Mistral atteinte - veuillez patienter")
            elif response.status_code == 503:
                raise Exception("Service Mistral temporairement indisponible")
            else:
                raise Exception(f"Erreur API Mistral: {response.status_code}")
                
        except requests.exceptions.Timeout:
            raise Exception(f"Timeout API Mistral (>{settings.max_response_time}s)")
        except requests.exceptions.ConnectionError:
            raise Exception("Erreur de connexion à l'API Mistral")
        except Exception as e:
            self.logger.error(f"❌ Erreur API Mistral: {str(e)}")
            raise
    
    def _parse_mistral_response(self, content: str) -> Dict[str, Any]:
        """
        Parse la réponse de Mistral (JSON dans du texte)
        
        Args:
            content: Contenu retourné par Mistral
            
        Returns:
            dict: Données parsées
            
        Raises:
            Exception: Si le parsing échoue
        """
        try:
            # Nettoie les balises markdown si présentes
            cleaned_content = content.strip()
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:]
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-3]
            
            cleaned_content = cleaned_content.strip()
            
            # Parse le JSON
            result = json.loads(cleaned_content)
            
            self.logger.debug("✅ Réponse Mistral parsée avec succès")
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Erreur parsing JSON Mistral: {str(e)}")
            self.logger.error(f"Contenu reçu: {content[:200]}...")
            raise Exception(f"Réponse Mistral non-JSON: {str(e)}")
    
    # ============== MÉTHODES PUBLIQUES ==============
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyse le sentiment d'un texte d'avis patient
        
        Args:
            text: Texte à analyser
            
        Returns:
            dict: Résultat de l'analyse de sentiment
        """
        if not text or len(text.strip()) < 5:
            raise Exception("Texte trop court pour l'analyse")
        
        prompt = SENTIMENT_ANALYSIS_PROMPT.format(text=text.strip())
        
        try:
            result = self._make_api_request(prompt)
            
            # Validation du résultat
            required_fields = ['sentiment', 'confidence', 'emotional_intensity']
            for field in required_fields:
                if field not in result:
                    raise Exception(f"Champ manquant dans la réponse: {field}")
            
            # Validation des valeurs
            if result['sentiment'] not in ['positif', 'negatif', 'neutre']:
                raise Exception("Sentiment invalide dans la réponse")
            
            if not (0 <= result['confidence'] <= 1):
                raise Exception("Confiance hors limites [0-1]")
            
            if not (0 <= result['emotional_intensity'] <= 1):
                raise Exception("Intensité émotionnelle hors limites [0-1]")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur analyse sentiment: {str(e)}")
            raise
    
    def calculate_rating(self, sentiment_analysis: Dict[str, Any], text: str = "") -> Dict[str, Any]:
        """
        Calcule une note basée sur l'analyse de sentiment
        
        Args:
            sentiment_analysis: Résultat de l'analyse de sentiment
            text: Texte original (optionnel)
            
        Returns:
            dict: Note calculée et justification
        """
        prompt = RATING_CALCULATION_PROMPT.format(
            sentiment_analysis=json.dumps(sentiment_analysis, ensure_ascii=False)
        )
        
        try:
            result = self._make_api_request(prompt)
            
            # Validation
            if 'suggested_rating' not in result:
                raise Exception("Note manquante dans la réponse")
            
            rating = float(result['suggested_rating'])
            if not (1 <= rating <= 5):
                raise Exception(f"Note invalide: {rating} (doit être entre 1 et 5)")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur calcul rating: {str(e)}")
            raise
    
    def calculate_hybrid_rating(self, questionnaire_note: float, sentiment_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule une note hybride en combinant questionnaire et analyse textuelle
        
        Args:
            questionnaire_note: Note du questionnaire (1-5)
            sentiment_analysis: Analyse de sentiment du texte
            
        Returns:
            dict: Note hybride calculée
        """
        if not (1 <= questionnaire_note <= 5):
            raise Exception(f"Note questionnaire invalide: {questionnaire_note}")
        
        prompt = HYBRID_RATING_CALCULATION_PROMPT.format(
            questionnaire_note=questionnaire_note,
            sentiment_analysis=json.dumps(sentiment_analysis, ensure_ascii=False)
        )
        
        try:
            result = self._make_api_request(prompt)
            
            # Validation
            if 'suggested_rating' not in result:
                raise Exception("Note hybride manquante dans la réponse")
            
            rating = float(result['suggested_rating'])
            if not (1 <= rating <= 5):
                raise Exception(f"Note hybride invalide: {rating}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur calcul hybride: {str(e)}")
            raise
    
    def generate_title(self, sentiment_analysis: Dict[str, Any], rating: float, text: str) -> Dict[str, Any]:
        """
        Génère un titre pour l'avis
        
        Args:
            sentiment_analysis: Analyse de sentiment
            rating: Note calculée
            text: Texte de l'avis
            
        Returns:
            dict: Titre suggéré et alternatives
        """
        prompt = TITLE_GENERATION_PROMPT.format(
            sentiment_analysis=json.dumps(sentiment_analysis, ensure_ascii=False),
            rating=rating,
            text=text[:500]  # Limite pour éviter les prompts trop longs
        )
        
        try:
            result = self._make_api_request(prompt)
            
            if 'suggested_title' not in result:
                raise Exception("Titre manquant dans la réponse")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur génération titre: {str(e)}")
            raise
    
    def health_check(self) -> bool:
        """
        Vérifie que l'API Mistral est accessible
        
        Returns:
            bool: True si OK, False sinon
        """
        try:
            test_result = self.analyze_sentiment("Test de fonctionnement")
            return 'sentiment' in test_result
        except:
            return False
    
    def clear_cache(self) -> None:
        """Vide le cache"""
        self._cache.clear()
        self.logger.info("Cache Mistral vidé")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur le cache"""
        current_time = time.time()
        valid_entries = sum(
            1 for entry in self._cache.values() 
            if (current_time - entry['timestamp']) < self._cache_ttl
        )
        
        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "cache_hit_rate": f"{(valid_entries / max(len(self._cache), 1)) * 100:.1f}%"
        }