"""
Routeur de scénarios utilisant l'agent GM PydanticAI.
Version finale après migration complète de Haystack vers PydanticAI.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
import traceback

from back.services.scenario_service import ScenarioService
from back.services.session_service import SessionService
from back.models.schema import (
    ScenarioList, PlayScenarioRequest, PlayScenarioResponse,
    ActiveSessionsResponse, StartScenarioRequest, StartScenarioResponse,
    ScenarioHistoryResponse
)
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
    
    **Format de réponse :**
    ```json
    {
        "scenarios": [
            {
                "name": "Les_Pierres_du_Passe.md",
                "status": "available",
                "session_id": null,
                "scenario_name": null,
                "character_name": null
            },
            {
                "name": "Les_Pierres_du_Passe.md - Galadhwen",
                "status": "in_progress",
                "session_id": "12345678-1234-5678-9012-123456789abc",
                "scenario_name": "Les_Pierres_du_Passe.md",
                "character_name": "Galadhwen"
            }
        ]
    }
    ```
    """
    log_debug("Appel endpoint scenarios/list_scenarios")
    scenarios = ScenarioService.list_scenarios()
    return ScenarioList(scenarios=scenarios)

@router.get("/sessions", response_model=ActiveSessionsResponse)
async def list_active_sessions():
    """
    ### list_active_sessions
    **Description :** Récupère la liste de toutes les sessions de jeu en cours avec le nom du scénario et le nom du personnage.
    **Paramètres :** Aucun.
    **Retour :**
    - `sessions` (List[SessionInfo]) : Liste des sessions actives avec session_id, scenario_name, character_id et character_name.
    
    **Format de réponse :**
    ```json
    {
        "sessions": [
            {
                "session_id": "12345678-1234-5678-9012-123456789abc",
                "scenario_name": "Les_Pierres_du_Passe.md",
                "character_id": "87654321-4321-8765-2109-987654321def",
                "character_name": "Galadhwen"
            }
        ]
    }
    ```
    """
    
    log_debug("Appel endpoint scenarios/list_active_sessions")
    try:
        # Récupérer toutes les sessions via SessionService
        sessions = SessionService.list_all_sessions()
          # Enrichir chaque session avec le nom du personnage
        enriched_sessions = []
        for session in sessions:
            try:
                # Récupérer le nom du personnage via CharacterService (méthode statique)
                character = CharacterService.get_character(session["character_id"])
                character_name = character.name
            except Exception as e:
                log_debug("Erreur lors du chargement du nom du personnage", error=str(e), character_id=session["character_id"])
                character_name = "Inconnu"
            
            enriched_sessions.append({
                "session_id": session["session_id"],
                "scenario_name": session["scenario_name"],
                "character_id": session["character_id"],
                "character_name": character_name
            })
        
        log_debug("Sessions actives récupérées", count=len(enriched_sessions))
        return {"sessions": enriched_sessions}
        
    except Exception as e:
        log_debug("Erreur lors de la récupération des sessions actives", error=str(e))
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@router.get("/{scenario_file}")
async def get_scenario_details(scenario_file: str):
    """
    ### get_scenario_details
    **Description :** Récupère le contenu d'un scénario (fichier Markdown) à partir de son nom de fichier.
    **Paramètres :**
    - `scenario_file` (str) : Le nom du fichier du scénario (ex: Les_Pierres_du_Passe.md).
    **Retour :** Le contenu du fichier Markdown du scénario sous forme de chaîne de caractères.
    **Exceptions :**
    - HTTPException 404 : Si le fichier de scénario n'existe pas.
    
    **Format de réponse :**
    ```
    # Scénario : Les Pierres du Passé
    
    ## Contexte
    L'histoire se déroule en l'année 2955 du Troisième Âge...
    
    ## 1. Lieux
    ### Village d'Esgalbar
    - **Description** : Petit hameau de maisons en bois...
    ```
    """
    log_debug("Appel endpoint scenarios/get_scenario_details", scenario_file=scenario_file)
    try:
        return ScenarioService.get_scenario_details(scenario_file)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Scénario '{scenario_file}' introuvable.")

class StartScenarioRequest(BaseModel):
    scenario_name: str
    character_id: str

@router.post("/start", response_model=StartScenarioResponse)
async def start_scenario(request: StartScenarioRequest):
    """
    ### start_scenario
    **Description :** Démarre un scénario avec un personnage spécifique, retourne l'id de session et déclenche le début du scénario avec le LLM.
    **Paramètres :**
    - `request` (StartScenarioRequest) : Contient le nom du scénario et l'identifiant du personnage.
        - `scenario_name` (str) : Nom du fichier de scénario (ex: "Les_Pierres_du_Passe.md")
        - `character_id` (str) : UUID du personnage qui participe au scénario
    **Retour :**
    - `session_id` (str) : Identifiant unique de la session créée
    - `scenario_name` (str) : Nom du scénario démarré
    - `character_id` (str) : ID du personnage participant
    - `message` (str) : Message de confirmation
    - `llm_response` (str) : Réponse initiale du Maître du Jeu pour commencer l'aventure
    **Exceptions :**
    - HTTPException 409 : Si une session existe déjà avec le même scénario et personnage.
    - HTTPException 404 : Si le scénario demandé n'existe pas.
    
    **Format de réponse :**
    ```json
    {
        "session_id": "12345678-1234-5678-9012-123456789abc",
        "scenario_name": "Les_Pierres_du_Passe.md",
        "character_id": "87654321-4321-8765-2109-987654321def",
        "message": "Scénario 'Les_Pierres_du_Passe.md' démarré avec succès pour le personnage 87654321-4321-8765-2109-987654321def.",
        "llm_response": "**Esgalbar, place centrale du village**\n\n*Le soleil décline lentement à l'horizon, teintant le ciel de nuances orangées. Une brume légère flotte autour de la fontaine sèche...*"
    }
    ```
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
        # Construire l'agent PydanticAI avec le scénario (le personnage est accessible via deps.character_service)
        agent, deps = build_gm_agent_pydantic(session_id, request.scenario_name)
        
        # Message initial pour démarrer le scénario
        start_message = "Démarre le scénario et présente-moi la situation initiale."
        
        # Enrichir le message avec la fiche personnage via le service de session
        character_json = deps.character_service.get_character_json()
        if character_json:
            enriched_message = enrich_user_message_with_character(start_message, character_json)
        else:
            enriched_message = start_message
        
        # Appeler l'agent PydanticAI avec l'historique existant (vide pour un nouveau scénario)
        result = await agent.run(
            enriched_message, 
            deps=deps
        )
        
        # Sauvegarder l'historique complet après la réponse
        deps.store.save_pydantic_history(result.all_messages())
        
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

@router.post("/play", response_model=PlayScenarioResponse)
async def play_scenario(session_id: UUID, request: PlayScenarioRequest):
    """
    ### play_scenario
    **Description :** Envoie un message au MJ (LLM) pour jouer le scénario. Récupère automatiquement les informations de session (personnage et scénario) et retourne l'historique complet des messages générés.
    **Paramètres :**
    - `session_id` (UUID) : Identifiant de la session de jeu (query parameter).
    - `request` (PlayScenarioRequest) : Objet contenant le message du joueur.
        - `message` (str) : Le message du joueur à envoyer au Maître du Jeu.
    **Retour :**
    - `response` (List[ConversationMessage]) : Liste complète des messages de conversation incluant :
        - Les messages utilisateur et système
        - Les réponses du LLM
        - Les appels d'outils et leurs résultats
        - Les métadonnées (tokens utilisés, timestamps, etc.)
    **Exceptions :**
    - HTTPException 404 : Si la session n'existe pas.
    - HTTPException 500 : Erreur lors de la génération de la réponse.
    
    **Format de réponse :**
    ```json
    {
        "response": [
            {
                "parts": [
                    {
                        "content": "Contenu du message",
                        "timestamp": "2025-06-09T09:30:34.839940Z",
                        "part_kind": "user-prompt|system-prompt|text|tool-call|tool-return"
                    }
                ],
                "kind": "request|response",
                "usage": {
                    "requests": 1,
                    "request_tokens": 2951,
                    "response_tokens": 423,
                    "total_tokens": 3374
                },
                "model_name": "deepseek-chat",
                "timestamp": "2025-06-09T09:30:35Z"
            }
        ]
    }
    ```
    """
    
    log_debug("Appel endpoint scenarios/play_scenario", session_id=str(session_id))
    try:
        # Récupérer les informations de session
        session_info = ScenarioService.get_session_info(str(session_id))
        character_id = session_info["character_id"]
        scenario_name = session_info["scenario_name"]
          # Construire l'agent PydanticAI avec le scénario (le personnage est accessible via deps.character_service)
        agent, deps = build_gm_agent_pydantic(str(session_id), scenario_name)
        
        # Enrichir le message utilisateur avec la fiche personnage via le service de session
        character_json = deps.character_service.get_character_json()
        if character_json:
            enriched_message = enrich_user_message_with_character(request.message, character_json)
        else:
            enriched_message = request.message

        history = deps.store.load_pydantic_history()

        # Appeler l'agent PydanticAI avec l'historique de la session
        result = await agent.run(
            enriched_message,
            deps=deps,
            message_history=history  # Utiliser l'historique chargé depuis le store
        )
        
        # Sauvegarder les nouveaux messages dans l'historique
        deps.store.save_pydantic_history(result.all_messages())
        
        log_debug("Réponse générée", action="play_scenario", session_id=str(session_id), character_id=character_id, scenario_name=scenario_name, user_message=request.message)
        
        return {
            "response": result.all_messages()
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

def get_message_dict(obj):
    """
    Convertit un objet message (ModelRequest, ModelResponse, etc.) en dict.
    Essaie .model_dump(), puis .dict(), puis vars(obj).
    """
    if hasattr(obj, 'model_dump'):
        return obj.model_dump()
    if hasattr(obj, 'dict'):
        return obj.dict()
    try:
        return vars(obj)
    except Exception:
        return None

def normalize_json_history(history):
    """
    Normalise l'historique JSON natif pour garantir la présence des champs obligatoires dans chaque part.
    - Ajoute un timestamp ISO si manquant ("1970-01-01T00:00:00Z").
    - Ajoute content vide si manquant.
    - Ajoute part_kind 'text' si manquant.
    """
    import datetime
    DEFAULT_TIMESTAMP = "1970-01-01T00:00:00Z"
    if not isinstance(history, list):
        return []
    normalized = []
    for msg in history:
        msg = dict(msg)  # Copie défensive
        parts = msg.get('parts', [])
        norm_parts = []
        for part in parts:
            part = dict(part)
            part.setdefault('content', '')
            part.setdefault('timestamp', DEFAULT_TIMESTAMP)
            part.setdefault('part_kind', 'text')
            norm_parts.append(part)
        msg['parts'] = norm_parts
        normalized.append(msg)
    return normalized

@router.get("/history/{session_id}", response_model=ScenarioHistoryResponse)
async def get_scenario_history(session_id: UUID):
    """
    ### get_scenario_history
    **Description :** Récupère l'historique complet des messages de la session de jeu spécifiée.
    **Paramètres :**
    - `session_id` (UUID) : Identifiant de la session de jeu.
    **Retour :**
    - `history` (List[ConversationMessage]) : Liste ordonnée de tous les messages (user, assistant, tool, etc.) de la session, avec le même format que `/scenarios/play`.
    **Exceptions :**
    - HTTPException 404 : Si la session n'existe pas.
    - HTTPException 500 : Erreur lors de la récupération de l'historique.
    """
    log_debug("Appel endpoint scenarios/get_scenario_history", session_id=str(session_id))
    try:
        # Récupérer les informations de session (vérifie l'existence)
        session_info = ScenarioService.get_session_info(str(session_id))
        scenario_name = session_info["scenario_name"]
        # Construire l'agent et accéder au store
        agent, deps = build_gm_agent_pydantic(str(session_id), scenario_name)
        history = deps.store.read_json_history()
        normalized_history = normalize_json_history(history)
        return {"history": normalized_history}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log_debug("Erreur lors de la récupération de l'historique de session", error=str(e), session_id=str(session_id))
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")
