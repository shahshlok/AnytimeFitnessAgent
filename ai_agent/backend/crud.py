# CRUD operations for managing conversations and messages in the database.
# This module provides functions to create or retrieve conversations and messages,ensuring that conversations are created only when they do not already exist.

from sqlalchemy.orm import Session
from models import Conversation, Message
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

def get_or_create_conversation(db: Session, session_id: uuid.UUID) -> Conversation:
    """
    Find an existing conversation by session_id or create a new one if it doesn't exist.
    
    Args:
        db: Database session
        session_id: UUID of the session
        
    Returns:
        Conversation object
    """
    # Try to find existing conversation
    conversation = db.query(Conversation).filter(Conversation.session_id == session_id).first()
    
    if conversation is None:
        # Create new conversation
        conversation = Conversation(session_id=session_id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    return conversation

def create_message(
    db: Session, 
    conversation_id: int, 
    role: str, 
    content: str, 
    extra_data_payload: Optional[Dict[str, Any]] = None
) -> Message:
    """
    Create a new message record and save it to the database.
    
    Args:
        db: Database session
        conversation_id: ID of the conversation this message belongs to
        role: Message role ('user' or 'assistant')
        content: Message content
        extra_data_payload: Optional extra data dictionary
        
    Returns:
        Message object
    """
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        extra_data=extra_data_payload
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return message