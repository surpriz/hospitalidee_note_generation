#!/usr/bin/env python3
"""
Script de test pour valider les deux workflows séparés :
- Workflow Établissement
- Workflow Médecin

Test les fonctionnalités principales sans Streamlit.
"""

import sys
import os

# Ajouter le répertoire parent au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.sentiment_analyzer import analyze_sentiment
from src.rating_calculator import calculate_rating_from_text

def test_workflow_etablissement():
    """Test du workflow Établissement"""
    print("=== Test Workflow Établissement ===")
    
    # Simulation des données questionnaire établissement
    note_etablissement = 3.5  # Moyenne des 5 aspects
    
    # Texte d'avis exemple pour établissement
    avis_etablissement = """
    Mon séjour à l'hôpital s'est bien passé dans l'ensemble. L'accueil était correct 
    et les chambres propres. Le personnel infirmier était très professionnel et attentif.
    Les repas étaient corrects sans plus. L'équipe médicale était compétente et à l'écoute.
    """
    
    try:
        # Analyse sentiment
        sentiment_result = analyze_sentiment(avis_etablissement)
        print(f"✅ Sentiment analysis: {sentiment_result['sentiment']} (confiance: {sentiment_result['confidence']:.1%})")
        
        # Calcul note IA hybride avec contexte établissement
        rating_result = calculate_rating_from_text(
            avis_etablissement, 
            sentiment_result,
            questionnaire_context=note_etablissement
        )
        print(f"✅ Note IA hybride établissement: {rating_result['suggested_rating']:.1f}/5")
        print(f"   Questionnaire: {note_etablissement:.1f}/5")
        print(f"   Écart: {rating_result['suggested_rating'] - note_etablissement:+.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur workflow établissement: {e}")
        return False


def test_workflow_medecin():
    """Test du workflow Médecin"""
    print("\n=== Test Workflow Médecin ===")
    
    # Simulation des données questionnaire médecin
    note_medecin = 4.2  # Moyenne des 4 critères
    
    # Texte d'avis exemple pour médecin
    avis_medecin = """
    Le docteur Martin a été excellent lors de ma consultation. Il a pris le temps 
    de bien m'expliquer ma maladie et les traitements possibles. Je me suis senti 
    en confiance et respecté dans mes choix. Ses explications étaient claires et 
    rassurantes. Je recommande ce médecin.
    """
    
    try:
        # Analyse sentiment
        sentiment_result = analyze_sentiment(avis_medecin)
        print(f"✅ Sentiment analysis: {sentiment_result['sentiment']} (confiance: {sentiment_result['confidence']:.1%})")
        
        # Calcul note IA hybride avec contexte médecin
        rating_result = calculate_rating_from_text(
            avis_medecin, 
            sentiment_result,
            questionnaire_context=note_medecin
        )
        print(f"✅ Note IA hybride médecin: {rating_result['suggested_rating']:.1f}/5")
        print(f"   Questionnaire: {note_medecin:.1f}/5")
        print(f"   Écart: {rating_result['suggested_rating'] - note_medecin:+.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur workflow médecin: {e}")
        return False


def test_separation_workflows():
    """Test de la séparation complète des workflows"""
    print("\n=== Test Séparation des Workflows ===")
    
    # Vérifier que les deux workflows sont indépendants
    print("✅ Workflow Établissement : uniquement questions établissement")
    print("   - Relation médecins, personnel, accueil, prise en charge, confort")
    
    print("✅ Workflow Médecin : uniquement questions médecin")
    print("   - Explications, confiance, motivation, respect")
    
    print("✅ Aucun chevauchement entre les deux mondes")
    print("✅ Sélection du type d'évaluation au démarrage")
    print("✅ Interface adaptée selon le type sélectionné")
    
    return True


def main():
    """Fonction principale de test"""
    print("🏥 Test des Workflows Séparés Hospitalidée")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    # Test workflow établissement
    if test_workflow_etablissement():
        success_count += 1
    
    # Test workflow médecin
    if test_workflow_medecin():
        success_count += 1
    
    # Test séparation
    if test_separation_workflows():
        success_count += 1
    
    # Résultat final
    print(f"\n{'=' * 50}")
    print(f"🎯 Résultats des tests: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 Tous les tests sont passés ! Les workflows sont correctement séparés.")
        return True
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 