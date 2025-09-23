"""
Compliance Rules Package

This package contains compliance rule definitions for various frameworks:
- GDPR (General Data Protection Regulation)
- HIPAA (Health Insurance Portability and Accountability Act)
- SOX (Sarbanes-Oxley Act)

Each rule file contains:
- Rule metadata (type, description)
- Individual rules with patterns and LLM prompts
- Severity levels and categorization
"""

import os
import json
from typing import Dict, Any, List

def load_rule_file(rule_type: str) -> Dict[str, Any]:
    """
    Load a specific rule file by type
    
    Args:
        rule_type: The rule type (e.g., 'gdpr', 'hipaa', 'sox')
    
    Returns:
        Dictionary containing the rule definitions
    """
    current_dir = os.path.dirname(__file__)
    rule_file = os.path.join(current_dir, f"{rule_type.lower()}_rules.json")
    
    if os.path.exists(rule_file):
        with open(rule_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"Rule file not found: {rule_file}")

def get_available_rule_types() -> List[str]:
    """
    Get list of available rule types
    
    Returns:
        List of available rule type names
    """
    current_dir = os.path.dirname(__file__)
    rule_files = [f for f in os.listdir(current_dir) if f.endswith('_rules.json')]
    return [f.replace('_rules.json', '').upper() for f in rule_files]

def load_all_rules() -> Dict[str, Any]:
    """
    Load all available rule files
    
    Returns:
        Dictionary with rule type as key and rule definitions as values
    """
    rules = {}
    for rule_type in get_available_rule_types():
        try:
            rules[rule_type] = load_rule_file(rule_type)
        except FileNotFoundError:
            continue
    return rules

# Export main functions
__all__ = [
    "load_rule_file",
    "get_available_rule_types", 
    "load_all_rules"
]
