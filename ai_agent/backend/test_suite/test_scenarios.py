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
    },
    "budget_conscious_browsing": {
        "name": "Rajeev Kumar",
        "email": "rajeev.kumar84@yahoo.com",
        "age": 40,
        "background": "Government clerk in Patna with a tight budget",
        "fitness_goal": "Improve health without spending too much",
        "communication_style": "Polite and cautious, asks many cost-related questions",
        "initial_query": "Ask if there are any budget membership plans or discounts.",
        "potential_follow_ups": [
            "Ask about family or couple membership offers.",
            "Ask about EMI or monthly payment options.",
            "Ask about cancellation or refund policies.",
            "Ask about hidden charges or enrollment fees."
        ],
        "scenario_description": "Budget Conscious Browsing - User looking for affordable options"
    },
    "casual_interest_non_lead": {
        "name": "Sahil Verma",
        "email": "sahil.v.official@gmail.com",
        "age": 22,
        "background": "College student in Pune exploring gym options out of curiosity",
        "fitness_goal": "Not sure yet, maybe build some muscle",
        "communication_style": "Casual, informal, uses emojis or slang, often disengaged mid-convo",
        "initial_query": "Hey, just checking — is the gym open on Sundays?",
        "potential_follow_ups": [
            "Ask if students get any discount.",
            "Ask if WiFi is available at the gym.",
            "Ghosts the chatbot after 1-2 messages."
        ],
        "scenario_description": "Casual Interest - User isn’t ready to commit, possibly just browsing"
    },
    "elderly_health_focus": {
        "name": "Meena Joshi",
        "email": "meenajoshi60@gmail.com",
        "age": 63,
        "background": "Retired school teacher from Ahmedabad looking to stay active",
        "fitness_goal": "Improve mobility and maintain general health",
        "communication_style": "Respectful, needs slow-paced clear responses",
        "initial_query": "Ask if the gym has programs for senior citizens.",
        "potential_follow_ups": [
            "Ask about low-impact or physiotherapy-friendly exercises.",
            "Ask about trainer support and supervision.",
            "Ask if any group activities are available for seniors.",
            "Ask about morning timings and safety measures."
        ],
        "scenario_description": "Elderly Health Focus - User needs age-specific fitness support"
    },
    "family_fitness_package": {
        "name": "Harshita Rao",
        "email": "harshita.rao23@gmail.com",
        "age": 35,
        "background": "HR Manager in Hyderabad, looking for a gym plan for her whole family",
        "fitness_goal": "Create a regular fitness routine with her spouse and teenage son",
        "communication_style": "Goal-oriented and decisive, wants efficient answers",
        "initial_query": "Ask if there are any family membership packages available.",
        "potential_follow_ups": [
            "Ask about teenage-friendly programs.",
            "Ask if couples can train together.",
            "Ask about availability of weekend group sessions.",
            "Ask about discounts for long-term signups."
        ],
        "scenario_description": "Family Fitness Package - User wants multi-member deals"
    },
    "weight_loss_specific_goal": {
        "name": "Imran Sheikh",
        "email": "imran.sheikh90@protonmail.com",
        "age": 34,
        "background": "Startup founder in Delhi under high work stress and poor routine",
        "fitness_goal": "Lose 15 kg in the next 6 months with measurable progress",
        "communication_style": "Very results-driven, asks data-driven questions",
        "initial_query": "Ask if the gym offers customized weight loss plans.",
        "potential_follow_ups": [
            "Ask about diet consultation or tie-ups with nutritionists.",
            "Ask how progress is measured and tracked.",
            "Ask if trainers specialize in fat loss.",
            "Ask about before-after success stories."
        ],
        "scenario_description": "Weight Loss Specific Goal - User seeks structured fat loss program"
    },
    "female_safety_concern": {
        "name": "Tanvi Deshmukh",
        "email": "tanvi.deshmukh01@gmail.com",
        "age": 29,
        "background": "Freelance graphic designer in Nagpur, works from home",
        "fitness_goal": "Get toned and build stamina in a safe and supportive environment",
        "communication_style": "Assertive, expects prompt and respectful responses",
        "initial_query": "Ask if the gym has women-only hours or areas.",
        "potential_follow_ups": [
            "Ask if there are female trainers available.",
            "Ask about CCTV and locker security.",
            "Ask about harassment policies or female feedback.",
            "Ask if there are women-centric group classes."
        ],
        "scenario_description": "Female Safety Concern - User emphasizes privacy and security"
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