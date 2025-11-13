# Configuration centralisée du projet JdR

import os
import logging
import logging.handlers
from typing import Dict, Any, Optional
from pathlib import Path
import yaml

class Config:
    """Classe de configuration centralisée utilisant un fichier YAML."""

    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = Path(__file__).parent / config_file
        self._config: Dict[str, Any] = {}
        self._logger: Optional[logging.Logger] = None
        self._load_config()
        self._setup_logging()

    def _load_config(self) -> None:
        """Charge la configuration depuis le fichier YAML."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Fichier de configuration '{self.config_file}' introuvable")
        except yaml.YAMLError as e:
            raise ValueError(f"Erreur de syntaxe dans le fichier de configuration: {e}")

    def get_llm_config(self) -> Dict[str, str]:
        """
        ### get_llm_config
        **Description :** Retourne la configuration du modèle LLM.
        **Returns :**
        - (Dict[str, str]) : Configuration avec model, api_endpoint, api_key
        """
        llm_config = self._config.get("llm", {})

        # Surcharge par les variables d'environnement si elles existent
        return {
            "model": os.environ.get("DEEPSEEK_API_MODEL") or llm_config.get("model", "deepseek-chat"),
            "api_endpoint": os.environ.get("DEEPSEEK_API_BASE_URL") or llm_config.get("api_endpoint", "https://api.deepseek.com"),
            "api_key": os.environ.get("DEEPSEEK_API_KEY") or llm_config.get("api_key", "")
        }

    def get_data_dir(self) -> str:
        """
        ### get_data_dir
        **Description :** Retourne le chemin du dossier data utilisé par l'application. Peut être surchargé par la variable d'environnement JDR_DATA_DIR.
        **Parameters :**
        - Aucun
        **Returns :**
        - (str) : Chemin absolu du dossier data à utiliser.
        """
        # Priorité : variable d'environnement > config YAML > valeur par défaut
        data_dir = os.environ.get("JDR_DATA_DIR")
        if not data_dir:
            data_dir = self._config.get("data", {}).get("directory", "gamedata")

        return os.path.abspath(os.path.join(os.path.dirname(__file__), data_dir))

    def get_app_config(self) -> Dict[str, Any]:
        """
        ### get_app_config
        **Description :** Retourne la configuration de l'application.
        **Returns :**
        - (Dict[str, Any]) : Configuration de l'application
        """
        return self._config.get("app", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """
        ### get_logging_config
        **Description :** Retourne la configuration du logging.
        **Returns :**
        - (Dict[str, Any]) : Configuration du logging
        """
        return self._config.get("logging", {})

    def _setup_logging(self) -> None:
        """Configure le système de logging selon la configuration YAML."""
        logging_config = self.get_logging_config()

        # Niveau de log
        log_level = getattr(logging, logging_config.get("level", "INFO").upper())

        # Format des logs
        if logging_config.get("format", "json").lower() == "json":
            # Format JSON pour Grafana/Loki
            log_format = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
            formatter = logging.Formatter(log_format, datefmt='%Y-%m-%dT%H:%M:%S.%fZ')
        else:
            # Format texte standard
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            formatter = logging.Formatter(log_format)

        # Configuration du logger root
        logger = logging.getLogger()
        logger.setLevel(log_level)

        # Supprimer les handlers existants
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Handler fichier (optionnel)
        log_file = logging_config.get("file")
        if log_file:
            # Créer le répertoire si nécessaire
            log_file_path = Path(log_file)
            log_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Handler avec rotation
            max_size = logging_config.get("max_file_size", 10 * 1024 * 1024)  # 10MB par défaut
            backup_count = logging_config.get("backup_count", 5)

            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        # Stocker le logger configuré
        self._logger = logger

    def get_logger(self, name: str):
        """
        ### get_logger
        **Description :** Retourne un logger configuré avec le nom spécifié.
        **Parameters :**
        - `name` (str) : Nom du logger (généralement __name__)
        **Returns :**
        - Logger configuré
        """
        return logging.getLogger(name)

# Instance globale de configuration
config = Config()

# Fonctions de compatibilité pour l'existant
def get_data_dir() -> str:
    """Fonction de compatibilité pour get_data_dir."""
    return config.get_data_dir()

def get_llm_config() -> Dict[str, str]:
    """Fonction de compatibilité pour la configuration LLM."""
    return config.get_llm_config()

def get_logger(name: str):
    """Fonction de compatibilité pour obtenir un logger configuré."""
    return config.get_logger(name)

# Configuration du logging au niveau module
logger = get_logger(__name__)
