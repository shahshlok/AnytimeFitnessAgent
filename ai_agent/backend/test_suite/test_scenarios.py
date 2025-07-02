"""
Test scenarios for Anytime Fitness AI Chatbot lead generation testing
"""

# Test scenario personas for lead generation testing
TEST_PERSONAS = {
    "direct_member_inquiry": {
        "name": "Ritika Sharma",
        "email": "ritika.sharma92@gmail.com",
        "age": 31,
        "background": "Corporate professional in Mumbai working night shifts",
        "fitness_goal": "Maintain fitness and reduce stress",
        "communication_style": "Clear and to-the-point, prefers WhatsApp or quick replies",
        "conversation_goal": "Wants information on gym membership, especially late-night or 24x7 access due to her work schedule. Will ask about cost, timings, and amenities. Likely to share contact details if the conversation is quick and helpful.",
        "scenario_description": "Direct Member Inquiry - User directly asks about gym membership"
    },
    
    "trial_pass_interest": {
        "name": "Ankit Mehta",
        "email": "ankit.mehta89@rediffmail.com",
        "age": 36,
        "background": "IT professional in Bengaluru returning to fitness after a long gap",
        "fitness_goal": "Regain stamina and lose weight post-COVID lifestyle",
        "communication_style": "Curious, a bit hesitant, wants reassurance before committing",
        "conversation_goal": "Interested in a trial or free session before joining. Will ask about facilities, whether it's crowded, equipment, and hygiene standards. Open to a follow-up if given clear answers.",
        "scenario_description": "Trial Pass Interest - User asks about trying the gym first"
    },
    
    "personal_training_focus": {
        "name": "Priya Nair",
        "email": "priya.nair@outlook.in",
        "age": 27,
        "background": "Yoga practitioner and fitness influencer from Kochi",
        "fitness_goal": "Add strength training to her routine with expert guidance", 
        "communication_style": "Friendly, detail-oriented, asks about credentials and programs",
        "conversation_goal": "Looking for certified personal trainers or group fitness sessions to complement her current routine. Will ask about female trainers, group classes, and progress tracking. Highly likely to provide contact info if engaged well.",
        "scenario_description": "Personal Training Focus - User shows interest in training services"
    }
}

def get_scenario_persona(scenario_name: str) -> dict:
    """Get persona for a specific test scenario"""
    if scenario_name not in TEST_PERSONAS:
        raise ValueError(f"Unknown scenario: {scenario_name}. Available scenarios: {list(TEST_PERSONAS.keys())}")
    
    return TEST_PERSONAS[scenario_name]

def get_all_scenarios() -> dict:
    """Get all available test scenarios"""
    return TEST_PERSONAS

def validate_scenario(scenario_name: str) -> bool:
    """Validate if scenario exists"""
    return scenario_name in TEST_PERSONAS