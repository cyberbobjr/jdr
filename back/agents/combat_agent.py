from typing import Any, Optional
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from back.graph.dto.combat import CombatTurnContinuePayload, CombatTurnEndPayload
from back.models.schema import LLMConfig
from back.services.game_session_service import GameSessionService
from back.utils.history_processors import summarize_old_messages


class CombatAgent:
    """
    ### CombatAgent
    **Description:** PydanticAI agent dedicated to combat resolution.
    Handles turns, damage, and combat state updates.
    """

    DEFAULT_SYSTEM_PROMPT = "You are a combat master for a Middle-earth RPG."

    def __init__(self, llm_config: LLMConfig):
        """
        ### __init__
        **Description:** Initialize the combat agent with LLM configuration.
        **Parameters:**
        - `llm_config` (LLMConfig): LLM configuration containing api_endpoint, api_key, model.
        """
        provider = OpenAIProvider(
            base_url=llm_config.api_endpoint,
            api_key=llm_config.api_key
        )
        model = OpenAIChatModel(
            model_name=llm_config.model,
            provider=provider
        )
        
        # Register tools
        from back.tools import combat_tools, skill_tools, equipment_tools
        self.system_prompt = ""
        self.agent = Agent(
            model=model,
            output_type=CombatTurnContinuePayload | CombatTurnEndPayload,
            deps_type=GameSessionService,
            tools=[
                combat_tools.execute_attack_tool,
                combat_tools.apply_direct_damage_tool,
                combat_tools.end_turn_tool,
                combat_tools.check_combat_end_tool,
                combat_tools.end_combat_tool,
                combat_tools.get_combat_status_tool,
                skill_tools.skill_check_with_character,
                equipment_tools.inventory_remove_item,
                equipment_tools.inventory_decrease_quantity,
                equipment_tools.inventory_increase_quantity,
            ],
            history_processors=[summarize_old_messages]
        )

        @self.agent.system_prompt
        def _inject_dynamic_system_prompt(ctx: RunContext[GameSessionService]) -> str:
            return self.system_prompt

    async def run(self, user_message: str, deps: GameSessionService, message_history: Optional[list] = None, system_prompt: str = ""):
        """
        ### run
        **Description:** Run the combat agent with user input.
        **Parameters:**
        - `user_message` (str): Player's message.
        - `message_history` (list): Previous messages.
        - `system_prompt` (str): System prompt for combat.
        - `deps` (GameSessionService): Service dependencies.
        **Returns:** Agent run result.
        """
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        return await self.agent.run(
            user_prompt=user_message,
            message_history=message_history or [],
            deps=deps
        )

    async def run_stream(self, user_message: str, deps: GameSessionService, message_history: Optional[list] = None, system_prompt: str = ""):
        """
        ### run_stream
        **Description:** Run the combat agent with streaming support.
        **Parameters:**
        - `user_message` (str): Player's message.
        - `deps` (GameSessionService): Service dependencies.
        - `message_history` (Optional[list]): Previous messages.
        - `system_prompt` (str): System prompt for combat state.
        **Returns:** Agent streaming result context manager.
        """
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT
        stream = self.agent.run_stream(
            user_prompt=user_message,
            message_history=message_history or [],
            deps=deps
        )

        return self._CombatStreamContext(stream)

    class _CombatStreamContext:
        def __init__(self, inner: Any):
            self._inner = inner

        async def __aenter__(self):
            return await self._inner.__aenter__()

        async def __aexit__(self, exc_type, exc, tb):
            return await self._inner.__aexit__(exc_type, exc, tb)

        def __aiter__(self):
            return self._inner.__aiter__()

        async def __anext__(self):
            return await self._inner.__anext__()

        def __getattr__(self, name: str) -> Any:
            return getattr(self._inner, name)