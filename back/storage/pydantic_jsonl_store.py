"""
Store JSONL adapté pour PydanticAI.
Compatible avec les messages PydanticAI tout en conservant l'interface du JsonlChatMessageStore.
"""

import os

from back.utils.logger import log_debug

try:
    from pydantic_ai.messages import ModelMessagesTypeAdapter
except ImportError:
    # Fallback pour les environnements où pydantic_ai n'est pas disponible
    ModelMessagesTypeAdapter = None


class PydanticJsonlStore:
    """
    ### PydanticJsonlStore
    **Description :** Store JSONL adapté pour PydanticAI, compatible avec les formats de messages PydanticAI.
    **Paramètres :**
    - `filepath` (str) : Chemin du fichier JSONL de stockage.
    **Méthodes :**
    - `load()` : Charge l'historique
    - `save_pydantic_history(messages)` : Sérialise et sauvegarde une liste de messages PydanticAI dans le fichier JSONL.
    - `load_pydantic_history()` : Recharge l'historique complet au format PydanticAI à partir du fichier JSONL.
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._messages = []
        log_debug("Initialisation du PydanticJsonlStore", action="init_store", filepath=os.path.abspath(filepath))
        self._ensure_file()

    def _ensure_file(self):
        """
        ### _ensure_file
        **Description :** Crée le répertoire et le fichier de stockage s'ils n'existent pas.
        """
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8"): 
                pass
            log_debug("Création du fichier de session PydanticAI", action="create_session_file", filepath=os.path.abspath(self.filepath))
        else:
            log_debug("Fichier de session existant PydanticAI", action="existing_session_file", filepath=os.path.abspath(self.filepath))

    def save_pydantic_history(self, messages: list):
        """
        ### save_pydantic_history
        **Description :** Sérialise et sauvegarde une liste de messages PydanticAI dans le fichier JSONL, en utilisant ModelMessagesTypeAdapter.dump_json comme recommandé dans la documentation officielle.
        **Paramètres :**
        - `messages` (list) : Liste de messages PydanticAI à sauvegarder.
        """
        import json

        # Vérifier que ModelMessagesTypeAdapter est disponible
        if ModelMessagesTypeAdapter is None:
            raise ImportError("pydantic_ai.messages.ModelMessagesTypeAdapter n'est pas disponible. Vérifiez que pydantic-ai est installé.")

        # Utiliser dump_json pour une sérialisation cohérente avec PydanticAI
        json_bytes = ModelMessagesTypeAdapter.dump_json(messages, indent=2)
        json_str = json_bytes.decode('utf-8')

        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(json_str)
        log_debug("Historique PydanticAI sauvegardé (ModelMessagesTypeAdapter.dump_json)", action="save_pydantic_history", filepath=os.path.abspath(self.filepath), count=len(messages))

    def load_pydantic_history(self) -> list:
        """
        ### load_pydantic_history
        **Description :** Recharge l'historique complet au format PydanticAI à partir du fichier JSONL, en utilisant ModelMessagesTypeAdapter.validate_python comme dans la documentation officielle.
        **Returns :** Liste de messages PydanticAI désérialisés (list[ModelMessage]).
        """
        import json
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:  # Fichier vide
                    return []
                data = json.loads(content)

            # Vérifier que ModelMessagesTypeAdapter est disponible
            if ModelMessagesTypeAdapter is None:
                raise ImportError("pydantic_ai.messages.ModelMessagesTypeAdapter n'est pas disponible. Vérifiez que pydantic-ai est installé.")

            history = ModelMessagesTypeAdapter.validate_python(data)
            log_debug("Historique PydanticAI rechargé (validate_python)", action="load_pydantic_history", filepath=os.path.abspath(self.filepath), count=len(history))
            return history
        except Exception as e:
            log_debug("Erreur lors du rechargement de l'historique PydanticAI", error=str(e), filepath=os.path.abspath(self.filepath))
            return []

    def read_json_history(self) -> list:
        """
        ### read_json_history
        **Description :** Lit et retourne directement le contenu JSON du fichier d'historique, sans désérialisation PydanticAI.
        **Returns :** Liste de messages (dictionnaires) au format PydanticAI natif (jsonable).
        """
        import json
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:  # Fichier vide
                    return []
                data = json.loads(content)
            return data
        except Exception as e:
            log_debug("Erreur lors de la lecture du json historique brut", error=str(e), filepath=os.path.abspath(self.filepath))
            return []

    # Suppression des méthodes de compatibilité Haystack (save, load) qui ne sont plus utilisées ni nécessaires.
    # Seules les méthodes PydanticAI modernes sont conservées.
