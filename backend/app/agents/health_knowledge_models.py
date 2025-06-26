from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from app.models import KnowledgeResponse, HealthTopic
from app.agents.base_agent import AgentOutput

class ExpertInput(BaseModel):
    """Input for an expert agent"""
    query: str
    user_profile: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    
class ExpertOutput(AgentOutput):
    """Output from an expert agent"""
    title: str
    content: str
    subtopics: Optional[List[Dict[str, str]]] = None
    references: Optional[List[str]] = None
    disclaimers: Optional[List[str]] = None

class GeneralHealthExpertOutput(ExpertOutput):
    """Output from the general health expert"""
    agent_name: str = "general_health_expert"
    health_recommendations: Optional[List[str]] = None

class NutritionExpertOutput(ExpertOutput):
    """Output from the nutrition expert"""
    agent_name: str = "nutrition_expert"
    dietary_recommendations: Optional[List[str]] = None
    food_groups: Optional[Dict[str, List[str]]] = None

class FitnessExpertOutput(ExpertOutput):
    """Output from the fitness expert"""
    agent_name: str = "fitness_expert"
    exercise_recommendations: Optional[List[str]] = None
    activity_guidelines: Optional[Dict[str, str]] = None

class MentalWellnessExpertOutput(ExpertOutput):
    """Output from the mental wellness expert"""
    agent_name: str = "mental_wellness_expert"
    wellness_techniques: Optional[List[str]] = None
    stress_management: Optional[Dict[str, str]] = None

class HealthKnowledgeCouncilOutput(AgentOutput):
    """Output from the health knowledge council"""
    agent_name: str = "health_knowledge_council"
    general_health: Optional[Union[str, Dict[str, Any], HealthTopic]] = None
    nutrition: Optional[Union[str, Dict[str, Any], HealthTopic]] = None
    fitness: Optional[Union[str, Dict[str, Any], HealthTopic]] = None
    mental_wellness: Optional[Union[str, Dict[str, Any], HealthTopic]] = None
    references: Optional[List[str]] = None
    disclaimers: Optional[List[str]] = None
    
    def to_knowledge_response(self) -> KnowledgeResponse:
        """Convert to KnowledgeResponse model"""
        return KnowledgeResponse(
            general_health=self.general_health,
            nutrition=self.nutrition,
            fitness=self.fitness,
            mental_wellness=self.mental_wellness,
            references=self.references
        ) 