"""
Django REST Framework Serializers for Physio AI API

Handles data validation and transformation for all API endpoints:
- Session management (create, update, complete)
- Pose angle capture from computer vision
- Form scoring calculations
- Feedback generation and retrieval
- Progress tracking and history
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Avg, Count

User = get_user_model()


# ============================================================================
# USER SERIALIZERS
# ============================================================================

class UserDetailSerializer(serializers.ModelSerializer):
    """User profile with physiotherapy-specific information."""
    
    age = serializers.SerializerMethodField()
    injury_display = serializers.CharField(source='get_injury_type_display', read_only=True)
    fitness_display = serializers.CharField(source='get_fitness_level_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'date_of_birth', 'age', 'injury_type', 'injury_display',
            'fitness_level', 'fitness_display', 'height_cm', 'weight_kg',
            'medical_notes', 'phone_number', 'profile_picture', 'last_activity'
        ]
        read_only_fields = ['id', 'last_activity']
    
    def get_age(self, obj):
        """Calculate age from date of birth."""
        if obj.date_of_birth:
            return obj.get_age()
        return None


# ============================================================================
# SESSION SERIALIZERS
# ============================================================================

class SessionStartSerializer(serializers.Serializer):
    """Serializer for starting a new session."""
    
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    session_type = serializers.ChoiceField(
        choices=['home_supervised', 'home_unsupervised', 'clinic', 'telehealth'],
        default='home_unsupervised'
    )
    scheduled_duration_minutes = serializers.IntegerField(
        min_value=5, max_value=180, default=30
    )
    assigned_therapist_id = serializers.IntegerField(required=False, allow_null=True)
    pain_level_before = serializers.IntegerField(
        min_value=0, max_value=10, required=True,
        help_text="Pain level before session (0-10)"
    )
    
    def validate_assigned_therapist_id(self, value):
        """Validate therapist exists."""
        if value and not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Therapist not found.")
        return value


class SessionExerciseInputSerializer(serializers.Serializer):
    """Serializer for adding exercises to a session."""
    
    exercise_id = serializers.IntegerField(required=True)
    order_in_session = serializers.IntegerField(min_value=1, required=True)
    target_reps = serializers.IntegerField(min_value=1, required=False)
    target_sets = serializers.IntegerField(min_value=1, required=False)
    user_notes = serializers.CharField(required=False, allow_blank=True)


class SessionExerciseDetailSerializer(serializers.Serializer):
    """Serializer for displaying exercise performance within a session."""
    
    id = serializers.IntegerField()
    exercise_id = serializers.IntegerField()
    exercise_name = serializers.CharField()
    order_in_session = serializers.IntegerField()
    status = serializers.CharField()
    reps_performed = serializers.IntegerField(allow_null=True)
    sets_performed = serializers.IntegerField(allow_null=True)
    target_reps = serializers.IntegerField()
    form_score = serializers.FloatField(allow_null=True)
    consistency_score = serializers.FloatField(allow_null=True)
    range_of_motion_percentage = serializers.FloatField(allow_null=True)
    pain_during_exercise = serializers.IntegerField(allow_null=True)
    form_issues_detected = serializers.JSONField(allow_null=True)
    ai_feedback_for_exercise = serializers.CharField(allow_null=True)
    user_difficulty_rating = serializers.IntegerField(allow_null=True)


class SessionDetailSerializer(serializers.Serializer):
    """Detailed session information with all exercises and scores."""
    
    id = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField(allow_null=True)
    status = serializers.CharField()
    session_type = serializers.CharField()
    duration_minutes = serializers.SerializerMethodField()
    scheduled_duration_minutes = serializers.IntegerField()
    
    # Scoring
    overall_session_score = serializers.FloatField(allow_null=True)
    average_exercise_score = serializers.FloatField(allow_null=True)
    completion_percentage = serializers.FloatField(allow_null=True)
    
    # Exercises
    exercises = serializers.SerializerMethodField()
    exercise_count = serializers.SerializerMethodField()
    
    # Pain tracking
    pain_level_before = serializers.IntegerField(allow_null=True)
    pain_level_after = serializers.IntegerField(allow_null=True)
    pain_improvement = serializers.SerializerMethodField()
    
    # Feedback
    ai_generated_feedback = serializers.CharField(allow_null=True)
    therapist_feedback = serializers.CharField(allow_null=True)
    improvement_areas = serializers.JSONField(allow_null=True)
    positive_feedback_points = serializers.JSONField(allow_null=True)
    
    # Video
    video_recording_available = serializers.BooleanField()
    device_tracking_confidence = serializers.FloatField(allow_null=True)
    
    def get_duration_minutes(self, obj):
        """Calculate session duration."""
        if obj.get('start_time') and obj.get('end_time'):
            delta = obj['end_time'] - obj['start_time']
            return int(delta.total_seconds() / 60)
        return None
    
    def get_exercises(self, obj):
        """Return exercises in order."""
        # This will be populated by the view
        return obj.get('exercises', [])
    
    def get_exercise_count(self, obj):
        """Count of exercises."""
        exercises = obj.get('exercises', [])
        return len(exercises)
    
    def get_pain_improvement(self, obj):
        """Calculate pain improvement."""
        before = obj.get('pain_level_before')
        after = obj.get('pain_level_after')
        if before is not None and after is not None:
            return before - after
        return None


class SessionListSerializer(serializers.Serializer):
    """Simplified session info for lists."""
    
    id = serializers.IntegerField()
    title = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField(allow_null=True)
    status = serializers.CharField()
    overall_session_score = serializers.FloatField(allow_null=True)
    completion_percentage = serializers.FloatField(allow_null=True)
    exercise_count = serializers.IntegerField()
    pain_level_before = serializers.IntegerField(allow_null=True)
    pain_level_after = serializers.IntegerField(allow_null=True)


# ============================================================================
# POSE ANALYSIS SERIALIZERS
# ============================================================================

class PoseAngleSubmitSerializer(serializers.Serializer):
    """Serializer for submitting pose angles from computer vision."""
    
    session_exercise_id = serializers.IntegerField(
        help_text="ID of the SessionExercise being performed"
    )
    frame_number = serializers.IntegerField(
        min_value=0,
        help_text="Frame number in the video sequence"
    )
    timestamp_seconds = serializers.FloatField(
        min_value=0,
        help_text="Timestamp in seconds"
    )
    detected_joint_angles = serializers.JSONField(
        help_text="Dictionary of detected joint angles: {'shoulder': 92.5, 'elbow': 178.2, ...}"
    )
    pose_detection_confidence = serializers.FloatField(
        min_value=0, max_value=100,
        help_text="Overall pose detection confidence (0-100)"
    )
    individual_joint_confidence = serializers.JSONField(
        help_text="Per-joint confidence scores: {'shoulder': 95.2, 'elbow': 88.1, ...}",
        required=False
    )
    body_position_description = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Description of body position (e.g., 'peak extension', 'return to start')"
    )
    is_peak_position = serializers.BooleanField(
        default=False,
        help_text="Is this the peak position of the exercise?"
    )
    
    def validate_detected_joint_angles(self, value):
        """Validate joint angles are reasonable."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Joint angles must be a dictionary.")
        
        for joint, angle in value.items():
            if not isinstance(angle, (int, float)):
                raise serializers.ValidationError(
                    f"Angle for {joint} must be a number."
                )
            if not (0 <= angle <= 360):
                raise serializers.ValidationError(
                    f"Angle for {joint} must be between 0-360 degrees."
                )
        return value


class PoseAnalysisDetailSerializer(serializers.Serializer):
    """Detailed pose analysis results."""
    
    id = serializers.IntegerField()
    frame_number = serializers.IntegerField()
    timestamp_seconds = serializers.FloatField()
    detected_joint_angles = serializers.JSONField()
    angle_errors = serializers.JSONField(allow_null=True)
    pose_detection_confidence = serializers.FloatField()
    individual_joint_confidence = serializers.JSONField(allow_null=True)
    form_issues = serializers.JSONField(allow_null=True)
    body_position_description = serializers.CharField()
    is_peak_position = serializers.BooleanField()
    overall_form_quality = serializers.FloatField(allow_null=True)


# ============================================================================
# SCORE & FEEDBACK SERIALIZERS
# ============================================================================

class ScoreCalculationResultSerializer(serializers.Serializer):
    """Results of score calculation for an exercise."""
    
    session_exercise_id = serializers.IntegerField()
    exercise_name = serializers.CharField()
    form_score = serializers.FloatField()
    consistency_score = serializers.FloatField()
    range_of_motion_percentage = serializers.FloatField()
    overall_exercise_score = serializers.SerializerMethodField()
    form_issues = serializers.JSONField()
    recommendations = serializers.ListField(child=serializers.CharField())
    
    def get_overall_exercise_score(self, obj):
        """Calculate overall score from components."""
        form = obj.get('form_score', 0) * 0.5
        consistency = obj.get('consistency_score', 0) * 0.3
        rom = obj.get('range_of_motion_percentage', 0) * 0.2
        return round(form + consistency + rom, 1)


class FeedbackSerializer(serializers.Serializer):
    """Comprehensive feedback for a session."""
    
    session_id = serializers.IntegerField()
    overall_session_score = serializers.FloatField()
    completion_percentage = serializers.FloatField()
    
    # AI Generated Feedback
    ai_feedback = serializers.CharField()
    improvement_areas = serializers.JSONField()
    positive_feedback_points = serializers.JSONField()
    
    # Performance Analysis
    avg_form_score = serializers.FloatField()
    avg_consistency_score = serializers.FloatField()
    avg_range_of_motion = serializers.FloatField()
    
    # Pain tracking
    pain_level_before = serializers.IntegerField()
    pain_level_after = serializers.IntegerField()
    pain_improvement = serializers.SerializerMethodField()
    
    # Exercises performed
    exercises_completed = serializers.IntegerField()
    total_exercises = serializers.IntegerField()
    exercises_skipped = serializers.IntegerField()
    
    # Recommendations
    recommended_focus_areas = serializers.ListField(child=serializers.CharField())
    next_session_recommendations = serializers.ListField(child=serializers.CharField())
    
    def get_pain_improvement(self, obj):
        """Calculate pain improvement percentage."""
        before = obj.get('pain_level_before', 0)
        after = obj.get('pain_level_after', 0)
        if before > 0:
            return round(((before - after) / before) * 100, 1)
        return 0


# ============================================================================
# PROGRESS & HISTORY SERIALIZERS
# ============================================================================

class DailyMetricsSerializer(serializers.Serializer):
    """Daily aggregated metrics for a user."""
    
    date = serializers.DateField()
    sessions_completed = serializers.IntegerField()
    exercises_completed = serializers.IntegerField()
    total_minutes_exercised = serializers.IntegerField()
    average_session_score = serializers.FloatField(allow_null=True)
    average_form_score = serializers.FloatField(allow_null=True)
    completion_rate = serializers.FloatField(allow_null=True)
    average_pain_before = serializers.FloatField(allow_null=True)
    average_pain_after = serializers.FloatField(allow_null=True)


class UserProgressSerializer(serializers.Serializer):
    """Comprehensive user progress metrics."""
    
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    
    # Session Statistics
    total_sessions_completed = serializers.IntegerField()
    total_sessions_started = serializers.IntegerField()
    session_completion_rate = serializers.FloatField()
    
    # Performance Metrics
    average_session_score = serializers.FloatField(allow_null=True)
    best_session_score = serializers.FloatField(allow_null=True)
    worst_session_score = serializers.FloatField(allow_null=True)
    average_exercise_form_score = serializers.FloatField(allow_null=True)
    
    # Streaks
    current_streak_days = serializers.IntegerField()
    longest_streak_days = serializers.IntegerField()
    last_session_date = serializers.DateField(allow_null=True)
    
    # Progression
    exercises_mastered = serializers.IntegerField()
    avg_difficulty_of_exercises = serializers.CharField()
    
    # Pain Tracking
    average_pain_before_session = serializers.FloatField(allow_null=True)
    average_pain_after_session = serializers.FloatField(allow_null=True)
    pain_improvement_percentage = serializers.FloatField(allow_null=True)
    
    # Goals
    primary_goal = serializers.CharField()
    goal_progress_percentage = serializers.FloatField(allow_null=True)
    estimated_recovery_date = serializers.DateField(allow_null=True)
    
    # Weekly
    sessions_this_week = serializers.IntegerField()
    average_score_this_week = serializers.FloatField(allow_null=True)
    
    # Milestones
    total_reward_points = serializers.SerializerMethodField()
    recent_milestones = serializers.SerializerMethodField()
    
    def get_total_reward_points(self, obj):
        """Get total reward points."""
        return obj.get('total_reward_points', 0)
    
    def get_recent_milestones(self, obj):
        """Get recent achievement milestones."""
        return obj.get('recent_milestones', [])


class ProgressHistorySerializer(serializers.Serializer):
    """Historical progress data with trends."""
    
    date_range_start = serializers.DateField()
    date_range_end = serializers.DateField()
    
    # Summary Stats
    total_sessions = serializers.IntegerField()
    total_exercises_completed = serializers.IntegerField()
    total_hours_exercised = serializers.FloatField()
    average_session_score = serializers.FloatField()
    
    # Trend Analysis
    trend = serializers.CharField()  # 'improving', 'stable', 'declining'
    trend_percentage = serializers.FloatField()
    best_week = serializers.CharField()
    worst_week = serializers.CharField()
    
    # Pain Improvement
    pain_improvement_over_period = serializers.FloatField()
    starting_average_pain = serializers.FloatField()
    ending_average_pain = serializers.FloatField()
    
    # Exercise Progression
    exercises_attempted = serializers.IntegerField()
    new_exercises_mastered = serializers.IntegerField()
    difficulty_progression = serializers.CharField()
    
    # Daily Breakdown
    daily_metrics = DailyMetricsSerializer(many=True)


class ExerciseProgressSerializer(serializers.Serializer):
    """Progress on a specific exercise."""
    
    exercise_id = serializers.IntegerField()
    exercise_name = serializers.CharField()
    category = serializers.CharField()
    
    # Performance
    times_performed = serializers.IntegerField()
    average_form_score = serializers.FloatField()
    best_form_score = serializers.FloatField()
    worst_form_score = serializers.FloatField()
    
    # Trend
    form_score_trend = serializers.CharField()  # 'improving', 'stable', 'declining'
    recent_scores = serializers.ListField(child=serializers.FloatField())
    
    # Difficulty
    average_user_difficulty_rating = serializers.FloatField()
    average_pain_during_exercise = serializers.FloatField()
    
    # Common Issues
    most_common_form_issues = serializers.JSONField()
    recent_feedback = serializers.CharField()
    
    # Recommendations
    recommendation = serializers.CharField()


# ============================================================================
# ERROR & STATUS SERIALIZERS
# ============================================================================

class ErrorSerializer(serializers.Serializer):
    """Standardized error response."""
    
    error = serializers.CharField()
    detail = serializers.CharField(required=False)
    code = serializers.CharField(required=False)


class StatusSerializer(serializers.Serializer):
    """Generic status response."""
    
    status = serializers.CharField()  # 'success', 'error', 'pending'
    message = serializers.CharField()
    data = serializers.JSONField(required=False, allow_null=True)
    timestamp = serializers.DateTimeField(default=timezone.now)
