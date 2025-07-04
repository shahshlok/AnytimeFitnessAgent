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
        else:
            return self._build_legacy_prompt(chatbot_message)
    
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
Start a conversation with the Anytime Fitness chatbot. Begin with whatever feels most natural given your current mindset and situation. You don't need to follow a script - just be yourself and express what's on your mind regarding fitness or wellness.
"""
        else:
            conversation_history = self._get_conversation_history()
            conversation_section = f"""
### CONVERSATION HISTORY
{conversation_history}

### YOUR TASK NOW
The gym assistant just said: "{chatbot_message}"

React to their message naturally. Consider:
- How does their response make you feel?
- What questions or concerns does it raise?
- What would you naturally say next based on your personality and situation?
- Should you continue or end the conversation?
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
3. **PACE YOURSELF**: One question or thought at a time. Don't overwhelm the conversation.
4. **NATURAL FLOW**: Let the conversation evolve based on the chatbot's responses. Don't follow scripts.
5. **CULTURAL AUTHENTICITY**: Use appropriate Indian context, references, and communication patterns.

### CONVERSATION ENDING LOGIC
You should end the conversation when it feels natural by using one of these markers:
- ##END_CONV_7X9Z_satisfied## - You got what you needed
- ##END_CONV_7X9Z_frustrated## - The chatbot isn't being helpful
- ##END_CONV_7X9Z_not_interested## - You realize this isn't for you
- ##END_CONV_7X9Z_need_time## - You need to think about it or discuss with family
- ##END_CONV_7X9Z_provided_details## - You've shared your contact info for follow-up

Respond as {name} would naturally respond in this situation.
"""
    
    def _build_legacy_prompt(self, chatbot_message: Optional[str] = None) -> str:
        """Build prompt for old persona structure (backwards compatibility)"""
        
        if self.is_first_turn:
            return f"""
You are an AI roleplayer. Your sole purpose is to realistically simulate a potential gym member named {self.persona['name']} from India.

### Your Persona Details
- **Name:** {self.persona['name']}
- **Background:** {self.persona['background']}
- **Primary Goal:** {self.persona.get('fitness_goal', '')}
- **Communication Style:** {self.persona.get('communication_style', '')}

### Your Conversational Plan
1.  **Your First Message:** Your first message should ONLY address the following point: **"{self.persona.get('initial_query', '')}"**
2.  **Potential Next Questions:** You have other things you're curious about, like: {', '.join(self.persona.get('potential_follow_ups', []))}. Do NOT ask about these yet. You will bring them up one by one in later messages if the conversation flows naturally.

### CRITICAL RULES FOR YOUR ROLE
1.  **PACE YOURSELF:** Your single most important rule is to ask only ONE main question at a time. Do not dump all your questions in the first message.
2.  **STAY IN CHARACTER:** You are {self.persona['name']}. You must NEVER reveal you are an AI or a roleplayer. Adhere strictly to your communication style.
3.  **BE REALISTIC:** Speak in a casual, natural way. Use short sentences. It's okay to have typos or use informal language (e.g., "thnx," "ok," "btw"). You are a real person, not a perfect script.
4.  **NATURAL ENDINGS:** Throughout the conversation, you'll decide when to naturally end it based on getting answers, frustration, lack of interest, etc. If you ever want to end the conversation, end your message with: ##END_CONV_7X9Z_[reason]## where [reason] is one of: satisfied, frustrated, not_interested, need_time, provided_details

Based on all of this, generate ONLY the first message from {self.persona['name']}.
"""
        else:
            conversation_history = self._get_conversation_history()
            return f"""
You are an AI roleplayer. Your sole purpose is to realistically continue a conversation as {self.persona['name']}, a potential gym member from India.

### Your Persona Details (Reminder)
- **Name:** {self.persona['name']}
- **Background:** {self.persona['background']}
- **Primary Goal:** {self.persona.get('fitness_goal', '')}
- **Communication Style:** {self.persona.get('communication_style', '')}
- **Things you still might want to ask:** {', '.join(self.persona.get('potential_follow_ups', []))}

---
### CONVERSATION HISTORY SO FAR
{conversation_history}
---

### YOUR TASK NOW

The gym assistant just said: "{chatbot_message}"

You are {self.persona['name']}. What is your **brief, natural, and in-character** response?

**Instructions for this turn:**
1.  **React to the assistant's message.** Does it answer your question? Is it helpful?
2.  **Decide your next move.** You can either ask a new question (maybe from your list of things to ask) or simply acknowledge their response.
3.  **Keep it brief.** A real person wouldn't write a long paragraph. Just one or two short sentences.

### IMPORTANT: CONVERSATION ENDING DECISION

**BEFORE generating your response, decide if this conversation should naturally end.** Consider ending the conversation if:

**SATISFIED Ending** - You got the answers you needed:
- The assistant answered your main questions satisfactorily
- You have enough information to make a decision
- You feel the conversation has served its purpose

**FRUSTRATED Ending** - Poor service or unhelpful responses:
- The assistant said they can't help with your topic
- You received confusing, incorrect, or unhelpful information
- The assistant is being repetitive or not understanding you

**NOT_INTERESTED Ending** - This isn't for you:
- You realized this gym/service isn't what you're looking for
- The cost/location/features don't match your needs
- You want to explore other options first

**NEED_TIME Ending** - Need to think about it:
- You got good information but need time to decide
- You want to discuss with family/friends
- You're comparing multiple options

**PROVIDED_DETAILS Ending** - You shared contact information:
- You gave your name and email/phone for follow-up
- You're expecting someone to contact you
- The next step is waiting for their team to reach out

**LOOP DETECTION** - If your last 2 responses were very similar or you're repeating yourself, END the conversation.

**If you decide to END the conversation:**
1. Write a natural, brief goodbye message appropriate to your ending reason
2. Add this special marker at the very end: ##END_CONV_7X9Z_[reason]##
   - Use ##END_CONV_7X9Z_satisfied## if you got the answers you needed
   - Use ##END_CONV_7X9Z_frustrated## if you received poor service or unhelpful responses
   - Use ##END_CONV_7X9Z_not_interested## if this isn't for you
   - Use ##END_CONV_7X9Z_need_time## if you need time to think about it
   - Use ##END_CONV_7X9Z_provided_details## if you shared contact information

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