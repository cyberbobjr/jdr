"""
Routeur de scénarios utilisant l'agent GM PydanticAI.
Version finale après migration complète de Haystack vers PydanticAI.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
import traceback
import datetime

from back.services.scenario_service import ScenarioService
from back.services.session_service import SessionService
from back.models.schema import (
    ScenarioList, PlayScenarioRequest, ActiveSessionsResponse, StartScenarioRequest, StartScenarioResponse
)
from back.utils.logger import log_debug
from back.agents.gm_agent_pydantic import build_gm_agent_pydantic, enrich_user_message_with_character
from back.services.character_service import CharacterService
from back.services.character_persistence_service import CharacterPersistenceService

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
    ```    """
    
    log_debug("Appel endpoint scenarios/list_active_sessions")
    try:
        # Récupérer toutes les sessions via SessionService
        sessions = SessionService.list_all_sessions()
        
        # Enrichir chaque session avec le nom du personnage
        enriched_sessions = []
        for session in sessions:
            try:
                # Récupérer le nom du personnage via CharacterService (méthode statique)
                character = CharacterService.get_character_by_id(session["character_id"])
                character_name = character.get("name", "Personnage sans nom")
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
        # Vérification du statut du personnage
        character_data = CharacterPersistenceService.load_character_data(request.character_id)
        if character_data.get("status") == "en_cours":
            raise HTTPException(status_code=400, detail="Impossible de démarrer un scénario avec un personnage en cours de création.")
        
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
            "llm_response": result.output
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

@router.post("/play")
async def play_scenario(session_id: UUID, request: PlayScenarioRequest):
    """
    ### play_scenario
    **Description :** Envoie un message au MJ (LLM) pour jouer le scénario. Récupère automatiquement les informations de session (personnage et scénario) et retourne l'historique complet des messages générés au format JSON brut.
    **Paramètres :**
    - `session_id` (UUID) : Identifiant de la session de jeu (query parameter).
    - `request` (PlayScenarioRequest) : Objet contenant le message du joueur.
        - `message` (str) : Le message du joueur à envoyer au Maître du Jeu.
    **Retour :**
    - `response` (List[dict]) : Liste complète des messages de conversation normalisés au format JSON brut incluant :
        - Les messages utilisateur et système
        - Les réponses du LLM
        - Les appels d'outils et leurs résultats
        - Les métadonnées (tokens utilisés, timestamps, etc.)
        - Tous les timestamps sont convertis en chaînes ISO format
        - Tous les champs requis sont garantis présents
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
                        "timestamp": "2025-06-21T12:30:34.839940Z",
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
                "timestamp": "2025-06-21T12:30:35.000000Z"
            }
        ]
    }
    ```
    **Note :** Cette route retourne du JSON brut sans validation Pydantic pour éviter les erreurs de sérialisation.
    """
    
    log_debug("Appel endpoint scenarios/play_scenario", session_id=str(session_id))
    try:
        # Récupérer les informations de session
        session_info = ScenarioService.get_session_info(str(session_id))
        character_id = session_info["character_id"]
        # Vérification du statut du personnage
        character_data = CharacterPersistenceService.load_character_data(character_id)
        if character_data.get("status") == "en_cours":
            raise HTTPException(status_code=400, detail="Impossible de jouer avec un personnage en cours de création.")
        
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
        
        # Retourner directement les messages normalisés sans validation Pydantic
        normalized_messages = normalize_json_history(result.all_messages())
        return {
            "response": normalized_messages
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

def normalize_json_history(history):
    """
    Normalise l'historique JSON natif pour garantir la présence des champs obligatoires dans chaque part.
    - Ajoute un timestamp ISO si manquant ("1970-01-01T00:00:00Z").
    - Convertit les objets datetime en chaînes ISO.
    - Ajoute content vide si manquant.
    - Ajoute part_kind 'text' si manquant.
    """
    DEFAULT_TIMESTAMP = "1970-01-01T00:00:00Z"
    
    def convert_timestamp(ts):
        """Convertit un timestamp en chaîne ISO."""
        if ts is None:
            return DEFAULT_TIMESTAMP
        if isinstance(ts, datetime.datetime):
            return ts.isoformat()
        if isinstance(ts, str):
            return ts
        return DEFAULT_TIMESTAMP
    
    def normalize_part(part):
        """Normalise une part de message en gérant tous les types d'objets."""
        # Convertir l'objet en dictionnaire
        if hasattr(part, '__dict__'):
            part_dict = vars(part)
        elif hasattr(part, 'model_dump'):
            part_dict = part.model_dump()
        elif hasattr(part, 'dict'):
            part_dict = part.dict()
        else:
            part_dict = dict(part)
        
        # Déterminer le type de part et ajuster les champs
        part_type = type(part).__name__ if hasattr(part, '__class__') else 'unknown'
        
        if 'TextPart' in part_type:
            part_dict.setdefault('content', part_dict.get('content', ''))
            part_dict.setdefault('part_kind', 'text')
        elif 'ToolCallPart' in part_type:
            # Pour les ToolCallPart, créer un contenu structuré
            tool_name = part_dict.get('tool_name', 'unknown_tool')
            args = part_dict.get('args', '{}')
            tool_call_id = part_dict.get('tool_call_id', 'unknown_id')
            part_dict['content'] = f"Tool call: {tool_name} with args: {args}"
            part_dict.setdefault('part_kind', 'tool-call')
        elif 'ToolReturnPart' in part_type:
            # Pour les ToolReturnPart
            part_dict.setdefault('content', str(part_dict.get('content', '')))
            part_dict.setdefault('part_kind', 'tool-return')
        else:
            # Pour les autres types
            part_dict.setdefault('content', str(part_dict.get('content', '')))
            part_dict.setdefault('part_kind', 'text')
          # Normaliser le timestamp - utiliser le timestamp du message si celui de la part est None
        part_timestamp = part_dict.get('timestamp')
        if part_timestamp is None:
            part_timestamp = msg_dict.get('timestamp')
        part_dict['timestamp'] = convert_timestamp(part_timestamp)
        
        return part_dict
    
    if not isinstance(history, list):
        return []
    
    normalized = []
    for msg in history:
        # Convertir le message en dictionnaire
        if hasattr(msg, '__dict__'):
            msg_dict = vars(msg)
        elif hasattr(msg, 'model_dump'):
            msg_dict = msg.model_dump()
        elif hasattr(msg, 'dict'):
            msg_dict = msg.dict()
        else:
            msg_dict = dict(msg)
        
        # Normaliser le timestamp du message
        msg_dict['timestamp'] = convert_timestamp(msg_dict.get('timestamp'))
        
        # Normaliser toutes les parts
        parts = msg_dict.get('parts', [])
        norm_parts = []
        for part in parts:
            norm_parts.append(normalize_part(part))
            
        msg_dict['parts'] = norm_parts
        normalized.append(msg_dict)
    
    return normalized

@router.get("/history/{session_id}")
async def get_scenario_history(session_id: UUID):    
    """
    ### get_scenario_history
    **Description :** Récupère l'historique complet des messages de la session de jeu spécifiée au format JSON brut.
    **Paramètres :**
    - `session_id` (UUID) : Identifiant de la session de jeu.
    **Retour :**
    - `history` (List[dict]) : Liste ordonnée de tous les messages (user, assistant, tool, etc.) de la session, normalisés au format JSON brut incluant :
        - Les messages utilisateur et système avec leurs prompts
        - Les réponses du LLM avec le contenu généré
        - Les appels d'outils (tool-call) et leurs résultats (tool-return)
        - Les métadonnées complètes (usage des tokens, model_name, timestamps, etc.)
        - Tous les timestamps convertis en chaînes ISO format
        - Tous les champs requis garantis présents (content, timestamp, part_kind)
        - Format identique à celui retourné par `/scenarios/play`
    **Exceptions :**
    - HTTPException 404 : Si la session n'existe pas.
    - HTTPException 500 : Erreur lors de la récupération de l'historique.
    
    **Format de réponse :**
    ```json
    {
        "history": [
            {
                "parts": [
                    {
                        "content": "Démarre le scénario et présente-moi la situation initiale.",
                        "timestamp": "2025-06-21T12:00:00.000000Z",
                        "part_kind": "user-prompt"
                    }
                ],
                "kind": "request",
                "timestamp": "2025-06-21T12:00:00.000000Z"
            },
            {
                "parts": [
                    {
                        "content": "**Esgalbar, place centrale du village**...",
                        "timestamp": "2025-06-21T12:00:05.123456Z",
                        "part_kind": "text"
                    }
                ],
                "kind": "response",
                "usage": {
                    "requests": 1,
                    "request_tokens": 1250,
                    "response_tokens": 567,
                    "total_tokens": 1817
                },
                "model_name": "deepseek-chat",
                "timestamp": "2025-06-21T12:00:05.123456Z"
            },
            {
                "parts": [
                    {
                        "content": "Je vais parler à Thadric le forgeron.",
                        "timestamp": "2025-06-21T12:05:00.000000Z",
                        "part_kind": "user-prompt"
                    }
                ],
                "kind": "request",
                "timestamp": "2025-06-21T12:05:00.000000Z"
            },
            {
                "parts": [
                    {
                        "content": "Tool call: skill_check_with_character with args: {\"skill_name\":\"Diplomatie\",\"difficulty_name\":\"Moyenne\"}",
                        "timestamp": "2025-06-21T12:05:02.000000Z",
                        "part_kind": "tool-call"
                    },
                    {
                        "content": "{\"success\": true, \"result\": 15, \"difficulty\": 12}",
                        "timestamp": "2025-06-21T12:05:03.000000Z",
                        "part_kind": "tool-return"
                    },
                    {
                        "content": "**Thadric vous accueille avec un sourire**...",
                        "timestamp": "2025-06-21T12:05:05.000000Z",
                        "part_kind": "text"
                    }
                ],
                "kind": "response",
                "usage": {
                    "requests": 1,
                    "request_tokens": 2100,
                    "response_tokens": 423,
                    "total_tokens": 2523
                },
                "model_name": "deepseek-chat",
                "timestamp": "2025-06-21T12:05:05.000000Z"
            }
        ]
    }
    ```
    **Note :** Cette route retourne du JSON brut sans validation Pydantic pour éviter les erreurs de sérialisation, et garantit la cohérence du format avec `/scenarios/play`.
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

@router.delete("/history/{session_id}/{message_index}")
async def delete_history_message(session_id: UUID, message_index: int):
    """
    ### delete_history_message
    **Description :** Supprime une entrée spécifique de l'historique de la session de jeu en utilisant son index dans le tableau.
    **Paramètres :**
    - `session_id` (UUID) : Identifiant de la session de jeu.
    - `message_index` (int) : Index (base 0) du message à supprimer dans le tableau d'historique.
    **Retour :**
    - `message` (str) : Message de confirmation de la suppression.
    - `deleted_message_info` (dict) : Informations sur le message supprimé (kind, timestamp, nombre de parts).
    - `remaining_messages_count` (int) : Nombre de messages restants dans l'historique.
    **Exceptions :**
    - HTTPException 404 : Si la session n'existe pas ou si l'index est invalide.
    - HTTPException 400 : Si l'index est négatif ou hors limites.
    - HTTPException 500 : Erreur lors de la suppression.
    
    **Format de réponse :**
    ```json
    {
        "message": "Message à l'index 2 supprimé avec succès de la session 83d68867-a944-4f33-be82-2365904c3c43.",
        "deleted_message_info": {
            "kind": "response",
            "timestamp": "2025-06-21T12:05:05.000000Z",
            "parts_count": 3,
            "model_name": "deepseek-chat"
        },
        "remaining_messages_count": 5
    }
    ```
    
    **Exemples d'utilisation :**
    - `DELETE /scenarios/history/{session_id}/0` : Supprime le premier message (souvent le message de démarrage)
    - `DELETE /scenarios/history/{session_id}/3` : Supprime le 4ème message de l'historique
    - `DELETE /scenarios/history/{session_id}/-1` : Erreur 400 (index négatif non autorisé)
    
    **Note :** Cette opération modifie définitivement l'historique. Il est recommandé de sauvegarder l'historique avant suppression si nécessaire. Cette route retourne du JSON brut sans validation Pydantic pour éviter les erreurs de sérialisation.
    """
    
    log_debug("Appel endpoint scenarios/delete_history_message", session_id=str(session_id), message_index=message_index)
    
    # Validation de l'index
    if message_index < 0:
        raise HTTPException(status_code=400, detail=f"L'index {message_index} ne peut pas être négatif.")
    
    try:
        # Récupérer les informations de session (vérifie l'existence)
        session_info = ScenarioService.get_session_info(str(session_id))
        scenario_name = session_info["scenario_name"]
        
        # Construire l'agent et accéder au store
        agent, deps = build_gm_agent_pydantic(str(session_id), scenario_name)
        
        # Charger l'historique actuel
        history = deps.store.read_json_history()
        
        # Vérifier que l'index est valide
        if message_index >= len(history):
            raise HTTPException(
                status_code=404, 
                detail=f"Index {message_index} invalide. L'historique contient {len(history)} message(s) (indices 0 à {len(history)-1})."
            )
        
        # Récupérer les informations du message à supprimer
        deleted_message = history[message_index]
        deleted_message_info = {
            "kind": deleted_message.get("kind", "unknown"),
            "timestamp": deleted_message.get("timestamp", "unknown"),
            "parts_count": len(deleted_message.get("parts", [])),
        }
        
        # Ajouter le model_name si disponible
        if "model_name" in deleted_message:
            deleted_message_info["model_name"] = deleted_message["model_name"]
          # Supprimer le message de l'historique
        history.pop(message_index)
        
        # Sauvegarder l'historique modifié (utiliser save_pydantic_history, pas save_json_history)
        # Convertir d'abord en format PydanticAI puis sauvegarder
        try:
            from pydantic_ai.messages import ModelMessagesTypeAdapter
            pydantic_history = ModelMessagesTypeAdapter.validate_python(history)
            deps.store.save_pydantic_history(pydantic_history)
        except ImportError as e:
            log_debug("Erreur d'import pydantic_ai.messages", error=str(e))
            raise HTTPException(status_code=500, detail=f"Configuration PydanticAI manquante: {str(e)}")
        
        remaining_count = len(history)
        
        log_debug(
            "Message d'historique supprimé", 
            session_id=str(session_id), 
            message_index=message_index, 
            remaining_count=remaining_count,
            deleted_kind=deleted_message_info["kind"]
        )
        
        # Retourner du JSON brut sans validation Pydantic
        return {
            "message": f"Message à l'index {message_index} supprimé avec succès de la session {session_id}.",
            "deleted_message_info": deleted_message_info,
            "remaining_messages_count": remaining_count
        }
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IndexError:
        # Au cas où l'erreur d'index ne serait pas attrapée plus haut
        raise HTTPException(status_code=404, detail=f"Index {message_index} invalide pour cette session.")
    except Exception as e:
        log_debug(
            "Erreur lors de la suppression du message d'historique", 
            error=str(e), 
            session_id=str(session_id), 
            message_index=message_index
        )
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")
