"""
Main CLI for Anytime Fitness AI Chatbot Test Suite
"""
import argparse
import logging
import sys
import time
from datetime import datetime

from .config import TEST_SCENARIOS
from .test_scenarios import get_scenario_persona, get_all_scenarios, validate_scenario
from .conversation_runner import ConversationRunner
from .test_database import TestDatabase
from .conversation_summarizer import ConversationSummarizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/af_test_suite.log')
    ]
)
logger = logging.getLogger(__name__)

class TestSuite:
    def __init__(self):
        self.db = TestDatabase()
        self.summarizer = ConversationSummarizer()
        
    def run_scenario(self, scenario_name: str) -> dict:
        """Run a single test scenario"""
        logger.info(f"Running test scenario: {scenario_name}")
        
        if not validate_scenario(scenario_name):
            raise ValueError(f"Invalid scenario: {scenario_name}")
        
        try:
            # Get persona for scenario
            persona = get_scenario_persona(scenario_name)
            
            # Create test run record
            test_metadata = {
                'scenario_name': scenario_name,
                'persona': persona,
                'start_time': datetime.now().isoformat()
            }
            
            test_run_id = self.db.create_test_run(scenario_name, test_metadata)
            
            # Run conversation
            runner = ConversationRunner()
            result = runner.run_conversation(persona)
            
            # Store conversation messages
            for msg in result['conversation_log']:
                self.db.add_test_message(
                    test_run_id=test_run_id,
                    message_order=msg['message_order'],
                    role=msg['role'],
                    content=msg['content'],
                    extra_data={'timestamp': msg['timestamp'], 'tool_calls': msg.get('tool_calls', [])}
                )
            
            # Store lead data if generated
            if result['lead_generated']:
                # Extract lead data from conversation log
                lead_data = None
                for msg in result['conversation_log']:
                    if msg.get('is_lead_generated'):
                        lead_data = {
                            'name': persona['name'],
                            'email': persona['email'],
                            'summary': f"Lead generated during test for {persona['name']}"
                        }
                        break
                
                if lead_data:
                    self.db.add_test_lead(
                        test_run_id=test_run_id,
                        name=lead_data['name'],
                        email=lead_data['email'],
                        summary=lead_data['summary'],
                        hubspot_status='test_generated'
                    )
            
            # Update test run with results
            self.db.update_test_run_result(
                test_run_id=test_run_id,
                success=result['lead_generated'],  # Use lead_generated as success indicator
                lead_generated=result['lead_generated'],
                total_messages=result['total_messages'],
                conversation_duration=result['conversation_duration_seconds']
            )
            
            # Generate conversation summary for all completed conversations (successful or not)
            try:
                summary = self.summarizer.generate_summary(test_run_id)
                if summary:
                    logger.info(f"Generated summary for test run {test_run_id}")
                    result['summary'] = summary
                else:
                    logger.warning(f"Failed to generate summary for test run {test_run_id}")
            except Exception as e:
                logger.error(f"Summary generation failed for test run {test_run_id}: {e}")
            
            # Add test run ID to result
            result['test_run_id'] = test_run_id
            
            logger.info(f"Test scenario {scenario_name} completed. Test run ID: {test_run_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error running scenario {scenario_name}: {e}")
            raise
    
    def run_all_scenarios(self) -> dict:
        """Run all test scenarios"""
        logger.info("Running all test scenarios")
        
        results = {}
        total_success = 0
        total_runs = 0
        
        for scenario_name in TEST_SCENARIOS.keys():
            try:
                result = self.run_scenario(scenario_name)
                results[scenario_name] = result
                
                if result['lead_generated']:
                    total_success += 1
                total_runs += 1
                    
                logger.info(f"Scenario {scenario_name}: {'SUCCESS' if result['lead_generated'] else 'FAILED'}")
                
                # Add delay between scenarios
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to run scenario {scenario_name}: {e}")
                results[scenario_name] = {'error': str(e), 'success': False}
                total_runs += 1
        
        summary = {
            'total_scenarios': total_runs,
            'successful_scenarios': total_success,
            'success_rate': (total_success / total_runs * 100) if total_runs > 0 else 0,
            'results': results
        }
        
        logger.info(f"All scenarios completed. Success rate: {summary['success_rate']:.1f}%")
        return summary
    
    def show_recent_results(self, limit: int = 10):
        """Show recent test results"""
        try:
            recent_runs = self.db.get_recent_test_runs(limit)
            
            print(f"\n=== Recent Test Results (Last {limit}) ===")
            print(f"{'ID':<5} {'Scenario':<25} {'Success':<8} {'Lead Gen':<9} {'Messages':<9} {'Duration':<10} {'Timestamp'}")
            print("-" * 80)
            
            for run in recent_runs:
                timestamp = run['timestamp'].strftime('%m/%d %H:%M') if run['timestamp'] else 'N/A'
                success_icon = '✓' if run['success'] else '✗'
                lead_icon = '✓' if run['lead_generated'] else '✗'
                
                print(f"{run['id']:<5} {run['scenario_name']:<25} {success_icon:<8} {lead_icon:<9} "
                      f"{run['total_messages']:<9} {run['conversation_duration_seconds']:<10} {timestamp}")
                      
        except Exception as e:
            print(f"Error retrieving recent results: {e}")
    
    def generate_summaries_batch(self, limit: int = 10):
        """Generate summaries for test runs that don't have summaries yet"""
        try:
            print(f"\n=== Generating Summaries (Batch of {limit}) ===")
            successful, failed = self.summarizer.generate_summaries_for_runs_without_summaries(limit)
            
            print(f"Summary generation completed:")
            print(f"  Successful: {successful}")
            print(f"  Failed: {failed}")
            
            if successful > 0:
                print(f"✓ Generated {successful} new summaries")
            if failed > 0:
                print(f"✗ Failed to generate {failed} summaries")
                
        except Exception as e:
            print(f"Error generating summaries: {e}")
    
    def show_recent_summaries(self, limit: int = 10):
        """Show recent conversation summaries"""
        try:
            recent_summaries = self.db.get_recent_summaries(limit)
            
            if not recent_summaries:
                print(f"\nNo summaries found.")
                return
            
            print(f"\n=== Recent Conversation Summaries (Last {limit}) ===")
            
            for summary in recent_summaries:
                test_run = summary['test_run']
                print(f"\n📊 Test Run #{summary['test_run_id']} - {summary['conversation_type']}")
                print(f"   Timestamp: {summary['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Success: {'✓' if test_run['success'] else '✗'} | Lead: {'✓' if test_run['lead_generated'] else '✗'}")
                print(f"   Messages: {test_run['total_messages']} | Duration: {test_run['conversation_duration_seconds']}s")
                print(f"   Model: {summary['model_used']} | Tokens: {summary['tokens_used']} | Time: {summary['generation_time_ms']}ms")
                print(f"   Summary: {summary['summary']}")
                print("-" * 80)
                      
        except Exception as e:
            print(f"Error retrieving recent summaries: {e}")
    
    def show_summaries_by_type(self, conversation_type: str):
        """Show summaries for a specific conversation type"""
        try:
            summaries = self.db.get_summaries_by_type(conversation_type)
            
            if not summaries:
                print(f"\nNo summaries found for conversation type: {conversation_type}")
                return
            
            print(f"\n=== Summaries for {conversation_type} ===")
            
            for summary in summaries:
                test_run = summary['test_run']
                print(f"\n📊 Test Run #{summary['test_run_id']}")
                print(f"   Timestamp: {summary['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Success: {'✓' if test_run['success'] else '✗'} | Lead: {'✓' if test_run['lead_generated'] else '✗'}")
                print(f"   Summary: {summary['summary']}")
                print("-" * 60)
                      
        except Exception as e:
            print(f"Error retrieving summaries by type: {e}")

def main():
    parser = argparse.ArgumentParser(description='Anytime Fitness AI Chatbot Test Suite')
    parser.add_argument('--scenario', '-s', 
                       choices=list(TEST_SCENARIOS.keys()) + ['all'],
                       help='Test scenario to run (or "all" for all scenarios)')
    parser.add_argument('--list-scenarios', '-l', action='store_true',
                       help='List available test scenarios')
    parser.add_argument('--recent-results', '-r', type=int, default=10,
                       help='Show recent test results (default: 10)')
    parser.add_argument('--setup-db', action='store_true',
                       help='Setup the test database')
    parser.add_argument('--generate-summaries', action='store_true',
                       help='Generate summaries for test runs without summaries')
    parser.add_argument('--view-summaries', action='store_true',
                       help='View recent conversation summaries')
    parser.add_argument('--summaries-by-type', type=str,
                       help='View summaries for a specific conversation type')
    parser.add_argument('--limit', type=int, default=10,
                       help='Limit for summary queries (default: 10)')
    
    args = parser.parse_args()
    
    # Handle setup database
    if args.setup_db:
        from .setup_test_db import main as setup_main
        setup_main()
        return
    
    # Initialize test suite (needed for summary operations)
    test_suite = TestSuite()
    
    # Handle summary generation
    if args.generate_summaries:
        test_suite.generate_summaries_batch(args.limit)
        return
    
    # Handle viewing summaries
    if args.view_summaries:
        test_suite.show_recent_summaries(args.limit)
        return
    
    # Handle summaries by type
    if args.summaries_by_type:
        test_suite.show_summaries_by_type(args.summaries_by_type)
        return
    
    # Handle list scenarios  
    if args.list_scenarios:
        scenarios = get_all_scenarios()
        print("\n=== Available Test Scenarios ===")
        for name, persona in scenarios.items():
            print(f"{name:25} - {persona['scenario_description']}")
        return
    
    # Handle recent results
    if not args.scenario:
        test_suite.show_recent_results(args.recent_results)
        return
    
    # Run scenarios
    try:
        if args.scenario == 'all':
            results = test_suite.run_all_scenarios()
            print(f"\n=== Test Suite Summary ===")
            print(f"Total Scenarios: {results['total_scenarios']}")
            print(f"Successful: {results['successful_scenarios']}")
            print(f"Success Rate: {results['success_rate']:.1f}%")
        else:
            result = test_suite.run_scenario(args.scenario)
            print(f"\n=== Test Result: {args.scenario} ===")
            print(f"Success: {'✓' if result['lead_generated'] else '✗'}")
            print(f"Lead Generated: {'✓' if result['lead_generated'] else '✗'}")
            print(f"Total Messages: {result['total_messages']}")
            print(f"Duration: {result['conversation_duration_seconds']}s")
            print(f"Test Run ID: {result['test_run_id']}")
            if 'summary' in result:
                print(f"Summary: {result['summary']}")
            
    except Exception as e:
        logger.error(f"Test suite error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()