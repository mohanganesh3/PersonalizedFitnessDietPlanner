import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from fastapi.security import APIKeyHeader

from app.agents import (
    ChiefStrategistAgent,
    HealthKnowledgeCouncilAgent,
    PlanGenerationCouncilAgent,
    UserProfileAgent,
    registry,
)
from app.agents.mental_wellness_agent import MentalWellnessAgent
from app.models import (
    HealthPlanResponse,
    UserProfile,
    KnowledgeResponse,
    DietPlan,
    FitnessPlan,
)
from app.utils import robust_json_parser, safe_model_parse, extract_user_profile_info, merge_user_profiles, replace_user_profile

# --- Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

# --- Global State ---
agents: Dict[str, Any] = {}
user_profiles: Dict[str, Dict[str, Any]] = {}  # Simple in-memory storage for user profiles

# --- Security ---
API_KEY_NAME = "X-API-Key"
API_KEY = os.getenv("API_KEY", "")  # Default to empty string if not set
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Depends(api_key_header)):
    """Validate API key if enabled"""
    if not API_KEY:  # If no API key is set, authentication is disabled
        return True
    if api_key_header == API_KEY:
        return True
    raise HTTPException(
        status_code=401,
        detail="Invalid API Key",
        headers={"WWW-Authenticate": "API key required"},
    )

# --- FastAPI Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agents on startup and cleanup on shutdown."""
    logger.info("Initializing AI agents...")
    try:
        model_name = os.getenv("MODEL_NAME")
        api_key = os.getenv("GOOGLE_API_KEY")

        if not model_name or not api_key:
            raise ValueError("CRITICAL: GOOGLE_API_KEY and/or MODEL_NAME environment variables are not set.")
        
        genai.configure(api_key=api_key)

        # Initialize the agents with the new agentic architecture
        # The HealthKnowledgeCouncilAgent will automatically initialize and register all expert agents
        agents.update({
            'chief_strategist': ChiefStrategistAgent(model_name),
            'knowledge_council': HealthKnowledgeCouncilAgent(model_name),
            'plan_generator': PlanGenerationCouncilAgent(model_name),
            'user_profile': UserProfileAgent(model_name),
            'mental_wellness': MentalWellnessAgent(model_name),
        })
        
        logger.info(f"Agents initialized successfully: {list(agents.keys())}")
        logger.info(f"All registered agents: {registry.list_agents()}")
        
        yield
    except Exception as e:
        logger.critical(f"Critical error during agent initialization: {e}", exc_info=True)
        # We will now re-raise the exception to prevent the server from starting
        # in a broken state.
        raise
    finally:
        logger.info("Shutting down and clearing agents.")
        agents.clear()

# --- FastAPI App ---
app = FastAPI(
    title="AI Health & Fitness Planner",
    description="A sophisticated multi-agent health and fitness planning system.",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Models ---
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: HealthPlanResponse

# --- Helper Functions ---
def _build_chat_response(
    intent_analysis: str,
    plans: Optional[Dict[str, Any]] = None,
    knowledge: Optional[KnowledgeResponse] = None,
    follow_up_questions: Optional[List[str]] = None,
) -> str:
    """Builds a friendly, natural language summary of the agent outputs."""
    parts = []

    # Clean up the intent_analysis to remove phrases like "user is asking for"
    cleaned_intent = intent_analysis.lower()
    phrases_to_remove = [
        "user is asking for ",
        "user is asking about ",
        "user is inquiring about ",
        "user wants to know about ",
        "user needs information on ",
        "user is requesting ",
        "advice on ",
        "information about "
    ]
    
    for phrase in phrases_to_remove:
        if cleaned_intent.startswith(phrase):
            cleaned_intent = cleaned_intent[len(phrase):]
    
    # Capitalize first letter
    if cleaned_intent:
        cleaned_intent = cleaned_intent[0].upper() + cleaned_intent[1:]

    # Create appropriate response based on content type
    if plans:
        # For plan requests
        parts.append(f"Here's a personalized plan for {cleaned_intent}.")
    elif knowledge:
        # For knowledge queries, don't include any reference to the intent analysis
        # Just provide a direct response
        if follow_up_questions and len(follow_up_questions) > 0:
            # If we have follow-up questions, just add them without a prefix
            for i, question in enumerate(follow_up_questions[:2], 1):
                # Remove question marks and convert to statement
                statement = question.rstrip('?')
                parts.append(f"{i}. {statement}")
            return "\n\nWould you like to know more about:\n" + "\n".join(parts)
        else:
            # If no follow-up questions, return empty string to use the knowledge content directly
            return ""
    else:
        return "How can I help you with your health and fitness goals today?"

    # Add follow-up questions if available
    if follow_up_questions and len(follow_up_questions) > 0:
        parts.append("\n\nWould you like to know more about:")
        for i, question in enumerate(follow_up_questions[:2], 1):
            # Remove question marks and convert to statement
            statement = question.rstrip('?')
            parts.append(f"{i}. {statement}")

    return " ".join(parts)

def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Get user profile from storage or create a new one"""
    if not user_id:
        return {}
    return user_profiles.get(user_id, {})

def update_user_profile(user_id: str, new_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update user profile by clearing old data and adding only new information"""
    if not user_id:
        return new_data
    
    # Completely replace the profile with new data (ignore old profile)
    user_profiles[user_id] = new_data.copy()
    return user_profiles[user_id]

# --- API Endpoints ---
@app.get("/", summary="Root endpoint")
async def root():
    return {"message": "AI Health & Fitness Planner API", "status": "active", "version": "3.0.0"}

@app.get("/health", summary="Health check")
async def health_check():
    return {"status": "healthy", "agents_initialized": bool(agents)}

@app.post("/chat", response_model=ChatResponse, summary="Main chat endpoint", dependencies=[Depends(get_api_key)])
async def chat_endpoint(request: ChatRequest):
    """
    Processes a user message through the multi-agent system to generate a health and fitness response.
    """
    if not agents:
        raise HTTPException(
            status_code=503,
            detail="The AI agents are not available. Please check the server logs."
        )
    
    try:
        # Get user profile if user_id provided
        user_id = request.user_id or "anonymous"
        current_profile = get_user_profile(user_id)
        
        # 1. STRATEGIZE: Determine the user's intent with the chief strategist
        strategy = agents['chief_strategist'].analyze_query(
            request.message, 
            current_profile=current_profile
        )
        logger.info(f"Strategy Determined: {strategy}")

        # 2. PROFILE: Extract and update user profile information if needed
        updated_profile = current_profile
        if strategy.get("profile_extraction_needed", False):
            profile_result = agents['user_profile'].extract_profile_info(
                request.message, 
                existing_profile=current_profile
            )
            updated_profile = update_user_profile(user_id, profile_result["profile"])
            logger.info(f"Updated profile with new information: {profile_result['new_information']}")

        # 3. RESPOND: Handle immediate responses (greetings, off-topic)
        if strategy.get("next_action") == "immediate_response":
            response = HealthPlanResponse(
                chat_response=strategy.get("response", "I can only assist with health and fitness topics."),
                user_profile_updates=updated_profile if updated_profile != current_profile else None,
                follow_up_questions=strategy.get("follow_up_suggestions", [])
            )
            return ChatResponse(response=response)

        # 4. Check for stress management or relief exercises queries
        intent = strategy.get("intent_analysis", "").lower()
        if "stress" in intent or "relief" in intent or "relax" in intent or "anxiety" in intent:
            # Use the specialized mental wellness agent
            if "relief exercises" in request.message.lower() or "stress relief" in request.message.lower():
                chat_response = agents['mental_wellness'].get_relief_exercises(
                    request.message,
                    user_profile=updated_profile
                )
            else:
                chat_response = agents['mental_wellness'].provide_stress_management_guidance(
                    request.message,
                    user_profile=updated_profile
                )
            
            # Generate follow-up questions
            follow_up_questions = agents['chief_strategist'].generate_follow_up_questions(
                request.message, 
                {"has_knowledge": True},
                user_profile=updated_profile
            )
            
            response = HealthPlanResponse(
                chat_response=chat_response,
                user_profile_updates=updated_profile if updated_profile != current_profile else None,
                follow_up_questions=follow_up_questions,
                disclaimers=["This information is for educational purposes only. If you're experiencing severe stress or anxiety, please consult with a healthcare professional."]
            )
            return ChatResponse(response=response)

        # 5. DELEGATE: Run the required agents
        knowledge: Optional[KnowledgeResponse] = None
        diet_plan: Optional[DietPlan] = None
        fitness_plan: Optional[FitnessPlan] = None
        disclaimers = set()
        follow_up_questions = []

        if "HealthKnowledgeCouncilAgent" in strategy.get("required_agents", []):
            knowledge_data = agents['knowledge_council'].process_knowledge_query(
                request.message, 
                user_profile=updated_profile
            )
            try:
                knowledge = safe_model_parse(KnowledgeResponse, knowledge_data.get("expert_responses", {}))
            except ValueError:
                knowledge = KnowledgeResponse.model_validate(knowledge_data.get("expert_responses", {}))
                
            for d in knowledge_data.get("disclaimers", []):
                disclaimers.add(d)

        if "PlanGenerationCouncilAgent" in strategy.get("required_agents", []):
            plan_data = agents['plan_generator'].generate_plans(
                intent_analysis=strategy["intent_analysis"],
                user_profile=updated_profile
            )
            # Safely validate the received dictionaries into Pydantic models
            try:
                if "diet_plan" in plan_data:
                    diet_plan = safe_model_parse(DietPlan, plan_data["diet_plan"])
            except ValueError as e:
                logger.warning(f"Diet plan validation failed: {e}")
                diet_plan = DietPlan(goal="Validation Error", notes="Could not generate a valid diet plan structure.")

            try:
                if "fitness_plan" in plan_data:
                    fitness_plan = safe_model_parse(FitnessPlan, plan_data["fitness_plan"])
            except ValueError as e:
                logger.warning(f"Fitness plan validation failed: {e}")
                fitness_plan = FitnessPlan(goal="Validation Error", notes="Could not generate a valid fitness plan structure.")
        
        # 6. FOLLOW-UP: Generate follow-up questions
        response_content = {
            "has_diet_plan": bool(diet_plan),
            "has_fitness_plan": bool(fitness_plan),
            "has_knowledge": bool(knowledge)
        }
        follow_up_questions = agents['chief_strategist'].generate_follow_up_questions(
            request.message, 
            response_content,
            user_profile=updated_profile
        )
        
        # 7. ASSEMBLE: Build the final, validated response
        chat_summary = _build_chat_response(
            strategy["intent_analysis"], 
            {"diet": bool(diet_plan), "fitness": bool(fitness_plan)} if diet_plan or fitness_plan else None, 
            knowledge,
            follow_up_questions
        )
        
        # Consolidate all disclaimers
        if knowledge or diet_plan or fitness_plan:
             disclaimers.update([
                "This information is for educational purposes and not a substitute for professional medical advice.",
                "Consult a healthcare provider before starting any new fitness or diet program."
             ])

        response = HealthPlanResponse(
            chat_response=chat_summary,
            diet_plan=diet_plan,
            fitness_plan=fitness_plan,
            knowledge=knowledge,
            disclaimers=sorted(list(disclaimers)),
            user_profile_updates=updated_profile if updated_profile != current_profile else None,
            follow_up_questions=follow_up_questions
        )
        
        return ChatResponse(response=response)

    except ValidationError as e:
        logger.error(f"A Pydantic validation error occurred in the chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"There was a data structure mismatch. Please check the logs. Error: {e}"
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred in /chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An internal server error occurred: {str(e)}"
        )

@app.get("/user_profile/{user_id}", summary="Get user profile", dependencies=[Depends(get_api_key)])
async def get_profile(user_id: str):
    """Get the current user profile"""
    profile = get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return {"user_id": user_id, "profile": profile}

@app.post("/user_profile/{user_id}", summary="Update user profile", dependencies=[Depends(get_api_key)])
async def update_profile(user_id: str, profile_data: Dict[str, Any]):
    """Update the user profile with new information"""
    updated = update_user_profile(user_id, profile_data)
    return {"user_id": user_id, "profile": updated}

# --- Main Execution ---
if __name__ == "__main__":
    import uvicorn
    # This is for local development. For production, use a proper ASGI server like Gunicorn.
    uvicorn.run(app, host="0.0.0.0", port=8000)

