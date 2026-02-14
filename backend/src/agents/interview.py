"""Interview agent for handling resume-style interview questions."""

from .base import BaseAgent
from .prompt_config import AgentRole, get_system_prompt, get_data_section, get_response_instruction
from .agent_utils import PromptBuilder


class InterviewAgent(BaseAgent):
    """Handles resume-style interview questions like strengths, weaknesses, challenges, etc."""

    def __init__(self, **kwargs):
        super().__init__(
            name="Interview",
            role=AgentRole.INTERVIEW,
            **kwargs
        )

    def process(self, message: str, conversation_state):
        """Process interview-style questions with authentic, structured responses."""
        # Prepare relevant resume data with all available information
        interview_data = {
            "name": self.resume_data.get("name"),
            "work_experience": self.resume_data.get("experience", []),
            "skills": self.resume_data.get("skills", {}),
            "projects": self.resume_data.get("projects", []),
            "education": self.resume_data.get("education", []),
            "personality": self.resume_data.get("personality", {}),
            "publications": self.resume_data.get("publications", [])
        }

        # Build prompt
        system_prompt = get_system_prompt(AgentRole.INTERVIEW)
        data_section = get_data_section(AgentRole.INTERVIEW, str(interview_data))
        context = self._build_context(conversation_state)
        response_instruction = get_response_instruction(AgentRole.INTERVIEW)

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
            "confidence": 0.9,
            "metadata": {"focus": "interview"}
        }
