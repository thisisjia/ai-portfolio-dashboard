"""Background/experience specialist agent."""

from .base import BaseAgent
from .prompt_config import AgentRole, get_system_prompt, get_data_section, get_response_instruction
from .agent_utils import DateUtils, DataExtractor, PromptBuilder


class BackgroundAgent(BaseAgent):
    """Handles questions about education, work history, and career progression."""

    def __init__(self, **kwargs):
        super().__init__(
            name="Background",
            role=AgentRole.BACKGROUND,
            **kwargs
        )

    def process(self, message: str, conversation_state):
        """Process background/experience questions."""
        # Get date context
        today = DateUtils.get_current_date()
        one_year_ago = DateUtils.get_one_year_ago()

        # Extract and format experience data
        experience_list = self.resume_data.get("experience", [])
        formatted_experience = DataExtractor.format_work_experience_with_dates(experience_list)

        # Prepare background data
        background_data = {
            "TODAY_DATE": today,
            "ONE_YEAR_AGO": one_year_ago,
            "WORK_EXPERIENCE_ONLY": formatted_experience,
            "EDUCATION_ONLY": self.resume_data.get("education", []),
            "summary": self.resume_data.get("summary", ""),
            "career_progression": DataExtractor.extract_career_progression(experience_list),
            "IMPORTANT_NOTE": DataExtractor.get_background_context_note()
        }

        # Build prompt
        system_prompt = get_system_prompt(AgentRole.BACKGROUND, today_date=today)
        data_section = get_data_section(AgentRole.BACKGROUND, str(background_data))
        context = self._build_context(conversation_state)
        response_instruction = get_response_instruction(AgentRole.BACKGROUND)

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
            "metadata": {"focus": "background"}
        }
