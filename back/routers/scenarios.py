from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
from haystack.dataclasses import ChatMessage

from back.services.scenario_service import ScenarioService
from back.models.schema import ScenarioList
from back.utils.logger import log_debug
from back.agents.gm_agent import build_gm_agent, enrich_user_message_with_character
from back.services.character_service import CharacterService

router = APIRouter()

@router.get("/", response_model=ScenarioList)
async def list_scenarios():
    """
    ### list_scenarios
    **Description:** Endpoint pour lister les scénarios disponibles et en cours.
    **Parameters:** Aucun.
    **Returns:** `ScenarioList` contenant une liste de scénarios avec leurs états.
    """
    log_debug("Appel endpoint scenarios/list_scenarios")
    scenarios = ScenarioService.list_scenarios()
    return ScenarioList(scenarios=scenarios)

@router.get("/{scenario_file}")
async def get_scenario_details(scenario_file: str):
    """
    ### get_scenario_details
    **Description:** Récupère le contenu d'un scénario (fichier Markdown) à partir de son nom de fichier.
    **Parameters:**
    - `scenario_file` (str): Le nom du fichier du scénario (ex: Les_Pierres_du_Passe.md).
    **Returns:** Le contenu du fichier Markdown du scénario, ou une erreur 404 si le fichier n'existe pas.
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
    **Description:** Démarre un scénario avec un personnage spécifique, retourne l'id de session et déclenche le début du scénario avec le LLM.
    **Parameters:**
    - `request` (StartScenarioRequest): Contient le nom du scénario et l'identifiant du personnage.
    **Returns:** Un objet JSON avec session_id, scenario_name, character_id, message et la réponse initiale du LLM.
    **Raises:**
    - HTTPException 409: Si une session existe déjà avec le même scénario et personnage.
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
    
    try:        # Récupérer la fiche personnage pour l'injection
        character_json = ""
        try:
            character = CharacterService.get_character(request.character_id)
            character_json = character.model_dump_json()
        except Exception as e:
            log_debug("Erreur lors du chargement du personnage pour start_scenario", error=str(e), character_id=request.character_id)
            character_json = ""
        
        # Construire l'agent avec le scénario
        agent = build_gm_agent(session_id, request.scenario_name)
        store = agent._store
        messages = store.load()
        
        # Message initial pour démarrer le scénario
        start_message = "Démarre le scénario et présente-moi la situation initiale."
        
        # Enrichir le message avec la fiche personnage si disponible
        if character_json:
            enriched_message = enrich_user_message_with_character(start_message, character_json)
            messages.append(ChatMessage.from_user(enriched_message))
        else:
            messages.append(ChatMessage.from_user(start_message))
          # Appeler l'agent pour obtenir la réponse initiale
        result = agent.run(messages=messages)
        
        # Sauvegarder l'historique
        store.save(result["messages"])
        
        # Retourner les informations de session + la réponse du LLM
        response_data = {
            **session_info,  # session_id, scenario_name, character_id, message
            "llm_response": result["messages"][-1].text
        }
        
        log_debug("Scénario démarré avec réponse LLM", action="start_scenario", session_id=session_id, character_id=request.character_id, scenario_name=request.scenario_name)
        return response_data
        
    except Exception as e:
        log_debug("Erreur lors du démarrage du scénario avec LLM", error=str(e), session_id=session_id)
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
    **Description:** Envoie un message au MJ (LLM) pour jouer le scénario. Récupère automatiquement les informations de session (personnage et scénario).
    **Paramètres:**
    - `session_id` (UUID): Identifiant de la session de jeu (query parameter).
    - `request` (PlayScenarioRequest): Contient le message du joueur.
    **Retour:** Réponse générée par le LLM, incluant les réponses d'outils éventuelles.
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
        # Construire l'agent avec le scénario
        agent = build_gm_agent(str(session_id), scenario_name)
        store = agent._store
        messages = store.load()
        # Enrichir le message utilisateur avec la fiche personnage
        if character_json:
            enriched_message = enrich_user_message_with_character(request.message, character_json)
            user_message = ChatMessage.from_user(enriched_message)
        else:
            user_message = ChatMessage.from_user(request.message)
        # Ajouter le nouveau message à la liste existante
        messages.append(user_message)
        # Appeler l'agent Haystack avec tout l'historique
        result = agent.run(messages=messages)
        # Sauvegarder l'historique complet (incluant la nouvelle réponse)
        store.save(result["messages"])
        # Extraire les réponses d'outils et la réponse finale du LLM
        tool_responses = None
        final_llm_response = None
        # On parcourt les messages pour extraire la dernière réponse d'outil (role == 'tool') et la dernière réponse assistant
        for msg in reversed(result["messages"]):
            if hasattr(msg, "role") and msg.role == "tool":
                tool_result = msg.tool_call_results[0].result if len(msg.tool_call_results) > 0 else None
                tool_responses = tool_result
                break
        # La dernière réponse assistant est la réponse finale du LLM
        for msg in reversed(result["messages"]):
            if hasattr(msg, "role") and msg.role == "assistant":
                final_llm_response = msg.text
                break
        log_debug("Réponse LLM générée", action="play_scenario", session_id=str(session_id), character_id=character_id, scenario_name=scenario_name, user_message=request.message)
        return {
            "response": final_llm_response,
            "tool_responses": tool_responses
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log_debug("Erreur lors du jeu de scénario", error=str(e), session_id=str(session_id))
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")