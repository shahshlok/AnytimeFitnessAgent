"""
Configuration settings for the Anytime Fitness AI Chatbot Test Suite
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = "http://localhost:7479"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Test Database Configuration  
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://anytime_fitness_user:anytime_fitness_password@localhost:5432/af_chatbot_db")

# Test Configuration
MAX_CONVERSATION_MESSAGES = 20  # Safety limit to prevent infinite loops
MESSAGE_DELAY_SECONDS = 1  # Delay between messages to simulate human behavior
SIMULATED_USER_MODEL = "gpt-4.1-mini"

# Test Scenarios
TEST_SCENARIOS = {
    "direct_member_inquiry": {
        "name": "Direct Member Inquiry",
        "description": "User directly asks about gym membership",
        "expected_outcome": "lead_generated"
    },
    "trial_pass_interest": {
        "name": "Trial Pass Interest", 
        "description": "User asks about trying the gym first",
        "expected_outcome": "lead_generated"
    },
    "personal_training_focus": {
        "name": "Personal Training Focus",
        "description": "User shows interest in personal training services",
        "expected_outcome": "lead_generated"
    }
}

# Validation
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY must be set in environment variables")