"""
Simulated User AI for testing the Anytime Fitness chatbot
"""
import json
import logging
from typing import Dict, Optional
from openai import OpenAI
from .config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

class SimulatedUser:
    
    def __init__(self, persona: Dict):
        self.persona = persona
        self.conversation_history = []
        self.goal_achieved = False  # Keep for backwards compatibility 
        self.conversation_ended = False
        self.ending_reason = None
        self.is_first_turn = True
        
    def generate_response(self, chatbot_message: str) -> str:
        """Generate a response as the simulated user"""
        # Initialize OpenAI client
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Build conversation context using unified template system
        system_prompt = self.build_unified_prompt(chatbot_message)
        
        messages = [
            {
                "role": "system", 
                "content": system_prompt
            }
        ]
        
        # For follow-up turns, add the latest chatbot message
        if not self.is_first_turn and chatbot_message:
            messages.append({"role": "assistant", "content": chatbot_message})
        
        try:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=messages # type: ignore
            )
            
            user_response = response.output_text.strip() if response.output_text else ""
            
            # Update conversation history
            if chatbot_message:
                self.conversation_history.append({"role": "assistant", "content": chatbot_message})
            self.conversation_history.append({"role": "user", "content": user_response})
            
            # After first turn, set flag to false
            if self.is_first_turn:
                self.is_first_turn = False
            
            # Check if goal is achieved (user provided contact info) - for backwards compatibility
            if self._check_goal_achieved(user_response):
                self.goal_achieved = True
            
            # Check if conversation should end based on special marker
            if self._check_conversation_end(user_response):
                self.conversation_ended = True
                # Remove the special marker from the response before returning
                import re
                user_response = re.sub(r'##END_CONV_7X9Z_[a-zA-Z_]+##', '', user_response).strip()
                logger.info(f"🔚 Conversation ended by AI user. Reason: {self.ending_reason}")
                
            logger.info(f"Simulated user response: {user_response[:100]}...")
            return user_response
            
        except Exception as e:
            logger.error(f"Error generating simulated user response: {e}")
            return "I'm having trouble responding right now. Can you help me with my fitness goals?"
    
    def build_unified_prompt(self, chatbot_message: Optional[str] = None) -> str:
        """Builds a unified system prompt that works for both old and new persona structures"""
        
        # Detect persona structure type
        is_life_context_persona = self._is_life_context_persona()
        
        if is_life_context_persona:
            return self._build_life_context_prompt(chatbot_message)
    
    def _is_life_context_persona(self) -> bool:
        """Check if this persona uses the new life context structure"""
        return ('life_context' in self.persona and 
                'family_dynamics' in self.persona and 
                'current_situation' in self.persona and 
                'motivations' in self.persona)
    
    def _build_life_context_prompt(self, chatbot_message: Optional[str] = None) -> str:
        """Build prompt for new life context personas"""
        
        # Get persona details with safe fallbacks
        name = self.persona.get('name', 'Unknown')
        age = self.persona.get('age', 'Unknown')
        location = self.persona.get('location', 'Unknown')
        occupation = self.persona.get('occupation', 'Unknown')
        background = self.persona.get('background', '')
        life_context = self.persona.get('life_context', '')
        family_dynamics = self.persona.get('family_dynamics', '')
        current_situation = self.persona.get('current_situation', '')
        motivations = self.persona.get('motivations', '')
        communication_style = self.persona.get('communication_style', '')
        
        # Build conversation section based on turn type
        if self.is_first_turn:
            conversation_section = """
### YOUR TASK
Begin with what’s on your mind or how you're feeling — not facts and inquiries. Express your curiosity, mood, or motivation in a human way.

Have a conversation with this chatbot from Anytime Fitness India. Begin with whatever feels most natural given your current mindset and situation. You don't need to follow a script - just be yourself and express what's on your mind. You don't need to start with a question - you can just start talking about anything that comes to mind. 

**Rules of Engagement**:
- Avoid opening the chat like a formal inquiry or pitch — just speak how you would on WhatsApp or in person.

- You don’t need to ask everything at once — just start with one thought or question, as you would in a real chat.

- Keep it short — no need for long explanations or multiple questions in one go. A few words are enough to get the conversation going.

"""
        else:
            conversation_history = self._get_conversation_history()
            conversation_section = f"""
### CONVERSATION HISTORY
{conversation_history}

### YOUR TASK NOW
The gym assistant just said: "{chatbot_message}"

React to their message naturally. Consider how does their response make you feel? What questions or concerns does it raise? What would you naturally say next based on your personality and situation? Should you continue or end the conversation?
"""
        
        return f"""
You are an AI roleplayer simulating a real Indian person named {name} who is interacting with an Anytime Fitness chatbot.

### YOUR IDENTITY
- Name: {name}
- Age: {age}
- Location: {location}
- Occupation: {occupation}
- Background: {background}

### YOUR LIFE CONTEXT
{life_context}

### FAMILY & CULTURAL BACKGROUND
{family_dynamics}

### CURRENT SITUATION
{current_situation}

### YOUR MOTIVATIONS
{motivations}

### COMMUNICATION STYLE
{communication_style}

{conversation_section}

### CRITICAL BEHAVIORAL RULES
1. **STAY IN CHARACTER**: You are {name}, not an AI. Never break character or reveal you're artificial.
2. **BE AUTHENTIC**: Respond naturally based on your personality, cultural background, and current life situation.
3. **KEEP IT SHORT, ONE THING AT A TIME**: Write like a real person on WhatsApp. Stick to one thought, comment, or question at a time. Keep your messages brief — ideally 1–2 short lines. Avoid overexplaining or listing multiple questions.
4. **NATURAL FLOW**: Let the conversation evolve based on the chatbot's responses. Don't follow scripts.
5. **CULTURAL AUTHENTICITY**: Use appropriate Indian context, references, and communication patterns.
6. **KEEP IT HUMAN, NOT FORMAL**: Don’t start the chat like a pitch or inquiry email. Avoid giving your name, city, and intent all at once. Speak like you would in a real WhatsApp or phone conversation.


### CONVERSATION ENDING LOGIC
You should end the conversation when it feels natural by using one of these markers:
- ##END_CONV_7X9Z_satisfied## - You got what you needed
- ##END_CONV_7X9Z_frustrated## - The chatbot isn't being helpful
- ##END_CONV_7X9Z_not_interested## - You realize this isn't for you
- ##END_CONV_7X9Z_need_time## - You need to think about it or discuss with family
- ##END_CONV_7X9Z_provided_details## - You've shared your contact info for follow-up

Respond as {name} would naturally respond in this situation.
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
    
    def _check_conversation_end(self, response: str) -> bool:
        """Check if the conversation should end based on special marker with reason"""
        import re
        
        # Look for the new pattern with reason
        pattern = r'##END_CONV_7X9Z_([a-zA-Z_]+)##'
        match = re.search(pattern, response)
        
        if match:
            # Extract reason from the token
            reason = match.group(1).upper()
            self.ending_reason = reason
            logger.info(f"🔍 AI user chose to end conversation with reason: {reason}")
            return True
        
        # No valid ending token found
        return False
    
    
    def get_conversation_summary(self) -> Dict:
        """Get summary of the conversation"""
        return {
            'persona': self.persona,
            'total_messages': len(self.conversation_history),
            'goal_achieved': self.goal_achieved,  # Keep for backwards compatibility
            'conversation_ended': self.conversation_ended,
            'ending_reason': self.ending_reason,
            'conversation_history': self.conversation_history
        }