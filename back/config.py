# Variables d’environnement

import os

def get_data_dir() -> str:
    """
    ### get_data_dir
    **Description :** Retourne le chemin du dossier data utilisé par l'application. Peut être surchargé par la variable d'environnement JDR_DATA_DIR.
    **Parameters :**
    - Aucun
    **Returns :**
    - (str) : Chemin absolu du dossier data à utiliser.
    """
    return os.environ.get("JDR_DATA_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data")))
