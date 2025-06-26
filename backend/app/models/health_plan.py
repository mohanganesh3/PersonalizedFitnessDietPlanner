from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import List, Optional, Dict, Any, Union, Literal
from .common import Meal, Exercise, FlexibleModel, NutritionalInfo

# ==============================================================================
# Fitness Plan Components
# ==============================================================================

class Circuit(FlexibleModel):
    """A workout circuit with exercises and parameters"""
    name: Optional[str] = None
    circuit_name: Optional[str] = None
    description: Optional[str] = None
    exercises: List[Exercise] = []
    rounds: Optional[Union[int, str]] = None
    rest_between_rounds: Optional[str] = None
    rest_between_rounds_seconds: Optional[int] = None
    duration: Optional[str] = None
    intensity: Optional[str] = None
    target_areas: Optional[List[str]] = None
    
    @model_validator(mode='after')
    def ensure_name(self):
        """Ensure circuit has a name"""
        if not self.name and self.circuit_name:
            self.name = self.circuit_name
        return self

class WorkoutSegment(FlexibleModel):
    """
    Enhanced model for a segment of a workout (day, phase, etc.)
    """
    # Accept common variations for the segment title
    day: Optional[str] = Field(None, alias="phase")
    phase: Optional[str] = None
    type: Optional[str] = None
    activity: Optional[str] = None
    name: Optional[str] = None
    
    # Focus and description
    focus: Optional[str] = None
    description: Optional[str] = None
    
    # Duration information
    duration: Optional[str] = None
    duration_minutes: Optional[int] = None
    
    # Exercises list
    exercises: Optional[List[Exercise]] = None
    
    # Circuit information
    circuits: Optional[List[Circuit]] = None
    workout_circuits: Optional[List[Circuit]] = None
    hiit_circuit: Optional[Circuit] = None
    
    # Warm-up and cool-down
    warm_up: Optional[Union[str, Dict[str, Any]]] = None
    cool_down: Optional[Union[str, Dict[str, Any]]] = None
    
    # Additional fields
    notes: Optional[str] = None
    equipment: Optional[List[str]] = None
    
    def get_title(self) -> str:
        """Get a display title for the segment"""
        for field in [self.day, self.phase, self.type, self.activity, self.name]:
            if field:
                return field
        return "Workout Segment"

# ==============================================================================
# Diet Plan Components
# ==============================================================================

class MealPlanDay(FlexibleModel):
    """A single day in a meal plan"""
    day: str
    meals: List[Meal] = []
    total_calories: Optional[float] = None
    notes: Optional[str] = None
    
    @field_validator('day')
    @classmethod
    def normalize_day(cls, v):
        """Normalize day names"""
        if not v:
            return v
        v = cls.normalize_string(v)
        # Capitalize first letter of each word
        return ' '.join(word.capitalize() for word in v.split())

class NutritionGuidelines(FlexibleModel):
    """Nutritional guidelines and recommendations"""
    daily_calorie_target: Optional[float] = None
    macronutrient_ratio: Optional[Dict[str, Union[float, str]]] = None
    foods_to_emphasize: Optional[List[str]] = None
    foods_to_limit: Optional[List[str]] = None
    meal_timing: Optional[Dict[str, str]] = None
    hydration: Optional[Union[str, Dict[str, Any]]] = None
    supplements: Optional[List[Dict[str, Any]]] = None

# ==============================================================================
# Main Plan Models
# ==============================================================================

class DietPlan(FlexibleModel):
    """
    Enhanced model for diet plans with better structure
    """
    goal: Optional[str] = None
    description: Optional[str] = None
    duration_days: Optional[int] = Field(7, ge=1, le=90)
    
    # Flexible meal structures
    meals: Optional[Union[List[Meal], Dict[str, Any]]] = None
    meal_plan: Optional[Union[List[Meal], Dict[str, Any]]] = None
    sample_daily_menu: Optional[Union[List[Meal], Dict[str, Any]]] = None
    weekly_meal_plan: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None
    weekly_menu: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None
    
    # Nutritional information
    daily_calorie_target: Optional[float] = None
    macros: Optional[Dict[str, float]] = None
    nutrition_guidelines: Optional[NutritionGuidelines] = None
    
    # Daily structure
    daily_structure: Optional[Dict[str, Any]] = None
    
    # Recommendations and guidelines
    general_recommendations: Optional[List[str]] = None
    general_tips: Optional[List[str]] = None
    foods_to_emphasize: Optional[List[str]] = None
    foods_to_limit: Optional[List[str]] = None
    
    # Hydration info
    hydration: Optional[Union[str, Dict[str, Any]]] = None
    
    # Notes
    notes: Optional[str] = None
    
    @field_validator('goal', 'description', 'notes')
    @classmethod
    def normalize_text(cls, v):
        return cls.normalize_string(v) if v else v
    
    @model_validator(mode='after')
    def process_weekly_plan(self):
        """Convert weekly plan to a standardized format if needed"""
        # Implementation would normalize weekly plan formats
        return self

class FitnessPlan(FlexibleModel):
    """
    Enhanced model for fitness plans with better structure
    """
    goal: Optional[str] = None
    description: Optional[str] = None
    
    # Accept common variations for frequency
    frequency: Optional[str] = None
    frequency_per_week: Optional[Union[str, int]] = None

    # Accept common variations for duration
    duration: Optional[str] = None
    duration_minutes: Optional[Union[str, int]] = None
    duration_weeks: Optional[int] = None
    session_duration_minutes: Optional[int] = None

    # Schedule structures
    workout_schedule: Optional[List[WorkoutSegment]] = Field(None, alias="schedule")
    schedule: Optional[List[WorkoutSegment]] = Field(None, alias="structure")
    structure: Optional[Any] = None
    workout_structure: Optional[Dict[str, Any]] = None
    workout_details: Optional[Dict[str, Any]] = None
    workouts: Optional[Dict[str, Any]] = None
    weekly_schedule: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None
    
    # Progression information
    progression: Optional[str] = None
    progression_tips: Optional[List[str]] = None
    progression_recommendations: Optional[List[str]] = None
    progression_guidelines: Optional[List[str]] = None
    
    # Rest and recovery
    rest_days_recommendation: Optional[str] = None
    recovery_strategies: Optional[List[str]] = None
    
    # Equipment and notes
    equipment_needed: Optional[List[str]] = None
    important_notes: Optional[List[str]] = None
    notes: Optional[str] = None
    additional_notes: Optional[str] = None
    
    @field_validator('goal', 'description', 'notes', 'additional_notes')
    @classmethod
    def normalize_text(cls, v):
        return cls.normalize_string(v) if v else v
    
    @model_validator(mode='after')
    def ensure_structure(self):
        """Process workout structure into a consistent format"""
        # Implementation would normalize workout structures
        return self

# ==============================================================================
# Knowledge Response Models
# ==============================================================================

class HealthTopic(FlexibleModel):
    """Model for a specific health topic"""
    title: str
    content: str
    subtopics: Optional[List[Dict[str, str]]] = None
    references: Optional[List[str]] = None
    
    @field_validator('title', 'content')
    @classmethod
    def normalize_text(cls, v):
        return cls.normalize_string(v) if v else v

class KnowledgeResponse(FlexibleModel):
    """Enhanced knowledge response with structured information"""
    general_health: Optional[Union[str, Dict[str, Any], HealthTopic]] = None
    nutrition: Optional[Union[str, Dict[str, Any], HealthTopic]] = None
    fitness: Optional[Union[str, Dict[str, Any], HealthTopic]] = None
    mental_wellness: Optional[Union[str, Dict[str, Any], HealthTopic]] = None
    references: Optional[List[str]] = None

# ==============================================================================
# User Profile and Response Models
# ==============================================================================

class UserProfile(FlexibleModel):
    """Enhanced user profile with more fields and validation"""
    # Basic demographics
    age: Optional[int] = Field(None, ge=13, le=120)
    weight_lbs: Optional[float] = Field(None, gt=0)
    height_inches: Optional[float] = Field(None, gt=0)
    gender: Optional[str] = None
    
    # Fitness information
    activity_level: Optional[Literal["sedentary", "light", "moderate", "active", "very active"]] = None
    fitness_level: Optional[Literal["beginner", "intermediate", "advanced"]] = None
    
    # Goals and preferences
    dietary_preferences: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    fitness_goals: Optional[List[str]] = None
    target_areas: Optional[List[str]] = None
    
    # Health information
    health_conditions: Optional[List[str]] = None
    physical_limitations: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    
    # Lifestyle factors
    sleep_hours: Optional[float] = None
    stress_level: Optional[Literal["low", "moderate", "high"]] = None
    occupation: Optional[str] = None
    
    # Equipment access
    available_equipment: Optional[List[str]] = None
    gym_access: Optional[bool] = None
    
    # Time availability
    available_time_minutes: Optional[int] = None
    preferred_workout_time: Optional[str] = None
    
    @property
    def bmi(self) -> Optional[float]:
        """Calculate BMI if height and weight are available"""
        if self.weight_lbs and self.height_inches and self.height_inches > 0:
            return (self.weight_lbs * 703) / (self.height_inches ** 2)
        return None

class HealthPlanResponse(FlexibleModel):
    """Enhanced response model with more structure"""
    chat_response: str
    diet_plan: Optional[DietPlan] = None
    fitness_plan: Optional[FitnessPlan] = None
    knowledge: Optional[KnowledgeResponse] = None
    disclaimers: List[str] = []
    user_profile_updates: Optional[Dict[str, Any]] = None
    follow_up_questions: Optional[List[str]] = None


