# src/metadata_analyzer.py

import re

BUG_FIX_KEYWORDS = [
    'fix', 'bug', 'patch', 'resolve', 'issue', 'correct', 'error', 'defect', 'hotfix'
]
FEATURE_KEYWORDS = [
    'feat', 'add', 'implement', 'new', 'refactor', 'introduce', 'enhance'
]

def analyze_commit_message(message: str) -> str:
    """
    Analyzes the commit message for intent.
    Returns: 'BUG_FIX', 'FEATURE_OR_REFACTOR', or 'NEUTRAL'.
    """
    if not message:
        return 'NEUTRAL'
        
    normalized_message = message.lower().strip()
    
    if any(keyword in normalized_message for keyword in BUG_FIX_KEYWORDS):
        return 'BUG_FIX'
    
    if any(keyword in normalized_message for keyword in FEATURE_KEYWORDS):
        return 'FEATURE_OR_REFACTOR'
        
    return 'NEUTRAL'

def get_change_type_risk(combined_score: float) -> str:
    """
    Analyzes the structural risk of the line-to-line change based on the combined similarity score.
    """
    # High Content/Combined Similarity (> 0.9): Low risk (formatting, minor comment change)
    if combined_score > 0.90:
        return 'LOW_RISK_MINOR_CHANGE'
    
    # Moderate Change (0.5 to 0.9): Standard modification, medium risk
    if combined_score >= 0.50:
        return 'MODERATE_RISK_STANDARD_CHANGE'
        
    # Very Low Similarity (< 0.5): High risk. The old line was heavily rewritten/deleted and replaced.
    if combined_score < 0.50:
        return 'HIGH_RISK_MAJOR_REWRITE'
        
    return 'UNKNOWN'

def categorize_bug_potential(commit_intent: str, change_risk: str) -> str:
    """
    Combines commit intent and change risk to determine bug potential category.
    
    Returns: 'BUG_FIX', 'BUG_INTRODUCING_RISK', or 'NEUTRAL_CHANGE'.
    """
    
    # 1. Bug Fix Changes
    if commit_intent == 'BUG_FIX':
        # If the commit was meant to fix a bug, we categorize the change as BUG_FIX.
        return 'BUG_FIX'
        
    # 2. Bug Introducing Risks (Occurs during Feature or Refactor commits)
    if commit_intent == 'FEATURE_OR_REFACTOR':
        if change_risk == 'HIGH_RISK_MAJOR_REWRITE':
            # A major rewrite during feature/refactor is the HIGHEST RISK
            return 'BUG_INTRODUCING_RISK_HIGH'
        if change_risk == 'MODERATE_RISK_STANDARD_CHANGE':
            # Standard changes are moderate risk
            return 'BUG_INTRODUCING_RISK_MODERATE'
            
    # 3. Neutral/Safe Changes (e.g., identity matches, minor format changes)
    return 'NEUTRAL_CHANGE'