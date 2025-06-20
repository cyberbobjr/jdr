"""
Routeur FastAPI pour la création de personnage.
Expose les routes nécessaires à chaque étape de la création et au suivi du statut.
"""
from fastapi import APIRouter, HTTPException, Body, status
from uuid import uuid4
from datetime import datetime
from typing import List
import random
from ..services.character_creation_service import CharacterCreationService
from back.services.character_persistence_service import CharacterPersistenceService
from back.models.domain.races_manager import RacesManager
from back.models.schema import (
    AllocateAttributesRequest, AllocateAttributesResponse,
    CheckAttributesRequest, CheckAttributesResponse,
    SaveCharacterRequest, SaveCharacterResponse,
    CheckSkillsRequest, CheckSkillsResponse,
    CreationStatusResponse,
    RaceData,  # Remplace RaceSchema
    CharacteristicsResponse, UpdateSkillsRequest, UpdateSkillsResponse,  # Nouveau schéma pour les caractéristiques
    AddEquipmentRequest, AddEquipmentResponse,
    RemoveEquipmentRequest, RemoveEquipmentResponse,
    UpdateMoneyRequest, UpdateMoneyResponse
)
from back.agents.gm_agent_pydantic import build_gm_agent_pydantic, enrich_user_message_with_character

router = APIRouter(tags=["creation"])

@router.get("/races", summary="Liste des races", response_model=List[RaceData])
def get_races():
    """
    Retourne la liste complète des races disponibles (structure typée RaceData pour documentation Swagger).
    **Sortie** : Liste d'objets RaceData (structure complète issue du JSON).
    """
    from back.models.domain.races_manager import RacesManager
    races_manager = RacesManager()
    return races_manager.get_all_races()

@router.get(
    "/skills",
    summary="Compétences détaillées (LLM)",
    response_model=dict,  # Pour Swagger, on expose le schéma JSON complet
    response_description="Structure complète du fichier skills_for_llm.json (groupes, compétences, niveaux de difficulté, etc.)"
)
def get_skills():
    """
    Retourne la structure complète du fichier skills_for_llm.json (groupes, compétences, niveaux de difficulté, etc.).
    **Sortie** : Dictionnaire conforme à skills_for_llm.json
    """
    return CharacterCreationService.get_skills()


@router.get("/equipments", summary="Liste des équipements", response_model=list)
def get_equipments():
    """
    Retourne la liste des équipements disponibles.
    **Sortie** : Liste de chaînes (équipements)
    """
    return CharacterCreationService.get_equipments()

@router.get("/equipments-detailed", summary="Équipements avec détails", response_model=dict)
def get_equipments_detailed():
    """
    Retourne la structure complète des équipements avec leurs détails (armes, armures, objets).
    **Sortie** : Dictionnaire complet des équipements groupés par catégorie
    """
    from back.models.domain.equipment_manager import EquipmentManager
    equipment_manager = EquipmentManager()
    return equipment_manager.get_all_equipment()

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
    description="Alloue automatiquement les caractéristiques selon la race fournie."
)
def allocate_attributes(request: AllocateAttributesRequest):
    """
    Alloue automatiquement les caractéristiques selon la race.
    - **Entrée** : race (str)
    - **Sortie** : Dictionnaire des caractéristiques allouées
    """
    # Récupérer l'objet RaceData complet à partir du nom
    races_manager = RacesManager()
    race_data = races_manager.get_race_by_name(request.race)
    if not race_data:
        raise HTTPException(status_code=404, detail=f"Race '{request.race}' not found")
    
    attributes = CharacterCreationService.allocate_attributes_auto(race_data)
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
      # Générer l'argent de départ avec 1D100 (en pièce d'or)
    starting_money = random.randint(1, 100)
    
    character_data = {
        "id": character_id,
        "created_at": now,
        "last_update": now,
        "current_step": "creation",
        "status": "en_cours",
        "gold": starting_money  # Argent de départ (1D100 en pièce d'or)
    }
    CharacterPersistenceService.save_character_data(character_id, character_data)
    return {"id": character_id, "created_at": now, "status": "en_cours"}

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
    CharacterPersistenceService.save_character_data(request.character_id, request.character)
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
    - **Entrée** : skills (dict)
    - **Sortie** : valid (bool), cost (int)
    """
    valid = CharacterCreationService.check_skills_points(request.skills)
    cost = CharacterCreationService.calculate_skills_cost(request.skills)
    return CheckSkillsResponse(valid=valid, cost=cost)

@router.post("/generate-name", summary="Générer un nom de personnage via LLM")
async def generate_character_name(character: dict = Body(...)):
    """
    Génère un nom de personnage adapté via l'agent LLM, selon la fiche de personnage partielle.
    **Entrée** : Fiche de personnage (partielle)
    **Sortie** : Nom généré (str)
    """
    try:
        character_id = character.get("id")
        agent, _ = build_gm_agent_pydantic(session_id="creation-nom", character_id=str(character_id) if character_id else None)
        prompt = enrich_user_message_with_character(
            "Propose un nom de personnage approprié pour cette fiche. Réponds uniquement par le nom.",
            character
        )
        result = await agent.run(prompt)
        return {"name": result.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-background", summary="Générer un background de personnage via LLM")
async def generate_character_background(character: dict = Body(...)):
    """
    Génère un background d'histoire pour le personnage via l'agent LLM.
    **Entrée** : Fiche de personnage (partielle)
    **Sortie** : Background généré (str)
    """
    try:
        character_id = character.get("id")
        agent, _ = build_gm_agent_pydantic(session_id="creation-background", character_id=str(character_id) if character_id else None)
        prompt = enrich_user_message_with_character(
            "Rédige un background d'histoire immersif et cohérent pour ce personnage. Réponds uniquement par le texte du background.",
            character
        )
        result = await agent.run(prompt)
        return {"background": result.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-physical-description", summary="Générer une description physique via LLM")
async def generate_character_physical_description(character: dict = Body(...)):
    """
    Génère une description physique pour le personnage via l'agent LLM.
    **Entrée** : Fiche de personnage (partielle)
    **Sortie** : Description physique générée (str)
    """
    try:
        character_id = character.get("id")
        agent, _ = build_gm_agent_pydantic(session_id="creation-description", character_id=str(character_id) if character_id else None)
        prompt = enrich_user_message_with_character(
            "Décris l'apparence physique de ce personnage de façon détaillée et immersive. Réponds uniquement par la description.",
            character
        )
        result = await agent.run(prompt)
        return {"physical_description": result.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/characteristics", summary="Données complètes des caractéristiques", response_model=CharacteristicsResponse)
def get_characteristics():
    """
    Retourne le fichier characteristics.json complet avec toutes les données :
    - Définitions des caractéristiques (Force, Agilité, etc.)
    - Table des bonus par valeur
    - Table des coûts en points
    - Points de départ
    **Sortie** : Contenu complet du fichier characteristics.json
    """
    from back.models.domain.characteristics_manager import CharacteristicsManager
    manager = CharacteristicsManager()
    return manager.get_all_characteristics()

@router.delete("/delete/{character_id}", summary="Supprimer un personnage", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(character_id: str):
    """
    Supprime un personnage à partir de son identifiant.
    **Entrée** : character_id (str)
    **Sortie** : 204 No Content si succès
    """
    from back.services.character_persistence_service import CharacterPersistenceService
    CharacterPersistenceService.delete_character_data(character_id)
    return None

@router.post(
    "/update-skills",
    response_model=UpdateSkillsResponse,
    summary="Mise à jour des compétences",
    description="Met à jour uniquement les compétences du personnage en cours de création."
)
def update_skills(request: UpdateSkillsRequest):
    """
    Met à jour uniquement les compétences du personnage en cours de création.
    Effectue un merge avec les données existantes.
    - **Entrée** : character_id (str), skills (dict)
    - **Sortie** : status (str)
    """
    # Créer un dictionnaire avec seulement les compétences
    character_data = {"competences": request.skills}
    CharacterPersistenceService.save_character_data(request.character_id, character_data)
    return UpdateSkillsResponse(status="en_cours")

# === Routes pour la gestion d'équipement ===

@router.post(
    "/add-equipment",
    response_model=AddEquipmentResponse,
    summary="Ajouter un équipement",
    description="Ajoute un équipement au personnage et débite l'argent correspondant."
)
def add_equipment(request: AddEquipmentRequest):    
    """
    Ajoute un équipement au personnage et débite l'argent correspondant.
    - **Entrée** : character_id (str), equipment_name (str)
    - **Sortie** : status (str), gold (int), total_weight (float), equipment_added (dict)
    """
    try:
        # Charger les données du personnage directement
        character_data = CharacterPersistenceService.load_character_data(request.character_id)
        
        # Importer EquipmentManager pour gérer l'équipement
        from back.models.domain.equipment_manager import EquipmentManager
        
        # Récupérer les détails de l'équipement
        equipment_manager = EquipmentManager()
        equipment_details = equipment_manager.get_equipment_by_name(request.equipment_name)
        
        if not equipment_details:
            raise ValueError(f"Équipement '{request.equipment_name}' non trouvé")
          # Vérifier le budget avec la clé 'gold'
        current_gold = character_data.get('gold', 0.0)
        equipment_cost = equipment_details.get('cost', 0)
        
        if current_gold < equipment_cost:
            raise ValueError("Pas assez d'argent pour acheter cet équipement")
        
        # Ajouter l'équipement à l'inventaire (nouveau format)
        inventory = character_data.get('inventory', [])
          # Vérifier si l'équipement n'est pas déjà présent
        equipment_already_exists = any(
            item.get('name') == request.equipment_name for item in inventory
        )
        
        if not equipment_already_exists:            # Créer un objet Item complet pour l'inventaire selon le modèle schema.py
            import uuid
            
            # Mapper le type d'équipement vers l'énumération ItemType
            equipment_type = equipment_details.get('type', 'materiel').lower()
            if equipment_type == 'arme':
                item_type = 'Arme'
            elif equipment_type == 'armure':
                item_type = 'Armure'
            elif equipment_type == 'nourriture':
                item_type = 'Nourriture'
            elif equipment_type == 'objet_magique':
                item_type = 'Objet_Magique'
            else:
                item_type = 'Materiel'
            
            new_item = {
                "id": str(uuid.uuid4()),  # ID unique pour cette instance
                "name": request.equipment_name,
                "item_type": item_type,  # Type d'objet mappé
                "price_pc": equipment_details.get('cost', 0),  # Prix en pièces de cuivre 
                "weight_kg": equipment_details.get('weight', 0),  # Poids en kg
                "description": equipment_details.get('description', ''),  # Description
                "category": equipment_details.get('category'),  # Catégorie
                "damage": equipment_details.get('damage'),  # Dégâts si arme
                "quantity": 1,  # Quantité
                "is_equipped": False  # Pas équipé par défaut
            }
            inventory.append(new_item)
        
        # Mettre à jour l'or du personnage
        new_gold = current_gold - equipment_cost
        
        # Calculer le poids total pour la réponse
        total_weight = sum(item.get('weight_kg', 0) * item.get('quantity', 1) for item in inventory)
        
        # Mettre à jour les données du personnage
        character_data['inventory'] = inventory
        character_data['gold'] = new_gold
        
        # Sauvegarder les données mises à jour
        CharacterPersistenceService.save_character_data(request.character_id, character_data)
        return AddEquipmentResponse(
            status='success',
            gold=new_gold,
            total_weight=total_weight,
            equipment_added=equipment_details
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Personnage non trouvé")

@router.post(
    "/remove-equipment",
    response_model=RemoveEquipmentResponse,
    summary="Retirer un équipement",
    description="Retire un équipement du personnage et rembourse l'argent correspondant."
)
def remove_equipment(request: RemoveEquipmentRequest):   
    """
    Retire un équipement du personnage et rembourse l'argent correspondant.
    - **Entrée** : character_id (str), equipment_name (str)
    - **Sortie** : status (str), gold (int), total_weight (float), equipment_removed (dict)
    """
    try:
        # Charger les données du personnage directement
        character_data = CharacterPersistenceService.load_character_data(request.character_id)
        
        # Importer EquipmentManager pour gérer l'équipement
        from back.models.domain.equipment_manager import EquipmentManager
        
        # Récupérer les détails de l'équipement
        equipment_manager = EquipmentManager()
        equipment_details = equipment_manager.get_equipment_by_name(request.equipment_name)
        
        if not equipment_details:
            raise ValueError(f"Équipement '{request.equipment_name}' non trouvé")
          # Retirer l'équipement de l'inventaire
        inventory = character_data.get('inventory', [])
        
        # Trouver l'équipement dans l'inventaire
        item_to_remove = None
        for item in inventory:
            if item.get('name') == request.equipment_name:
                item_to_remove = item
                break
        
        if not item_to_remove:
            raise ValueError(f"L'équipement '{request.equipment_name}' n'est pas dans l'inventaire")
            
        inventory.remove(item_to_remove)
          # Rembourser l'or du personnage
        current_gold = character_data.get('gold', 0.0)
        equipment_cost = equipment_details.get('cost', 0)
        new_gold = current_gold + equipment_cost
          # Calculer le poids total pour la réponse
        total_weight = sum(item.get('weight_kg', 0) * item.get('quantity', 1) for item in inventory)
        
        # Mettre à jour les données du personnage
        character_data['inventory'] = inventory
        character_data['gold'] = new_gold
        
        # Sauvegarder les données mises à jour
        CharacterPersistenceService.save_character_data(request.character_id, character_data)
        return RemoveEquipmentResponse(
            status='success',
            gold=new_gold,
            total_weight=total_weight,
            equipment_removed=equipment_details
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Personnage non trouvé")

@router.post(
    "/update-money",
    response_model=UpdateMoneyResponse,
    summary="Mettre à jour l'argent",
    description="Met à jour l'argent du personnage (positif pour ajouter, négatif pour retirer)."
)
def update_money(request: UpdateMoneyRequest):    
    """
    Met à jour l'argent du personnage.
    - **Entrée** : character_id (str), amount (int)
    - **Sortie** : status (str), gold (int)
    """
    try:
        # Charger les données du personnage directement
        character_data = CharacterPersistenceService.load_character_data(request.character_id)
        
        # Mettre à jour l'or du personnage
        current_gold = character_data.get('gold', 0.0)
        new_gold = max(0.0, current_gold + request.amount)  # Ne pas aller en négatif
        
        character_data['gold'] = new_gold
        
        # Sauvegarder les données mises à jour
        CharacterPersistenceService.save_character_data(request.character_id, character_data)
        return UpdateMoneyResponse(
            status='success',
            gold=new_gold
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Personnage non trouvé")
