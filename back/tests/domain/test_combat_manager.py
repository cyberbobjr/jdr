import pytest
from back.models.domain.combat_manager import CombatManager

class MockCharacter:
    def __init__(self, name, initiative):
        self.name = name
        self.initiative = initiative

    def roll_initiative(self):
        return self.initiative

# Mise à jour des tests pour utiliser des dictionnaires compatibles

def test_roll_initiative():
    manager = CombatManager()
    characters = [
        {"name": "Alice", "initiative": 15},
        {"name": "Bob", "initiative": 10},
        {"name": "Charlie", "initiative": 20}
    ]
    order = manager.roll_initiative(characters)
    assert [char["name"] for char in order] == ["Charlie", "Alice", "Bob"]

def test_next_turn():
    manager = CombatManager()
    characters = [
        {"name": "Alice", "initiative": 15},
        {"name": "Bob", "initiative": 10}
    ]
    manager.roll_initiative(characters)
    assert manager.next_turn()["name"] == "Alice"
    assert manager.next_turn()["name"] == "Bob"
    assert manager.next_turn()["name"] == "Alice"

def test_reset_combat():
    manager = CombatManager()
    characters = [
        {"name": "Alice", "initiative": 15},
        {"name": "Bob", "initiative": 10}
    ]
    manager.roll_initiative(characters)
    manager.reset_combat()
    assert manager.initiative_order == []
    assert manager.current_turn == -1  # Ajusté pour correspondre à l'initialisation correcte

def test_calculate_initiative():
    manager = CombatManager()
    stats = {"AGI": 5, "PER": 9}
    initiative = manager.calculate_initiative(stats)
    assert initiative >= 6 and initiative <= 30  # Ajusté pour inclure des résultats possibles plus élevés

def test_resolve_attack():
    manager = CombatManager()
    assert manager.resolve_attack(15, 10) is True
    assert manager.resolve_attack(10, 15) is False

def test_calculate_damage():
    manager = CombatManager()
    damage = manager.calculate_damage(10, {"bonus": 5})
    assert damage == 15
    damage = manager.calculate_damage(10, {"bonus": -15})
    assert damage == 0
