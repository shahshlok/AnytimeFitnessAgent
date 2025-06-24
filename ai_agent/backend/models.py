# The blueprint for the database models using SQLAlchemy ORM.
# This module defines the Conversation and Message models, their relationships, and constraints.
# It also includes necessary imports and configurations for the database connection.

from sqlalchemy import Column, BigInteger, String, Text, ForeignKey, SmallInteger, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid
from datetime import datetime

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    started_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # One-to-many relationship with messages
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(BigInteger, primary_key=True, index=True)
    conversation_id = Column(BigInteger, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    extra_data = Column(JSONB, nullable=True)
    rating = Column(SmallInteger, nullable=True)
    
    # Check constraints
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name='check_role'),
        CheckConstraint("rating IN (-1, 1)", name='check_rating'),
    )
    
    # Many-to-one relationship with conversation
    conversation = relationship("Conversation", back_populates="messages")