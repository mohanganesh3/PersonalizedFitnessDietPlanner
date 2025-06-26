from agno.agent import Agent
from agno.models.google import Gemini
from typing import Dict, Any, List, Optional
import json
import logging
import re
from app.utils import robust_json_parser, extract_user_profile_info

logger = logging.getLogger(__name__)

class ChiefStrategistAgent(Agent):
    """
    The Chief Strategist agent analyzes user queries to determine intent and orchestrate the system's response.
    It decides which specialized agents should handle each query and how to process the user's input.
    """
    
    def __init__(self, model_name: str):
        super().__init__(
            name="ChiefStrategistAgent",
            model=Gemini(id=model_name, temperature=0.3),
            instructions="""
            You are the Chief Strategist for an AI health and fitness planning system. Your role is to analyze 
            user queries, determine their primary intent, and decide which specialized agents should handle each request.
            
            ## Specialized Agents Available:
            1. **HealthKnowledgeCouncilAgent**: Provides expert health and fitness knowledge
            2. **UserProfileAgent**: Manages user profile information
            3. **PlanGenerationCouncilAgent**: Creates personalized diet and fitness plans
            4. **MentalWellnessAgent**: Provides stress management and mental wellness guidance
            
            ## Response Format:
            Your response MUST be a single, valid JSON object with this structure:
            
            ```json
            {
              "intent_analysis": "topic or goal of user's query",
              "intent_category": "knowledge_query|plan_request|greeting|profile_update|off_topic",
              "required_agents": ["AgentName1", "AgentName2"],
              "next_action": "delegate_to_agents|immediate_response|extract_profile_info",
              "response": "Direct response for greetings or off-topic queries",
              "profile_extraction_needed": true|false,
              "follow_up_suggestions": ["Suggested follow-up question 1", "Suggested follow-up question 2"]
            }
            ```
            
            ## Critical Rules:
            1. For greetings, set next_action to "immediate_response" and provide a warm welcome
            2. For off-topic queries, set next_action to "immediate_response" and explain the system's purpose
            3. For health/fitness questions, include "HealthKnowledgeCouncilAgent" in required_agents
            4. For plan requests, include "PlanGenerationCouncilAgent" in required_agents
            5. For stress management or mental wellness queries, include "MentalWellnessAgent" in required_agents
            6. If the query contains personal information, set profile_extraction_needed to true
            7. Structure your response EXACTLY as specified - valid JSON only
            8. Do NOT include markdown code fences or any text outside the JSON
            9. For intent_analysis, provide ONLY the topic or goal directly (e.g., "stress management techniques" NOT "user is asking about stress management techniques")
            10. Never include phrases like "User is asking for" or "User wants to know about" in your intent_analysis
            """,
            debug_mode=True
        )
    
    def analyze_query(self, query: str, current_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyzes the user query to determine intent and required agents.
        
        Args:
            query: The user's message
            current_profile: Optional existing user profile
            
        Returns:
            Dict containing intent analysis and routing information
        """
        # Extract potential profile information using regex first
        extracted_profile = extract_user_profile_info(query)
        profile_info_present = len(extracted_profile) > 0
        
        # Build context for the prompt
        profile_context = ""
        if current_profile:
            profile_context = f"Current User Profile:\n{json.dumps(current_profile, indent=2)}\n\n"
            
        prompt = f"""
        {profile_context}Analyze the following user query and determine the appropriate response strategy:
        
        User Query: "{query}"
        
        Identify the user's primary intent, which specialized agents should handle this query, 
        and whether profile information should be extracted.
        
        IMPORTANT: For intent_analysis, provide ONLY the direct topic or goal (e.g., "stress management techniques" NOT "user is asking about stress management techniques")
        
        Respond with a valid JSON object following the exact structure specified in your instructions.
        """
        
        try:
            response = self.run(prompt)
            result = robust_json_parser(response.messages[-1].content)
            
            # Validate the required fields
            required_fields = ["intent_analysis", "intent_category", "next_action"]
            if not all(field in result for field in required_fields):
                logger.warning(f"Missing required fields in strategy: {[f for f in required_fields if f not in result]}")
                return self._fallback_strategy(query, profile_info_present)
            
            # Add profile_extraction_needed if not present but profile info detected
            if "profile_extraction_needed" not in result and profile_info_present:
                result["profile_extraction_needed"] = True
            
            # Ensure required_agents is always a list
            if "required_agents" not in result:
                result["required_agents"] = []
            
            # If next_action is immediate_response, ensure response field exists
            if result.get("next_action") == "immediate_response" and "response" not in result:
                result["response"] = "Hello! I'm your AI Health and Fitness assistant. How can I help you today?"
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing query: {e}", exc_info=True)
            return self._fallback_strategy(query, profile_info_present)
    
    def _fallback_strategy(self, query: str, profile_info_present: bool = False) -> Dict[str, Any]:
        """
        Provides a safe fallback strategy when analysis fails.
        
        Args:
            query: The original user query
            profile_info_present: Whether profile information was detected
            
        Returns:
            Dict containing a conservative fallback strategy
        """
        # Check for common greetings
        greeting_patterns = ["hello", "hi ", "hey", "greetings", "good morning", "good afternoon", "good evening"]
        is_greeting = any(pattern in query.lower() for pattern in greeting_patterns)
        
        if is_greeting:
            return {
                "intent_analysis": "greeting",
                "intent_category": "greeting",
                "required_agents": [],
                "next_action": "immediate_response",
                "response": "Hello! I'm your AI Health and Fitness assistant. How can I help you with your health and fitness goals today?",
                "profile_extraction_needed": profile_info_present
            }
        
        # Default to treating as a knowledge query
        return {
            "intent_analysis": query.strip(),
            "intent_category": "knowledge_query",
            "required_agents": ["HealthKnowledgeCouncilAgent"],
            "next_action": "delegate_to_agents",
            "profile_extraction_needed": profile_info_present
        }
    
    def generate_follow_up_questions(self, query: str, response_content: Dict[str, Any], user_profile: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Generates contextual follow-up questions based on the conversation.
        
        Args:
            query: The user's original query
            response_content: The content of the system's response
            user_profile: Optional user profile information
            
        Returns:
            List of suggested follow-up questions
        """
        # Build context for the prompt
        profile_context = ""
        if user_profile:
            profile_context = f"User Profile:\n{json.dumps(user_profile, indent=2)}\n\n"
        
        response_context = ""
        if response_content:
            response_context = f"System Response:\n{json.dumps(response_content, indent=2)}\n\n"
        
        prompt = f"""
        {profile_context}{response_context}Generate 2-3 natural follow-up questions based on this conversation:
        
        User Query: "{query}"
        
        The follow-up questions should be natural questions that the user might ask next, after receiving our response. 
        
        IMPORTANT RULES:
        1. DO NOT include phrases like "What are some..." or "Are there any..." at the beginning of questions
        2. Make questions direct and concise
        3. Avoid questions that start with "Would you like to know more about..."
        4. Each question should be a complete, standalone question
        
        Respond with a valid JSON array of strings, each containing a single question.
        Format your response as: ["Question 1?", "Question 2?", "Question 3?"]
        """
        
        try:
            response = self.run(prompt)
            content = response.messages[-1].content
            
            # Try to parse as JSON first
            try:
                questions = robust_json_parser(content)
                
                if isinstance(questions, list) and all(isinstance(q, str) for q in questions):
                    return questions[:3]  # Limit to 3 questions
                elif isinstance(questions, dict) and "questions" in questions:
                    return questions["questions"][:3]
            except ValueError:
                # If JSON parsing fails, try to extract questions directly from the text
                logger.warning("JSON parsing failed for follow-up questions, attempting text extraction")
                
                # Look for numbered or bulleted questions
                question_pattern = r'(?:^|\n)(?:\d+\.|\*|\-)\s*(.*?\?)'
                questions = re.findall(question_pattern, content)
                
                if questions:
                    return questions[:3]
                
                # Look for quoted questions
                quoted_pattern = r'"([^"]*?\?)"'
                quoted_questions = re.findall(quoted_pattern, content)
                
                if quoted_questions:
                    return quoted_questions[:3]
                
                # As a last resort, split by newlines and look for question marks
                lines = [line.strip() for line in content.split('\n') if '?' in line]
                if lines:
                    return lines[:3]
            
            # If we got here, we couldn't extract questions
            logger.warning(f"Could not extract questions from: {content[:100]}...")
            return []
                
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {e}", exc_info=True)
            return []
        


