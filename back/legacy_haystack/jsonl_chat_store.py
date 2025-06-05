from haystack.dataclasses import ChatMessage
from back.utils.logger import log_debug
from back.utils.message_adapter import extract_message_text
import os
import json


class JsonlChatMessageStore:
    """
    ### JsonlChatMessageStore
    **Description :** Stocke l'historique des messages de chat dans un fichier JSONL pour la persistance entre sessions.
    **Paramètres :**
    - `filepath` (str) : Chemin du fichier JSONL de stockage.
    **Retour :**
    - Instance de store compatible avec la logique Haystack (méthodes load/save).
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        log_debug("Initialisation du JsonlChatMessageStore", action="init_store", filepath=os.path.abspath(filepath))
        self._ensure_file()

    def _ensure_file(self):
        """
        ### _ensure_file
        **Description :** Crée le répertoire et le fichier de stockage s'ils n'existent pas.
        **Paramètres :** Aucun.
        **Retour :** Aucun.
        """
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8"): 
                pass
            log_debug("Création du fichier de session", action="create_session_file", filepath=os.path.abspath(self.filepath))
        else:
            log_debug("Fichier de session existant", action="existing_session_file", filepath=os.path.abspath(self.filepath))

    def load(self):
        """
        ### load
        **Description :** Charge l'historique des messages depuis le fichier JSONL, en ignorant les messages de rôle 'system'.
        **Paramètres :** Aucun.
        **Retour :** Liste des messages ChatMessage chargés depuis le fichier (hors prompt système).
        """
        log_debug("Chargement de l'historique des messages", action="load_messages", filepath=os.path.abspath(self.filepath))
        messages = []
        with open(self.filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        # Correction : ignorer les listes ou mauvais formats
                        if isinstance(data, dict):
                            try:
                                # Vérifier que le contenu n'est pas None ou vide
                                content = data.get("content")
                                if content is None or content == "":
                                    log_debug("Message ignoré : contenu vide", action="skip_empty_message", line_data=str(data))
                                    continue
                                # Ne jamais charger les messages de rôle 'system' (prompt système)
                                if data.get("role") == "user":
                                    messages.append(ChatMessage.from_user(content))
                                elif data.get("role") == "assistant":
                                    messages.append(ChatMessage.from_assistant(content))
                                elif data.get("role") == "tool":
                                    # Pour les messages tool, nous avons besoin d'un origin
                                    # Si pas d'origin spécifié, on utilise un défaut
                                    origin = data.get("origin", "unknown_tool")
                                    content = data.get("content")
                                    messages.append(ChatMessage.from_tool(content, origin=origin))
                            except Exception as e:
                                log_debug("Erreur lors du parsing d'une ligne de message", error=str(e), line=line)
                    except Exception as e:
                        log_debug("Erreur lors du chargement d'une ligne JSONL", error=str(e), line=line)
        log_debug("Historique chargé avec succès", action="load_messages_success", filepath=os.path.abspath(self.filepath), message_count=len(messages))
        return messages

    def save(self, messages):
        """
        ### save
        **Description :** Sauvegarde l'historique des messages dans le fichier JSONL.
        **Paramètres :**
        - `messages` (list): Liste des messages ChatMessage à sauvegarder.
        **Retour :** Aucun.
        """
        log_debug("Sauvegarde de l'historique des messages", action="save_messages", filepath=os.path.abspath(self.filepath), message_count=len(messages))
        with open(self.filepath, "w", encoding="utf-8") as f:
            for msg in messages:
                # Utiliser extract_message_text pour sérialiser chaque message
                data_to_save = extract_message_text(msg)
                # Pour compatibilité Haystack, ajouter l'origin si tool
                if data_to_save["role"] == "system":
                    log_debug(json.dumps(data_to_save, ensure_ascii=False), action="skip_system_message")
                    continue
                f.write(json.dumps(data_to_save, ensure_ascii=False) + "\n")
            f.flush()
        log_debug("Historique sauvegardé avec succès", action="save_messages_success", filepath=os.path.abspath(self.filepath))

    def append_message(self, message: dict):
        """
        ### append_message
        **Description :** Ajoute un message unique (par exemple tool_call ou tool_result) à la fin du fichier JSONL, sans réécrire tout l'historique. Permet la persistance incrémentale des messages critiques pour la traçabilité (ex : [TOOL_CALL], [TOOL_RESULT]).
        **Paramètres :**
        - `message` (dict) : Message à ajouter (doit être sérializable en JSON).
        **Retour :** Aucun.
        """
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(message, ensure_ascii=False) + "\n")
        log_debug("Message ajouté au store JSONL", action="append_message", message=message)
