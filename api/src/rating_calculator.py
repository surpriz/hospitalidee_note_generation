"""
Calculateur de notes pour les avis patients Hospitalidée
Implémentation selon les Cursor rules avec Mistral AI
Version optimisée pour l'API REST avec calculs hybrides
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
                },
                'hybrid_mode': bool,
                'fallback_mode': bool (si mode dégradé)
            }
        """
        if not text or not text.strip():
            self.logger.warning("Texte vide fourni pour le calcul de note")
            return self._get_default_rating()
        
        try:
            # 1. Obtenir l'analyse de sentiment si non fournie
            if sentiment_analysis is None:
                self.logger.debug("Calcul de l'analyse de sentiment...")
                sentiment_analysis = self.sentiment_analyzer.analyze_sentiment(text)
            
            # 2. Calcul avec Mistral AI
            if questionnaire_context is not None:
                # Mode hybride : questionnaire + analyse textuelle
                self.logger.debug(f"Calcul hybride: questionnaire={questionnaire_context:.1f}")
                rating_result = self._calculate_hybrid_rating_with_mistral(
                    text, sentiment_analysis, questionnaire_context
                )
            else:
                # Mode texte seul
                self.logger.debug("Calcul basé sur le texte seul")
                rating_result = self._calculate_text_only_rating_with_mistral(text, sentiment_analysis)
            
            # 3. Validation et enrichissement
            self._validate_rating_result(rating_result)
            
            # 4. Calcul local pour comparaison/vérification
            local_result = self._calculate_local_rating(sentiment_analysis, questionnaire_context)
            
            # 5. Réconciliation des résultats
            final_result = self._reconcile_ratings(rating_result, local_result, questionnaire_context)
            
            self.logger.info(f"✅ Note calculée: {final_result.get('suggested_rating', 0):.1f}/5")
            return final_result
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur calcul rating Mistral: {str(e)}")
            # Mode dégradé avec calcul local uniquement
            return self._get_fallback_rating(text, sentiment_analysis, questionnaire_context, str(e))
    
    def _calculate_hybrid_rating_with_mistral(self, text: str, sentiment_analysis: Dict[str, Any], questionnaire_note: float) -> Dict[str, Any]:
        """
        Calcule une note hybride avec Mistral AI
        
        Args:
            text: Texte de l'avis
            sentiment_analysis: Analyse de sentiment
            questionnaire_note: Note du questionnaire
            
        Returns:
            dict: Résultat du calcul hybride
        """
        try:
            result = self.mistral_client.calculate_hybrid_rating(questionnaire_note, sentiment_analysis)
            result['hybrid_mode'] = True
            result['calculation_method'] = 'mistral_hybrid'
            return result
        except Exception as e:
            self.logger.error(f"Erreur calcul hybride Mistral: {str(e)}")
            raise
    
    def _calculate_text_only_rating_with_mistral(self, text: str, sentiment_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule une note basée uniquement sur le texte avec Mistral AI
        
        Args:
            text: Texte de l'avis
            sentiment_analysis: Analyse de sentiment
            
        Returns:
            dict: Résultat du calcul basé sur le texte
        """
        try:
            result = self.mistral_client.calculate_rating(sentiment_analysis, text)
            result['hybrid_mode'] = False
            result['calculation_method'] = 'mistral_text_only'
            return result
        except Exception as e:
            self.logger.error(f"Erreur calcul texte Mistral: {str(e)}")
            raise
    
    def _calculate_local_rating(self, sentiment_analysis: Dict[str, Any], questionnaire_note: float = None) -> Dict[str, Any]:
        """
        Calcule une note avec un algorithme local simple
        
        Args:
            sentiment_analysis: Analyse de sentiment
            questionnaire_note: Note du questionnaire (optionnel)
            
        Returns:
            dict: Résultat du calcul local
        """
        sentiment = sentiment_analysis.get('sentiment', 'neutre')
        intensity = sentiment_analysis.get('emotional_intensity', 0.5)
        confidence = sentiment_analysis.get('confidence', 0.5)
        
        # Mapping sentiment → note de base
        sentiment_ratings = {
            'positif': 4.0,
            'neutre': 3.0,
            'negatif': 2.0
        }
        
        base_rating = sentiment_ratings.get(sentiment, 3.0)
        
        # Ajustement par intensité émotionnelle
        if sentiment == 'positif' and intensity > 0.8:
            base_rating = min(5.0, base_rating + 1.0)
        elif sentiment == 'positif' and intensity > 0.6:
            base_rating = min(5.0, base_rating + 0.5)
        elif sentiment == 'negatif' and intensity > 0.8:
            base_rating = max(1.0, base_rating - 1.0)
        elif sentiment == 'negatif' and intensity > 0.6:
            base_rating = max(1.0, base_rating - 0.5)
        
        # Ajustement par confiance
        if confidence < 0.3:
            # Si confiance faible, on tend vers la neutralité
            base_rating = base_rating * 0.7 + 3.0 * 0.3
        
        # Calcul final selon le mode
        if questionnaire_note is not None:
            # Mode hybride : pondération questionnaire + texte
            final_rating = (0.4 * questionnaire_note + 0.6 * base_rating)
            
            factors = {
                'questionnaire_weight': 0.4,
                'sentiment_weight': 0.4,
                'intensity_weight': 0.15,
                'content_weight': 0.05
            }
        else:
            # Mode texte seul
            final_rating = base_rating
            
            factors = {
                'sentiment_weight': 0.6,
                'intensity_weight': 0.3,
                'content_weight': 0.1
            }
        
        # Assurer que la note est dans [1, 5]
        final_rating = max(1.0, min(5.0, final_rating))
        
        justification = self._generate_local_justification(
            sentiment, intensity, confidence, questionnaire_note, final_rating
        )
        
        return {
            'suggested_rating': round(final_rating, 1),
            'confidence': confidence,
            'justification': justification,
            'factors': factors,
            'hybrid_mode': questionnaire_note is not None,
            'calculation_method': 'local_algorithm'
        }
    
    def _reconcile_ratings(self, mistral_result: Dict[str, Any], local_result: Dict[str, Any], questionnaire_note: float = None) -> Dict[str, Any]:
        """
        Réconcilie les résultats Mistral et local pour obtenir le meilleur résultat
        
        Args:
            mistral_result: Résultat du calcul Mistral
            local_result: Résultat du calcul local
            questionnaire_note: Note du questionnaire
            
        Returns:
            dict: Résultat final réconcilié
        """
        mistral_rating = mistral_result.get('suggested_rating', 3.0)
        local_rating = local_result.get('suggested_rating', 3.0)
        mistral_confidence = mistral_result.get('confidence', 0.5)
        
        # Calcul de l'écart entre les deux méthodes
        rating_difference = abs(mistral_rating - local_rating)
        
        # Si les résultats sont cohérents (écart < 1 point), on privilégie Mistral
        if rating_difference < 1.0:
            result = mistral_result.copy()
            result['local_comparison'] = {
                'local_rating': local_rating,
                'difference': rating_difference,
                'coherence': 'good'
            }
            result['reconciliation_applied'] = False
            
        else:
            # Si écart important, on fait une moyenne pondérée selon la confiance
            if mistral_confidence > 0.7:
                # Confiance élevée Mistral : 80% Mistral, 20% local
                final_rating = 0.8 * mistral_rating + 0.2 * local_rating
                weight_mistral = 0.8
            elif mistral_confidence > 0.4:
                # Confiance modérée : 60% Mistral, 40% local
                final_rating = 0.6 * mistral_rating + 0.4 * local_rating
                weight_mistral = 0.6
            else:
                # Confiance faible : 40% Mistral, 60% local
                final_rating = 0.4 * mistral_rating + 0.6 * local_rating
                weight_mistral = 0.4
            
            result = mistral_result.copy()
            result['suggested_rating'] = round(final_rating, 1)
            result['local_comparison'] = {
                'local_rating': local_rating,
                'difference': rating_difference,
                'coherence': 'poor',
                'weight_mistral': weight_mistral,
                'weight_local': 1.0 - weight_mistral
            }
            result['reconciliation_applied'] = True
            result['justification'] += f" (Ajusté par réconciliation locale: écart de {rating_difference:.1f})"
        
        return result
    
    def _validate_rating_result(self, result: Dict[str, Any]) -> None:
        """
        Valide un résultat de calcul de note
        
        Args:
            result: Résultat à valider
            
        Raises:
            Exception: Si le résultat est invalide
        """
        if 'suggested_rating' not in result:
            raise Exception("Note manquante dans le résultat")
        
        rating = result['suggested_rating']
        if not isinstance(rating, (int, float)):
            raise Exception(f"Note invalide (type): {type(rating)}")
        
        if not (1 <= rating <= 5):
            raise Exception(f"Note hors limites: {rating} (doit être entre 1 et 5)")
        
        if 'confidence' in result:
            confidence = result['confidence']
            if not (0 <= confidence <= 1):
                raise Exception(f"Confiance hors limites: {confidence}")
    
    def _generate_local_justification(self, sentiment: str, intensity: float, confidence: float, questionnaire_note: float, final_rating: float) -> str:
        """
        Génère une justification pour le calcul local
        
        Args:
            sentiment: Sentiment détecté
            intensity: Intensité émotionnelle
            confidence: Confiance de l'analyse
            questionnaire_note: Note du questionnaire
            final_rating: Note finale calculée
            
        Returns:
            str: Justification textuelle
        """
        justification_parts = []
        
        # Sentiment
        sentiment_texts = {
            'positif': 'Le sentiment exprimé est positif',
            'negatif': 'Le sentiment exprimé est négatif',
            'neutre': 'Le sentiment exprimé est neutre'
        }
        justification_parts.append(sentiment_texts.get(sentiment, 'Sentiment indéterminé'))
        
        # Intensité
        if intensity > 0.8:
            justification_parts.append('avec une forte intensité émotionnelle')
        elif intensity > 0.5:
            justification_parts.append('avec une intensité émotionnelle modérée')
        else:
            justification_parts.append('avec une faible intensité émotionnelle')
        
        # Questionnaire
        if questionnaire_note is not None:
            justification_parts.append(f'La note questionnaire ({questionnaire_note:.1f}/5) a été intégrée dans le calcul hybride')
        
        # Confiance
        if confidence < 0.4:
            justification_parts.append('La confiance de l\'analyse étant faible, la note a été modérée')
        
        # Note finale
        if final_rating >= 4.5:
            justification_parts.append('indiquant une expérience excellente')
        elif final_rating >= 3.5:
            justification_parts.append('indiquant une expérience satisfaisante')
        elif final_rating >= 2.5:
            justification_parts.append('indiquant une expérience mitigée')
        else:
            justification_parts.append('indiquant une expérience décevante')
        
        return '. '.join(justification_parts) + '.'
    
    def _get_fallback_rating(self, text: str, sentiment_analysis: Dict[str, Any] = None, questionnaire_note: float = None, error: str = "IA indisponible") -> Dict[str, Any]:
        """
        Calcule une note en mode dégradé (sans IA)
        
        Args:
            text: Texte de l'avis
            sentiment_analysis: Analyse de sentiment (peut être en mode dégradé)
            questionnaire_note: Note du questionnaire
            error: Message d'erreur
            
        Returns:
            dict: Note en mode dégradé
        """
        # Si on n'a pas d'analyse de sentiment, on en fait une locale
        if sentiment_analysis is None:
            try:
                sentiment_analysis = self.sentiment_analyzer.analyze_sentiment(text)
            except:
                sentiment_analysis = {
                    'sentiment': 'neutre',
                    'confidence': 0.0,
                    'emotional_intensity': 0.5,
                    'fallback_mode': True
                }
        
        # Calcul local
        local_result = self._calculate_local_rating(sentiment_analysis, questionnaire_note)
        
        # Mode dégradé ultime : utiliser la note questionnaire si disponible
        if questionnaire_note is not None and sentiment_analysis.get('fallback_mode', False):
            # Si l'analyse de sentiment est aussi en mode dégradé, on privilégie le questionnaire
            rating = questionnaire_note
            justification = f"Mode dégradé complet: utilisation de la note questionnaire ({questionnaire_note:.1f}/5)"
            confidence = 0.0
        else:
            rating = local_result['suggested_rating']
            justification = f"Mode dégradé: {local_result['justification']}"
            confidence = local_result['confidence'] * 0.5  # Confiance réduite en mode dégradé
        
        return {
            'suggested_rating': rating,
            'confidence': confidence,
            'justification': justification,
            'factors': local_result.get('factors', {}),
            'hybrid_mode': questionnaire_note is not None,
            'fallback_mode': True,
            'calculation_method': 'fallback_local',
            'error': error
        }
    
    def _get_default_rating(self) -> Dict[str, Any]:
        """
        Retourne une note par défaut pour les cas d'erreur
        
        Returns:
            dict: Note par défaut (3/5)
        """
        return {
            'suggested_rating': 3.0,
            'confidence': 0.0,
            'justification': 'Note par défaut en l\'absence de données suffisantes',
            'factors': {
                'sentiment_weight': 0.0,
                'intensity_weight': 0.0,
                'content_weight': 0.0
            },
            'hybrid_mode': False,
            'fallback_mode': True,
            'calculation_method': 'default',
            'error': 'Données insuffisantes'
        }
    
    # ============== MÉTHODES UTILITAIRES ==============
    
    def calculate_etablissement_note(self, scores: Dict[str, int]) -> Dict[str, Any]:
        """
        Calcule la note globale d'un questionnaire établissement
        
        Args:
            scores: {medecins: int, personnel: int, accueil: int, prise_en_charge: int, confort: int}
            
        Returns:
            dict: Note globale et détails
        """
        aspects = ['medecins', 'personnel', 'accueil', 'prise_en_charge', 'confort']
        valid_scores = []
        
        for aspect in aspects:
            score = scores.get(aspect, 3)
            if not isinstance(score, (int, float)) or not (1 <= score <= 5):
                self.logger.warning(f"Score invalide pour {aspect}: {score}, utilisation de 3 par défaut")
                score = 3
            valid_scores.append(score)
        
        note_globale = sum(valid_scores) / len(valid_scores)
        
        return {
            'note_globale': round(note_globale, 1),
            'details': dict(zip(aspects, valid_scores)),
            'type': 'etablissement',
            'nb_aspects': len(aspects)
        }
    
    def calculate_medecin_note(self, evaluations: Dict[str, str]) -> Dict[str, Any]:
        """
        Calcule la note globale d'un questionnaire médecin
        
        Args:
            evaluations: {explications: str, confiance: str, motivation: str, respect: str}
            
        Returns:
            dict: Note globale et détails
        """
        # Mapping des réponses textuelles vers des notes
        text_to_rating = {
            # Explications
            'Très insuffisantes': 1, 'Insuffisantes': 2, 'Correctes': 3, 'Bonnes': 4, 'Excellentes': 5,
            # Confiance
            'Aucune confiance': 1, 'Peu de confiance': 2, 'Confiance modérée': 3, 
            'Bonne confiance': 4, 'Confiance totale': 5,
            # Motivation
            'Aucune motivation': 1, 'Peu motivé': 2, 'Moyennement motivé': 3,
            'Bien motivé': 4, 'Très motivé': 5,
            # Respect
            'Pas du tout': 1, 'Peu respectueux': 2, 'Modérément respectueux': 3,
            'Respectueux': 4, 'Très respectueux': 5
        }
        
        criteria = ['explications', 'confiance', 'motivation', 'respect']
        scores = []
        details = {}
        
        for criterion in criteria:
            evaluation = evaluations.get(criterion, 'Correctes')  # Valeur par défaut
            score = text_to_rating.get(evaluation, 3)
            scores.append(score)
            details[criterion] = {
                'evaluation': evaluation,
                'note': score
            }
        
        note_globale = sum(scores) / len(scores)
        
        return {
            'note_globale': round(note_globale, 1),
            'details': details,
            'type': 'medecin',
            'nb_criteres': len(criteria)
        }
    
    def get_rating_distribution(self, ratings: list) -> Dict[str, Any]:
        """
        Analyse une distribution de notes
        
        Args:
            ratings: Liste de notes
            
        Returns:
            dict: Statistiques de distribution
        """
        if not ratings:
            return {'error': 'Aucune note fournie'}
        
        ratings = [r for r in ratings if isinstance(r, (int, float)) and 1 <= r <= 5]
        
        if not ratings:
            return {'error': 'Aucune note valide'}
        
        return {
            'count': len(ratings),
            'moyenne': round(sum(ratings) / len(ratings), 1),
            'mediane': round(sorted(ratings)[len(ratings) // 2], 1),
            'min': min(ratings),
            'max': max(ratings),
            'distribution': {
                '1-2': len([r for r in ratings if r < 2.5]),
                '2-3': len([r for r in ratings if 2.5 <= r < 3.5]),
                '3-4': len([r for r in ratings if 3.5 <= r < 4.5]),
                '4-5': len([r for r in ratings if r >= 4.5])
            }
        }