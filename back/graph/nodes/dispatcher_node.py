"""
Dispatcher node for routing between narrative and combat modes.
"""

from typing import Any
from pydantic_graph import BaseNode, GraphRunContext, End
from back.graph.dto.session import SessionGraphState, DispatchResult
from back.graph.nodes.narrative_node import NarrativeNode
from back.graph.nodes.combat_node import CombatNode
from back.services.game_session_service import GameSessionService, HISTORY_NARRATIVE, HISTORY_COMBAT


class DispatcherNode(BaseNode[SessionGraphState, GameSessionService, DispatchResult]):
    """
    ### DispatcherNode
    **Description:** Routes the session to the appropriate node based on session_mode.
    Loads the relevant history into the state.
    **Returns:** NarrativeNode or CombatNode based on mode.
    """

    async def run(
        self, ctx: GraphRunContext[SessionGraphState, GameSessionService]
    ) -> NarrativeNode | CombatNode:
        """
        ### run
        **Description:** Determine the current mode and load the appropriate history.
        **Parameters:**
        - `ctx` (GraphRunContext[SessionGraphState]): Graph context with state.
        **Returns:** Next node to run (NarrativeNode or CombatNode).
        """
        mode = ctx.state.game_state.session_mode
        history_kind = HISTORY_NARRATIVE if mode == "narrative" else HISTORY_COMBAT

        # Load history from GameSessionService
        ctx.state.model_messages = await ctx.deps.load_history(history_kind)
        ctx.state.active_history_kind = history_kind

        if mode == "narrative":
            return NarrativeNode()
        else:
            return CombatNode()