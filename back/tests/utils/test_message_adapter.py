from back.utils.message_adapter import extract_message_text

class DummyToolResult:
    def __init__(self, result, origin):
        self.result = result
        self.origin = origin

class DummyToolMessage:
    def __init__(self, result, origin):
        self.role = 'tool'
        self.tool_call_results = [DummyToolResult(result, origin)]

class DummyUserMessage:
    def __init__(self, text):
        self.role = 'user'
        self.text = text

class DummyAssistantMessage:
    def __init__(self, text):
        self.role = 'assistant'
        self.text = text

def test_extract_message_text_user():
    msg = DummyUserMessage("Bonjour !")
    data = extract_message_text(msg)
    assert data["role"] == "user"
    assert data["content"] == "Bonjour !"

def test_extract_message_text_assistant():
    msg = DummyAssistantMessage("Salut, aventurier !")
    data = extract_message_text(msg)
    assert data["role"] == "assistant"
    assert data["content"] == "Salut, aventurier !"

def test_extract_message_text_tool():
    msg = DummyToolMessage("Résultat du tool", "combat_tool")
    data = extract_message_text(msg)
    assert data["role"] == "tool"
    assert data["content"] == "Résultat du tool"
    assert data["origin"] == "combat_tool"

def test_extract_message_text_tool_result_not_serializable():
    class NotSerializable:
        def __str__(self):
            return "not_serializable_object"
    msg = DummyToolMessage(NotSerializable(), "test_tool")
    data = extract_message_text(msg)
    # On attend que le champ content soit converti en str
    assert data["role"] == "tool"
    assert isinstance(data["content"], str)
    assert data["origin"] == "test_tool"
