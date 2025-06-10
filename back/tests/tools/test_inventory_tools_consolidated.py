"""
Consolidated tests for inventory-related tools.
Combines tests from:
- test_inventory_tools.py
- test_inventory_remove_item.py
"""

import pytest
import sys
from pathlib import Path

# Configuration des chemins pour les imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from back.tools.inventory_tools import (
    inventory_add_item,
    inventory_remove_item
)
from back.services.session_service import SessionService


class TestInventoryTools:
    """Test suite for all inventory-related tools"""

    @pytest.fixture
    def mock_context(self):
        """Create a mock context for testing"""
        class MockContext:
            def __init__(self):
                # Use existing character ID
                self.deps = SessionService("test_inventory", "79e55c14-7dd5-4189-b209-ea88f6d067eb", "test_scenario")
        return MockContext()

    def test_inventory_add_item_basic(self, mock_context):
        """Test adding items to player inventory"""
        item_id = "test_sword"
        qty = 1

        result = inventory_add_item(mock_context, item_id, qty)
        
        assert isinstance(result, dict)
        assert "inventory" in result or "inventaire" in result or "message" in result

    def test_inventory_remove_item_basic(self, mock_context):
        """Test removing items from player inventory"""
        item_id = "test_potion"
        qty = 1
        
        # Add item first
        inventory_add_item(mock_context, item_id, qty)
        
        # Remove item
        result = inventory_remove_item(mock_context, item_id, qty)
        
        assert isinstance(result, dict)
        assert "inventory" in result or "inventaire" in result or "message" in result

    def test_inventory_add_multiple_quantities(self, mock_context):
        """Test adding multiple quantities of the same item"""
        item_id = "test_arrows"
        
        # Add first batch
        result1 = inventory_add_item(mock_context, item_id, 5)
        assert isinstance(result1, dict)
        
        # Add second batch
        result2 = inventory_add_item(mock_context, item_id, 3)
        assert isinstance(result2, dict)

    def test_inventory_remove_partial_quantity(self, mock_context):
        """Test removing partial quantity of items"""
        item_id = "test_gems"
        initial_qty = 10
        remove_qty = 3
        
        # Add items first
        inventory_add_item(mock_context, item_id, initial_qty)
        
        # Remove partial quantity
        result = inventory_remove_item(mock_context, item_id, remove_qty)
        
        assert isinstance(result, dict)

    def test_inventory_remove_more_than_available(self, mock_context):
        """Test removing more items than available"""
        item_id = "test_rare_item"
        initial_qty = 2
        remove_qty = 5
        
        # Add items first
        inventory_add_item(mock_context, item_id, initial_qty)
        
        # Try to remove more than available
        result = inventory_remove_item(mock_context, item_id, remove_qty)
        
        assert isinstance(result, dict)

    def test_inventory_operations_sequence(self, mock_context):
        """Test a sequence of inventory operations"""
        item_id = "test_sequence_item"
        
        # Add item
        add_result = inventory_add_item(mock_context, item_id, 5)
        assert isinstance(add_result, dict)
        
        # Remove some
        remove_result = inventory_remove_item(mock_context, item_id, 2)
        assert isinstance(remove_result, dict)
        
        # Add more
        add_result2 = inventory_add_item(mock_context, item_id, 3)
        assert isinstance(add_result2, dict)


if __name__ == "__main__":
    # Direct execution for quick tests
    import traceback
    
    print("🧪 Tests consolidés des outils d'inventaire")
    print("=" * 45)
    
    try:
        test = TestInventoryTools()
        session = SessionService("test_direct", "79e55c14-7dd5-4189-b209-ea88f6d067eb", "Test")
        
        class MockContext:
            def __init__(self):
                self.deps = session
        
        context = MockContext()
        
        test.test_inventory_add_item_basic(context)
        print("✅ Test ajout d'objet basique")
        
        test.test_inventory_remove_item_basic(context)
        print("✅ Test suppression d'objet basique")
        
        test.test_inventory_operations_sequence(context)
        print("✅ Test séquence d'opérations")
        
        print("\n🎉 TOUS LES TESTS D'INVENTAIRE PASSÉS !")
        
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        traceback.print_exc()
