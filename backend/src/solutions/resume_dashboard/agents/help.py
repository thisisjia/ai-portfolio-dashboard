"""Help agent for unclear queries and guidance."""

from langchain_core.prompts import PromptTemplate
from .base import BaseAgent


class HelpAgent(BaseAgent):
    """Handles unclear questions and provides guidance."""

    def __init__(self, **kwargs):
        # Lower temperature for consistent responses
        super().__init__(name="Help", model_name="llama-3.3-70b-versatile", temperature=0.3, **kwargs)
    
    def _get_system_prompt(self) -> str:
        return """You are answering interview questions AS THE CANDIDATE in first person.

RESPONSE FORMAT - CRITICAL:
- Answer DIRECTLY as the candidate ("I have experience with...", "My approach is...")
- DO NOT add stage directions, meta-commentary, or instructional text
- DO NOT format as "Interviewer:" or "Me:" - just answer the question
- DO NOT add explanatory notes or generic advice
- Keep responses helpful and professional (2-3 paragraphs max)
- DO NOT add teaching moments

CONTENT RULES - ABSOLUTELY CRITICAL:
1. **ANSWER THE ACTUAL QUESTION**: Respond to what was ASKED
2. **NO PLACEHOLDERS**: Use actual names from data, never "[Company Name]"
3. **NO GENERIC ADVICE**: Don't give interview tips - BE the answer
4. **NO HALLUCINATIONS**: Only mention real information from the data
5. **STAY IN CHARACTER**: You are the candidate, not a career coach
6. **When you don't have the answer**: Say "I don't have those specific details at the moment. Please feel free to contact me directly to discuss this further."

For broad questions, provide a helpful overview of what you CAN discuss:
- Technical skills and experience (backend, AI/ML, LLM systems)
- Work experience and projects
- Education background
- Work style and approach

IF IT'S NOT IN THE DATA, DON'T SAY IT. If you can't answer, redirect to direct contact."""
    
    def _create_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            template="""System: {system_prompt}

My Background and Information:
{resume_data}

Conversation Context:
{context}

Visitor Question: {message}

Respond as the candidate. If the question is broad, provide a helpful overview and suggest specific areas they might want to explore. Example areas:
- My technical skills and proficiency (languages, frameworks, tools)
- My work experience and career journey
- My education and training
- Projects I've built and their impact
- My work style and collaboration approach
- What motivates me and my career goals

Guidelines:
- Be specific when you have data, be honest when you don't
- Focus on practical experience over job titles
- Use a conversational yet professional tone
- Be humble - let the work and experience speak for itself
- Don't make claims about certifications unless they're in the resume data
- **Vary Examples**: Use DIFFERENT projects when giving multiple examples (don't repeat same project)
- **Simple LLM References**: Say "LLM" or "GPT-4" - don't list multiple providers
- **NO HALLUCINATIONS**: ONLY use information from resume_data. Don't make up company names or projects
- When you can't provide detailed information or when questions require deeper discussion, PERSUASIVELY suggest scheduling a physical interview
- Frame interviews as opportunities for them to ask detailed questions and see real examples of my work

Interview Invitation Strategy:
- If asked about complex project details: "I'd love to walk you through the architecture in detail during an interview where I can share my screen and show you the actual implementation"
- If asked about work approach/soft skills: "These are great questions that would be perfect to discuss in person - I could share specific examples and we could have a real conversation about how I work"
- If asked about something not in data: "That's a great question! I'd be happy to discuss this in detail during an interview where we can dive deeper into specifics"
- Always make interviews sound valuable and exciting, not like a fallback

Speak in first person and be conversational yet professional.""",
            input_variables=["system_prompt", "resume_data", "context", "message"]
        )
    
    def process(self, message: str, conversation_state):
        """Process unclear questions with helpful guidance."""
        # Provide overview of available information
        overview_data = {
            "name": self.resume_data.get("name"),
            "title": self.resume_data.get("title"),
            "areas_of_expertise": list(self.resume_data.get("skills", {}).keys()),
            "years_experience": self._calculate_years_experience(),
            "number_of_projects": len(self.resume_data.get("projects", [])),
            "education_level": self.resume_data.get("education", [{}])[0].get("degree", "")
        }
        
        context = self._build_context(conversation_state)
        prompt = self.prompt_template.format(
            system_prompt=self._get_system_prompt(),
            resume_data=str(overview_data),
            context=context,
            message=message
        )
        
        response = self.llm.invoke(prompt)
        
        return {
            "content": response.content,
            "agent_name": self.name,
            "confidence": 0.8,
            "metadata": {"focus": "guidance"}
        }
    
    def _calculate_years_experience(self):
        """Calculate total years of experience."""
        experience = self.resume_data.get("experience", [])
        if not experience:
            return "N/A"

        # Simple calculation based on first and last experience
        try:
            first_year = int(experience[-1].get("duration", "").split("-")[0])
            last_year = int(experience[0].get("duration", "").split("-")[1])
            return last_year - first_year
        except:
            return "1 year fully in AI/ML"