"""
Interface Streamlit pour le Besoin #1 : Génération Automatique de Notes
Implémentation selon les Cursor rules d'Hospitalidée avec les 5 écrans requis
"""

# Configuration automatique du PYTHONPATH pour les imports
import os
import sys

# Ajouter le répertoire parent (hospitalidee_notation) au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from typing import Dict, Any

# Imports des modules selon les Cursor rules
import importlib
import sys

# Force refresh du module rating_calculator pour éviter les problèmes de cache
if 'src.rating_calculator' in sys.modules:
    importlib.reload(sys.modules['src.rating_calculator'])

from src.sentiment_analyzer import analyze_sentiment
from src.rating_calculator import calculate_rating_from_text
from src.mistral_client import MistralClient
from config.settings import settings


def init_streamlit_config():
    """Configuration initiale de Streamlit selon les Cursor rules"""
    st.set_page_config(
        page_title="Hospitalidée - Génération Automatique de Notes",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Styles personnalisés Hospitalidée
    st.markdown(f"""
    <style>
        .main {{
            padding-top: 1rem;
        }}
        .stButton > button {{
            background-color: {settings.streamlit_theme_primary_color};
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
        }}
        .metric-card {{
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
        }}
        .sentiment-positive {{
            color: #28a745;
            font-weight: bold;
        }}
        .sentiment-negative {{
            color: #dc3545;
            font-weight: bold;
        }}
        .sentiment-neutral {{
            color: #6c757d;
            font-weight: bold;
        }}
    </style>
    """, unsafe_allow_html=True)


def init_session_state():
    """Initialise les variables de session selon les Cursor rules"""
    # Sélection du type d'évaluation
    if 'evaluation_type' not in st.session_state:
        st.session_state.evaluation_type = None
    
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0  # Commencer à 0 pour la sélection
    
    if 'avis_text' not in st.session_state:
        st.session_state.avis_text = ""
    
    if 'sentiment_analysis' not in st.session_state:
        st.session_state.sentiment_analysis = None
    
    if 'rating_calculation' not in st.session_state:
        st.session_state.rating_calculation = None
    
    if 'final_rating' not in st.session_state:
        st.session_state.final_rating = None
    
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    
    # Variables pour les questions fermées - établissement
    if 'note_etablissement' not in st.session_state:
        st.session_state.note_etablissement = None
    
    # Variables pour les questions fermées - médecins
    if 'note_medecins' not in st.session_state:
        st.session_state.note_medecins = None
    
    # Note du questionnaire (selon le type d'évaluation)
    if 'note_questions_fermees' not in st.session_state:
        st.session_state.note_questions_fermees = None
    
    if 'composite_calculation' not in st.session_state:
        st.session_state.composite_calculation = None
    
    if 'adjustment_reason' not in st.session_state:
        st.session_state.adjustment_reason = ""


def render_sidebar():
    """Interface latérale avec navigation selon les Cursor rules"""
    st.sidebar.markdown("## 🏥 Hospitalidée")
    st.sidebar.markdown("### Génération Automatique de Notes")
    
    # Affichage du type d'évaluation sélectionné
    if st.session_state.evaluation_type:
        eval_icon = "🏥" if st.session_state.evaluation_type == "etablissement" else "👨‍⚕️"
        eval_name = "Établissement" if st.session_state.evaluation_type == "etablissement" else "Médecin"
        st.sidebar.markdown(f"**{eval_icon} Évaluation : {eval_name}**")
    
    st.sidebar.markdown("---")
    
    # Indicateur de progression - nouveau workflow séparé
    steps = ["Questionnaire", "Saisie", "Note IA", "Analyse hybride", "Résultat"]
    
    if st.session_state.evaluation_type:
        current = st.session_state.current_step
        
        for i, step in enumerate(steps, 1):
            if i < current:
                st.sidebar.markdown(f"✅ **{i}. {step}**")
            elif i == current:
                st.sidebar.markdown(f"🔄 **{i}. {step}**")
            else:
                st.sidebar.markdown(f"⏸️ {i}. {step}")
        
        # Affichage du type d'évaluation dans la sidebar
        eval_icon = "🏥" if st.session_state.evaluation_type == "etablissement" else "👨‍⚕️"
        eval_name = "Établissement" if st.session_state.evaluation_type == "etablissement" else "Médecin"
        st.sidebar.markdown(f"**Type d'évaluation :** {eval_icon} {eval_name}")
        
        # Bouton de reset
        if st.sidebar.button("🔄 Recommencer"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()
    
    st.sidebar.markdown("---")
    
    # Informations techniques
    if st.session_state.sentiment_analysis:
        st.sidebar.markdown("### 📊 Analyse Rapide")
        sentiment = st.session_state.sentiment_analysis.get('sentiment', 'neutre')
        confidence = st.session_state.sentiment_analysis.get('confidence', 0.0)
        
        sentiment_color = {
            'positif': '🟢',
            'negatif': '🔴', 
            'neutre': '🟡'
        }.get(sentiment, '🟡')
        
        st.sidebar.metric(
            label="Sentiment détecté",
            value=f"{sentiment_color} {sentiment.title()}",
            delta=f"Confiance: {confidence:.1%}"
        )


def step_0_selection_type():
    """Écran 0: Sélection du type d'évaluation (Établissement ou Médecin)"""
    st.header("🎯 Sélection du type d'évaluation")
    
    st.markdown("""
    **Bienvenue dans l'outil d'évaluation Hospitalidée !**
    
    Pour commencer votre évaluation, veuillez sélectionner le type d'évaluation que vous souhaitez effectuer.
    Chaque type propose un questionnaire et une analyse spécialisée.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            "🏥 Évaluer un Établissement",
            help="Évaluez votre expérience dans un établissement de santé (hôpital, clinique...)",
            use_container_width=True,
            type="secondary"
        ):
            st.session_state.evaluation_type = "etablissement"
            st.session_state.current_step = 1
            st.rerun()
        
        st.markdown("""
        **Évaluation Établissement :**
        - Relation avec les médecins
        - Relation avec le personnel
        - Accueil et prise en charge
        - Confort (chambres, repas)
        - Analyse globale de l'établissement
        """)
    
    with col2:
        if st.button(
            "👨‍⚕️ Évaluer un Médecin",
            help="Évaluez spécifiquement votre relation avec un médecin",
            use_container_width=True,
            type="secondary"
        ):
            st.session_state.evaluation_type = "medecin"
            st.session_state.current_step = 1
            st.rerun()
        
        st.markdown("""
        **Évaluation Médecin :**
        - Qualité des explications
        - Sentiment de confiance
        - Motivation prescription
        - Respect de votre identité
        - Analyse centrée sur la relation médecin-patient
        """)
    
    st.markdown("---")
    st.info("💡 **Astuce :** Vous pourrez toujours revenir à cette sélection en utilisant le bouton 'Nouvelle analyse' à la fin du processus.")


def step_1_questionnaire():
    """Écran 1: Questionnaire avec questions fermées selon nouveau workflow séparé"""
    if not st.session_state.evaluation_type:
        st.error("Type d'évaluation non sélectionné. Retournez à la sélection.")
        return
    
    # Titre selon le type d'évaluation
    eval_icon = "🏥" if st.session_state.evaluation_type == "etablissement" else "👨‍⚕️"
    eval_name = "Établissement" if st.session_state.evaluation_type == "etablissement" else "Médecin"
    
    st.header(f"📋 Étape 1 : Questionnaire d'évaluation {eval_icon}")
    
    st.markdown(f"""
    **Évaluez votre expérience {eval_name.lower()}** en répondant aux questions suivantes. 
    Cette évaluation nous permettra de mieux comprendre votre ressenti lors de l'analyse de votre avis textuel.
    """)
    
    if st.session_state.evaluation_type == "etablissement":
        # Workflow Établissement uniquement
        st.markdown("### 🏥 **Évaluation de l'Établissement**")
        st.markdown("*Donnez une note sur 5 pour chaque aspect de votre expérience dans l'établissement :*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            etab_medecins = st.slider(
                "Votre relation avec les médecins",
                min_value=1, max_value=5, value=3,
                help="Qualité de la communication et des interactions avec les médecins",
                key="etab_medecins"
            )
            
            etab_personnel = st.slider(
                "Votre relation avec le personnel",
                min_value=1, max_value=5, value=3,
                help="Qualité des interactions avec les infirmières, aides-soignants, etc.",
                key="etab_personnel"
            )
            
            etab_accueil = st.slider(
                "L'accueil",
                min_value=1, max_value=5, value=3,
                help="Qualité de l'accueil à votre arrivée dans l'établissement",
                key="etab_accueil"
            )
        
        with col2:
            etab_prise_charge = st.slider(
                "La prise en charge jusqu'à la sortie",
                min_value=1, max_value=5, value=3,
                help="Qualité du suivi médical du début à la fin de votre séjour",
                key="etab_prise_charge"
            )
            
            etab_confort = st.slider(
                "Les chambres et les repas",
                min_value=1, max_value=5, value=3,
                help="Qualité de l'hébergement et de la restauration",
                key="etab_confort"
            )
        
        # Calcul note établissement
        note_etablissement = (etab_medecins + etab_personnel + etab_accueil + etab_prise_charge + etab_confort) / 5
        st.session_state.note_etablissement = note_etablissement
        st.session_state.note_questions_fermees = note_etablissement  # Pour ce workflow, c'est la note finale
        
        # Résumé établissement
        st.markdown("---")
        st.markdown("### 🎯 Résumé de votre évaluation")
        
        col_summary1, col_summary2 = st.columns(2)
        with col_summary1:
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; border-radius: 10px; margin: 10px 0;'>
                <h2 style='color: white; margin: 0;'>Note Établissement</h2>
                <h1 style='color: #FFD700; margin: 5px 0; font-size: 2.5em;'>{note_etablissement:.1f}/5</h1>
                <p style='margin: 0; color: #E0E0E0;'>⭐ Moyenne des 5 aspects évalués</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_summary2:
            st.markdown("#### 📊 Détail par aspect")
            aspects = {
                "Médecins": etab_medecins,
                "Personnel": etab_personnel, 
                "Accueil": etab_accueil,
                "Prise en charge": etab_prise_charge,
                "Confort": etab_confort
            }
            
            for aspect, score in aspects.items():
                stars = "⭐" * score + "☆" * (5 - score)
                st.markdown(f"**{aspect}**: {score}/5 {stars}")
    
    elif st.session_state.evaluation_type == "medecin":
        # Workflow Médecin uniquement
        st.markdown("### 👨‍⚕️ **Évaluation du Médecin**")
        st.markdown("*Évaluez votre relation avec le médecin sur les aspects suivants :*")
        
        col1, col2 = st.columns(2)
        
        with col1:
            medecin_explications = st.select_slider(
                "Qualité des explications",
                options=["Très insuffisantes", "Insuffisantes", "Correctes", "Bonnes", "Excellentes"],
                value="Correctes",
                key="medecin_explications",
                help="Clarté et qualité des explications données par le médecin"
            )
            
            medecin_confiance = st.select_slider(
                "Sentiment de confiance",
                options=["Aucune confiance", "Peu de confiance", "Confiance modérée", "Bonne confiance", "Confiance totale"],
                value="Confiance modérée",
                key="medecin_confiance",
                help="Niveau de confiance que vous ressentez envers ce médecin"
            )
        
        with col2:
            medecin_motivation = st.select_slider(
                "Motivation à respecter la prescription",
                options=["Aucune motivation", "Peu motivé", "Moyennement motivé", "Bien motivé", "Très motivé"],
                value="Moyennement motivé",
                key="medecin_motivation",
                help="Votre motivation à suivre les conseils et prescriptions du médecin"
            )
            
            medecin_respect = st.select_slider(
                "Respect de votre identité, préférences et besoins",
                options=["Pas du tout", "Peu respectueux", "Modérément respectueux", "Respectueux", "Très respectueux"],
                value="Modérément respectueux",
                key="medecin_respect",
                help="Respect de vos besoins personnels et de votre individualité"
            )
        
        # Calcul note médecins (conversion des choix en notes)
        medecin_scores = {
            medecin_explications: convert_text_to_rating(medecin_explications),
            medecin_confiance: convert_text_to_rating(medecin_confiance),
            medecin_motivation: convert_text_to_rating(medecin_motivation),
            medecin_respect: convert_text_to_rating(medecin_respect)
        }
        
        note_medecins = sum(medecin_scores.values()) / len(medecin_scores)
        st.session_state.note_medecins = note_medecins
        st.session_state.note_questions_fermees = note_medecins  # Pour ce workflow, c'est la note finale
        
        # Résumé médecins
        st.markdown("---")
        st.markdown("### 🎯 Résumé de votre évaluation")
        
        col_summary1, col_summary2 = st.columns(2)
        with col_summary1:
            st.markdown(f"""
            <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin: 10px 0;'>
                <h2 style='color: white; margin: 0;'>Note Médecin</h2>
                <h1 style='color: #FFD700; margin: 5px 0; font-size: 2.5em;'>{note_medecins:.1f}/5</h1>
                <p style='margin: 0; color: #E0E0E0;'>⭐ Moyenne des 4 critères évalués</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_summary2:
            st.markdown("#### 📊 Détail par critère")
            
            for aspect, evaluation in [
                ("Explications", medecin_explications),
                ("Confiance", medecin_confiance), 
                ("Motivation", medecin_motivation),
                ("Respect", medecin_respect)
            ]:
                score = convert_text_to_rating(evaluation)
                stars = "⭐" * int(score) + "☆" * (5 - int(score))
                st.markdown(f"**{aspect}**: {evaluation} ({score:.1f}/5) {stars}")
    
    # Navigation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Changer de type", use_container_width=True):
            st.session_state.current_step = 0
            st.rerun()
    
    with col3:
        if st.button("Continuer vers la saisie d'avis 📝", type="primary", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()


def step_2_saisie_avis():
    """Écran 2: Saisie d'avis avec analyse en temps réel selon nouveau workflow séparé"""
    if not st.session_state.evaluation_type:
        st.error("Type d'évaluation non sélectionné. Retournez à la sélection.")
        return
    
    # Titre selon le type d'évaluation
    eval_icon = "🏥" if st.session_state.evaluation_type == "etablissement" else "👨‍⚕️"
    eval_name = "Établissement" if st.session_state.evaluation_type == "etablissement" else "Médecin"
    
    st.header(f"📝 Étape 2 : Saisie de votre avis {eval_icon}")
    
    # Affichage du résumé questionnaire selon le type
    if st.session_state.get('note_questions_fermees'):
        st.info(f"✅ Questionnaire {eval_name} complété - Note: {st.session_state.note_questions_fermees:.1f}/5")
    else:
        st.warning(f"⚠️ Questionnaire {eval_name} non complété. Retournez à l'étape 1.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Message personnalisé selon le type d'évaluation
        if st.session_state.evaluation_type == "etablissement":
            st.markdown("""
            **Partagez votre expérience** dans l'établissement de santé. 
            Plus votre avis sera détaillé, plus notre analyse sera précise et cohérente avec votre évaluation.
            """)
            
            placeholder_text = "Décrivez votre expérience dans l'établissement : accueil, soins reçus, personnel, confort, locaux..."
            help_text = "Partagez tous les aspects de votre séjour dans l'établissement qui vous semblent importants"
        else:
            st.markdown("""
            **Partagez votre expérience** avec le médecin. 
            Plus votre avis sera détaillé, plus notre analyse sera précise et cohérente avec votre évaluation.
            """)
            
            placeholder_text = "Décrivez votre relation avec le médecin : communication, écoute, explications, traitement..."
            help_text = "Partagez tous les aspects de votre relation avec le médecin qui vous semblent importants"
        
        # Zone de texte principale avec callback selon Cursor rules
        avis_text = st.text_area(
            label="Votre avis complet",
            value=st.session_state.avis_text,
            height=200,
            placeholder=placeholder_text,
            help=help_text
        )
        
        # Mise à jour en temps réel
        if avis_text != st.session_state.avis_text:
            st.session_state.avis_text = avis_text
            # Déclencher une nouvelle analyse si le texte a suffisamment changé
            if len(avis_text.strip()) > 10:
                st.rerun()
    
    with col2:
        # Indicateurs en temps réel selon Cursor rules
        if avis_text and len(avis_text.strip()) > 10:
            with st.spinner("Analyse en cours..."):
                try:
                    # Analyse sentiment en temps réel
                    sentiment_result = analyze_sentiment(avis_text)
                    st.session_state.sentiment_analysis = sentiment_result
                    
                    # Affichage des métriques
                    sentiment = sentiment_result.get('sentiment', 'neutre')
                    confidence = sentiment_result.get('confidence', 0.0)
                    intensity = sentiment_result.get('emotional_intensity', 0.5)
                    
                    st.markdown("### 🎯 Analyse instantanée")
                    
                    # Sentiment avec couleur
                    sentiment_display = {
                        'positif': ('🟢 Positif', 'sentiment-positive'),
                        'negatif': ('🔴 Négatif', 'sentiment-negative'),
                        'neutre': ('🟡 Neutre', 'sentiment-neutral')
                    }.get(sentiment, ('🟡 Neutre', 'sentiment-neutral'))
                    
                    st.markdown(f'<div class="{sentiment_display[1]}">{sentiment_display[0]}</div>', 
                              unsafe_allow_html=True)
                    
                    # Métriques visuelles selon Cursor rules
                    st.metric("Confiance", f"{confidence:.1%}")
                    st.metric("Intensité émotionnelle", f"{intensity:.1%}")
                    
                    # Indicateurs détaillés
                    word_count = len(avis_text.split())
                    st.metric("Mots analysés", word_count)
                    
                    # Cohérence avec questionnaire
                    if st.session_state.get('note_questions_fermees'):
                        questionnaire_note = st.session_state.note_questions_fermees
                        # Estimation sentiment vs questionnaire
                        sentiment_score = {'negatif': 2.0, 'neutre': 3.0, 'positif': 4.0}.get(sentiment, 3.0)
                        coherence = 1 - abs(sentiment_score - questionnaire_note) / 5
                        
                        st.markdown("#### 🔗 Cohérence")
                        st.metric("Avec questionnaire", f"{coherence:.0%}")
                    
                except Exception as e:
                    error_msg = str(e)
                    if "Timeout" in error_msg:
                        st.error("⏱️ L'API Mistral prend plus de temps que prévu. Veuillez réessayer dans quelques instants.")
                        st.info("💡 **Conseil :** L'API peut être temporairement surchargée. Le système fonctionne en mode dégradé.")
                    elif "rate limit" in error_msg.lower():
                        st.error("🚦 Limite de requêtes atteinte. Veuillez attendre quelques minutes avant de réessayer.")
                    elif "clé API" in error_msg.lower() or "401" in error_msg:
                        st.error("🔑 Problème de configuration API. Contactez l'administrateur.")
                    else:
                        st.error(f"❌ Erreur d'analyse : {error_msg}")
                        st.info("🔄 Le système continue de fonctionner avec des analyses simplifiées.")
        
        else:
            st.info("Commencez à écrire votre avis pour voir l'analyse en temps réel")
    
    # Navigation selon Cursor rules
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Retour questionnaire", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
    
    with col3:
        if st.button("Calculer la note IA →", type="primary", use_container_width=True):
            if len(avis_text.strip()) > 20:  # Validation minimum
                st.session_state.current_step = 3
                st.rerun()
            else:
                st.error("Veuillez écrire un avis plus détaillé (minimum 20 caractères)")


def step_3_note_ia():
    """Écran 3: Note suggérée par l'IA en tenant compte du questionnaire selon nouveau workflow séparé"""
    if not st.session_state.evaluation_type:
        st.error("Type d'évaluation non sélectionné. Retournez à la sélection.")
        return
    
    # Titre selon le type d'évaluation
    eval_icon = "🏥" if st.session_state.evaluation_type == "etablissement" else "👨‍⚕️"
    eval_name = "Établissement" if st.session_state.evaluation_type == "etablissement" else "Médecin"
    
    st.header(f"⭐ Étape 3 : Note suggérée par l'IA {eval_icon}")
    
    if not st.session_state.sentiment_analysis:
        st.error("Analyse de sentiment manquante. Retournez à l'étape 2.")
        return
    
    if not st.session_state.get('note_questions_fermees'):
        st.error(f"Questionnaire {eval_name} non complété. Retournez à l'étape 1.")
        return
    
    # Calcul de la note IA hybride si pas déjà fait
    if not st.session_state.rating_calculation:
        with st.spinner("Calcul de la note IA hybride en cours..."):
            try:
                # Calcul avec prise en compte du questionnaire
                rating_result = calculate_rating_from_text(
                    st.session_state.avis_text, 
                    st.session_state.sentiment_analysis,
                    st.session_state.note_questions_fermees  # Paramètre positionnel
                )
                st.session_state.rating_calculation = rating_result
            except Exception as e:
                error_msg = str(e)
                if "Timeout" in error_msg:
                    st.error("⏱️ L'IA prend plus de temps que prévu pour calculer la note.")
                    st.info("💡 **Le système continue avec une note basée sur l'analyse de sentiment local.**")
                    # Calcul de fallback en mode dégradé
                    sentiment = st.session_state.sentiment_analysis.get('sentiment', 'neutre')
                    fallback_ratings = {'positif': 4.0, 'neutre': 3.0, 'negatif': 2.0}
                    fallback_rating = fallback_ratings.get(sentiment, 3.0)
                    
                    st.session_state.rating_calculation = {
                        'suggested_rating': fallback_rating,
                        'confidence': 0.5,
                        'justification': f"Note basée sur le sentiment {sentiment} (mode dégradé)",
                        'factors': {'sentiment_weight': 1.0},
                        'fallback_mode': True
                    }
                elif "rate limit" in error_msg.lower():
                    st.error("🚦 L'API est temporairement surchargée. Veuillez réessayer dans quelques minutes.")
                    return
                else:
                    st.error(f"❌ Erreur lors du calcul : {error_msg}")
                    st.info("🔄 Utilisez le mode dégradé ou réessayez plus tard.")
                return
    
    rating_data = st.session_state.rating_calculation
    suggested_rating = rating_data.get('suggested_rating', 3.0)
    confidence = rating_data.get('confidence', 0.0)
    justification = rating_data.get('justification', "Calcul automatique")
    
    # Affichage de la note suggérée selon Cursor rules
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"### 🎯 Note suggérée par l'IA hybride - {eval_name}")
        
        # Affichage visuel de la note - amélioration visibilité selon demande utilisateur
        rating_display = "⭐" * int(suggested_rating) + "☆" * (5 - int(suggested_rating))
        gradient_color = "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)" if st.session_state.evaluation_type == "etablissement" else "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        
        st.markdown(f"""
        <div style='text-align: center; padding: 30px; background: {gradient_color}; color: white; border-radius: 15px; margin: 15px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
            <h1 style='color: white; margin: 0; font-size: 3em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>{suggested_rating}/5</h1>
            <h2 style='margin: 10px 0; color: #FFD700; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);'>{rating_display}</h2>
            <p style='margin: 0; font-style: italic; color: #E0E0E0; font-size: 1.1em;'>Confiance: {confidence:.1%}</p>
            <p style='margin: 5px 0; color: #F0F0F0; font-size: 0.9em;'>🔗 Analyse hybride {eval_name} (Questionnaire + Avis textuel)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Justification détaillée
        st.markdown("#### 💭 Justification de l'IA")
        st.info(justification)
        
        # Comparaison avec le questionnaire
        questionnaire_note = st.session_state.note_questions_fermees
        difference = suggested_rating - questionnaire_note
        
        st.markdown(f"#### 🔗 Cohérence avec le questionnaire {eval_name}")
        col_coh1, col_coh2, col_coh3 = st.columns(3)
        with col_coh1:
            st.metric(f"Note questionnaire {eval_name}", f"{questionnaire_note:.1f}/5")
        with col_coh2:
            st.metric("Note IA hybride", f"{suggested_rating:.1f}/5")
        with col_coh3:
            st.metric("Écart", f"{difference:+.1f}", 
                     delta_color="normal" if abs(difference) < 1 else "inverse")
        
        # Facteurs de calcul selon Cursor rules
        factors = rating_data.get('factors', {})
        if factors:
            st.markdown("#### ⚖️ Facteurs pris en compte")
            factors_df = pd.DataFrame([
                {"Facteur": "Questionnaire fermé", "Poids": f"{factors.get('questionnaire_weight', 0.4):.1%}"},
                {"Facteur": "Sentiment textuel", "Poids": f"{factors.get('sentiment_weight', 0.3):.1%}"},
                {"Facteur": "Intensité émotionnelle", "Poids": f"{factors.get('intensity_weight', 0.2):.1%}"},
                {"Facteur": "Richesse du contenu", "Poids": f"{factors.get('content_weight', 0.1):.1%}"}
            ])
            st.dataframe(factors_df, hide_index=True)
    
    with col2:
        st.markdown("### 📊 Analyse comparative")
        
        # Graphique comparatif selon Cursor rules
        fig_rating = create_rating_breakdown_chart(rating_data)
        st.plotly_chart(fig_rating, use_container_width=True)
        
        # Section "Note calcul local" supprimée selon demande utilisateur
    
    # Navigation selon Cursor rules
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Retour saisie avis", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()
    
    with col3:
        if st.button("Voir analyse hybride →", type="primary", use_container_width=True):
            st.session_state.current_step = 4
            st.rerun()


def step_4_analyse_hybride():
    """Écran 4: Analyse complète hybride selon nouveau workflow séparé"""
    if not st.session_state.evaluation_type:
        st.error("Type d'évaluation non sélectionné. Retournez à la sélection.")
        return
    
    # Titre selon le type d'évaluation
    eval_icon = "🏥" if st.session_state.evaluation_type == "etablissement" else "👨‍⚕️"
    eval_name = "Établissement" if st.session_state.evaluation_type == "etablissement" else "Médecin"
    
    st.header(f"🔍 Étape 4 : Analyse complète hybride {eval_icon}")
    
    if not st.session_state.rating_calculation:
        st.error("Calcul de note IA manquant. Retournez à l'étape 3.")
        return
    
    if not st.session_state.sentiment_analysis:
        st.error("Analyse de sentiment manquante. Retournez à l'étape 2.")
        return
    
    if not st.session_state.get('note_questions_fermees'):
        st.error(f"Questionnaire {eval_name} non complété. Retournez à l'étape 1.")
        return
    
    # Données pour l'analyse hybride
    sentiment_data = st.session_state.sentiment_analysis
    rating_data = st.session_state.rating_calculation
    suggested_rating = rating_data.get('suggested_rating', 3.0)
    questionnaire_note = st.session_state.note_questions_fermees
    
    st.markdown(f"""
    Cette analyse combine les résultats du **questionnaire {eval_name.lower()} structuré** et de l'**analyse textuelle** 
    pour offrir une vue complète de votre expérience.
    """)
    
    # Vue d'ensemble hybride
    st.markdown(f"### 📊 Vue d'ensemble hybride - {eval_name}")
    
    col_overview1, col_overview2, col_overview3, col_overview4 = st.columns(4)
    with col_overview1:
        st.metric(f"Note Questionnaire {eval_name}", f"{questionnaire_note:.1f}/5", help="Basée sur vos réponses structurées")
    with col_overview2:
        sentiment = sentiment_data.get('sentiment', 'neutre')
        st.metric("Sentiment Textuel", sentiment.title(), help="Détecté dans votre avis")
    with col_overview3:
        st.metric("Note IA Hybride", f"{suggested_rating:.1f}/5", help="Combinaison intelligente des deux approches")
    with col_overview4:
        confidence = sentiment_data.get('confidence', 0.0)
        st.metric("Confiance Globale", f"{confidence:.1%}", help="Fiabilité de l'analyse")
    
    # Analyse détaillée en colonnes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### 📋 Analyse du questionnaire {eval_name}")
        
        if st.session_state.evaluation_type == "etablissement":
            # Détail établissement uniquement
            if st.session_state.get('note_etablissement'):
                etab_note = st.session_state.note_etablissement
                st.markdown(f"**🏥 Établissement : {etab_note:.1f}/5**")
        
                # Sous-scores établissement
                scores = {
                    "Médecins": st.session_state.get('etab_medecins', 3),
                    "Personnel": st.session_state.get('etab_personnel', 3),
                    "Accueil": st.session_state.get('etab_accueil', 3),
                    "Prise en charge": st.session_state.get('etab_prise_charge', 3),
                    "Confort": st.session_state.get('etab_confort', 3)
                }
                
                for aspect, score in scores.items():
                    progress = score / 5
                    st.progress(progress, text=f"{aspect}: {score}/5")
        
        elif st.session_state.evaluation_type == "medecin":
            # Détail médecins uniquement
            if st.session_state.get('note_medecins'):
                med_note = st.session_state.note_medecins
                st.markdown(f"**👨‍⚕️ Médecin : {med_note:.1f}/5**")
                
                evaluations = {
                    "Explications": st.session_state.get('medecin_explications', 'Correctes'),
                    "Confiance": st.session_state.get('medecin_confiance', 'Confiance modérée'),
                    "Motivation": st.session_state.get('medecin_motivation', 'Moyennement motivé'),
                    "Respect": st.session_state.get('medecin_respect', 'Modérément respectueux')
                }
                
                for aspect, evaluation in evaluations.items():
                    score = convert_text_to_rating(evaluation)
                    progress = score / 5
                    st.progress(progress, text=f"{aspect}: {evaluation} ({score:.1f}/5)")
    
    with col2:
        st.markdown("### 📝 Analyse textuelle")
        
        # Métriques sentiment
        sentiment = sentiment_data.get('sentiment', 'neutre')
        confidence = sentiment_data.get('confidence', 0.0)
        intensity = sentiment_data.get('emotional_intensity', 0.5)
        
        sentiment_color = {
            'positif': '🟢',
            'negatif': '🔴',
            'neutre': '🟡'
        }.get(sentiment, '🟡')
        
        st.markdown(f"**{sentiment_color} Sentiment global : {sentiment.title()}**")
        st.progress(confidence, text=f"Confiance: {confidence:.1%}")
        st.progress(intensity, text=f"Intensité émotionnelle: {intensity:.1%}")
        
        # Indicateurs positifs et négatifs
        st.markdown("**🟢 Aspects positifs détectés**")
        positive_indicators = sentiment_data.get('positive_indicators', [])
        if positive_indicators:
            for indicator in positive_indicators[:3]:
                st.markdown(f"• {indicator}")
        else:
            st.info("Aucun aspect positif spécifique détecté")
        
        st.markdown("**🔴 Aspects négatifs détectés**")
        negative_indicators = sentiment_data.get('negative_indicators', [])
        if negative_indicators:
            for indicator in negative_indicators[:3]:
                st.markdown(f"• {indicator}")
        else:
            st.info("Aucun aspect négatif spécifique détecté")
    
    # Synthèse hybride
    st.markdown("---")
    st.markdown("### 🎯 Synthèse hybride")
    
    difference = suggested_rating - questionnaire_note
    coherence_percent = max(0, 1 - abs(difference) / 5) * 100
    
    col_synth1, col_synth2 = st.columns(2)
    
    with col_synth1:
        st.markdown("#### 🔗 Cohérence des approches")
        st.progress(coherence_percent / 100, text=f"Cohérence: {coherence_percent:.0f}%")
        
        if abs(difference) < 0.5:
            st.success("✅ Excellente cohérence entre questionnaire et analyse textuelle")
        elif abs(difference) < 1.0:
            st.info("ℹ️ Bonne cohérence avec quelques nuances")
        else:
            st.warning("⚠️ Écart significatif détecté - analyse approfondie requise")
    
    with col_synth2:
        st.markdown("#### 📈 Répartition des sources")
        factors = rating_data.get('factors', {})
        
        # Graphique simple de répartition
        sources = ['Questionnaire', 'Sentiment', 'Intensité', 'Contenu']
        weights = [
            factors.get('questionnaire_weight', 0.4) * 100,
            factors.get('sentiment_weight', 0.3) * 100,
            factors.get('intensity_weight', 0.2) * 100,
            factors.get('content_weight', 0.1) * 100
        ]
        
        for source, weight in zip(sources, weights):
            st.progress(weight / 100, text=f"{source}: {weight:.0f}%")
    
    # Navigation selon Cursor rules
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Retour note IA", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()
    
    with col3:
        if st.button("Finaliser l'avis ✨", type="primary", use_container_width=True):
            # Calculer la note finale (déjà calculée dans l'IA hybride)
            st.session_state.final_rating = suggested_rating
            st.session_state.analysis_complete = True
            st.session_state.current_step = 5
            st.rerun()








def convert_text_to_rating(text_choice: str) -> float:
    """Convertit les choix textuels en notes numériques selon les Cursor rules"""
    mapping = {
        # Pour explications, confiance, motivation, respect
        "Très insuffisantes": 1.0, "Aucune confiance": 1.0, "Aucune motivation": 1.0, "Pas du tout": 1.0,
        "Insuffisantes": 2.0, "Peu de confiance": 2.0, "Peu motivé": 2.0, "Peu respectueux": 2.0,
        "Correctes": 3.0, "Confiance modérée": 3.0, "Moyennement motivé": 3.0, "Modérément respectueux": 3.0,
        "Bonnes": 4.0, "Bonne confiance": 4.0, "Bien motivé": 4.0, "Respectueux": 4.0,
        "Excellentes": 5.0, "Confiance totale": 5.0, "Très motivé": 5.0, "Très respectueux": 5.0
    }
    return mapping.get(text_choice, 3.0)








def step_5_resultat_final():
    """Écran 5: Résultat final avec export selon les Cursor rules - workflow séparé"""
    if not st.session_state.evaluation_type:
        st.error("Type d'évaluation non sélectionné. Retournez à la sélection.")
        return
    
    # Titre selon le type d'évaluation
    eval_icon = "🏥" if st.session_state.evaluation_type == "etablissement" else "👨‍⚕️"
    eval_name = "Établissement" if st.session_state.evaluation_type == "etablissement" else "Médecin"
    
    st.header(f"🎉 Étape 5 : Avis {eval_name} finalisé {eval_icon}")
    
    if not st.session_state.analysis_complete:
        st.error("Processus non terminé")
        return
    
    # Résultat final selon Cursor rules
    st.success(f"🎊 Félicitations ! Votre avis {eval_name.lower()} a été analysé et finalisé avec succès.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 Votre avis finalisé")
        
        # Carte récapitulative avec détails de la note composite
        final_rating = st.session_state.final_rating
        rating_stars = "⭐" * int(final_rating) + "☆" * (5 - int(final_rating))
        
        st.markdown(f"""
        <div style='padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin: 15px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
            <h2 style='margin-top: 0; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>Note finale hybride: {final_rating:.1f}/5 {rating_stars}</h2>
            <p style='color: #E0E0E0; font-size: 1.1em;'><strong>Sentiment:</strong> {st.session_state.sentiment_analysis.get('sentiment', '').title()}</p>
            <p style='color: #E0E0E0; font-size: 1.1em;'><strong>Méthode:</strong> IA hybride (Questionnaire + Analyse textuelle)</p>
            <p style='color: #E0E0E0; font-size: 1.1em;'><strong>Avis:</strong></p>
            <em style='color: #F0F0F0; font-size: 1.05em;'>"{st.session_state.avis_text}"</em>
        </div>
        """, unsafe_allow_html=True)
        
        # Détail de la composition hybride
        if st.session_state.get('rating_calculation'):
            st.markdown("#### 🔍 Détail de la composition hybride")
            rating_data = st.session_state.rating_calculation
            questionnaire_note = st.session_state.get('note_questions_fermees', 0)
            
            col_comp1, col_comp2, col_comp3 = st.columns(3)
            with col_comp1:
                st.metric("Note Questionnaire", f"{questionnaire_note:.1f}/5", help="Évaluation structurée")
            with col_comp2:
                sentiment = st.session_state.sentiment_analysis.get('sentiment', 'neutre')
                sentiment_score = {'negatif': 2.0, 'neutre': 3.0, 'positif': 4.0}.get(sentiment, 3.0)
                st.metric("Sentiment Textuel", f"{sentiment_score:.1f}/5", help="Analyse du texte")
            with col_comp3:
                st.metric("Note IA Hybride", f"{final_rating:.1f}/5", help="Synthèse intelligente")
        
        # Détail des évaluations par questions fermées
        if 'note_etablissement' in st.session_state and 'note_medecins' in st.session_state:
            st.markdown("#### 📋 Détail des évaluations spécifiques")
            
            with st.expander("🏥 Évaluation Établissement"):
                etab_note = st.session_state.note_etablissement
                if etab_note is not None:
                    st.markdown(f"**Note globale établissement : {etab_note:.1f}/5**")
                    
                    # Récupérer les notes individuelles depuis la session
                    scores = {
                        "Relation médecins": st.session_state.get('etab_medecins', 3),
                        "Relation personnel": st.session_state.get('etab_personnel', 3),
                        "Accueil": st.session_state.get('etab_accueil', 3),
                        "Prise en charge": st.session_state.get('etab_prise_charge', 3),
                        "Chambres et repas": st.session_state.get('etab_confort', 3)
                    }
                    
                    for aspect, score in scores.items():
                        stars = "⭐" * score + "☆" * (5 - score)
                        st.markdown(f"• **{aspect}**: {score}/5 {stars}")
                else:
                    st.info("Aucune évaluation établissement détaillée disponible.")
            
            with st.expander("👨‍⚕️ Évaluation Médecins"):
                med_note = st.session_state.note_medecins
                if med_note is not None:
                    st.markdown(f"**Note globale médecins : {med_note:.1f}/5**")
                    
                    # Récupérer les évaluations textuelles depuis la session
                    evaluations = {
                        "Qualité des explications": st.session_state.get('medecin_explications', 'Correctes'),
                        "Sentiment de confiance": st.session_state.get('medecin_confiance', 'Confiance modérée'),
                        "Motivation prescription": st.session_state.get('medecin_motivation', 'Moyennement motivé'),
                        "Respect identité/besoins": st.session_state.get('medecin_respect', 'Modérément respectueux')
                    }
                    
                    for aspect, evaluation in evaluations.items():
                        score = convert_text_to_rating(evaluation)
                        stars = "⭐" * int(score) + "☆" * (5 - int(score))
                        st.markdown(f"• **{aspect}**: {evaluation} ({score:.1f}/5) {stars}")
                else:
                    st.info("Aucune évaluation médecine détaillée disponible.")
        
        # Génération titre suggéré selon Cursor rules
        if st.button("Générer un titre suggéré 📝"):
            with st.spinner("Génération du titre..."):
                try:
                    mistral_client = MistralClient()
                    title_result = mistral_client.generate_title(
                        st.session_state.sentiment_analysis,
                        final_rating,
                        st.session_state.avis_text
                    )
                    
                    suggested_title = title_result.get('suggested_title', 'Avis sur mon séjour')
                    alternatives = title_result.get('alternative_titles', [])
                    
                    st.markdown("#### 📝 Titre suggéré")
                    st.info(f'"{suggested_title}"')
                    
                    if alternatives:
                        st.markdown("**Alternatives:**")
                        for alt in alternatives:
                            st.markdown(f"• {alt}")
                    
                except Exception as e:
                    st.error(f"Erreur génération titre: {e}")
    
    with col2:
        st.markdown("### 📊 Statistiques de l'analyse")
        
        # Métriques finales
        sentiment_data = st.session_state.sentiment_analysis
        rating_data = st.session_state.rating_calculation
        
        metrics_data = [
            {"Métrique": "Sentiment", "Valeur": sentiment_data.get('sentiment', 'N/A').title()},
            {"Métrique": "Confiance IA", "Valeur": f"{sentiment_data.get('confidence', 0):.1%}"},
            {"Métrique": "Note suggérée", "Valeur": f"{rating_data.get('suggested_rating', 0)}/5"},
            {"Métrique": "Note finale", "Valeur": f"{final_rating}/5"},
            {"Métrique": "Mots analysés", "Valeur": str(len(st.session_state.avis_text.split()))},
            {"Métrique": "Thèmes détectés", "Valeur": str(len(sentiment_data.get('key_themes', [])))}
        ]
        
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, hide_index=True)
        
        # Export des résultats selon Cursor rules
        st.markdown("### 💾 Export des résultats")
        
        export_data = {
            "avis_text": st.session_state.avis_text,
            "final_rating": final_rating,
            "sentiment_analysis": sentiment_data,
            "rating_calculation": rating_data,
            "analysis_timestamp": pd.Timestamp.now().isoformat(),
            
            # Données hybrides
            "workflow_type": "hybride_questionnaire_puis_texte",
            "detailed_evaluations": {
                "etablissement": {
                    "note_globale": st.session_state.get('note_etablissement', None),
                    "relation_medecins": st.session_state.get('etab_medecins', None),
                    "relation_personnel": st.session_state.get('etab_personnel', None),
                    "accueil": st.session_state.get('etab_accueil', None),
                    "prise_en_charge": st.session_state.get('etab_prise_charge', None),
                    "chambres_repas": st.session_state.get('etab_confort', None)
                },
                "medecins": {
                    "note_globale": st.session_state.get('note_medecins', None),
                    "qualite_explications": {
                        "evaluation": st.session_state.get('medecin_explications', None),
                        "note": convert_text_to_rating(st.session_state.get('medecin_explications', 'Correctes'))
                    },
                    "sentiment_confiance": {
                        "evaluation": st.session_state.get('medecin_confiance', None),
                        "note": convert_text_to_rating(st.session_state.get('medecin_confiance', 'Confiance modérée'))
                    },
                    "motivation_prescription": {
                        "evaluation": st.session_state.get('medecin_motivation', None),
                        "note": convert_text_to_rating(st.session_state.get('medecin_motivation', 'Moyennement motivé'))
                    },
                    "respect_identite": {
                        "evaluation": st.session_state.get('medecin_respect', None),
                        "note": convert_text_to_rating(st.session_state.get('medecin_respect', 'Modérément respectueux'))
                    }
                }
            },
            "note_questions_fermees": st.session_state.get('note_questions_fermees', None)
        }
        
        export_json = json.dumps(export_data, ensure_ascii=False, indent=2)
        
        st.download_button(
            label="📁 Télécharger l'analyse complète (JSON)",
            data=export_json,
            file_name=f"hospitalidee_analyse_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # Actions finales selon Cursor rules
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🔄 Nouvelle analyse", use_container_width=True):
            # Reset complet - retour à la sélection du type
            for key in list(st.session_state.keys()):
                if key.startswith(('avis_', 'sentiment_', 'rating_', 'final_', 'analysis_', 'current_', 'note_', 'etab_', 'medecin_', 'evaluation_')):
                    del st.session_state[key]
            init_session_state()
            st.rerun()
    
    with col2:
        if st.button("← Retour analyse", use_container_width=True):
            st.session_state.current_step = 4
            st.rerun()
    
    with col3:
        st.markdown("✅ **Analyse terminée**")


def create_sentiment_gauge(sentiment: str, confidence: float):
    """Crée un graphique gauge pour le sentiment selon Cursor rules"""
    sentiment_values = {'negatif': 0, 'neutre': 50, 'positif': 100}
    value = sentiment_values.get(sentiment, 50)
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Sentiment ({confidence:.0%} confiance)"},
        delta = {'reference': 50},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': settings.streamlit_theme_primary_color},
            'steps': [
                {'range': [0, 33], 'color': "lightgray"},
                {'range': [33, 66], 'color': "gray"},
                {'range': [66, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def create_detailed_sentiment_chart(sentiment_data: Dict[str, Any]):
    """Crée un graphique détaillé du sentiment selon Cursor rules"""
    metrics = ['Confiance', 'Intensité émotionnelle']
    values = [
        sentiment_data.get('confidence', 0) * 100,
        sentiment_data.get('emotional_intensity', 0) * 100
    ]
    
    fig = px.bar(
        x=metrics,
        y=values,
        title="Métriques d'analyse",
        color=values,
        color_continuous_scale=['red', 'yellow', 'green']
    )
    
    fig.update_layout(
        yaxis_title="Pourcentage",
        yaxis=dict(range=[0, 100]),
        height=300,
        showlegend=False
    )
    
    return fig


def create_rating_breakdown_chart(rating_data: Dict[str, Any]):
    """Crée un graphique de décomposition de la note selon Cursor rules"""
    factors = rating_data.get('factors', {})
    
    labels = ['Sentiment', 'Intensité', 'Contenu']
    values = [
        factors.get('sentiment_weight', 0.5) * 100,
        factors.get('intensity_weight', 0.3) * 100, 
        factors.get('content_weight', 0.2) * 100
    ]
    
    fig = px.pie(
        values=values,
        names=labels,
        title="Facteurs de calcul de la note"
    )
    
    fig.update_layout(height=300)
    return fig


def main():
    """Fonction principale de l'application selon les Cursor rules - workflow séparé"""
    init_streamlit_config()
    init_session_state()
    render_sidebar()
    
    # Routage par étapes selon nouveau workflow séparé
    current_step = st.session_state.current_step
    
    if current_step == 0:
        step_0_selection_type()
    elif current_step == 1:
        step_1_questionnaire()
    elif current_step == 2:
        step_2_saisie_avis()
    elif current_step == 3:
        step_3_note_ia()
    elif current_step == 4:
        step_4_analyse_hybride()
    elif current_step == 5:
        step_5_resultat_final()
    else:
        st.error("Étape inconnue")
        st.session_state.current_step = 0
        st.rerun()


if __name__ == "__main__":
    main() 