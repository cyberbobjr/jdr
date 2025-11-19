"""
Combat node for handling combat turns.
"""

from pydantic_graph import BaseNode, GraphRunContext, End
from back.graph.dto.session import SessionGraphState, DispatchResult
from back.graph.dto.combat import CombatTurnEndPayload
from back.agents.combat_agent import CombatAgent
from back.utils.logger import log_debug
from back.services.game_session_service import GameSessionService, HISTORY_NARRATIVE, HISTORY_COMBAT


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
        self.combat_agent = CombatAgent()

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

        # Build system prompt with combat state
        system_prompt = await ctx.deps.build_combat_prompt(ctx.state.game_state.combat_state) # type: ignore

        # Run the agent
        result = await self.combat_agent.run(
            user_message=ctx.state.pending_player_message.message,
            message_history=ctx.state.model_messages or [],
            system_prompt=system_prompt
        )

        # Persist the new messages
        await ctx.deps.save_history(HISTORY_COMBAT, result.all_messages())

        # Handle structured output
        output = result.output
        if isinstance(output, CombatTurnEndPayload):
            # End combat
            ctx.state.game_state.session_mode = "narrative"
            ctx.state.game_state.last_combat_result = output.model_dump()
            ctx.state.game_state.combat_state = None  # Clear combat state
            await ctx.deps.update_game_state(ctx.state.game_state)
            log_debug("Ending combat mode", session_id=ctx.deps.session_id)
        else:
            # Continue combat, combat_state already updated by tools
            await ctx.deps.update_game_state(ctx.state.game_state)

        # Use built-in JSON serialization methods
        import json
        all_messages_json = json.loads(result.all_messages_json())
        new_messages_json = json.loads(result.new_messages_json())

        return End(DispatchResult(
            all_messages=all_messages_json,
            new_messages=new_messages_json
        ))