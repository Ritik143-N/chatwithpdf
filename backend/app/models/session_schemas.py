"""
Session and Chat History Management Models
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    id: Optional[str] = None
    session_id: str
    message_type: str  # 'user', 'bot', 'system'
    content: str
    timestamp: datetime
    model_used: Optional[str] = None
    context_sources: Optional[List[Dict[str, Any]]] = None

class ChatSession(BaseModel):
    session_id: str
    document_id: str
    document_name: str
    document_filename: str
    created_at: datetime
    last_activity: datetime
    message_count: int = 0
    model_provider: Optional[str] = None

class SessionListResponse(BaseModel):
    sessions: List[ChatSession]
    total_count: int

class SessionDetailResponse(BaseModel):
    session: ChatSession
    messages: List[ChatMessage]

class CreateSessionRequest(BaseModel):
    document_id: str
    document_name: str
    document_filename: str

class SaveMessageRequest(BaseModel):
    session_id: str
    message_type: str
    content: str
    model_used: Optional[str] = None
    context_sources: Optional[List[Dict[str, Any]]] = None
