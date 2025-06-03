from fastapi import APIRouter
from back.models.domain.combat_manager import CombatManager
from back.utils.logger import log_debug

router = APIRouter()
combat_manager = CombatManager()

@router.post("/attack")
async def attack_endpoint(dice: str):
    """
    Endpoint pour effectuer un jet d'attaque.

    Parameters:
    - dice (str): La notation des dés à lancer (ex: "1d20").

    Returns:
    - dict: Le résultat du jet d'attaque.
    """
    log_debug("Appel endpoint combat/attack_endpoint", dice=dice)
    result = combat_manager.perform_attack(dice)
    return {"result": result}

# Endpoints REST (FastAPI "router")
