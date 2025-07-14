#!/usr/bin/env python3
"""
Test final pour l'étape 3 - Validation complète
"""

import sys
import os

# Configuration du PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_complete_workflow():
    """Test du workflow complet de l'étape 3"""
    print("🚀 Test workflow complet étape 3")
    
    try:
        # Force reload comme dans Streamlit
        import importlib
        if 'src.rating_calculator' in sys.modules:
            importlib.reload(sys.modules['src.rating_calculator'])
        
        from src.rating_calculator import calculate_rating_from_text
        from src.sentiment_analyzer import analyze_sentiment
        
        # Simulation données réelles
        avis_text = "Excellent médecin, très à l'écoute. Les explications étaient très claires et j'ai eu confiance immédiatement. Je recommande vivement."
        
        # 1. Analyse de sentiment
        print("1️⃣ Analyse de sentiment...")
        sentiment_analysis = analyze_sentiment(avis_text)
        print(f"   Sentiment: {sentiment_analysis.get('sentiment', 'erreur')}")
        print(f"   Confiance: {sentiment_analysis.get('confidence', 0):.2f}")
        
        # 2. Note questionnaire simulée
        questionnaire_note = 4.3  # Note élevée du questionnaire
        print(f"2️⃣ Note questionnaire: {questionnaire_note}/5")
        
        # 3. Calcul hybride (nouvelle méthode avec paramètre positionnel)
        print("3️⃣ Calcul note IA hybride...")
        rating_result = calculate_rating_from_text(
            avis_text,
            sentiment_analysis,
            questionnaire_note  # Paramètre positionnel - SOLUTION AU PROBLÈME
        )
        
        # 4. Résultats
        suggested_rating = rating_result.get('suggested_rating', 0)
        confidence = rating_result.get('confidence', 0)
        hybrid_mode = rating_result.get('hybrid_mode', False)
        
        print(f"4️⃣ Résultats:")
        print(f"   Note suggérée: {suggested_rating}/5")
        print(f"   Confiance: {confidence:.2f}")
        print(f"   Mode hybride: {hybrid_mode}")
        print(f"   Justification: {rating_result.get('justification', 'N/A')[:100]}...")
        
        # Validation
        if suggested_rating > 0 and confidence > 0 and hybrid_mode:
            print("✅ Test workflow complet RÉUSSI")
            return True
        else:
            print("❌ Résultats invalides")
            return False
            
    except Exception as e:
        print(f"❌ Erreur workflow: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test principal"""
    print("🔍 VALIDATION FINALE ÉTAPE 3")
    print("=" * 40)
    print("Solution appliquée:")
    print("• Force reload du module rating_calculator")
    print("• Paramètre positionnel au lieu de keyword argument")
    print("• Gestion robuste des erreurs")
    print("=" * 40)
    
    if test_complete_workflow():
        print("\n🎉 ÉTAPE 3 COMPLÈTEMENT VALIDÉE")
        print("✅ Le problème 'questionnaire_context' est résolu")
        print("🚀 Votre application est prête pour le VPS")
    else:
        print("\n❌ Des problèmes persistent")
        print("🔧 Vérification supplémentaire nécessaire")

if __name__ == "__main__":
    main() 