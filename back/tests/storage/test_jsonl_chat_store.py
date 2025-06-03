import tempfile
import os
from haystack.dataclasses import ChatMessage, ChatRole
from back.storage.jsonl_chat_store import JsonlChatMessageStore


class TestJsonlChatMessageStore:
    """
    ### TestJsonlChatMessageStore
    **Description :** Tests unitaires pour la classe JsonlChatMessageStore.
    """

    def test_init_creates_file(self):
        """
        ### test_init_creates_file
        **Description :** Teste que l'initialisation crée le fichier et le répertoire.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = JsonlChatMessageStore(filepath)
            
            assert os.path.exists(filepath)
            assert store.filepath == filepath

    def test_save_and_load_messages(self):
        """
        ### test_save_and_load_messages
        **Description :** Teste la sauvegarde et le chargement des messages.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = JsonlChatMessageStore(filepath)
            
            # Créer des messages de test
            messages = [
                ChatMessage.from_user("Hello!"),
                ChatMessage.from_assistant("Hi there!"),
                ChatMessage.from_system("System message"),
                ChatMessage.from_tool("Tool result", origin="test_tool")
            ]
            
            # Sauvegarder
            store.save(messages)
            
            # Charger
            loaded_messages = store.load()
            
            assert len(loaded_messages) == 4
            assert loaded_messages[0].text == "Hello!"
            assert loaded_messages[1].text == "Hi there!"
            assert loaded_messages[2].text == "System message"
            assert loaded_messages[3].tool_call_result.result == "Tool result"

    def test_skip_empty_messages_on_save(self):
        """
        ### test_skip_empty_messages_on_save
        **Description :** Teste que les messages vides sont ignorés lors de la sauvegarde.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = JsonlChatMessageStore(filepath)
            
            # Créer des messages incluant des messages vides
            valid_message = ChatMessage.from_user("Valid message")
            empty_message = ChatMessage.from_user("")
            none_message = ChatMessage.from_user(None)
            
            messages = [valid_message, empty_message, none_message]
            
            # Sauvegarder
            store.save(messages)
            
            # Charger
            loaded_messages = store.load()
            
            # Seul le message valide doit être chargé
            assert len(loaded_messages) == 1
            assert loaded_messages[0].text == "Valid message"

    def test_skip_empty_messages_on_load(self):
        """
        ### test_skip_empty_messages_on_load
        **Description :** Teste que les messages vides sont ignorés lors du chargement.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = JsonlChatMessageStore(filepath)
            
            # Écrire manuellement des données incluant des messages vides
            with open(filepath, "w") as f:
                f.write('{"role": "user", "content": "Valid message"}\n')
                f.write('{"role": "user", "content": ""}\n')  # Message vide
                f.write('{"role": "user", "content": null}\n')  # Contenu null
                f.write('{"role": "assistant", "content": "Another valid message"}\n')
            
            # Charger
            loaded_messages = store.load()
            
            # Seuls les messages valides doivent être chargés
            assert len(loaded_messages) == 2
            assert loaded_messages[0].text == "Valid message"
            assert loaded_messages[1].text == "Another valid message"

    def test_tool_message_with_origin(self):
        """
        ### test_tool_message_with_origin
        **Description :** Teste la sauvegarde et le chargement d'un message tool avec un origin de type chaîne (str).
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = JsonlChatMessageStore(filepath)
            # Créer un message tool avec origin (str)
            tool_message = ChatMessage.from_tool("Tool executed successfully", origin="skill_check_tool")
            messages = [tool_message]
            # Sauvegarder
            store.save(messages)
            # Charger
            loaded_messages = store.load()
            assert len(loaded_messages) == 1
            assert loaded_messages[0].tool_call_result.result == "Tool executed successfully"
            # Vérifier que l'origin est bien la chaîne attendue
            assert loaded_messages[0].tool_call_result.origin == "skill_check_tool"

    def test_malformed_json_handling(self):
        """
        ### test_malformed_json_handling
        **Description :** Teste la gestion des JSON malformés lors du chargement.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = JsonlChatMessageStore(filepath)
            
            # Écrire des données incluant du JSON malformé
            with open(filepath, "w") as f:
                f.write('{"role": "user", "content": "Valid message"}\n')
                f.write('{"invalid": "json", "missing": "role"}\n')  # JSON invalide
                f.write('not json at all\n')  # Pas du JSON
                f.write('{"role": "assistant", "content": "Another valid message"}\n')
            
            # Charger - ne doit pas lever d'exception
            loaded_messages = store.load()
            
            # Seuls les messages valides doivent être chargés
            assert len(loaded_messages) == 2
            assert loaded_messages[0].text == "Valid message"
            assert loaded_messages[1].text == "Another valid message"
