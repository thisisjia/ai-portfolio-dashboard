"""Help agent for unclear queries and guidance."""

from .base import BaseAgent
from .prompt_config import AgentRole, get_system_prompt, get_data_section, get_response_instruction
from .agent_utils import DataExtractor, PromptBuilder


class HelpAgent(BaseAgent):
    """Handles unclear questions and provides guidance."""

    def __init__(self, **kwargs):
        super().__init__(
            name="Help",
            role=AgentRole.HELP,
            **kwargs
        )

    def process(self, message: str, conversation_state):
        """Process unclear questions with helpful guidance."""
        # Provide overview of available information
        overview_data = {
            "name": self.resume_data.get("name"),
            "title": self.resume_data.get("title"),
            "areas_of_expertise": list(self.resume_data.get("skills", {}).keys()),
            "years_experience": DataExtractor.calculate_years_experience(
                self.resume_data.get("experience", [])
            ),
            "number_of_projects": len(self.resume_data.get("projects", [])),
            "education_level": self.resume_data.get("education", [{}])[0].get("degree", "")
        }

        # Build prompt
        system_prompt = get_system_prompt(AgentRole.HELP)
        data_section = get_data_section(AgentRole.HELP, str(overview_data))
        context = self._build_context(conversation_state)
        response_instruction = get_response_instruction(AgentRole.HELP)

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
            "confidence": 0.8,
            "metadata": {"focus": "guidance"}
        }
