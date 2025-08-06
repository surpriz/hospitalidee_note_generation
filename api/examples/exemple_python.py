#!/usr/bin/env python3
"""
🏥 Hospitalidée IA API - Exemple Python
======================================

Exemple d'intégration de l'API Hospitalidée IA en Python.
Montre comment utiliser l'API pour analyser des avis patients.

Usage:
    python exemple_python.py

Prérequis:
    pip install requests
"""

import requests
import json
import time
from typing import Dict, Any, Optional


class HospitalideeIA:
    """Client Python pour l'API Hospitalidée IA"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """
        Initialise le client API
        
        Args:
            api_url: URL de base de l'API
                    'http://localhost:8000'          → 💻 Tests en local
                    'http://VOTRE_IP_VPS:8000'       → 🌐 VPS production  
                    'https://api.votre-site.com'     → 🔒 VPS avec domaine SSL
        """
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'HospitalideeIA-Python-Client/1.0'
        })
    
    def evaluer_avis_complet(self, 
                           type_evaluation: str,
                           avis_text: str,
                           questionnaire_etablissement: Optional[Dict] = None,
                           questionnaire_medecin: Optional[Dict] = None,
                           generer_titre: bool = True,
                           analyse_detaillee: bool = True) -> Dict[str, Any]:
        """
        Évalue un avis patient de manière complète
        
        Args:
            type_evaluation: "etablissement" ou "medecin"
            avis_text: Texte de l'avis patient
            questionnaire_etablissement: Notes établissement (si type="etablissement")
            questionnaire_medecin: Évaluations médecin (si type="medecin")
            generer_titre: Générer un titre suggéré
            analyse_detaillee: Inclure l'analyse détaillée
            
        Returns:
            dict: Résultat complet de l'évaluation
            
        Raises:
            Exception: En cas d'erreur API
        """
        data = {
            'type_evaluation': type_evaluation,
            'avis_text': avis_text,
            'generer_titre': generer_titre,
            'analyse_detaillee': analyse_detaillee
        }
        
        # Ajouter le questionnaire approprié
        if type_evaluation == 'etablissement':
            if not questionnaire_etablissement:
                raise ValueError("questionnaire_etablissement requis pour type 'etablissement'")
            data['questionnaire_etablissement'] = questionnaire_etablissement
        elif type_evaluation == 'medecin':
            if not questionnaire_medecin:
                raise ValueError("questionnaire_medecin requis pour type 'medecin'")
            data['questionnaire_medecin'] = questionnaire_medecin
        else:
            raise ValueError("type_evaluation doit être 'etablissement' ou 'medecin'")
        
        return self._post('/evaluate', data)
    
    def analyser_sentiment_seul(self, text: str) -> Dict[str, Any]:
        """
        Analyse uniquement le sentiment d'un texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            dict: Analyse de sentiment
        """
        return self._post('/sentiment', text)
    
    def verifier_sante(self) -> Dict[str, Any]:
        """
        Vérifie que l'API fonctionne
        
        Returns:
            dict: Status de l'API
        """
        return self._get('/health')
    
    def _get(self, endpoint: str) -> Dict[str, Any]:
        """Effectue une requête GET"""
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur API GET {endpoint}: {str(e)}")
    
    def _post(self, endpoint: str, data: Any) -> Dict[str, Any]:
        """Effectue une requête POST"""
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = self.session.post(url, json=data, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json().get('detail', str(e))
                except:
                    error_detail = str(e)
                raise Exception(f"Erreur API POST {endpoint}: {error_detail}")
            else:
                raise Exception(f"Erreur API POST {endpoint}: {str(e)}")


def exemple_etablissement():
    """Exemple d'évaluation d'un établissement"""
    print("🏥 EXEMPLE: Évaluation Établissement")
    print("=" * 50)
    
    # Initialisation du client
    client = HospitalideeIA()
    
    # Données d'exemple
    avis_text = """
    Séjour globalement satisfaisant dans cet hôpital. Le personnel était très 
    professionnel et attentif, particulièrement les infirmières de nuit qui ont 
    été formidables. Les médecins ont pris le temps d'expliquer les traitements 
    et ont répondu à toutes mes questions.
    
    Seul bémol: l'attente aux urgences était un peu longue (3h) et les repas 
    auraient pu être un peu plus variés. Mais globalement, je recommande cet 
    établissement pour la qualité des soins.
    """
    
    questionnaire = {
        'medecins': 4,
        'personnel': 5,
        'accueil': 3,
        'prise_en_charge': 4,
        'confort': 3
    }
    
    try:
        print("📤 Envoi de l'évaluation...")
        start_time = time.time()
        
        result = client.evaluer_avis_complet(
            type_evaluation='etablissement',
            avis_text=avis_text,
            questionnaire_etablissement=questionnaire
        )
        
        duration = time.time() - start_time
        
        print("✅ Évaluation terminée!")
        print(f"⏱️  Durée: {duration:.1f}s")
        print()
        
        # Affichage des résultats
        print("📊 RÉSULTATS:")
        print(f"Note finale: {result['note_finale']}/5")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Confiance: {result['confiance']:.0%}")
        print(f"Intensité émotionnelle: {result['intensite_emotionnelle']:.0%}")
        
        if result.get('titre_suggere'):
            print(f"Titre suggéré: \"{result['titre_suggere']}\"")
        
        if result.get('mode_degrade'):
            print("⚠️  Mode dégradé activé (IA limitée)")
        
        print()
        
        # Analyse détaillée si disponible
        if result.get('analyse_detaillee'):
            analyse = result['analyse_detaillee']
            print("🔍 ANALYSE DÉTAILLÉE:")
            
            if 'questionnaire' in analyse:
                q = analyse['questionnaire']
                print(f"Note questionnaire: {q['note']}/5")
                print(f"Détails: {q['details']}")
            
            if 'sentiment' in analyse:
                s = analyse['sentiment']
                print(f"Sentiment IA: {s.get('sentiment', 'N/A')}")
                print(f"Confiance IA: {s.get('confidence', 0):.0%}")
                
                if s.get('positive_indicators'):
                    print(f"Indicateurs positifs: {s['positive_indicators'][:3]}")
                
                if s.get('negative_indicators'):
                    print(f"Indicateurs négatifs: {s['negative_indicators'][:3]}")
        
        return result
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return None


def exemple_medecin():
    """Exemple d'évaluation d'un médecin"""
    print("\n👨‍⚕️ EXEMPLE: Évaluation Médecin")
    print("=" * 50)
    
    client = HospitalideeIA()
    
    avis_text = """
    Dr Martin est un médecin exceptionnel. Dès notre première rencontre, j'ai 
    été impressionné par sa capacité d'écoute et sa bienveillance. Il prend 
    vraiment le temps d'expliquer les traitements de façon claire et 
    compréhensible.
    
    Je me sens en totale confiance avec lui. Ses prescriptions sont toujours 
    très motivées et il respecte complètement mes choix et mes contraintes. 
    Je le recommande vivement !
    """
    
    questionnaire = {
        'explications': 'Excellentes',
        'confiance': 'Confiance totale',
        'motivation': 'Très motivé',
        'respect': 'Très respectueux'
    }
    
    try:
        print("📤 Envoi de l'évaluation...")
        
        result = client.evaluer_avis_complet(
            type_evaluation='medecin',
            avis_text=avis_text,
            questionnaire_medecin=questionnaire
        )
        
        print("✅ Évaluation terminée!")
        print()
        
        print("📊 RÉSULTATS:")
        print(f"Note finale: {result['note_finale']}/5")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Confiance: {result['confiance']:.0%}")
        
        if result.get('titre_suggere'):
            print(f"Titre suggéré: \"{result['titre_suggere']}\"")
        
        return result
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return None


def exemple_sentiment_seul():
    """Exemple d'analyse de sentiment uniquement"""
    print("\n😊 EXEMPLE: Analyse Sentiment Seule")
    print("=" * 50)
    
    client = HospitalideeIA()
    
    texts = [
        "Personnel très gentil et professionnel",
        "Attente beaucoup trop longue, très décevant",
        "Correct dans l'ensemble, sans plus",
        "Absolument parfait, je recommande vivement !"
    ]
    
    for i, text in enumerate(texts, 1):
        try:
            print(f"📝 Texte {i}: \"{text}\"")
            
            result = client.analyser_sentiment_seul(text)
            
            if result['status'] == 'success':
                data = result['data']
                sentiment = data.get('sentiment', 'inconnu')
                confidence = data.get('confidence', 0)
                
                sentiment_emoji = {
                    'positif': '😊',
                    'negatif': '😞', 
                    'neutre': '😐'
                }.get(sentiment, '❓')
                
                print(f"   → {sentiment_emoji} {sentiment} (confiance: {confidence:.0%})")
            else:
                print(f"   → ❌ Erreur: {result.get('message', 'Inconnue')}")
            
            print()
            
        except Exception as e:
            print(f"   → ❌ Erreur: {str(e)}")
            print()


def test_connexion():
    """Teste la connexion à l'API"""
    print("🔍 TEST DE CONNEXION")
    print("=" * 50)
    
    client = HospitalideeIA()
    
    try:
        health = client.verifier_sante()
        
        if health.get('status') == 'healthy':
            print("✅ API accessible et fonctionnelle")
            print(f"   Modèle Mistral: {health.get('config', {}).get('modele_mistral', 'N/A')}")
            print(f"   Version: {health.get('config', {}).get('version', 'N/A')}")
            
            services = health.get('services', {})
            for service, status in services.items():
                status_emoji = '✅' if status == 'ok' else '❌'
                print(f"   {service}: {status_emoji} {status}")
            
            return True
        else:
            print("⚠️  API accessible mais en mode dégradé")
            print(f"   Status: {health.get('status', 'inconnu')}")
            return False
            
    except Exception as e:
        print(f"❌ API non accessible: {str(e)}")
        print()
        print("🔧 Vérifications:")
        print("   • L'API est-elle démarrée ?")
        print("   • Le port 8000 est-il ouvert ?")
        print("   • URL correcte ? (défaut: http://localhost:8000)")
        return False


def main():
    """Fonction principale - exécute tous les exemples"""
    print("🏥 Hospitalidée IA API - Exemples Python")
    print("=" * 60)
    print()
    print("💡 Pour VPS, changez API_URL dans la classe HospitalideeIA:")
    print("   http://localhost:8000          → 💻 Tests en local")
    print("   http://VOTRE_IP_VPS:8000       → 🌐 VPS production")
    print("   https://api.votre-site.com     → 🔒 VPS avec domaine SSL")
    print()
    
    # Test de connexion
    if not test_connexion():
        print("\n❌ Impossible de continuer sans connexion API")
        return
    
    print("\n" + "=" * 60)
    
    # Exemples d'utilisation
    try:
        # Évaluation établissement
        result_etab = exemple_etablissement()
        
        # Évaluation médecin
        result_med = exemple_medecin()
        
        # Analyse sentiment seule
        exemple_sentiment_seul()
        
        print("=" * 60)
        print("🎉 Tous les exemples ont été exécutés avec succès !")
        print()
        print("💡 Intégration dans votre code:")
        print("   1. Installez: pip install requests")
        print("   2. Copiez la classe HospitalideeIA")
        print("   3. Utilisez client.evaluer_avis_complet()")
        print()
        print("📖 Documentation complète: http://localhost:8000/docs")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Arrêt par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur générale: {str(e)}")


if __name__ == "__main__":
    main()