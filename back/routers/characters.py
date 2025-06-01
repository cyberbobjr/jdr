from fastapi import APIRouter
from back.services.character_service import CharacterService
from back.models.schema import CharacterList
from back.utils.logger import log_debug

router = APIRouter()

@router.get("/example")
async def example_endpoint():
    log_debug("Appel endpoint characters/example_endpoint")
    return {"message": "Example endpoint for characters"}

@router.get("/", response_model=CharacterList)
def list_characters():
    """
    Récupère la liste de tous les personnages disponibles.

    Returns:
        CharacterList: Une liste de personnages disponibles.
    """
    log_debug("Appel endpoint characters/list_characters")
    characters = CharacterService.get_all_characters()
    return {"characters": characters}

# Endpoints REST (FastAPI "router")
