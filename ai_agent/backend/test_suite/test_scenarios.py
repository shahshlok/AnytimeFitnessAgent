"""
Test scenarios for Anytime Fitness AI Chatbot diverse interaction testing

⚠️  DEPRECATION WARNING ⚠️ 
This file is deprecated and will be removed in a future version.
Please use persona_manager.py and persona.json instead.
The JSON-based approach provides enhanced filtering, validation, and management capabilities.
"""
import warnings

# Test scenario personas for diverse chatbot interaction testing
TEST_PERSONAS = {
    "serious_gym_seeker": {
        "name": "Arjun Patel",
        "email": "arjun.patel91@gmail.com",
        "age": 32,
        "background": "Software engineer in Bangalore looking for serious fitness commitment",
        "fitness_goal": "Build strength and muscle mass with structured training",
        "communication_style": "Direct, focused, asks detailed questions about facilities",
        "initial_query": "I'm looking for a gym with proper weightlifting equipment and squat racks.",
        "potential_follow_ups": [
            "Ask about peak hours and equipment availability.",
            "Ask about personal trainer credentials.",
            "Ask about membership plans and pricing.",
            "Express interest in signing up if facilities meet requirements."
        ],
        "scenario_description": "Serious Gym Seeker - Potential lead with specific fitness goals"
    },
    "chatty_socializer": {
        "name": "Riya Kapoor",
        "email": "riya.kapoor@yahoo.in",
        "age": 26,
        "background": "Marketing executive in Mumbai who loves to chat and make friends",
        "fitness_goal": "Social fitness, meeting new people while staying active",
        "communication_style": "Very talkative, goes off-topic frequently, asks about everything",
        "initial_query": "Hi! I saw your gym online. Do you have good music? I love working out to Bollywood songs!",
        "potential_follow_ups": [
            "Share stories about previous gym experiences.",
            "Ask about the social scene and making friends.",
            "Discuss favorite workout music and ask about sound system.",
            "Talk about weekend plans and social activities.",
            "Ask random questions about staff, decor, and atmosphere."
        ],
        "scenario_description": "Chatty Socializer - Uses chatbot to socialize and talk about various topics"
    },
    "philosophical_questioner": {
        "name": "Vikram Singh",
        "email": "vikram.philosopher@protonmail.com",
        "age": 45,
        "background": "Philosophy professor in Delhi who questions everything and loves deep conversations",
        "fitness_goal": "Holistic wellness and mental-physical balance",
        "communication_style": "Intellectual, asks existential questions, goes into philosophical tangents",
        "initial_query": "What is the true purpose of physical fitness in the modern human experience?",
        "potential_follow_ups": [
            "Discuss the philosophy of mind-body connection.",
            "Ask about the gym's approach to holistic wellness.",
            "Question the commercialization of fitness.",
            "Talk about ancient Indian fitness practices vs modern methods.",
            "Ask if the gym promotes mindful exercise."
        ],
        "scenario_description": "Philosophical Questioner - Tests chatbot's ability to handle abstract conversations"
    },
    "tech_troubleshooter": {
        "name": "Aditi Sharma",
        "email": "aditi.tech@gmail.com",
        "age": 28,
        "background": "IT support specialist in Pune who tests systems and finds bugs",
        "fitness_goal": "Stay fit while working long hours in tech",
        "communication_style": "Analytical, tries to break the chatbot, asks edge case questions",
        "initial_query": "What happens if I type really long messages like this one that goes on and on and on and has no real point but I want to see how you handle it?",
        "potential_follow_ups": [
            "Send messages with special characters: @#$%^&*().",
            "Ask the same question multiple times in different ways.",
            "Try to get the chatbot to contradict itself.",
            "Ask impossible questions like 'What's the weight of your thoughts?'.",
            "Test the chatbot's memory by referencing things from 10 messages ago."
        ],
        "scenario_description": "Tech Troubleshooter - Tests chatbot limits and edge cases"
    },
    "lonely_senior": {
        "name": "Rajesh Uncle",
        "email": "rajesh.uncle67@gmail.com",
        "age": 67,
        "background": "Retired bank manager in Kolkata who lives alone and craves conversation",
        "fitness_goal": "Stay active and have someone to talk to",
        "communication_style": "Lonely, shares personal stories, talks about family and past",
        "initial_query": "Beta, I'm feeling very lonely these days. My children are busy. Do you have time to chat?",
        "potential_follow_ups": [
            "Share stories about his grandchildren and family.",
            "Talk about his health concerns and doctor visits.",
            "Discuss his late wife and memories.",
            "Ask about the chatbot's 'family' and personal life.",
            "Share opinions about today's youth and changing times."
        ],
        "scenario_description": "Lonely Senior - Uses chatbot for companionship and emotional support"
    },
    "conspiracy_theorist": {
        "name": "Rohit Mishra",
        "email": "rohit.truthseeker@rediffmail.com",
        "age": 38,
        "background": "Freelance journalist in Lucknow who questions everything and believes in conspiracies",
        "fitness_goal": "Expose the truth about the fitness industry",
        "communication_style": "Suspicious, asks probing questions, brings up conspiracy theories",
        "initial_query": "Are you recording this conversation? Who has access to my data?",
        "potential_follow_ups": [
            "Ask about data privacy and surveillance.",
            "Question the gym's corporate affiliations.",
            "Discuss fitness industry conspiracies.",
            "Ask about hidden cameras and monitoring.",
            "Talk about government health policies and control."
        ],
        "scenario_description": "Conspiracy Theorist - Tests chatbot's handling of suspicious and paranoid users"
    },
    "meme_lord_teenager": {
        "name": "Aarav Gupta",
        "email": "aarav.memes@gmail.com",
        "age": 17,
        "background": "High school student in Gurgaon who communicates primarily through memes and slang",
        "fitness_goal": "Get swole for Instagram pics",
        "communication_style": "Uses Gen Z slang, memes, abbreviations, and internet language",
        "initial_query": "yo this gym looks mid ngl 💀 do u even lift bro? fr fr no cap",
        "potential_follow_ups": [
            "Use heavy internet slang and abbreviations.",
            "Ask about Instagram-worthy spots in the gym.",
            "Reference popular memes and trends.",
            "Use terms like 'sus', 'slay', 'periodt', 'no cap', 'bussin'.",
            "Ask if the gym is 'aesthetic' enough for social media."
        ],
        "scenario_description": "Meme Lord Teenager - Tests chatbot's ability to understand modern slang and youth culture"
    },
    "medical_anxiety_person": {
        "name": "Kavya Iyer",
        "email": "kavya.health@outlook.com",
        "age": 35,
        "background": "Accountant in Chennai with health anxiety and multiple medical concerns",
        "fitness_goal": "Exercise safely without triggering health issues",
        "communication_style": "Anxious, asks many health-related questions, very cautious",
        "initial_query": "I have diabetes, high blood pressure, and knee problems. Is it safe for me to exercise?",
        "potential_follow_ups": [
            "Ask about medical clearance requirements.",
            "Discuss various health conditions and exercise restrictions.",
            "Ask about emergency procedures and first aid.",
            "Want to know about insurance and liability.",
            "Ask about specific exercises for medical conditions."
        ],
        "scenario_description": "Medical Anxiety Person - Tests chatbot's handling of health-related queries and boundaries"
    },
    "price_haggler": {
        "name": "Suresh Agarwal",
        "email": "suresh.deals@gmail.com",
        "age": 52,
        "background": "Business owner in Jaipur who loves to negotiate and find the best deals",
        "fitness_goal": "Get fit while spending the least amount of money",
        "communication_style": "Persistent negotiator, asks for discounts, compares prices constantly",
        "initial_query": "What's your best price? I can get membership at Gold's Gym for ₹500 less.",
        "potential_follow_ups": [
            "Ask for discounts, offers, and deals.",
            "Compare prices with other gyms.",
            "Ask about free trials and money-back guarantees.",
            "Try to negotiate custom packages.",
            "Ask about referral bonuses and loyalty programs."
        ],
        "scenario_description": "Price Haggler - Tests chatbot's ability to handle price negotiations and comparisons"
    },
    "random_topic_jumper": {
        "name": "Neha Jain",
        "email": "neha.random@gmail.com",
        "age": 29,
        "background": "Graphic designer in Ahmedabad with ADHD who jumps between topics constantly",
        "fitness_goal": "Stay focused and improve concentration through exercise",
        "communication_style": "Scattered, changes topics mid-conversation, asks unrelated questions",
        "initial_query": "Do you have treadmills? Oh wait, do you know where I can get good samosas nearby?",
        "potential_follow_ups": [
            "Jump from gym questions to food recommendations.",
            "Ask about completely unrelated topics like weather or movies.",
            "Start talking about pets, family, or work suddenly.",
            "Ask about local attractions and places to visit.",
            "Discuss current events or social media trends randomly."
        ],
        "scenario_description": "Random Topic Jumper - Tests chatbot's ability to handle scattered conversations and topic changes"
    }
}

def get_scenario_persona(scenario_name: str) -> dict:
    """Get persona for a specific test scenario"""
    warnings.warn(
        "test_scenarios.py is deprecated. Use persona_manager.py instead.",
        DeprecationWarning,
        stacklevel=2
    )
    if scenario_name not in TEST_PERSONAS:
        raise ValueError(f"Unknown scenario: {scenario_name}. Available scenarios: {list(TEST_PERSONAS.keys())}")
    
    return TEST_PERSONAS[scenario_name]

def get_all_scenarios() -> dict:
    """Get all available test scenarios"""
    warnings.warn(
        "test_scenarios.py is deprecated. Use persona_manager.py instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return TEST_PERSONAS

def validate_scenario(scenario_name: str) -> bool:
    """Validate if scenario exists"""
    warnings.warn(
        "test_scenarios.py is deprecated. Use persona_manager.py instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return scenario_name in TEST_PERSONAS