"""
Calculateur de notes pour les avis patients Hospitalidée
Implémentation selon les Cursor rules avec Mistral AI
"""

from typing import Dict, Any
import logging
from src.mistral_client import MistralClient
from src.sentiment_analyzer import SentimentAnalyzer


class RatingCalculator:
    """Calculateur de notes spécialisé pour les avis patients"""
    
    def __init__(self, mistral_client: MistralClient = None):
        """
        Initialise le calculateur de notes
        
        Args:
            mistral_client: Instance du client Mistral AI
        """
        self.mistral_client = mistral_client or MistralClient()
        self.sentiment_analyzer = SentimentAnalyzer(self.mistral_client)
        self.logger = logging.getLogger(__name__)
    
    def calculate_rating_from_text(self, text: str, sentiment_analysis: Dict[str, Any] = None, questionnaire_context: float = None) -> Dict[str, Any]:
        """
        Calcule une note sur 5 basée sur l'analyse de sentiment et optionnellement le questionnaire
        
        Args:
            text: Texte de l'avis patient
            sentiment_analysis: Analyse de sentiment optionnelle (si None, sera calculée)
            questionnaire_context: Note du questionnaire pour analyse hybride
            
        Returns:
            dict: {
                'suggested_rating': 1-5,
                'confidence': 0.0-1.0,
                'justification': str,
                'factors': {
                    'questionnaire_weight': float (si questionnaire fourni),
                    'sentiment_weight': float,
                    'intensity_weight': float,
                    'content_weight': float
                }
            }
        """
        if not text or not text.strip():
            self.logger.warning("Texte vide fourni pour le calcul de note")
            return self._get_default_rating()
        
        try:
            # Obtenir l'analyse de sentiment si non fournie
            if sentiment_analysis is None:
                sentiment_analysis = self.sentiment_analyzer.analyze_sentiment(text)
            
            # Calcul avec Mistral AI (hybride si questionnaire fourni)
            if questionnaire_context is not None:
                result = self.mistral_client.calculate_hybrid_rating(sentiment_analysis, questionnaire_context)
            else:
                result = self.mistral_client.calculate_rating(sentiment_analysis)
            
            # Validation et enrichissement du résultat
            validated_result = self._validate_rating_result(result)
            
            # Ajout des facteurs hybrides si applicable
            if questionnaire_context is not None:
                validated_result['factors'].update({
                    'questionnaire_weight': 0.4,
                    'sentiment_weight': 0.3,
                    'intensity_weight': 0.2,
                    'content_weight': 0.1
                })
                validated_result['hybrid_mode'] = True
                validated_result['questionnaire_note'] = questionnaire_context
            
            # Ajout du calcul local pour comparaison (seulement si pas hybride)
            if questionnaire_context is None:
                local_rating = self._calculate_local_rating(sentiment_analysis, text)
                validated_result['local_rating'] = local_rating
            
            # Ajustement final basé sur la cohérence
            final_result = self._adjust_rating_with_coherence(validated_result, sentiment_analysis, questionnaire_context)
            
            mode = "hybride" if questionnaire_context is not None else "standard"
            self.logger.info(f"Calcul de note {mode} réussi: {final_result['suggested_rating']}/5 "
                           f"(confiance: {final_result['confidence']:.2f})")
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul de note: {e}")
            return self._get_default_rating(error=str(e))
    
    def calculate_partial_ratings(self, criteria_scores: Dict[str, int], verbatim: str) -> Dict[str, Any]:
        """
        Calcule la note globale basée sur les critères partiels et le verbatim
        
        Args:
            criteria_scores: {
                'medecins': 1-5,
                'personnel': 1-5, 
                'prise_en_charge': 1-5,
                'hotellerie': 1-5
            }
            verbatim: Texte du verbatim patient
        
        Returns:
            dict: {
                'global_rating': 1-5,
                'coherence_score': 0.0-1.0,
                'adjustments': [...],
                'warnings': [...]
            }
        """
        if not criteria_scores:
            self.logger.warning("Aucun critère fourni pour le calcul de notes partielles")
            return self._get_default_partial_rating()
        
        try:
            # Validation des critères d'entrée
            validated_criteria = self._validate_criteria_scores(criteria_scores)
            
            # Calcul de la moyenne pondérée
            weighted_average = self._calculate_weighted_average(validated_criteria)
            
            # Analyse du verbatim si fourni
            verbatim_analysis = None
            if verbatim and verbatim.strip():
                verbatim_analysis = self.sentiment_analyzer.analyze_sentiment(verbatim)
            
            # Vérification de cohérence avec Mistral AI
            coherence_result = self.mistral_client.check_coherence(validated_criteria, verbatim or "")
            
            # Calcul de la note globale avec ajustements
            global_rating, adjustments, warnings = self._calculate_global_rating(
                weighted_average, 
                verbatim_analysis, 
                coherence_result
            )
            
            result = {
                'global_rating': global_rating,
                'weighted_average': weighted_average,
                'coherence_score': coherence_result.get('coherence_score', 0.5),
                'adjustments': adjustments,
                'warnings': warnings,
                'criteria_breakdown': validated_criteria,
                'verbatim_sentiment': verbatim_analysis.get('sentiment', 'neutre') if verbatim_analysis else None,
                'mistral_suggestion': coherence_result.get('global_rating_suggestion', weighted_average)
            }
            
            self.logger.info(f"Calcul de notes partielles réussi: {global_rating}/5 "
                           f"(cohérence: {coherence_result.get('coherence_score', 0.5):.2f})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul de notes partielles: {e}")
            return self._get_default_partial_rating(error=str(e))
    
    def _validate_criteria_scores(self, criteria_scores: Dict[str, int]) -> Dict[str, int]:
        """Valide et normalise les scores de critères"""
        validated = {}
        expected_criteria = ['medecins', 'personnel', 'prise_en_charge', 'hotellerie']
        
        for criterion in expected_criteria:
            score = criteria_scores.get(criterion, 3)  # Défaut à 3 (neutre)
            validated[criterion] = max(1, min(5, int(score)))  # Contrainte 1-5 selon Cursor rules
        
        return validated
    
    def _calculate_weighted_average(self, criteria_scores: Dict[str, int]) -> float:
        """
        Calcule la moyenne pondérée des critères selon l'importance
        Pondération selon les standards Hospitalidée
        """
        weights = {
            'medecins': 0.35,      # Critère le plus important
            'personnel': 0.25,     # Deuxième critère important  
            'prise_en_charge': 0.25,  # Égal au personnel
            'hotellerie': 0.15     # Moins critique
        }
        
        weighted_sum = sum(criteria_scores[criterion] * weights[criterion] 
                          for criterion in criteria_scores)
        
        return round(weighted_sum, 2)
    
    def _calculate_global_rating(self, weighted_average: float, verbatim_analysis: Dict[str, Any], 
                               coherence_result: Dict[str, Any]) -> tuple:
        """Calcule la note globale avec ajustements et warnings"""
        global_rating = weighted_average
        adjustments = []
        warnings = []
        
        # Ajustement basé sur la cohérence selon Cursor rules
        coherence_score = coherence_result.get('coherence_score', 0.5)
        if coherence_score < 0.7:  # Seuil de cohérence
            warnings.append(f"Faible cohérence détectée ({coherence_score:.2f})")
            
            # Utiliser la suggestion Mistral si plus cohérente
            mistral_suggestion = coherence_result.get('global_rating_suggestion')
            if mistral_suggestion and abs(mistral_suggestion - weighted_average) > 0.5:
                adjustments.append(f"Ajustement cohérence: {weighted_average:.1f} → {mistral_suggestion:.1f}")
                global_rating = mistral_suggestion
        
        # Ajustement basé sur le verbatim
        if verbatim_analysis:
            sentiment = verbatim_analysis.get('sentiment', 'neutre')
            intensity = verbatim_analysis.get('emotional_intensity', 0.5)
            
            if sentiment == 'positif' and global_rating < 4 and intensity > 0.7:
                adjustment = min(0.5, (intensity - 0.5))
                global_rating = min(5.0, global_rating + adjustment)
                adjustments.append(f"Bonus sentiment très positif: +{adjustment:.1f}")
                
            elif sentiment == 'negatif' and global_rating > 2 and intensity > 0.7:
                adjustment = min(0.5, (intensity - 0.5))
                global_rating = max(1.0, global_rating - adjustment)
                adjustments.append(f"Pénalité sentiment très négatif: -{adjustment:.1f}")
        
        # Contrainte finale selon Cursor rules (1-5)
        global_rating = max(1.0, min(5.0, round(global_rating, 1)))
        
        return global_rating, adjustments, warnings
    
    def _calculate_local_rating(self, sentiment_analysis: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Calcul de note local basé sur des règles simples"""
        sentiment = sentiment_analysis.get('sentiment', 'neutre')
        intensity = sentiment_analysis.get('emotional_intensity', 0.5)
        confidence = sentiment_analysis.get('confidence', 0.0)
        
        # Mapping sentiment → note selon Cursor rules
        base_ratings = {
            'positif': 4.0,
            'neutre': 3.0,
            'negatif': 2.0
        }
        
        base_rating = base_ratings.get(sentiment, 3.0)
        
        # Ajustement par intensité
        if sentiment == 'positif' and intensity > 0.8:
            base_rating = min(5.0, base_rating + 1.0)
        elif sentiment == 'negatif' and intensity > 0.8:
            base_rating = max(1.0, base_rating - 1.0)
        
        # Ajustement par longueur du texte (plus de détails = plus fiable)
        text_length = len(text.split())
        if text_length > 50:  # Avis détaillé
            confidence_bonus = 0.1
        else:
            confidence_bonus = 0.0
        
        return {
            'local_suggested_rating': round(base_rating, 1),
            'base_sentiment_rating': base_ratings.get(sentiment, 3.0),
            'intensity_adjustment': intensity,
            'text_length_bonus': confidence_bonus,
            'final_confidence': min(1.0, confidence + confidence_bonus)
        }
    
    def _validate_rating_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Valide et normalise le résultat du calcul de note"""
        validated = {
            'suggested_rating': 3.0,
            'confidence': 0.0,
            'justification': "Note par défaut",
            'factors': {
                'sentiment_weight': 0.5,
                'intensity_weight': 0.3,
                'content_weight': 0.2
            }
        }
        
        # Validation de la note (1-5) selon Cursor rules
        if 'suggested_rating' in result:
            rating = float(result['suggested_rating'])
            validated['suggested_rating'] = max(1.0, min(5.0, rating))
        
        # Validation de la confiance (0.0-1.0)
        if 'confidence' in result:
            confidence = float(result['confidence'])
            validated['confidence'] = max(0.0, min(1.0, confidence))
        
        # Validation de la justification
        if 'justification' in result and result['justification']:
            validated['justification'] = str(result['justification'])
        
        # Validation des facteurs
        if 'rating_factors' in result and isinstance(result['rating_factors'], dict):
            validated['factors'] = result['rating_factors']
        
        # Propagation des erreurs
        if 'error' in result:
            validated['error'] = result['error']
        
        return validated
    
    def _adjust_rating_with_coherence(self, rating_result: Dict[str, Any], 
                                    sentiment_analysis: Dict[str, Any], questionnaire_context: float = None) -> Dict[str, Any]:
        """Ajuste la note finale en fonction de la cohérence globale"""
        mistral_rating = rating_result['suggested_rating']
        local_rating = rating_result.get('local_rating', {}).get('local_suggested_rating', 3.0)
        
        # Si les deux méthodes sont très différentes, prendre une moyenne pondérée
        if abs(mistral_rating - local_rating) > 1.0:
            confidence = rating_result.get('confidence', 0.0)
            
            # Plus la confiance Mistral est haute, plus on lui fait confiance
            weight_mistral = 0.7 + (confidence * 0.3)
            weight_local = 1.0 - weight_mistral
            
            adjusted_rating = (mistral_rating * weight_mistral) + (local_rating * weight_local)
            rating_result['suggested_rating'] = round(adjusted_rating, 1)
            rating_result['adjustment_applied'] = True
            rating_result['original_mistral_rating'] = mistral_rating
            rating_result['adjustment_reason'] = f"Écart important entre Mistral ({mistral_rating}) et local ({local_rating})"
        
        return rating_result
    
    def _get_default_rating(self, error: str = None) -> Dict[str, Any]:
        """Retourne un calcul de note par défaut"""
        result = {
            'suggested_rating': 3.0,
            'confidence': 0.0,
            'justification': "Note par défaut (mode dégradé)",
            'factors': {
                'sentiment_weight': 0.5,
                'intensity_weight': 0.3,
                'content_weight': 0.2
            },
            'local_rating': {
                'local_suggested_rating': 3.0,
                'base_sentiment_rating': 3.0,
                'intensity_adjustment': 0.5,
                'text_length_bonus': 0.0,
                'final_confidence': 0.0
            }
        }
        
        if error:
            result['error'] = error
            
        return result
    
    def _get_default_partial_rating(self, error: str = None) -> Dict[str, Any]:
        """Retourne un calcul de notes partielles par défaut"""
        result = {
            'global_rating': 3.0,
            'weighted_average': 3.0,
            'coherence_score': 0.5,
            'adjustments': [],
            'warnings': [],
            'criteria_breakdown': {
                'medecins': 3,
                'personnel': 3,
                'prise_en_charge': 3,
                'hotellerie': 3
            },
            'verbatim_sentiment': None,
            'mistral_suggestion': 3.0
        }
        
        if error:
            result['error'] = error
            
        return result


# Fonctions standalone pour compatibilité avec les Cursor rules
def calculate_rating_from_text(text: str, sentiment_analysis: Dict[str, Any] = None, questionnaire_context: float = None) -> Dict[str, Any]:
    """
    Calcule une note sur 5 basée sur l'analyse de sentiment et optionnellement le questionnaire
    Function standalone selon les Cursor rules
    """
    calculator = RatingCalculator()
    return calculator.calculate_rating_from_text(text, sentiment_analysis, questionnaire_context)


def calculate_partial_ratings(criteria_scores: Dict[str, int], verbatim: str) -> Dict[str, Any]:
    """
    Calcule la note globale basée sur les critères partiels et le verbatim
    Function standalone selon les Cursor rules
    """
    calculator = RatingCalculator()
    return calculator.calculate_partial_ratings(criteria_scores, verbatim) 