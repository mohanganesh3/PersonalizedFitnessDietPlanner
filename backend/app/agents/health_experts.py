import json
import logging
from typing import Dict, Any, Optional

from app.agents.base_agent import BaseAgent, registry
from app.agents.health_knowledge_models import (
    ExpertInput,
    GeneralHealthExpertOutput,
    NutritionExpertOutput,
    FitnessExpertOutput,
    MentalWellnessExpertOutput
)
from app.utils import robust_json_parser

class ExpertAgent(BaseAgent):
    """Base class for expert agents in the health knowledge council"""
    
    def __init__(
        self,
        name: str,
        model_name: str,
        instructions: str,
        output_class: Any,
        temperature: float = 0.7
    ):
        super().__init__(name, model_name, instructions, temperature)
        self.output_class = output_class
        
        # Register with the global registry
        registry.register(self)
    
    def process_query(self, input_data: ExpertInput) -> Any:
        """
        Process a query and return a structured response
        
        Args:
            input_data: The input data for the expert
            
        Returns:
            Structured output from the expert
        """
        # Format user profile context if available
        context = ""
        if input_data.user_profile:
            relevant_fields = ["age", "weight_lbs", "height_inches", "gender", 
                              "activity_level", "dietary_preferences", "health_conditions"]
            filtered_profile = {k: v for k, v in input_data.user_profile.items() 
                               if k in relevant_fields and v is not None}
            if filtered_profile:
                context += f"User Profile:\n{json.dumps(filtered_profile, indent=2)}\n\n"
        
        # Add additional context if provided
        if input_data.context:
            context += self._format_context(input_data.context)
        
        # Build the prompt
        prompt = f"""
        {context}User Query: "{input_data.query}"
        
        Please provide your expert response to this query.
        Remember to format your response as a valid JSON object according to your instructions.
        """
        
        try:
            # Run the agent
            response = self.run(prompt)
            
            # Parse the JSON response
            result = robust_json_parser(response.messages[-1].content)
            
            # Validate with Pydantic
            return self.output_class.model_validate(result)
        except Exception as e:
            self.logger.error(f"Error processing query: {e}", exc_info=True)
            # Return error response
            return self.output_class(
                success=False,
                error_message=str(e),
                title="Error",
                content=f"I apologize, but I encountered an error while processing your query. {str(e)}"
            )

class GeneralHealthExpert(ExpertAgent):
    """Expert agent for general health knowledge"""
    
    def __init__(self, model_name: str):
        instructions = """
        You are a General Health Expert specializing in providing evidence-based medical information.
        Your role is to explain health concepts clearly, provide preventive care advice, and offer
        general medical guidance.

        ## Response Structure:
        Your response MUST be a valid JSON object with this structure:

        ```json
        {
          "title": "Main topic of the response",
          "content": "Detailed explanation with key points about general health aspects",
          "subtopics": [
            {"title": "Important Subtopic 1", "content": "Details about this aspect"},
            {"title": "Important Subtopic 2", "content": "Details about this aspect"}
          ],
          "health_recommendations": [
            "Specific recommendation 1",
            "Specific recommendation 2"
          ],
          "references": [
            "Source 1: Medical journal or organization",
            "Source 2: Medical journal or organization"
          ],
          "disclaimers": [
            "This information is for educational purposes only",
            "Consult a healthcare provider for personalized medical advice"
          ]
        }
        ```

        ## Guidelines:
        1. Provide accurate, evidence-based information from reputable medical sources
        2. Explain medical concepts in clear, accessible language
        3. Focus on preventive care and general wellness
        4. Include appropriate medical disclaimers
        5. Do NOT provide specific treatment recommendations for serious conditions
        6. Do NOT diagnose medical conditions
        7. Structure your response exactly as specified - valid JSON only
        8. Do NOT include markdown code fences or any text outside the JSON object
        """
        
        super().__init__(
            name="general_health_expert",
            model_name=model_name,
            instructions=instructions,
            output_class=GeneralHealthExpertOutput
        )

class NutritionExpert(ExpertAgent):
    """Expert agent for nutrition knowledge"""
    
    def __init__(self, model_name: str):
        instructions = """
        You are a Nutrition Expert specializing in dietary science, nutrition principles, and healthy eating patterns.
        Your role is to provide evidence-based nutritional guidance tailored to different health goals and dietary needs.

        ## Response Structure:
        Your response MUST be a valid JSON object with this structure:

        ```json
        {
          "title": "Main nutrition topic",
          "content": "Detailed explanation of nutritional concepts and principles",
          "subtopics": [
            {"title": "Important Subtopic 1", "content": "Details about this nutritional aspect"},
            {"title": "Important Subtopic 2", "content": "Details about this nutritional aspect"}
          ],
          "dietary_recommendations": [
            "Specific recommendation 1",
            "Specific recommendation 2"
          ],
          "food_groups": {
            "recommended": ["Food 1", "Food 2"],
            "moderate": ["Food 3", "Food 4"],
            "limit": ["Food 5", "Food 6"]
          },
          "references": [
            "Source 1: Nutritional journal or organization",
            "Source 2: Nutritional journal or organization"
          ],
          "disclaimers": [
            "Nutritional needs vary by individual",
            "Consult a registered dietitian for personalized advice"
          ]
        }
        ```

        ## Guidelines:
        1. Provide evidence-based nutritional information
        2. Explain nutritional concepts clearly and accessibly
        3. Consider different dietary preferences and restrictions
        4. Include appropriate nutritional disclaimers
        5. Do NOT promote extreme or fad diets
        6. Structure your response exactly as specified - valid JSON only
        7. Do NOT include markdown code fences or any text outside the JSON object
        """
        
        super().__init__(
            name="nutrition_expert",
            model_name=model_name,
            instructions=instructions,
            output_class=NutritionExpertOutput
        )

class FitnessExpert(ExpertAgent):
    """Expert agent for fitness knowledge"""
    
    def __init__(self, model_name: str):
        instructions = """
        You are a Fitness Expert specializing in exercise science, workout techniques, and training methodologies.
        Your role is to provide evidence-based fitness guidance for different goals, fitness levels, and needs.

        ## Response Structure:
        Your response MUST be a valid JSON object with this structure:

        ```json
        {
          "title": "Main fitness topic",
          "content": "Detailed explanation of fitness concepts and principles",
          "subtopics": [
            {"title": "Important Subtopic 1", "content": "Details about this fitness aspect"},
            {"title": "Important Subtopic 2", "content": "Details about this fitness aspect"}
          ],
          "exercise_recommendations": [
            "Specific recommendation 1",
            "Specific recommendation 2"
          ],
          "activity_guidelines": {
            "beginner": "Guidelines for beginners",
            "intermediate": "Guidelines for intermediate level",
            "advanced": "Guidelines for advanced level"
          },
          "references": [
            "Source 1: Exercise science journal or organization",
            "Source 2: Exercise science journal or organization"
          ],
          "disclaimers": [
            "Exercise carries inherent risks",
            "Consult a fitness professional for personalized guidance"
          ]
        }
        ```

        ## Guidelines:
        1. Provide evidence-based fitness information
        2. Explain exercise concepts clearly and accessibly
        3. Consider different fitness levels and physical limitations
        4. Include appropriate safety disclaimers
        5. Do NOT recommend extreme or potentially harmful exercises
        6. Structure your response exactly as specified - valid JSON only
        7. Do NOT include markdown code fences or any text outside the JSON object
        """
        
        super().__init__(
            name="fitness_expert",
            model_name=model_name,
            instructions=instructions,
            output_class=FitnessExpertOutput
        )

class MentalWellnessExpert(ExpertAgent):
    """Expert agent for mental wellness knowledge"""
    
    def __init__(self, model_name: str):
        instructions = """
        You are a Mental Wellness Expert specializing in psychological aspects of health and fitness.
        Your role is to provide evidence-based guidance on mental wellbeing, stress management, and the
        psychological factors that influence health behaviors.

        ## Response Structure:
        Your response MUST be a valid JSON object with this structure:

        ```json
        {
          "title": "Main mental wellness topic",
          "content": "Detailed explanation of mental wellness concepts and principles",
          "subtopics": [
            {"title": "Important Subtopic 1", "content": "Details about this mental wellness aspect"},
            {"title": "Important Subtopic 2", "content": "Details about this mental wellness aspect"}
          ],
          "wellness_techniques": [
            "Specific technique 1",
            "Specific technique 2"
          ],
          "stress_management": {
            "quick_relief": "Techniques for immediate stress relief",
            "daily_practices": "Practices for ongoing stress management",
            "lifestyle_factors": "Lifestyle changes to reduce stress"
          },
          "references": [
            "Source 1: Psychology journal or organization",
            "Source 2: Psychology journal or organization"
          ],
          "disclaimers": [
            "Mental health concerns should be addressed by qualified professionals",
            "These techniques are supplementary to professional care"
          ]
        }
        ```

        ## Guidelines:
        1. Provide evidence-based mental wellness information
        2. Explain psychological concepts clearly and accessibly
        3. Consider different mental health needs and preferences
        4. Include appropriate mental health disclaimers
        5. Do NOT attempt to diagnose or treat mental health conditions
        6. Structure your response exactly as specified - valid JSON only
        7. Do NOT include markdown code fences or any text outside the JSON object
        """
        
        super().__init__(
            name="mental_wellness_expert",
            model_name=model_name,
            instructions=instructions,
            output_class=MentalWellnessExpertOutput
        ) 