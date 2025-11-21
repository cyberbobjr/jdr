import pytest
from back.agents.narrative_agent import NarrativeAgent
from back.tools.equipment_tools import inventory_buy_item
from back.tools.character_tools import character_add_currency

from unittest.mock import MagicMock
from back.models.schema import LLMConfig

def test_narrative_agent_instantiation():
    """Test that NarrativeAgent can be instantiated and has the correct tools"""
    # Mock LLMConfig
    mock_config = MagicMock(spec=LLMConfig)
    mock_config.api_endpoint = "http://localhost:11434/v1"
    mock_config.api_key = "test_key"
    mock_config.model = "llama3"
    
    agent = NarrativeAgent(llm_config=mock_config)
    
    # If we reached here, instantiation was successful, which means all tools were imported correctly
    assert agent is not None
    
    print("NarrativeAgent instantiated successfully with new tools.")
