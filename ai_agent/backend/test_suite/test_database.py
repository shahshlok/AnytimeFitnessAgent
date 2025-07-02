"""
Test database setup and operations for the Anytime Fitness AI Test Suite
Uses SQLAlchemy following the same patterns as the main backend
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
import os
import time
import logging
from dotenv import load_dotenv
from typing import Generator, Dict, List, Optional
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get test database URL from environment or construct from main database credentials
def get_test_database_url():
    """Get test database URL, using same credentials as main backend but different database name"""
    test_db_url = os.getenv("TEST_DATABASE_URL")
    if test_db_url:
        return test_db_url
    
    # Construct test database URL from main database URL
    main_db_url = os.getenv("DATABASE_URL")
    if main_db_url:
        # Replace database name with 'automated_testing'
        if main_db_url.endswith("/af_chatbot_db"):
            return main_db_url.replace("/af_chatbot_db", "/automated_testing")
        else:
            # Use same host as main database
            if "db:" in main_db_url:
                # Running in Docker
                return "postgresql://anytime_fitness_user:anytime_fitness_password@db:5432/automated_testing"
            else:
                # Running locally
                return "postgresql://anytime_fitness_user:anytime_fitness_password@localhost:5432/automated_testing"
    
    # Final fallback - assume Docker environment since that's what you're using
    return "postgresql://anytime_fitness_user:anytime_fitness_password@db:5432/automated_testing"

TEST_DATABASE_URL = get_test_database_url()

def create_test_engine_with_retry(database_url: str, max_retries: int = 10, retry_delay: int = 3):
    """
    Create SQLAlchemy engine with retry mechanism for test database connections.
    
    Args:
        database_url: Database connection URL
        max_retries: Maximum number of connection attempts
        retry_delay: Delay between retry attempts in seconds
        
    Returns:
        SQLAlchemy engine object
        
    Raises:
        OperationalError: If all connection attempts fail
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempting to connect to test database (attempt {attempt}/{max_retries})")
            engine = create_engine(database_url)
            
            # Test the connection
            with engine.connect() as conn:
                logger.info("Test database connection successful!")
                return engine
                
        except OperationalError as e:
            if attempt == max_retries:
                logger.error(f"Failed to connect to test database after {max_retries} attempts")
                raise e
            else:
                logger.warning(f"Test database connection failed (attempt {attempt}/{max_retries}): {e}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
        except Exception as e:
            logger.error(f"Unexpected error during test database connection: {e}")
            raise e

# We'll create the engine later, after the database exists
test_engine = None

# We'll create the SessionLocal after the engine is created
TestSessionLocal = None

# Create Base class for test models
TestBase = declarative_base()

# Dependency to get test DB session
def get_test_db() -> Generator[Session, None, None]:
    if TestSessionLocal is None:
        raise RuntimeError("Test database not initialized. Run setup first.")
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

def initialize_test_database():
    """Initialize the test database engine and session after database creation"""
    global test_engine, TestSessionLocal
    
    if test_engine is None:
        test_engine = create_test_engine_with_retry(TEST_DATABASE_URL)
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        logger.info("Test database engine initialized")

class TestDatabase:
    """Test database operations class"""
    
    def __init__(self):
        # Initialize the database connection if not already done
        if test_engine is None:
            initialize_test_database()
        self.engine = test_engine
        self.SessionLocal = TestSessionLocal
        
    def create_all_tables(self):
        """Create all test database tables"""
        try:
            # Import models to ensure they're registered with TestBase
            from . import test_models
            
            TestBase.metadata.create_all(bind=self.engine)
            logger.info("Test database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create test database tables: {e}")
            return False
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def create_test_run(self, scenario_name: str, test_metadata: Dict = None) -> int:
        """Create a new test run and return the run ID"""
        from .test_models import TestRun
        
        session = self.get_session()
        try:
            test_run = TestRun(
                scenario_name=scenario_name,
                test_metadata=test_metadata or {}
            )
            session.add(test_run)
            session.commit()
            session.refresh(test_run)
            
            run_id = test_run.id
            logger.info(f"Created test run {run_id} for scenario: {scenario_name}")
            return run_id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create test run: {e}")
            raise
        finally:
            session.close()
    
    def add_test_message(self, test_run_id: int, message_order: int, role: str, 
                        content: str, extra_data: Dict = None):
        """Add a message to a test run"""
        from .test_models import TestMessage
        
        session = self.get_session()
        try:
            message = TestMessage(
                test_run_id=test_run_id,
                message_order=message_order,
                role=role,
                content=content,
                extra_data=extra_data or {}
            )
            session.add(message)
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to add test message: {e}")
            raise
        finally:
            session.close()
    
    def add_test_lead(self, test_run_id: int, name: str, email: str, 
                     summary: str, hubspot_status: str):
        """Record lead generation data"""
        from .test_models import TestLead
        
        session = self.get_session()
        try:
            lead = TestLead(
                test_run_id=test_run_id,
                name=name,
                email=email,
                summary=summary,
                hubspot_status=hubspot_status
            )
            session.add(lead)
            session.commit()
            logger.info(f"Recorded lead generation for test run {test_run_id}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to record test lead: {e}")
            raise
        finally:
            session.close()
    
    def update_test_run_result(self, test_run_id: int, success: bool, 
                              lead_generated: bool, total_messages: int,
                              conversation_duration: int, error_message: str = None):
        """Update test run with final results"""
        from .test_models import TestRun
        
        session = self.get_session()
        try:
            test_run = session.query(TestRun).filter(TestRun.id == test_run_id).first()
            if test_run:
                test_run.success = success
                test_run.lead_generated = lead_generated
                test_run.total_messages = total_messages
                test_run.conversation_duration_seconds = conversation_duration
                test_run.error_message = error_message
                
                session.commit()
                logger.info(f"Updated test run {test_run_id} with results")
            else:
                logger.error(f"Test run {test_run_id} not found")
                
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update test run results: {e}")
            raise
        finally:
            session.close()
    
    def get_test_run_results(self, test_run_id: int) -> Optional[Dict]:
        """Get complete test run results"""
        from .test_models import TestRun, TestMessage, TestLead
        
        session = self.get_session()
        try:
            # Get test run info
            test_run = session.query(TestRun).filter(TestRun.id == test_run_id).first()
            
            if not test_run:
                return None
            
            # Get messages
            messages = session.query(TestMessage).filter(
                TestMessage.test_run_id == test_run_id
            ).order_by(TestMessage.message_order).all()
            
            # Get lead data if any
            leads = session.query(TestLead).filter(TestLead.test_run_id == test_run_id).all()
            
            return {
                'test_run': {
                    'id': test_run.id,
                    'scenario_name': test_run.scenario_name,
                    'timestamp': test_run.timestamp,
                    'success': test_run.success,
                    'lead_generated': test_run.lead_generated,
                    'total_messages': test_run.total_messages,
                    'conversation_duration_seconds': test_run.conversation_duration_seconds,
                    'error_message': test_run.error_message,
                    'test_metadata': test_run.test_metadata
                },
                'messages': [
                    {
                        'id': msg.id,
                        'message_order': msg.message_order,
                        'role': msg.role,
                        'content': msg.content,
                        'timestamp': msg.timestamp,
                        'extra_data': msg.extra_data
                    } for msg in messages
                ],
                'leads': [
                    {
                        'id': lead.id,
                        'name': lead.name,
                        'email': lead.email,
                        'summary': lead.summary,
                        'hubspot_status': lead.hubspot_status,
                        'timestamp': lead.timestamp
                    } for lead in leads
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get test run results: {e}")
            raise
        finally:
            session.close()
    
    def get_recent_test_runs(self, limit: int = 10) -> List[Dict]:
        """Get recent test runs"""
        from .test_models import TestRun
        
        session = self.get_session()
        try:
            test_runs = session.query(TestRun).order_by(
                TestRun.timestamp.desc()
            ).limit(limit).all()
            
            return [
                {
                    'id': run.id,
                    'scenario_name': run.scenario_name,
                    'timestamp': run.timestamp,
                    'success': run.success,
                    'lead_generated': run.lead_generated,
                    'total_messages': run.total_messages,
                    'conversation_duration_seconds': run.conversation_duration_seconds,
                    'error_message': run.error_message
                } for run in test_runs
            ]
            
        except Exception as e:
            logger.error(f"Failed to get recent test runs: {e}")
            raise
        finally:
            session.close()