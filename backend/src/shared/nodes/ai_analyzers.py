"""AI/LLM analysis nodes for intelligent processing."""

from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph
from pydantic import BaseModel
import os
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


class LLMAnalyzerState(BaseModel):
    prompt: str = ""
    context: Optional[Dict[str, Any]] = None
    response: Optional[str] = None
    model: Optional[str] = None
    prompt_tokens: int = 0
    context_provided: bool = False


class LLMAnalyzerNode:
    """Node for LLM-based text analysis.
    
    Args:
        model_name: OpenAI model name
        temperature: Model temperature
        system_prompt: System prompt for the LLM
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def __call__(self, state: LLMAnalyzerState) -> LLMAnalyzerState:
        """Analyze text using LLM.
        
        Args:
            state: LLMAnalyzerState containing prompt and context
            
        Returns:
            Updated state with LLM response and metadata
        """
        messages = [SystemMessage(content=self.system_prompt)]
        
        if state.context:
            context_str = f"Context: {state.context}"
            messages.append(HumanMessage(content=f"{context_str}\n\n{state.prompt}"))
        else:
            messages.append(HumanMessage(content=state.prompt))
        
        response = self.llm(messages)
        
        state.response = response.content
        state.model = self.model_name
        state.prompt_tokens = len(state.prompt.split())
        state.context_provided = state.context is not None
        
        return state


class ChatRouterState(BaseModel):
    message: str = ""
    conversation_history: Optional[List[Dict]] = None
    selected_agent: Optional[str] = None
    original_message: Optional[str] = None
    confidence: float = 0.0


class ChatRouterNode:
    """Node for routing chat messages to appropriate agents.
    
    Args:
        agent_types: List of available agent types
        routing_prompt: Custom routing prompt
    """
    
    def __init__(
        self,
        agent_types: List[str],
        routing_prompt: Optional[str] = None
    ):
        self.agent_types = agent_types
        self.routing_prompt = routing_prompt or self._default_routing_prompt()
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def _default_routing_prompt(self) -> str:
        """Generate default routing prompt based on agent types."""
        agents_str = ", ".join(self.agent_types)
        return f"""You are a message router. Given a user message, determine which agent should handle it.
        Available agents: {agents_str}
        Respond with ONLY the agent name, nothing else."""
    
    def __call__(self, state: ChatRouterState) -> ChatRouterState:
        """Route message to appropriate agent.
        
        Args:
            state: ChatRouterState containing message and conversation history
            
        Returns:
            Updated state with selected agent and confidence
        """
        prompt = self.routing_prompt
        if state.conversation_history:
            history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.conversation_history[-3:]])
            prompt += f"\n\nRecent conversation:\n{history_str}"
        
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"Route this message: {state.message}")
        ]
        
        response = self.llm(messages)
        selected_agent = response.content.strip().lower()
        
        # Validate agent selection
        if selected_agent not in [agent.lower() for agent in self.agent_types]:
            selected_agent = self.agent_types[0]  # Default to first agent
        
        state.selected_agent = selected_agent
        state.original_message = state.message
        state.confidence = 1.0 if selected_agent in [a.lower() for a in self.agent_types] else 0.5
        
        return state