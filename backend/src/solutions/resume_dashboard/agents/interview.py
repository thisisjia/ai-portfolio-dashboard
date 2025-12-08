"""Interview agent for handling resume-style interview questions."""

from langchain_core.prompts import PromptTemplate
from .base import BaseAgent


class InterviewAgent(BaseAgent):
    """Handles resume-style interview questions like strengths, weaknesses, challenges, etc."""

    def __init__(self, **kwargs):
        # Lower temperature for accurate responses
        super().__init__(name="Interview", model_name="llama-3.3-70b-versatile", temperature=0.2, **kwargs)

    def _get_system_prompt(self) -> str:
        return """You are answering interview questions AS THE CANDIDATE in first person.

RESPONSE FORMAT - CRITICAL:
- Answer DIRECTLY as the candidate ("I...", "My approach is...", "I have experience with...")
- DO NOT add stage directions, meta-commentary, or instructional text
- DO NOT format as "Interviewer:" or "Me:" - just answer the question
- DO NOT add explanatory notes like "This demonstrates..." or "The key is to..."
- Keep responses authentic and professional (2-3 paragraphs max)
- DO NOT add generic interview advice or coaching tips

CONTENT RULES - ABSOLUTELY CRITICAL:
1. **ANSWER THE ACTUAL QUESTION**: Respond to what was ASKED, don't invent different questions
2. **NO PLACEHOLDERS**: Use actual company names and projects from the data
3. **NO GENERIC ADVICE**: Don't give tips on "how to answer" - BE the answer
4. **NO HALLUCINATIONS**: Only mention real experiences from the data
5. **STAY IN CHARACTER**: You are the candidate being interviewed, not an interview coach
6. **ONE PROJECT PER EXAMPLE**: Don't repeat the same project multiple times
7. **When you don't have the answer**: Say "I don't have those specific details at the moment. Please feel free to contact me directly to discuss this further."

SPECIAL HANDLING FOR SENSITIVE QUESTIONS:

**If asked "Why are you leaving your current job?" or "Why did you leave [company]?":**
- Check the work_experience data for the company mentioned
- DO NOT invent reasons for leaving
- Use this template: "I've learned a lot at [Company] and contributed to [mention 1-2 actual achievements from data]. I'm looking for new opportunities to continue growing and take on new challenges. I'd be happy to discuss this in more detail during a conversation."
- Keep it brief, professional, and positive
- DO NOT speculate about company issues, compensation, or personal conflicts

Common interview questions you may encounter:
- Tell me about yourself
- What are your strengths/weaknesses?
- Why should we hire you?
- Tell me about a challenging project
- How do you handle pressure?
- What motivates you?

Use the STAR method (Situation, Task, Action, Result) for behavioral questions when appropriate.

IF IT'S NOT IN THE DATA, DON'T SAY IT. If you can't answer fully, give a brief professional response and redirect to direct contact."""

    def _create_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            template="""System: {system_prompt}

My Background & Data:
{resume_data}

Conversation Context:
{context}

Interview Question: {message}

Respond as the candidate in an interview. Be authentic, use specific examples from my actual experience, and show both confidence and humility. If this is a complex behavioral question, use the STAR method. Always speak in first person.""",
            input_variables=["system_prompt", "resume_data", "context", "message"]
        )

    def process(self, message: str, conversation_state):
        """Process interview-style questions with authentic, structured responses."""
        # Prepare relevant resume data with ALL available information
        interview_data = {
            "name": self.resume_data.get("name"),
            "work_experience": self.resume_data.get("experience", []),
            "skills": self.resume_data.get("skills", {}),
            "projects": self.resume_data.get("projects", []),
            "education": self.resume_data.get("education", []),
            "personality": self.resume_data.get("personality", {}),
            "publications": self.resume_data.get("publications", [])
        }

        context = self._build_context(conversation_state)
        prompt = self.prompt_template.format(
            system_prompt=self._get_system_prompt(),
            resume_data=str(interview_data),
            context=context,
            message=message
        )

        response = self.llm.invoke(prompt)

        return {
            "content": response.content,
            "agent_name": self.name,
            "confidence": 0.9,
            "metadata": {"focus": "interview"}
        }
