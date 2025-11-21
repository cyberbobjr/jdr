"""
Narrative agent for story progression.
"""

from typing import Any, Optional
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from back.graph.dto.combat import CombatSeedPayload
from back.graph.dto.scenario import ScenarioEndPayload
from back.models.schema import LLMConfig
from back.services.game_session_service import GameSessionService


class NarrativeAgent:
    """
    ### NarrativeAgent
    **Description:** PydanticAI agent dedicated to narrative progression.
    Handles story advancement and triggers combat when appropriate.
    """

    def __init__(self, llm_config: LLMConfig):
        """
        ### __init__
        **Description:** Initialize the narrative agent with LLM configuration.
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
        from back.tools import equipment_tools, character_tools, combat_tools, scenario_tools, skill_tools
        
        self.system_prompt = ""
        self.agent = Agent(
            model=model,
            output_type=str | CombatSeedPayload | ScenarioEndPayload,
            deps_type=GameSessionService,
            tools=[
                equipment_tools.inventory_buy_item,
                equipment_tools.inventory_add_item,
                equipment_tools.inventory_remove_item,
                equipment_tools.list_available_equipment,
                character_tools.character_add_currency,
                skill_tools.skill_check_with_character,
                character_tools.character_take_damage,
                character_tools.character_heal,
                character_tools.character_apply_xp,
                combat_tools.start_combat_tool,
                scenario_tools.end_scenario_tool,
            ]
        )

        @self.agent.system_prompt
        def _inject_dynamic_system_prompt(ctx: RunContext[GameSessionService]) -> str:
            return self.system_prompt

    async def run(self, user_message: str, deps: GameSessionService, message_history: Optional[list] = None, system_prompt: str = ""):
        """
        ### run
        **Description:** Run the narrative agent with user input.
        **Parameters:**
        - `user_message` (str): Player's message.
        - `deps` (GameSessionService): Service dependencies.
        - `message_history` (Optional[list]): Previous messages.
        - `system_prompt` (str): System prompt for the scenario.
        **Returns:** Agent run result.
        """
        self.system_prompt = system_prompt or "You are a game master for a Middle-earth RPG."
        
        return await self.agent.run(
            user_prompt=user_message,
            message_history=message_history or [],
            deps=deps
        )

    async def run_stream(self, user_message: str, deps: GameSessionService, message_history: Optional[list] = None, system_prompt: str = ""):
        """
        ### run_stream
        **Description:** Run the narrative agent with streaming support.
        **Parameters:**
        - `user_message` (str): Player's message.
        - `deps` (GameSessionService): Service dependencies.
        - `message_history` (Optional[list]): Previous messages.
        - `system_prompt` (str): System prompt for the scenario.
        **Returns:** Agent streaming result context manager.
        """
        self.system_prompt = system_prompt or "You are a game master for a Middle-earth RPG."

        stream = self.agent.run_stream(
            user_prompt=user_message,
            message_history=message_history or [],
            deps=deps
        )

        return self._NarrativeStreamContext(stream)

    class _NarrativeStreamContext:
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