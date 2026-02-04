"""Chat API routes for the multi-agent chatbot."""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, AsyncGenerator
import uuid
import json
from datetime import datetime

from ..agents.workflow import ChatbotManager
from ..utils.database import DatabaseManager

router = APIRouter(prefix="/api/chat", tags=["Chat"])

# Initialize chatbot manager
chatbot_manager = ChatbotManager()
db_manager = DatabaseManager()


class ChatMessage(BaseModel):
    """Chat message request model."""
    message: str
    session_id: Optional[str] = None
    token: Optional[str] = None
    company: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    success: bool
    response: Optional[str] = None
    agent: Optional[str] = None
    confidence: Optional[float] = None
    session_id: str
    error: Optional[str] = None


class ChatHistory(BaseModel):
    """Chat history response model."""
    session_id: str
    messages: List[Dict]
    created_at: str
    last_updated: str


@router.post("/message", response_model=ChatResponse)
async def send_message(chat_message: ChatMessage):
    """Send a message to the chatbot and get a response."""
    try:
        # Generate session ID if not provided
        session_id = chat_message.session_id or str(uuid.uuid4())
        
        # Process message through the chatbot
        result = await chatbot_manager.process_message(
            message=chat_message.message,
            session_id=session_id
        )
        
        # Log the chat interaction
        await db_manager.log_chat(
            session_id=session_id,
            token=chat_message.token,
            company=chat_message.company,
            user_message=chat_message.message,
            ai_response=result.get("response", ""),
            agent_used=result.get("agent", "unknown")
        )
        
        if result["success"]:
            return ChatResponse(
                success=True,
                response=result["response"],
                agent=result["agent"],
                confidence=result["confidence"],
                session_id=session_id
            )
        else:
            return ChatResponse(
                success=False,
                error=result.get("error", "Failed to generate response"),
                session_id=session_id
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}", response_model=ChatHistory)
async def get_chat_history(session_id: str):
    """Get chat history for a session."""
    try:
        history = chatbot_manager.get_session_history(session_id)
        
        if not history:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return ChatHistory(
            session_id=session_id,
            messages=history,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(
    session_id: str,
    message_index: int,
    feedback: str,
    token: str
):
    """Submit feedback for a specific message."""
    try:
        await db_manager.log_feedback(
            token=token,
            session_id=session_id,
            feedback_type="chat_message",
            feedback_value=feedback,
            metadata={"message_index": message_index}
        )
        
        return {"success": True, "message": "Feedback recorded"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message/stream")
async def send_message_stream(chat_message: ChatMessage):
    """
    Stream chat responses using Server-Sent Events (SSE).
    Demonstrates real-time AI response streaming for better UX.
    """

    async def generate() -> AsyncGenerator[str, None]:
        """Generator function that yields SSE-formatted messages."""
        session_id = chat_message.session_id or str(uuid.uuid4())

        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'message': 'Processing your question...'})}\n\n"

            # Check if chatbot_manager has streaming capability
            if hasattr(chatbot_manager, 'stream_message'):
                # Use streaming if available
                async for chunk in chatbot_manager.stream_message(
                    message=chat_message.message,
                    session_id=session_id,
                    token=chat_message.token,
                    company=chat_message.company
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"
            else:
                # Fallback: use regular process_message and stream token by token
                yield f"data: {json.dumps({'type': 'status', 'message': 'Generating response...'})}\n\n"

                result = await chatbot_manager.process_message(
                    message=chat_message.message,
                    session_id=session_id
                )

                if result["success"]:
                    # Send agent notification
                    yield f"data: {json.dumps({'type': 'agent_change', 'agent': result.get('agent', 'unknown')})}\n\n"

                    # Clear status after agent change
                    yield f"data: {json.dumps({'type': 'status', 'message': None})}\n\n"

                    # Stream response token by token for typing effect
                    import asyncio
                    response_text = result['response']

                    # Stream word by word (faster than char by char, still looks nice)
                    words = response_text.split(' ')
                    for i, word in enumerate(words):
                        # Add space back except for first word
                        token_content = word if i == 0 else ' ' + word
                        yield f"data: {json.dumps({'type': 'token', 'content': token_content})}\n\n"

                        # Small delay for typing effect (adjust speed here)
                        await asyncio.sleep(0.03)  # 30ms per word

                    # Log the chat interaction
                    await db_manager.log_chat(
                        session_id=session_id,
                        token=chat_message.token,
                        company=chat_message.company,
                        user_message=chat_message.message,
                        ai_response=result["response"],
                        agent_used=result.get("agent", "unknown")
                    )
                else:
                    yield f"data: {json.dumps({'type': 'error', 'message': result.get('error', 'Failed to generate response')})}\n\n"

            # Send completion signal
            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"

        except Exception as e:
            # Send error through stream
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/suggestions")
async def get_suggestions():
    """Get suggested questions to ask the chatbot."""
    suggestions = [
        {
            "category": "Technical Skills",
            "questions": [
                "What programming languages are you most proficient in?",
                "Can you describe a complex technical problem you've solved?",
                "What's your experience with distributed systems?",
                "How do you approach system design challenges?"
            ]
        },
        {
            "category": "AI/ML Experience",
            "questions": [
                "What's your experience with LangChain and LangGraph?",
                "Can you explain a project where you used AI/ML?",
                "How do you approach prompt engineering?",
                "What's your experience with RAG systems?"
            ]
        },
        {
            "category": "Work Style",
            "questions": [
                "How do you prefer to collaborate with team members?",
                "What motivates you in your work?",
                "How do you handle tight deadlines?",
                "What's your approach to code reviews?"
            ]
        },
        {
            "category": "Background",
            "questions": [
                "Tell me about your education",
                "Why did you transition between roles?",
                "What's been your most impactful project?",
                "How has your career progressed over time?"
            ]
        }
    ]

    return {"suggestions": suggestions}