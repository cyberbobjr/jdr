from back.services.combat_service import CombatService
from back.models.domain.combat_state import CombatState

def make_participants():
    return [
        {"id": "p1", "name": "Alice", "initiative": 15, "hp": 20, "camp": "joueur"},
        {"id": "p2", "name": "Bob", "initiative": 10, "hp": 18, "camp": "joueur"},
        {"id": "e1", "name": "Goblin", "initiative": 12, "hp": 10, "camp": "adversaire"}
    ]

def test_start_combat():
    service = CombatService()
    participants = make_participants()
    state = service.start_combat(participants)
    assert isinstance(state, CombatState)
    assert state.status == "en_cours"
    assert len(state.participants) == 3
    assert state.initiative_order == ["p1", "e1", "p2"]

def test_roll_initiative():
    service = CombatService()
    participants = make_participants()
    state = service.start_combat(participants)
    state = service.roll_initiative(state)
    assert state.initiative_order == ["p1", "e1", "p2"]

def test_perform_attack_and_apply_damage():
    service = CombatService()
    participants = make_participants()
    state = service.start_combat(participants)
    state = service.perform_attack(state, "p1", "e1", 8)
    state = service.apply_damage(state, "e1", 8)
    goblin = next(p for p in state.participants if p["id"] == "e1")
    assert goblin["hp"] == 2

def test_end_turn_and_round():
    service = CombatService()
    participants = make_participants()
    state = service.start_combat(participants)
    turn0 = state.current_turn
    state = service.end_turn(state)
    assert state.current_turn == (turn0 + 1) % 3
    # Simule un tour complet
    for _ in range(2):
        state = service.end_turn(state)
    assert state.round == 2

def test_check_combat_end_and_end_combat():
    service = CombatService()
    participants = make_participants()
    state = service.start_combat(participants)
    # Simule la mort de tous les adversaires
    for p in state.participants:
        if p["camp"] == "adversaire":
            p["hp"] = 0
    assert service.check_combat_end(state) is True
    state = service.end_combat(state, reason="victoire")
    assert state.status == "termine"
    assert state.end_reason == "victoire"

def test_get_combat_summary():
    service = CombatService()
    participants = make_participants()
    state = service.start_combat(participants)
    summary = service.get_combat_summary(state)
    assert summary["combat_id"] == state.combat_id
    assert summary["status"] == state.status
