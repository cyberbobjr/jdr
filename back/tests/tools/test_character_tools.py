import os
import json
import shutil
import pytest
from uuid import uuid4
from back.tools.character_tools import character_apply_xp_tool, character_add_gold_tool, character_take_damage_tool

CHARACTERS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data/characters'))

def create_test_character(player_id, hp=100, xp=0, gold=0):
    os.makedirs(CHARACTERS_DIR, exist_ok=True)
    filepath = os.path.join(CHARACTERS_DIR, f"{player_id}.json")
    data = {"state": {"id": str(player_id), "hp": hp, "xp": xp, "gold": gold}}
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filepath

def remove_test_character(player_id):
    filepath = os.path.join(CHARACTERS_DIR, f"{player_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)

@pytest.mark.asyncio
async def test_character_apply_xp():
    player_id = uuid4()
    create_test_character(player_id)
    xp = 100
    result = character_apply_xp_tool.function(player_id=str(player_id), xp=xp)
    assert "xp" in result or "experience" in result
    assert result["xp"] >= 100
    remove_test_character(player_id)

@pytest.mark.asyncio
async def test_character_add_gold():
    player_id = uuid4()
    create_test_character(player_id)
    gold = 50
    result = character_add_gold_tool.function(player_id=str(player_id), gold=gold)
    assert "gold" in result or "money" in result
    assert result["gold"] >= 50
    remove_test_character(player_id)

@pytest.mark.asyncio
async def test_character_take_damage():
    player_id = uuid4()
    create_test_character(player_id, hp=100)
    amount = 10
    result = character_take_damage_tool.function(player_id=str(player_id), amount=amount)
    assert ("hp" in result and result["hp"] == 90) or ("health" in result and result["health"] == 90) or ("pv" in result and result["pv"] == 90)
    remove_test_character(player_id)
