"""
Tests for NarrativeAgent.
"""

import pytest
from pydantic import ValidationError
from back.agents.narrative_agent import NarrativeAgent
from back.graph.dto.combat import CombatSeedPayload
from back.models.schema import LLMConfig


class TestNarrativeAgent:
    """Test cases for NarrativeAgent."""

    def test_init_valid_config(self):
        """Test initialization with valid LLM config."""
        llm_config = LLMConfig(
            api_endpoint="https://api.example.com",
            api_key="test_key",
            model="test-model"
        )
        agent = NarrativeAgent(llm_config)
        assert agent.agent is not None
        assert agent.agent.output_type == str | CombatSeedPayload

    def test_init_missing_api_endpoint(self):
        """Test that LLMConfig raises ValidationError with missing api_endpoint."""
        with pytest.raises(ValidationError):
            LLMConfig(  # type: ignore
                api_key="test_key",
                model="test-model"
            )

    def test_init_missing_api_key(self):
        """Test that LLMConfig raises ValidationError with missing api_key."""
        with pytest.raises(ValidationError):
            LLMConfig(  # type: ignore
                api_endpoint="https://api.example.com",
                model="test-model"
            )

    def test_init_missing_model(self):
        """Test that LLMConfig raises ValidationError with missing model."""
        with pytest.raises(ValidationError):
            LLMConfig(  # type: ignore
                api_endpoint="https://api.example.com",
                api_key="test_key"
            )

    def test_init_empty_strings(self):
        """Test initialization with empty strings."""
        llm_config = LLMConfig(
            api_endpoint="",
            api_key="",
            model=""
        )
        agent = NarrativeAgent(llm_config)
        assert agent.agent is not None