"""
Session and Chat History Service
Manages chat sessions and message history using SQLite
"""
import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..models.session_schemas import ChatSession, ChatMessage, SessionListResponse, SessionDetailResponse
import logging
import os

logger = logging.getLogger(__name__)

class SessionService:
    def __init__(self, db_path: str = "./sessions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database and create tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS chat_sessions (
                        session_id TEXT PRIMARY KEY,
                        document_id TEXT NOT NULL,
                        document_name TEXT NOT NULL,
                        document_filename TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        last_activity TIMESTAMP NOT NULL,
                        message_count INTEGER DEFAULT 0,
                        model_provider TEXT
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS chat_messages (
                        id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        message_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP NOT NULL,
                        model_used TEXT,
                        context_sources TEXT,
                        FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
                    )
                ''')
                
                # Create indexes for better performance
                conn.execute('CREATE INDEX IF NOT EXISTS idx_session_document ON chat_sessions(document_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_session_activity ON chat_sessions(last_activity)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_message_session ON chat_messages(session_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_message_timestamp ON chat_messages(timestamp)')
                
                conn.commit()
                logger.info("Session database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize session database: {e}")
            raise
    
    def create_session(self, document_id: str, document_name: str, document_filename: str, model_provider: str = None) -> ChatSession:
        """Create a new chat session for a document"""
        try:
            session_id = str(uuid.uuid4())
            now = datetime.now()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO chat_sessions 
                    (session_id, document_id, document_name, document_filename, created_at, last_activity, model_provider)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (session_id, document_id, document_name, document_filename, now, now, model_provider))
                conn.commit()
            
            session = ChatSession(
                session_id=session_id,
                document_id=document_id,
                document_name=document_name,
                document_filename=document_filename,
                created_at=now,
                last_activity=now,
                message_count=0,
                model_provider=model_provider
            )
            
            logger.info(f"Created new session: {session_id} for document: {document_name}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a specific session by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM chat_sessions WHERE session_id = ?
                ''', (session_id,))
                
                row = cursor.fetchone()
                if row:
                    return ChatSession(
                        session_id=row['session_id'],
                        document_id=row['document_id'],
                        document_name=row['document_name'],
                        document_filename=row['document_filename'],
                        created_at=datetime.fromisoformat(row['created_at']),
                        last_activity=datetime.fromisoformat(row['last_activity']),
                        message_count=row['message_count'],
                        model_provider=row['model_provider']
                    )
                return None
                
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    def get_sessions(self, limit: int = 50, offset: int = 0) -> SessionListResponse:
        """Get list of all sessions, ordered by last activity"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get total count
                count_cursor = conn.execute('SELECT COUNT(*) as total FROM chat_sessions')
                total_count = count_cursor.fetchone()['total']
                
                # Get sessions
                cursor = conn.execute('''
                    SELECT * FROM chat_sessions 
                    ORDER BY last_activity DESC 
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
                
                sessions = []
                for row in cursor.fetchall():
                    sessions.append(ChatSession(
                        session_id=row['session_id'],
                        document_id=row['document_id'],
                        document_name=row['document_name'],
                        document_filename=row['document_filename'],
                        created_at=datetime.fromisoformat(row['created_at']),
                        last_activity=datetime.fromisoformat(row['last_activity']),
                        message_count=row['message_count'],
                        model_provider=row['model_provider']
                    ))
                
                return SessionListResponse(sessions=sessions, total_count=total_count)
                
        except Exception as e:
            logger.error(f"Failed to get sessions: {e}")
            return SessionListResponse(sessions=[], total_count=0)
    
    def get_sessions_by_document(self, document_id: str) -> List[ChatSession]:
        """Get all sessions for a specific document"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM chat_sessions 
                    WHERE document_id = ? 
                    ORDER BY last_activity DESC
                ''', (document_id,))
                
                sessions = []
                for row in cursor.fetchall():
                    sessions.append(ChatSession(
                        session_id=row['session_id'],
                        document_id=row['document_id'],
                        document_name=row['document_name'],
                        document_filename=row['document_filename'],
                        created_at=datetime.fromisoformat(row['created_at']),
                        last_activity=datetime.fromisoformat(row['last_activity']),
                        message_count=row['message_count'],
                        model_provider=row['model_provider']
                    ))
                
                return sessions
                
        except Exception as e:
            logger.error(f"Failed to get sessions for document {document_id}: {e}")
            return []
    
    def save_message(self, session_id: str, message_type: str, content: str, 
                    model_used: str = None, context_sources: List[Dict[str, Any]] = None) -> ChatMessage:
        """Save a message to a session"""
        try:
            message_id = str(uuid.uuid4())
            now = datetime.now()
            context_json = json.dumps(context_sources) if context_sources else None
            
            with sqlite3.connect(self.db_path) as conn:
                # Insert message
                conn.execute('''
                    INSERT INTO chat_messages 
                    (id, session_id, message_type, content, timestamp, model_used, context_sources)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (message_id, session_id, message_type, content, now, model_used, context_json))
                
                # Update session activity and message count
                conn.execute('''
                    UPDATE chat_sessions 
                    SET last_activity = ?, message_count = message_count + 1
                    WHERE session_id = ?
                ''', (now, session_id))
                
                conn.commit()
            
            message = ChatMessage(
                id=message_id,
                session_id=session_id,
                message_type=message_type,
                content=content,
                timestamp=now,
                model_used=model_used,
                context_sources=context_sources
            )
            
            logger.info(f"Saved message to session {session_id}")
            return message
            
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            raise
    
    def get_session_messages(self, session_id: str, limit: int = 100, offset: int = 0) -> List[ChatMessage]:
        """Get messages for a specific session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM chat_messages 
                    WHERE session_id = ? 
                    ORDER BY timestamp ASC 
                    LIMIT ? OFFSET ?
                ''', (session_id, limit, offset))
                
                messages = []
                for row in cursor.fetchall():
                    context_sources = None
                    if row['context_sources']:
                        try:
                            context_sources = json.loads(row['context_sources'])
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse context sources for message {row['id']}")
                    
                    messages.append(ChatMessage(
                        id=row['id'],
                        session_id=row['session_id'],
                        message_type=row['message_type'],
                        content=row['content'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        model_used=row['model_used'],
                        context_sources=context_sources
                    ))
                
                return messages
                
        except Exception as e:
            logger.error(f"Failed to get messages for session {session_id}: {e}")
            return []
    
    def get_session_detail(self, session_id: str) -> Optional[SessionDetailResponse]:
        """Get complete session details including messages"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        messages = self.get_session_messages(session_id)
        return SessionDetailResponse(session=session, messages=messages)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Delete messages first (foreign key constraint)
                conn.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
                # Delete session
                cursor = conn.execute('DELETE FROM chat_sessions WHERE session_id = ?', (session_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Deleted session: {session_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    def update_session_model(self, session_id: str, model_provider: str) -> bool:
        """Update the model provider for a session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    UPDATE chat_sessions 
                    SET model_provider = ?, last_activity = ?
                    WHERE session_id = ?
                ''', (model_provider, datetime.now(), session_id))
                conn.commit()
                
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Failed to update session model: {e}")
            return False


# Global session service instance
session_service = SessionService()
