from fastapi import APIRouter, HTTPException
from back.services.character_service import CharacterService
from back.models.schema import Character, CharacterListAny
from back.utils.logger import log_debug
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=CharacterListAny)
def list_characters():
    """
    Récupère la liste de tous les personnages disponibles dans le système.

    Cet endpoint permet d'obtenir tous les personnages créés, qu'ils soient complets ou en cours de création.
    Les personnages incomplets (status="en_cours") sont retournés avec uniquement les champs présents.

    Returns:
        CharacterListAny: Une liste contenant tous les personnages disponibles (complets ou partiels)
        
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
    result = []
    for c in characters:
        if isinstance(c, dict):
            c = c.copy()
            if "id" in c and not isinstance(c["id"], str):
                c["id"] = str(c["id"])
            result.append(c)
        else:
            d = c.model_dump()
            if "id" in d and not isinstance(d["id"], str):
                d["id"] = str(d["id"])
            result.append(d)
    return {"characters": result}

@router.get("/{character_id}", response_model=Character)
def get_character_detail(character_id: UUID):
    """
    Récupère le détail d'un personnage à partir de son identifiant unique.

    Cet endpoint permet d'obtenir toutes les informations détaillées d'un personnage spécifique.

    Paramètres:
        character_id (UUID): L'identifiant unique du personnage à récupérer
    Retourne:
        Character: Les informations détaillées du personnage
    """
    log_debug("Appel endpoint characters/get_character_detail", character_id=str(character_id))
    try:
        character = CharacterService.get_character(str(character_id))
        return character
    except Exception as e:
        log_debug(f"Erreur lors de la récupération du personnage: {e}", character_id=str(character_id))
        raise HTTPException(status_code=404, detail="Personnage non trouvé")
