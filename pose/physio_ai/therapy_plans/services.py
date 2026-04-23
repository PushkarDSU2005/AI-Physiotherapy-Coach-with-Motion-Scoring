"""
Therapy Plan Generation Service

This module provides GPT-based generation of personalized physiotherapy plans
based on injury type and user performance history.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal

import openai
from django.contrib.auth.models import User
from django.db import transaction

from exercises.models import Exercise
from analytics.models import UserProgress, DailyMetrics
from therapy_plans.models import TherapyPlan, WeeklyExercise

logger = logging.getLogger(__name__)

# Configure OpenAI
openai.api_key_from_env = True  # Use OPENAI_API_KEY environment variable


class TherapyPlanGenerator:
    """
    Generates personalized therapy plans using GPT-4/GPT-3.5-turbo.
    
    Features:
    - Analyzes injury type and severity
    - Reviews user performance history
    - Generates week-by-week exercise plans
    - Includes progression strategy
    - Provides safety precautions
    """

    # System prompt for GPT
    SYSTEM_PROMPT = """You are an expert physiotherapist AI assistant specializing in creating personalized 
rehabilitation plans. Your role is to generate detailed, safe, and effective therapy plans based on patient 
injury information and performance history.

Key principles:
1. Safety first - always include appropriate precautions
2. Progressive loading - start conservative, gradually increase intensity
3. Evidence-based exercises - recommend clinically proven movements
4. Personalization - adapt based on patient's fitness level and history
5. Achievability - set realistic goals that maintain patient motivation

Always structure your response as valid JSON."""

    def __init__(self, user: User):
        """Initialize the plan generator for a specific user."""
        self.user = user
        self.logger = logger

    def generate_plan(
        self,
        injury_type: str,
        injury_severity: str = "moderate",
        duration_weeks: int = 4,
        difficulty_level: str = "intermediate",
        goals: Optional[List[str]] = None,
    ) -> Tuple[Optional[TherapyPlan], str]:
        """
        Generate a personalized therapy plan using GPT.

        Args:
            injury_type: Type of injury (e.g., "knee pain", "rotator cuff tear")
            injury_severity: Severity level ("mild", "moderate", "severe")
            duration_weeks: Number of weeks for the plan (default: 4)
            difficulty_level: Starting difficulty ("beginner", "intermediate", "advanced")
            goals: Optional list of specific therapeutic goals

        Returns:
            Tuple of (TherapyPlan object, status_message)
            Returns (None, error_message) if generation fails
        """
        try:
            self.logger.info(
                f"Generating therapy plan for user {self.user.username}: "
                f"injury={injury_type}, severity={injury_severity}"
            )

            # Collect user performance data
            performance_data = self._collect_performance_data()

            # Generate plan using GPT
            gpt_response = self._call_gpt_api(
                injury_type=injury_type,
                injury_severity=injury_severity,
                duration_weeks=duration_weeks,
                difficulty_level=difficulty_level,
                goals=goals,
                performance_data=performance_data,
            )

            if not gpt_response:
                return None, "Failed to generate plan from GPT"

            # Parse and validate GPT response
            plan_data = self._parse_gpt_response(gpt_response)
            if not plan_data:
                return None, "Failed to parse GPT response"

            # Create TherapyPlan object in database
            therapy_plan = self._save_therapy_plan(
                injury_type=injury_type,
                duration_weeks=duration_weeks,
                difficulty_level=difficulty_level,
                plan_data=plan_data,
                gpt_response=gpt_response,
                performance_data=performance_data,
            )

            self.logger.info(
                f"Successfully generated therapy plan {therapy_plan.id} for user {self.user.username}"
            )
            return therapy_plan, "Plan generated successfully"

        except Exception as e:
            error_msg = f"Error generating therapy plan: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return None, error_msg

    def _collect_performance_data(self) -> Dict[str, Any]:
        """
        Collect user's performance history and metrics.

        Returns:
            Dictionary with performance data
        """
        try:
            # Get user progress
            user_progress = UserProgress.objects.filter(user=self.user).first()
            
            # Get recent daily metrics (last 2 weeks)
            two_weeks_ago = datetime.now().date() - timedelta(days=14)
            recent_metrics = DailyMetrics.objects.filter(
                user=self.user,
                date__gte=two_weeks_ago
            ).order_by('-date')

            # Calculate averages
            total_sessions = user_progress.total_sessions_completed if user_progress else 0
            avg_form_score = user_progress.average_form_score if user_progress else 0
            avg_daily_form = (
                sum(m.average_form_score for m in recent_metrics) / len(recent_metrics)
                if recent_metrics
                else avg_form_score
            )
            current_streak = user_progress.current_streak_days if user_progress else 0
            avg_daily_minutes = (
                sum(m.total_minutes_exercised for m in recent_metrics) / len(recent_metrics)
                if recent_metrics
                else 0
            )

            performance_data = {
                'total_sessions_completed': total_sessions,
                'average_form_score': float(avg_form_score),
                'average_form_score_recent': float(avg_daily_form),
                'current_streak_days': current_streak,
                'fitness_level': self.user.profile.fitness_level if hasattr(self.user, 'profile') else 'intermediate',
                'age': self.user.profile.age if hasattr(self.user, 'profile') else 'unknown',
                'previous_injuries': self.user.profile.injury_history if hasattr(self.user, 'profile') else '',
                'average_daily_minutes': float(avg_daily_minutes),
                'data_collection_date': datetime.now().isoformat(),
            }

            return performance_data

        except Exception as e:
            self.logger.warning(f"Error collecting performance data: {str(e)}")
            return {'error': str(e)}

    def _call_gpt_api(
        self,
        injury_type: str,
        injury_severity: str,
        duration_weeks: int,
        difficulty_level: str,
        goals: Optional[List[str]],
        performance_data: Dict[str, Any],
    ) -> Optional[str]:
        """
        Call OpenAI GPT API to generate therapy plan.

        Returns:
            GPT response as string, or None if failed
        """
        try:
            # Build user prompt
            user_prompt = self._build_gpt_prompt(
                injury_type=injury_type,
                injury_severity=injury_severity,
                duration_weeks=duration_weeks,
                difficulty_level=difficulty_level,
                goals=goals,
                performance_data=performance_data,
            )

            # Call GPT API
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Use gpt-4 or gpt-3.5-turbo
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"},  # Request JSON format
            )

            # Extract content
            content = response.choices[0].message.content
            self.logger.info("Successfully received response from GPT API")
            return content

        except openai.error.RateLimitError:
            self.logger.error("GPT API rate limit exceeded")
            return None
        except openai.error.AuthenticationError:
            self.logger.error("GPT API authentication failed - check API key")
            return None
        except Exception as e:
            self.logger.error(f"GPT API error: {str(e)}")
            return None

    def _build_gpt_prompt(
        self,
        injury_type: str,
        injury_severity: str,
        duration_weeks: int,
        difficulty_level: str,
        goals: Optional[List[str]],
        performance_data: Dict[str, Any],
    ) -> str:
        """
        Build the prompt to send to GPT.

        Returns:
            Formatted prompt string
        """
        goals_text = "\n".join([f"- {goal}" for goal in (goals or [])])
        
        prompt = f"""Generate a detailed personalized physiotherapy plan with the following specifications:

**Patient Information:**
- Injury Type: {injury_type}
- Injury Severity: {injury_severity} (mild/moderate/severe)
- Fitness Level: {performance_data.get('fitness_level', 'unknown')}
- Age: {performance_data.get('age', 'unknown')}
- Previous Injuries: {performance_data.get('previous_injuries', 'none')}

**Performance History:**
- Total Sessions Completed: {performance_data.get('total_sessions_completed', 0)}
- Average Form Score: {performance_data.get('average_form_score', 'N/A')}/100
- Recent Form Score: {performance_data.get('average_form_score_recent', 'N/A')}/100
- Current Exercise Streak: {performance_data.get('current_streak_days', 0)} days
- Average Daily Exercise Time: {performance_data.get('average_daily_minutes', 'N/A')} minutes

**Plan Requirements:**
- Duration: {duration_weeks} weeks
- Starting Difficulty: {difficulty_level}
- Specific Goals:
{goals_text if goals_text else "- Improve mobility and strength"}

**Required Output Format (JSON):**
{{
  "title": "Personalized {injury_type} Recovery Plan",
  "description": "Brief description of the plan approach",
  "goals": ["goal1", "goal2", "goal3"],
  "precautions": ["precaution1", "precaution2", ...],
  "progression_strategy": "Detailed explanation of how to progress through the plan",
  "weekly_plan": {{
    "week_1": {{
      "monday": [{{"name": "Exercise name", "sets": 3, "reps": 10, "description": "How to do it", "precautions": "Any warnings"}}],
      "tuesday": [{{"name": "Rest day", "is_rest": true}}],
      "wednesday": [...],
      "thursday": [...],
      "friday": [...],
      "saturday": [{{"name": "Light activity", ...}}],
      "sunday": [{{"name": "Rest day", "is_rest": true}}],
      "notes": "Week-specific notes and adjustments"
    }},
    "week_2": {{ ... }},
    ...
  }},
  "exercise_library": {{
    "exercise_name": {{
      "description": "Detailed how-to",
      "benefits": "Why this exercise",
      "modifications": "Easier or harder versions",
      "common_mistakes": "What to avoid"
    }},
    ...
  }},
  "progression_schedule": {{
    "week_1_2": "Build foundation and establish routine",
    "week_3_4": "Increase intensity and challenge",
    ...
  }}
}}

Please generate a comprehensive, safe, and effective therapy plan based on the patient's specific condition and performance history. Include exercises that progressively challenge the patient while respecting their current fitness level and injury status."""

        return prompt

    def _parse_gpt_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse JSON response from GPT.

        Returns:
            Parsed dictionary, or None if parsing fails
        """
        try:
            plan_data = json.loads(response_text)
            
            # Validate required fields
            required_fields = ['title', 'description', 'goals', 'precautions', 'weekly_plan']
            if not all(field in plan_data for field in required_fields):
                self.logger.error(
                    f"GPT response missing required fields. Has: {list(plan_data.keys())}"
                )
                return None

            return plan_data

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse GPT response as JSON: {str(e)}")
            return None

    @transaction.atomic
    def _save_therapy_plan(
        self,
        injury_type: str,
        duration_weeks: int,
        difficulty_level: str,
        plan_data: Dict[str, Any],
        gpt_response: str,
        performance_data: Dict[str, Any],
    ) -> Optional[TherapyPlan]:
        """
        Save the generated plan to the database.

        Returns:
            Created TherapyPlan object, or None if failed
        """
        try:
            # Create TherapyPlan
            therapy_plan = TherapyPlan.objects.create(
                user=self.user,
                injury_type=injury_type,
                title=plan_data.get('title', f"{injury_type} Recovery Plan"),
                description=plan_data.get('description', ''),
                duration_weeks=duration_weeks,
                difficulty_level=difficulty_level,
                weekly_plan=plan_data.get('weekly_plan', {}),
                goals=plan_data.get('goals', []),
                precautions=plan_data.get('precautions', []),
                progression_strategy=plan_data.get('progression_strategy', ''),
                gpt_response=json.loads(gpt_response) if isinstance(gpt_response, str) else gpt_response,
                created_from_performance=performance_data,
                status='active',
                start_date=datetime.now().date(),
                end_date=(datetime.now() + timedelta(weeks=duration_weeks)).date(),
            )

            # Create WeeklyExercise records
            self._create_weekly_exercises(therapy_plan, plan_data)

            self.logger.info(f"Saved therapy plan {therapy_plan.id}")
            return therapy_plan

        except Exception as e:
            self.logger.error(f"Error saving therapy plan: {str(e)}", exc_info=True)
            return None

    def _create_weekly_exercises(
        self,
        therapy_plan: TherapyPlan,
        plan_data: Dict[str, Any],
    ) -> int:
        """
        Create WeeklyExercise records from the plan data.

        Returns:
            Number of exercises created
        """
        try:
            weekly_plan = plan_data.get('weekly_plan', {})
            exercises_created = 0

            # Days of week mapping
            day_mapping = {
                'monday': 'monday',
                'tuesday': 'tuesday',
                'wednesday': 'wednesday',
                'thursday': 'thursday',
                'friday': 'friday',
                'saturday': 'saturday',
                'sunday': 'sunday',
            }

            for week_key, week_data in weekly_plan.items():
                # Extract week number
                week_number = int(week_key.split('_')[-1])

                for day_name, exercises_list in week_data.items():
                    if day_name not in day_mapping or not isinstance(exercises_list, list):
                        continue

                    for order, exercise_data in enumerate(exercises_list):
                        # Check if it's a rest day
                        is_rest = exercise_data.get('is_rest', False) or exercise_data.get('name', '').lower() == 'rest day'

                        # Try to match with existing Exercise in database
                        db_exercise = None
                        if not is_rest:
                            db_exercise = self._find_matching_exercise(
                                exercise_data.get('name', '')
                            )

                        # Create WeeklyExercise record
                        weekly_exercise = WeeklyExercise.objects.create(
                            therapy_plan=therapy_plan,
                            week_number=week_number,
                            day_of_week=day_mapping[day_name],
                            exercise=db_exercise,
                            exercise_name=exercise_data.get('name', 'Rest'),
                            description=exercise_data.get('description', ''),
                            sets=exercise_data.get('sets', 1),
                            reps=exercise_data.get('reps', 1),
                            duration_minutes=exercise_data.get('duration', 1),
                            rest_seconds=exercise_data.get('rest_seconds', 60),
                            modifications=exercise_data.get('modifications', ''),
                            precautions=exercise_data.get('precautions', ''),
                            benefits=exercise_data.get('benefits', ''),
                            is_rest_day=is_rest,
                            order=order,
                        )
                        exercises_created += 1

            self.logger.info(f"Created {exercises_created} weekly exercise records")
            return exercises_created

        except Exception as e:
            self.logger.error(f"Error creating weekly exercises: {str(e)}", exc_info=True)
            return 0

    def _find_matching_exercise(self, exercise_name: str) -> Optional[Exercise]:
        """
        Find a matching exercise in the Exercise model by name.

        Returns:
            Exercise object if found, None otherwise
        """
        try:
            # Try exact match first (case-insensitive)
            exercise = Exercise.objects.filter(
                name__iexact=exercise_name,
                is_active=True
            ).first()

            if exercise:
                return exercise

            # Try partial match if no exact match
            exercise = Exercise.objects.filter(
                name__icontains=exercise_name,
                is_active=True
            ).first()

            return exercise

        except Exception as e:
            self.logger.warning(f"Error finding matching exercise: {str(e)}")
            return None


def generate_therapy_plan(
    user: User,
    injury_type: str,
    injury_severity: str = "moderate",
    duration_weeks: int = 4,
    difficulty_level: str = "intermediate",
    goals: Optional[List[str]] = None,
) -> Tuple[Optional[TherapyPlan], str]:
    """
    Convenience function to generate a therapy plan.

    Args:
        user: Django User object
        injury_type: Type of injury
        injury_severity: Severity level ("mild", "moderate", "severe")
        duration_weeks: Number of weeks for the plan
        difficulty_level: Starting difficulty level
        goals: Optional list of specific goals

    Returns:
        Tuple of (TherapyPlan object, status_message)

    Example:
        >>> from django.contrib.auth.models import User
        >>> from therapy_plans.services import generate_therapy_plan
        >>> user = User.objects.get(username='john_doe')
        >>> plan, message = generate_therapy_plan(
        ...     user=user,
        ...     injury_type="knee pain",
        ...     injury_severity="moderate",
        ...     goals=["Reduce pain", "Improve mobility", "Return to sports"]
        ... )
        >>> if plan:
        ...     print(f"Plan created: {plan.title}")
        ... else:
        ...     print(f"Error: {message}")
    """
    generator = TherapyPlanGenerator(user)
    return generator.generate_plan(
        injury_type=injury_type,
        injury_severity=injury_severity,
        duration_weeks=duration_weeks,
        difficulty_level=difficulty_level,
        goals=goals,
    )
