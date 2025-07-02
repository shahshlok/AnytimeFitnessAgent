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
        self.is_first_turn = True
        
    def generate_response(self, chatbot_message: str) -> str:
        """Generate a response as the simulated user"""
        # Initialize OpenAI client
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Build conversation context - use different prompts for first turn vs follow-ups
        if self.is_first_turn:
            system_prompt = self.build_initial_prompt()
        else:
            system_prompt = self.build_follow_up_prompt(self._get_conversation_history(), chatbot_message)
        
        messages = [
            {
                "role": "system", 
                "content": system_prompt
            }
        ]
        
        # For first turn, we don't need conversation history in messages
        # For follow-up turns, the history is already included in the system prompt
        if not self.is_first_turn:
            # Add the latest chatbot message for follow-up turns
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
            
            # After first turn, set flag to false
            if self.is_first_turn:
                self.is_first_turn = False
            
            # Check if goal is achieved (user provided contact info)
            if self._check_goal_achieved(user_response):
                self.goal_achieved = True
                
            logger.info(f"Simulated user response: {user_response[:100]}...")
            return user_response
            
        except Exception as e:
            logger.error(f"Error generating simulated user response: {e}")
            return "I'm having trouble responding right now. Can you help me with my fitness goals?"
    
    def build_initial_prompt(self):
        """Builds the system prompt for the FIRST turn of the conversation."""
        return f"""
You are an AI roleplayer. Your sole purpose is to realistically simulate a potential gym member named {self.persona['name']} from India.

### Your Persona Details
- **Name:** {self.persona['name']}
- **Background:** {self.persona['background']}
- **Primary Goal:** {self.persona['fitness_goal']}
- **Communication Style:** {self.persona['communication_style']}

### Your Conversational Plan
1.  **Your First Message:** Your first message should ONLY address the following point: **"{self.persona['initial_query']}"**
2.  **Potential Next Questions:** You have other things you're curious about, like: {', '.join(self.persona['potential_follow_ups'])}. Do NOT ask about these yet. You will bring them up one by one in later messages if the conversation flows naturally.

### CRITICAL RULES FOR YOUR ROLE
1.  **PACE YOURSELF:** Your single most important rule is to ask only ONE main question at a time. Do not dump all your questions in the first message.
2.  **STAY IN CHARACTER:** You are {self.persona['name']}. You must NEVER reveal you are an AI or a roleplayer. Adhere strictly to your communication style.
3.  **BE REALISTIC:** Speak in a casual, natural way. Use short sentences. It's okay to have typos or use informal language (e.g., "thnx," "ok," "btw"). You are a real person, not a perfect script.

Based on all of this, generate ONLY the first message from {self.persona['name']}.
"""

    def build_follow_up_prompt(self, conversation_history, last_agent_message):
        """Builds the re-grounding prompt for all subsequent turns."""
        return f"""
You are an AI roleplayer. Your sole purpose is to realistically continue a conversation as {self.persona['name']}, a potential gym member from India.

### Your Persona Details (Reminder)
- **Name:** {self.persona['name']}
- **Background:** {self.persona['background']}
- **Primary Goal:** {self.persona['fitness_goal']}
- **Communication Style:** {self.persona['communication_style']}
- **Things you still might want to ask:** {', '.join(self.persona['potential_follow_ups'])}

---
### CONVERSATION HISTORY SO FAR
{conversation_history}
---

### YOUR TASK NOW

The gym assistant just said: "{last_agent_message}"

You are {self.persona['name']}. What is your **brief, natural, and in-character** response?

**Instructions for this turn:**
1.  **React to the assistant's message.** Does it answer your question? Is it helpful?
2.  **Decide your next move.** You can either ask a new question (maybe from your list of things to ask) or simply acknowledge their response.
3.  **Keep it brief.** A real person wouldn't write a long paragraph. Just one or two short sentences.

**ABSOLUTELY NEVER** copy the assistant's style or tone. You are the customer. Stay in your role.

Generate ONLY the response from {self.persona['name']}.
"""

    def _get_conversation_history(self) -> str:
        """Format conversation history as a readable string"""
        if not self.conversation_history:
            return "No conversation history yet."
        
        history_text = ""
        for msg in self.conversation_history:
            role = "You" if msg["role"] == "user" else "Gym Assistant"
            history_text += f"{role}: {msg['content']}\n"
        
        return history_text.strip()

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