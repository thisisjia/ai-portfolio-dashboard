"""Router agent that directs messages to appropriate specialist agents."""

from typing import Tuple
from langchain_core.prompts import PromptTemplate
from .base import BaseAgent, ConversationState
import re


class RouterAgent(BaseAgent):
    """Routes incoming messages to the appropriate specialist agent."""
    
    def __init__(self, **kwargs):
        super().__init__(name="Router", temperature=0.3, **kwargs)
    
    def _get_system_prompt(self) -> str:
        return """You are a routing agent for a resume chatbot system. Your job is to analyze incoming messages and determine which specialist agent should handle them.

Available agents:
1. INTERVIEW - Handles resume-style interview questions like "tell me about yourself", "what are your strengths/weaknesses", "why should we hire you", "describe a challenging project", "how do you handle pressure", behavioral questions
2. TECHNICAL - Handles questions about programming languages, frameworks, tools, system design, technical projects
3. PERSONAL - Handles questions about personality, work style, motivations, interests, soft skills, culture fit
4. BACKGROUND - Handles questions about education, work history, career progression, past companies
5. HELP - Handles unclear questions, requests for guidance, or when user needs help understanding capabilities

Respond with ONLY the agent name (INTERVIEW, TECHNICAL, PERSONAL, BACKGROUND, or HELP) that should handle the message."""
    
    def _create_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            template="""System: {system_prompt}

Previous conversation context:
{context}

User message: {message}

Which agent should handle this message? Respond with only the agent name.""",
            input_variables=["system_prompt", "context", "message"]
        )
    
    def route(self, message: str, conversation_state: ConversationState) -> Tuple[str, float]:
        """Determine which agent should handle the message."""
        context = self._build_context(conversation_state)
        
        prompt = self.prompt_template.format(
            system_prompt=self._get_system_prompt(),
            context=context,
            message=message
        )
        
        response = self.llm.invoke(prompt).content.strip().upper()
        
        # Extract agent name from response
        agent_map = {
            "INTERVIEW": ("interview", 0.9),
            "TECHNICAL": ("technical", 0.9),
            "PERSONAL": ("personal", 0.9),
            "BACKGROUND": ("background", 0.9),
            "HELP": ("help", 0.9)
        }
        
        # Find which agent was mentioned
        for key, value in agent_map.items():
            if key in response:
                return value
        
        # Default to help agent if unclear
        return ("help", 0.5)
    
    def process(self, message: str, conversation_state: ConversationState):
        """Override process to just return routing decision."""
        agent_name, confidence = self.route(message, conversation_state)
        return {
            "agent": agent_name,
            "confidence": confidence,
            "reasoning": f"Routing to {agent_name} agent"
        }