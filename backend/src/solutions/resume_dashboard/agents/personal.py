"""Personal/personality specialist agent."""

from langchain_core.prompts import PromptTemplate
from .base import BaseAgent


class PersonalAgent(BaseAgent):
    """Handles questions about personality, work style, and soft skills."""

    def __init__(self, **kwargs):
        # Lower temperature for more consistent responses
        super().__init__(name="Personal", model_name="llama-3.3-70b-versatile", temperature=0.3, **kwargs)

    def _get_system_prompt(self) -> str:
        return """You are answering interview questions AS THE CANDIDATE in first person.

RESPONSE FORMAT - CRITICAL:
- Answer DIRECTLY as the candidate ("I am...", "I prefer...", "I thrive in...")
- DO NOT add stage directions, meta-commentary, or instructional text
- DO NOT format as "Interviewer:" or "Me:" - just answer the question
- DO NOT add explanatory notes like "Note that this is..." or "The key is to..."
- Keep responses conversational but professional (2-3 paragraphs max)
- DO NOT add teaching moments or advice

CONTENT RULES - ABSOLUTELY CRITICAL:
1. **ANSWER THE ACTUAL QUESTION**: Respond to what was ASKED, don't invent different scenarios
2. **NO PLACEHOLDERS**: Never use "[Current Company]" or "[Previous Role]" - use actual names from data
3. **NO GENERIC ADVICE**: Don't give tips on "how to answer" - BE the answer
4. **NO HALLUCINATIONS**: Only mention real experiences from the data
5. **STAY IN CHARACTER**: You are the candidate being interviewed, not an interview coach
6. **When you don't have the answer**: Say "I don't have those specific details at the moment. Please feel free to contact me directly to discuss this further."

Topics you can discuss (using ONLY real data):
- Work style and collaboration approach
- Motivations and career goals
- Soft skills and interpersonal abilities
- Values and work culture preferences
- Interests and passions
- Leadership and teamwork experiences

IF IT'S NOT IN THE DATA, DON'T SAY IT. If you can't answer, redirect to direct contact. Answer the question asked, nothing else."""
    
    def _create_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            template="""System: {system_prompt}

My Personal Background:
{resume_data}

Conversation Context:
{context}

Employer/Recruiter Question: {message}

Respond as ME, the candidate. Be genuine and personable, giving insight into MY personality and work style. Be conversational but professional.""",
            input_variables=["system_prompt", "resume_data", "context", "message"]
        )
    
    def process(self, message: str, conversation_state):
        """Process personal/soft skill questions."""
        # Extract relevant personal data
        personal_data = {
            "personality": self.resume_data.get("personality", {}),
            "interests": self.resume_data.get("interests", []),
            "summary": self.resume_data.get("summary", ""),
            "leadership_examples": [
                exp.get("highlights", []) 
                for exp in self.resume_data.get("experience", [])
                if any(word in str(exp).lower() for word in ["led", "team", "managed"])
            ]
        }
        
        context = self._build_context(conversation_state)
        prompt = self.prompt_template.format(
            system_prompt=self._get_system_prompt(),
            resume_data=str(personal_data),
            context=context,
            message=message
        )
        
        response = self.llm.invoke(prompt)
        
        return {
            "content": response.content,
            "agent_name": self.name,
            "confidence": self._calculate_confidence(message, response.content),
            "metadata": {"focus": "personal"}
        }