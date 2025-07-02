#!/usr/bin/env python3
"""
Setup script for the automated testing database using SQLAlchemy
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_postgres_credentials():
    """Extract PostgreSQL credentials from main DATABASE_URL"""
    main_db_url = os.getenv("DATABASE_URL")
    
    # Use the known working credentials from docker-compose.yml
    if not main_db_url or "localhost" not in main_db_url:
        # Running in Docker - connect to the db container
        logger.info("Using Docker database container credentials")
        return {
            "host": "db",  # Docker service name
            "port": "5432",
            "user": "anytime_fitness_user",
            "password": "anytime_fitness_password",
            "database": "af_chatbot_db"  # Connect to existing database first
        }
    else:
        # Running locally - connect to localhost
        logger.info("Using localhost database credentials")
        return {
            "host": "localhost",
            "port": "5432", 
            "user": "anytime_fitness_user",
            "password": "anytime_fitness_password",
            "database": "af_chatbot_db"  # Connect to existing database first
        }

def create_test_database():
    """Create the automated testing database if it doesn't exist"""
    try:
        creds = get_postgres_credentials()
        
        # Connect to existing database first (af_chatbot_db) to create new database
        conn = psycopg2.connect(
            host=creds["host"],
            port=creds["port"],
            user=creds["user"],
            password=creds["password"],
            database=creds["database"]  # Connect to existing database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'automated_testing'")
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            cursor.execute("CREATE DATABASE automated_testing")
            logger.info("Created automated_testing database")
        else:
            logger.info("automated_testing database already exists")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create test database: {e}")
        return False

def setup_test_tables():
    """Create tables in the test database using SQLAlchemy"""
    try:
        # Initialize the database connection now that the database exists
        from .test_database import initialize_test_database, TestDatabase
        
        # Initialize the engine and session maker
        initialize_test_database()
        
        # Create the tables
        test_db = TestDatabase()
        if test_db.create_all_tables():
            logger.info("Test database tables created successfully")
            return True
        else:
            return False
            
    except Exception as e:
        logger.error(f"Failed to setup test tables: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("Setting up automated testing database...")
    
    # Step 1: Create database
    if not create_test_database():
        logger.error("Failed to create test database")
        sys.exit(1)
    
    # Step 2: Create tables using SQLAlchemy
    if not setup_test_tables():
        logger.error("Failed to create test tables")
        sys.exit(1)
    
    logger.info("Test database setup completed successfully!")
    logger.info("Database: automated_testing")
    
    # Show the connection URL that will be used
    from .test_database import TEST_DATABASE_URL
    logger.info(f"Connection URL: {TEST_DATABASE_URL}")

if __name__ == "__main__":
    main()