# Connection to the database using SQLAlchemy
# This module sets up the database connection and session management

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
import os
import time
import logging
from dotenv import load_dotenv
from typing import Generator

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")

def create_engine_with_retry(database_url: str, max_retries: int = 10, retry_delay: int = 3):
    """
    Create SQLAlchemy engine with retry mechanism for database connections.
    
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
            logger.info(f"Attempting to connect to database (attempt {attempt}/{max_retries})")
            engine = create_engine(database_url)
            
            # Test the connection
            with engine.connect() as conn:
                logger.info("Database connection successful!")
                return engine
                
        except OperationalError as e:
            if attempt == max_retries:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                raise e
            else:
                logger.warning(f"Database connection failed (attempt {attempt}/{max_retries}): {e}")
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
        except Exception as e:
            logger.error(f"Unexpected error during database connection: {e}")
            raise e

# Create SQLAlchemy engine with retry mechanism
engine = create_engine_with_retry(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()