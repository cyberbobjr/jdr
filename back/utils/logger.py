# Logger JSON (Grafana/Loki‑friendly) - Migration vers système de logging standard

from datetime import datetime, timezone

from ..config import get_logger

# Logger pour ce module
logger = get_logger(__name__)

def log_debug(message: str, **kwargs):
    """
    ### log_debug
    **Description :** Écrit un message de log JSON sur la sortie standard et/ou dans un fichier si DEBUG est à true ou LOG_FILE défini.
    **Paramètres :**
    - `message` (str) : Message à logger.
    - `kwargs` (dict) : Informations additionnelles à inclure dans le log.
    **Retour :** None
    **Raises :** ValueError si des attributs réservés sont passés dans kwargs.
    """
    # Prévenir le conflit sur les attributs réservés dans kwargs
    reserved_attrs = {'message', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                     'filename', 'module', 'lineno', 'funcName', 'created', 
                     'msecs', 'relativeCreated', 'thread', 'threadName', 
                     'processName', 'process', 'name'}
    conflicting = set(kwargs.keys()) & reserved_attrs
    if conflicting:
        raise ValueError(f"Les clés suivantes sont réservées par LogRecord: {conflicting}")

    try:
        # Utiliser le système de logging standard avec format JSON
        # Ne pas mettre 'message' ou 'level' dans extra pour éviter les conflits
        extra_data = {
            "log_timestamp": datetime.now(timezone.utc).isoformat(),
            "log_level": "DEBUG",
            **kwargs
        }

        # Log via le logger standard Python
        logger.debug(message, extra=extra_data)

    except Exception as e:
        # Log minimal sur erreur de log (pas pour les erreurs de validation)
        print(f"[LOGGING ERROR] {e}")
        import traceback
        print(traceback.format_exc())

def log_info(message: str, **kwargs):
    """
    ### log_info
    **Description :** Log un message d'information.
    **Paramètres :**
    - `message` (str) : Message à logger.
    - `kwargs` (dict) : Informations additionnelles.
    """
    try:
        extra_data = {
            "log_timestamp": datetime.now(timezone.utc).isoformat(),
            "log_level": "INFO",
            **kwargs
        }
        logger.info(message, extra=extra_data)
    except Exception as e:
        print(f"[LOGGING ERROR] {e}")

def log_warning(message: str, **kwargs):
    """
    ### log_warning
    **Description :** Log un message d'avertissement.
    **Paramètres :**
    - `message` (str) : Message à logger.
    - `kwargs` (dict) : Informations additionnelles.
    """
    try:
        extra_data = {
            "log_timestamp": datetime.now(timezone.utc).isoformat(),
            "log_level": "WARNING",
            **kwargs
        }
        logger.warning(message, extra=extra_data)
    except Exception as e:
        print(f"[LOGGING ERROR] {e}")

def log_error(message: str, **kwargs):
    """
    ### log_error
    **Description :** Log un message d'erreur.
    **Paramètres :**
    - `message` (str) : Message à logger.
    - `kwargs` (dict) : Informations additionnelles.
    """
    try:
        extra_data = {
            "log_timestamp": datetime.now(timezone.utc).isoformat(),
            "log_level": "ERROR",
            **kwargs
        }
        logger.error(message, extra=extra_data)
    except Exception as e:
        print(f"[LOGGING ERROR] {e}")

def log_critical(message: str, **kwargs):
    """
    ### log_critical
    **Description :** Log un message critique.
    **Paramètres :**
    - `message` (str) : Message à logger.
    - `kwargs` (dict) : Informations additionnelles.
    """
    try:
        extra_data = {
            "log_timestamp": datetime.now(timezone.utc).isoformat(),
            "log_level": "CRITICAL",
            **kwargs
        }
        logger.critical(message, extra=extra_data)
    except Exception as e:
        print(f"[LOGGING ERROR] {e}")
