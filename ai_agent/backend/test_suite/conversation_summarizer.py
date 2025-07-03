"""
Conversation Summarizer for Test Suite
Generates AI-powered summaries of test conversations using OpenAI's Responses API
"""

import time
import logging
from typing import List, Dict, Optional, Tuple
from openai import OpenAI
from .test_models import TestMessage, TestRun, TestConversationSummary
from .test_database import TestDatabase
from .config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

class ConversationSummarizer:
    """
    Generates concise summaries of test conversations using GPT-4.1-nano
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = "gpt-4.1-nano"
        self.test_db = TestDatabase()
        
    def generate_summary(self, test_run_id: int) -> Optional[str]:
        """
        Generate summary for a completed test run
        
        Args:
            test_run_id: ID of the test run to summarize
            
        Returns:
            Generated summary text or None if failed
        """
        try:
            logger.info(f"Starting summary generation for test run {test_run_id}")
            
            # Get test run details and messages
            test_run_data = self.test_db.get_test_run_results(test_run_id)
            if not test_run_data:
                logger.error(f"Test run {test_run_id} not found")
                return None
            
            test_run = test_run_data['test_run']
            messages = test_run_data['messages']
            
            if not messages:
                logger.warning(f"No messages found for test run {test_run_id}")
                return None
                
            logger.info(f"Found {len(messages)} messages for test run {test_run_id}")
                
            # Build conversation context
            conversation_context = self._build_conversation_context(messages, test_run)
            
            # Create summary prompt
            prompt = self._create_summary_prompt(conversation_context, test_run['scenario_name'])
            
            # Generate summary using OpenAI Responses API
            logger.info(f"Calling OpenAI API for test run {test_run_id}")
            start_time = time.time()
            summary_data = self._call_responses_api(prompt)
            generation_time_ms = int((time.time() - start_time) * 1000)
            
            if summary_data:
                summary = summary_data['summary']
                tokens_used = summary_data.get('tokens_used', 0)
                logger.info(f"API call successful, got summary: {summary[:100]}...")
                
                # Save summary to database
                logger.info(f"Saving summary to database for test run {test_run_id}")
                self._save_summary(
                    test_run_id, 
                    test_run['scenario_name'], 
                    summary, 
                    tokens_used, 
                    generation_time_ms
                )
                
                logger.info(f"Successfully generated and saved summary for test run {test_run_id}")
                return summary
            else:
                logger.error(f"Failed to get summary data from API for test run {test_run_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating summary for test run {test_run_id}: {e}")
            return None
    
    def _build_conversation_context(self, messages: List[Dict], test_run: Dict) -> str:
        """
        Build formatted conversation context for the AI
        
        Args:
            messages: List of conversation messages
            test_run: Test run metadata
            
        Returns:
            Formatted conversation context string
        """
        context_parts = [
            f"Test Scenario: {test_run['scenario_name']}",
            f"Total Messages: {len(messages)}",
            f"Duration: {test_run['conversation_duration_seconds']} seconds",
            f"Lead Generated: {'Yes' if test_run['lead_generated'] else 'No'}",
            f"Success: {'Yes' if test_run['success'] else 'No'}",
            "",
            "Conversation Flow:"
        ]
        
        for msg in messages:
            role = "User" if msg['role'] == 'user' else "AI Agent"
            content = msg['content']
            
            # Truncate very long messages
            if len(content) > 300:
                content = content[:297] + "..."
            
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def _create_summary_prompt(self, conversation_context: str, _conversation_type: str) -> str:
        """
        Create the prompt for GPT-4.1-nano to generate summary
        
        Args:
            conversation_context: Formatted conversation context
            conversation_type: Type of conversation (scenario name)
            
        Returns:
            Prompt string for the AI
        """
        prompt = """
Analyze this conversation between a simulated user and the Anytime Fitness AI receptionist. Create a concise summary that captures the essence of what happened.

Focus on:
- What the user was trying to accomplish or learn about
- The overall vibe and flow of the conversation
- How well the AI handled the user's needs
- Whether lead generation was successful (contact info collected)
- Key outcomes or next steps

Keep the summary to 2-3 sentences maximum. Make it glanceable and informative - capture the "story" of this conversation rather than a detailed transcript.

{conversation_context}

Summary:
"""
        
        return prompt.format(conversation_context=conversation_context)
    
    def _call_responses_api(self, prompt: str) -> Optional[Dict]:
        """
        Make API call using OpenAI Responses API
        
        Args:
            prompt: The prompt to send to the API
            
        Returns:
            Dictionary with summary and metadata, or None if failed
        """
        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt
            )
            
            if response.output_text:
                summary = response.output_text.strip()
                
                # Extract token usage if available
                tokens_used = 0
                if hasattr(response, 'usage') and response.usage:
                    tokens_used = response.usage.total_tokens
                
                return {
                    'summary': summary,
                    'tokens_used': tokens_used
                }
            else:
                logger.error("No output received from OpenAI Responses API")
                return None
                
        except Exception as e:
            logger.error(f"Error calling OpenAI Responses API: {e}")
            return None
    
    def _save_summary(self, test_run_id: int, conversation_type: str, summary: str, 
                     tokens_used: int, generation_time_ms: int):
        """
        Save summary to database
        
        Args:
            test_run_id: ID of the test run
            conversation_type: Type of conversation
            summary: Generated summary text
            tokens_used: Number of tokens used
            generation_time_ms: Time taken to generate summary
        """
        try:
            self.test_db.create_conversation_summary(
                test_run_id=test_run_id,
                conversation_type=conversation_type,
                summary=summary,
                tokens_used=tokens_used,
                generation_time_ms=generation_time_ms
            )
            logger.info(f"Saved summary for test run {test_run_id}")
        except Exception as e:
            logger.error(f"Error saving summary for test run {test_run_id}: {e}")
            raise
    
    def generate_summaries_for_runs_without_summaries(self, limit: int = 10) -> Tuple[int, int]:
        """
        Generate summaries for test runs that don't have summaries yet
        
        Args:
            limit: Maximum number of summaries to generate in this batch
            
        Returns:
            Tuple of (successful_summaries, failed_summaries)
        """
        successful = 0
        failed = 0
        
        try:
            # Get test runs without summaries
            runs_without_summaries = self.test_db.get_test_runs_without_summaries(limit)
            
            for run_id in runs_without_summaries:
                try:
                    summary = self.generate_summary(run_id)
                    if summary:
                        successful += 1
                    else:
                        failed += 1
                except Exception as e:
                    logger.error(f"Failed to generate summary for run {run_id}: {e}")
                    failed += 1
                    
            logger.info(f"Batch summary generation: {successful} successful, {failed} failed")
            return successful, failed
            
        except Exception as e:
            logger.error(f"Error in batch summary generation: {e}")
            return successful, failed