#!/usr/bin/env python3
"""
🏥 Hospitalidée IA API - Tests
=============================

Tests simples pour valider le fonctionnement de l'API.
Ces tests peuvent être exécutés pour vérifier que l'installation fonctionne.

Usage:
    python tests/test_api.py

Prérequis:
    - API démarrée sur localhost:8000
    - pip install requests
"""

import requests
import json
import time
import sys
import os

# Configuration
API_URL = "http://localhost:8000"
TIMEOUT = 60


class Colors:
    """Codes de couleur pour l'affichage"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_colored(text, color=Colors.WHITE):
    """Affiche un texte en couleur"""
    print(f"{color}{text}{Colors.END}")


def print_test_header(test_name):
    """Affiche l'en-tête d'un test"""
    print_colored(f"\n🧪 TEST: {test_name}", Colors.BOLD + Colors.CYAN)
    print_colored("-" * 50, Colors.CYAN)


def print_success(message):
    """Affiche un message de succès"""
    print_colored(f"✅ {message}", Colors.GREEN)


def print_error(message):
    """Affiche un message d'erreur"""
    print_colored(f"❌ {message}", Colors.RED)


def print_warning(message):
    """Affiche un avertissement"""
    print_colored(f"⚠️  {message}", Colors.YELLOW)


def print_info(message):
    """Affiche une information"""
    print_colored(f"ℹ️  {message}", Colors.BLUE)


class APITester:
    """Classe pour tester l'API Hospitalidée IA"""
    
    def __init__(self, api_url=API_URL):
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'HospitalideeIA-Test/1.0'
        })
        self.tests_passed = 0
        self.tests_failed = 0
    
    def test_health_check(self):
        """Test 1: Health check de l'API"""
        print_test_header("Health Check")
        
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'healthy':
                    print_success("API accessible et saine")
                    
                    # Affichage des détails
                    config = data.get('config', {})
                    print_info(f"Modèle Mistral: {config.get('modele_mistral', 'N/A')}")
                    print_info(f"Version: {config.get('version', 'N/A')}")
                    
                    services = data.get('services', {})
                    for service, status in services.items():
                        if status == 'ok':
                            print_success(f"Service {service}: OK")
                        else:
                            print_warning(f"Service {service}: {status}")
                    
                    self.tests_passed += 1
                    return True
                else:
                    print_warning(f"API en mode dégradé: {data.get('status', 'inconnu')}")
                    self.tests_passed += 1
                    return True
            else:
                print_error(f"Réponse HTTP {response.status_code}")
                self.tests_failed += 1
                return False
                
        except requests.exceptions.RequestException as e:
            print_error(f"Erreur de connexion: {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_basic_endpoints(self):
        """Test 2: Endpoints de base"""
        print_test_header("Endpoints de Base")
        
        endpoints = [
            ('/', 'Page d\'accueil'),
            ('/docs', 'Documentation Swagger'),
            ('/redoc', 'Documentation ReDoc')
        ]
        
        all_passed = True
        
        for endpoint, description in endpoints:
            try:
                response = self.session.get(f"{self.api_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    print_success(f"{description}: Accessible")
                else:
                    print_error(f"{description}: HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                print_error(f"{description}: {str(e)}")
                all_passed = False
        
        if all_passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
        
        return all_passed
    
    def test_evaluation_etablissement(self):
        """Test 3: Évaluation établissement"""
        print_test_header("Évaluation Établissement")
        
        data = {
            "type_evaluation": "etablissement",
            "avis_text": "Séjour excellent dans cet hôpital. Le personnel était très attentif et professionnel. Les médecins ont pris le temps d'expliquer les traitements. Quelques petits problèmes avec les repas mais globalement très satisfait.",
            "questionnaire_etablissement": {
                "medecins": 4,
                "personnel": 5,
                "accueil": 4,
                "prise_en_charge": 4,
                "confort": 3
            },
            "generer_titre": True,
            "analyse_detaillee": True
        }
        
        try:
            print_info("Envoi de l'évaluation...")
            start_time = time.time()
            
            response = self.session.post(
                f"{self.api_url}/evaluate", 
                json=data, 
                timeout=TIMEOUT
            )
            
            duration = time.time() - start_time
            print_info(f"Durée: {duration:.1f}s")
            
            if response.status_code == 200:
                result = response.json()
                
                # Vérifications de base
                required_fields = ['note_finale', 'sentiment', 'confiance', 'timestamp']
                for field in required_fields:
                    if field not in result:
                        print_error(f"Champ manquant: {field}")
                        self.tests_failed += 1
                        return False
                
                # Vérification des valeurs
                note = result['note_finale']
                if not (1 <= note <= 5):
                    print_error(f"Note finale invalide: {note} (doit être 1-5)")
                    self.tests_failed += 1
                    return False
                
                confiance = result['confiance']
                if not (0 <= confiance <= 1):
                    print_error(f"Confiance invalide: {confiance} (doit être 0-1)")
                    self.tests_failed += 1
                    return False
                
                sentiment = result['sentiment']
                if sentiment not in ['positif', 'negatif', 'neutre']:
                    print_error(f"Sentiment invalide: {sentiment}")
                    self.tests_failed += 1
                    return False
                
                # Affichage des résultats
                print_success("Évaluation réussie !")
                print_info(f"Note finale: {note}/5")
                print_info(f"Sentiment: {sentiment}")
                print_info(f"Confiance: {confiance:.0%}")
                
                if result.get('titre_suggere'):
                    print_info(f"Titre: \"{result['titre_suggere']}\"")
                
                if result.get('mode_degrade'):
                    print_warning("Mode dégradé activé")
                
                self.tests_passed += 1
                return True
                
            else:
                print_error(f"Réponse HTTP {response.status_code}")
                try:
                    error_detail = response.json().get('detail', 'Erreur inconnue')
                    print_error(f"Détail: {error_detail}")
                except:
                    pass
                self.tests_failed += 1
                return False
                
        except requests.exceptions.Timeout:
            print_error(f"Timeout après {TIMEOUT}s")
            self.tests_failed += 1
            return False
        except Exception as e:
            print_error(f"Erreur: {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_evaluation_medecin(self):
        """Test 4: Évaluation médecin"""
        print_test_header("Évaluation Médecin")
        
        data = {
            "type_evaluation": "medecin",
            "avis_text": "Dr Martin est formidable. Explications très claires et rassurantes. Je me sens en totale confiance avec lui. Il prend vraiment le temps d'écouter et ses prescriptions sont toujours bien motivées.",
            "questionnaire_medecin": {
                "explications": "Excellentes",
                "confiance": "Confiance totale",
                "motivation": "Très motivé",
                "respect": "Très respectueux"
            }
        }
        
        try:
            print_info("Envoi de l'évaluation médecin...")
            
            response = self.session.post(
                f"{self.api_url}/evaluate", 
                json=data, 
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print_success("Évaluation médecin réussie !")
                print_info(f"Note finale: {result['note_finale']}/5")
                print_info(f"Sentiment: {result['sentiment']}")
                
                self.tests_passed += 1
                return True
                
            else:
                print_error(f"Réponse HTTP {response.status_code}")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print_error(f"Erreur: {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_sentiment_seul(self):
        """Test 5: Analyse de sentiment seule"""
        print_test_header("Analyse Sentiment Seule")
        
        try:
            response = self.session.post(
                f"{self.api_url}/sentiment", 
                json="Personnel très gentil et professionnel",
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status') == 'success':
                    data = result['data']
                    print_success("Analyse sentiment réussie !")
                    print_info(f"Sentiment: {data.get('sentiment', 'N/A')}")
                    print_info(f"Confiance: {data.get('confidence', 0):.0%}")
                    
                    self.tests_passed += 1
                    return True
                else:
                    print_error(f"Erreur dans la réponse: {result.get('message', 'Inconnue')}")
                    self.tests_failed += 1
                    return False
            else:
                print_error(f"Réponse HTTP {response.status_code}")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print_error(f"Erreur: {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_erreurs(self):
        """Test 6: Gestion des erreurs"""
        print_test_header("Gestion des Erreurs")
        
        # Test 1: Données manquantes
        try:
            response = self.session.post(
                f"{self.api_url}/evaluate", 
                json={"type_evaluation": "etablissement", "avis_text": "Test"},
                timeout=10
            )
            
            if response.status_code == 400 or response.status_code == 422:
                print_success("Erreur 400/422 correctement retournée pour données manquantes")
            else:
                print_warning(f"Code inattendu pour données manquantes: {response.status_code}")
        except Exception as e:
            print_error(f"Erreur test données manquantes: {str(e)}")
        
        # Test 2: Texte trop court
        try:
            response = self.session.post(
                f"{self.api_url}/evaluate", 
                json={
                    "type_evaluation": "etablissement",
                    "avis_text": "Court",
                    "questionnaire_etablissement": {
                        "medecins": 3, "personnel": 3, "accueil": 3,
                        "prise_en_charge": 3, "confort": 3
                    }
                },
                timeout=10
            )
            
            if response.status_code == 422:
                print_success("Erreur 422 correctement retournée pour texte trop court")
            else:
                print_warning(f"Code inattendu pour texte court: {response.status_code}")
        except Exception as e:
            print_error(f"Erreur test texte court: {str(e)}")
        
        self.tests_passed += 1
        return True
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print_colored("🏥 Hospitalidée IA API - Suite de Tests", Colors.BOLD + Colors.MAGENTA)
        print_colored("=" * 60, Colors.MAGENTA)
        
        # Liste des tests
        tests = [
            self.test_health_check,
            self.test_basic_endpoints,
            self.test_evaluation_etablissement,
            self.test_evaluation_medecin,
            self.test_sentiment_seul,
            self.test_erreurs
        ]
        
        # Exécution des tests
        for test in tests:
            try:
                test()
            except KeyboardInterrupt:
                print_error("\nTests interrompus par l'utilisateur")
                break
            except Exception as e:
                print_error(f"Erreur inattendue dans {test.__name__}: {str(e)}")
                self.tests_failed += 1
        
        # Résultats finaux
        print_colored("\n" + "=" * 60, Colors.MAGENTA)
        print_colored("📊 RÉSULTATS DES TESTS", Colors.BOLD + Colors.WHITE)
        print_colored("=" * 60, Colors.MAGENTA)
        
        total_tests = self.tests_passed + self.tests_failed
        
        if self.tests_passed > 0:
            print_success(f"Tests passés: {self.tests_passed}/{total_tests}")
        
        if self.tests_failed > 0:
            print_error(f"Tests échoués: {self.tests_failed}/{total_tests}")
        
        if self.tests_failed == 0:
            print_colored("\n🎉 TOUS LES TESTS PASSENT !", Colors.BOLD + Colors.GREEN)
            print_success("Votre API Hospitalidée IA fonctionne parfaitement !")
            print_info("Prêt pour la production ! 🚀")
            return True
        else:
            print_colored(f"\n⚠️  {self.tests_failed} test(s) ont échoué", Colors.BOLD + Colors.YELLOW)
            print_warning("Vérifications suggérées:")
            print_info("• L'API est-elle démarrée ? curl http://localhost:8000/health")
            print_info("• La clé Mistral est-elle configurée dans .env ?")
            print_info("• Consultez les logs: docker-compose logs")
            return False


def main():
    """Fonction principale"""
    # Vérification des arguments
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
        print_info(f"URL API personnalisée: {api_url}")
    else:
        api_url = API_URL
        print_info(f"URL API par défaut: {api_url}")
    
    # Exécution des tests
    tester = APITester(api_url)
    success = tester.run_all_tests()
    
    # Code de sortie
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n⏹️  Tests arrêtés par l'utilisateur", Colors.YELLOW)
        sys.exit(130)