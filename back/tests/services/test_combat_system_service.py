"""Tests for CombatSystemService (obsolete).

Quarantined: original implementation removed from codebase. This test is skipped
to avoid failing the suite while legacy combat system is deprecated.
"""
import pytest

pytest.skip("combat_system_service module removed; test obsolete", allow_module_level=True)

from typing import Any, Dict, Optional, cast  # noqa: F401
from back.models.domain.combat_system_manager import CombatSystemManager  # type: ignore  # noqa: F401,E401
from back.services.combat_system_service import CombatSystemService  # type: ignore  # noqa: F401,E401


class DummyCombatSystemManager:
    """Minimal stub to avoid YAML I/O in tests."""

    def __init__(self) -> None:
        self.actions = {"strike": {"name": "Strike"}}
        self.difficulty_mods = {"easy": 10}

    def get_initiative_rules(self) -> Dict[str, Any]:
        return {"dice": "1d20"}

    def get_turn_structure(self) -> Dict[str, Any]:
        return {"phases": ["major", "minor"]}

    def get_all_actions(self) -> Dict[str, Dict[str, Any]]:
        return self.actions

    def get_action_by_id(self, action_id: str) -> Optional[Dict[str, Any]]:
        return self.actions.get(action_id)

    def get_difficulty_modifiers(self) -> Dict[str, int]:
        return self.difficulty_mods

    def get_difficulty_modifier(self, difficulty: str) -> int:
        return self.difficulty_mods.get(difficulty, 0)

    def get_damage_types(self) -> Dict[str, Dict[str, Any]]:
        return {"slash": {"description": "slashing"}}

    def get_armor_types(self) -> Dict[str, Dict[str, Any]]:
        return {"light": {"description": "light armor"}}

    def get_basic_mechanics(self) -> Dict[str, Any]:
        return {"attack_roll": {"formula": "1d20 + stat"}}

    def get_combat_modifiers(self) -> Dict[str, Any]:
        return {"flanking": {"bonus": 2}}


@pytest.fixture()
def service() -> CombatSystemService:
    """Provide a service wired to the dummy manager."""
    dummy = cast(CombatSystemManager, DummyCombatSystemManager())
    return CombatSystemService(data_manager=dummy)


def test_calculate_initiative_with_explicit_roll(service: CombatSystemService) -> None:
    result = service.calculate_initiative(agility_value=5, dice_roll=12)
    assert result == 17


def test_calculate_initiative_random_roll(monkeypatch: pytest.MonkeyPatch, service: CombatSystemService) -> None:
    monkeypatch.setattr("random.randint", lambda _a, _b: 8)
    result = service.calculate_initiative(agility_value=4)
    assert result == 12


def test_get_action_by_id(service: CombatSystemService) -> None:
    action = service.get_action_by_id("strike")
    assert action is not None
    assert action["name"] == "Strike"


def test_get_difficulty_modifier_default(service: CombatSystemService) -> None:
    assert service.get_difficulty_modifier("unknown") == 0
    assert service.get_difficulty_modifier("easy") == 10


def test_get_basic_mechanics_and_modifiers(service: CombatSystemService) -> None:
    assert "attack_roll" in service.get_basic_mechanics()
    assert "flanking" in service.get_combat_modifiers()
