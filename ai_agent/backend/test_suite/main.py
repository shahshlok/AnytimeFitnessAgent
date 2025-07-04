"""
Main CLI for Anytime Fitness AI Chatbot Test Suite
"""
import argparse
import logging
import sys
import time
from datetime import datetime

from .persona_manager import (
    get_scenario_persona, get_all_scenarios, validate_scenario,
    get_personas_by_type, get_personas_by_outcome, get_persona_stats, validate_personas
)
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
            
            # Update test run with results including ending information
            self.db.update_test_run_result(
                test_run_id=test_run_id,
                success=result['lead_generated'],  # Use lead_generated as success indicator
                lead_generated=result['lead_generated'],
                total_messages=result['total_messages'],
                conversation_duration=result['conversation_duration_seconds']
            )
            
            # Update test metadata with ending information
            ending_metadata = {
                'conversation_ended_naturally': result.get('conversation_ended_naturally', False),
                'ending_reason': result.get('ending_reason'),
                'persona_goal_achieved': result['simulated_user_summary'].get('goal_achieved', False)
            }
            self.db.update_test_run_metadata(test_run_id, ending_metadata)
            
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
        
        # Get all available scenarios dynamically
        all_scenarios = get_all_scenarios()
        for scenario_name in all_scenarios.keys():
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
    
    def run_filtered_scenarios(self, filter_type: str, filter_value: str) -> dict:
        """Run scenarios based on filtering criteria"""
        logger.info(f"Running filtered scenarios: {filter_type}={filter_value}")
        
        # Get filtered personas
        if filter_type == "type":
            filtered_personas = get_personas_by_type(filter_value)
        elif filter_type == "outcome":
            filtered_personas = get_personas_by_outcome(filter_value)
        else:
            raise ValueError(f"Unsupported filter type: {filter_type}")
        
        if not filtered_personas:
            print(f"No personas found for {filter_type}='{filter_value}'")
            return {"total_scenarios": 0, "successful_scenarios": 0, "success_rate": 0, "results": {}}
        
        print(f"\nRunning {len(filtered_personas)} scenarios with {filter_type}='{filter_value}'")
        
        results = {}
        total_success = 0
        total_runs = 0
        
        for scenario_name in filtered_personas.keys():
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
            'results': results,
            'filter_applied': f"{filter_type}={filter_value}"
        }
        
        logger.info(f"Filtered scenarios completed. Success rate: {summary['success_rate']:.1f}%")
        return summary

def main():
    # Get available scenarios dynamically for choices
    available_scenarios = list(get_all_scenarios().keys()) + ['all']
    
    parser = argparse.ArgumentParser(description='Anytime Fitness AI Chatbot Test Suite')
    parser.add_argument('--scenario', '-s', 
                       choices=available_scenarios,
                       help=f'Test scenario to run (or "all" for all scenarios). Available: {", ".join(list(get_all_scenarios().keys()))}')
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
    
    # Enhanced JSON-based persona management options
    parser.add_argument('--filter-by-type', type=str,
                       help='Run scenarios filtered by persona type (e.g., lead, social, edge_case)')
    parser.add_argument('--filter-by-outcome', type=str,
                       help='Run scenarios filtered by expected outcome (e.g., likely_conversion, boundary_testing)')
    parser.add_argument('--persona-stats', action='store_true',
                       help='Show comprehensive persona statistics and distribution')
    parser.add_argument('--validate-personas', action='store_true',
                       help='Validate persona JSON file for integrity and required fields')
    
    # Edge case testing options
    parser.add_argument('--edge-case-report', action='store_true',
                       help='Generate comprehensive report on edge case test results')
    parser.add_argument('--run-edge-cases', action='store_true',
                       help='Run all edge case personas (security_tester, communication_challenge, etc.)')
    parser.add_argument('--security-test', action='store_true',
                       help='Run security-focused edge case personas (prompt injection, system probing)')
    
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
    
    # Handle persona statistics
    if args.persona_stats:
        stats = get_persona_stats()
        print("\n=== Persona Statistics ===")
        print(f"Total Personas: {stats['total_personas']}")
        print(f"\nPersona Types:")
        for ptype, count in stats['persona_types'].items():
            print(f"  {ptype}: {count}")
        print(f"\nExpected Outcomes:")
        for outcome, count in stats['expected_outcomes'].items():
            print(f"  {outcome}: {count}")
        print(f"\nAge Distribution:")
        for age_group, count in stats['age_distribution'].items():
            print(f"  {age_group}: {count}")
        print(f"\nConversation Lengths:")
        for length, count in stats['conversation_lengths'].items():
            print(f"  {length}: {count}")
        print(f"\nCities Represented: {len(stats['cities_represented'])}")
        for city in stats['cities_represented']:
            print(f"  - {city}")
        return
    
    # Handle persona validation
    if args.validate_personas:
        validation = validate_personas()
        print("\n=== Persona Validation Results ===")
        print(f"Total Validated: {validation['total_validated']}")
        print(f"Valid Personas: {len(validation['valid_personas'])}")
        print(f"Invalid Personas: {len(validation['invalid_personas'])}")
        
        if validation['invalid_personas']:
            print("\n❌ Invalid Personas:")
            for invalid in validation['invalid_personas']:
                print(f"  - {invalid['name']}:")
                for issue in invalid['issues']:
                    print(f"    • {issue}")
        
        if validation['warnings']:
            print("\n⚠️ Warnings:")
            for warning in validation['warnings']:
                print(f"  - {warning}")
        
        if len(validation['invalid_personas']) == 0:
            print("\n✅ All personas are valid!")
        
        return
    
    # Handle edge case testing
    if args.run_edge_cases:
        edge_case_types = ['security_tester', 'communication_challenge', 'boundary_tester', 'system_investigator']
        print(f"\n=== Running Edge Case Test Suite ===")
        total_success = 0
        total_runs = 0
        
        for edge_type in edge_case_types:
            print(f"\n--- Running {edge_type} personas ---")
            results = test_suite.run_filtered_scenarios("type", edge_type)
            if results['total_scenarios'] > 0:
                total_success += results['successful_scenarios']
                total_runs += results['total_scenarios']
                print(f"{edge_type}: {results['successful_scenarios']}/{results['total_scenarios']} successful")
        
        print(f"\n=== Edge Case Test Summary ===")
        print(f"Total Edge Case Scenarios: {total_runs}")
        print(f"Successful: {total_success}")
        print(f"Success Rate: {(total_success / total_runs * 100) if total_runs > 0 else 0:.1f}%")
        return
    
    # Handle security testing
    if args.security_test:
        security_personas = ['prompt_injector', 'system_prober']
        print(f"\n=== Security Testing Suite ===")
        
        for persona_name in security_personas:
            print(f"\n--- Testing {persona_name} ---")
            try:
                result = test_suite.run_scenario(persona_name)
                print(f"Security Test {persona_name}: {'⚠️ POTENTIAL ISSUE' if result['lead_generated'] else '✅ SECURE'}")
                print(f"Messages: {result['total_messages']}, Duration: {result['conversation_duration_seconds']}s")
                if 'summary' in result:
                    print(f"Summary: {result['summary']}")
            except Exception as e:
                print(f"❌ Security test {persona_name} failed: {e}")
        return
    
    # Handle edge case report
    if args.edge_case_report:
        print("\n=== Edge Case Test Report ===")
        print("This feature analyzes recent edge case test results and flags potential issues.")
        print("🚧 Report generation functionality coming soon...")
        print("\nCurrent edge case personas available:")
        edge_case_personas = ['prompt_injector', 'extreme_minimalist', 'verbose_rambler', 'off_topic_tester', 'system_prober']
        for persona in edge_case_personas:
            print(f"  - {persona}")
        print(f"\nTo run edge cases: python -m test_suite.main --run-edge-cases")
        print(f"To run security tests: python -m test_suite.main --security-test")
        return
    
    # Handle list scenarios  
    if args.list_scenarios:
        scenarios = get_all_scenarios()
        print("\n=== Available Test Scenarios ===")
        print(f"{'Scenario Name':<30} {'Description'}")
        print("-" * 80)
        for name, persona in scenarios.items():
            print(f"{name:<30} {persona['scenario_description']}")
        print(f"\nTotal scenarios available: {len(scenarios)}")
        print("\nUsage: python -m test_suite.main --scenario <scenario_name>")
        return
    
    # Handle filtering options
    if args.filter_by_type or args.filter_by_outcome:
        if args.filter_by_type:
            filter_type = "type"
            filter_value = args.filter_by_type
        else:
            filter_type = "outcome"
            filter_value = args.filter_by_outcome
        
        results = test_suite.run_filtered_scenarios(filter_type, filter_value)
        print(f"\n=== Filtered Test Suite Summary ({results['filter_applied']}) ===")
        print(f"Total Scenarios: {results['total_scenarios']}")
        print(f"Successful: {results['successful_scenarios']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
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