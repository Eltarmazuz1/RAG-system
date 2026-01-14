import logging
import json
import asyncio
from typing import AsyncGenerator
from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatMessage
from app.services.agent import run_agent_with_history

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)

# In-memory conversation store
MAX_HISTORY = 50
conversation_store: dict[str, list[ChatMessage]] = {}

async def event_generator(session_id: str, question: str) -> AsyncGenerator[str, None]:
    """
    Generate SSE events for the chat stream.
    """
    # 1. Retrieve or init history
    if session_id not in conversation_store:
        conversation_store[session_id] = []
    
    history = conversation_store[session_id]
    
    # 2. Append User Message
    history.append(ChatMessage(role="user", content=question))
    
    # 3. Call Agent and Stream
    full_answer = ""
    try:
        async for token in run_agent_with_history(history):
            full_answer += token
            # Yield token event
            data = json.dumps({"type": "token", "content": token})
            yield f"event: token\ndata: {data}\n\n"
    except Exception as e:
        logger.error(f"Agent run failed: {e}")
        error_data = json.dumps({"type": "error", "content": str(e)})
        yield f"event: error\ndata: {error_data}\n\n"
        return

    # 4. Append Assistant Message to History
    history.append(ChatMessage(role="assistant", content=full_answer))
    
    # 5. Truncate History
    if len(history) > MAX_HISTORY:
        conversation_store[session_id] = history[-MAX_HISTORY:]

    # 6. Done Event
    yield "event: done\ndata: {\"type\": \"done\"}\n\n"

@router.get("/stream")
async def stream_chat(
    session_id: str = Query(..., description="Unique session ID"), 
    question: str = Query(..., description="User's question")
):
    """
    Stream chat response using Server-Sent Events (SSE).
    """
    logger.info(f"Starting chat stream for session {session_id}")
    return StreamingResponse(
        event_generator(session_id, question),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
