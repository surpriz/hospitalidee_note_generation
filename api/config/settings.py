"""
Configuration centralisée pour l'API Hospitalidée IA
Respect des standards définis dans les Cursor rules
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Chargement automatique du fichier .env
load_dotenv()


class Settings:
    """Configuration centralisée pour l'API Hospitalidée"""
    
    def __init__(self):
        # === API MISTRAL AI (OBLIGATOIRE) ===
        self.mistral_api_key: str = os.getenv("MISTRAL_API_KEY", "")
        self.mistral_model: str = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
        self.mistral_temperature: float = float(os.getenv("MISTRAL_TEMPERATURE", "0.3"))
        self.mistral_max_tokens: int = int(os.getenv("MISTRAL_MAX_TOKENS", "1000"))
        self.mistral_top_p: float = float(os.getenv("MISTRAL_TOP_P", "0.9"))
        self.mistral_presence_penalty: float = float(os.getenv("MISTRAL_PRESENCE_PENALTY", "0.0"))
        self.mistral_frequency_penalty: float = float(os.getenv("MISTRAL_FREQUENCY_PENALTY", "0.0"))
        
        # === CONFIGURATION API ===
        self.api_host: str = os.getenv("API_HOST", "0.0.0.0")
        self.api_port: int = int(os.getenv("API_PORT", "8000"))
        self.api_workers: int = int(os.getenv("API_WORKERS", "1"))
        
        # === LOGGING ET DEBUG ===
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.debug_mode: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.enable_logging: bool = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
        
        # === CACHE REDIS (OPTIONNEL) ===
        self.redis_url: Optional[str] = os.getenv("REDIS_URL")
        self.cache_duration: int = int(os.getenv("CACHE_DURATION", "3600"))
        self.enable_cache: bool = os.getenv("ENABLE_CACHE", "false").lower() == "true"
        
        # === PERFORMANCE ET KPIs ===
        self.max_response_time: float = float(os.getenv("MAX_RESPONSE_TIME", "30.0"))
        self.required_precision: float = float(os.getenv("REQUIRED_PRECISION", "0.85"))
        self.required_coherence: float = float(os.getenv("REQUIRED_COHERENCE", "0.90"))
        self.max_text_length: int = int(os.getenv("MAX_TEXT_LENGTH", "5000"))
        
        # === SÉCURITÉ ===
        self.cors_origins: str = os.getenv("CORS_ORIGINS", "*")
        self.rate_limit_enabled: bool = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
        self.rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))
        
        # === RGPD ET ANONYMISATION ===
        self.anonymize_data: bool = os.getenv("ANONYMIZE_DATA", "true").lower() == "true"
        self.store_requests: bool = os.getenv("STORE_REQUESTS", "false").lower() == "true"
        
        # Validation des paramètres critiques
        self._validate_settings()
    
    def _validate_settings(self):
        """Valide les paramètres critiques"""
        if not self.mistral_api_key:
            raise ValueError("MISTRAL_API_KEY est obligatoire. Configurez votre fichier .env")
        
        if self.mistral_temperature < 0 or self.mistral_temperature > 2:
            raise ValueError("MISTRAL_TEMPERATURE doit être entre 0 et 2")
        
        if self.mistral_max_tokens < 100 or self.mistral_max_tokens > 4000:
            raise ValueError("MISTRAL_MAX_TOKENS doit être entre 100 et 4000")
    
    def get_cors_origins(self) -> list:
        """Retourne la liste des origines CORS autorisées"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def is_production(self) -> bool:
        """Vérifie si on est en mode production"""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"


# Instance globale des settings
settings = Settings()


def load_dotenv_if_exists():
    """Charge le fichier .env s'il existe"""
    env_files = [".env", ".env.local", ".env.prod"]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            load_dotenv(env_file)
            print(f"✅ Configuration chargée depuis {env_file}")
            break
    else:
        print("⚠️ Aucun fichier .env trouvé - utilisation des variables d'environnement système")


# Chargement automatique au import
load_dotenv_if_exists()