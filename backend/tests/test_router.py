"""Tests for RouterAgent."""

import pytest
from langchain_core.messages import HumanMessage

from solutions.resume_dashboard.agents.router import RouterAgent
from solutions.resume_dashboard.agents.base import ConversationState


class TestRouterAgent:
    """Test suite for RouterAgent routing logic."""

    @pytest.fixture
    def router_agent(self, mock_groq_api_key):
        """Create RouterAgent instance for testing."""
        return RouterAgent()

    @pytest.fixture
    def conversation_state(self):
        """Create a mock conversation state."""
        return ConversationState(
            session_id="test-session",
            token="test-token",
            company="test-company"
        )

    def test_router_initialization(self, router_agent):
        """Test that router initializes correctly."""
        assert router_agent.name == "Router"
        assert router_agent.llm is not None
        assert router_agent.temperature == 0.3

    def test_router_has_correct_system_prompt(self, router_agent):
        """Test that router has proper system prompt with agent descriptions."""
        system_prompt = router_agent._get_system_prompt()

        # Check that all required agents are mentioned
        assert "INTERVIEW" in system_prompt
        assert "TECHNICAL" in system_prompt
        assert "PERSONAL" in system_prompt
        assert "BACKGROUND" in system_prompt
        assert "HELP" in system_prompt

        # Check descriptions are included
        assert "programming languages" in system_prompt.lower()
        assert "interview" in system_prompt.lower()

    def test_router_process_returns_valid_structure(self, router_agent, conversation_state):
        """Test that router process returns expected structure."""
        message = "What programming languages do you know?"
        result = router_agent.process(message, conversation_state)

        # Check result structure
        assert "agent" in result
        assert "confidence" in result
        assert result["agent"] in ["interview", "technical", "personal", "background", "help"]
        assert 0 <= result["confidence"] <= 1

    def test_router_route_returns_tuple(self, router_agent, conversation_state):
        """Test that route method returns (agent_name, confidence) tuple."""
        message = "Tell me about your skills"
        agent_name, confidence = router_agent.route(message, conversation_state)

        assert isinstance(agent_name, str)
        assert isinstance(confidence, float)
        assert agent_name in ["interview", "technical", "personal", "background", "help"]
        assert 0 <= confidence <= 1
