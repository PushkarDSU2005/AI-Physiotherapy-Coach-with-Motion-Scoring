"""
Serializers for Therapy Plan API endpoints
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from therapy_plans.models import TherapyPlan, WeeklyExercise


class WeeklyExerciseSerializer(serializers.ModelSerializer):
    """Serializer for weekly exercise assignments"""
    
    class Meta:
        model = WeeklyExercise
        fields = [
            'id',
            'week_number',
            'day_of_week',
            'exercise_name',
            'description',
            'sets',
            'reps',
            'duration_minutes',
            'rest_seconds',
            'modifications',
            'precautions',
            'benefits',
            'progression_notes',
            'is_rest_day',
            'order',
        ]
        read_only_fields = ['id']


class TherapyPlanDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for therapy plans with all data"""
    
    exercise_assignments = WeeklyExerciseSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = TherapyPlan
        fields = [
            'id',
            'user_username',
            'injury_type',
            'status',
            'title',
            'description',
            'duration_weeks',
            'difficulty_level',
            'weekly_plan',
            'goals',
            'precautions',
            'progression_strategy',
            'exercise_assignments',
            'created_from_performance',
            'start_date',
            'end_date',
            'progress_score',
            'created_at',
            'updated_at',
            'generated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'generated_at']


class TherapyPlanListSerializer(serializers.ModelSerializer):
    """Minimal serializer for therapy plan listings"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = TherapyPlan
        fields = [
            'id',
            'user_username',
            'injury_type',
            'title',
            'status',
            'duration_weeks',
            'difficulty_level',
            'progress_score',
            'start_date',
            'end_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GeneratePlanSerializer(serializers.Serializer):
    """Serializer for plan generation request"""
    
    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    injury_type = serializers.CharField(
        max_length=255,
        help_text="Type of injury (e.g., 'knee pain', 'rotator cuff')"
    )
    injury_severity = serializers.ChoiceField(
        choices=SEVERITY_CHOICES,
        default='moderate',
        help_text="Severity of the injury"
    )
    duration_weeks = serializers.IntegerField(
        min_value=1,
        max_value=52,
        default=4,
        help_text="Duration of the plan in weeks"
    )
    difficulty_level = serializers.ChoiceField(
        choices=DIFFICULTY_CHOICES,
        default='intermediate',
        help_text="Starting difficulty level"
    )
    goals = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=False,
        help_text="Specific therapeutic goals"
    )
    
    def validate_injury_type(self, value):
        """Validate injury type is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Injury type cannot be empty")
        return value.strip()


class UpdateProgressSerializer(serializers.Serializer):
    """Serializer for updating plan progress"""
    
    progress_score = serializers.FloatField(
        min_value=0.0,
        max_value=100.0,
        help_text="User's progress on the plan (0-100)"
    )
    status = serializers.ChoiceField(
        choices=['draft', 'active', 'completed', 'archived'],
        required=False,
        help_text="Updated status of the plan"
    )
    notes = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True,
        help_text="Any additional notes about progress"
    )


class WeeklyPlanSerializer(serializers.Serializer):
    """Serializer for structured weekly plan data"""
    
    week = serializers.IntegerField(help_text="Week number")
    plan = serializers.DictField(help_text="Daily exercises for the week")
    notes = serializers.CharField(required=False, help_text="Week-specific notes")


class ComparisonReportSerializer(serializers.Serializer):
    """Serializer for comparing multiple plans"""
    
    plan_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of therapy plan IDs to compare"
    )
    metric = serializers.ChoiceField(
        choices=['progress', 'difficulty', 'duration', 'goals'],
        default='progress',
        help_text="Metric to compare"
    )
