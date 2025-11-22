"""
Combat node for handling combat turns.
"""

from pydantic_graph import BaseNode, GraphRunContext, End
from back.graph.dto.session import SessionGraphState, DispatchResult
from back.graph.dto.combat import CombatTurnEndPayload
from back.agents.combat_agent import CombatAgent
from back.utils.logger import log_debug
from back.services.game_session_service import GameSessionService, HISTORY_NARRATIVE, HISTORY_COMBAT
from back.config import get_llm_config


class CombatNode(BaseNode[SessionGraphState, GameSessionService, DispatchResult]):
    """
    ### CombatNode
    **SessionGraphState:** state of the graph
    **GameSessionService:** dependency injection
    **DispatchResult:** result of the node
    **Description:** Handles combat turns using the CombatAgent.
    Processes player actions and manages combat state.
    **Returns:** End with DispatchResult.
    """

    def __init__(self):
        """
        ### __init__
        **Description:** Initialize with a CombatAgent instance.
        """
        llm_config = get_llm_config()
        self.combat_agent = CombatAgent(llm_config)

    async def run(
        self, ctx: GraphRunContext[SessionGraphState, GameSessionService]
    ) -> End[DispatchResult]:
        """
        ### run
        **Description:** Run the combat agent and handle responses.
        **Parameters:**
        - `ctx` (GraphRunContext[SessionGraphState]): Graph context with state.
        **Returns:** End with DispatchResult containing response parts.
        """
        log_debug("Running CombatNode", session_id=ctx.deps.session_id)

        # Load the active combat state
        from back.services.combat_state_service import CombatStateService
        combat_state_service = CombatStateService()
        
        # Ensure we have a session ID (should be in deps)
        session_id_uuid = ctx.deps.session_id
        # Convert to UUID if it's a string (GameSessionService stores it as string usually, but let's be safe)
        import uuid
        if isinstance(session_id_uuid, str):
            session_id_uuid = uuid.UUID(session_id_uuid)

        combat_state = combat_state_service.load_combat_state(session_id_uuid)
        
        if not combat_state:
            # Fallback if no combat state found but we are in combat mode
            # This shouldn't happen if flow is correct, but safety net:
            log_debug("No active combat state found in CombatNode, reverting to narrative", session_id=ctx.deps.session_id)
            ctx.state.game_state.session_mode = "narrative"
            ctx.state.game_state.active_combat_id = None
            await ctx.deps.update_game_state(ctx.state.game_state)
            return End(DispatchResult(
                all_messages=[],
                new_messages=[{"role": "system", "content": "Combat state lost. Returning to narrative mode."}]
            ))

        # Build system prompt with loaded combat state
        from back.services.settings_service import SettingsService
        settings_service = SettingsService()
        language = settings_service.get_preferences().language

        system_prompt = await ctx.deps.build_combat_prompt(combat_state, language)

        # Load LLM-specific history (summarized)
        llm_history = await ctx.deps.load_history_llm(HISTORY_COMBAT)
        
        if not llm_history:
             llm_history = await ctx.deps.load_history(HISTORY_COMBAT)

        # Run the agent
        result = await self.combat_agent.run(
            user_message=ctx.state.pending_player_message.message,
            message_history=llm_history,
            system_prompt=system_prompt,
            deps=ctx.deps
        )

        # Persist the new LLM history
        await ctx.deps.save_history_llm(HISTORY_COMBAT, result.all_messages())

        # Update Full History
        full_history = await ctx.deps.load_history(HISTORY_COMBAT)
        full_history.extend(result.new_messages())
        await ctx.deps.save_history(HISTORY_COMBAT, full_history)

        # Handle structured output
        output = result.output
        if isinstance(output, CombatTurnEndPayload):
            # End combat
            ctx.state.game_state.session_mode = "narrative"
            ctx.state.game_state.last_combat_result = output.model_dump()
            ctx.state.game_state.active_combat_id = None  # Clear active combat
            
            # TODO: Handle Player Death gracefully.
            # If the player died (see last_combat_result), we should probably transition to a "Game Over" or "Unconscious" state
            # rather than just returning to narrative mode as if nothing happened.
            
            await ctx.deps.update_game_state(ctx.state.game_state)
            log_debug("Ending combat mode", session_id=ctx.deps.session_id)
        else:
            # Continue combat
            # Note: We don't need to save combat_state here as tools update it directly via CombatStateService
            await ctx.deps.update_game_state(ctx.state.game_state)

        # Use built-in JSON serialization methods
        import json
        from pydantic_ai.messages import ModelMessage
        from pydantic import TypeAdapter
        
        ta = TypeAdapter(list[ModelMessage])
        all_messages_json = json.loads(ta.dump_json(full_history))
        new_messages_json = json.loads(result.new_messages_json())

        return End(DispatchResult(
            all_messages=all_messages_json,
            new_messages=new_messages_json
        ))