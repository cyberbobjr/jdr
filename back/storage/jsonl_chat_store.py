from haystack.dataclasses import ChatMessage, ChatRole
from back.utils.logger import log_debug
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
            with open(self.filepath, "w"): 
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
        with open(self.filepath, "r") as f:
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
        with open(self.filepath, "w") as f:
            for msg in messages:
                # Gestion spéciale pour les messages d'outils dans Haystack 3.x
                if msg.role.value == ChatRole.TOOL and hasattr(msg, 'tool_call_results') and msg.tool_call_results:
                    tool_result = msg.tool_call_results[0]
                    content = tool_result.result
                    """
                        tool_result.origin = ToolCall ou tool_result = ToolCallResult
                    """
                    # Gestion des différents cas d'origin/tool_result
                    if hasattr(tool_result, 'tool_name') and hasattr(tool_result, 'tool_call_id') and hasattr(tool_result, 'arguments'):
                        origin = {
                            "tool_name": tool_result.tool_name,
                            "tool_call_id": tool_result.tool_call_id,
                            "arguments": tool_result.arguments
                        }
                    elif hasattr(tool_result, 'origin'):
                        if hasattr(tool_result.origin, 'tool_name') and hasattr(tool_result.origin, 'tool_call_id') and hasattr(tool_result.origin, 'arguments'):
                            origin = {
                                "tool_name": tool_result.origin.tool_name,
                                "tool_call_id": tool_result.origin.tool_call_id,
                                "arguments": tool_result.origin.arguments
                            }
                        elif isinstance(tool_result.origin, str):
                            origin = tool_result.origin
                        else:
                            origin = "unknown_tool"
                    else:
                        origin = "unknown_tool"
                    if content is None or content == "":
                        log_debug("Message tool ignoré à la sauvegarde : contenu vide", action="skip_save_empty_tool_message")
                        continue
                    data_to_save = {"role": "tool", "content": content, "origin": origin}
                else:
                    # Vérifier que le message a un contenu valide
                    if not hasattr(msg, 'text') or msg.text is None or msg.text == "":
                        log_debug(f"Message ignoré à la sauvegarde : contenu vide - {msg.role.value}", action="skip_save_empty_message", message_type=type(msg).__name__)
                        continue
                        
                    # Extraction robuste du rôle (Enum ou str)
                    role = getattr(msg, "role", None)
                    if hasattr(role, "value"):
                        role = role.value
                    elif role is None and hasattr(msg, "_role"):
                        role = msg._role.value
                    if role == ChatRole.SYSTEM:
                        log_debug("Message de rôle 'system' ignoré à la sauvegarde", action="skip_save_system_message")
                        continue
                    data_to_save = {"role": str(role), "content": msg.text}
                    
                f.write(json.dumps(data_to_save) + "\n")
            f.flush()
        log_debug("Historique sauvegardé avec succès", action="save_messages_success", filepath=os.path.abspath(self.filepath))
