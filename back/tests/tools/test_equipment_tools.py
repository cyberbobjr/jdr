import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from pydantic_ai import RunContext
from pydantic_ai.usage import RunUsage
from back.services.game_session_service import GameSessionService
from back.tools.equipment_tools import inventory_add_item, inventory_remove_item
from back.models.domain.character import Character

@pytest.fixture
def mock_session_service():
    service = MagicMock(spec=GameSessionService)
    service.character_id = str(uuid4())
    service.character_data = MagicMock(spec=Character)
    service.equipment_service = MagicMock()
    return service

@pytest.fixture
def mock_run_context(mock_session_service):
    mock_model = MagicMock()
    usage = RunUsage(requests=1)
    return RunContext(deps=mock_session_service, retry=0, tool_name="test_tool", model=mock_model, usage=usage)

def test_inventory_add_item(mock_run_context):
    mock_updated_character = MagicMock(spec=Character)
    mock_item = MagicMock()
    mock_item.item_id = "sword"
    mock_updated_character.inventory = [mock_item]
    
    initial_character_data = mock_run_context.deps.character_data
    mock_run_context.deps.equipment_service.add_item.return_value = mock_updated_character
    
    result = inventory_add_item(mock_run_context, "sword", 1)
    
    mock_run_context.deps.equipment_service.add_item.assert_called_once_with(
        initial_character_data, item_id="sword", quantity=1
    )
    assert result["message"] == "Added 1 x sword"
    assert result["inventory"] == ["sword"]
    assert mock_run_context.deps.character_data == mock_updated_character

def test_inventory_add_item_service_unavailable(mock_run_context):
    mock_run_context.deps.equipment_service = None
    
    result = inventory_add_item(mock_run_context, "sword", 1)
    
    assert result["error"] == "Equipment service not available"

def test_inventory_remove_item(mock_run_context):
    mock_updated_character = MagicMock(spec=Character)
    mock_updated_character.inventory = []
    
    initial_character_data = mock_run_context.deps.character_data
    mock_run_context.deps.equipment_service.remove_item.return_value = mock_updated_character
    
    result = inventory_remove_item(mock_run_context, "potion", 1)
    
    mock_run_context.deps.equipment_service.remove_item.assert_called_once_with(
        initial_character_data, item_id="potion", quantity=1
    )
    assert result["message"] == "Removed 1 x potion"
    assert result["inventory"] == []
    assert mock_run_context.deps.character_data == mock_updated_character

def test_inventory_remove_item_service_unavailable(mock_run_context):
    mock_run_context.deps.equipment_service = None
    
    result = inventory_remove_item(mock_run_context, "potion", 1)
    
    assert result["error"] == "Equipment service not available"
