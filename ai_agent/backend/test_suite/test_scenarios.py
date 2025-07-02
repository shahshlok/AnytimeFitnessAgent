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
    "initial_query": "Ask if the gym has 24/7 access, because I work night shifts.",
    "potential_follow_ups": [
        "Ask about membership costs.",
        "Ask about the kinds of equipment available.",
        "Ask if there are any group classes like yoga or Zumba.",
        "Ask how crowded it gets late at night."
    ],
    "scenario_description": "Direct Member Inquiry - User directly asks about gym membership"
    },
    
    "trial_pass_interest": {
        "name": "Ankit Mehta",
        "email": "ankit.mehta89@rediffmail.com",
        "age": 36,
        "background": "IT professional in Bengaluru returning to fitness after a long gap",
        "fitness_goal": "Regain stamina and lose weight post-COVID lifestyle",
        "communication_style": "Curious, a bit hesitant, wants reassurance before committing",
        "initial_query": "Ask if there's a trial pass or free session available before joining.",
        "potential_follow_ups": [
            "Ask about what facilities are available.",
            "Ask if the gym gets crowded during certain hours.",
            "Ask about the equipment and how well-maintained it is.",
            "Ask about hygiene standards and cleanliness.",
            "Ask about membership costs after the trial."
        ],
        "scenario_description": "Trial Pass Interest - User asks about trying the gym first"
    },
    
    "personal_training_focus": {
        "name": "Priya Nair",
        "email": "priya.nair@outlook.in",
        "age": 27,
        "background": "Yoga practitioner and fitness influencer from Kochi",
        "fitness_goal": "Add strength training to her routine with expert guidance", 
        "communication_style": "Friendly, detail-oriented, asks about credentials and programs",
        "initial_query": "Ask about personal training services and certified trainers.",
        "potential_follow_ups": [
            "Ask if there are female personal trainers available.",
            "Ask about group fitness classes or sessions.",
            "Ask about trainer credentials and certifications.",
            "Ask about progress tracking and workout programs.",
            "Ask about pricing for personal training sessions."
        ],
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