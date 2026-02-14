"""Base agent class and shared utilities for the multi-agent system."""

from abc import ABC
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import os

# Import database queries for accurate resume data
from ..utils.resume_queries import get_resume_queries
from .prompt_config import AgentRole, DEFAULT_MODEL, AGENT_TEMPERATURES


class AgentResponse(BaseModel):
    """Response from an agent."""
    content: str
    agent_name: str
    confidence: float = Field(ge=0, le=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationState(BaseModel):
    """State of the conversation."""
    session_id: str
    token: str
    company: str
    messages: List[BaseMessage] = Field(default_factory=list)
    current_agent: Optional[str] = None
    agent_history: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """Base class for all agents in the multi-agent system."""

    def __init__(
        self,
        name: str,
        role: Optional[AgentRole] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        resume_data: Optional[Dict] = None
    ):
        self.name = name
        self.role = role

        # Get temperature from config if not specified
        if temperature is None and role is not None:
            temperature = AGENT_TEMPERATURES.get(role, 0.7)
        elif temperature is None:
            temperature = 0.7

        # Get model from config if not specified
        if model_name is None:
            model_name = DEFAULT_MODEL

        # Initialize LLM
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        self.llm = ChatGroq(
            model=model_name,
            temperature=temperature,
            groq_api_key=groq_api_key
        )
        self.resume_data = resume_data or self._load_resume_data()
    
    def _load_resume_data(self) -> Dict:
        """Load resume data from database for accuracy."""
        try:
            resume_queries = get_resume_queries()
            return resume_queries.get_complete_resume_data()
        except Exception as e:
            print(f"Warning: Could not load resume data from database: {e}")
            return self._get_default_resume_data()
    
    def _get_default_resume_data(self) -> Dict:
        """Return default resume data structure."""
        return {
            "name": "J M",
            "title": "Full-Stack Engineer & AI Developer",
            "email": "jm@example.com",
            "location": "San Francisco, CA",
            "summary": "Experienced full-stack engineer with expertise in AI/ML, distributed systems, and modern web technologies.",
            "skills": {
                "languages": ["Python", "TypeScript", "JavaScript", "Go", "SQL"],
                "frameworks": ["React", "Next.js", "FastAPI", "Django", "LangChain"],
                "databases": ["PostgreSQL", "MongoDB", "Redis", "Pinecone"],
                "tools": ["Docker", "Kubernetes", "AWS", "Git", "CI/CD"],
                "ai_ml": ["LangChain", "LangGraph", "OpenAI", "Hugging Face", "PyTorch"]
            },
            "experience": [
                {
                    "company": "Tech Startup",
                    "role": "Senior Full-Stack Engineer",
                    "duration": "2022-2024",
                    "highlights": [
                        "Built AI-powered features using LangChain and OpenAI",
                        "Designed scalable microservices architecture",
                        "Led team of 4 engineers"
                    ]
                },
                {
                    "company": "AI Company",
                    "role": "ML Engineer",
                    "duration": "2020-2022",
                    "highlights": [
                        "Developed NLP models for customer service automation",
                        "Reduced response time by 60% with intelligent routing",
                        "Implemented RAG system for knowledge base"
                    ]
                }
            ],
            "education": [
                {
                    "degree": "BS Computer Science",
                    "school": "UC Berkeley",
                    "year": "2020",
                    "gpa": "3.8"
                }
            ],
            "projects": [
                {
                    "name": "Token-Gated Resume Dashboard",
                    "description": "Interactive portfolio with multi-agent chatbot",
                    "technologies": ["FastAPI", "LangGraph", "React", "PostgreSQL"],
                    "impact": "Showcases full-stack and AI capabilities"
                },
                {
                    "name": "Distributed Task Queue",
                    "description": "High-performance task processing system",
                    "technologies": ["Go", "Redis", "RabbitMQ"],
                    "impact": "Handles 100k+ tasks per minute"
                }
            ],
            "interests": ["Open Source", "System Design", "AI Ethics", "Teaching"],
            "personality": {
                "work_style": "Collaborative, detail-oriented, and proactive",
                "strengths": ["Problem-solving", "Communication", "Leadership"],
                "values": ["Code quality", "User experience", "Continuous learning"]
            }
        }

    def _build_context(self, state: ConversationState) -> str:
        """Build context from conversation history."""
        if not state.messages:
            return "This is the start of the conversation."
        
        context_messages = state.messages[-5:]  # Last 5 messages for context
        context = []
        for msg in context_messages:
            if isinstance(msg, HumanMessage):
                context.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                context.append(f"Assistant: {msg.content}")
        
        return "\n".join(context)
    
    def _calculate_confidence(self, message: str, response: str) -> float:
        """Calculate confidence score for the response."""
        # Simple heuristic - can be improved
        if len(response) < 50:
            return 0.6
        if "I'm not sure" in response or "I don't know" in response:
            return 0.4
        return 0.85