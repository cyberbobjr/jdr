from fastapi import APIRouter, HTTPException
from back.models.domain.character import Character
from back.models.schema import CharacterListAny
from back.services.character_service import CharacterService
from back.utils.logger import log_debug

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
                    "spells": [],
                    "gold": 200,
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
        if isinstance(c, Character):
            c = c.model_dump()
            # Debug: vérifier le statut avant traitement
            log_debug("Character dict status avant traitement", character_id=c.get("id"), status=c.get("status"))
            # S'assurer que le statut est présent même s'il est None
        result.append(c)
    
    # Debug: vérifier le résultat final
    for r in result:
        log_debug("Résultat final", character_id=r.get("id"), status=r.get("status"))
    
    return {"characters": result}

@router.get("/{character_id}", response_model=dict)
def get_character_detail(character_id: str):
    """
    Récupère le détail d'un personnage à partir de son identifiant unique.

    Cet endpoint permet d'obtenir toutes les informations détaillées d'un personnage spécifique.

    Paramètres:
        character_id (str): L'identifiant unique du personnage à récupérer
    Retourne:
        dict: Les informations détaillées du personnage (permissif pour les personnages en cours)
    """
    log_debug("Appel endpoint characters/get_character_detail", character_id=str(character_id))
    
    try:
        character = CharacterService.get_character_by_id(character_id)
        return character
    except FileNotFoundError as e:
        log_debug(f"Personnage non trouvé: {e}", character_id=str(character_id))
        raise HTTPException(status_code=404, detail="Personnage non trouvé")
    except Exception as e:
        log_debug(f"Erreur lors de la récupération du personnage: {e}", character_id=str(character_id))
        raise HTTPException(status_code=500, detail=f"Erreur interne du serveur: {str(e)}")
