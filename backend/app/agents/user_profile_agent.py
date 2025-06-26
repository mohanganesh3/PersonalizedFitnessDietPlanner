import json
import logging
from typing import Dict, Any, Optional, List
from agno.agent import Agent
from agno.models.google import Gemini
from app.utils import robust_json_parser, extract_user_profile_info, merge_user_profiles, replace_user_profile
from app.models import UserProfile

logger = logging.getLogger(__name__)

class UserProfileAgent(Agent):
    """
    Agent responsible for extracting, maintaining, and updating user profile information
    from natural conversations. This agent builds a comprehensive understanding of the
    user over time to enable personalized health and fitness recommendations.
    """
    
    def __init__(self, model_name: str):
        super().__init__(
            name="UserProfileAgent",
            model=Gemini(id=model_name, temperature=0.1),  # Low temperature for factual extraction
            instructions="""
            You are a User Profile Agent for a health and fitness planning application.
            Your role is to extract relevant user information from conversations and maintain
            an accurate user profile. You never interact with the user directly.
            
            ## Core Responsibilities:
            1. Extract health metrics (age, weight, height, etc.)
            2. Identify dietary preferences and restrictions
            3. Recognize fitness goals and current activity levels
            4. Note health conditions and limitations
            5. Understand equipment availability and time constraints
            
            ## Output Format:
            You MUST respond with a single, valid JSON object containing:
            1. "extracted_profile": New information extracted from this message
            2. "confidence_scores": Confidence level (0.0-1.0) for each extracted field
            3. "missing_information": List of important fields still needed for better recommendations
            
            ## Example Output:
            {
              "extracted_profile": {
                "age": 35,
                "weight_lbs": 180,
                "fitness_goals": ["lose weight", "improve endurance"],
                "dietary_restrictions": ["gluten-free"]
              },
              "confidence_scores": {
                "age": 0.95,
                "weight_lbs": 0.9,
                "fitness_goals": 0.8,
                "dietary_restrictions": 0.7
              },
              "missing_information": ["height_inches", "activity_level", "available_equipment"]
            }
            
            ## Critical Rules:
            1. NEVER invent information not present in the message
            2. Assign accurate confidence scores based on clarity of information
            3. Only include fields in extracted_profile if they appear in the message
            4. Do not include any explanations or text outside the JSON object
            """,
            debug_mode=True
        )
    
    def extract_profile_info(self, message: str, existing_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Extract user profile information from a message and completely replace any existing profile.
        
        Args:
            message: The user message to analyze
            existing_profile: Optional existing profile (will be ignored)
            
        Returns:
            Dict containing the new profile and extraction metadata
        """
        # First use regex-based extraction for basic fields
        regex_extracted = extract_user_profile_info(message)
        
        # Then use LLM for more nuanced extraction
        prompt = f"""
        Extract user profile information from this message:
        "{message}"
        
        Only extract information mentioned in this specific message. Do not invent or assume information.
        Respond with a valid JSON object following the required format.
        """
        
        try:
            response = self.run(prompt)
            llm_result = robust_json_parser(response.messages[-1].content)
            
            # Validate LLM extraction
            llm_extracted = llm_result.get("extracted_profile", {})
            confidence_scores = llm_result.get("confidence_scores", {})
            missing_information = llm_result.get("missing_information", [])
            
            # Filter out low-confidence extractions
            filtered_llm_extracted = {
                k: v for k, v in llm_extracted.items() 
                if k in confidence_scores and confidence_scores[k] >= 0.6
            }
            
            # Combine regex and LLM extractions (prefer regex for basic fields)
            combined_extraction = {**filtered_llm_extracted, **regex_extracted}
            
            # Use only the newly extracted information
            final_profile = combined_extraction
            
            # Validate against our model
            try:
                validated_profile = UserProfile.model_validate(final_profile)
                final_profile = validated_profile.model_dump(exclude_none=True)
            except Exception as e:
                self.logger.warning(f"Profile validation error: {e}")
            
            return {
                "profile": final_profile,
                "new_information": combined_extraction,
                "confidence_scores": confidence_scores,
                "missing_information": missing_information
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting profile info: {e}", exc_info=True)
            # Fall back to regex extraction only
            return {
                "profile": regex_extracted,
                "new_information": regex_extracted,
                "confidence_scores": {},
                "missing_information": []
            }
    
    def generate_profile_questions(self, profile: Dict[str, Any], context: str) -> List[str]:
        """
        Generate natural follow-up questions to fill gaps in the user profile.
        
        Args:
            profile: The current user profile
            context: The conversation context
            
        Returns:
            List of suggested follow-up questions
        """
        prompt = f"""
        Based on the current user profile and conversation context, generate 2-3 natural follow-up questions 
        that would help fill important gaps in the user profile for better health and fitness recommendations.
        
        Current user profile:
        {json.dumps(profile, indent=2)}
        
        Recent conversation context:
        "{context}"
        
        Output MUST be a valid JSON array of strings, each containing a single question.
        Questions should be conversational and not feel like a form or questionnaire.
        Do not ask about information we already have in the profile.
        """
        
        try:
            response = self.run(prompt)
            questions = robust_json_parser(response.messages[-1].content)
            
            if isinstance(questions, list) and all(isinstance(q, str) for q in questions):
                return questions
            elif isinstance(questions, dict) and "questions" in questions:
                return questions["questions"]
            else:
                logger.warning(f"Unexpected questions format: {questions}")
                return []
        except Exception as e:
            logger.error(f"Error generating profile questions: {e}", exc_info=True)
            return [] 