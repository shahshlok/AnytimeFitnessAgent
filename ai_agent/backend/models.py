

from sqlalchemy import (Column, BigInteger, String, Text, Integer, Boolean,
                      SmallInteger, DateTime, ForeignKey, CheckConstraint)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base  

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(BigInteger, primary_key=True)
    session_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(BigInteger, primary_key=True)
    conversation_id = Column(BigInteger, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False)
    role = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    response_time_ms = Column(Integer)
    is_unanswered = Column(Boolean, default=False)
    api_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint(role.in_(['user', 'assistant']), name='check_role'),
    )
    
    conversation = relationship("Conversation", back_populates="messages")
    feedback = relationship("UserFeedback", back_populates="message", uselist=False, cascade="all, delete-orphan")

class UserFeedback(Base):
    __tablename__ = 'user_feedback'
    
    id = Column(BigInteger, primary_key=True)
    message_id = Column(BigInteger, ForeignKey('chat_messages.id', ondelete='CASCADE'), unique=True, nullable=False)
    rating = Column(SmallInteger, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint(rating.in_([-1, 1]), name='check_rating'),
    )
    
    message = relationship("ChatMessage", back_populates="feedback")