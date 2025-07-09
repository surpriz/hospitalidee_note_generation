#!/usr/bin/env python3
"""
Script de lancement pour l'interface Streamlit Hospitalidée
Configure automatiquement le PYTHONPATH et lance l'application
"""

import os
import sys
import subprocess

def main():
    """Lance l'application Streamlit avec la configuration correcte"""
    
    # Obtenir le répertoire du script (hospitalidee_notation)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ajouter le répertoire au PYTHONPATH
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    # Configuration des variables d'environnement
    env = os.environ.copy()
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f"{script_dir}:{env['PYTHONPATH']}"
    else:
        env['PYTHONPATH'] = script_dir
    
    # Chemin vers l'application Streamlit
    app_path = os.path.join(script_dir, 'streamlit_apps', 'besoin_1_notation_auto.py')
    
    # Vérifier que le fichier existe
    if not os.path.exists(app_path):
        print(f"Erreur: Fichier non trouvé: {app_path}")
        sys.exit(1)
    
    # Arguments pour Streamlit
    cmd = [
        sys.executable, 
        '-m', 'streamlit', 
        'run', 
        app_path,
        '--server.port', '8501',
        '--server.headless', 'false',
        '--server.fileWatcherType', 'auto'
    ]
    
    print("🏥 Lancement de l'interface Hospitalidée...")
    print(f"📁 Répertoire: {script_dir}")
    print(f"🚀 Application: {app_path}")
    print("🌐 URL: http://localhost:8501")
    print("-" * 50)
    
    try:
        # Lancer Streamlit avec l'environnement configuré
        subprocess.run(cmd, env=env, cwd=script_dir)
    except KeyboardInterrupt:
        print("\n🛑 Application arrêtée par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 