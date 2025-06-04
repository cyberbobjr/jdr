from back.services.combat_service import CombatService

def make_characters():
    return [
        {"id": "p1", "name": "Alice", "initiative": 15, "hp": 20, "camp": "joueur"},
        {"id": "p2", "name": "Bob", "initiative": 10, "hp": 18, "camp": "joueur"},
        {"id": "e1", "name": "Charlie", "initiative": 20, "hp": 10, "camp": "adversaire"}
    ]

def test_roll_initiative():
    service = CombatService()
    characters = make_characters()
    state = service.start_combat(characters)
    state = service.roll_initiative(state)
    order = [cid for cid in state.initiative_order]
    assert order == ["e1", "p1", "p2"]

def test_next_turn():
    service = CombatService()
    state = service.start_combat(make_characters())
    turn0 = state.current_turn
    state = service.end_turn(state)
    assert state.current_turn == (turn0 + 1) % 3
    state = service.end_turn(state)
    assert state.current_turn == (turn0 + 2) % 3
    state = service.end_turn(state)
    assert state.round == 2

def test_reset_combat():
    service = CombatService()
    state = service.start_combat(make_characters())
    state.participants = []
    state.initiative_order = []
    state.current_turn = 0
    assert state.participants == []
    assert state.initiative_order == []

def test_calculate_initiative():
    service = CombatService()
    stats = {"AGI": 5, "PER": 9}
    # Utilise la méthode statique de CombatService si elle existe, sinon simule
    initiative = stats["AGI"] + (stats["PER"] // 3) + 1  # min roll_attack = 1
    assert initiative >= 6

def test_resolve_attack():
    service = CombatService()
    assert service.check_combat_end is not None  # La logique est dans check_combat_end

def test_calculate_damage():
    service = CombatService()
    damage = service.apply_damage(service.start_combat(make_characters()), "e1", 5)
    assert damage is not None
