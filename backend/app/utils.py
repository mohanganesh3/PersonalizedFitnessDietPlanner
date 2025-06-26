import json
import re
import logging
import yaml  # PyYAML
from typing import Dict, Any, List, Optional, Union, TypeVar, Type
import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=BaseModel)

def robust_json_parser(json_string: str) -> Dict[str, Any]:
    """
    Enhanced JSON parser that handles various LLM output formats and common errors.
    
    This function attempts multiple strategies to extract valid JSON:
    1. Direct JSON parsing
    2. Markdown code block extraction
    3. Newline sanitization
    4. Common LLM error pattern fixing (unquoted values)
    5. YAML parsing as fallback
    6. Substring extraction as last resort
    
    Args:
        json_string: The string containing JSON data
        
    Returns:
        Dict[str, Any]: The parsed JSON object
        
    Raises:
        ValueError: If no valid JSON could be extracted
    """
    logger.debug(f"Attempting to parse JSON from raw string: {json_string[:500]}...")

    # Strategy 1: Direct JSON parsing
    try:
        return json.loads(json_string.strip())
    except json.JSONDecodeError:
        logger.debug("Direct JSON parsing failed, trying alternative strategies")
    
    # Strategy 2: Extract from markdown code block
    json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', json_string, re.DOTALL)
    if json_match:
        json_data_string = json_match.group(1)
        logger.debug(f"Extracted JSON from markdown block: {json_data_string[:200]}...")
        try:
            return json.loads(json_data_string)
        except json.JSONDecodeError:
            logger.debug("JSON extraction from markdown block failed")
    
    # Strategy 3: Newline sanitization
    try:
        sanitized = re.sub(r"\n\s*", " ", json_string)
        logger.debug("Attempting JSON parse after collapsing newlines/whitespace")
        return json.loads(sanitized.strip())
    except json.JSONDecodeError:
        logger.debug("Newline sanitization strategy failed")
    
    # Strategy 4: Fix common LLM JSON errors
    try:
        # Fix unquoted strings in values like "reps": 30 seconds → "reps": "30 seconds"
        fixed_json = re.sub(
            r':\s*(\d+(?:-\d+)?)\s+(seconds|minutes|reps|sets|each|direction|per|side|leg|arm)',
            r': "\1 \2"', 
            json_string
        )
        
        # Fix "hold_seconds": 30 per leg → "hold_seconds": "30 per leg"
        fixed_json = re.sub(
            r':\s*(\d+(?:-\d+)?)\s+(each|per)\s+(side|leg|arm|direction)',
            r': "\1 \2 \3"', 
            fixed_json
        )
        
        # Fix trailing commas in objects: {"a": 1, "b": 2,} → {"a": 1, "b": 2}
        fixed_json = re.sub(r',\s*}', '}', fixed_json)
        fixed_json = re.sub(r',\s*]', ']', fixed_json)
        
        logger.debug("Attempting JSON parse after fixing common LLM-generated patterns")
        return json.loads(fixed_json.strip())
    except json.JSONDecodeError:
        logger.debug("Common error fixing strategy failed")
    
    # Strategy 5: YAML parsing (more permissive)
    try:
        logger.debug("Attempting YAML parse as permissive fallback")
        yaml_obj = yaml.safe_load(json_string)
        if isinstance(yaml_obj, dict):
            return yaml_obj
    except Exception:
        logger.debug("YAML parsing strategy failed")
    
    # Strategy 6: JSON decoder with extra data handling
    try:
        decoder = json.JSONDecoder()
        obj, _ = decoder.raw_decode(json_string.strip())
        logger.debug("Parsed JSON using raw_decode with trailing data ignored")
        return obj
    except Exception:
        logger.debug("JSON decoder with extra data handling failed")
    
    # Strategy 7: Substring extraction (last resort)
    try:
        start = json_string.find('{')
        end = json_string.rfind('}') + 1
        if start != -1 and end != 0 and end > start:
            potential_json = json_string[start:end]
            logger.debug(f"Attempting last-resort JSON parse on substring: {potential_json[:100]}...")
            return json.loads(potential_json)
    except json.JSONDecodeError:
        logger.critical(f"All JSON parsing strategies failed. Original string: {json_string[:500]}...")
    
    # If all strategies fail, raise error
    raise ValueError("The string does not contain a valid JSON object.")

def safe_model_parse(model_class: Type[T], data: Dict[str, Any]) -> T:
    """
    Safely parse data into a Pydantic model, with detailed error logging
    
    Args:
        model_class: The Pydantic model class
        data: The data to parse
        
    Returns:
        An instance of the model class
        
    Raises:
        ValueError: If parsing fails
    """
    try:
        return model_class.model_validate(data)
    except Exception as e:
        logger.error(f"Failed to parse {model_class.__name__}: {e}")
        logger.debug(f"Problematic data: {data}")
        raise ValueError(f"Could not parse {model_class.__name__}: {e}")

def extract_user_profile_info(message: str) -> Dict[str, Any]:
    """
    Extract potential user profile information from a message
    
    This uses regex patterns to identify common health metrics and preferences
    
    Args:
        message: The user message to analyze
        
    Returns:
        Dict with extracted profile information
    """
    profile = {}
    
    # Age extraction
    age_match = re.search(r'(?:I am|I\'m)\s+(\d+)(?:\s+years old|\s+years|\s+yo\b)', message, re.IGNORECASE)
    if not age_match:
        age_match = re.search(r'(?:age|aged?)[:\s]+(\d+)', message, re.IGNORECASE)
    if age_match:
        try:
            profile['age'] = int(age_match.group(1))
        except ValueError:
            pass
    
    # Weight extraction
    weight_match = re.search(r'(?:I weigh|my weight is|weight[:\s]+)(?:about|around|approximately)?\s*(\d+\.?\d*)\s*(kg|kilos?|pounds?|lbs?)', message, re.IGNORECASE)
    if weight_match:
        try:
            weight_val = float(weight_match.group(1))
            weight_unit = weight_match.group(2).lower()
            
            # Convert to pounds if in kg
            if 'kg' in weight_unit or 'kilo' in weight_unit:
                weight_val = weight_val * 2.20462
            
            profile['weight_lbs'] = round(weight_val, 1)
        except ValueError:
            pass
    
    # Height extraction
    height_match = re.search(r'(?:I am|I\'m|height[:\s]+)(?:about|around|approximately)?\s*(\d+)[\'\"]?\s*(?:feet|foot|ft)\.?\s*(?:and|,)?\s*(\d+)?[\'\"]?\s*(?:inches|inch|in)?', message, re.IGNORECASE)
    if height_match:
        try:
            feet = int(height_match.group(1))
            inches = int(height_match.group(2) or 0)
            profile['height_inches'] = feet * 12 + inches
        except ValueError:
            pass
    
    # Extract dietary preferences
    diet_patterns = [
        (r'\b(?:I am|I\'m)\s+(?:a\s+)?(vegan|vegetarian|pescatarian|flexitarian|carnivore|omnivore)\b', 'dietary_preferences'),
        (r'\b(?:I follow|I\'m on|I do)\s+(?:a\s+)?(keto|paleo|mediterranean|dash|low[\s-]carb|high[\s-]protein)\s+(?:diet|eating plan)\b', 'dietary_preferences'),
        (r'\bI don\'t eat\s+([\w\s,]+)', 'dietary_restrictions'),
        (r'\bI\'m allergic to\s+([\w\s,]+)', 'allergies'),
        (r'\bI can\'t have\s+([\w\s,]+)', 'dietary_restrictions')
    ]
    
    for pattern, field in diet_patterns:
        matches = re.finditer(pattern, message, re.IGNORECASE)
        for match in matches:
            if field not in profile:
                profile[field] = []
            value = match.group(1).strip().lower()
            if value and value not in profile[field]:
                profile[field].append(value)
    
    # Extract fitness goals
    goal_patterns = [
        r'(?:I want to|I\'d like to|looking to|goal is to)\s+(lose weight|build muscle|get stronger|improve endurance|increase flexibility|tone up|bulk up)',
        r'(?:I\'m trying to|I aim to|I need to)\s+(lose weight|build muscle|get stronger|improve endurance|increase flexibility|tone up|bulk up)',
    ]
    
    profile['fitness_goals'] = []
    for pattern in goal_patterns:
        matches = re.finditer(pattern, message, re.IGNORECASE)
        for match in matches:
            goal = match.group(1).strip().lower()
            if goal and goal not in profile['fitness_goals']:
                profile['fitness_goals'].append(goal)
    
    if not profile['fitness_goals']:
        del profile['fitness_goals']
    
    return profile

def generate_timestamp() -> str:
    """Generate a formatted timestamp for the current time"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def merge_user_profiles(old_profile: Dict[str, Any], new_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge an existing user profile with new information
    
    Args:
        old_profile: The existing profile
        new_profile: The new profile information
        
    Returns:
        The merged profile
    """
    merged = old_profile.copy()
    
    for key, new_value in new_profile.items():
        # For list fields, append new items
        if key in merged and isinstance(merged[key], list) and isinstance(new_value, list):
            for item in new_value:
                if item not in merged[key]:
                    merged[key].append(item)
        # For scalar fields, always use the newest value
        else:
            merged[key] = new_value
    
    return merged

def replace_user_profile(old_profile: Dict[str, Any], new_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Replace an existing user profile with completely new information
    
    Args:
        old_profile: The existing profile (used only for fields not in new_profile)
        new_profile: The new profile information
        
    Returns:
        The new profile
    """
    # Start with a completely fresh profile
    return new_profile.copy() 