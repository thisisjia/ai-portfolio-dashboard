"""Technical skills specialist agent."""

from .base import BaseAgent
from .prompt_config import AgentRole, get_system_prompt, get_data_section, get_response_instruction
from .agent_utils import DataExtractor, PromptBuilder


class TechnicalAgent(BaseAgent):
    """Handles technical questions about skills, tools, and projects."""

    def __init__(self, **kwargs):
        super().__init__(
            name="Technical",
            role=AgentRole.TECHNICAL,
            **kwargs
        )

    def process(self, message: str, conversation_state):
        """Process technical questions with detailed responses."""
        # Extract relevant technical data
        tech_data = {
            "skills": self.resume_data.get("skills", {}),
            "projects": self.resume_data.get("projects", []),
            "experience": DataExtractor.extract_technical_experience(
                self.resume_data.get("experience", [])
            )
        }

        # Build prompt
        system_prompt = get_system_prompt(AgentRole.TECHNICAL)
        data_section = get_data_section(AgentRole.TECHNICAL, str(tech_data))
        context = self._build_context(conversation_state)
        response_instruction = get_response_instruction(AgentRole.TECHNICAL)

        prompt = PromptBuilder.build_prompt(
            system_prompt=system_prompt,
            data_section=data_section,
            context=context,
            message=message,
            response_instruction=response_instruction
        )

        # Get LLM response
        response = self.llm.invoke(prompt)

        return {
            "content": response.content,
            "agent_name": self.name,
            "confidence": self._calculate_confidence(message, response.content),
            "metadata": {"focus": "technical"}
        }
