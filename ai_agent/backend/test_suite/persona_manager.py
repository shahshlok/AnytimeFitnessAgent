"""
Persona Manager for JSON-based persona repository
Replaces test_scenarios.py with enhanced JSON-based persona management
"""
import json
import logging
import os
import warnings
from typing import Dict, List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class PersonaManager:
    def __init__(self, json_file_path: Optional[str] = None):
        """Initialize persona manager with JSON file path"""
        if json_file_path is None:
            # Default to persona.json in the same directory
            current_dir = Path(__file__).parent
            json_file_path = current_dir / "persona.json"
        
        self.json_file_path = Path(json_file_path)
        self._personas_cache = None
        self._metadata_cache = None
        self._load_personas()
    
    def _load_personas(self):
        """Load personas from JSON file and cache them"""
        try:
            if not self.json_file_path.exists():
                raise FileNotFoundError(f"Persona JSON file not found: {self.json_file_path}")
            
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate JSON structure
            if 'personas' not in data:
                raise ValueError("JSON file must contain 'personas' key")
            
            self._personas_cache = data['personas']
            self._metadata_cache = data.get('metadata', {})
            
            logger.info(f"Loaded {len(self._personas_cache)} personas from {self.json_file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load personas from {self.json_file_path}: {e}")
            # Fallback to empty personas to prevent crashes
            self._personas_cache = {}
            self._metadata_cache = {}
            raise
    
    def get_scenario_persona(self, scenario_name: str) -> Dict:
        """Get persona for a specific test scenario - backwards compatible interface"""
        if scenario_name not in self._personas_cache:
            available_scenarios = list(self._personas_cache.keys())
            raise ValueError(f"Unknown scenario: {scenario_name}. Available scenarios: {available_scenarios}")
        
        return self._personas_cache[scenario_name]
    
    def get_all_scenarios(self) -> Dict:
        """Get all available test scenarios - backwards compatible interface"""
        return self._personas_cache.copy()
    
    def validate_scenario(self, scenario_name: str) -> bool:
        """Validate if scenario exists - backwards compatible interface"""
        return scenario_name in self._personas_cache
    
    def get_personas_by_type(self, persona_type: str) -> Dict[str, Dict]:
        """Get all personas of a specific type"""
        filtered_personas = {}
        for name, persona in self._personas_cache.items():
            if persona.get('persona_type') == persona_type:
                filtered_personas[name] = persona
        return filtered_personas
    
    def get_personas_by_outcome(self, expected_outcome: str) -> Dict[str, Dict]:
        """Get all personas with a specific expected outcome"""
        filtered_personas = {}
        for name, persona in self._personas_cache.items():
            if persona.get('expected_outcome') == expected_outcome:
                filtered_personas[name] = persona
        return filtered_personas
    
    def get_personas_by_age_range(self, min_age: int, max_age: int) -> Dict[str, Dict]:
        """Get personas within a specific age range"""
        filtered_personas = {}
        for name, persona in self._personas_cache.items():
            age = persona.get('age', 0)
            if min_age <= age <= max_age:
                filtered_personas[name] = persona
        return filtered_personas
    
    def get_personas_by_conversation_length(self, length: str) -> Dict[str, Dict]:
        """Get personas with specific conversation length expectation"""
        filtered_personas = {}
        for name, persona in self._personas_cache.items():
            if persona.get('conversation_length') == length:
                filtered_personas[name] = persona
        return filtered_personas
    
    def get_personas_with_topics(self, topics: List[str]) -> Dict[str, Dict]:
        """Get personas that include any of the specified topics"""
        filtered_personas = {}
        for name, persona in self._personas_cache.items():
            persona_topics = persona.get('topics', [])
            if any(topic in persona_topics for topic in topics):
                filtered_personas[name] = persona
        return filtered_personas
    
    def get_likely_leads(self) -> Dict[str, Dict]:
        """Get personas that are likely to become leads"""
        likely_leads = self._metadata_cache.get('lead_potential', {}).get('likely_leads', [])
        return {name: self._personas_cache[name] for name in likely_leads if name in self._personas_cache}
    
    def get_unlikely_leads(self) -> Dict[str, Dict]:
        """Get personas that are unlikely to become leads"""
        unlikely_leads = self._metadata_cache.get('lead_potential', {}).get('unlikely_leads', [])
        return {name: self._personas_cache[name] for name in unlikely_leads if name in self._personas_cache}
    
    def get_edge_case_personas(self) -> Dict[str, Dict]:
        """Get personas designed for edge case testing"""
        return self.get_personas_by_type('edge_case')
    
    def get_persona_stats(self) -> Dict:
        """Get comprehensive statistics about loaded personas"""
        if not self._personas_cache:
            return {"total_personas": 0, "error": "No personas loaded"}
        
        # Count by persona type
        type_counts = {}
        outcome_counts = {}
        age_distribution = {"teenager": 0, "young_adult": 0, "middle_aged": 0, "senior": 0}
        conversation_length_counts = {}
        
        for persona in self._personas_cache.values():
            # Count persona types
            persona_type = persona.get('persona_type', 'unknown')
            type_counts[persona_type] = type_counts.get(persona_type, 0) + 1
            
            # Count expected outcomes
            outcome = persona.get('expected_outcome', 'unknown')
            outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
            
            # Count conversation lengths
            length = persona.get('conversation_length', 'unknown')
            conversation_length_counts[length] = conversation_length_counts.get(length, 0) + 1
            
            # Age distribution
            age = persona.get('age', 0)
            if age < 20:
                age_distribution["teenager"] += 1
            elif age < 30:
                age_distribution["young_adult"] += 1
            elif age < 60:
                age_distribution["middle_aged"] += 1
            else:
                age_distribution["senior"] += 1
        
        return {
            "total_personas": len(self._personas_cache),
            "persona_types": type_counts,
            "expected_outcomes": outcome_counts,
            "age_distribution": age_distribution,
            "conversation_lengths": conversation_length_counts,
            "cities_represented": self._metadata_cache.get('cities_represented', []),
            "lead_potential": self._metadata_cache.get('lead_potential', {}),
            "metadata": self._metadata_cache
        }
    
    def validate_personas(self) -> Dict:
        """Validate all personas for required fields and consistency"""
        validation_results = {
            "valid_personas": [],
            "invalid_personas": [],
            "warnings": [],
            "total_validated": 0
        }
        
        required_fields = ['name', 'email', 'age', 'background', 'fitness_goal', 'communication_style', 
                          'initial_query', 'potential_follow_ups', 'scenario_description']
        
        for persona_name, persona in self._personas_cache.items():
            validation_results["total_validated"] += 1
            persona_issues = []
            
            # Check required fields
            for field in required_fields:
                if field not in persona:
                    persona_issues.append(f"Missing required field: {field}")
            
            # Check data types
            if 'age' in persona and not isinstance(persona['age'], int):
                persona_issues.append("Age must be an integer")
            
            if 'potential_follow_ups' in persona and not isinstance(persona['potential_follow_ups'], list):
                persona_issues.append("potential_follow_ups must be a list")
            
            # Check email format (basic validation)
            if 'email' in persona and '@' not in persona['email']:
                persona_issues.append("Email format appears invalid")
            
            # Record validation results
            if persona_issues:
                validation_results["invalid_personas"].append({
                    "name": persona_name,
                    "issues": persona_issues
                })
            else:
                validation_results["valid_personas"].append(persona_name)
        
        # Check for potential duplicates
        emails = [p.get('email', '') for p in self._personas_cache.values()]
        if len(emails) != len(set(emails)):
            validation_results["warnings"].append("Duplicate email addresses found")
        
        return validation_results
    
    def reload_personas(self):
        """Reload personas from JSON file (useful for testing)"""
        self._personas_cache = None
        self._metadata_cache = None
        self._load_personas()
    
    def get_persona_names(self) -> List[str]:
        """Get list of all persona names"""
        return list(self._personas_cache.keys())
    
    def search_personas(self, query: str) -> Dict[str, Dict]:
        """Search personas by name, background, or description"""
        query_lower = query.lower()
        matching_personas = {}
        
        for name, persona in self._personas_cache.items():
            # Search in name, background, and scenario description
            searchable_text = " ".join([
                name.lower(),
                persona.get('background', '').lower(),
                persona.get('scenario_description', '').lower(),
                persona.get('fitness_goal', '').lower()
            ])
            
            if query_lower in searchable_text:
                matching_personas[name] = persona
        
        return matching_personas


# Global persona manager instance
_persona_manager = None

def get_persona_manager() -> PersonaManager:
    """Get the global persona manager instance"""
    global _persona_manager
    if _persona_manager is None:
        _persona_manager = PersonaManager()
    return _persona_manager


# Backwards compatible functions for existing code
def get_scenario_persona(scenario_name: str) -> Dict:
    """Get persona for a specific test scenario - backwards compatible"""
    return get_persona_manager().get_scenario_persona(scenario_name)

def get_all_scenarios() -> Dict:
    """Get all available test scenarios - backwards compatible"""
    return get_persona_manager().get_all_scenarios()

def validate_scenario(scenario_name: str) -> bool:
    """Validate if scenario exists - backwards compatible"""
    return get_persona_manager().validate_scenario(scenario_name)


# Enhanced functions using JSON capabilities
def get_personas_by_type(persona_type: str) -> Dict[str, Dict]:
    """Get all personas of a specific type"""
    return get_persona_manager().get_personas_by_type(persona_type)

def get_personas_by_outcome(expected_outcome: str) -> Dict[str, Dict]:
    """Get all personas with a specific expected outcome"""
    return get_persona_manager().get_personas_by_outcome(expected_outcome)

def get_persona_stats() -> Dict:
    """Get comprehensive statistics about loaded personas"""
    return get_persona_manager().get_persona_stats()

def validate_personas() -> Dict:
    """Validate all personas for required fields and consistency"""
    return get_persona_manager().validate_personas()