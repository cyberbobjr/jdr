"""
Narrative node for handling story progression.
"""

from pydantic_graph import BaseNode, GraphRunContext, End
from back.graph.dto.session import SessionGraphState, DispatchResult
from back.graph.dto.combat import CombatSeedPayload
from back.graph.dto.scenario import ScenarioEndPayload
from back.agents.narrative_agent import NarrativeAgent
from back.utils.logger import log_debug
from back.services.game_session_service import GameSessionService, HISTORY_NARRATIVE, HISTORY_COMBAT
from back.config import get_llm_config


class NarrativeNode(BaseNode[SessionGraphState, GameSessionService, DispatchResult]):
    """
    ### NarrativeNode
    **Description:** Handles narrative progression using the NarrativeAgent.
    Processes player messages and manages transitions to combat.
    **Returns:** End with DispatchResult.
    """

    def __init__(self):
        """
        ### __init__
        **Description:** Initialize with a NarrativeAgent instance.
        """
        llm_config = get_llm_config()
        self.narrative_agent = NarrativeAgent(llm_config)

    async def run(
        self, ctx: GraphRunContext[SessionGraphState, GameSessionService]
    ) -> End[DispatchResult]:
        """
        ### run
        **Description:** Run the narrative agent and handle responses.
        **Parameters:**
        - `ctx` (GraphRunContext[SessionGraphState]): Graph context with state.
        **Returns:** End with DispatchResult containing response parts.
        """
        log_debug("Running NarrativeNode", session_id=ctx.deps.session_id)

        # Build system prompt with scenario
        from back.services.settings_service import SettingsService
        settings_service = SettingsService()
        language = settings_service.get_preferences().language
        
        system_prompt = await ctx.deps.build_narrative_system_prompt(language)

        # Load LLM-specific history (summarized)
        llm_history = await ctx.deps.load_history_llm(HISTORY_NARRATIVE)
        
        # If LLM history is empty but full history exists (migration or first run), 
        # we might want to seed it from full history or just start fresh.
        # For now, if empty, we pass empty list (or let agent handle it).
        # But we must ensure we don't lose context on first run.
        if not llm_history:
             # Fallback to full history if LLM history is missing (e.g. first run after feature add)
             llm_history = await ctx.deps.load_history(HISTORY_NARRATIVE)

        # Run the agent with LLM history
        result = await self.narrative_agent.run(
            user_message=ctx.state.pending_player_message.message,
            message_history=llm_history,
            system_prompt=system_prompt,
            deps=ctx.deps
        )

        # Persist the new LLM history (which might include the summary now)
        await ctx.deps.save_history_llm(HISTORY_NARRATIVE, result.all_messages())

        # Update Full History (Source of Truth for UI)
        # We load the full history, append the NEW messages from the agent result, and save.
        full_history = await ctx.deps.load_history(HISTORY_NARRATIVE)
        
        # We need to append the user message and the model response(s)
        # result.new_messages() contains exactly that.
        full_history.extend(result.new_messages())
        
        await ctx.deps.save_history(HISTORY_NARRATIVE, full_history)

        # Handle structured output
        output = result.output
        if isinstance(output, CombatSeedPayload):
            # Load the full combat state that was initialized by the tool
            from back.services.combat_state_service import CombatStateService
            combat_state_service = CombatStateService()
            
            # We need the session_id to load the state
            session_id = ctx.deps.session_id
            # Ensure session_id is a UUID if needed, but load_combat_state likely takes UUID
            import uuid
            try:
                session_uuid = uuid.UUID(session_id)
                combat_state = combat_state_service.load_combat_state(session_uuid)
                
                if combat_state:
                    # Transition to combat
                    ctx.state.game_state.session_mode = "combat"
                    ctx.state.game_state.active_combat_id = combat_state.id
                    log_debug("Transitioning to combat mode", session_id=ctx.deps.session_id)
                else:
                    log_debug("Failed to load combat state after seed", session_id=session_id)
            except Exception as e:
                 log_debug(f"Error loading combat state: {e}", session_id=session_id)

            await ctx.deps.update_game_state(ctx.state.game_state)

        # Check for player death (automatic detection)
        if ctx.deps.character_service:
            character = ctx.deps.character_service.get_character()
            if character and character.combat_stats.current_hit_points <= 0:
                # Force scenario end due to death
                output = ScenarioEndPayload(
                    outcome="death",
                    summary=f"{character.name} has fallen. The adventure ends here."
                )
                log_debug("Player death detected, ending scenario", session_id=ctx.deps.session_id)

        # Handle scenario end
        if isinstance(output, ScenarioEndPayload):
            # Update game state with scenario end information
            ctx.state.game_state.scenario_status = output.outcome
            ctx.state.game_state.scenario_end_summary = output.summary
            await ctx.deps.update_game_state(ctx.state.game_state)
            
            log_debug(
                f"Scenario ended: {output.outcome}",
                session_id=ctx.deps.session_id,
                outcome=output.outcome,
                rewards=output.rewards
            )

        # Use built-in JSON serialization methods
        # We want to return the FULL history to the UI, not the summarized LLM history.
        # We need to serialize full_history.
        from back.storage.pydantic_jsonl_store import PydanticJsonlStore
        # Helper to serialize list of messages
        # Since we don't have a direct helper on result for arbitrary list, we use the store's helper or manual.
        # PydanticJsonlStore has to_json methods? No, but we can use TypeAdapter or similar if needed.
        # Actually, result.new_messages_json() is fine for the delta.
        # For all_messages, we should return the full_history we just saved.
        
        # We can reuse the logic from PydanticJsonlStore or just rely on the fact that 
        # the UI might reload history or we send it here.
        # Let's try to serialize full_history using pydantic-ai's internal tools if accessible, 
        # or just use the result's new messages and let the UI append them?
        # The DispatchResult expects all_messages and new_messages.
        
        # Hack: We use the result's new_messages_json for the delta.
        # For all_messages, we need to serialize full_history.
        # Since full_history is a list of ModelMessage, we can use the same serialization as PydanticAI.
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