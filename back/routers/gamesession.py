"""
Game Session router for managing game sessions with LLM gameplay.
Handles session creation, listing, playing, and history management.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from uuid import UUID
from typing import List, Dict, Any, Optional
import traceback
import json



from back.services.game_session_service import GameSessionService, HISTORY_NARRATIVE
from back.models.schema import (
    PlayScenarioRequest,
    ActiveSessionsResponse,
    PlayScenarioResponse,
    ScenarioHistoryResponse,
    DeleteMessageResponse,
    SessionInfo,
)
from back.utils.logger import log_debug
from back.models.domain.character import Character
from back.models.enums import CharacterStatus
from back.services.character_data_service import CharacterDataService
from pydantic_ai.messages import ModelMessagesTypeAdapter
from back.utils.exceptions import (
    SessionNotFoundError,
    CharacterNotFoundError,
    ServiceNotInitializedError,
    CharacterInvalidStateError
)

# New imports for graph
from back.graph.nodes.dispatcher_node import DispatcherNode
from back.graph.dto.session import SessionGraphState, PlayerMessagePayload, GameState
from back.graph.graph_instance import session_graph  # Import global graph instance

router = APIRouter(tags=["gamesession"])

@router.get("/sessions", response_model=ActiveSessionsResponse)
async def list_active_sessions() -> ActiveSessionsResponse:
    """
    Retrieve the list of all active game sessions with scenario name and character name.

    **Response:**
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
    log_debug("Endpoint call: gamesession/list_active_sessions")
    try:
        sessions: List[Dict[str, Any]] = await GameSessionService.list_all_sessions()
        enriched_sessions: List[SessionInfo] = []
        data_service = CharacterDataService()
        for session in sessions:
            try:
                character: Optional[Character] = data_service.load_character(str(session["character_id"]))
                character_name: str = character.name if character else "Unknown"
            except FileNotFoundError:
                character_name = "Unknown"
            except Exception as e:
                log_debug("Error loading character name", error=str(e), character_id=session["character_id"])
                character_name = "Unknown"

            enriched_sessions.append(SessionInfo(
                session_id=str(session["session_id"]),
                scenario_name=session.get("scenario_id", "Unknown"),
                character_id=str(session["character_id"]),
                character_name=character_name
            ))

        log_debug("Active sessions retrieved", count=len(enriched_sessions))
        return ActiveSessionsResponse(sessions=enriched_sessions)

    except Exception as e:
        log_debug("Error retrieving active sessions", error=str(e), traceback=traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/play", response_model=PlayScenarioResponse)
async def play_scenario(
    request: PlayScenarioRequest,
    session_id: Optional[UUID] = None
) -> PlayScenarioResponse:
    """
    Play or start a scenario. If session_id is provided, continue the existing session.
    Otherwise, start a new session with scenario_name and character_id, then play with the default start message.

    **Parameters:**
    - session_id (UUID, optional): Existing session ID.
    - request (PlayScenarioRequest): Request body with optional message, and scenario_name/character_id for starting.

    **Request Body:**
    ```json
    {
        "message": "I go to the blacksmith.",  // Optional for continuation
        "scenario_name": "Les_Pierres_du_Passe.md",  // Required for starting
        "character_id": "87654321-4321-8765-2109-987654321def"  // Required for starting
    }
    ```

    **Response:**
    ```json
    ```json
    {
        "session_id": "12345678-1234-5678-9012-123456789abc",
        "response": [
            {
                "parts": [
                    {
                        "content": "I go to the blacksmith Thadric.",
                        "timestamp": "2025-06-21T12:30:34.839940Z",
                        "part_kind": "user-prompt"
                    }
                ],
                "kind": "request",
                "timestamp": "2025-06-21T12:30:34.839940Z"
            },
            {
                "parts": [
                    {
                        "content": "**Thadric welcomes you with a smile**...",
                        "timestamp": "2025-06-21T12:30:35.000000Z",
                        "part_kind": "text"
                    }
                ],
                "kind": "response",
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

    **Raises:**
    - HTTPException 404: If the session does not exist.
    - HTTPException 500: Error generating the response.

    **Note:** This route returns raw JSON without Pydantic validation to avoid serialization errors.
    """
    log_debug("Endpoint call: gamesession/play_scenario", session_id=str(session_id) if session_id else None)

    # Logique de démarrage si session_id est None
    if session_id is None:
        if not request.scenario_name or not request.character_id:
            raise HTTPException(status_code=400, detail="scenario_name and character_id are required to start a new session.")
        
        try:
            data_service = CharacterDataService()
            character_data = data_service.load_character(request.character_id)
            if character_data.status == CharacterStatus.DRAFT:
                raise HTTPException(status_code=400, detail="Cannot start a scenario with a character in creation.")
            
            session_info = await GameSessionService.start_scenario(request.scenario_name, UUID(request.character_id))
            session_id = UUID(session_info["session_id"])
            message = "Start the scenario and present the initial situation."  # Message de démarrage fixe
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
    else:
        if not request.message:
            raise HTTPException(status_code=400, detail="message is required for continuing a session.")
        message = request.message

    # Logique commune
    try:
        session_service = await GameSessionService.load(str(session_id))

        game_state = await session_service.load_game_state()
        if game_state is None:
            game_state = GameState(
                session_mode="narrative",
                narrative_history_id="default",
                combat_history_id="default"
            )
            await session_service.update_game_state(game_state)

        player_message = PlayerMessagePayload(message=message)
        graph_state = SessionGraphState(
            game_state=game_state,
            pending_player_message=player_message
        )

        result = await session_graph.run(DispatcherNode(), state=graph_state, deps=session_service)

        log_debug("Graph response generated", action="play_scenario", session_id=str(session_id))
        return PlayScenarioResponse(
            response=result.output.all_messages,
            session_id=session_id
        )

    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CharacterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ServiceNotInitializedError as e:
        raise HTTPException(status_code=500, detail=f"Service initialization error: {str(e)}")
    except Exception as e:
        log_debug("Error playing scenario", error=str(e), traceback=traceback.format_exc(), session_id=str(session_id))
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.post("/play-stream")
async def play_stream(session_id: UUID, message: PlayScenarioRequest):
    """
    Send a message to the GM (LLM) and stream the response using Server-Sent Events.
    Uses the graph-based system for session management with real-time streaming.
    """
    log_debug("Endpoint call: gamesession/play_stream", session_id=str(session_id))

    try:
        # Get session service
        session_service = await GameSessionService.load(str(session_id))

        # Load or create game_state
        game_state = await session_service.load_game_state()
        if game_state is None:
            # Create initial game_state
            game_state = GameState(
                session_mode="narrative",
                narrative_history_id="default",
                combat_history_id="default"
            )
            await session_service.update_game_state(game_state)

        # Create graph state
        player_message = PlayerMessagePayload(message=message.message or "")
        graph_state = SessionGraphState(
            game_state=game_state,
            pending_player_message=player_message
        )

        async def stream_generator():
            """
            Generator for emitting the graph results.
            Note: This is not true real-time streaming - it waits for the full response
            before emitting. For true streaming, agents inside nodes would need to use
            agent.run_stream() and yield tokens as they arrive from the LLM.
            """
            try:
                # Run the full graph to completion
                result = await session_graph.run(DispatcherNode(), state=graph_state, deps=session_service)
                
                # Emit new messages (already serialized in DispatchResult)
                for message_dict in result.output.new_messages:
                    for part in message_dict.get("parts", []):
                        yield f"data: {json.dumps(part, default=str)}\n\n"

                log_debug("Stream finished", session_id=str(session_id))

            except Exception as e:
                log_debug(
                    "Error during graph streaming",
                    error=str(e),
                    exc_info=True,
                    session_id=str(session_id),
                )
                error_message = {
                    "error": "An error occurred during the stream.",
                    "details": str(e),
                    "exception_type": e.__class__.__name__,
                    "traceback": traceback.format_exc(),
                }
                yield f"data: {json.dumps(error_message, default=str)}\n\n"

        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
        )

    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CharacterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ServiceNotInitializedError as e:
        raise HTTPException(status_code=500, detail=f"Service initialization error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        log_debug("Error preparing stream", error=str(e), traceback=traceback.format_exc(), session_id=str(session_id))
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/history/{session_id}", response_model=ScenarioHistoryResponse)
async def get_scenario_history(session_id: UUID) -> ScenarioHistoryResponse:
    """
    Retrieve the complete message history of the specified game session in raw JSON format.

    **Parameters:**
    - `session_id` (UUID): Game session identifier.

    **Response:**
    ```json
    {
        "history": [
            {
                "parts": [
                    {
                        "content": "Start the scenario and present the initial situation.",
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
                        "content": "**Esgalbar, central square of the village**...",
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
            }
        ]
    }
    ```

    **Raises:**
    - HTTPException 404: If the session does not exist.
    - HTTPException 500: Error retrieving the history.

    **Note:** This route returns raw JSON without Pydantic validation to ensure format consistency with `/gamesession/play`.
    """
    log_debug("Endpoint call: gamesession/get_scenario_history", session_id=str(session_id))
    try:
        session = await GameSessionService.load(str(session_id))
        history: List[Dict[str, Any]] = await session.load_history_raw_json(HISTORY_NARRATIVE)
        return ScenarioHistoryResponse(history=history)
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log_debug("Error retrieving session history", error=str(e), session_id=str(session_id))
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.delete("/history/{session_id}/{message_index}", response_model=DeleteMessageResponse)
async def delete_history_message(session_id: UUID, message_index: int) -> DeleteMessageResponse:
    """
    Delete a specific entry from the game session history by its index in the array.

    **Parameters:**
    - `session_id` (UUID): Game session identifier.
    - `message_index` (int): Index (0-based) of the message to delete in the history array.

    **Response:**
    ```json
    {
        "message": "Message at index 2 deleted successfully from session 83d68867-a944-4f33-be82-2365904c3c43.",
        "deleted_message_info": {
            "kind": "response",
            "timestamp": "2025-06-21T12:05:05.000000Z",
            "parts_count": 3,
            "model_name": "deepseek-chat"
        },
        "remaining_messages_count": 5
    }
    ```

    **Raises:**
    - HTTPException 404: If the session does not exist or the index is invalid.
    - HTTPException 400: If the index is negative or out of bounds.
    - HTTPException 500: Error during deletion.

    **Note:** This operation permanently modifies the history. It is recommended to backup the history before deletion if necessary. This route returns raw JSON without Pydantic validation to avoid serialization errors.
    """

    log_debug("Endpoint call: gamesession/delete_history_message", session_id=str(session_id), message_index=message_index)

    if message_index < 0:
        raise HTTPException(status_code=400, detail=f"Index {message_index} cannot be negative.")

    try:
        session = await GameSessionService.load(str(session_id))

        history: List[Dict[str, Any]] = await session.load_history_raw_json(HISTORY_NARRATIVE)

        if message_index >= len(history):
            raise HTTPException(
                status_code=404,
                detail=f"Invalid index {message_index}. History contains {len(history)} message(s) (indices 0 to {len(history)-1})."
            )

        deleted_message: Dict[str, Any] = history[message_index]
        deleted_message_info: Dict[str, Any] = {
            "kind": deleted_message.get("kind", "unknown"),
            "timestamp": deleted_message.get("timestamp", "unknown"),
            "parts_count": len(deleted_message.get("parts", [])),
        }

        if "model_name" in deleted_message:
            deleted_message_info["model_name"] = deleted_message["model_name"]

        history.pop(message_index)

        try:
            pydantic_history = ModelMessagesTypeAdapter.validate_python(history)
            await session.save_history("narrative", pydantic_history)
        except ImportError as e:
            log_debug("PydanticAI messages import error", error=str(e))
            raise HTTPException(status_code=500, detail=f"PydanticAI configuration missing: {str(e)}")

        remaining_count: int = len(history)

        log_debug(
            "History message deleted",
            session_id=str(session_id),
            message_index=message_index,
            remaining_count=remaining_count,
            deleted_kind=deleted_message_info["kind"]
        )

        return DeleteMessageResponse(
            message=f"Message at index {message_index} deleted successfully from session {session_id}.",
            deleted_message_info=deleted_message_info,
            remaining_messages_count=remaining_count
        )

    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except IndexError:
        raise HTTPException(status_code=404, detail=f"Invalid index {message_index} for this session.")
    except Exception as e:
        log_debug(
            "Error deleting history message",
            error=str(e),
            session_id=str(session_id),
            message_index=message_index
        )
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/{session_id}/preferences", response_model=Dict[str, str])
async def get_preferences(session_id: UUID) -> Dict[str, str]:
    """
    Retrieve the user preferences for the specified session.

    **Parameters:**
    - `session_id` (UUID): Game session identifier.

    **Response:**
    ```json
    {
        "language": "English"
    }
    ```
    """
    log_debug("Endpoint call: gamesession/get_preferences", session_id=str(session_id))
    try:
        session_service = await GameSessionService.load(str(session_id))
        game_state = await session_service.load_game_state()
        if not game_state:
            raise HTTPException(status_code=404, detail="Game state not found")
        
        return {"language": game_state.preferences.language}
    except SessionNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")