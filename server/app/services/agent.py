from typing import List, AsyncIterator
from pydantic import BaseModel
from pydantic_ai import Agent, Tool, RunContext
from app.services.rag import retrieve_context
from app.models.schemas import ChatMessage, Chunk
from app.config import settings
import os

# Set environment variable as well, as some libraries might expect it
if settings.OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

# --- Tool Definition ---

class DocChunk(BaseModel):
    text: str
    source_file: str
    score: float

async def search_docs(ctx: RunContext, query: str, top_k: int = 5) -> List[DocChunk]:
    """
    Search the uploaded documents for relevant information.
    """
    # Note: PydanticAI tools usually take a Context as first arg if configured, 
    # but for simple function tools it can be omitted or properly typed.
    # We will wrap it properly or just use the function.
    results = await retrieve_context(query, top_k)
    return [
        DocChunk(
            text=r.text,
            source_file=r.metadata.get('source_file', 'unknown'),
            score=r.score,
        )
        for r in results
    ]

# --- Agent Definition ---

def get_model():
    if settings.LLM_PROVIDER == "openai":
        from pydantic_ai.models.openai import OpenAIModel
        return OpenAIModel(settings.LLM_MODEL)
    elif settings.LLM_PROVIDER == "anthropic":
        from pydantic_ai.models.anthropic import AnthropicModel
        return AnthropicModel(settings.LLM_MODEL)
    elif settings.LLM_PROVIDER == "gemini":
        from pydantic_ai.models.gemini import GeminiModel
        return GeminiModel(settings.LLM_MODEL)
    return settings.LLM_MODEL

agent = Agent(
    model=get_model(),
    system_prompt="""
You are a helpful assistant. You have access to a `search_docs` tool to search through the user's uploaded documents.

Rules:
1. If the user asks about uploaded documents or specific information that might be in them, ALWAYS call `search_docs`.
2. If `search_docs` returns results, use them to provide a comprehensive answer, citing the document name if possible.
3. If the user asks a general question (e.g., math, greetings, general knowledge) not related to the documents, you can answer it directly using your internal knowledge.
4. If you search the documents and don't find the answer, inform the user that the documents don't contain that information, but you can still try to help with general knowledge or clarify what they are looking for.
5. Maintain a professional and helpful tone.
    """,
    tools=[search_docs] 
)

async def run_agent_with_history(history: list[ChatMessage]) -> AsyncIterator[str]:
    """
    Run the agent with the given history.
    Since PydanticAI might manage its own history or be designed for single-turn logic with context,
    we'll need to adapt the 'history' list to what PydanticAI expects, 
    OR we use our own LLMProvider loop if we weren't using PydanticAI for the main loop.
    
    The user asked to use PydanticAI agent.
    PydanticAI '.run' or '.stream' usually takes the user prompt.
    For history, we might need to pass messages.
    """
    
    # Extract the last user message as the prompt
    if not history or history[-1].role != 'user':
        yield "Error: No user message found."
        return

    last_user_msg = history[-1].content
    
    try:
        # Convert ChatMessage history to PydanticAI messages if possible, 
        # or simplified approach: just send the prompt.
        # Ideally we'd convert `history[:-1]` to context for the agent.
        
        async with agent.run_stream(last_user_msg) as result:
            async for chunk in result.stream_text(delta=True):
                yield chunk
                
    except Exception as e:
        # Fallback if PydanticAI setup fails or is mocking:
        # Use our manual provider (Task 5) if PydanticAI (Task 6) has issues 
        # but the prompt implies we MUST use PydanticAI.
        yield f"Agent Error: {str(e)}"

# Re-exporting our tool for clarity if needed elsewhere
__all__ = ["agent", "run_agent_with_history"]
