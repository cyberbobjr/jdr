import unittest
from back.tools.combat_tools import roll_initiative, perform_attack, resolve_attack

class TestCombatTools(unittest.TestCase):

    def test_roll_initiative_tool(self):
        input_data = {"characters": [
            {"name": "Hero", "initiative": 15},
            {"name": "Villain", "initiative": 10}
        ]}
        result = roll_initiative.invoke(**input_data)
        self.assertEqual(len(result), 2)
        self.assertGreaterEqual(result[0]['initiative'], result[1]['initiative'])

    def test_perform_attack_tool(self):
        input_data = {"dice": "1d20"}
        result = perform_attack.invoke(**input_data)
        self.assertGreaterEqual(result, 1)
        self.assertLessEqual(result, 20)

    def test_resolve_attack_tool(self):
        input_data = {"attack_roll": 15, "defense_roll": 10}
        result = resolve_attack.invoke(**input_data)
        self.assertTrue(result)

        input_data = {"attack_roll": 5, "defense_roll": 10}
        result = resolve_attack.invoke(**input_data)
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
