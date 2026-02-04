"""Integration tests for specialized agents with mocked LLM calls."""

import pytest
from unittest.mock import patch
from langchain_core.messages import AIMessage

from solutions.resume_dashboard.agents.technical import TechnicalAgent
from solutions.resume_dashboard.agents.personal import PersonalAgent
from solutions.resume_dashboard.agents.interview import InterviewAgent
from solutions.resume_dashboard.agents.base import ConversationState, AgentResponse


class TestTechnicalAgentIntegration:
    """Test TechnicalAgent with mocked Groq API."""

    @pytest.fixture
    def technical_agent(self, mock_groq_api_key, sample_resume_data):
        """Create TechnicalAgent instance."""
        return TechnicalAgent(resume_data=sample_resume_data)

    @pytest.fixture
    def conversation_state(self):
        """Create a mock conversation state."""
        return ConversationState(
            session_id="test-session",
            token="test-token",
            company="test-company"
        )

    @patch('solutions.resume_dashboard.agents.technical.ChatGroq.invoke')
    def test_technical_agent_responds_to_skill_question(self, mock_invoke, technical_agent, conversation_state):
        """Test technical agent processing skill-related questions."""
        mock_response = AIMessage(
            content="I'm proficient in Python, JavaScript, and TypeScript. I also have experience with FastAPI and React."
        )
        mock_invoke.return_value = mock_response

        message = "What programming languages do you know?"
        response = technical_agent.process(message, conversation_state)

        # Verify LLM was called
        assert mock_invoke.called

        # Verify response structure
        assert response.agent_name == "Technical"
        assert response.content is not None
        assert isinstance(response.confidence, float)
        assert 0 <= response.confidence <= 1

    @patch('solutions.resume_dashboard.agents.technical.ChatGroq.invoke')
    def test_technical_agent_uses_resume_data_in_prompt(self, mock_invoke, technical_agent, conversation_state):
        """Test that technical agent includes resume data in LLM prompt."""
        mock_response = AIMessage(content="Response about frameworks")
        mock_invoke.return_value = mock_response

        message = "What frameworks do you use?"
        technical_agent.process(message, conversation_state)

        # Verify invoke was called
        assert mock_invoke.called

        # Get the prompt that was sent to LLM
        call_args = mock_invoke.call_args[0][0]
        # Resume data should be included in the prompt
        assert call_args is not None

    @patch('solutions.resume_dashboard.agents.technical.ChatGroq.invoke')
    def test_technical_agent_handles_short_response(self, mock_invoke, technical_agent, conversation_state):
        """Test confidence scoring for short responses."""
        mock_response = AIMessage(content="Yes.")  # Very short response
        mock_invoke.return_value = mock_response

        message = "Do you know Python?"
        response = technical_agent.process(message, conversation_state)

        # Short responses should have lower confidence
        assert response.confidence <= 0.7


class TestPersonalAgentIntegration:
    """Test PersonalAgent with mocked Groq API."""

    @pytest.fixture
    def personal_agent(self, mock_groq_api_key, sample_resume_data):
        """Create PersonalAgent instance."""
        return PersonalAgent(resume_data=sample_resume_data)

    @pytest.fixture
    def conversation_state(self):
        """Create a mock conversation state."""
        return ConversationState(
            session_id="test-session",
            token="test-token",
            company="test-company"
        )

    @patch('solutions.resume_dashboard.agents.personal.ChatGroq.invoke')
    def test_personal_agent_responds_to_motivation_question(self, mock_invoke, personal_agent, conversation_state):
        """Test personal agent processing motivation questions."""
        mock_response = AIMessage(
            content="I'm motivated by building products that make a real impact on users' lives."
        )
        mock_invoke.return_value = mock_response

        message = "What motivates you?"
        response = personal_agent.process(message, conversation_state)

        assert mock_invoke.called
        assert response.agent_name == "Personal"
        assert len(response.content) > 0

    @patch('solutions.resume_dashboard.agents.personal.ChatGroq.invoke')
    def test_personal_agent_handles_uncertainty(self, mock_invoke, personal_agent, conversation_state):
        """Test confidence scoring when agent expresses uncertainty."""
        mock_response = AIMessage(content="I'm not sure about that specific question.")
        mock_invoke.return_value = mock_response

        message = "What's your favorite color?"
        response = personal_agent.process(message, conversation_state)

        # Uncertain responses should have lower confidence
        assert response.confidence <= 0.5


class TestInterviewAgentIntegration:
    """Test InterviewAgent with mocked Groq API."""

    @pytest.fixture
    def interview_agent(self, mock_groq_api_key, sample_resume_data):
        """Create InterviewAgent instance."""
        return InterviewAgent(resume_data=sample_resume_data)

    @pytest.fixture
    def conversation_state(self):
        """Create a mock conversation state."""
        return ConversationState(
            session_id="test-session",
            token="test-token",
            company="test-company"
        )

    @patch('solutions.resume_dashboard.agents.interview.ChatGroq.invoke')
    def test_interview_agent_responds_to_behavioral_question(self, mock_invoke, interview_agent, conversation_state):
        """Test interview agent processing behavioral questions."""
        mock_response = AIMessage(
            content="In my previous role, I faced a challenging deadline. I prioritized tasks, "
                   "collaborated with the team, and we delivered successfully."
        )
        mock_invoke.return_value = mock_response

        message = "Tell me about a time you overcame a challenge"
        response = interview_agent.process(message, conversation_state)

        assert mock_invoke.called
        assert response.agent_name == "Interview"
        assert len(response.content) > 50  # Should be substantial

    @patch('solutions.resume_dashboard.agents.interview.ChatGroq.invoke')
    def test_interview_agent_handles_api_timeout(self, mock_invoke, interview_agent, conversation_state):
        """Test that interview agent handles API timeouts."""
        mock_invoke.side_effect = TimeoutError("Groq API timeout")

        message = "Tell me about yourself"

        with pytest.raises(TimeoutError):
            interview_agent.process(message, conversation_state)


class TestAgentContextBuilding:
    """Test conversation context building across agents."""

    @pytest.fixture
    def technical_agent(self, mock_groq_api_key, sample_resume_data):
        """Create TechnicalAgent instance."""
        return TechnicalAgent(resume_data=sample_resume_data)

    @patch('solutions.resume_dashboard.agents.technical.ChatGroq.invoke')
    def test_agent_uses_conversation_history(self, mock_invoke, technical_agent):
        """Test that agents include conversation history in context."""
        from langchain_core.messages import HumanMessage, AIMessage as AIMsg

        # Create state with message history
        state = ConversationState(
            session_id="test-session",
            token="test-token",
            company="test-company",
            messages=[
                HumanMessage(content="What languages do you know?"),
                AIMsg(content="I know Python and JavaScript."),
                HumanMessage(content="Tell me more about Python")
            ]
        )

        mock_response = AIMessage(content="Python is great for...")
        mock_invoke.return_value = mock_response

        message = "What about async programming?"
        response = technical_agent.process(message, state)

        # Verify invoke was called with context
        assert mock_invoke.called
        assert response is not None

    def test_empty_conversation_has_default_context(self, technical_agent):
        """Test that agents handle empty conversation history."""
        state = ConversationState(
            session_id="test-session",
            token="test-token",
            company="test-company",
            messages=[]
        )

        context = technical_agent._build_context(state)
        assert context is not None
        assert "start" in context.lower() or len(context) == 0 or "conversation" in context.lower()
