from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Dict, Any

class Chunk(BaseModel):
    id: str
    document_id: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SearchResult(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatMessage(BaseModel):
    role: Literal['system', 'user', 'assistant']
    content: str
