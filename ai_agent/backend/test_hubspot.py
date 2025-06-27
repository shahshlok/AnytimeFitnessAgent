import os
from dotenv import load_dotenv
from hubspot_integration import create_lead

# This is a crucial step for standalone scripts.
# It loads the variables from your .env file (like HUBSPOT_PERSONAL_KEY)
# so os.getenv() can find them.
print("Loading environment variables...")
load_dotenv()

# --- Your Test Data ---
# Feel free to change these values for your test.
test_name = "Some Test Name"
test_email = "test_abc.com"
test_summary = "This is a test lead generated directly from the test_hubspot.py script. The user expressed interest in a yearly membership."

# --- Calling Your Function ---
print(f"Attempting to create a HubSpot lead for: {test_email}")
create_lead(
    name=test_name,
    email=test_email,
    summary=test_summary
)
print("Test script finished.")