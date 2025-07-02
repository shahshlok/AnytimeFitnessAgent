"""
Conversation runner for testing between simulated user and Anytime Fitness chatbot
"""
import requests
import json
import time
import uuid
import logging
from typing import Dict, List, Tuple, Optional
from .config import API_BASE_URL, MAX_CONVERSATION_MESSAGES, MESSAGE_DELAY_SECONDS
from .simulated_user import SimulatedUser

logger = logging.getLogger(__name__)

class ConversationRunner:
    def __init__(self):
        self.api_base_url = API_BASE_URL
        self.session_id = str(uuid.uuid4())
        self.conversation_history = []
        
    def run_conversation(self, persona: Dict) -> Dict:
        """Run a complete conversation between simulated user and chatbot"""
        logger.info(f"Starting conversation for persona: {persona['name']}")
        
        # Initialize simulated user
        simulated_user = SimulatedUser(persona)
        
        # Start conversation with user's opening message
        user_message = simulated_user.generate_response("")
        
        conversation_log = []
        message_count = 0
        start_time = time.time()
        lead_generated = False
        lead_data = None
        
        while message_count < MAX_CONVERSATION_MESSAGES:
            message_count += 1
            
            # Send user message to chatbot
            logger.info(f"Message {message_count}: User -> Chatbot")
            chatbot_response, tool_calls = self._send_message_to_chatbot(user_message)
            
            if not chatbot_response:
                logger.error("Failed to get response from chatbot")
                break
                
            # Log the exchange
            conversation_log.append({
                'message_order': message_count * 2 - 1,
                'role': 'user',
                'content': user_message,
                'timestamp': time.time()
            })
            
            conversation_log.append({
                'message_order': message_count * 2,
                'role': 'assistant', 
                'content': chatbot_response,
                'timestamp': time.time(),
                'tool_calls': tool_calls
            })
            
            # Check for lead generation
            if tool_calls:
                for tool_call in tool_calls:
                    if tool_call.get('tool') == 'create_lead':
                        lead_generated = True
                        lead_data = tool_call.get('arguments', {})
                        logger.info(f"Lead generated: {lead_data}")
            
            # If lead was generated, conversation goal achieved
            if lead_generated:
                logger.info("Lead generation detected - conversation completed successfully")
                break
                
            # Generate next user response
            user_message = simulated_user.generate_response(chatbot_response)
            
            # If simulated user achieved goal, break
            if simulated_user.goal_achieved:
                logger.info("Simulated user goal achieved")
                break
                
            # Add delay to simulate human response time
            time.sleep(MESSAGE_DELAY_SECONDS)
        
        end_time = time.time()
        conversation_duration = int(end_time - start_time)
        
        # Build result summary
        result = {
            'success': lead_generated,
            'lead_generated': lead_generated,
            'lead_data': lead_data,
            'total_messages': len(conversation_log),
            'conversation_duration_seconds': conversation_duration,
            'conversation_log': conversation_log,
            'persona': persona,
            'session_id': self.session_id,
            'simulated_user_summary': simulated_user.get_conversation_summary()
        }
        
        logger.info(f"Conversation completed. Success: {lead_generated}, Messages: {len(conversation_log)}")
        return result
    
    def _send_message_to_chatbot(self, message: str) -> Tuple[Optional[str], List[Dict]]:
        """Send message to chatbot and return response with tool calls"""
        try:
            payload = {
                'message': message,
                'history': self.conversation_history,
                'session_id': self.session_id,
                'input_type': 'text'
            }
            
            response = requests.post(
                f"{self.api_base_url}/chat",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                chatbot_reply = data.get('reply', '')
                
                # Update conversation history
                self.conversation_history.append({'role': 'user', 'content': message})
                self.conversation_history.append({'role': 'assistant', 'content': chatbot_reply})
                
                # Extract tool calls from response (if any)
                tool_calls = self._extract_tool_calls_from_response(data)
                
                return chatbot_reply, tool_calls
            else:
                logger.error(f"Chatbot API error: {response.status_code} - {response.text}")
                return None, []
                
        except Exception as e:
            logger.error(f"Error sending message to chatbot: {e}")
            return None, []
    
    def _extract_tool_calls_from_response(self, response_data: Dict) -> List[Dict]:
        """Extract tool calls from chatbot response"""
        # Note: This is a simplified extraction - in practice, you might need to 
        # check the backend logs or response metadata for actual tool call information
        tool_calls = []
        
        # For now, we'll detect lead generation by checking if the response mentions
        # passing details to the team (indicating successful lead creation)
        reply = response_data.get('reply', '').lower()
        
        # Simple heuristic to detect lead generation
        lead_indicators = [
            'passed your details',
            'someone will be in touch',
            'team will reach out',
            'someone will contact you',
            'we\'ll be in touch'
        ]
        
        if any(indicator in reply for indicator in lead_indicators):
            # This is a simplified detection - in production you'd want to check
            # the actual backend logs or response metadata
            tool_calls.append({
                'tool': 'create_lead',
                'arguments': {
                    'detected_via': 'response_heuristic',
                    'response_content': reply[:200]
                }
            })
        
        return tool_calls