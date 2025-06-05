import tempfile
import os
from back.storage.jsonl_chat_store import JsonlChatMessageStore

class DummyToolResult:
    def __init__(self, result, origin=None):
        self.result = result
        self.origin = origin

class DummyToolMessage:
    def __init__(self, result, origin=None):
        self.role = type('Role', (), {'value': 'tool'})()
        self.tool_call_results = [DummyToolResult(result, origin)]

class DummyAssistantMessage:
    def __init__(self, text):
        self.role = type('Role', (), {'value': 'assistant'})()
        self.text = text

class DummyUserMessage:
    def __init__(self, text):
        self.role = type('Role', (), {'value': 'user'})()
        self.text = text

def test_save_and_load_with_adapter():
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test.jsonl")
        store = JsonlChatMessageStore(filepath)
        # Créer des messages variés
        user_msg = DummyUserMessage("Bonjour !")
        assistant_msg = DummyAssistantMessage("Salut, aventurier !")
        tool_msg = DummyToolMessage("Résultat du tool", origin="combat_tool")
        messages = [user_msg, assistant_msg, tool_msg]
        # Sauvegarder
        store.save(messages)
        # Charger
        loaded = store.load()
        # Vérifier le contenu
        assert len(loaded) == 3
        assert hasattr(loaded[0], "text") and loaded[0].text == "Bonjour !"
        assert hasattr(loaded[1], "text") and loaded[1].text == "Salut, aventurier !"
        # Pour le message tool, vérifier le résultat dans tool_call_results ou _content
        tool_loaded = loaded[2]
        # Haystack stocke le résultat dans _content ou tool_call_results
        result = None
        if hasattr(tool_loaded, "tool_call_results") and tool_loaded.tool_call_results:
            result = tool_loaded.tool_call_results[0].result
        elif hasattr(tool_loaded, "_content") and tool_loaded._content:
            # _content est une liste de ToolCallResult
            result = tool_loaded._content[0].result
        assert result == "Résultat du tool"
        # Vérifier l'origine si présente
        origin = None
        if hasattr(tool_loaded, "origin"):
            origin = tool_loaded.origin
        elif hasattr(tool_loaded, "_content") and tool_loaded._content:
            origin = getattr(tool_loaded._content[0], "origin", None)
        assert origin == "combat_tool"
