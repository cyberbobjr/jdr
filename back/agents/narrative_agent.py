"""
Narrative agent for story progression.
"""

from typing import Optional
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from back.graph.dto.combat import CombatSeedPayload
from back.config import get_llm_config


class NarrativeAgent:
    """
    ### NarrativeAgent
    **Description:** PydanticAI agent dedicated to narrative progression.
    Handles story advancement and triggers combat when appropriate.
    """

    def __init__(self):
        """
        ### __init__
        **Description:** Initialize the narrative agent with appropriate configuration.
        """
        llm_config = get_llm_config()
        provider = OpenAIProvider(
            base_url=llm_config["api_endpoint"],
            api_key=llm_config["api_key"]
        )
        model = OpenAIChatModel(
            model_name=llm_config["model"],
            provider=provider
        )
        self.agent = Agent(
            model=model,
            output_type=str | CombatSeedPayload,
        )

    async def run(self, user_message: str, message_history: Optional[list] = None, system_prompt: str = ""):
        """
        ### run
        **Description:** Run the narrative agent with user input.
        **Parameters:**
        - `user_message` (str): Player's message.
        - `message_history` (Optional[list]): Previous messages.
        - `system_prompt` (str): System prompt for the scenario.
        **Returns:** Agent run result.
        """
        # Create a new agent with the system prompt
        agent = Agent(
            model=self.agent.model,
            output_type=self.agent.output_type,
            system_prompt=system_prompt or "You are a game master for a Middle-earth RPG."
        )

        return await agent.run(
            user_prompt=user_message,
            message_history=message_history or []
        )

    async def run_stream(self, user_message: str, message_history: Optional[list] = None, system_prompt: str = ""):
        """
        ### run_stream
        **Description:** Run the narrative agent with streaming support.
        **Parameters:**
        - `user_message` (str): Player's message.
        - `message_history` (Optional[list]): Previous messages.
        - `system_prompt` (str): System prompt for the scenario.
        **Returns:** Agent streaming result context manager.
        """
        # Create a new agent with the system prompt
        agent = Agent(
            model=self.agent.model,
            output_type=self.agent.output_type,
            system_prompt=system_prompt or "You are a game master for a Middle-earth RPG."
        )

        return agent.run_stream(
            user_prompt=user_message,
            message_history=message_history or []
        )