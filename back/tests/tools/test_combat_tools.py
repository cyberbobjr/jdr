import pytest
from back.tools.combat_tools import roll_attack

def test_roll_attack():
    result = roll_attack("1d20")
    assert 1 <= result <= 20
