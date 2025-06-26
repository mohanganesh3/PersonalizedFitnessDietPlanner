import logging
from typing import Dict, Any, List, Optional, Union, Callable
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.google import Gemini

class AgentOutput(BaseModel):
    """Base class for structured agent outputs"""
    agent_name: str
    success: bool = True
    error_message: Optional[str] = None
    
    class Config:
        extra = "allow"

class BaseAgent:
    """
    Base agent class for the health fitness planner.
    Provides common functionality for all agents in the system.
    """
    
    def __init__(
        self, 
        name: str,
        model_name: str,
        instructions: str,
        temperature: float = 0.7,
        logger: Optional[logging.Logger] = None
    ):
        self.name = name
        self.model_name = model_name
        self.instructions = instructions
        self.temperature = temperature
        self.logger = logger or logging.getLogger(name)
        
        # Initialize the agent
        self.agent = Agent(
            name=name,
            model=Gemini(id=model_name, temperature=temperature),
            instructions=instructions,
            debug_mode=True
        )
    
    def run(self, prompt: str) -> Any:
        """
        Run the agent with the given prompt
        
        Args:
            prompt: The prompt to send to the agent
            
        Returns:
            The response from the agent
        """
        try:
            return self.agent.run(prompt)
        except Exception as e:
            self.logger.error(f"Error running agent {self.name}: {e}", exc_info=True)
            raise
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """
        Format context information for inclusion in prompts
        
        Args:
            context: Dictionary of context information
            
        Returns:
            Formatted context string
        """
        if not context:
            return ""
        
        result = "Context Information:\n"
        for key, value in context.items():
            result += f"- {key}: {value}\n"
        return result + "\n"

class AgentRegistry:
    """
    Registry for all agents in the system.
    Allows agents to discover and communicate with each other.
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("AgentRegistry")
    
    def register(self, agent: BaseAgent) -> None:
        """Register an agent with the registry"""
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    def get(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all registered agents"""
        return list(self.agents.keys())

# Global agent registry
registry = AgentRegistry() 