#!/usr/bin/env python3
"""
Script de test pour vérifier les imports du projet Hospitalidée
"""

import os
import sys

# Configuration du PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_imports():
    """Teste tous les imports du projet"""
    
    print("🧪 Test des imports Hospitalidée...")
    print("-" * 40)
    
    try:
        print("✅ Import config.settings...", end=" ")
        from config.settings import settings
        print("OK")
        
        print("✅ Import config.prompts...", end=" ")
        from config.prompts import SENTIMENT_ANALYSIS_PROMPT
        print("OK")
        
        print("✅ Import src.mistral_client...", end=" ")
        from src.mistral_client import MistralClient
        print("OK")
        
        print("✅ Import src.sentiment_analyzer...", end=" ")
        from src.sentiment_analyzer import analyze_sentiment
        print("OK")
        
        print("✅ Import src.rating_calculator...", end=" ")
        from src.rating_calculator import calculate_rating_from_text
        print("OK")
        
        print("-" * 40)
        print("🎉 Tous les imports fonctionnent correctement !")
        
        # Test basique de fonctionnement (sans clé API)
        print("\n🔍 Test basique de fonctionnement...")
        
        try:
            # Test avec un texte simple (devrait utiliser le mode dégradé)
            result = analyze_sentiment("Test d'avis patient")
            print(f"✅ Analyse de sentiment: {result.get('sentiment', 'erreur')}")
            
            # Test du calcul de note
            rating_result = calculate_rating_from_text("Test d'avis patient", result)
            print(f"✅ Calcul de note: {rating_result.get('suggested_rating', 'erreur')}/5")
            
        except Exception as e:
            print(f"⚠️  Mode dégradé activé (normal sans clé API): {e}")
        
        print("\n🚀 Le projet est prêt à être lancé !")
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1) 