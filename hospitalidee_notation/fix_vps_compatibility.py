#!/usr/bin/env python3
"""
Script de correction pour compatibilité VPS
Corrige l'appel de calculate_rating_from_text si nécessaire
"""

import os
import re

def fix_streamlit_app():
    """Corrige l'appel dans l'application Streamlit"""
    file_path = "streamlit_apps/besoin_1_notation_auto.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Recherche de l'appel problématique
    old_pattern = r'rating_result = calculate_rating_from_text\(\s*st\.session_state\.avis_text,\s*st\.session_state\.sentiment_analysis,\s*questionnaire_context=st\.session_state\.note_questions_fermees\s*\)'
    
    # Nouveau code compatible
    new_code = '''rating_result = calculate_rating_from_text(
                    st.session_state.avis_text, 
                    st.session_state.sentiment_analysis,
                    st.session_state.note_questions_fermees  # Paramètre positionnel au lieu de keyword
                )'''
    
    if re.search(old_pattern, content):
        print("🔧 Correction de l'appel avec paramètre positionnel...")
        content = re.sub(old_pattern, new_code, content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Correction appliquée")
        return True
    else:
        print("⚠️ Pattern non trouvé - vérification manuelle nécessaire")
        return False

def main():
    """Script principal de correction"""
    print("🔧 CORRECTION COMPATIBILITÉ VPS")
    print("=" * 40)
    
    if fix_streamlit_app():
        print("\n🎉 Correction terminée avec succès")
        print("🔄 Redémarrez votre application Streamlit")
    else:
        print("\n❌ Correction non appliquée")
        print("🔍 Vérifiez manuellement le fichier")

if __name__ == "__main__":
    main() 