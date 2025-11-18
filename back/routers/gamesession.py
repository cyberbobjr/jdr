"""
Game Session router for managing game sessions with LLM gameplay.
Handles session creation, listing, playing, and history management.
"""

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ValidationError
from fastapi.responses import StreamingResponse
from uuid import UUID
from typing import List, Dict, Any, Optional
import traceback
import json

from pydantic_ai import Agent

from back.services.game_session_service import GameSessionService
from back.models.schema import (
    PlayScenarioRequest,
    ActiveSessionsResponse,
    StartScenarioResponse,
    StartScenarioRequest,
    PlayScenarioResponse,
    ScenarioHistoryResponse,
    DeleteMessageResponse,
    SessionInfo,
)
from back.utils.logger import log_debug
from back.agents.gm_agent_pydantic import build_gm_agent_pydantic, enrich_user_message_with_character
from back.models.domain.character import Character, CharacterStatus
from back.services.character_persistence_service import CharacterPersistenceService
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter
from pydantic_ai import Agent

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
        sessions: List[Dict[str, Any]] = GameSessionService.list_all_sessions()
        enriched_sessions: List[SessionInfo] = []
        persistence_service = CharacterPersistenceService()
        for session in sessions:
            try:
                character: Optional[Character] = persistence_service.load_character_data(str(session["character_id"]))
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

@router.post("/start", response_model=StartScenarioResponse)
async def start_scenario(request: StartScenarioRequest) -> StartScenarioResponse:
    """
    Start a scenario with a specific character, return session ID and trigger initial narration with LLM.

    **Request Body:**
    ```json
    {
        "scenario_name": "Les_Pierres_du_Passe.md",
        "character_id": "87654321-4321-8765-2109-987654321def"
    }
    ```

    **Response:**
    ```json
    {
        "session_id": "12345678-1234-5678-9012-123456789abc",
        "scenario_name": "Les_Pierres_du_Passe.md",
        "character_id": "87654321-4321-8765-2109-987654321def",
        "message": "Scenario 'Les_Pierres_du_Passe.md' started successfully for character 87654321-4321-8765-2109-987654321def.",
        "llm_response": "**Esgalbar, central square of the village**\n\n*The sun slowly sets on the horizon, tinting the sky with orange hues. A light mist floats around the dry fountain...*"
    }
    ```

    **Raises:**
    - HTTPException 409: If a session already exists with the same scenario and character.
    - HTTPException 404: If the requested scenario does not exist.
    """
    log_debug("Endpoint call: gamesession/start_scenario")

    try:
        persistence_service = CharacterPersistenceService()
        character_data = persistence_service.load_character_data(str(request.character_id))
        if character_data.status == CharacterStatus.DRAFT:
            raise HTTPException(status_code=400, detail="Cannot start a scenario with a character in creation.")

        session_info: Dict[str, Any] = GameSessionService.start_scenario(request.scenario_name, UUID(request.character_id))
        session_id: str = session_info["session_id"]
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    try:
        agent, deps = build_gm_agent_pydantic(session_id, request.scenario_name)

        start_message: str = "Start the scenario and present the initial situation."

        character_json: Optional[Dict[str, Any]] = deps.character_data.model_dump() if deps.character_data else None
        if character_json:
            enriched_message: str = enrich_user_message_with_character(start_message, character_json)
        else:
            enriched_message = start_message

        result = await agent.run(
            enriched_message,
            deps=deps
        )

        deps.store.save_pydantic_history(result.all_messages())

        response_data: Dict[str, Any] = {
            **session_info,
            "llm_response": result.output
        }

        log_debug("Scenario started with LLM response", action="start_scenario", session_id=session_id, character_id=request.character_id, scenario_name=request.scenario_name)
        return StartScenarioResponse(**response_data)

    except Exception as e:
        log_debug("Error starting scenario with LLM", error=str(e), traceback=traceback.format_exc(), session_id=session_id)
        return StartScenarioResponse(**session_info, llm_response=f"Error starting scenario: {str(e)}")

@router.post("/play", response_model=PlayScenarioResponse)
async def play_scenario(session_id: UUID, request: PlayScenarioRequest) -> PlayScenarioResponse:
    """
    Send a message to the GM (LLM) to play the scenario. Automatically retrieves session info (character and scenario) and returns the complete conversation history in raw JSON format.

    **Parameters:**
    - `session_id` (UUID): Game session identifier (query parameter).
    - `request` (PlayScenarioRequest): Object containing the player's message.

    **Request Body:**
    ```json
    {
        "message": "I go to the blacksmith Thadric."
    }
    ```

    **Response:**
    ```json
    {
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

    log_debug("Endpoint call: gamesession/play_scenario", session_id=str(session_id))
    try:
        session_info: Dict[str, Any] = GameSessionService.get_session_info(str(session_id))
        character_id: str = session_info["character_id"]
        character_data = CharacterPersistenceService.load_character_data(character_id)
        if character_data.status == "in_progress":
            raise HTTPException(status_code=400, detail="Cannot play with a character in creation.")

        scenario_name: str = session_info["scenario_name"]
        agent, deps = build_gm_agent_pydantic(str(session_id), scenario_name)

        character_json: Optional[Dict[str, Any]] = deps.character_data.model_dump() if deps.character_data else None
        if character_json:
            enriched_message: str = enrich_user_message_with_character(request.message, character_json)
        else:
            enriched_message = request.message

        history = deps.store.load_pydantic_history()

        result = await agent.run(
            enriched_message,
            deps=deps,
            message_history=history
        )
        deps.store.save_pydantic_history(result.all_messages())

        log_debug("Response generated", action="play_scenario", session_id=str(session_id), character_id=character_id, scenario_name=scenario_name, user_message=request.message)

        response_json = json.loads(result.all_messages_json())
        return PlayScenarioResponse(response=response_json)

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        log_debug(
            "Error playing scenario",
            error=str(e),
            traceback=traceback.format_exc(),
            session_id=str(session_id)
        )
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.post("/play-stream")
async def play_stream(session_id: UUID, message: PlayScenarioRequest):
    """
    Send a message to the GM (LLM) and stream the response using Server-Sent Events.
    The full conversation history is saved after the stream is complete.
    """
    log_debug("Endpoint call: gamesession/play_stream", session_id=str(session_id))

    try:
        session_info = GameSessionService.get_session_info(str(session_id))
        character_id = session_info["character_id"]
        character_data = CharacterPersistenceService.load_character_data(character_id)
        if character_data.status == CharacterStatus.DRAFT:
            raise HTTPException(status_code=400, detail="Cannot play with a character in creation.")

        scenario_name = session_info["scenario_name"]
        agent, deps = build_gm_agent_pydantic(str(session_id), scenario_name)
        history = deps.store.load_pydantic_history()

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        log_debug("Error preparing stream", error=str(e), traceback=traceback.format_exc(), session_id=str(session_id))
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    async def stream_generator(
        user_message: str,
        agent: Agent[GameSessionService, str],
        history: list[ModelMessage],
        deps: GameSessionService,
    ):
        """Generator for streaming the agent's response."""
        try:
            character_json = deps.character_data.model_dump() if deps.character_data else None
            enriched_message = enrich_user_message_with_character(user_message, character_json) if character_json else user_message

            async with agent.run_stream(
                enriched_message,
                message_history=history,
                deps=deps,
            ) as stream_result:
                streamed_text = False
                text_stream_error: Optional[Exception] = None

                try:
                    async for text_chunk in stream_result.stream_text(delta=True):
                        streamed_text = True
                        payload = jsonable_encoder({"content": text_chunk, "part_kind": "text-stream"})
                        yield f"data: {json.dumps(payload, default=str)}\n\n"
                except (AttributeError, TypeError, ValueError) as stream_err:
                    text_stream_error = stream_err

                if not streamed_text:
                    if text_stream_error:
                        log_debug(
                            "Falling back to stream_responses",
                            error=str(text_stream_error),
                            session_id=str(session_id),
                        )
                    async for response, _ in stream_result.stream_responses(debounce_by=0.01):
                        if isinstance(response, BaseModel):
                            payload = json.loads(response.model_dump_json())
                        else:
                            payload = jsonable_encoder(response)
                        yield f"data: {json.dumps(payload, default=str)}\n\n"

                # After the stream is complete, save the full history
                final_messages_json = stream_result.all_messages_json()
                if final_messages_json:
                    try:
                        final_messages = json.loads(final_messages_json)
                        pydantic_history = ModelMessagesTypeAdapter.validate_python(final_messages)
                        deps.store.save_pydantic_history(pydantic_history)
                        log_debug("Stream finished and history saved", session_id=str(session_id))
                    except ValidationError as history_error:
                        log_debug(
                            "Skipping history persistence for streamed run",
                            error=str(history_error),
                            session_id=str(session_id),
                        )

        except Exception as e:
            log_debug(
                "Error during agent streaming",
                error=str(e),
                exc_info=True,
                user_message=user_message,
            )
            error_message = {
                "error": "An error occurred during the stream.",
                "details": str(e),
                "exception_type": e.__class__.__name__,
                "traceback": traceback.format_exc(),
            }
            yield f"data: {json.dumps(error_message, default=str)}\n\n"

    return StreamingResponse(
        stream_generator(message.message, agent, history, deps),
        media_type="text/event-stream",
    )


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
        session_info: Dict[str, Any] = GameSessionService.get_session_info(str(session_id))
        scenario_name: str = session_info["scenario_name"]
        _, deps = build_gm_agent_pydantic(str(session_id), scenario_name)
        history: List[Dict[str, Any]] = deps.store.read_json_history()
        return ScenarioHistoryResponse(history=history)
    except FileNotFoundError as e:
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
        session_info: Dict[str, Any] = GameSessionService.get_session_info(str(session_id))
        scenario_name: str = session_info["scenario_name"]

        agent, deps = build_gm_agent_pydantic(str(session_id), scenario_name)

        history: List[Dict[str, Any]] = deps.store.read_json_history()

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
            deps.store.save_pydantic_history(pydantic_history)
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

    except FileNotFoundError as e:
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