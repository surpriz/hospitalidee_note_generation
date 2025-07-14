#!/usr/bin/env python3
"""
Script de diagnostic pour l'intégration Mistral AI
Vérifie la configuration, la connectivité et les performances
"""

import os
import sys
import time
import requests
from typing import Dict, Any

# Ajouter le répertoire parent au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Charger le fichier .env
try:
    from dotenv import load_dotenv
    load_dotenv('.env')
except ImportError:
    pass

def check_environment():
    """Vérifie les variables d'environnement"""
    print("🔍 Vérification de l'environnement...")
    
    # Variables critiques
    critical_vars = {
        'MISTRAL_API_KEY': os.getenv('MISTRAL_API_KEY'),
        'MISTRAL_MODEL': os.getenv('MISTRAL_MODEL', 'mistral-small-latest'),
        'MAX_RESPONSE_TIME': os.getenv('MAX_RESPONSE_TIME', '30.0')
    }
    
    all_good = True
    for var, value in critical_vars.items():
        if value:
            if var == 'MISTRAL_API_KEY':
                masked_value = f"{value[:8]}..." if len(value) > 8 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NON DÉFINIE")
            all_good = False
    
    if not all_good:
        print("\n⚠️  Variables manquantes détectées!")
        print("💡 Solution:")
        print("   1. Copiez config_example.env vers .env")
        print("   2. Remplissez votre clé API Mistral")
        print("   3. Exécutez: export $(cat .env | xargs)")
        return False
    
    return True

def test_mistral_connectivity():
    """Test de connectivité de base avec l'API Mistral"""
    print("\n🌐 Test de connectivité Mistral...")
    
    api_key = os.getenv('MISTRAL_API_KEY')
    if not api_key:
        print("❌ Clé API manquante")
        return False
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test simple avec timeout court
    simple_payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": "Bonjour"}],
        "max_tokens": 10
    }
    
    try:
        start_time = time.time()
        response = requests.post(url, json=simple_payload, headers=headers, timeout=10)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Connectivité OK ({elapsed:.2f}s)")
            return True
        elif response.status_code == 401:
            print("❌ Clé API invalide")
            return False
        elif response.status_code == 429:
            print("❌ Rate limit atteint")
            return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout de connexion")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion réseau")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def test_mistral_performance():
    """Test de performance avec l'API Mistral"""
    print("\n⚡ Test de performance...")
    
    try:
        from src.mistral_client import MistralClient
        
        client = MistralClient()
        
        # Test d'analyse de sentiment
        test_text = "L'hôpital était très bien, le personnel était attentif et professionnel."
        
        start_time = time.time()
        result = client.analyze_sentiment(test_text)
        elapsed = time.time() - start_time
        
        if 'error' in result:
            print(f"❌ Erreur dans l'analyse: {result['error']}")
            return False
        else:
            print(f"✅ Analyse de sentiment OK ({elapsed:.2f}s)")
            print(f"   Résultat: {result.get('sentiment', 'inconnu')} (confiance: {result.get('confidence', 0):.1%})")
            
            if elapsed > 30:
                print("⚠️  Temps de réponse élevé (>30s)")
            elif elapsed > 10:
                print("⚠️  Temps de réponse modéré (>10s)")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur de performance: {e}")
        return False

def test_fallback_mode():
    """Test du mode dégradé"""
    print("\n🔄 Test du mode dégradé...")
    
    try:
        from src.sentiment_analyzer import analyze_sentiment
        
        # Test avec texte simple
        test_text = "Service excellent, très satisfait!"
        result = analyze_sentiment(test_text)
        
        # Vérifier que même sans API, on a un résultat
        if result and 'sentiment' in result:
            print("✅ Mode dégradé fonctionnel")
            print(f"   Sentiment: {result['sentiment']}")
            print(f"   Confiance: {result.get('confidence', 0):.1%}")
            return True
        else:
            print("❌ Mode dégradé non fonctionnel")
            return False
            
    except Exception as e:
        print(f"❌ Erreur mode dégradé: {e}")
        return False

def run_full_diagnostic():
    """Exécute le diagnostic complet"""
    print("🏥 Diagnostic Mistral AI - Hospitalidée")
    print("=" * 50)
    
    tests = [
        ("Configuration", check_environment),
        ("Connectivité", test_mistral_connectivity),
        ("Performance", test_mistral_performance),
        ("Mode dégradé", test_fallback_mode)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Erreur lors du test {test_name}: {e}")
            results[test_name] = False
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSÉ" if result else "❌ ÉCHOUÉ"
        print(f"{test_name:<15}: {status}")
    
    print(f"\nScore global: {passed}/{total}")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! L'IA devrait fonctionner correctement.")
        return True
    elif passed >= total * 0.5:
        print("⚠️  Certains problèmes détectés mais le système peut fonctionner en mode dégradé.")
        return True
    else:
        print("❌ Problèmes critiques détectés. Vérifiez la configuration.")
        return False

def print_recommendations():
    """Affiche des recommandations pour résoudre les problèmes"""
    print("\n💡 RECOMMANDATIONS")
    print("=" * 50)
    print("1. **Configuration manquante :**")
    print("   - Copiez config_example.env vers .env")
    print("   - Ajoutez votre clé API Mistral")
    print("   - Chargez les variables: export $(cat .env | xargs)")
    print("")
    print("2. **Problèmes de connectivité :**")
    print("   - Vérifiez votre connexion internet")
    print("   - Vérifiez que l'API Mistral est accessible")
    print("   - Testez manuellement: curl -H 'Authorization: Bearer VOTRE_CLE' https://api.mistral.ai/v1/models")
    print("")
    print("3. **Performance lente :**")
    print("   - L'API peut être surchargée temporairement")
    print("   - Augmentez MAX_RESPONSE_TIME si nécessaire")
    print("   - Utilisez le mode dégradé en attendant")
    print("")
    print("4. **Mode dégradé non fonctionnel :**")
    print("   - Vérifiez les imports Python")
    print("   - Exécutez: python test_imports.py")

if __name__ == "__main__":
    success = run_full_diagnostic()
    print_recommendations()
    
    if success:
        print("\n🚀 Prêt à utiliser l'application Hospitalidée !")
    else:
        print("\n🔧 Configuration requise avant utilisation.")
    
    sys.exit(0 if success else 1) 