"""Combat system service wrapping combat_system.yaml data access.

This service keeps business logic (initiative rolls, rules lookup) outside of the
Pydantic domain layer by relying on the CombatSystemManager for YAML loading.
"""
from __future__ import annotations

import random
from typing import Any, Dict, Optional

from back.models.domain.combat_system_manager import CombatSystemManager


class CombatSystemService:
    """Provide combat-system lookups and calculations."""

    def __init__(self, data_manager: Optional[CombatSystemManager] = None) -> None:
        """
        Initialize service dependencies.

        **Parameters:**
        - `data_manager` (Optional[CombatSystemManager]): custom manager, useful for tests.
        """
        self._data_manager = data_manager or CombatSystemManager()

    @property
    def data(self) -> CombatSystemManager:
        """Expose the underlying manager for internal use."""
        return self._data_manager

    def get_initiative_rules(self) -> Dict[str, Any]:
        """Return initiative rules from YAML."""
        return self.data.get_initiative_rules()

    def get_turn_structure(self) -> Dict[str, Any]:
        """Return the combat turn structure."""
        return self.data.get_turn_structure()

    def get_all_actions(self) -> Dict[str, Dict[str, Any]]:
        """Return every combat action definition."""
        return self.data.get_all_actions()

    def get_action_by_id(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Return a single combat action by id."""
        return self.data.get_action_by_id(action_id)

    def get_difficulty_modifiers(self) -> Dict[str, int]:
        """Return the mapping of difficulty modifiers."""
        return self.data.get_difficulty_modifiers()

    def get_difficulty_modifier(self, difficulty: str) -> int:
        """Return the modifier for a specific difficulty level."""
        return self.data.get_difficulty_modifier(difficulty)

    def get_damage_types(self) -> Dict[str, Dict[str, Any]]:
        """Return available damage types."""
        return self.data.get_damage_types()

    def get_armor_types(self) -> Dict[str, Dict[str, Any]]:
        """Return available armor types."""
        return self.data.get_armor_types()

    def get_basic_mechanics(self) -> Dict[str, Any]:
        """Return attack, damage, and defense formulas."""
        return self.data.get_basic_mechanics()

    def get_combat_modifiers(self) -> Dict[str, Any]:
        """Return situational modifiers affecting rolls."""
        return self.data.get_combat_modifiers()

    def calculate_initiative(self, agility_value: int, dice_roll: Optional[int] = None) -> int:
        """
        Calculate initiative as `agility_value + dice_roll`.

        The dice roll is generated automatically when not supplied, which keeps
        randomness inside the service layer and outside the domain models.
        """
        roll = dice_roll if dice_roll is not None else random.randint(1, 20)
        return agility_value + roll
