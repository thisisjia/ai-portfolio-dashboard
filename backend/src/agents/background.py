"""Background/experience specialist agent."""

from langchain_core.prompts import PromptTemplate
from .base import BaseAgent


class BackgroundAgent(BaseAgent):
    """Handles questions about education, work history, and career progression."""
    
    def __init__(self, **kwargs):
        # Lower temperature to reduce hallucinations
        super().__init__(name="Background", model_name="llama-3.3-70b-versatile", temperature=0.1, **kwargs)
    
    def _get_system_prompt(self) -> str:
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        return f"""You are answering interview questions as the candidate. Today's date is {today}.

RESPONSE FORMAT - CRITICAL:
- Answer DIRECTLY in first person as the candidate
- DO NOT add stage directions like "(smiles)", "(pauses)", "(chuckles)"
- DO NOT format as "Me:" or "Interviewer:" - just answer the question
- Keep responses professional and concise (2-3 paragraphs max)
- DO NOT add theatrical elements or fake dialogue

ANTI-HALLUCINATION RULES - ABSOLUTELY CRITICAL:
1. **NO MADE-UP NAMES**: NEVER invent platform/product names. The data lists INDIVIDUAL achievements, not named platforms.
   - WRONG: "AI-Powered Treasury Market Intelligence Platform"
   - RIGHT: "At Integrum Global, I built Bloomberg-based dashboards for market analysis"
2. **STICK TO EXACT WORDING**: Use the EXACT company names and achievement descriptions from the data
3. **NO EMBELLISHMENT**: Don't add details about team dynamics, challenges, or feelings that aren't in the data
4. **WORK vs PROJECTS**: "Integrum Global" is a COMPANY where you worked, NOT a project name
5. **TIME-AWARENESS - CRITICAL**:
   - You have TODAY_DATE and ONE_YEAR_AGO in the data
   - Each role has a DATE_RANGE (e.g., "2024-11-01 to Present")
   - If asked "past year" / "last year" / "recently": Calculate which roles fall within that timeframe
   - If asked "past year" and a role started in 2016, DO NOT mention it
   - Focus on roles with end_date = "Present" or start_date within the requested timeframe
   - Example: If today is 2025-01-17 and asked "past year", only mention roles active since 2024-01-17
6. **When you don't have the answer**: Say "I don't have those specific details at the moment. Please feel free to contact me directly to discuss this further."

IF IT'S NOT IN THE DATA, DON'T SAY IT. If you can't answer, redirect to direct contact. No exceptions.

Answer factually about your work history, education, and achievements."""
    
    def _create_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            template="""System: {system_prompt}

My Professional Background:
{resume_data}

Conversation Context:
{context}

Employer/Recruiter Question: {message}

Respond as ME, the candidate. Provide clear, factual details about MY background and experience, including specific details about MY roles, achievements, and career progression.""",
            input_variables=["system_prompt", "resume_data", "context", "message"]
        )
    
    def process(self, message: str, conversation_state):
        """Process background/experience questions."""
        from datetime import datetime, timedelta

        # Calculate date context
        today = datetime.now()
        one_year_ago = today - timedelta(days=365)

        # Extract relevant background data with prominent dates
        experience_list = self.resume_data.get("experience", [])

        # Format experience with clear date markers
        formatted_experience = []
        for exp in experience_list:
            exp_copy = exp.copy()
            # Make dates super visible
            start = exp.get('start_date', 'Unknown')
            end = exp.get('end_date', 'Present')
            exp_copy['DATE_RANGE'] = f"{start} to {end}"
            formatted_experience.append(exp_copy)

        # Add important context note
        context_note = """WORK_EXPERIENCE_ONLY contains ONLY job titles and companies. DO NOT confuse work experience with specific projects. Each work experience entry is a ROLE at a COMPANY, NOT a project name.

CRITICAL: The 'achievements' field contains a LIST of separate features/tasks you completed. These are INDIVIDUAL achievements, NOT parts of one named platform. DO NOT invent umbrella names like 'the X Platform' or 'the Y System'. Just describe what you did: 'I built dashboards', 'I developed a RAG system', etc."""

        background_data = {
            "TODAY_DATE": today.strftime("%Y-%m-%d"),
            "ONE_YEAR_AGO": one_year_ago.strftime("%Y-%m-%d"),
            "WORK_EXPERIENCE_ONLY": formatted_experience,
            "EDUCATION_ONLY": self.resume_data.get("education", []),
            "summary": self.resume_data.get("summary", ""),
            "career_progression": self._extract_career_progression(),
            "IMPORTANT_NOTE": context_note
        }

        context = self._build_context(conversation_state)
        prompt = self.prompt_template.format(
            system_prompt=self._get_system_prompt(),
            resume_data=str(background_data),
            context=context,
            message=message
        )
        
        response = self.llm.invoke(prompt)
        
        return {
            "content": response.content,
            "agent_name": self.name,
            "confidence": self._calculate_confidence(message, response.content),
            "metadata": {"focus": "background"}
        }
    
    def _extract_career_progression(self):
        """Extract career progression from experience."""
        experience = self.resume_data.get("experience", [])
        progression = []
        for exp in experience:
            progression.append({
                "role": exp.get("role"),
                "company": exp.get("company"),
                "duration": exp.get("duration"),
                "key_achievement": exp.get("highlights", [""])[0] if exp.get("highlights") else ""
            })
        return progression