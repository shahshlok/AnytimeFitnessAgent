"""
SQLAlchemy models for the Anytime Fitness AI Test Suite
Following the same patterns as the main backend models
"""

from sqlalchemy import Column, BigInteger, String, Text, ForeignKey, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .test_database import TestBase

class TestRun(TestBase):
    __tablename__ = "test_runs"
    
    id = Column(BigInteger, primary_key=True, index=True)
    scenario_name = Column(String(100), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    success = Column(Boolean, default=False)
    lead_generated = Column(Boolean, default=False)
    total_messages = Column(Integer, default=0)
    conversation_duration_seconds = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    test_metadata = Column(JSONB, nullable=True)
    
    # One-to-many relationships
    messages = relationship("TestMessage", back_populates="test_run", cascade="all, delete-orphan")
    leads = relationship("TestLead", back_populates="test_run", cascade="all, delete-orphan")
    conversation_summary = relationship("TestConversationSummary", back_populates="test_run", uselist=False, cascade="all, delete-orphan")

class TestMessage(TestBase):
    __tablename__ = "test_messages"
    
    id = Column(BigInteger, primary_key=True, index=True)
    test_run_id = Column(BigInteger, ForeignKey("test_runs.id"), nullable=False)
    message_order = Column(Integer, nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    extra_data = Column(JSONB, nullable=True)
    
    # Many-to-one relationship with test run
    test_run = relationship("TestRun", back_populates="messages")

class TestLead(TestBase):
    __tablename__ = "test_leads"
    
    id = Column(BigInteger, primary_key=True, index=True)
    test_run_id = Column(BigInteger, ForeignKey("test_runs.id"), nullable=False)
    name = Column(String(200), nullable=True)
    email = Column(String(200), nullable=True)
    summary = Column(Text, nullable=True)
    hubspot_status = Column(String(50), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Many-to-one relationship with test run
    test_run = relationship("TestRun", back_populates="leads")

class TestConversationSummary(TestBase):
    __tablename__ = "test_conversation_summaries"
    
    id = Column(BigInteger, primary_key=True, index=True)
    test_run_id = Column(BigInteger, ForeignKey("test_runs.id"), nullable=False)
    conversation_type = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    model_used = Column(String(100), default="gpt-4.1-nano")
    tokens_used = Column(Integer, nullable=True)
    generation_time_ms = Column(Integer, nullable=True)
    
    # Many-to-one relationship with test run
    test_run = relationship("TestRun", back_populates="conversation_summary")