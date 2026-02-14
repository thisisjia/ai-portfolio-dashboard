"""Personal/personality specialist agent."""

from .base import BaseAgent
from .prompt_config import AgentRole, get_system_prompt, get_data_section, get_response_instruction
from .agent_utils import DataExtractor, PromptBuilder


class PersonalAgent(BaseAgent):
    """Handles questions about personality, work style, and soft skills."""

    def __init__(self, **kwargs):
        super().__init__(
            name="Personal",
            role=AgentRole.PERSONAL,
            **kwargs
        )

    def process(self, message: str, conversation_state):
        """Process personal/soft skill questions."""
        # Extract relevant personal data
        personal_data = {
            "personality": self.resume_data.get("personality", {}),
            "interests": self.resume_data.get("interests", []),
            "summary": self.resume_data.get("summary", ""),
            "leadership_examples": DataExtractor.extract_leadership_examples(
                self.resume_data.get("experience", [])
            )
        }

        # Build prompt
        system_prompt = get_system_prompt(AgentRole.PERSONAL)
        data_section = get_data_section(AgentRole.PERSONAL, str(personal_data))
        context = self._build_context(conversation_state)
        response_instruction = get_response_instruction(AgentRole.PERSONAL)

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
            "metadata": {"focus": "personal"}
        }
