"""
Serializers for Advanced Features API
"""

from rest_framework import serializers
from advanced_features.models import (
    DifficultyAdaptation,
    InjuryRiskAlert,
    ExerciseClassification,
    JointSafetyProfile,
    UserDifficultyPreference,
)
from exercises.models import Exercise


class DifficultyAdaptationSerializer(serializers.ModelSerializer):
    """Serializer for DifficultyAdaptation model"""
    
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = DifficultyAdaptation
        fields = [
            'id',
            'user',
            'user_username',
            'exercise',
            'exercise_name',
            'last_10_scores',
            'average_score',
            'min_score',
            'max_score',
            'trend',
            'trend_slope',
            'consistency_score',
            'recommendation',
            'recommended_difficulty',
            'recommendation_reason',
            'total_sessions',
            'days_since_last',
            'adaptation_count',
            'last_adapted_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_adapted_at']


class InjuryRiskAlertSerializer(serializers.ModelSerializer):
    """Serializer for InjuryRiskAlert model"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    exercise_name = serializers.CharField(source='session_exercise.exercise.name', read_only=True)
    days_since = serializers.SerializerMethodField()

    class Meta:
        model = InjuryRiskAlert
        fields = [
            'id',
            'user',
            'user_username',
            'alert_type',
            'risk_level',
            'joint_name',
            'current_angle',
            'safe_range_min',
            'safe_range_max',
            'angle_exceeded_by',
            'severity_score',
            'description',
            'recommendation',
            'is_acknowledged',
            'is_resolved',
            'resolution_notes',
            'detected_at',
            'resolved_at',
            'exercise_name',
            'days_since',
        ]
        read_only_fields = [
            'id',
            'detected_at',
            'resolved_at',
            'severity_score',
            'description',
        ]

    def get_days_since(self, obj):
        """Calculate days since alert was detected"""
        from datetime import datetime, timezone
        if obj.detected_at:
            delta = datetime.now(timezone.utc) - obj.detected_at
            return delta.days
        return None


class ExerciseClassificationSerializer(serializers.ModelSerializer):
    """Serializer for ExerciseClassification model"""
    
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)
    classification_type_display = serializers.CharField(
        source='get_classification_type_display',
        read_only=True
    )

    class Meta:
        model = ExerciseClassification
        fields = [
            'id',
            'exercise',
            'exercise_name',
            'classification_type',
            'classification_type_display',
            'classification_value',
            'weight',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class JointSafetyProfileSerializer(serializers.ModelSerializer):
    """Serializer for JointSafetyProfile model"""

    class Meta:
        model = JointSafetyProfile
        fields = [
            'id',
            'joint_name',
            'movement_axis',
            'exercise_type',
            'normal_min_angle',
            'normal_max_angle',
            'conservative_min_angle',
            'conservative_max_angle',
            'warning_threshold',
            'critical_threshold',
            'source',
            'notes',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserDifficultyPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for UserDifficultyPreference model"""

    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserDifficultyPreference
        fields = [
            'id',
            'user',
            'user_username',
            'progression_strategy',
            'min_score_threshold',
            'consistency_threshold',
            'injury_risk_sensitivity',
            'max_allowed_risk_level',
            'sessions_before_review',
            'auto_adapt_enabled',
            'notify_on_risk',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
