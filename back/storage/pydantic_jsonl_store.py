"""
Store JSONL adapté pour PydanticAI.
Compatible avec les messages PydanticAI tout en conservant l'interface du JsonlChatMessageStore.
"""

import os
import json
from typing import List, Dict, Any
from back.utils.logger import log_debug


class PydanticJsonlStore:
    """
    ### PydanticJsonlStore
    **Description :** Store JSONL adapté pour PydanticAI, compatible avec les formats de messages PydanticAI.
    **Paramètres :**
    - `filepath` (str) : Chemin du fichier JSONL de stockage.
    **Méthodes :**
    - `load()` : Charge l'historique
    - `save_user_message(message)` : Sauvegarde un message utilisateur
    - `save_assistant_message(message)` : Sauvegarde un message assistant
    - `save_tool_message(tool_name, args, result)` : Sauvegarde un appel d'outil
    - `get_messages()` : Retourne tous les messages chargés
    - `get_pydantic_messages()` : Retourne les messages au format PydanticAI
    """
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._messages = []
        log_debug("Initialisation du PydanticJsonlStore", action="init_store", filepath=os.path.abspath(filepath))
        self._ensure_file()
        self._load_messages()

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

    def _load_messages(self):
        """
        ### _load_messages
        **Description :** Charge tous les messages depuis le fichier JSONL.
        """
        log_debug("Chargement de l'historique des messages PydanticAI", action="load_messages", filepath=os.path.abspath(self.filepath))
        self._messages = []
        
        with open(self.filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        if isinstance(data, dict) and data.get("content"):
                            self._messages.append(data)
                    except Exception as e:
                        log_debug("Erreur lors du chargement d'une ligne JSONL PydanticAI", error=str(e), line=line)
        
        log_debug("Historique PydanticAI chargé avec succès", action="load_messages_success", filepath=os.path.abspath(self.filepath), count=len(self._messages))

    def load(self) -> List[Dict[str, Any]]:
        """
        ### load
        **Description :** Retourne l'historique des messages pour compatibilité avec l'interface Haystack.
        **Retour :** Liste des messages sous forme de dictionnaires.
        """
        return self._messages.copy()

    def save_user_message(self, message: str):
        """
        ### save_user_message
        **Description :** Sauvegarde un message utilisateur dans le fichier JSONL.
        **Paramètres :**
        - `message` (str) : Contenu du message utilisateur.
        """
        message_data = {
            "role": "user",
            "content": message,
            "timestamp": self._get_timestamp()
        }
        self._append_message(message_data)
        log_debug("Message utilisateur sauvegardé", action="save_user_message", content=message)

    def save_assistant_message(self, message: str):
        """
        ### save_assistant_message
        **Description :** Sauvegarde un message assistant dans le fichier JSONL.
        **Paramètres :**
        - `message` (str) : Contenu du message assistant.
        """
        message_data = {
            "role": "assistant",
            "content": message,
            "timestamp": self._get_timestamp()
        }
        self._append_message(message_data)
        log_debug("Message assistant sauvegardé", action="save_assistant_message", content=message)

    def save_tool_message(self, tool_name: str, args: Dict[str, Any], result: Any):
        """
        ### save_tool_message
        **Description :** Sauvegarde un appel d'outil dans le fichier JSONL.
        **Paramètres :**
        - `tool_name` (str) : Nom de l'outil appelé.
        - `args` (Dict[str, Any]) : Arguments de l'outil.
        - `result` (Any) : Résultat de l'outil.
        """
        message_data = {
            "role": "tool",
            "tool_name": tool_name,
            "args": args,
            "result": result,
            "content": f"[TOOL_CALL] {tool_name}: {result}",
            "timestamp": self._get_timestamp()
        }
        self._append_message(message_data)
        log_debug("Appel d'outil sauvegardé", action="save_tool_message", tool_name=tool_name, args=args, result=result)

    def _append_message(self, message_data: Dict[str, Any]):
        """
        ### _append_message
        **Description :** Ajoute un message au fichier JSONL et à la liste en mémoire.
        **Paramètres :**
        - `message_data` (Dict[str, Any]) : Données du message à ajouter.
        """
        # Ajouter à la liste en mémoire
        self._messages.append(message_data)
        
        # Ajouter au fichier
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(message_data, ensure_ascii=False) + "\n")

    def _get_timestamp(self) -> str:
        """
        ### _get_timestamp
        **Description :** Génère un timestamp pour les messages.
        **Retour :** Timestamp sous forme de chaîne.
        """
        from datetime import datetime
        return datetime.now().isoformat()

    def get_messages(self) -> List[Dict[str, Any]]:
        """
        ### get_messages
        **Description :** Retourne tous les messages chargés.
        **Retour :** Liste des messages.
        """
        return self._messages.copy()

    def clear(self):
        """
        ### clear
        **Description :** Efface tous les messages du store et du fichier.
        """
        self._messages = []
        with open(self.filepath, "w", encoding="utf-8"):
            pass
        log_debug("Store PydanticAI vidé", action="clear_store", filepath=os.path.abspath(self.filepath))

    def get_pydantic_messages(self) -> List[Dict[str, Any]]:
        """
        ### get_pydantic_messages
        **Description :** Retourne les messages dans un format compatible avec PydanticAI.
        **Retour :** Liste des messages formatés pour PydanticAI.
        """
        pydantic_messages = []
        
        for msg in self._messages:
            if isinstance(msg, dict):
                role = msg.get('role', '')
                content = msg.get('content', '')
                
                if role == 'user':
                    pydantic_messages.append({
                        'role': 'user',
                        'content': content
                    })
                elif role == 'assistant':
                    pydantic_messages.append({
                        'role': 'assistant', 
                        'content': content
                    })
                elif role == 'tool':
                    # Format spécial pour les appels d'outils
                    tool_name = msg.get('tool_name', '')
                    args = msg.get('args', {})
                    result = msg.get('result', '')
                    
                    pydantic_messages.append({
                        'role': 'tool_use',
                        'tool_name': tool_name,
                        'arguments': args,
                        'result': result,
                        'content': content
                    })
        
        return pydantic_messages

    def append_pydantic_messages(self, messages: List[Any]):
        """
        ### append_pydantic_messages
        **Description :** Ajoute des messages au format PydanticAI dans le store.
        **Paramètres :**
        - `messages` (List[Any]) : Messages PydanticAI à ajouter.
        """
        for msg in messages:
            # Conversion selon le type de message PydanticAI
            if hasattr(msg, 'role') and hasattr(msg, 'parts'):
                if msg.role == 'user':
                    for part in msg.parts:
                        if hasattr(part, 'content'):
                            self.save_user_message(part.content)
                elif msg.role == 'model':
                    for part in msg.parts:
                        if hasattr(part, 'content'):
                            self.save_assistant_message(part.content)
                        elif hasattr(part, 'tool_name'):
                            # Stockage temporaire de l'appel d'outil
                            pass
                elif msg.role == 'tool-return':
                    # Gérer le retour d'outil
                    pass

    # Méthodes de compatibilité pour l'interface Haystack existante
    def save(self, messages):
        """
        ### save
        **Description :** Sauvegarde une liste de messages (compatibilité Haystack).
        **Paramètres :**
        - `messages` : Liste de messages à sauvegarder.
        """
        # Vider le fichier et réécrire tout
        with open(self.filepath, "w", encoding="utf-8") as f:
            for msg in messages:
                if hasattr(msg, 'role') and hasattr(msg, 'text'):
                    # Format Haystack ChatMessage
                    role = msg.role.value if hasattr(msg.role, 'value') else str(msg.role)
                    message_data = {
                        "role": role,
                        "content": msg.text,
                        "timestamp": self._get_timestamp()
                    }
                    f.write(json.dumps(message_data, ensure_ascii=False) + "\n")
                elif isinstance(msg, dict):
                    # Format dict direct
                    f.write(json.dumps(msg, ensure_ascii=False) + "\n")
        
        # Recharger les messages
        self._load_messages()
        log_debug("Messages sauvegardés (compatibilité Haystack)", action="save_haystack_messages", count=len(messages))
