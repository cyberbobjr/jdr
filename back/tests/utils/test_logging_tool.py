import pytest
import tempfile
import os
from unittest.mock import Mock, MagicMock
from haystack.tools import Tool
from haystack.dataclasses import ChatMessage, ChatRole
from back.utils.logging_tool import LoggingTool, wrap_tools_with_logging
from back.storage.jsonl_chat_store import JsonlChatMessageStore


class TestLoggingTool:
    """
    ### TestLoggingTool
    **Description :** Tests unitaires pour la classe LoggingTool.
    """

    def test_logging_tool_preserves_original_properties(self):
        """
        ### test_logging_tool_preserves_original_properties
        **Description :** Teste que LoggingTool préserve les propriétés de l'outil original.
        """
        # Créer un outil de test
        def test_function(x: int, y: str) -> str:
            return f"Result: {x} - {y}"
        
        original_tool = Tool(
            name="test_tool",
            description="A test tool",
            parameters={
                "type": "object",
                "properties": {
                    "x": {"type": "integer"},
                    "y": {"type": "string"}
                },
                "required": ["x", "y"]
            },
            function=test_function
        )
        
        # Envelopper avec LoggingTool
        wrapped_tool = LoggingTool(original_tool)
        
        # Vérifier que les propriétés sont préservées
        assert wrapped_tool.name == "test_tool"
        assert wrapped_tool.description == "A test tool"
        assert wrapped_tool.parameters == original_tool.parameters

    def test_logging_tool_function_execution(self):
        """
        ### test_logging_tool_function_execution
        **Description :** Teste que LoggingTool exécute correctement la fonction originale.
        """
        # Créer un outil de test
        def test_function(x: int, y: str) -> str:
            return f"Result: {x} - {y}"
        
        original_tool = Tool(
            name="test_tool",
            description="A test tool",
            parameters={},
            function=test_function
        )
        
        # Envelopper avec LoggingTool
        wrapped_tool = LoggingTool(original_tool)
        
        # Tester l'exécution
        result = wrapped_tool.function(x=42, y="hello")
        assert result == "Result: 42 - hello"

    def test_logging_tool_with_store_and_agent(self):
        """
        ### test_logging_tool_with_store_and_agent
        **Description :** Teste le logging avec store et agent.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer un store temporaire
            store_path = os.path.join(temp_dir, "test.jsonl")
            store = JsonlChatMessageStore(store_path)
            
            # Créer un agent mock
            agent = Mock()
            agent._chat_history = []
            
            # Créer un outil de test
            def test_function(value: str) -> str:
                return f"Processed: {value}"
            
            original_tool = Tool(
                name="test_tool",
                description="A test tool",
                parameters={},
                function=test_function
            )
            
            # Envelopper avec LoggingTool
            wrapped_tool = LoggingTool(original_tool, store=store, agent=agent)
            
            # Exécuter l'outil
            result = wrapped_tool.function(value="test")
            
            # Vérifier le résultat
            assert result == "Processed: test"
            
            # Vérifier que des messages ont été ajoutés à l'historique
            assert len(agent._chat_history) == 2  # Un pour l'appel, un pour le résultat            # Vérifier le contenu des messages
            call_message = agent._chat_history[0]
            result_message = agent._chat_history[1]
            
            assert call_message.role == ChatRole.TOOL
            assert "[TOOL_CALL] test_tool" in call_message.tool_call_results[0].result
            assert call_message.tool_call_results[0].origin == "test_tool"
            
            assert result_message.role == ChatRole.TOOL
            assert "[TOOL_RESULT] test_tool" in result_message.tool_call_results[0].result
            assert result_message.tool_call_results[0].origin == "test_tool"

    def test_logging_tool_error_handling(self):
        """
        ### test_logging_tool_error_handling
        **Description :** Teste la gestion des erreurs dans LoggingTool.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Créer un store temporaire
            store_path = os.path.join(temp_dir, "test.jsonl")
            store = JsonlChatMessageStore(store_path)
            
            # Créer un agent mock
            agent = Mock()
            agent._chat_history = []
            
            # Créer un outil qui génère une erreur
            def error_function():
                raise ValueError("Test error")
            
            original_tool = Tool(
                name="error_tool",
                description="An error tool",
                parameters={},
                function=error_function
            )
            
            # Envelopper avec LoggingTool
            wrapped_tool = LoggingTool(original_tool, store=store, agent=agent)
            
            # Tester l'exécution avec erreur
            with pytest.raises(ValueError, match="Test error"):
                wrapped_tool.function()
            
            # Vérifier que des messages ont été ajoutés même en cas d'erreur
            assert len(agent._chat_history) == 2  # Un pour l'appel, un pour l'erreur            # Vérifier le message d'erreur
            error_message = agent._chat_history[1]
            assert error_message.role == ChatRole.TOOL
            assert "[TOOL_ERROR] error_tool" in error_message.tool_call_results[0].result
            assert "Test error" in error_message.tool_call_results[0].result

    def test_wrap_tools_with_logging(self):
        """
        ### test_wrap_tools_with_logging
        **Description :** Teste la fonction wrap_tools_with_logging.
        """
        # Créer des outils de test
        def func1():
            return "result1"
        
        def func2():
            return "result2"
        
        tool1 = Tool(name="tool1", description="Tool 1", parameters={}, function=func1)
        tool2 = Tool(name="tool2", description="Tool 2", parameters={}, function=func2)
        
        tools = [tool1, tool2]
        
        # Envelopper avec logging
        wrapped_tools = wrap_tools_with_logging(tools)
        
        # Vérifier que tous les outils sont enveloppés
        assert len(wrapped_tools) == 2
        assert all(isinstance(tool, LoggingTool) for tool in wrapped_tools)
        
        # Vérifier que les noms sont préservés
        assert wrapped_tools[0].name == "tool1"
        assert wrapped_tools[1].name == "tool2"

    def test_wrap_tools_avoids_double_wrapping(self):
        """
        ### test_wrap_tools_avoids_double_wrapping
        **Description :** Teste que wrap_tools_with_logging évite le double enveloppement.
        """
        def func():
            return "result"
        
        # Créer un outil et l'envelopper une première fois
        original_tool = Tool(name="tool", description="Tool", parameters={}, function=func)
        already_wrapped = LoggingTool(original_tool)
        
        tools = [already_wrapped]
        
        # Tenter un second enveloppement
        wrapped_tools = wrap_tools_with_logging(tools)
        
        # Vérifier qu'il n'y a pas de double enveloppement
        assert len(wrapped_tools) == 1
        assert wrapped_tools[0] is already_wrapped  # Même instance
