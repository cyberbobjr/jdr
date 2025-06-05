# Logger JSON (Grafana/Loki‑friendly)

import os
import json
from datetime import datetime, timezone
from pathlib import Path

def log_debug(message: str = None, **kwargs):
    """
    ### log_debug
    **Description :** Écrit un message de log JSON sur la sortie standard et/ou dans un fichier si DEBUG est à true ou LOG_FILE défini.
    **Paramètres :**
    - `message` (str) : Message à logger.
    - `kwargs` (dict) : Informations additionnelles à inclure dans le log.
    **Retour :** None
    """
    try:
        # Prévenir le conflit sur 'message' dans kwargs
        if 'message' in kwargs:
            raise ValueError("'message' ne doit pas être passé à la fois comme argument et dans kwargs.")
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "DEBUG",
            "message": message,
            **kwargs
        }
        log_line = json.dumps(log_entry, ensure_ascii=False)
        debug_enabled = os.environ.get("DEBUG", "false").lower() == "true"
        log_file = os.environ.get("LOG_FILE")
        if debug_enabled:
            print(log_line)
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
    except Exception as e:
        # Log minimal sur erreur de log
        print(f"[LOGGING ERROR] {e}")
        import traceback
        print(traceback.format_exc())
