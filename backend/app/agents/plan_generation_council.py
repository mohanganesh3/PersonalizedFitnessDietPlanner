from agno.agent import Agent
from agno.models.google import Gemini
from typing import Dict, Any, List, Optional, Union
import json
import logging
from app.utils import robust_json_parser
from app.models import DietPlan, FitnessPlan, UserProfile

logger = logging.getLogger(__name__)

class DietPlanCreatorAgent(Agent):
    """Creates personalized diet plans based on user profile."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-lite"):
        super().__init__(
            name="DietPlanCreator",
            model=Gemini(id=model_name, temperature=0.7),
            instructions="""
            You are a Diet Plan Creator specializing in personalized nutrition planning.
            
            ## Your Expertise:
            - Evidence-based nutritional science
            - Personalized meal planning
            - Dietary pattern optimization
            - Nutritional requirements for various health goals
            
            ## User Profile Considerations:
            - Age, weight, height, activity level
            - Dietary preferences (vegan, keto, etc.)
            - Food allergies and restrictions
            - Fitness goals (weight loss, muscle gain, maintenance)
            - Health conditions (diabetes, hypertension, etc.)
            
            ## Diet Plan Components:
            1. **Overall Goal**: Clear statement of the nutritional objective
            2. **Caloric Targets**: Daily calorie goals based on user metrics
            3. **Macronutrient Distribution**: Protein, carbs, fats percentages
            4. **Meal Structure**: Number of meals, timing recommendations
            5. **Food Recommendations**: Specific foods to emphasize or limit
            6. **Sample Meal Plan**: Detailed daily or weekly meal suggestions
            7. **Practical Tips**: Shopping, preparation, and adherence advice
            
            ## Response Format:
            Your response MUST be a single, valid JSON object matching this structure:
            
            ```json
            {
              "goal": "Primary nutritional goal",
              "description": "Brief overview of the approach",
                "duration_days": 7,
              "daily_calorie_target": 2000,
              "macros": {"protein": 30, "carbs": 40, "fats": 30},
              "daily_structure": {
                "meals_per_day": 4,
                "meal_timing": "Every 3-4 hours"
              },
              "foods_to_emphasize": [
                "Lean proteins (chicken, fish, tofu)",
                "Leafy greens",
                "Complex carbohydrates"
              ],
              "foods_to_limit": [
                "Processed foods",
                "Added sugars",
                "Refined carbohydrates"
              ],
              "weekly_meal_plan": {
                "Monday": {
                  "Breakfast": {
                    "items": ["Oatmeal with berries", "Greek yogurt"],
                    "notes": "Prep ahead for convenience"
                  },
                  "Lunch": {
                    "items": ["Grilled chicken salad", "Whole grain roll"],
                    "notes": "Pack dressing separately"
                  }
                }
              },
              "hydration": "Drink 8-10 glasses of water daily",
              "notes": "Adjust portions based on hunger levels"
            }
            ```
            
            ## Critical Rules:
            1. Provide SPECIFIC, ACTIONABLE advice (not vague guidelines)
            2. Include realistic, practical meal suggestions
            3. Consider the user's full profile when making recommendations
            4. Structure your response EXACTLY as specified - valid JSON only
            5. Do NOT include markdown code fences or any text outside the JSON
            """,
            debug_mode=True
        )
    
    def create_diet_plan(self, user_profile: Dict[str, Any], goal: str) -> Dict[str, Any]:
        """
        Generate a personalized diet plan based on user profile and goal.
        
        Args:
            user_profile: User characteristics and preferences
            goal: The primary nutritional/dietary goal
            
        Returns:
            Dict containing the structured diet plan
        """
        # Format the user profile for the prompt
        profile_str = json.dumps(user_profile, indent=2) if user_profile else "No profile information available"
        
        prompt = f"""
        Create a personalized diet plan based on this user profile:
        
        {profile_str}
        
        Primary Goal: {goal}
        
        Provide a comprehensive 7-day diet plan with specific meals, portions, and nutritional information.
        Include practical tips for meal preparation and adherence.
        Ensure your response is a valid JSON object following the exact structure specified in your instructions.
        """
        
        try:
            response = self.run(prompt)
            result = robust_json_parser(response.messages[-1].content)
            
            # Validate the response structure
            required_keys = ["goal", "daily_calorie_target"]
            if not all(key in result for key in required_keys):
                logger.warning(f"Diet plan missing required keys: {[k for k in required_keys if k not in result]}")
                result = self._create_fallback_diet_plan(goal, user_profile)
            
            # Try to validate with our model
            try:
                diet_plan = DietPlan.model_validate(result)
                return diet_plan.model_dump(exclude_none=True)
            except Exception as e:
                logger.warning(f"Diet plan validation error: {e}")
                return result
                
        except Exception as e:
            logger.error(f"Error creating diet plan: {e}", exc_info=True)
            return self._create_fallback_diet_plan(goal, user_profile)
    
    def _create_fallback_diet_plan(self, goal: str, user_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a simplified but useful diet plan when the main generation fails.
        
        Args:
            goal: The primary nutritional goal
            user_profile: Optional user profile data
            
        Returns:
            Dict containing a basic diet plan
        """
        # Extract basic info from profile if available
        is_vegetarian = False
        is_low_carb = False
        calorie_level = "moderate"
        
        if user_profile:
            if "dietary_preferences" in user_profile:
                prefs = [p.lower() for p in user_profile["dietary_preferences"]] if isinstance(user_profile["dietary_preferences"], list) else []
                is_vegetarian = any(p in ["vegetarian", "vegan"] for p in prefs)
                is_low_carb = any(p in ["keto", "low carb", "low-carb"] for p in prefs)
            
            # Estimate calorie level based on profile
            if "activity_level" in user_profile:
                activity = user_profile.get("activity_level", "").lower()
                if activity in ["sedentary", "light"]:
                    calorie_level = "lower"
                elif activity in ["active", "very active"]:
                    calorie_level = "higher"
        
        # Build a basic plan based on extracted info
        protein_sources = ["Tofu", "Lentils", "Beans", "Greek yogurt"] if is_vegetarian else ["Chicken breast", "Fish", "Lean beef", "Eggs"]
        carb_sources = ["Berries", "Non-starchy vegetables"] if is_low_carb else ["Brown rice", "Sweet potatoes", "Quinoa", "Oatmeal"]
        
        return {
            "goal": goal or "Balanced nutrition for general health",
            "description": "A simplified nutritional approach focusing on whole foods and balanced meals",
                "duration_days": 7,
            "daily_calorie_target": 1800 if calorie_level == "lower" else (2200 if calorie_level == "higher" else 2000),
                "meals": [
                    {
                        "meal_type": "Breakfast",
                    "food_items": ["Oatmeal with berries", "Greek yogurt"] if not is_low_carb else ["Eggs with avocado", "Spinach"],
                    "notes": "Focus on protein and fiber for sustained energy"
                },
                {
                    "meal_type": "Lunch",
                    "food_items": ["Large salad with " + protein_sources[0], "Olive oil dressing"],
                    "notes": "Include plenty of colorful vegetables"
                },
                {
                    "meal_type": "Dinner",
                    "food_items": [protein_sources[1], carb_sources[0], "Steamed vegetables"],
                    "notes": "Balance protein, carbs, and healthy fats"
                }
            ],
            "foods_to_emphasize": [
                "Whole, unprocessed foods",
                "Lean proteins: " + ", ".join(protein_sources),
                "Complex carbohydrates: " + ", ".join(carb_sources),
                "Healthy fats: Avocado, olive oil, nuts"
            ],
            "notes": "This is a simplified plan. For optimal results, consider consulting with a registered dietitian."
        }


class FitnessPlanCreatorAgent(Agent):
    """Creates personalized fitness plans based on user profile."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-lite"):
        super().__init__(
            name="FitnessPlanCreator",
            model=Gemini(id=model_name, temperature=0.7),
            instructions="""
            You are a Fitness Plan Creator specializing in personalized exercise programming.
            
            ## Your Expertise:
            - Exercise physiology and biomechanics
            - Progressive training methodologies
            - Periodization and program design
            - Injury prevention and rehabilitation
            
            ## User Profile Considerations:
            - Current fitness level and experience
            - Age, weight, and physical limitations
            - Available equipment and environment
            - Time constraints and preferences
            - Specific goals (strength, weight loss, etc.)
            
            ## Fitness Plan Components:
            1. **Overall Goal**: Clear statement of the fitness objective
            2. **Program Structure**: Weekly schedule and workout splits
            3. **Exercise Selection**: Specific movements with proper form cues
            4. **Progressive Overload**: How to advance over time
            5. **Recovery Strategies**: Rest days and active recovery
            6. **Warm-up and Cool-down**: Proper preparation and recovery
            7. **Tracking Methods**: How to monitor progress
            
            ## Response Format:
            Your response MUST be a single, valid JSON object matching this structure:
            
            ```json
            {
                "goal": "Primary fitness goal",
              "description": "Brief overview of the approach",
                "duration_weeks": 4,
              "frequency_per_week": 4,
              "session_duration_minutes": 45,
              "equipment_needed": ["Dumbbells", "Resistance bands", "Yoga mat"],
                "workout_schedule": [
                    {
                        "day": "Monday",
                  "focus": "Upper Body Strength",
                  "warm_up": {
                    "duration": "5-10 minutes",
                    "exercises": [
                      {"name": "Arm circles", "duration": "30 seconds"},
                      {"name": "Jumping jacks", "duration": "1 minute"}
                    ]
                  },
                        "exercises": [
                            {
                                "name": "Push-ups",
                                "sets": 3,
                                "reps": "8-12",
                      "rest_seconds": 60,
                      "notes": "Focus on proper form",
                      "target_areas": ["chest", "shoulders", "triceps"]
                    }
                  ],
                  "cool_down": "5 minutes of static stretching"
                }
              ],
              "progression_guidelines": [
                "Increase weight by 5% when you can complete all sets and reps with good form",
                "Add one rep per set each week until reaching the upper rep range"
              ],
              "rest_days_recommendation": "Take at least 2 full rest days per week",
              "notes": "Listen to your body and adjust intensity as needed"
            }
            ```
            
            ## Critical Rules:
            1. Provide SPECIFIC, ACTIONABLE workout details (not vague guidelines)
            2. Include proper exercise form cues and safety considerations
            3. Consider the user's full profile when designing the program
            4. Structure your response EXACTLY as specified - valid JSON only
            5. Do NOT include markdown code fences or any text outside the JSON
            """,
            debug_mode=True
        )
    
    def create_fitness_plan(self, user_profile: Dict[str, Any], goal: str) -> Dict[str, Any]:
        """
        Generate a personalized fitness plan based on user profile and goal.
        
        Args:
            user_profile: User characteristics and preferences
            goal: The primary fitness goal
            
        Returns:
            Dict containing the structured fitness plan
        """
        # Format the user profile for the prompt
        profile_str = json.dumps(user_profile, indent=2) if user_profile else "No profile information available"
        
        prompt = f"""
        Create a personalized fitness plan based on this user profile:
        
        {profile_str}
        
        Primary Goal: {goal}
        
        Provide a comprehensive workout program with specific exercises, sets, reps, and progression guidelines.
        Include warm-up and cool-down protocols, as well as rest and recovery recommendations.
        Ensure your response is a valid JSON object following the exact structure specified in your instructions.
        """
        
        try:
            response = self.run(prompt)
            result = robust_json_parser(response.messages[-1].content)
            
            # Validate the response structure
            required_keys = ["goal", "workout_schedule", "frequency_per_week"]
            if not all(key in result for key in required_keys):
                logger.warning(f"Fitness plan missing required keys: {[k for k in required_keys if k not in result]}")
                result = self._create_fallback_fitness_plan(goal, user_profile)
            
            # Try to validate with our model
            try:
                fitness_plan = FitnessPlan.model_validate(result)
                return fitness_plan.model_dump(exclude_none=True)
            except Exception as e:
                logger.warning(f"Fitness plan validation error: {e}")
                return result
                
        except Exception as e:
            logger.error(f"Error creating fitness plan: {e}", exc_info=True)
            return self._create_fallback_fitness_plan(goal, user_profile)
    
    def _create_fallback_fitness_plan(self, goal: str, user_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a simplified but useful fitness plan when the main generation fails.
        
        Args:
            goal: The primary fitness goal
            user_profile: Optional user profile data
            
        Returns:
            Dict containing a basic fitness plan
        """
        # Extract basic info from profile if available
        fitness_level = "beginner"
        has_equipment = False
        has_limitations = False
        
        if user_profile:
            if "fitness_level" in user_profile:
                fitness_level = user_profile["fitness_level"]
            if "available_equipment" in user_profile and user_profile["available_equipment"]:
                has_equipment = True
            if "physical_limitations" in user_profile and user_profile["physical_limitations"]:
                has_limitations = True
        
        # Adjust workout based on extracted info
        frequency = 3
        duration = 30
        
        # Basic bodyweight exercises most people can do
        basic_exercises = [
            {
                "name": "Modified Push-ups" if has_limitations else "Push-ups",
                "sets": 2 if fitness_level == "beginner" else 3,
                "reps": "5-8" if fitness_level == "beginner" else "8-12",
                "rest_seconds": 60,
                "notes": "Keep core engaged throughout the movement",
                "target_areas": ["chest", "shoulders", "triceps"]
            },
            {
                "name": "Bodyweight Squats",
                "sets": 2 if fitness_level == "beginner" else 3,
                "reps": "10-12" if fitness_level == "beginner" else "12-15",
                "rest_seconds": 60,
                "notes": "Keep weight in heels, knees tracking over toes",
                "target_areas": ["quadriceps", "glutes", "hamstrings"]
            },
            {
                "name": "Plank",
                "sets": 2,
                "duration": "20 seconds" if fitness_level == "beginner" else "30-45 seconds",
                "rest_seconds": 45,
                "notes": "Maintain neutral spine position",
                "target_areas": ["core", "shoulders"]
            }
        ]
        
        # Add equipment-based exercise if available
        if has_equipment:
            basic_exercises.append({
                "name": "Dumbbell Rows",
                "sets": 2 if fitness_level == "beginner" else 3,
                "reps": "8-10" if fitness_level == "beginner" else "10-12",
                "rest_seconds": 60,
                "notes": "Keep back straight, pull elbow back",
                "target_areas": ["back", "biceps"]
            })
        
            return {
            "goal": goal or "General fitness improvement",
            "description": "A simplified full-body workout routine focusing on fundamental movement patterns",
                "duration_weeks": 4,
            "frequency_per_week": frequency,
            "session_duration_minutes": duration,
            "equipment_needed": ["Dumbbells", "Exercise mat"] if has_equipment else ["None required", "Exercise mat (optional)"],
                "workout_schedule": [
                    {
                        "day": "Monday",
                "focus": "Cardiovascular Endurance & Light Strength",
                "warm_up": {
                    "duration": "5 minutes",
                    "exercises": [
                        {"name": "Marching in place", "duration": "1 minute"},
                        {"name": "Arm circles (forward and backward)", "duration": "1 minute"},
                        {"name": "Leg swings (forward/backward and side-to-side)", "duration": "1 minute"},
                        {"name": "Torso twists", "duration": "1 minute"},
                        {"name": "Light jogging in place", "duration": "1 minute"}
                    ]
                },
                        "exercises": [
                    {
                        "name": "Brisk Walking",
                        "sets": 1,
                        "reps": "20 minutes",
                        "rest_seconds": 0,
                        "notes": "Maintain a pace where you can talk but not sing. Focus on maintaining good posture.",
                        "target_areas": ["cardiovascular system", "legs", "glutes"]
                    },
                            {
                                "name": "Bodyweight Squats",
                                "sets": 3,
                        "reps": "10-12",
                        "rest_seconds": 60,
                        "notes": "Keep your chest up, back straight, and descend as if sitting into a chair. Ensure knees track over toes.",
                        "target_areas": ["quadriceps", "hamstrings", "glutes"]
                    },
                    {
                        "name": "Wall Push-ups",
                        "sets": 3,
                        "reps": "10-12",
                        "rest_seconds": 60,
                        "notes": "Stand facing a wall, place hands shoulder-width apart on the wall. Lower your chest towards the wall, keeping your body in a straight line.",
                        "target_areas": ["chest", "shoulders", "triceps"]
                    }
                ],
                "cool_down": "5 minutes of static stretching, holding each stretch for 20-30 seconds. Focus on quadriceps, hamstrings, calves, chest, and triceps."
                },
                {
                "day": "Tuesday",
                "focus": "Rest Day",
                "description": "Rest day to allow your body to recover from Monday's workout. Light stretching or a gentle walk is acceptable if desired.",
                "exercises": [
                    {
                        "name": "Rest & Recovery",
                        "notes": "Take this day off from structured exercise to allow your muscles to recover and adapt. Stay hydrated and focus on good nutrition."
                    }
                ],
                "optional_activities": "Light stretching (5-10 minutes) or a very short, easy walk if desired."
                },
                {
                "day": "Wednesday",
                "focus": "Cardiovascular Endurance & Core Strength",
                "warm_up": {
                    "duration": "5 minutes",
                    "exercises": [
                        {"name": "Marching in place", "duration": "1 minute"},
                        {"name": "Arm circles (forward and backward)", "duration": "1 minute"},
                        {"name": "Leg swings (forward/backward and side-to-side)", "duration": "1 minute"},
                        {"name": "Torso twists", "duration": "1 minute"},
                        {"name": "Light jogging in place", "duration": "1 minute"}
                    ]
                },
                "exercises": [
                    {
                        "name": "Brisk Walking",
                        "sets": 1,
                        "reps": "20 minutes",
                        "rest_seconds": 0,
                        "notes": "Focus on maintaining a consistent, moderate intensity.",
                        "target_areas": ["cardiovascular system", "legs", "glutes"]
                    },
                    {
                        "name": "Plank",
                        "sets": 3,
                        "reps": "Hold for 20-30 seconds",
                        "rest_seconds": 60,
                        "notes": "Maintain a straight line from head to heels, engaging your core. Avoid letting your hips sag or rise too high.",
                        "target_areas": ["core", "abs", "back"]
                    },
                    {
                        "name": "Glute Bridges",
                        "sets": 3,
                        "reps": "12-15",
                        "rest_seconds": 60,
                        "notes": "Lie on your back with knees bent and feet flat on the floor. Lift your hips off the ground, squeezing your glutes at the top.",
                        "target_areas": ["glutes", "hamstrings", "lower back"]
                    }
                ],
                "cool_down": "5 minutes of static stretching, holding each stretch for 20-30 seconds. Focus on hip flexors, hamstrings, glutes, and back."
                },
                {
                "day": "Thursday",
                "focus": "Rest Day",
                "description": "Rest day to allow your body to recover from Wednesday's workout. Light stretching or a gentle walk is acceptable if desired.",
                "exercises": [
                    {
                        "name": "Rest & Recovery",
                        "notes": "Take this day off from structured exercise to allow your muscles to recover and adapt. Stay hydrated and focus on good nutrition."
                    }
                ],
                "optional_activities": "Light stretching (5-10 minutes) or a very short, easy walk if desired."
                },
                {
                "day": "Friday",
                "focus": "Cardiovascular Endurance & Full Body Integration",
                "warm_up": {
                    "duration": "5 minutes",
                    "exercises": [
                        {"name": "Marching in place", "duration": "1 minute"},
                        {"name": "Arm circles (forward and backward)", "duration": "1 minute"},
                        {"name": "Leg swings (forward/backward and side-to-side)", "duration": "1 minute"},
                        {"name": "Torso twists", "duration": "1 minute"},
                        {"name": "Light jogging in place", "duration": "1 minute"}
                    ]
                },
                "exercises": [
                    {
                        "name": "Brisk Walking",
                        "sets": 1,
                        "reps": "20 minutes",
                        "rest_seconds": 0,
                        "notes": "Consider a slightly varied route or incline if available to challenge yourself.",
                        "target_areas": ["cardiovascular system", "legs", "glutes"]
                    },
                    {
                        "name": "Lunges (alternating legs)",
                        "sets": 3,
                        "reps": "8-10 per leg",
                        "rest_seconds": 60,
                        "notes": "Step forward with one leg, lowering your hips until both knees are bent at a 90-degree angle. Ensure front knee stays over ankle and back knee hovers above ground.",
                        "target_areas": ["quadriceps", "hamstrings", "glutes", "balance"]
                    },
                    {
                        "name": "Bird Dog",
                        "sets": 3,
                        "reps": "10-12 per side",
                        "rest_seconds": 60,
                        "notes": "Start on all fours. Extend opposite arm and leg simultaneously, keeping your core engaged and back flat. Return to start and switch sides.",
                        "target_areas": ["core", "back", "glutes", "balance"]
                    }
                ],
                "cool_down": "5 minutes of static stretching, holding each stretch for 20-30 seconds. Focus on quadriceps, hamstrings, glutes, hips, and back."
                },
                {
                "day": "Saturday",
                "focus": "Rest Day",
                "description": "Rest day to allow your body to recover from Friday's workout. Light stretching or a gentle walk is acceptable if desired.",
                "exercises": [
                    {
                        "name": "Rest & Recovery",
                        "notes": "Take this day off from structured exercise to allow your muscles to recover and adapt. Stay hydrated and focus on good nutrition."
                    }
                ],
                "optional_activities": "Light stretching (5-10 minutes) or a very short, easy walk if desired."
                },
                {
                "day": "Sunday",
                "focus": "Rest Day",
                "description": "Complete rest day to ensure full recovery before starting the next week's workouts. Focus on relaxation and preparation for the week ahead.",
                "exercises": [
                    {
                        "name": "Complete Rest & Recovery",
                        "notes": "Take this day off from all exercise to ensure full recovery. Focus on relaxation, good nutrition, and adequate sleep to prepare for the next week."
                    }
                ],
                "optional_activities": "Gentle stretching if desired, but primarily focus on rest."
                }
            ],
            "progression_guidelines": [
                "Weeks 1-2: Focus on establishing consistency and proper form. Complete the prescribed sets and reps.",
                "Weeks 3-4: If the current reps feel comfortable for all sets, aim to increase reps by 2-3 per set, or increase the duration of the plank hold by 5-10 seconds. For walking, aim to increase pace slightly or add small inclines if available."
            ],
            "rest_days_recommendation": "Take at least 2 full rest days per week. Active recovery like light stretching or very gentle walking on rest days is permissible if desired, but prioritize listening to your body.",
            "notes": "This plan is designed as a starting point. It's crucial to consult with a healthcare provider before beginning any new exercise program, especially with pre-existing health conditions. Pay attention to how your body feels and adjust intensity or rest as needed. Consistency is key for managing health conditions and achieving fitness goals. Combine this plan with the recommended dietary changes for optimal results."
        }


class PlanGenerationCouncilAgent(Agent):
    """
    Orchestrates the creation of comprehensive health and fitness plans by coordinating
    specialized sub-agents for diet and fitness planning.
    """
    
    def __init__(self, model_name: str):
        super().__init__(
            name="PlanGenerationCouncilAgent",
            model=Gemini(id=model_name, temperature=0.4),
            instructions="""
            You are the Plan Generation Council, responsible for coordinating the creation of 
            personalized health and fitness plans. You analyze user requests and delegate to 
            specialized agents to create comprehensive, tailored plans.
            
            ## Your Responsibilities:
            1. Analyze user intent to determine what types of plans are needed
            2. Extract key goals and requirements from user requests
            3. Coordinate between diet and fitness planning specialists
            4. Ensure plans are complementary and aligned with user goals
            5. Identify when a user request is too vague and needs clarification
            
            ## Output Format:
            Your response MUST be a single, valid JSON object with this structure:
            
            ```json
            {
              "analysis": {
                "primary_goal": "Main user objective",
                "plan_types_needed": ["diet", "fitness"],
                "key_requirements": ["low impact", "vegetarian", "time-efficient"],
                "clarity_score": 0.8
              },
              "diet_goal": "Specific goal for diet plan",
              "fitness_goal": "Specific goal for fitness plan"
            }
            ```
            
            ## Critical Rules:
            1. Focus ONLY on analyzing the request and setting goals
            2. Do NOT generate any actual diet or fitness plans yourself
            3. If the user request is unclear (clarity_score < 0.6), identify what information is missing
            4. Structure your response EXACTLY as specified - valid JSON only
            5. Do NOT include markdown code fences or any text outside the JSON
            """,
            debug_mode=True
        )
        
        # Initialize sub-agents
        self.diet_agent = DietPlanCreatorAgent(model_name)
        self.fitness_agent = FitnessPlanCreatorAgent(model_name)
    
    def generate_plans(self, intent_analysis: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes user intent and generates appropriate health and fitness plans.
        
        Args:
            intent_analysis: Analysis of the user's request
            user_profile: User characteristics and preferences
            
        Returns:
            Dict containing diet and/or fitness plans based on the user's needs
        """
        # First, analyze what types of plans are needed
        prompt = f"""
        Analyze this user request and determine what types of plans are needed:
        
        User Request: "{intent_analysis}"
        
        User Profile: {json.dumps(user_profile, indent=2) if user_profile else "No profile information available"}
        
        Determine if the user needs a diet plan, fitness plan, or both.
        Identify the primary goal for each plan type needed.
        Assess how clear the request is on a scale of 0.0 to 1.0.
        """
        
        try:
            response = self.run(prompt)
            analysis = robust_json_parser(response.messages[-1].content)
            
            # Extract plan types and goals
            plan_types = analysis.get("analysis", {}).get("plan_types_needed", [])
            diet_goal = analysis.get("diet_goal", "")
            fitness_goal = analysis.get("fitness_goal", "")
            clarity_score = analysis.get("analysis", {}).get("clarity_score", 0.0)
            
            # Initialize response dictionary
            plans_response = {
                "analysis": analysis.get("analysis", {})
            }
            
            # If request is unclear, return analysis without generating plans
            if clarity_score < 0.6:
                plans_response["status"] = "unclear_request"
                plans_response["missing_information"] = analysis.get("analysis", {}).get("missing_information", [])
                return plans_response
            
            # Generate requested plans
            if "diet" in plan_types and diet_goal:
                diet_plan = self.diet_agent.create_diet_plan(user_profile, diet_goal)
                plans_response["diet_plan"] = diet_plan
            
            if "fitness" in plan_types and fitness_goal:
                fitness_plan = self.fitness_agent.create_fitness_plan(user_profile, fitness_goal)
                plans_response["fitness_plan"] = fitness_plan
            
            return plans_response
            
        except Exception as e:
            logger.error(f"Error in plan generation: {e}", exc_info=True)
            # Provide a basic response with minimal plans
            return {
                "status": "error",
                "message": "An error occurred during plan generation",
                "diet_plan": self.diet_agent._create_fallback_diet_plan("General health improvement", user_profile),
                "fitness_plan": self.fitness_agent._create_fallback_fitness_plan("General fitness improvement", user_profile)
            }
    
    def refine_plan(self, plan_type: str, current_plan: Dict[str, Any], user_feedback: str) -> Dict[str, Any]:
        """
        Refines an existing plan based on user feedback.
        
        Args:
            plan_type: Type of plan to refine ('diet' or 'fitness')
            current_plan: The existing plan
            user_feedback: User's feedback on the plan
            
        Returns:
            Dict containing the refined plan
        """
        if plan_type.lower() == "diet":
            agent = self.diet_agent
        elif plan_type.lower() == "fitness":
            agent = self.fitness_agent
        else:
            raise ValueError(f"Invalid plan type: {plan_type}")
        
        prompt = f"""
        Refine this {plan_type} plan based on the user's feedback:
        
        Current Plan:
        {json.dumps(current_plan, indent=2)}
        
        User Feedback:
        "{user_feedback}"
        
        Create an improved version of the plan that addresses the user's concerns while maintaining the overall structure.
        Ensure your response is a valid JSON object following the exact structure of the current plan.
        """
        
        try:
            response = agent.run(prompt)
            refined_plan = robust_json_parser(response.messages[-1].content)
            
            # Try to validate with our model
            try:
                if plan_type.lower() == "diet":
                    validated_plan = DietPlan.model_validate(refined_plan)
                else:
                    validated_plan = FitnessPlan.model_validate(refined_plan)
                return validated_plan.model_dump(exclude_none=True)
            except Exception as e:
                logger.warning(f"Refined plan validation error: {e}")
                return refined_plan
                
        except Exception as e:
            logger.error(f"Error refining {plan_type} plan: {e}", exc_info=True)
            return current_plan

