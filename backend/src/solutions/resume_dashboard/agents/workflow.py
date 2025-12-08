"""LangGraph workflow for multi-agent chatbot system."""

from typing import Dict, List, TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator

from .router import RouterAgent
from .technical import TechnicalAgent
from .personal import PersonalAgent
from .background import BackgroundAgent
from .help import HelpAgent
from .interview import InterviewAgent
from .base import ConversationState


class GraphState(TypedDict):
    """State for the conversation graph."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_agent: str
    next_agent: str
    session_id: str
    token: str
    company: str
    agent_history: List[str]
    metadata: Dict


def create_chatbot_workflow():
    """Create the multi-agent chatbot workflow using LangGraph."""
    
    # Initialize agents
    router = RouterAgent()
    agents = {
        "interview": InterviewAgent(),
        "technical": TechnicalAgent(),
        "personal": PersonalAgent(),
        "background": BackgroundAgent(),
        "help": HelpAgent()
    }
    
    # Create the graph
    workflow = StateGraph(GraphState)
    
    def route_message(state: GraphState) -> GraphState:
        """Route the message to the appropriate agent."""
        messages = state["messages"]
        if not messages:
            return state
        
        last_message = messages[-1]
        if not isinstance(last_message, HumanMessage):
            return state
        
        # Create conversation state for routing
        conv_state = ConversationState(
            session_id=state["session_id"],
            token=state["token"],
            company=state["company"],
            messages=messages,
            current_agent=state.get("current_agent"),
            agent_history=state.get("agent_history", [])
        )
        
        # Get routing decision
        routing_result = router.process(last_message.content, conv_state)
        next_agent = routing_result["agent"]
        
        state["next_agent"] = next_agent
        state["metadata"]["routing_confidence"] = routing_result["confidence"]
        
        return state
    
    def process_with_agent(state: GraphState, agent_name: str) -> GraphState:
        """Process message with specified agent."""
        messages = state["messages"]
        if not messages:
            return state
        
        last_message = messages[-1]
        if not isinstance(last_message, HumanMessage):
            return state
        
        # Get the appropriate agent
        agent = agents.get(agent_name)
        if not agent:
            agent = agents["help"]
        
        # Create conversation state
        conv_state = ConversationState(
            session_id=state["session_id"],
            token=state["token"],
            company=state["company"],
            messages=messages[:-1],  # Exclude current message from context
            current_agent=agent_name,
            agent_history=state.get("agent_history", [])
        )
        
        # Process with agent
        response = agent.process(last_message.content, conv_state)
        
        # Add response to messages
        ai_message = AIMessage(
            content=response["content"],
            additional_kwargs={
                "agent": agent_name,
                "confidence": response.get("confidence", 0.8)
            }
        )
        state["messages"].append(ai_message)
        
        # Update state
        state["current_agent"] = agent_name
        state["agent_history"] = state.get("agent_history", []) + [agent_name]
        
        return state
    
    # Add nodes to the graph
    workflow.add_node("router", route_message)
    workflow.add_node("interview", lambda s: process_with_agent(s, "interview"))
    workflow.add_node("technical", lambda s: process_with_agent(s, "technical"))
    workflow.add_node("personal", lambda s: process_with_agent(s, "personal"))
    workflow.add_node("background", lambda s: process_with_agent(s, "background"))
    workflow.add_node("help", lambda s: process_with_agent(s, "help"))
    
    # Define the flow
    workflow.set_entry_point("router")
    
    # Add conditional edges based on routing
    def should_continue(state: GraphState) -> str:
        next_agent = state.get("next_agent")
        if next_agent in agents:
            return next_agent
        return "help"
    
    workflow.add_conditional_edges(
        "router",
        should_continue,
        {
            "interview": "interview",
            "technical": "technical",
            "personal": "personal",
            "background": "background",
            "help": "help"
        }
    )

    # All agents end the conversation
    workflow.add_edge("interview", END)
    workflow.add_edge("technical", END)
    workflow.add_edge("personal", END)
    workflow.add_edge("background", END)
    workflow.add_edge("help", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


class ChatbotManager:
    """Manager for the multi-agent chatbot."""
    
    def __init__(self):
        self.workflow = create_chatbot_workflow()
        self.sessions = {}
    
    async def process_message(
        self,
        message: str,
        session_id: str
    ) -> Dict:
        """Process a user message through the workflow."""
        
        # Get or create session state
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "messages": [],
                "current_agent": None,
                "next_agent": None,
                "session_id": session_id,
                "token": "demo_token",  # Default token for all sessions
                "company": "public_access",  # Default company for all sessions
                "agent_history": [],
                "metadata": {}
            }
        
        state = self.sessions[session_id]
        
        # Add user message
        state["messages"].append(HumanMessage(content=message))
        
        # Run the workflow
        result = await self.workflow.ainvoke(state)
        
        # Update session
        self.sessions[session_id] = result
        
        # Get the last AI message
        ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
        if ai_messages:
            last_response = ai_messages[-1]
            return {
                "success": True,
                "response": last_response.content,
                "agent": last_response.additional_kwargs.get("agent", "unknown"),
                "confidence": last_response.additional_kwargs.get("confidence", 0.8),
                "session_id": session_id
            }
        
        return {
            "success": False,
            "error": "No response generated",
            "session_id": session_id
        }
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session."""
        if session_id not in self.sessions:
            return []
        
        messages = self.sessions[session_id]["messages"]
        history = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({
                    "role": "assistant",
                    "content": msg.content,
                    "agent": msg.additional_kwargs.get("agent")
                })
        
        return history