"""Tests for specialized agents."""

import pytest

from src.agents.technical import TechnicalAgent
from src.agents.personal import PersonalAgent
from src.agents.background import BackgroundAgent
from src.agents.base import ConversationState, AgentResponse


class TestTechnicalAgent:
    """Test suite for TechnicalAgent."""

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

    def test_technical_agent_initialization(self, technical_agent):
        """Test that technical agent initializes correctly."""
        assert technical_agent.name == "Technical"
        assert technical_agent.llm is not None
        assert technical_agent.resume_data is not None

    def test_technical_agent_has_resume_data(self, technical_agent, sample_resume_data):
        """Test that technical agent loads resume data."""
        assert "skills" in technical_agent.resume_data or technical_agent.resume_data == sample_resume_data
        assert technical_agent.resume_data is not None

    def test_technical_agent_system_prompt_exists(self, technical_agent):
        """Test that technical agent has proper system prompt."""
        system_prompt = technical_agent._get_system_prompt()
        assert len(system_prompt) > 0
        assert "technical" in system_prompt.lower() or "skill" in system_prompt.lower()


class TestPersonalAgent:
    """Test suite for PersonalAgent."""

    @pytest.fixture
    def personal_agent(self, mock_groq_api_key, sample_resume_data):
        """Create PersonalAgent instance."""
        return PersonalAgent(resume_data=sample_resume_data)

    def test_personal_agent_initialization(self, personal_agent):
        """Test that personal agent initializes correctly."""
        assert personal_agent.name == "Personal"
        assert personal_agent.llm is not None

    def test_personal_agent_system_prompt_exists(self, personal_agent):
        """Test that personal agent has proper system prompt."""
        system_prompt = personal_agent._get_system_prompt()
        assert len(system_prompt) > 0
        assert "personal" in system_prompt.lower() or "personality" in system_prompt.lower() or "motivation" in system_prompt.lower()


class TestBackgroundAgent:
    """Test suite for BackgroundAgent."""

    @pytest.fixture
    def background_agent(self, mock_groq_api_key, sample_resume_data):
        """Create BackgroundAgent instance."""
        return BackgroundAgent(resume_data=sample_resume_data)

    def test_background_agent_initialization(self, background_agent):
        """Test that background agent initializes correctly."""
        assert background_agent.name == "Background"
        assert background_agent.llm is not None

    def test_background_agent_system_prompt_mentions_education_or_experience(self, background_agent):
        """Test that background agent prompt mentions education or work history."""
        system_prompt = background_agent._get_system_prompt()
        assert len(system_prompt) > 0
        keywords = ["background", "education", "experience", "work", "history"]
        assert any(keyword in system_prompt.lower() for keyword in keywords)


class TestAgentResponse:
    """Test AgentResponse model validation."""

    def test_valid_agent_response(self):
        """Test that valid AgentResponse is created correctly."""
        response = AgentResponse(
            content="Test response",
            agent_name="Test",
            confidence=0.85
        )
        assert response.content == "Test response"
        assert response.agent_name == "Test"
        assert response.confidence == 0.85
        assert 0 <= response.confidence <= 1

    def test_confidence_must_be_between_0_and_1(self):
        """Test that confidence must be in valid range."""
        # Valid confidence at boundaries
        response_0 = AgentResponse(content="Test", agent_name="Test", confidence=0.0)
        response_1 = AgentResponse(content="Test", agent_name="Test", confidence=1.0)
        assert response_0.confidence == 0.0
        assert response_1.confidence == 1.0

        # Invalid confidence should raise validation error
        with pytest.raises(Exception):
            AgentResponse(content="Test", agent_name="Test", confidence=1.5)

        with pytest.raises(Exception):
            AgentResponse(content="Test", agent_name="Test", confidence=-0.1)


class TestConversationState:
    """Test ConversationState model."""

    def test_conversation_state_initialization(self):
        """Test that ConversationState initializes correctly."""
        state = ConversationState(
            session_id="test-123",
            token="test-token",
            company="test-company"
        )
        assert state.session_id == "test-123"
        assert state.token == "test-token"
        assert state.company == "test-company"
        assert state.messages == []
        assert state.current_agent is None
        assert state.agent_history == []
