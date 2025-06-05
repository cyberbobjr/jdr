"""
Tests unitaires pour le PydanticJsonlStore.
Validation de la compatibilité avec l'agent PydanticAI.
"""

import tempfile
import os
from back.storage.pydantic_jsonl_store import PydanticJsonlStore


class TestPydanticJsonlStore:
    """
    ### TestPydanticJsonlStore
    **Description :** Tests unitaires pour la classe PydanticJsonlStore.
    """

    def test_init_creates_file(self):
        """
        ### test_init_creates_file
        **Description :** Teste que l'initialisation crée le fichier et le répertoire.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = PydanticJsonlStore(filepath)
            
            assert os.path.exists(filepath)
            assert store.filepath == filepath

    def test_save_and_load_user_message(self):
        """
        ### test_save_and_load_user_message
        **Description :** Teste la sauvegarde et le chargement des messages utilisateur.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = PydanticJsonlStore(filepath)
            
            # Sauvegarder un message utilisateur
            user_message = "Bonjour, je veux commencer l'aventure!"
            store.save_user_message(user_message)
            
            # Charger les messages
            messages = store.get_messages()
            
            assert len(messages) == 1
            assert messages[0]["role"] == "user"
            assert messages[0]["content"] == user_message
            assert "timestamp" in messages[0]

    def test_save_and_load_assistant_message(self):
        """
        ### test_save_and_load_assistant_message
        **Description :** Teste la sauvegarde et le chargement des messages assistant.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = PydanticJsonlStore(filepath)
            
            # Sauvegarder un message assistant
            assistant_message = "Bienvenue dans les Terres du Milieu! Votre aventure commence..."
            store.save_assistant_message(assistant_message)
            
            # Charger les messages
            messages = store.get_messages()
            
            assert len(messages) == 1
            assert messages[0]["role"] == "assistant"
            assert messages[0]["content"] == assistant_message
            assert "timestamp" in messages[0]

    def test_save_tool_message(self):
        """
        ### test_save_tool_message
        **Description :** Teste la sauvegarde des appels d'outils.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = PydanticJsonlStore(filepath)
            
            # Sauvegarder un appel d'outil
            tool_name = "apply_xp_to_character"
            args = {"character_id": "test123", "xp_amount": 100}
            result = {"success": True, "new_xp": 1100}
            
            store.save_tool_message(tool_name, args, result)
            
            # Charger les messages
            messages = store.get_messages()
            
            assert len(messages) == 1
            assert messages[0]["role"] == "tool"
            assert messages[0]["tool_name"] == tool_name
            assert messages[0]["args"] == args
            assert messages[0]["result"] == result
            assert "[TOOL_CALL]" in messages[0]["content"]
            assert "timestamp" in messages[0]

    def test_conversation_flow(self):
        """
        ### test_conversation_flow
        **Description :** Teste un flux de conversation complet avec différents types de messages.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = PydanticJsonlStore(filepath)
            
            # Simuler une conversation
            store.save_user_message("Je veux attaquer l'orc!")
            store.save_tool_message("perform_attack", {"target": "orc", "weapon": "épée"}, {"hit": True, "damage": 8})
            store.save_assistant_message("Votre attaque touche! L'orc prend 8 points de dégâts.")
            store.save_user_message("Est-ce qu'il est mort?")
            store.save_assistant_message("L'orc s'effondre, vaincu par votre coup mortel!")
            
            # Vérifier le flux complet
            messages = store.get_messages()
            
            assert len(messages) == 5
            assert messages[0]["role"] == "user"
            assert messages[1]["role"] == "tool"
            assert messages[2]["role"] == "assistant"
            assert messages[3]["role"] == "user"
            assert messages[4]["role"] == "assistant"

    def test_persistence_across_instances(self):
        """
        ### test_persistence_across_instances
        **Description :** Teste que les messages persistent entre différentes instances du store.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            
            # Première instance - sauvegarder des messages
            store1 = PydanticJsonlStore(filepath)
            store1.save_user_message("Message 1")
            store1.save_assistant_message("Réponse 1")
            
            # Deuxième instance - doit charger les messages existants
            store2 = PydanticJsonlStore(filepath)
            messages = store2.get_messages()
            
            assert len(messages) == 2
            assert messages[0]["content"] == "Message 1"
            assert messages[1]["content"] == "Réponse 1"
            
            # Ajouter un nouveau message avec la deuxième instance
            store2.save_user_message("Message 2")
            
            # Troisième instance - doit avoir tous les messages
            store3 = PydanticJsonlStore(filepath)
            messages = store3.get_messages()
            
            assert len(messages) == 3
            assert messages[2]["content"] == "Message 2"

    def test_clear_store(self):
        """
        ### test_clear_store
        **Description :** Teste la méthode de nettoyage du store.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = PydanticJsonlStore(filepath)
            
            # Ajouter des messages
            store.save_user_message("Message à supprimer")
            store.save_assistant_message("Réponse à supprimer")
            
            assert len(store.get_messages()) == 2
            
            # Nettoyer le store
            store.clear()
            
            assert len(store.get_messages()) == 0
            
            # Vérifier que le fichier est vide
            with open(filepath, "r") as f:
                content = f.read().strip()
                assert content == ""

    def test_haystack_compatibility(self):
        """
        ### test_haystack_compatibility
        **Description :** Teste la compatibilité avec l'interface Haystack (méthode save).
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = PydanticJsonlStore(filepath)
            
            # Simuler des messages format dict (comme ceux retournés par Haystack)
            messages = [
                {"role": "user", "content": "Test message 1"},
                {"role": "assistant", "content": "Test response 1"},
                {"role": "user", "content": "Test message 2"}
            ]
            
            # Utiliser la méthode save pour compatibilité
            store.save(messages)
            
            # Vérifier que les messages sont correctement chargés
            loaded_messages = store.get_messages()
            
            assert len(loaded_messages) == 3
            assert loaded_messages[0]["content"] == "Test message 1"
            assert loaded_messages[1]["content"] == "Test response 1"
            assert loaded_messages[2]["content"] == "Test message 2"

    def test_load_method_compatibility(self):
        """
        ### test_load_method_compatibility
        **Description :** Teste la méthode load pour compatibilité avec l'interface Haystack.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "test_session.jsonl")
            store = PydanticJsonlStore(filepath)
            
            # Ajouter des messages
            store.save_user_message("Test load")
            store.save_assistant_message("Test response")
            
            # Tester la méthode load (compatibilité Haystack)
            loaded_messages = store.load()
            
            assert len(loaded_messages) == 2
            assert loaded_messages[0]["content"] == "Test load"
            assert loaded_messages[1]["content"] == "Test response"
            
            # Vérifier que load() et get_messages() retournent la même chose
            get_messages_result = store.get_messages()
            assert loaded_messages == get_messages_result
