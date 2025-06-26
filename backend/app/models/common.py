from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Dict, Any, Union, Annotated
import re

# ==============================================================================
# Base Models with Enhanced Validation
# ==============================================================================

class FlexibleModel(BaseModel):
    """Base model with configuration for maximum flexibility"""
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    @classmethod
    def normalize_string(cls, value: str) -> str:
        """Normalize strings by removing extra whitespace and standardizing format"""
        if not value:
            return value
        # Replace multiple spaces with single space
        value = re.sub(r'\s+', ' ', value.strip())
        return value

# ==============================================================================
# Enhanced Exercise Model
# ==============================================================================

class ExerciseQuantity(FlexibleModel):
    """Flexible representation of exercise quantities (reps, sets, duration)"""
    value: Union[int, float, str]
    unit: Optional[str] = None
    
    @field_validator('value')
    @classmethod
    def parse_value(cls, v):
        """Convert string representations to appropriate types when possible"""
        if isinstance(v, str):
            # Try to extract numeric part from strings like "30 seconds"
            match = re.match(r'^(\d+(?:\.\d+)?)\s*(.*)$', v)
            if match:
                number, unit = match.groups()
                try:
                    return float(number) if '.' in number else int(number)
                except ValueError:
                    pass
        return v
    
    def __str__(self) -> str:
        """String representation for display"""
        if self.unit:
            return f"{self.value} {self.unit}"
        return str(self.value)

class Exercise(FlexibleModel):
    """
    Enhanced model for exercises with better parsing of quantities
    """
    name: str = Field(..., description="Name of the exercise")
    
    # Duration fields with flexible parsing
    duration: Optional[Union[ExerciseQuantity, int, float, str]] = None
    duration_minutes: Optional[Union[int, float, str]] = None
    duration_seconds: Optional[Union[int, float, str]] = None
    
    # Sets and reps with flexible parsing
    sets: Optional[Union[int, str]] = None
    reps: Optional[Union[ExerciseQuantity, int, str]] = None
    
    # Rest periods with flexible parsing
    rest: Optional[Union[ExerciseQuantity, int, str]] = None
    rest_seconds: Optional[Union[int, float, str]] = None
    rest_time_seconds: Optional[Union[int, float, str]] = None
    
    # Additional fields
    intensity: Optional[str] = None
    hold_seconds: Optional[Union[int, str]] = None
    per_side: Optional[bool] = None
    notes: Optional[str] = None
    target_areas: Optional[List[str]] = None
    equipment: Optional[List[str]] = None
    difficulty: Optional[str] = None
    variations: Optional[List[str]] = None
    
    @field_validator('name')
    @classmethod
    def normalize_name(cls, v):
        return cls.normalize_string(v)
    
    @field_validator('notes')
    @classmethod
    def normalize_notes(cls, v):
        return cls.normalize_string(v) if v else v

# ==============================================================================
# Enhanced Meal Models
# ==============================================================================

class NutritionalInfo(FlexibleModel):
    """Detailed nutritional information for food items"""
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None
    
    # Allow additional nutrients
    model_config = ConfigDict(extra="allow")

class MealItem(FlexibleModel):
    """Enhanced model for individual food items"""
    item: Optional[str] = Field(None, description="Name of the food item")
    food: Optional[str] = None  # Alternative field name
    quantity: Optional[str] = None
    serving_size: Optional[str] = None
    preparation: Optional[str] = None
    nutrition: Optional[NutritionalInfo] = None
    alternatives: Optional[List[str]] = None
    
    def __str__(self) -> str:
        """String representation for display"""
        parts = []
        name = self.item or self.food or ""
        if name:
            parts.append(name)
        if self.quantity:
            parts.append(f"({self.quantity})")
        if self.preparation:
            parts.append(f"- {self.preparation}")
        return " ".join(parts)
    
    @field_validator('item', 'food')
    @classmethod
    def normalize_item(cls, v):
        return cls.normalize_string(v) if v else v

class Meal(FlexibleModel):
    """
    Enhanced flexible model for meals with better handling of various formats
    """
    # Accept common variations for the meal title
    meal_type: Optional[str] = Field(None, alias="meal_time")
    meal_time: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    time: Optional[str] = None
    
    # Accept common variations for food lists
    food_items: Optional[List[Union[str, Dict, MealItem]]] = Field(None, alias="items")
    items: Optional[List[Union[str, Dict, MealItem]]] = Field(None, alias="options")
    options: Optional[List[Union[str, Dict, MealItem]]] = Field(None, alias="foods")
    foods: Optional[List[Union[str, Dict, MealItem]]] = None
    
    # Nutritional information
    calories: Optional[float] = None
    macros: Optional[Dict[str, float]] = None
    nutrition: Optional[NutritionalInfo] = None
    
    # Additional information
    notes: Optional[str] = None
    preparation_notes: Optional[str] = None
    timing: Optional[str] = None
    
    def get_name(self) -> str:
        """Return a user-friendly label for rendering"""
        for field in [self.meal_type, self.meal_time, self.type, self.name, self.time]:
            if field:
                return field
        return "Meal"
    
    def get_items(self) -> List[Union[str, MealItem]]:
        """Get food items from any of the possible fields"""
        for field in [self.food_items, self.items, self.options, self.foods]:
            if field:
                return field
        return []
    
    @field_validator('meal_type', 'meal_time', 'type', 'name', 'time')
    @classmethod
    def normalize_meal_name(cls, v):
        return cls.normalize_string(v) if v else v 