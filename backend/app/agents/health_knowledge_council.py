import logging
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor

from app.agents.base_agent import BaseAgent, registry
from app.agents.health_experts import (
    GeneralHealthExpert,
    NutritionExpert,
    FitnessExpert,
    MentalWellnessExpert
)
from app.agents.health_knowledge_models import (
    ExpertInput,
    HealthKnowledgeCouncilOutput
)
from app.utils import robust_json_parser

logger = logging.getLogger(__name__)

class HealthKnowledgeCouncilAgent(BaseAgent):
    def __init__(self, model_name: str):
        instructions = """
        You are the Health Knowledge Council Coordinator, responsible for delegating health and fitness queries 
        to specialized experts and synthesizing their responses into a comprehensive answer.
        
        Your role is to:
        1. Analyze user queries to determine which experts should respond
        2. Synthesize expert responses into a cohesive, well-structured answer
        3. Ensure all information is evidence-based and includes appropriate disclaimers
        4. Present information in a clear, accessible format
        """
        
        super().__init__(
            name="health_knowledge_council",
            model_name=model_name,
            instructions=instructions
        )
        
        self.experts = {
            "general_health": GeneralHealthExpert(model_name),
            "nutrition": NutritionExpert(model_name),
            "fitness": FitnessExpert(model_name),
            "mental_wellness": MentalWellnessExpert(model_name)
        }
        registry.register(self)

    def determine_required_experts(self, query: str) -> List[str]:
        prompt = f"""
        Analyze this health/fitness query: "{query}"
        
        Determine which health experts should respond to this query. Choose from:
        1. general_health - For general medical and health information
        2. nutrition - For dietary and nutritional information
        3. fitness - For exercise and physical activity information
        4. mental_wellness - For psychological and mental health aspects
        
        Return a JSON array with the names of the experts that should respond.
        For example: ["general_health", "nutrition"]
        """
        
        try:
            response = self.run(prompt)
            result = robust_json_parser(response.messages[-1].content)
            
            if isinstance(result, list):
                return [expert for expert in result if expert in self.experts]
            else:
                logger.warning("Invalid response format for expert determination")
                return list(self.experts.keys())
        except Exception as e:
            logger.error(f"Error determining required experts: {e}", exc_info=True)
            return list(self.experts.keys())

    def process_knowledge_query(self, user_message: str, user_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            required_experts = self.determine_required_experts(user_message)
            logger.info(f"Required experts for query: {required_experts}")
            
            expert_input = ExpertInput(
                query=user_message,
                user_profile=user_profile
            )
            
            expert_responses = {}
            all_references = []
            all_disclaimers = []
            
            with ThreadPoolExecutor() as executor:
                future_to_expert = {
                    executor.submit(self.experts[expert].process_query, expert_input): expert
                    for expert in required_experts
                }
                
                for future in future_to_expert:
                    expert_name = future_to_expert[future]
                    try:
                        result = future.result()
                        expert_responses[expert_name] = {
                            "title": result.title,
                            "content": result.content,
                            "subtopics": result.subtopics
                        }
                        if result.references:
                            all_references.extend(result.references)
                        if result.disclaimers:
                            all_disclaimers.extend(result.disclaimers)
                    except Exception as e:
                        logger.error(f"Error getting response from {expert_name}: {e}", exc_info=True)
                        expert_responses[expert_name] = {
                            "title": f"Error from {expert_name}",
                            "content": "Could not retrieve information due to a technical issue."
                        }
            
            all_references = list(set(all_references))
            all_disclaimers = list(set(all_disclaimers))
            
            council_output = HealthKnowledgeCouncilOutput(
                general_health=expert_responses.get("general_health"),
                nutrition=expert_responses.get("nutrition"),
                fitness=expert_responses.get("fitness"),
                mental_wellness=expert_responses.get("mental_wellness"),
                references=all_references,
                disclaimers=all_disclaimers
            )
            
            return council_output.model_dump(exclude_none=True)
            
        except Exception as e:
            logger.error(f"Error in knowledge council: {e}", exc_info=True)
            return self._run_fallback_llm_call(user_message)

    def _run_fallback_llm_call(self, user_message: str) -> Dict[str, Any]:
        fallback_prompt = f"""
        Generate a simplified but helpful response to this health question: "{user_message}"
        
        Your response must be a valid JSON object with this structure:
        {{
          "expert_responses": {{
            "general_health": {{
              "title": "General Health Information",
              "content": "Brief general health information"
            }},
            "nutrition": {{
              "title": "Nutritional Guidance",
              "content": "Brief nutritional guidance"
            }},
            "fitness": {{
              "title": "Fitness Recommendations",
              "content": "Brief fitness recommendations"
            }},
            "mental_wellness": {{
              "title": "Mental Wellness Considerations",
              "content": "Brief mental wellness considerations"
            }}
          }},
          "references": ["General health guidelines"],
          "disclaimers": ["This is general advice only, consult professionals for personalized guidance"]
        }}
        """
        
        try:
            response = self.run(fallback_prompt)
            return robust_json_parser(response.messages[-1].content)
        except Exception as e:
            logger.critical(f"CRITICAL: Fallback LLM call failed: {e}", exc_info=True)
            return {
                "expert_responses": {
                    "general_health": {
                        "title": "General Health Information",
                        "content": "We're experiencing technical difficulties providing detailed health information. For reliable health guidance, please consult with qualified healthcare professionals."
                    },
                    "nutrition": {
                        "title": "Nutritional Guidance",
                        "content": "Nutrition information unavailable due to technical issues."
                    },
                    "fitness": {
                        "title": "Fitness Recommendations",
                        "content": "Fitness information unavailable due to technical issues."
                    },
                    "mental_wellness": {
                        "title": "Mental Wellness Considerations",
                        "content": "Mental wellness information unavailable due to technical issues."
                    }
                },
                "references": ["Please consult reliable health resources like the CDC, WHO, or NIH."],
                "disclaimers": ["This is a system-generated fallback response due to technical issues."]
            }

    def get_topic_information(self, topic: str) -> Dict[str, Any]:
        topic_lower = topic.lower()
        if "diet" in topic_lower or "nutrition" in topic_lower or "food" in topic_lower:
            primary_expert = "nutrition"
        elif "exercise" in topic_lower or "workout" in topic_lower or "fitness" in topic_lower:
            primary_expert = "fitness"
        elif "mental" in topic_lower or "stress" in topic_lower or "anxiety" in topic_lower:
            primary_expert = "mental_wellness"
        else:
            primary_expert = "general_health"
        
        expert_input = ExpertInput(
            query=f"Provide comprehensive information about {topic}"
        )
        
        try:
            result = self.experts[primary_expert].process_query(expert_input)
            return {
                "topic_information": {
                    "title": result.title,
                    "content": result.content,
                    "subtopics": result.subtopics
                },
                "references": result.references or [],
                "disclaimers": result.disclaimers or []
            }
        except Exception as e:
            logger.error(f"Failed to get topic information for '{topic}': {e}", exc_info=True)
            return {
                "topic_information": {
                    "title": topic,
                    "content": "We couldn't retrieve detailed information about this topic due to technical issues."
                },
                "references": [],
                "disclaimers": ["This is a system-generated fallback response due to technical issues."]
            } 