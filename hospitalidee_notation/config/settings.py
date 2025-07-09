"""
Configuration centralisée pour l'extension IA Hospitalidée
Respect des standards définis dans les Cursor rules
"""

import os
from typing import Optional


class Settings:
    """Configuration centralisée pour Hospitalidée"""
    
    def __init__(self):
        # API Mistral AI (obligatoire)
        self.mistral_api_key: str = os.getenv("MISTRAL_API_KEY", "")
        self.mistral_model: str = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
        self.mistral_temperature: float = float(os.getenv("MISTRAL_TEMPERATURE", "0.3"))
        self.mistral_max_tokens: int = int(os.getenv("MISTRAL_MAX_TOKENS", "1000"))
        self.mistral_top_p: float = float(os.getenv("MISTRAL_TOP_P", "0.9"))
        self.mistral_presence_penalty: float = float(os.getenv("MISTRAL_PRESENCE_PENALTY", "0.0"))
        self.mistral_frequency_penalty: float = float(os.getenv("MISTRAL_FREQUENCY_PENALTY", "0.0"))
        
        # Configuration Streamlit
        self.streamlit_port: int = int(os.getenv("STREAMLIT_PORT", "8501"))
        self.streamlit_theme_primary_color: str = os.getenv("STREAMLIT_THEME_PRIMARY_COLOR", "#FF6B35")
        
        # Logging et Debug
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.debug_mode: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
        
        # Cache Redis (optionnel)
        self.redis_url: Optional[str] = os.getenv("REDIS_URL")
        self.cache_duration: int = int(os.getenv("CACHE_DURATION", "3600"))
        
        # Performance et KPIs
        self.max_response_time: float = float(os.getenv("MAX_RESPONSE_TIME", "3.0"))
        self.required_precision: float = float(os.getenv("REQUIRED_PRECISION", "0.85"))
        self.required_coherence: float = float(os.getenv("REQUIRED_COHERENCE", "0.90"))
        
        # RGPD et Sécurité
        self.enable_logging: bool = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
        self.anonymize_data: bool = os.getenv("ANONYMIZE_DATA", "true").lower() == "true"


# Instance globale des settings
settings = Settings()

# Fonction pour recharger la configuration depuis un fichier .env
def load_dotenv_if_exists():
    """Charge le fichier .env s'il existe"""
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            # Recharger les settings après avoir chargé le .env
            global settings
            settings = Settings()
    except ImportError:
        pass  # python-dotenv n'est pas installé

# Charger automatiquement le .env au démarrage
load_dotenv_if_exists() 