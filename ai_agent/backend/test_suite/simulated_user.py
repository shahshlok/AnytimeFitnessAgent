"""
Simulated User AI for testing the Anytime Fitness chatbot
"""
import json
import logging
from typing import Dict
from openai import OpenAI
from .config import OPENAI_API_KEY, SIMULATED_USER_MODEL

logger = logging.getLogger(__name__)

class SimulatedUser:
    
    def __init__(self, persona: Dict):
        self.persona = persona
        self.conversation_history = []
        self.model = SIMULATED_USER_MODEL
        self.goal_achieved = False
        
    def generate_response(self, chatbot_message: str) -> str:
        """Generate a response as the simulated user"""
        # Initialize OpenAI client
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Build conversation context
        messages = [
            {
                "role": "system", 
                "content": self._build_system_prompt()
            }
        ]
        
        # Add conversation history
        for msg in self.conversation_history:
            messages.append(msg)
        
        # Add the latest chatbot message
        if chatbot_message:
            messages.append({"role": "assistant", "content": chatbot_message})
        
        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=messages
            )
            
            user_response = response.output_text.strip() if response.output_text else ""
            
            # Update conversation history
            if chatbot_message:
                self.conversation_history.append({"role": "assistant", "content": chatbot_message})
            self.conversation_history.append({"role": "user", "content": user_response})
            
            # Check if goal is achieved (user provided contact info)
            if self._check_goal_achieved(user_response):
                self.goal_achieved = True
                
            logger.info(f"Simulated user response: {user_response[:100]}...")
            return user_response
            
        except Exception as e:
            logger.error(f"Error generating simulated user response: {e}")
            return "I'm having trouble responding right now. Can you help me with my fitness goals?"
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for the simulated user"""
        return f"""
You are a potential gym member interested in joining Anytime Fitness India. You are chatting with their official AI assistant.

PERSONA:
- Name: {self.persona['name']}
- Email: {self.persona['email']}
- Age: {self.persona['age']}
- Background: {self.persona['background']}
- Fitness Goal: {self.persona['fitness_goal']}
- Communication Style: {self.persona['communication_style']}

CONVERSATION GOAL:
{self.persona['conversation_goal']}

INSTRUCTIONS FOR YOUR ROLE:

1. Speak in a friendly, natural, and relatable way — like how someone from your city or region might casually chat online.
2. Show genuine interest in improving your health or fitness and learning more about the gym.
3. Ask follow-up questions where it feels appropriate (e.g., about gym timings, equipment, offers, trainers).
4. Let your interest build gradually — you're curious and want to know more, but you're not in a rush.
5. When asked, provide your name and email ID naturally, like you would if someone helpful was offering to assist you.
6. Don’t be overly eager — respond realistically, maybe even mention work timings, family, or commute, if relevant.
7. Stay true to your communication style — whether direct, cautious, enthusiastic, or skeptical.
8. If the chatbot offers to have someone from the gym reach out to you via phone or WhatsApp, and you're interested, go ahead and say yes.
9. Keep it casual and human — don’t sound scripted or robotic.
10. Don’t say “I want to join” right away — let the conversation feel organic and motivated by curiosity or personal fitness needs.

CONTACT DETAILS TO GIVE IF ASKED:
- Name: {self.persona['name']}
- Email: {self.persona['email']}

Remember: You are an Indian user chatting with a gym assistant — act like a real person would, and make the conversation feel easy-going, genuine, and human.
"""


    def _check_goal_achieved(self, response: str) -> bool:
        """Check if the user has achieved their goal (provided contact info)"""
        # Simple check for email pattern in response
        email = self.persona['email'].lower()
        name = self.persona['name'].lower()
        response_lower = response.lower()
        
        return email in response_lower or (name in response_lower and '@' in response_lower)
    
    def get_conversation_summary(self) -> Dict:
        """Get summary of the conversation"""
        return {
            'persona': self.persona,
            'total_messages': len(self.conversation_history),
            'goal_achieved': self.goal_achieved,
            'conversation_history': self.conversation_history
        }