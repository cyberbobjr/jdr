from fastapi import APIRouter
from back.services.combat_service import CombatService
from back.utils.logger import log_debug
from back.models.domain.combat_state import CombatState

router = APIRouter()
combat_service = CombatService()

@router.post("/attack")
async def attack_endpoint(attacker_id: str, target_id: str, attack_value: int, combat_state: dict):
    """
    Endpoint pour effectuer une attaque dans le nouveau système de combat.

    Parameters:
    - attacker_id (str): ID de l'attaquant.
    - target_id (str): ID de la cible.
    - attack_value (int): Valeur d'attaque.
    - combat_state (dict): Etat courant du combat (sérialisé).

    Returns:
    - dict: Etat du combat mis à jour.
    """
    log_debug("Appel endpoint combat/attack_endpoint", attacker_id=attacker_id, target_id=target_id, attack_value=attack_value)
    state = CombatState(**combat_state)
    state = combat_service.perform_attack(state, attacker_id, target_id, attack_value)
    return {"combat_state": state.dict()}

# Endpoints REST (FastAPI "router")
