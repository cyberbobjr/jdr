"""
Consolidated tests for combat-related tools.
Combines tests from:
- test_combat_tools.py
- combat_tools_test.py  
- test_calculate_damage.py
"""

import unittest
import sys
from pathlib import Path

# Configuration des chemins pour les imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from back.tools.combat_tools import (
    roll_initiative_tool, 
    perform_attack_tool, 
    resolve_attack_tool,
    calculate_damage_tool
)
from back.utils.dice import roll_attack


class TestCombatTools(unittest.TestCase):
    """Test suite for all combat-related tools"""
    
    def test_roll_attack_basic(self):
        """Test basic roll_attack functionality"""
        result = roll_attack("1d20")
        assert 1 <= result <= 20

    def test_roll_initiative_tool(self):
        """Test initiative rolling with character data"""
        class MockContext:
            def __init__(self):
                self.deps = None  # Don't need a real SessionService for this test
        
        ctx = MockContext()
        characters = [
            {"name": "Hero", "agilite": 15, "id": "char1"},
            {"name": "Villain", "agilite": 10, "id": "char2"}
        ]
        result = roll_initiative_tool(ctx, characters)
        self.assertEqual(len(result), 2)
        # Check that both characters are in the result
        names = [char["name"] for char in result]
        self.assertIn("Hero", names)
        self.assertIn("Villain", names)

    def test_perform_attack_tool(self):
        """Test attack performance with dice rolls"""
        class MockContext:
            def __init__(self):
                self.deps = None
        
        ctx = MockContext()
        result = perform_attack_tool(ctx, "1d20")
        self.assertGreaterEqual(result, 1)
        self.assertLessEqual(result, 20)

    def test_resolve_attack_success(self):
        """Test attack resolution when attack succeeds"""
        class MockContext:
            def __init__(self):
                self.deps = None
        
        ctx = MockContext()
        result = resolve_attack_tool(ctx, 15, 10)
        self.assertTrue(result)

    def test_resolve_attack_failure(self):
        """Test attack resolution when attack fails"""
        class MockContext:
            def __init__(self):
                self.deps = None
        
        ctx = MockContext()
        result = resolve_attack_tool(ctx, 5, 10)
        self.assertFalse(result)

    def test_calculate_damage_positive_bonus(self):
        """Test damage calculation with positive bonus"""
        class MockContext:
            def __init__(self):
                self.deps = None
        
        ctx = MockContext()
        result = calculate_damage_tool(ctx, 10, 5)
        assert result == 15

    def test_calculate_damage_negative_bonus(self):
        """Test damage calculation with negative bonus (minimum 0)"""
        class MockContext:
            def __init__(self):
                self.deps = None
        
        ctx = MockContext()
        result = calculate_damage_tool(ctx, 10, -15)
        assert result == 0

    def test_calculate_damage_default_bonus(self):
        """Test damage calculation with default bonus"""
        class MockContext:
            def __init__(self):
                self.deps = None
        
        ctx = MockContext()
        result = calculate_damage_tool(ctx, 10)
        assert result == 10


if __name__ == "__main__":
    unittest.main()
