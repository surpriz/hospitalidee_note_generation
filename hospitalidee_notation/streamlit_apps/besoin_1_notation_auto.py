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
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    
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


def render_sidebar():
    """Interface latérale avec navigation selon les Cursor rules"""
    st.sidebar.markdown("## 🏥 Hospitalidée")
    st.sidebar.markdown("### Génération Automatique de Notes")
    
    st.sidebar.markdown("---")
    
    # Indicateur de progression
    steps = ["Saisie", "Analyse", "Proposition", "Validation", "Résultat"]
    current = st.session_state.current_step
    
    for i, step in enumerate(steps, 1):
        if i < current:
            st.sidebar.markdown(f"✅ **{i}. {step}**")
        elif i == current:
            st.sidebar.markdown(f"🔄 **{i}. {step}**")
        else:
            st.sidebar.markdown(f"⏸️ {i}. {step}")
    
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


def step_1_saisie_avis():
    """Écran 1: Saisie d'avis avec analyse en temps réel selon les Cursor rules"""
    st.header("📝 Étape 1 : Saisie de votre avis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Partagez votre expérience** dans l'établissement de santé. 
        Plus votre avis sera détaillé, plus notre analyse sera précise.
        """)
        
        # Zone de texte principale avec callback selon Cursor rules
        avis_text = st.text_area(
            label="Votre avis complet",
            value=st.session_state.avis_text,
            height=200,
            placeholder="Décrivez votre expérience : accueil, soins reçus, personnel, confort...",
            help="Partagez tous les aspects de votre séjour qui vous semblent importants"
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
                    
                    # Graphique de répartition
                    if confidence > 0.3:  # Seuil de fiabilité
                        fig = create_sentiment_gauge(sentiment, confidence)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Indicateurs détaillés
                    word_count = len(avis_text.split())
                    st.metric("Mots analysés", word_count)
                    
                except Exception as e:
                    st.error(f"Erreur d'analyse : {str(e)}")
        
        else:
            st.info("Commencez à écrire votre avis pour voir l'analyse en temps réel")
    
    # Navigation selon Cursor rules
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("Continuer vers l'analyse complète 📊", type="primary", use_container_width=True):
            if len(avis_text.strip()) > 20:  # Validation minimum
                st.session_state.current_step = 2
                st.rerun()
            else:
                st.error("Veuillez écrire un avis plus détaillé (minimum 20 caractères)")


def step_2_analyse_complete():
    """Écran 2: Analyse complète avec détails selon les Cursor rules"""
    st.header("🔍 Étape 2 : Analyse complète de votre avis")
    
    if not st.session_state.sentiment_analysis:
        st.error("Analyse de sentiment manquante. Retournez à l'étape 1.")
        return
    
    sentiment_data = st.session_state.sentiment_analysis
    
    # Affichage des résultats détaillés selon Cursor rules
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Résultats de l'analyse")
        
        # Métriques principales
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        
        with metrics_col1:
            sentiment = sentiment_data.get('sentiment', 'neutre')
            st.metric("Sentiment global", sentiment.title())
        
        with metrics_col2:
            confidence = sentiment_data.get('confidence', 0.0)
            st.metric("Niveau de confiance", f"{confidence:.1%}")
        
        with metrics_col3:
            intensity = sentiment_data.get('emotional_intensity', 0.5)
            st.metric("Intensité émotionnelle", f"{intensity:.1%}")
        
        # Indicateurs positifs et négatifs
        st.markdown("#### 🟢 Aspects positifs détectés")
        positive_indicators = sentiment_data.get('positive_indicators', [])
        if positive_indicators:
            for indicator in positive_indicators[:5]:  # Limite affichage
                st.markdown(f"• {indicator}")
        else:
            st.info("Aucun aspect positif spécifique détecté")
        
        st.markdown("#### 🔴 Aspects négatifs détectés")
        negative_indicators = sentiment_data.get('negative_indicators', [])
        if negative_indicators:
            for indicator in negative_indicators[:5]:  # Limite affichage
                st.markdown(f"• {indicator}")
        else:
            st.info("Aucun aspect négatif spécifique détecté")
    
    with col2:
        st.markdown("### 📈 Visualisations")
        
        # Graphique de sentiment selon Cursor rules
        fig_sentiment = create_detailed_sentiment_chart(sentiment_data)
        st.plotly_chart(fig_sentiment, use_container_width=True)
        
        # Thèmes clés
        key_themes = sentiment_data.get('key_themes', [])
        if key_themes:
            st.markdown("#### 🏷️ Thèmes principaux")
            themes_df = pd.DataFrame({'Thèmes': key_themes})
            st.dataframe(themes_df, hide_index=True)
    
    # Navigation selon Cursor rules
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Retour à la saisie", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
    
    with col3:
        if st.button("Calculer la note suggérée →", type="primary", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()


def step_3_proposition_note():
    """Écran 3: Proposition de note avec justification selon les Cursor rules"""
    st.header("⭐ Étape 3 : Note suggérée par l'IA")
    
    if not st.session_state.sentiment_analysis:
        st.error("Analyse de sentiment manquante")
        return
    
    # Calcul de la note si pas déjà fait
    if not st.session_state.rating_calculation:
        with st.spinner("Calcul de la note en cours..."):
            try:
                rating_result = calculate_rating_from_text(
                    st.session_state.avis_text, 
                    st.session_state.sentiment_analysis
                )
                st.session_state.rating_calculation = rating_result
            except Exception as e:
                st.error(f"Erreur lors du calcul : {str(e)}")
                return
    
    rating_data = st.session_state.rating_calculation
    suggested_rating = rating_data.get('suggested_rating', 3.0)
    confidence = rating_data.get('confidence', 0.0)
    justification = rating_data.get('justification', "Calcul automatique")
    
    # Affichage de la note suggérée selon Cursor rules
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎯 Note suggérée par l'IA")
        
        # Affichage visuel de la note
        rating_display = "⭐" * int(suggested_rating) + "☆" * (5 - int(suggested_rating))
        st.markdown(f"""
        <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px; margin: 10px 0;'>
            <h1 style='color: {settings.streamlit_theme_primary_color}; margin: 0;'>{suggested_rating}/5</h1>
            <h3 style='margin: 5px 0;'>{rating_display}</h3>
            <p style='margin: 0; font-style: italic;'>Confiance: {confidence:.1%}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Justification détaillée
        st.markdown("#### 💭 Justification de l'IA")
        st.info(justification)
        
        # Facteurs de calcul selon Cursor rules
        factors = rating_data.get('factors', {})
        if factors:
            st.markdown("#### ⚖️ Facteurs pris en compte")
            factors_df = pd.DataFrame([
                {"Facteur": "Impact du sentiment", "Poids": f"{factors.get('sentiment_weight', 0.5):.1%}"},
                {"Facteur": "Intensité émotionnelle", "Poids": f"{factors.get('intensity_weight', 0.3):.1%}"},
                {"Facteur": "Richesse du contenu", "Poids": f"{factors.get('content_weight', 0.2):.1%}"}
            ])
            st.dataframe(factors_df, hide_index=True)
    
    with col2:
        st.markdown("### 📊 Analyse comparative")
        
        # Graphique comparatif selon Cursor rules
        fig_rating = create_rating_breakdown_chart(rating_data)
        st.plotly_chart(fig_rating, use_container_width=True)
        
        # Comparaison avec note locale si disponible
        local_rating = rating_data.get('local_rating', {})
        if local_rating:
            local_suggested = local_rating.get('local_suggested_rating', 3.0)
            
            st.markdown("#### 🔍 Validation croisée")
            st.metric(
                "Note IA Mistral", 
                f"{suggested_rating}/5",
                delta=None
            )
            st.metric(
                "Note calcul local", 
                f"{local_suggested}/5",
                delta=f"{local_suggested - suggested_rating:+.1f}" if abs(local_suggested - suggested_rating) > 0.1 else None
            )
    
    # Navigation selon Cursor rules
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Retour à l'analyse", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()
    
    with col3:
        if st.button("Valider cette note →", type="primary", use_container_width=True):
            st.session_state.final_rating = suggested_rating
            st.session_state.current_step = 4
            st.rerun()


def step_4_validation():
    """Écran 4: Validation avec possibilité d'ajustement selon les Cursor rules"""
    st.header("✅ Étape 4 : Validation de votre note")
    
    if not st.session_state.rating_calculation:
        st.error("Calcul de note manquant")
        return
    
    suggested_rating = st.session_state.rating_calculation.get('suggested_rating', 3.0)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎯 Note proposée par l'IA")
        st.markdown(f"""
        <div style='text-align: center; padding: 15px; background-color: #e8f4f8; border-radius: 10px;'>
            <h2>{suggested_rating}/5 ⭐</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ⚖️ Ajustement si nécessaire")
        st.markdown("Vous pouvez ajuster cette note si elle ne reflète pas parfaitement votre expérience :")
        
        # Slider d'ajustement selon Cursor rules
        adjusted_rating = st.slider(
            "Note finale",
            min_value=1.0,
            max_value=5.0,
            value=float(suggested_rating),
            step=0.5,
            help="Ajustez la note selon votre ressenti personnel"
        )
        
        # Indication de changement
        if abs(adjusted_rating - suggested_rating) > 0.1:
            difference = adjusted_rating - suggested_rating
            st.info(f"Ajustement: {difference:+.1f} point{'s' if abs(difference) > 1 else ''}")
        
        # Raison de l'ajustement si modifié
        if abs(adjusted_rating - suggested_rating) > 0.1:
            adjustment_reason = st.text_area(
                "Pourquoi cet ajustement ? (optionnel)",
                placeholder="Expliquez pourquoi vous modifiez la note suggérée...",
                help="Cela nous aide à améliorer notre algorithme"
            )
            st.session_state.adjustment_reason = adjustment_reason
        
        st.session_state.final_rating = adjusted_rating
    
    with col2:
        st.markdown("### 📋 Récapitulatif de votre avis")
        
        # Résumé complet selon Cursor rules
        sentiment = st.session_state.sentiment_analysis.get('sentiment', 'neutre')
        confidence = st.session_state.sentiment_analysis.get('confidence', 0.0)
        
        st.markdown(f"""
        **Sentiment détecté:** {sentiment.title()}  
        **Confiance de l'analyse:** {confidence:.1%}  
        **Note originale IA:** {suggested_rating}/5  
        **Note finale:** {adjusted_rating}/5  
        """)
        
        # Aperçu du texte
        st.markdown("**Extrait de votre avis:**")
        preview_text = st.session_state.avis_text[:200] + "..." if len(st.session_state.avis_text) > 200 else st.session_state.avis_text
        st.markdown(f"> {preview_text}")
        
        # Métriques finales
        st.markdown("#### 📊 Statistiques")
        word_count = len(st.session_state.avis_text.split())
        char_count = len(st.session_state.avis_text)
        
        col_stats1, col_stats2 = st.columns(2)
        with col_stats1:
            st.metric("Mots", word_count)
        with col_stats2:
            st.metric("Caractères", char_count)
    
    # Navigation selon Cursor rules
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Modifier la note", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()
    
    with col3:
        if st.button("Finaliser l'avis ✨", type="primary", use_container_width=True):
            st.session_state.analysis_complete = True
            st.session_state.current_step = 5
            st.rerun()


def step_5_resultat_final():
    """Écran 5: Résultat final avec export selon les Cursor rules"""
    st.header("🎉 Étape 5 : Avis finalisé")
    
    if not st.session_state.analysis_complete:
        st.error("Processus non terminé")
        return
    
    # Résultat final selon Cursor rules
    st.success("🎊 Félicitations ! Votre avis a été analysé et finalisé avec succès.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 Votre avis finalisé")
        
        # Carte récapitulative
        final_rating = st.session_state.final_rating
        rating_stars = "⭐" * int(final_rating) + "☆" * (5 - int(final_rating))
        
        st.markdown(f"""
        <div style='padding: 20px; background-color: #f8f9fa; border-left: 5px solid {settings.streamlit_theme_primary_color}; border-radius: 5px; margin: 10px 0;'>
            <h3 style='margin-top: 0; color: {settings.streamlit_theme_primary_color};'>Note finale: {final_rating}/5 {rating_stars}</h3>
            <p><strong>Sentiment:</strong> {st.session_state.sentiment_analysis.get('sentiment', '').title()}</p>
            <p><strong>Avis:</strong></p>
            <em>"{st.session_state.avis_text}"</em>
        </div>
        """, unsafe_allow_html=True)
        
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
            "analysis_timestamp": pd.Timestamp.now().isoformat()
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
            # Reset complet
            for key in list(st.session_state.keys()):
                if key.startswith(('avis_', 'sentiment_', 'rating_', 'final_', 'analysis_', 'current_')):
                    del st.session_state[key]
            init_session_state()
            st.rerun()
    
    with col2:
        if st.button("← Modifier l'avis", use_container_width=True):
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
    """Fonction principale de l'application selon les Cursor rules"""
    init_streamlit_config()
    init_session_state()
    render_sidebar()
    
    # Routage par étapes selon Cursor rules
    current_step = st.session_state.current_step
    
    if current_step == 1:
        step_1_saisie_avis()
    elif current_step == 2:
        step_2_analyse_complete()
    elif current_step == 3:
        step_3_proposition_note()
    elif current_step == 4:
        step_4_validation()
    elif current_step == 5:
        step_5_resultat_final()
    else:
        st.error("Étape inconnue")
        st.session_state.current_step = 1
        st.rerun()


if __name__ == "__main__":
    main() 