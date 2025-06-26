import json
import logging
from typing import Dict, Any, Optional

from app.agents.base_agent import BaseAgent, registry
from app.utils import robust_json_parser

logger = logging.getLogger(__name__)

class MentalWellnessAgent(BaseAgent):
    """
    Specialized agent for mental wellness and stress management.
    This agent provides evidence-based guidance on managing stress, anxiety,
    and maintaining mental wellbeing.
    """
    
    def __init__(self, model_name: str):
        instructions = """
        You are a Mental Wellness Expert specializing in psychological aspects of health and fitness.
        Your role is to provide evidence-based guidance on mental wellbeing, stress management, and the
        psychological factors that influence health behaviors.

        ## Response Format:
        Your response should be conversational, empathetic, and well-structured. Begin with a brief
        acknowledgment of the user's situation or concern, then provide helpful information.
        
        Structure your response with:
        1. A brief, empathetic introduction (1-2 sentences)
        2. Main content with clear headings and well-formatted sections
        3. Specific, actionable techniques with proper formatting
        4. A brief encouraging conclusion
        
        When providing techniques or exercises, format them clearly with:
        - Bold headings for technique names
        - Numbered or bulleted steps
        - Clear separation between different techniques
        - Proper paragraph breaks and spacing
        
        ## Critical Guidelines:
        1. Be conversational and empathetic while maintaining professionalism
        2. Use proper formatting with headings, paragraphs, and lists
        3. Offer specific, actionable techniques
        4. Be supportive and encouraging
        5. Consider different mental health needs and preferences
        6. Include appropriate mental health disclaimers at the end of your response
        7. DO NOT include phrases like "Here's what you should know about..."
        8. DO NOT analyze the user's query in your response text
        """
        
        super().__init__(
            name="mental_wellness_agent",
            model_name=model_name,
            instructions=instructions,
            temperature=0.5
        )
        
        # Register with the global registry
        registry.register(self)
    
    def provide_stress_management_guidance(self, query: str, user_profile: Optional[Dict[str, Any]] = None) -> str:
        """
        Provides guidance on stress management techniques.
        
        Args:
            query: The user's query about stress management
            user_profile: Optional user profile data to personalize the response
            
        Returns:
            String containing stress management guidance
        """
        # Format user profile context if available
        context = ""
        if user_profile:
            relevant_fields = ["age", "activity_level", "health_conditions"]
            filtered_profile = {k: v for k, v in user_profile.items() 
                               if k in relevant_fields and v is not None}
            if filtered_profile:
                context += f"User Profile:\n{json.dumps(filtered_profile, indent=2)}\n\n"
        
        # Build the prompt
        prompt = f"""
        {context}User Query: "{query}"
        
        Provide practical, evidence-based guidance on stress management techniques.
        
        Your response should:
        1. Start with a brief, empathetic acknowledgment (1-2 sentences)
        2. Provide well-structured information with clear headings and formatting
        3. Include specific stress relief techniques with proper formatting
        4. End with a brief encouraging conclusion
        
        Use proper markdown formatting:
        - Use ** for bold text (technique names, section headings)
        - Use numbered lists for steps
        - Use paragraph breaks for readability
        - Format each technique in a consistent way
        
        Remember to be conversational and supportive while maintaining professionalism.
        """
        
        try:
            # Run the agent
            response = self.run(prompt)
            
            # Return the content directly
            return response.messages[-1].content
        except Exception as e:
            logger.error(f"Error providing stress management guidance: {e}", exc_info=True)
            return "I understand managing stress can be challenging. Here are some helpful techniques: deep breathing (inhale for 4, hold for 7, exhale for 8), progressive muscle relaxation, and short mindful walks. These simple practices can help reduce stress during difficult times."
    
    def get_relief_exercises(self, query: str, user_profile: Optional[Dict[str, Any]] = None) -> str:
        """
        Provides specific relief exercises based on the user's query.
        
        Args:
            query: The user's query about relief exercises
            user_profile: Optional user profile data to personalize the response
            
        Returns:
            String containing relief exercise instructions
        """
        # Format user profile context if available
        context = ""
        if user_profile:
            relevant_fields = ["age", "activity_level", "health_conditions"]
            filtered_profile = {k: v for k, v in user_profile.items() 
                               if k in relevant_fields and v is not None}
            if filtered_profile:
                context += f"User Profile:\n{json.dumps(filtered_profile, indent=2)}\n\n"
        
        # Build the prompt
        prompt = f"""
        {context}User Query: "{query}"
        
        The user is looking for relief exercises, likely for stress management during studies.
        
        Provide a well-formatted response with:
        1. A brief empathetic introduction (1-2 sentences acknowledging their need for stress relief)
        2. 3-5 specific stress relief exercises that can be done quickly
        3. A brief encouraging conclusion
        
        For each exercise, include and clearly format:
        - **Name of the exercise** (in bold)
        - Brief description (1-2 sentences)
        - Step-by-step instructions (as a numbered list)
        - Duration (how long it should be performed)
        - Benefits
        
        Use proper markdown formatting:
        - Use ** for bold text
        - Use numbered lists for steps
        - Use paragraph breaks between exercises
        - Ensure consistent formatting throughout
        """
        
        try:
            # Run the agent
            response = self.run(prompt)
            
            # Return the content directly
            return response.messages[-1].content
        except Exception as e:
            logger.error(f"Error providing relief exercises: {e}", exc_info=True)
            return """
Taking short breaks for stress relief exercises can make a big difference during intense study sessions. Here are some effective techniques you can try:

**Deep Breathing Exercise (4-7-8 Technique)**
This simple breathing pattern helps activate your parasympathetic nervous system, reducing stress quickly.
1. Sit comfortably with your back straight
2. Inhale quietly through your nose for 4 seconds
3. Hold your breath for 7 seconds
4. Exhale completely through your mouth for 8 seconds
5. Repeat 3-5 times
Duration: 2-3 minutes
Benefits: Reduces anxiety, improves focus, and helps regulate emotional responses

**Progressive Muscle Relaxation**
This technique helps release physical tension that accumulates during studying.
1. Start with your feet and focus on that muscle group
2. Tense the muscles tightly for 5 seconds
3. Release and relax for 10 seconds, noticing the difference
4. Move upward through each muscle group to your face
Duration: 5-10 minutes
Benefits: Releases physical tension, increases body awareness, and promotes mental relaxation

**Quick Mindfulness Break**
This grounding exercise brings you back to the present moment.
1. Pause and take a deep breath
2. Notice 5 things you can see around you
3. Acknowledge 4 things you can touch or feel
4. Listen for 3 things you can hear
5. Identify 2 things you can smell
6. Notice 1 thing you can taste
Duration: 2-3 minutes
Benefits: Reduces rumination, improves present-moment awareness, and resets mental focus

Remember that even short breaks using these techniques can significantly improve your study effectiveness and mental wellbeing.
""" 