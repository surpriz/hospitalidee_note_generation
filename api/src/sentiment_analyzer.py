"""
Analyseur de sentiment pour les avis patients Hospitalidée
Implémentation selon les Cursor rules avec Mistral AI
Version optimisée pour l'API REST
"""

from typing import Dict, Any
import logging
import re
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
                'negative_indicators': list,
                'key_themes': list,
                'fallback_mode': bool (si mode dégradé)
            }
        """
        if not text or not text.strip():
            self.logger.warning("Texte vide fourni pour l'analyse de sentiment")
            return self._get_default_sentiment()
        
        try:
            # Nettoyage du texte
            cleaned_text = self._clean_text(text)
            
            # Vérification de la longueur minimale
            if len(cleaned_text) < 10:
                self.logger.warning("Texte trop court après nettoyage")
                return self._get_fallback_sentiment(cleaned_text)
            
            # Analyse avec Mistral AI
            self.logger.debug(f"Analyse sentiment texte: {len(cleaned_text)} caractères")
            result = self.mistral_client.analyze_sentiment(cleaned_text)
            
            # Enrichissement avec analyse locale
            local_analysis = self._perform_local_analysis(cleaned_text)
            
            # Fusion des résultats
            enhanced_result = {
                **result,
                **local_analysis,
                'text_length': len(text),
                'cleaned_text_length': len(cleaned_text),
                'word_count': len(cleaned_text.split()),
                'fallback_mode': False
            }
            
            self.logger.info(f"✅ Sentiment analysé: {enhanced_result.get('sentiment', 'inconnu')}")
            return enhanced_result
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur analyse sentiment Mistral: {str(e)}")
            # Mode dégradé avec analyse locale uniquement
            return self._get_fallback_sentiment(text, str(e))
    
    def _clean_text(self, text: str) -> str:
        """
        Nettoie le texte pour améliorer l'analyse
        
        Args:
            text: Texte brut
            
        Returns:
            str: Texte nettoyé
        """
        # Suppression des caractères de contrôle
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Normalisation des espaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Suppression des espaces en début/fin
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _perform_local_analysis(self, text: str) -> Dict[str, Any]:
        """
        Effectue une analyse locale pour enrichir les résultats Mistral
        
        Args:
            text: Texte nettoyé
            
        Returns:
            dict: Résultats de l'analyse locale
        """
        text_lower = text.lower()
        
        # Mots-clés positifs spécifiques au domaine de la santé
        positive_keywords = [
            'excellent', 'parfait', 'recommande', 'professionnel', 'attentif',
            'efficace', 'rassurant', 'compétent', 'satisfait', 'merci',
            'formidable', 'super', 'génial', 'content', 'heureux',
            'bienveillant', 'à l\'écoute', 'disponible', 'souriant'
        ]
        
        # Mots-clés négatifs spécifiques au domaine de la santé
        negative_keywords = [
            'déçu', 'problème', 'inadmissible', 'négligent', 'froid',
            'débordé', 'sale', 'bruyant', 'incompétent', 'insatisfait',
            'catastrophe', 'horrible', 'décevant', 'inadéquat', 'insuffisant',
            'indisponible', 'désagréable', 'impoli', 'stressant'
        ]
        
        # Comptage des occurrences
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        # Détection d'expressions spécifiques
        positive_phrases = []
        negative_phrases = []
        
        positive_expressions = [
            r'très (bon|bien|satisfait|content)',
            r'(excellent|parfait) (service|accueil|soins)',
            r'(recommande|conseille) vivement',
            r'personnel (attentif|professionnel|compétent)',
            r'(médecin|docteur) (excellent|formidable|compétent)'
        ]
        
        negative_expressions = [
            r'très (déçu|mécontent|insatisfait)',
            r'(mauvais|horrible|catastrophique) (service|accueil|soins)',
            r'(personnel|médecin) (froid|désagréable|incompétent)',
            r'attente (trop longue|interminable)',
            r'(problème|difficulté) (majeur|important)'
        ]
        
        for expr in positive_expressions:
            matches = re.findall(expr, text_lower)
            positive_phrases.extend(matches)
        
        for expr in negative_expressions:
            matches = re.findall(expr, text_lower)
            negative_phrases.extend(matches)
        
        # Calcul du score local
        total_indicators = positive_count + negative_count + len(positive_phrases) + len(negative_phrases)
        local_sentiment_score = 0.0
        
        if total_indicators > 0:
            positive_score = positive_count + len(positive_phrases) * 2  # Les phrases valent plus
            negative_score = negative_count + len(negative_phrases) * 2
            local_sentiment_score = (positive_score - negative_score) / (positive_score + negative_score + 1)
        
        return {
            'local_positive_count': positive_count,
            'local_negative_count': negative_count,
            'local_positive_phrases': positive_phrases,
            'local_negative_phrases': negative_phrases,
            'local_sentiment_score': local_sentiment_score,
            'local_indicators_total': total_indicators
        }
    
    def _get_fallback_sentiment(self, text: str, error: str = "Analyse IA indisponible") -> Dict[str, Any]:
        """
        Retourne une analyse de sentiment en mode dégradé (sans IA)
        
        Args:
            text: Texte à analyser
            error: Message d'erreur
            
        Returns:
            dict: Résultat de l'analyse en mode dégradé
        """
        # Analyse locale seulement
        local_analysis = self._perform_local_analysis(text)
        
        # Détermination du sentiment basé sur l'analyse locale
        local_score = local_analysis.get('local_sentiment_score', 0.0)
        
        if local_score > 0.3:
            sentiment = 'positif'
            confidence = min(0.7, 0.5 + abs(local_score) * 0.3)
        elif local_score < -0.3:
            sentiment = 'negatif'
            confidence = min(0.7, 0.5 + abs(local_score) * 0.3)
        else:
            sentiment = 'neutre'
            confidence = 0.5
        
        # Intensité basée sur le nombre d'indicateurs
        total_indicators = local_analysis.get('local_indicators_total', 0)
        emotional_intensity = min(1.0, total_indicators * 0.2)
        
        # Génération d'indicateurs simples
        positive_indicators = []
        negative_indicators = []
        
        if local_analysis.get('local_positive_count', 0) > 0:
            positive_indicators.append(f"{local_analysis['local_positive_count']} mots positifs détectés")
        
        if local_analysis.get('local_negative_count', 0) > 0:
            negative_indicators.append(f"{local_analysis['local_negative_count']} mots négatifs détectés")
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'emotional_intensity': emotional_intensity,
            'positive_indicators': positive_indicators,
            'negative_indicators': negative_indicators,
            'key_themes': self._extract_basic_themes(text),
            **local_analysis,
            'text_length': len(text),
            'word_count': len(text.split()),
            'fallback_mode': True,
            'error': error
        }
    
    def _get_default_sentiment(self) -> Dict[str, Any]:
        """
        Retourne un sentiment par défaut pour les textes vides
        
        Returns:
            dict: Sentiment neutre par défaut
        """
        return {
            'sentiment': 'neutre',
            'confidence': 0.0,
            'emotional_intensity': 0.0,
            'positive_indicators': [],
            'negative_indicators': [],
            'key_themes': [],
            'local_positive_count': 0,
            'local_negative_count': 0,
            'local_sentiment_score': 0.0,
            'text_length': 0,
            'word_count': 0,
            'fallback_mode': True,
            'error': 'Texte vide ou trop court'
        }
    
    def _extract_basic_themes(self, text: str) -> list:
        """
        Extrait des thèmes basiques du texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            list: Liste des thèmes détectés
        """
        text_lower = text.lower()
        themes = []
        
        # Thèmes fréquents dans les avis patients
        theme_keywords = {
            'accueil': ['accueil', 'réception', 'entrée', 'arrivée'],
            'soins': ['soins', 'traitement', 'médical', 'thérapie', 'soin'],
            'personnel': ['personnel', 'équipe', 'staff', 'employé'],
            'médecin': ['médecin', 'docteur', 'praticien', 'chirurgien'],
            'confort': ['chambre', 'lit', 'repas', 'confort', 'propreté'],
            'organisation': ['organisation', 'rendez-vous', 'planning', 'attente'],
            'communication': ['explication', 'information', 'communication', 'écoute'],
            'établissement': ['hôpital', 'clinique', 'établissement', 'structure']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes[:5]  # Limite à 5 thèmes maximum
    
    def batch_analyze(self, texts: list) -> list:
        """
        Analyse plusieurs textes en lot (pour optimisation future)
        
        Args:
            texts: Liste des textes à analyser
            
        Returns:
            list: Liste des résultats d'analyse
        """
        results = []
        
        for i, text in enumerate(texts):
            self.logger.debug(f"Analyse batch {i+1}/{len(texts)}")
            try:
                result = self.analyze_sentiment(text)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Erreur analyse batch {i+1}: {str(e)}")
                results.append(self._get_fallback_sentiment(text, str(e)))
        
        return results
    
    def get_analysis_summary(self, analysis_result: Dict[str, Any]) -> str:
        """
        Génère un résumé textuel de l'analyse
        
        Args:
            analysis_result: Résultat de l'analyse de sentiment
            
        Returns:
            str: Résumé en français
        """
        sentiment = analysis_result.get('sentiment', 'inconnu')
        confidence = analysis_result.get('confidence', 0.0)
        intensity = analysis_result.get('emotional_intensity', 0.0)
        
        sentiment_text = {
            'positif': 'positif',
            'negatif': 'négatif', 
            'neutre': 'neutre'
        }.get(sentiment, 'indéterminé')
        
        confidence_text = "élevée" if confidence > 0.7 else "modérée" if confidence > 0.4 else "faible"
        intensity_text = "forte" if intensity > 0.7 else "modérée" if intensity > 0.4 else "faible"
        
        summary = f"Sentiment {sentiment_text} avec une confiance {confidence_text} "
        summary += f"et une intensité émotionnelle {intensity_text}."
        
        if analysis_result.get('fallback_mode', False):
            summary += " (Analyse en mode dégradé)"
        
        return summary