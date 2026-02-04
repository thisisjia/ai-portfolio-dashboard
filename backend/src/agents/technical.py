"""Technical skills specialist agent."""

from langchain_core.prompts import PromptTemplate
from .base import BaseAgent


class TechnicalAgent(BaseAgent):
    """Handles technical questions about skills, tools, and projects."""

    def __init__(self, **kwargs):
        # Lower temperature for accurate technical responses
        super().__init__(name="Technical", model_name="llama-3.3-70b-versatile", temperature=0.2, **kwargs)
    
    def _get_system_prompt(self) -> str:
        return """You are answering technical interview questions AS THE CANDIDATE in first person.

RESPONSE FORMAT - CRITICAL:
- Answer DIRECTLY as the candidate ("I have experience with...", "I built...", "My approach is...")
- DO NOT add stage directions, meta-commentary, or instructional text
- DO NOT format as "Interviewer:" or "Me:" - just answer the question
- DO NOT add explanatory notes like "This demonstrates..." or "The key is to..."
- Keep responses focused and technical (2-3 paragraphs max)
- DO NOT add generic advice or teaching moments

CONTENT RULES - ABSOLUTELY CRITICAL:
1. **ANSWER THE ACTUAL QUESTION**: Respond to what was ASKED, don't invent different scenarios
2. **NO PLACEHOLDERS**: Use actual company names, project names, and technologies from the data
3. **NO GENERIC ADVICE**: Don't give tips on "how to answer" - BE the answer
4. **NO HALLUCINATIONS**: Only mention real technologies and projects from the data
5. **STAY IN CHARACTER**: You are the candidate being interviewed, not a career coach
6. **ONE PROJECT PER EXAMPLE**: Don't repeat the same project multiple times
7. **When you don't have the answer**: Say "I don't have those specific details at the moment. Please feel free to contact me directly to discuss this further."

TECHNICAL FOCUS AREAS (use data to support):
- Backend Development: Python, FastAPI, Django
- LLM & AI Engineering: Multi-agent systems, LangGraph, LangChain, RAG
- Data Engineering: APIs, databases, data pipelines
- Frontend: React/Next.js (prototyping only, not core expertise)

IF IT'S NOT IN THE DATA, DON'T SAY IT. If you can't answer, redirect to direct contact. Answer the question asked, nothing else."""
    
    def _create_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            template="""System: {system_prompt}

My Technical Background:
{resume_data}

Conversation Context:
{context}

Employer/Recruiter Question: {message}

Respond as the candidate in first person. Showcase MY technical expertise with specific examples from MY projects and experience.""",
            input_variables=["system_prompt", "resume_data", "context", "message"]
        )
    
    def process(self, message: str, conversation_state):
        """Process technical questions with detailed responses."""
        # Extract relevant technical data
        tech_data = {
            "skills": self.resume_data.get("skills", {}),
            "projects": self.resume_data.get("projects", []),
            "experience": [
                exp for exp in self.resume_data.get("experience", [])
                if any(tech in str(exp) for tech in ["engineer", "developer", "tech"])
            ]
        }
        
        context = self._build_context(conversation_state)
        prompt = self.prompt_template.format(
            system_prompt=self._get_system_prompt(),
            resume_data=str(tech_data),
            context=context,
            message=message
        )
        
        response = self.llm.invoke(prompt)
        
        return {
            "content": response.content,
            "agent_name": self.name,
            "confidence": self._calculate_confidence(message, response.content),
            "metadata": {"focus": "technical"}
        }