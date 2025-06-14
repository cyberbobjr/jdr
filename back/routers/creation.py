"""
Routeur FastAPI pour la création de personnage.
Expose les routes nécessaires à chaque étape de la création et au suivi du statut.
"""
from fastapi import APIRouter
from uuid import uuid4
from datetime import datetime
from ..services.character_creation_service import CharacterCreationService
from back.services.character_persistence_service import CharacterPersistenceService
from back.models.schema import (
    AllocateAttributesRequest, AllocateAttributesResponse,
    CheckAttributesRequest, CheckAttributesResponse,
    SaveCharacterRequest, SaveCharacterResponse,
    CheckSkillsRequest, CheckSkillsResponse,
    CreationStatusResponse
)

router = APIRouter(tags=["creation"])

@router.get("/professions", summary="Liste des professions", response_model=list)
def get_professions():
    """
    Retourne la liste des professions disponibles.
    **Sortie** : Liste de chaînes (professions)
    """
    return CharacterCreationService.get_professions()

@router.get("/races", summary="Liste des races", response_model=list)
def get_races():
    """
    Retourne la liste des races disponibles.
    **Sortie** : Liste de chaînes (races)
    """
    return CharacterCreationService.get_races()

@router.get("/skills", summary="Liste des compétences", response_model=list)
def get_skills():
    """
    Retourne la liste des compétences disponibles.
    **Sortie** : Liste de chaînes (compétences)
    """
    return CharacterCreationService.get_skills()

@router.get("/cultures", summary="Liste des cultures", response_model=list)
def get_cultures():
    """
    Retourne la liste des cultures disponibles.
    **Sortie** : Liste de chaînes (cultures)
    """
    return CharacterCreationService.get_cultures()

@router.get("/equipments", summary="Liste des équipements", response_model=list)
def get_equipments():
    """
    Retourne la liste des équipements disponibles.
    **Sortie** : Liste de chaînes (équipements)
    """
    return CharacterCreationService.get_equipments()

@router.get("/spells", summary="Liste des sorts", response_model=list)
def get_spells():
    """
    Retourne la liste des sorts disponibles.
    **Sortie** : Liste de chaînes (sorts)
    """
    return CharacterCreationService.get_spells()

@router.post(
    "/allocate-attributes",
    response_model=AllocateAttributesResponse,
    summary="Allocation automatique des caractéristiques",
    description="Alloue automatiquement les caractéristiques selon la profession et la race fournies."
)
def allocate_attributes(request: AllocateAttributesRequest):
    """
    Alloue automatiquement les caractéristiques selon la profession et la race.
    - **Entrée** : profession (str), race (str)
    - **Sortie** : Dictionnaire des caractéristiques allouées
    """
    attributes = CharacterCreationService.allocate_attributes_auto(request.profession, request.race)
    return AllocateAttributesResponse(attributes=attributes)

@router.post(
    "/check-attributes",
    response_model=CheckAttributesResponse,
    summary="Validation des caractéristiques",
    description="Vérifie que la répartition des points de caractéristiques respecte les règles du jeu."
)
def check_attributes(request: CheckAttributesRequest):
    """
    Vérifie que les points de caractéristiques respectent les règles (budget, bornes).
    - **Entrée** : attributes (dict)
    - **Sortie** : valid (bool)
    """
    valid = CharacterCreationService.check_attributes_points(request.attributes)
    return CheckAttributesResponse(valid=valid)

@router.post(
    "/new",
    response_model=CreationStatusResponse,
    summary="Création d'un nouveau personnage",
    description="Crée un nouveau personnage (état initial, id et date de création)."
)
def create_new_character():
    """
    Crée un nouveau personnage (état initial, id et date de création).
    - **Sortie** : character_id (str), created_at (str), status (str)
    """
    character_id = str(uuid4())
    now = datetime.now().isoformat()
    character_data = {
        "id": character_id,
        "created_at": now,
        "last_update": now,
        "current_step": "creation",
        "status": "en_cours"
    }
    CharacterPersistenceService.save_character_data(character_id, character_data, operation="create")
    return {"character_id": character_id, "created_at": now, "status": "en_cours"}

@router.post(
    "/save",
    response_model=SaveCharacterResponse,
    summary="Sauvegarde du personnage",
    description="Enregistre ou met à jour les données du personnage en cours de création."
)
def save_character(request: SaveCharacterRequest):
    """
    Enregistre ou met à jour les données du personnage en cours de création.
    - **Entrée** : character_id (str), character (dict)
    - **Sortie** : status (str)
    """
    CharacterPersistenceService.save_character_data(request.character_id, request.character, operation="update")
    return SaveCharacterResponse(status="en_cours")

@router.get(
    "/status/{character_id}",
    response_model=CreationStatusResponse,
    summary="Statut de création du personnage",
    description="Retourne le statut de création du personnage (en cours, terminé, non trouvé)."
)
def get_creation_status(character_id: str):
    """
    Retourne le statut de création du personnage (en cours, terminé, non trouvé).
    - **Entrée** : character_id (str)
    - **Sortie** : status (str)
    """
    try:
        data = CharacterPersistenceService.load_character_data(character_id)
        return CreationStatusResponse(character_id=character_id, status=data.get("status", "en_cours"))
    except FileNotFoundError:
        return CreationStatusResponse(character_id=character_id, status="not_found")

@router.post(
    "/check-skills",
    response_model=CheckSkillsResponse,
    summary="Validation des compétences",
    description="Vérifie que la répartition des points de compétences respecte les règles (budget, groupes favoris, max par compétence)."
)
def check_skills(request: CheckSkillsRequest):
    """
    Vérifie que la répartition des points de compétences respecte les règles (budget, groupes favoris, max par compétence).
    - **Entrée** : skills (dict), profession (str)
    - **Sortie** : valid (bool), cost (int)
    """
    valid = CharacterCreationService.check_skills_points(request.skills, request.profession)
    cost = CharacterCreationService.calculate_skills_cost(request.skills, request.profession)
    return CheckSkillsResponse(valid=valid, cost=cost)
