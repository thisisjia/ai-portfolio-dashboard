"""Integration tests for RouterAgent with mocked LLM calls."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.messages import AIMessage

from solutions.resume_dashboard.agents.router import RouterAgent
from solutions.resume_dashboard.agents.base import ConversationState


class TestRouterIntegration:
    """Test RouterAgent with mocked Groq API responses."""

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

    @patch('solutions.resume_dashboard.agents.router.ChatGroq.invoke')
    def test_route_technical_question_to_technical_agent(self, mock_invoke, router_agent, conversation_state):
        """Test that technical questions route to technical agent."""
        # Mock LLM response
        mock_response = AIMessage(content="TECHNICAL")
        mock_invoke.return_value = mock_response

        message = "What programming languages do you know?"
        agent_name, confidence = router_agent.route(message, conversation_state)

        # Verify LLM was called
        assert mock_invoke.called
        # Verify routing decision
        assert agent_name == "technical"
        assert confidence == 0.9

    @patch('solutions.resume_dashboard.agents.router.ChatGroq.invoke')
    def test_route_interview_question_to_interview_agent(self, mock_invoke, router_agent, conversation_state):
        """Test that interview questions route to interview agent."""
        mock_response = AIMessage(content="INTERVIEW")
        mock_invoke.return_value = mock_response

        message = "Tell me about a time you overcame a challenge"
        agent_name, confidence = router_agent.route(message, conversation_state)

        assert mock_invoke.called
        assert agent_name == "interview"
        assert confidence == 0.9

    @patch('solutions.resume_dashboard.agents.router.ChatGroq.invoke')
    def test_route_personal_question_to_personal_agent(self, mock_invoke, router_agent, conversation_state):
        """Test that personal questions route to personal agent."""
        mock_response = AIMessage(content="PERSONAL")
        mock_invoke.return_value = mock_response

        message = "What motivates you in your work?"
        agent_name, confidence = router_agent.route(message, conversation_state)

        assert mock_invoke.called
        assert agent_name == "personal"
        assert confidence == 0.9

    @patch('solutions.resume_dashboard.agents.router.ChatGroq.invoke')
    def test_route_background_question_to_background_agent(self, mock_invoke, router_agent, conversation_state):
        """Test that background questions route to background agent."""
        mock_response = AIMessage(content="BACKGROUND")
        mock_invoke.return_value = mock_response

        message = "Where did you go to university?"
        agent_name, confidence = router_agent.route(message, conversation_state)

        assert mock_invoke.called
        assert agent_name == "background"
        assert confidence == 0.9

    @patch('solutions.resume_dashboard.agents.router.ChatGroq.invoke')
    def test_route_unclear_message_to_help_agent(self, mock_invoke, router_agent, conversation_state):
        """Test that unclear messages default to help agent."""
        mock_response = AIMessage(content="HELP")
        mock_invoke.return_value = mock_response

        message = "asdfghjkl"
        agent_name, confidence = router_agent.route(message, conversation_state)

        assert mock_invoke.called
        assert agent_name == "help"

    @patch('solutions.resume_dashboard.agents.router.ChatGroq.invoke')
    def test_route_handles_lowercase_response(self, mock_invoke, router_agent, conversation_state):
        """Test that router handles lowercase LLM responses."""
        mock_response = AIMessage(content="technical")  # lowercase
        mock_invoke.return_value = mock_response

        message = "What technologies do you use?"
        agent_name, confidence = router_agent.route(message, conversation_state)

        assert agent_name == "technical"

    @patch('solutions.resume_dashboard.agents.router.ChatGroq.invoke')
    def test_route_handles_invalid_response_gracefully(self, mock_invoke, router_agent, conversation_state):
        """Test that router defaults to help on invalid LLM response."""
        mock_response = AIMessage(content="INVALID_AGENT")
        mock_invoke.return_value = mock_response

        message = "Some question"
        agent_name, confidence = router_agent.route(message, conversation_state)

        # Should default to help agent
        assert agent_name == "help"
        assert confidence == 0.5

    @patch('solutions.resume_dashboard.agents.router.ChatGroq.invoke')
    def test_router_includes_conversation_context(self, mock_invoke, router_agent):
        """Test that router includes conversation history in routing decision."""
        # Create state with message history
        from langchain_core.messages import HumanMessage, AIMessage as AIMsg

        state = ConversationState(
            session_id="test-session",
            token="test-token",
            company="test-company",
            messages=[
                HumanMessage(content="What are your skills?"),
                AIMsg(content="I have skills in Python and JavaScript")
            ]
        )

        mock_response = AIMessage(content="TECHNICAL")
        mock_invoke.return_value = mock_response

        message = "Tell me more about Python"
        agent_name, confidence = router_agent.route(message, state)

        # Verify invoke was called with context
        assert mock_invoke.called
        call_args = mock_invoke.call_args[0][0]
        # Context should be built from message history
        assert agent_name == "technical"

    @patch('solutions.resume_dashboard.agents.router.ChatGroq.invoke')
    def test_router_handles_api_error(self, mock_invoke, router_agent, conversation_state):
        """Test that router handles Groq API errors gracefully."""
        # Simulate API error
        mock_invoke.side_effect = Exception("API connection failed")

        message = "What are your skills?"

        # Router should handle error and potentially default to help
        with pytest.raises(Exception):
            router_agent.route(message, conversation_state)
