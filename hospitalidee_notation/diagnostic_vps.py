#!/usr/bin/env python3
"""
Script de diagnostic pour identifier les problèmes entre environnement local et VPS
"""

import sys
import os
import traceback
import inspect

# Configuration du PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_imports():
    """Test des imports"""
    print("🔍 Test des imports...")
    try:
        from src.rating_calculator import calculate_rating_from_text
        print("✅ Import calculate_rating_from_text OK")
        
        # Vérifier la signature de la fonction
        sig = inspect.signature(calculate_rating_from_text)
        print(f"📋 Signature: {sig}")
        
        return calculate_rating_from_text
    except Exception as e:
        print(f"❌ Erreur import: {e}")
        traceback.print_exc()
        return None

def test_function_call(func):
    """Test de l'appel de fonction avec le paramètre questionnaire_context"""
    print("\n🧪 Test de l'appel de fonction...")
    
    try:
        # Test sans questionnaire_context
        print("Test 1: Sans questionnaire_context")
        result1 = func("Test d'avis positif")
        print(f"✅ Résultat 1: {result1.get('suggested_rating', 'erreur')}")
        
        # Test avec questionnaire_context
        print("Test 2: Avec questionnaire_context=4.0")
        result2 = func(
            text="Test d'avis positif", 
            sentiment_analysis=None,
            questionnaire_context=4.0
        )
        print(f"✅ Résultat 2: {result2.get('suggested_rating', 'erreur')}")
        
        # Test avec les 3 paramètres
        print("Test 3: Avec tous les paramètres")
        sentiment_test = {
            'sentiment': 'positif',
            'confidence': 0.8,
            'emotional_intensity': 0.7
        }
        result3 = func(
            text="Test d'avis positif", 
            sentiment_analysis=sentiment_test,
            questionnaire_context=4.0
        )
        print(f"✅ Résultat 3: {result3.get('suggested_rating', 'erreur')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'appel: {e}")
        print(f"📄 Type d'erreur: {type(e).__name__}")
        traceback.print_exc()
        return False

def test_environment():
    """Test de l'environnement"""
    print("\n🌐 Informations environnement:")
    print(f"Python version: {sys.version}")
    print(f"Plateforme: {sys.platform}")
    print(f"Répertoire courant: {os.getcwd()}")
    print(f"PYTHONPATH: {sys.path[:3]}...")  # Premiers éléments seulement
    
    # Test des variables d'environnement
    env_vars = ['MISTRAL_API_KEY', 'PYTHONPATH', 'PATH']
    for var in env_vars:
        value = os.environ.get(var, 'NON_DEFINIE')
        # Masquer la clé API pour sécurité
        if var == 'MISTRAL_API_KEY' and value != 'NON_DEFINIE':
            value = f"{value[:8]}...{value[-4:]}"
        print(f"{var}: {value}")

def test_class_vs_function():
    """Test la différence entre méthode de classe et fonction standalone"""
    print("\n🔬 Test classe vs fonction...")
    
    try:
        # Test de la méthode de classe
        from src.rating_calculator import RatingCalculator
        calculator = RatingCalculator()
        
        print("Test méthode de classe:")
        result_method = calculator.calculate_rating_from_text(
            text="Test positif",
            questionnaire_context=4.0
        )
        print(f"✅ Méthode: {result_method.get('suggested_rating', 'erreur')}")
        
        # Test de la fonction standalone
        from src.rating_calculator import calculate_rating_from_text
        print("Test fonction standalone:")
        result_function = calculate_rating_from_text(
            text="Test positif",
            questionnaire_context=4.0
        )
        print(f"✅ Fonction: {result_function.get('suggested_rating', 'erreur')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test classe/fonction: {e}")
        traceback.print_exc()
        return False

def main():
    """Script principal de diagnostic"""
    print("🩺 DIAGNOSTIC VPS vs LOCAL")
    print("=" * 40)
    
    # Test des imports
    func = test_imports()
    if not func:
        print("❌ Impossible de continuer sans les imports")
        return
    
    # Test de l'environnement
    test_environment()
    
    # Test des appels de fonction
    test_function_call(func)
    
    # Test classe vs fonction
    test_class_vs_function()
    
    print("\n" + "=" * 40)
    print("✅ Diagnostic terminé")
    print("📧 Envoyez ce résultat pour comparaison local/VPS")

if __name__ == "__main__":
    main() 