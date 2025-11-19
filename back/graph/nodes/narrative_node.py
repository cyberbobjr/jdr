"""
Narrative node for handling story progression.
"""

from pydantic_graph import BaseNode, GraphRunContext, End
from back.graph.dto.session import SessionGraphState, DispatchResult
from back.graph.dto.combat import CombatSeedPayload
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
        system_prompt = await ctx.deps.build_narrative_system_prompt()

        # Run the agent
        result = await self.narrative_agent.run(
            user_message=ctx.state.pending_player_message.message,
            message_history=ctx.state.model_messages or [],
            system_prompt=system_prompt,
            deps=ctx.deps
        )

        # Persist the new messages
        await ctx.deps.save_history(HISTORY_NARRATIVE, result.all_messages())

        # Handle structured output
        output = result.output
        if isinstance(output, CombatSeedPayload):
            # Transition to combat
            ctx.state.game_state.session_mode = "combat"
            ctx.state.game_state.combat_state = output.model_dump()
            await ctx.deps.update_game_state(ctx.state.game_state)
            log_debug("Transitioning to combat mode", session_id=ctx.deps.session_id)

        # Use built-in JSON serialization methods
        import json
        all_messages_json = json.loads(result.all_messages_json())
        new_messages_json = json.loads(result.new_messages_json())

        return End(DispatchResult(
            all_messages=all_messages_json,
            new_messages=new_messages_json
        ))