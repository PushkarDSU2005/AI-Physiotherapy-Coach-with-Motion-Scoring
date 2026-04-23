"""
Advanced Features Models for PhysioAI

Includes:
1. Adaptive Difficulty System - Tracks and adapts exercise difficulty based on performance
2. Injury Risk Detection - Monitors joint angles and flags dangerous positions
3. Exercise Classification - Multi-dimensional exercise categorization
"""

from django.db import models
from django.contrib.auth.models import User
from exercises.models import Exercise
from sessions.models import SessionExercise
from ai_engine.models import PoseAnalysis
import json


class ExerciseClassification(models.Model):
    """
    Multi-dimensional classification system for exercises.
    Exercises can have multiple classifications based on movement patterns,
    muscle groups, equipment, complexity, and recovery focus.
    """
    CLASSIFICATION_TYPES = [
        ('movement_pattern', 'Movement Pattern'),  # e.g., bilateral, unilateral, rotation
        ('equipment', 'Equipment'),                # e.g., bodyweight, band, weights
        ('intensity', 'Intensity'),                # e.g., isometric, dynamic, explosive
        ('plane_of_motion', 'Plane of Motion'),   # e.g., sagittal, frontal, transverse
        ('primary_joint', 'Primary Joint'),        # e.g., knee, shoulder, hip, spine
        ('secondary_joint', 'Secondary Joint'),    # e.g., supporting joints
        ('stabilization', 'Stabilization'),        # Whether exercise requires core/stability
        ('complexity_level', 'Complexity Level'),  # Simple, intermediate, complex
        ('recovery_focus', 'Recovery Focus'),      # e.g., ROM, mobility, strength, endurance
    ]

    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='classifications'
    )
    classification_type = models.CharField(max_length=50, choices=CLASSIFICATION_TYPES)
    classification_value = models.CharField(max_length=100, help_text="Classification label")
    weight = models.FloatField(default=1.0, help_text="Importance weight for matching")
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.exercise.name} - {self.get_classification_type_display()}: {self.classification_value}"

    class Meta:
        verbose_name = 'Exercise Classification'
        verbose_name_plural = 'Exercise Classifications'
        unique_together = ['exercise', 'classification_type', 'classification_value']
        indexes = [
            models.Index(fields=['exercise', 'classification_type']),
            models.Index(fields=['classification_type', 'classification_value']),
        ]


class DifficultyAdaptation(models.Model):
    """
    Tracks difficulty adaptation for a user on specific exercises.
    Analyzes performance trends and recommends difficulty changes.
    """
    TREND_TYPES = [
        ('improving', 'Improving'),           # User improving, suggest increase
        ('stable', 'Stable'),                 # User maintaining level
        ('declining', 'Declining'),           # User struggling, suggest decrease
        ('plateaued', 'Plateaued'),          # No change, suggest variation
    ]

    RECOMMENDATION_TYPES = [
        ('increase', 'Increase Difficulty'),
        ('maintain', 'Maintain Current'),
        ('decrease', 'Decrease Difficulty'),
        ('modify', 'Modify Exercise'),
        ('progress', 'Progress to Variant'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='difficulty_adaptations')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    
    # Performance tracking
    last_10_scores = models.JSONField(default=list, help_text="Last 10 form scores")
    average_score = models.FloatField(default=0.0, help_text="Average of last 10")
    min_score = models.FloatField(default=0.0)
    max_score = models.FloatField(default=0.0)
    
    # Trend analysis
    trend = models.CharField(max_length=20, choices=TREND_TYPES, default='stable')
    trend_slope = models.FloatField(default=0.0, help_text="Positive = improving")
    consistency_score = models.FloatField(default=0.0, help_text="How consistent performance 0-100")
    
    # Recommendations
    recommendation = models.CharField(
        max_length=20, 
        choices=RECOMMENDATION_TYPES, 
        default='maintain'
    )
    recommended_difficulty = models.CharField(
        max_length=20,
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        null=True,
        blank=True
    )
    recommendation_reason = models.TextField(blank=True)
    
    # Tracking
    total_sessions = models.IntegerField(default=0, help_text="Total sessions with this exercise")
    days_since_last = models.IntegerField(default=0, help_text="Days since last attempt")
    adaptation_count = models.IntegerField(default=0, help_text="Number of times adapted")
    
    last_adapted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name}: {self.trend}"

    class Meta:
        verbose_name = 'Difficulty Adaptation'
        verbose_name_plural = 'Difficulty Adaptations'
        unique_together = ['user', 'exercise']
        indexes = [
            models.Index(fields=['user', 'trend']),
            models.Index(fields=['exercise', 'recommendation']),
        ]


class InjuryRiskAlert(models.Model):
    """
    Tracks potential injury risks detected during exercise execution.
    Monitors joint angles and positions that exceed safe ranges.
    """
    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]

    ALERT_TYPES = [
        ('joint_angle', 'Joint Angle Exceeded'),
        ('range_of_motion', 'Excessive ROM'),
        ('joint_compression', 'Joint Compression'),
        ('shear_force', 'Shear Force Detected'),
        ('instability', 'Joint Instability'),
        ('asymmetry', 'Movement Asymmetry'),
        ('muscle_imbalance', 'Muscle Imbalance'),
        ('fatigue_risk', 'Fatigue-Related Risk'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='injury_risk_alerts')
    pose_analysis = models.ForeignKey(
        PoseAnalysis,
        on_delete=models.CASCADE,
        related_name='injury_alerts',
        null=True,
        blank=True
    )
    session_exercise = models.ForeignKey(
        SessionExercise,
        on_delete=models.CASCADE,
        related_name='injury_alerts'
    )
    
    # Alert details
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)
    
    # Joint/Angle specific info
    joint_name = models.CharField(max_length=100, help_text="e.g., left_knee, right_shoulder")
    current_angle = models.FloatField(null=True, blank=True, help_text="Current joint angle in degrees")
    safe_range_min = models.FloatField(null=True, blank=True, help_text="Min safe angle")
    safe_range_max = models.FloatField(null=True, blank=True, help_text="Max safe angle")
    angle_exceeded_by = models.FloatField(null=True, blank=True, help_text="Degrees exceeded")
    
    # Severity
    severity_score = models.FloatField(help_text="Risk severity 0-100")
    repetition_count = models.IntegerField(default=1, help_text="How many times this occurred")
    
    # Details
    description = models.TextField(help_text="Detailed explanation of the risk")
    recommendation = models.TextField(help_text="What user should do to reduce risk")
    
    # Tracking
    is_acknowledged = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)
    
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_alert_type_display()} ({self.get_risk_level_display()})"

    class Meta:
        verbose_name = 'Injury Risk Alert'
        verbose_name_plural = 'Injury Risk Alerts'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['user', '-detected_at']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['is_resolved']),
        ]


class JointSafetyProfile(models.Model):
    """
    Defines safe angle ranges for different joints based on exercise type,
    user's injury history, and clinical guidelines.
    """
    MOVEMENT_AXIS = [
        ('flexion_extension', 'Flexion/Extension'),
        ('abduction_adduction', 'Abduction/Adduction'),
        ('rotation', 'Rotation'),
        ('circumduction', 'Circumduction'),
    ]

    joint_name = models.CharField(max_length=100, help_text="e.g., knee, shoulder_external")
    movement_axis = models.CharField(max_length=50, choices=MOVEMENT_AXIS)
    exercise_type = models.CharField(
        max_length=100,
        help_text="Type of exercise (e.g., squatting, pressing, rotating)"
    )
    
    # Safe ranges
    normal_min_angle = models.FloatField(help_text="Normal minimum safe angle in degrees")
    normal_max_angle = models.FloatField(help_text="Normal maximum safe angle in degrees")
    conservative_min_angle = models.FloatField(help_text="Conservative minimum (for recovery)")
    conservative_max_angle = models.FloatField(help_text="Conservative maximum (for recovery)")
    
    # Risk thresholds
    warning_threshold = models.FloatField(
        default=5.0,
        help_text="Degrees beyond safe range before warning"
    )
    critical_threshold = models.FloatField(
        default=15.0,
        help_text="Degrees beyond safe range before critical alert"
    )
    
    # Source and notes
    source = models.CharField(
        max_length=100,
        help_text="Source of safe range data (e.g., ISO standard, clinical study)"
    )
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.joint_name} - {self.exercise_type} ({self.normal_min_angle}° to {self.normal_max_angle}°)"

    class Meta:
        verbose_name = 'Joint Safety Profile'
        verbose_name_plural = 'Joint Safety Profiles'
        unique_together = ['joint_name', 'movement_axis', 'exercise_type']
        indexes = [
            models.Index(fields=['joint_name', 'is_active']),
        ]


class UserDifficultyPreference(models.Model):
    """
    Stores user's preferred difficulty progression strategy and tolerance levels.
    """
    PROGRESSION_STRATEGIES = [
        ('conservative', 'Conservative'),    # Slow steady progression
        ('moderate', 'Moderate'),            # Standard progression
        ('aggressive', 'Aggressive'),        # Fast progression
        ('adaptive', 'Adaptive'),            # AI-determined
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='difficulty_preference'
    )
    
    # Preferences
    progression_strategy = models.CharField(
        max_length=20,
        choices=PROGRESSION_STRATEGIES,
        default='adaptive'
    )
    min_score_threshold = models.FloatField(
        default=70.0,
        help_text="Minimum score before suggesting progression (0-100)"
    )
    consistency_threshold = models.FloatField(
        default=80.0,
        help_text="Consistency score required for progression (0-100)"
    )
    
    # Risk tolerance
    injury_risk_sensitivity = models.CharField(
        max_length=20,
        choices=[('conservative', 'Conservative'), ('moderate', 'Moderate'), ('aggressive', 'Aggressive')],
        default='moderate',
        help_text="How sensitive to injury warnings"
    )
    max_allowed_risk_level = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
        default='medium'
    )
    
    # Adaptation parameters
    sessions_before_review = models.IntegerField(
        default=5,
        help_text="Review difficulty after N sessions"
    )
    auto_adapt_enabled = models.BooleanField(default=True)
    notify_on_risk = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_progression_strategy_display()}"

    class Meta:
        verbose_name = 'User Difficulty Preference'
        verbose_name_plural = 'User Difficulty Preferences'
