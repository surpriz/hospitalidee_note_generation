#!/usr/bin/env python3
"""
Test spécifique pour l'étape 3 - calcul de note IA hybride
Reproduit le problème et teste la solution
"""

import sys
import os

# Configuration du PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_import_fresh():
    """Test avec import frais (comme Streamlit)"""
    print("🧪 Test 1: Import frais")
    
    # Nettoyer le cache comme le fait Streamlit
    if 'src.rating_calculator' in sys.modules:
        del sys.modules['src.rating_calculator']
    if 'src.sentiment_analyzer' in sys.modules:
        del sys.modules['src.sentiment_analyzer']
    if 'src.mistral_client' in sys.modules:
        del sys.modules['src.mistral_client']
    
    try:
        from src.rating_calculator import calculate_rating_from_text
        print("✅ Import réussi")
        
        # Test avec keyword argument (celui qui échouait)
        print("Test avec keyword argument...")
        result1 = calculate_rating_from_text(
            "Test positif",
            None,
            questionnaire_context=4.0
        )
        print(f"✅ Keyword argument: {result1.get('suggested_rating', 'erreur')}")
        
        # Test avec paramètre positionnel (nouvelle méthode)
        print("Test avec paramètre positionnel...")
        result2 = calculate_rating_from_text(
            "Test positif",
            None,
            4.0  # Paramètre positionnel
        )
        print(f"✅ Paramètre positionnel: {result2.get('suggested_rating', 'erreur')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_simulation():
    """Simule l'environnement Streamlit"""
    print("\n🧪 Test 2: Simulation environnement Streamlit")
    
    # Simulation des variables de session Streamlit
    class MockSessionState:
        def __init__(self):
            self.avis_text = "Très bon médecin, explications claires et rassurantes"
            self.sentiment_analysis = {
                'sentiment': 'positif',
                'confidence': 0.9,
                'emotional_intensity': 0.8
            }
            self.note_questions_fermees = 4.2
    
    session_state = MockSessionState()
    
    try:
        from src.rating_calculator import calculate_rating_from_text
        
        # Test de l'appel exact utilisé dans Streamlit (après correction)
        rating_result = calculate_rating_from_text(
            session_state.avis_text, 
            session_state.sentiment_analysis,
            session_state.note_questions_fermees  # Paramètre positionnel
        )
        
        print(f"✅ Simulation Streamlit réussie: {rating_result.get('suggested_rating', 'erreur')}")
        print(f"   Confiance: {rating_result.get('confidence', 0):.2f}")
        print(f"   Mode hybride: {rating_result.get('hybrid_mode', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur simulation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_signature_verification():
    """Vérifie la signature de la fonction"""
    print("\n🧪 Test 3: Vérification signature")
    
    try:
        import inspect
        from src.rating_calculator import calculate_rating_from_text
        
        sig = inspect.signature(calculate_rating_from_text)
        print(f"📋 Signature: {sig}")
        
        # Vérifier les paramètres
        params = list(sig.parameters.keys())
        expected_params = ['text', 'sentiment_analysis', 'questionnaire_context']
        
        if params == expected_params:
            print("✅ Signature correcte")
            return True
        else:
            print(f"❌ Signature incorrecte. Attendu: {expected_params}, Trouvé: {params}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur vérification: {e}")
        return False

def main():
    """Test principal"""
    print("🔍 TEST SPÉCIFIQUE ÉTAPE 3 - CALCUL NOTE IA")
    print("=" * 50)
    
    tests = [
        test_signature_verification,
        test_import_fresh,
        test_streamlit_simulation
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 50)
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"🎉 TOUS LES TESTS RÉUSSIS ({success_count}/{total_count})")
        print("✅ Le problème de l'étape 3 devrait être résolu")
    else:
        print(f"⚠️ {success_count}/{total_count} tests réussis")
        print("❌ Des problèmes persistent")

if __name__ == "__main__":
    main() 