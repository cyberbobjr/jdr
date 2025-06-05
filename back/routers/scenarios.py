"""
Routeur de scénarios utilisant l'agent GM PydanticAI.
Version finale après migration complète de Haystack vers PydanticAI.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
import traceback

from back.services.scenario_service import ScenarioService
from back.models.schema import ScenarioList
from back.utils.logger import log_debug
from back.agents.gm_agent_pydantic import build_gm_agent_pydantic, enrich_user_message_with_character
from back.services.character_service import CharacterService

router = APIRouter()

@router.get("/", response_model=ScenarioList)
async def list_scenarios():
    """
    ### list_scenarios
    **Description :** Endpoint pour lister les scénarios disponibles et en cours.
    **Paramètres :** Aucun.
    **Retour :** `ScenarioList` contenant une liste de scénarios avec leurs états.
    """
    log_debug("Appel endpoint scenarios/list_scenarios")
    scenarios = ScenarioService.list_scenarios()
    return ScenarioList(scenarios=scenarios)

@router.get("/{scenario_file}")
async def get_scenario_details(scenario_file: str):
    """
    ### get_scenario_details
    **Description :** Récupère le contenu d'un scénario (fichier Markdown) à partir de son nom de fichier.
    **Paramètres :**
    - `scenario_file` (str) : Le nom du fichier du scénario (ex: Les_Pierres_du_Passe.md).
    **Retour :** Le contenu du fichier Markdown du scénario, ou une erreur 404 si le fichier n'existe pas.
    """
    log_debug("Appel endpoint scenarios/get_scenario_details", scenario_file=scenario_file)
    try:
        return ScenarioService.get_scenario_details(scenario_file)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Scénario '{scenario_file}' introuvable.")

class StartScenarioRequest(BaseModel):
    scenario_name: str
    character_id: str

@router.post("/start")
async def start_scenario(request: StartScenarioRequest):
    """
    ### start_scenario
    **Description :** Démarre un scénario avec un personnage spécifique, retourne l'id de session et déclenche le début du scénario avec le LLM.
    **Paramètres :**
    - `request` (StartScenarioRequest) : Contient le nom du scénario et l'identifiant du personnage.
    **Retour :** Un objet JSON avec session_id, scenario_name, character_id, message et la réponse initiale du LLM.
    **Exceptions :**
    - HTTPException 409 : Si une session existe déjà avec le même scénario et personnage.
    """
    log_debug("Appel endpoint scenarios/start_scenario")
    
    try:
        # Créer la session (vérifie automatiquement l'existence d'une session duplicatée)
        session_info = ScenarioService.start_scenario(request.scenario_name, request.character_id)
        session_id = session_info["session_id"]
    except ValueError as e:
        # Session déjà existante
        raise HTTPException(status_code=409, detail=str(e))
    except FileNotFoundError as e:
        # Scénario inexistant
        raise HTTPException(status_code=404, detail=str(e))
    
    try:
        # Récupérer la fiche personnage pour l'injection
        character_json = ""
        try:
            character = CharacterService.get_character(request.character_id)
            character_json = character.model_dump_json()
        except Exception as e:
            log_debug("Erreur lors du chargement du personnage pour start_scenario", error=str(e), character_id=request.character_id)
            character_json = ""
        
        # Construire l'agent PydanticAI avec le scénario
        agent, deps = build_gm_agent_pydantic(session_id, request.scenario_name)
        
        # Message initial pour démarrer le scénario
        start_message = "Démarre le scénario et présente-moi la situation initiale."
        
        # Enrichir le message avec la fiche personnage si disponible
        if character_json:
            enriched_message = enrich_user_message_with_character(start_message, character_json)
        else:
            enriched_message = start_message
        
        # Appeler l'agent PydanticAI avec l'historique existant (vide pour un nouveau scénario)
        result = await agent.run(
            enriched_message, 
            deps=deps,
            message_history=deps.message_history  # Utiliser l'historique chargé
        )
        
        # Sauvegarder les nouveaux messages dans l'historique
        deps.save_to_history(result.new_messages())
        
        # Retourner les informations de session + la réponse du LLM
        response_data = {
            **session_info,  # session_id, scenario_name, character_id, message
            "llm_response": result.data
        }
        
        log_debug("Scénario démarré avec réponse LLM", action="start_scenario", session_id=session_id, character_id=request.character_id, scenario_name=request.scenario_name)
        return response_data
        
    except Exception as e:
        log_debug("Erreur lors du démarrage du scénario avec LLM", error=str(e), traceback=traceback.format_exc(), session_id=session_id)
        # En cas d'erreur avec le LLM, retourner au moins les infos de session
        return {
            **session_info,
            "llm_response": f"Erreur lors du démarrage du scénario: {str(e)}"
        }

class PlayScenarioRequest(BaseModel):
    message: str

@router.post("/play")
async def play_scenario(session_id: UUID, request: PlayScenarioRequest):
    """
    ### play_scenario
    **Description :** Envoie un message au MJ (LLM) pour jouer le scénario. Récupère automatiquement les informations de session (personnage et scénario).
    **Paramètres :**
    - `session_id` (UUID) : Identifiant de la session de jeu (query parameter).
    - `request` (PlayScenarioRequest) : Contient le message du joueur.
    **Retour :**
    - `response` (str) : Réponse du Maître du Jeu
    - `tool_calls` (list) : Liste des appels d'outils effectués (si applicable)
    """
    log_debug("Appel endpoint scenarios/play_scenario", session_id=str(session_id))
    try:
        # Récupérer les informations de session
        session_info = ScenarioService.get_session_info(str(session_id))
        character_id = session_info["character_id"]
        scenario_name = session_info["scenario_name"]
        
        # Récupérer la fiche personnage
        character_json = ""
        try:
            character = CharacterService.get_character(character_id)
            character_json = character.model_dump_json()
        except Exception as e:
            log_debug("Erreur lors du chargement du personnage", error=str(e), character_id=character_id)
            character_json = ""
        
        # Construire l'agent PydanticAI avec le scénario
        agent, deps = build_gm_agent_pydantic(str(session_id), scenario_name)
        
        # Enrichir le message utilisateur avec la fiche personnage
        if character_json:
            enriched_message = enrich_user_message_with_character(request.message, character_json)
        else:
            enriched_message = request.message
        
        # Appeler l'agent PydanticAI avec l'historique de la session
        result = await agent.run(
            enriched_message,
            deps=deps,
            message_history=deps.message_history  # Utiliser l'historique chargé depuis le store
        )
        
        # Sauvegarder les nouveaux messages dans l'historique
        deps.save_to_history(result.new_messages())
        
        # Extraire les informations sur les appels d'outils
        tool_calls = []
        for msg in result.new_messages():
            if msg.role == 'model':
                for part in msg.parts:
                    if hasattr(part, 'tool_name'):  # ModelToolCall
                        tool_calls.append({
                            "tool_name": part.tool_name,
                            "arguments": part.args,
                            "tool_call_id": part.tool_call_id
                        })
        
        # Ajouter les résultats des outils
        for msg in result.new_messages():
            if msg.role == 'tool-return':
                for part in msg.parts:
                    if hasattr(part, 'tool_call_id'):  # ToolReturnPart
                        # Retrouver l'appel correspondant
                        for tool_call in tool_calls:
                            if tool_call['tool_call_id'] == part.tool_call_id:
                                tool_call['result'] = part.content
        
        log_debug("Réponse générée", action="play_scenario", session_id=str(session_id), character_id=character_id, scenario_name=scenario_name, user_message=request.message)
        
        return {
            "response": result.data,
            "tool_calls": tool_calls
        }
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log_debug(
            "Erreur lors du jeu de scénario",
            error=str(e),
            traceback=traceback.format_exc(),
            session_id=str(session_id)
        )
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.get("/history/{session_id}")
async def get_scenario_history(session_id: UUID):
    """
    ### get_scenario_history
    **Description :** Récupère l'historique complet des messages de la session de jeu spécifiée.
    **Paramètres :**
    - `session_id` (UUID) : Identifiant de la session de jeu.
    **Retour :**
    - `history` (list) : Liste ordonnée de tous les messages (user, assistant, tool, etc.) de la session.
    """
    log_debug("Appel endpoint scenarios/get_scenario_history", session_id=str(session_id))
    try:
        # Récupérer les informations de session (vérifie l'existence)
        session_info = ScenarioService.get_session_info(str(session_id))
        scenario_name = session_info["scenario_name"]
        
        # Construire l'agent et accéder au store
        agent, deps = build_gm_agent_pydantic(str(session_id), scenario_name)
        messages = deps.store.get_messages()
        
        # Retourner tous les messages de la session
        history = []
        for msg in messages:
            if isinstance(msg, dict):
                history.append(msg)
            elif hasattr(msg, 'model_dump'):
                history.append(msg.model_dump())
            else:
                # Pour compatibilité avec différents formats de messages
                history.append({
                    "role": getattr(msg, 'role', 'unknown'),
                    "content": getattr(msg, 'content', str(msg))
                })
        
        return {"history": history}
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log_debug("Erreur lors de la récupération de l'historique de session", error=str(e), session_id=str(session_id))
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")
