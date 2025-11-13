from fastapi import APIRouter
from back.models.api_dto import CharacterListResponse, CharacterDetailResponse
from back.services.character_data_service import CharacterDataService
from back.utils.exceptions import CharacterNotFoundError, InternalServerError
from back.utils.logger import log_debug

router = APIRouter()


@router.get("/", response_model=CharacterListResponse)
def list_characters():
    """
    Récupère la liste de tous les personnages disponibles dans le système.

    Cet endpoint permet d'obtenir tous les personnages créés, qu'ils soient complets ou en cours de création.
    Les personnages incomplets (status="en_cours") sont retournés avec uniquement les champs présents.

    Returns:
        CharacterListResponse: Une liste contenant tous les personnages disponibles (complets ou partiels)
        
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
    
    try:
        data_service = CharacterDataService()
        characters = data_service.get_all_characters()
        
        # Convertir les objets Character en dictionnaires pour la réponse
        characters_data = [char.model_dump() for char in characters]
        
        log_debug("Liste des personnages récupérée", 
                 action="list_characters_success", 
                 count=len(characters_data))
        
        return CharacterListResponse(characters=characters_data)
        
    except Exception as e:
        log_debug("Erreur lors de la récupération des personnages", 
                 action="list_characters_error", 
                 error=str(e))
        raise InternalServerError(f"Erreur lors de la récupération des personnages: {str(e)}")


@router.get("/{character_id}", response_model=CharacterDetailResponse)
def get_character_detail(character_id: str):
    """
    Récupère le détail d'un personnage à partir de son identifiant unique.

    Cet endpoint permet d'obtenir toutes les informations détaillées d'un personnage spécifique.

    Paramètres:
        character_id (str): L'identifiant unique du personnage à récupérer
    Retourne:
        CharacterDetailResponse: Les informations détaillées du personnage
    """
    log_debug("Appel endpoint characters/get_character_detail", character_id=str(character_id))
    
    try:
        data_service = CharacterDataService()
        character = data_service.get_character_by_id(character_id)
        
        log_debug("Personnage récupéré avec succès", 
                 action="get_character_detail_success", 
                 character_id=character_id)
        
        return CharacterDetailResponse(**character.model_dump())
        
    except FileNotFoundError as e:
        log_debug("Personnage non trouvé", 
                 action="get_character_detail_not_found", 
                 character_id=character_id,
                 error=str(e))
        raise CharacterNotFoundError(character_id)
        
    except Exception as e:
        log_debug("Erreur lors de la récupération du personnage", 
                 action="get_character_detail_error", 
                 character_id=character_id,
                 error=str(e))
        raise InternalServerError(f"Erreur lors de la récupération du personnage: {str(e)}")
