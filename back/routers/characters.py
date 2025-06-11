from fastapi import APIRouter
from back.services.character_service import CharacterService
from back.models.schema import CharacterList
from back.utils.logger import log_debug

router = APIRouter()

@router.get("/", response_model=CharacterList)
def list_characters():
    """
    Récupère la liste de tous les personnages disponibles dans le système.

    Cet endpoint permet d'obtenir tous les personnages créés et leurs informations
    détaillées (caractéristiques, compétences, équipement, etc.).

    Returns:
        CharacterList: Une liste contenant tous les personnages disponibles
        
    Example Response:
        ```json
        {
            "characters": [
                {
                    "id": "d7763165-4c03-4c8d-9bc6-6a2568b79eb3",
                    "name": "Aragorn",
                    "race": "Humain",
                    "culture": "Gondor",
                    "profession": "Rôdeur",
                    "caracteristiques": {
                        "Force": 85,
                        "Constitution": 80,
                        "Agilité": 70,
                        "Rapidité": 75,
                        "Volonté": 80,
                        "Raisonnement": 65,
                        "Intuition": 75,
                        "Présence": 70
                    },
                    "competences": {
                        "Perception": 60,
                        "Combat": 75,
                        "Survie": 55,
                        "Nature": 65
                    },
                    "hp": 85,
                    "inventory": [
                        {
                            "id": "sword_001",
                            "name": "Épée longue",
                            "weight": 1.5,
                            "base_value": 150.0
                        }
                    ],
                    "equipment": ["Épée longue", "Armure de cuir"],
                    "spells": [],
                    "equipment_summary": {
                        "total_weight": 8.5,
                        "total_value": 500.0,
                        "remaining_gold": 200.0
                    },
                    "culture_bonuses": {
                        "Combat": 5,
                        "Influence": 3
                    }
                }
            ]
        }
        ```

    Raises:
        500: Erreur interne du serveur lors de la récupération des personnages
    """
    log_debug("Appel endpoint characters/list_characters")
    characters = CharacterService.get_all_characters()
    return {"characters": characters}

# Endpoints REST (FastAPI "router")
