import pytest
from uuid import uuid4
from back.tools.combat_tools import calculate_damage

def test_calculate_damage_positive_bonus():
    result = calculate_damage.function(base_damage=10, bonus=5)
    assert result == 15

def test_calculate_damage_negative_bonus():
    result = calculate_damage.function(base_damage=10, bonus=-15)
    assert result == 0

def test_calculate_damage_default_bonus():
    result = calculate_damage.function(base_damage=10)
    assert result == 10
