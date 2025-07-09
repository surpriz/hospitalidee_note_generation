"""
Analyseur de sentiment pour les avis patients Hospitalidée
Implémentation selon les Cursor rules avec Mistral AI
"""

from typing import Dict, Any
import logging
from src.mistral_client import MistralClient


class SentimentAnalyzer:
    """Analyseur de sentiment spécialisé pour les avis patients"""
    
    def __init__(self, mistral_client: MistralClient = None):
        """
        Initialise l'analyseur de sentiment
        
        Args:
            mistral_client: Instance du client Mistral AI
        """
        self.mistral_client = mistral_client or MistralClient()
        self.logger = logging.getLogger(__name__)
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyse le sentiment d'un texte d'avis patient
        
        Args:
            text: Texte de l'avis patient à analyser
            
        Returns:
            dict: {
                'sentiment': 'positif|neutre|negatif',
                'confidence': float (0.0-1.0),
                'emotional_intensity': float (0.0-1.0),
                'key_phrases': list,
                'positive_indicators': list,
                'negative_indicators': list
            }
        """
        if not text or not text.strip():
            self.logger.warning("Texte vide fourni pour l'analyse de sentiment")
            return self._get_default_sentiment()
        
        try:
            # Nettoyage du texte
            cleaned_text = self._clean_text(text)
            
            # Analyse avec Mistral AI
            result = self.mistral_client.analyze_sentiment(cleaned_text)
            
            # Validation et enrichissement du résultat
            validated_result = self._validate_sentiment_result(result)
            
            # Ajout de métriques locales si disponibles
            local_analysis = self._local_sentiment_analysis(cleaned_text)
            validated_result.update(local_analysis)
            
            self.logger.info(f"Analyse de sentiment réussie: {validated_result['sentiment']} "
                           f"(confiance: {validated_result['confidence']:.2f})")
            
            return validated_result
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse de sentiment: {e}")
            return self._get_default_sentiment(error=str(e))
    
    def _clean_text(self, text: str) -> str:
        """
        Nettoie le texte pour l'analyse
        
        Args:
            text: Texte brut
            
        Returns:
            str: Texte nettoyé
        """
        # Suppression des caractères spéciaux excessifs
        cleaned = text.strip()
        
        # Limitation de la longueur pour éviter les timeouts
        max_length = 2000  # Limite pour performance
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
            self.logger.warning(f"Texte tronqué à {max_length} caractères")
        
        return cleaned
    
    def _validate_sentiment_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide et normalise le résultat de l'analyse de sentiment
        
        Args:
            result: Résultat brut de Mistral AI
            
        Returns:
            dict: Résultat validé et normalisé
        """
        # Valeurs par défaut selon Cursor rules
        validated = {
            'sentiment': 'neutre',
            'confidence': 0.0,
            'emotional_intensity': 0.5,
            'positive_indicators': [],
            'negative_indicators': [],
            'key_themes': []
        }
        
        # Validation du sentiment
        if 'sentiment' in result:
            sentiment = result['sentiment'].lower()
            if sentiment in ['positif', 'negatif', 'neutre']:
                validated['sentiment'] = sentiment
        
        # Validation de la confiance (0.0-1.0)
        if 'confidence' in result:
            confidence = float(result['confidence'])
            validated['confidence'] = max(0.0, min(1.0, confidence))
        
        # Validation de l'intensité émotionnelle (0.0-1.0)
        if 'emotional_intensity' in result:
            intensity = float(result['emotional_intensity'])
            validated['emotional_intensity'] = max(0.0, min(1.0, intensity))
        
        # Validation des listes
        for field in ['positive_indicators', 'negative_indicators', 'key_themes']:
            if field in result and isinstance(result[field], list):
                validated[field] = result[field]
        
        # Propagation des erreurs
        if 'error' in result:
            validated['error'] = result['error']
        
        return validated
    
    def _local_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """
        Analyse de sentiment locale complémentaire (règles simples)
        
        Args:
            text: Texte à analyser
            
        Returns:
            dict: Métriques locales additionnelles
        """
        text_lower = text.lower()
        
        # Mots-clés positifs spécifiques santé selon Cursor rules
        positive_keywords = [
            'excellent', 'parfait', 'recommande', 'professionnel', 'attentif',
            'efficace', 'rassurant', 'compétent', 'bienveillant', 'satisfait',
            'merci', 'reconnaissant', 'qualité', 'confort', 'propre'
        ]
        
        # Mots-clés négatifs spécifiques santé selon Cursor rules
        negative_keywords = [
            'déçu', 'attente', 'problème', 'inadmissible', 'négligent',
            'froid', 'débordé', 'sale', 'bruyant', 'désagréable',
            'incompétent', 'stress', 'douleur', 'insatisfait', 'colère'
        ]
        
        # Comptage des occurrences
        positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
        
        # Calcul du score local
        total_words = len(text.split())
        if total_words > 0:
            positive_ratio = positive_count / total_words
            negative_ratio = negative_count / total_words
        else:
            positive_ratio = negative_ratio = 0.0
        
        return {
            'local_positive_count': positive_count,
            'local_negative_count': negative_count,
            'local_positive_ratio': positive_ratio,
            'local_negative_ratio': negative_ratio,
            'text_length': len(text),
            'word_count': total_words
        }
    
    def _get_default_sentiment(self, error: str = None) -> Dict[str, Any]:
        """
        Retourne une analyse de sentiment par défaut
        
        Args:
            error: Message d'erreur optionnel
            
        Returns:
            dict: Résultat par défaut selon Cursor rules
        """
        result = {
            'sentiment': 'neutre',
            'confidence': 0.0,
            'emotional_intensity': 0.5,
            'positive_indicators': [],
            'negative_indicators': [],
            'key_themes': [],
            'local_positive_count': 0,
            'local_negative_count': 0,
            'local_positive_ratio': 0.0,
            'local_negative_ratio': 0.0,
            'text_length': 0,
            'word_count': 0
        }
        
        if error:
            result['error'] = error
            
        return result


# Fonction standalone pour compatibilité avec les Cursor rules
def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyse le sentiment d'un texte d'avis patient
    Function standalone selon les Cursor rules
    
    Args:
        text: Texte de l'avis patient à analyser
        
    Returns:
        dict: Résultat de l'analyse de sentiment
    """
    analyzer = SentimentAnalyzer()
    return analyzer.analyze_sentiment(text) 