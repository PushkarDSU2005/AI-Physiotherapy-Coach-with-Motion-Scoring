"""
Django Admin Interface for Advanced Features
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q

from advanced_features.models import (
    DifficultyAdaptation,
    InjuryRiskAlert,
    ExerciseClassification,
    JointSafetyProfile,
    UserDifficultyPreference,
)


@admin.register(DifficultyAdaptation)
class DifficultyAdaptationAdmin(admin.ModelAdmin):
    """Admin interface for Difficulty Adaptations"""
    
    list_display = [
        'user_link',
        'exercise_link',
        'average_score_badge',
        'trend_badge',
        'recommendation_badge',
        'consistency_score',
        'total_sessions',
        'last_adapted_at',
    ]
    list_filter = [
        'trend',
        'recommendation',
        'recommended_difficulty',
        'last_adapted_at',
    ]
    search_fields = ['user__username', 'exercise__name']
    readonly_fields = [
        'last_10_scores',
        'average_score',
        'min_score',
        'max_score',
        'trend_slope',
        'consistency_score',
        'created_at',
        'updated_at',
        'last_adapted_at',
    ]
    
    fieldsets = (
        ('User & Exercise', {
            'fields': ('user', 'exercise')
        }),
        ('Performance Metrics', {
            'fields': (
                'last_10_scores',
                'average_score',
                'min_score',
                'max_score',
                'consistency_score',
                'total_sessions',
                'days_since_last',
            )
        }),
        ('Trend Analysis', {
            'fields': (
                'trend',
                'trend_slope',
            )
        }),
        ('Recommendation', {
            'fields': (
                'recommendation',
                'recommended_difficulty',
                'recommendation_reason',
            )
        }),
        ('Tracking', {
            'fields': (
                'adaptation_count',
                'last_adapted_at',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        """Display user with link"""
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def exercise_link(self, obj):
        """Display exercise with link"""
        url = reverse('admin:exercises_exercise_change', args=[obj.exercise.id])
        return format_html('<a href="{}">{}</a>', url, obj.exercise.name)
    exercise_link.short_description = 'Exercise'
    
    def average_score_badge(self, obj):
        """Display average score with color coding"""
        if obj.average_score >= 85:
            color = 'green'
            text = 'Excellent'
        elif obj.average_score >= 75:
            color = 'blue'
            text = 'Good'
        elif obj.average_score >= 65:
            color = 'orange'
            text = 'Fair'
        else:
            color = 'red'
            text = 'Needs Work'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">'
            '{:.1f}% ({})</span>',
            color,
            obj.average_score,
            text
        )
    average_score_badge.short_description = 'Avg Score'
    
    def trend_badge(self, obj):
        """Display trend with arrow icon"""
        arrows = {
            'improving': '↗ Improving',
            'slightly_improving': '→ Slight ↗',
            'stable': '→ Stable',
            'slightly_declining': '↘ Slight',
            'declining': '↘ Declining',
            'plateaued': '⟺ Plateaued',
        }
        
        colors = {
            'improving': 'green',
            'declining': 'red',
            'stable': 'blue',
        }
        
        trend_text = arrows.get(obj.trend, obj.trend)
        color = colors.get(obj.trend, 'gray')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            trend_text
        )
    trend_badge.short_description = 'Trend'
    
    def recommendation_badge(self, obj):
        """Display recommendation with badge"""
        colors = {
            'increase': 'green',
            'maintain': 'blue',
            'decrease': 'orange',
            'modify': 'purple',
            'progress': 'teal',
        }
        
        color = colors.get(obj.recommendation, 'gray')
        text = obj.get_recommendation_display()
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">'
            '{}</span>',
            color,
            text
        )
    recommendation_badge.short_description = 'Recommendation'


@admin.register(InjuryRiskAlert)
class InjuryRiskAlertAdmin(admin.ModelAdmin):
    """Admin interface for Injury Risk Alerts"""
    
    list_display = [
        'user_link',
        'joint_name',
        'risk_level_badge',
        'angle_display',
        'alert_type',
        'is_acknowledged',
        'is_resolved',
        'detected_at',
    ]
    list_filter = [
        'risk_level',
        'alert_type',
        'is_acknowledged',
        'is_resolved',
        'detected_at',
    ]
    search_fields = ['user__username', 'joint_name', 'session_exercise__exercise__name']
    readonly_fields = [
        'user',
        'session_exercise',
        'pose_analysis',
        'severity_score',
        'detected_at',
        'resolved_at',
        'description_display',
    ]
    
    fieldsets = (
        ('Alert Details', {
            'fields': (
                'user',
                'alert_type',
                'risk_level',
                'joint_name',
                'severity_score',
            )
        }),
        ('Angle Information', {
            'fields': (
                'current_angle',
                'safe_range_min',
                'safe_range_max',
                'angle_exceeded_by',
            )
        }),
        ('Session Info', {
            'fields': (
                'session_exercise',
                'pose_analysis',
            )
        }),
        ('Recommendation', {
            'fields': ('recommendation',)
        }),
        ('Resolution', {
            'fields': (
                'is_acknowledged',
                'is_resolved',
                'resolution_notes',
            )
        }),
        ('Timestamps', {
            'fields': (
                'detected_at',
                'resolved_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_acknowledged', 'mark_resolved', 'mark_unresolved']
    
    def user_link(self, obj):
        """Display user with link"""
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def risk_level_badge(self, obj):
        """Display risk level with color coding"""
        colors = {
            'critical': '#e74c3c',
            'high': '#e67e22',
            'medium': '#f39c12',
            'low': '#27ae60',
        }
        
        color = colors.get(obj.risk_level, 'gray')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; '
            'font-weight: bold;">{}</span>',
            color,
            obj.get_risk_level_display()
        )
    risk_level_badge.short_description = 'Risk Level'
    
    def angle_display(self, obj):
        """Display angle information"""
        if obj.current_angle is not None:
            return f"{obj.current_angle:.1f}° (safe: {obj.safe_range_min}°-{obj.safe_range_max}°)"
        return "N/A"
    angle_display.short_description = 'Angle'
    
    def description_display(self, obj):
        """Display description in readonly field"""
        return format_html('<p style="background-color: #f5f5f5; padding: 10px; border-radius: 3px;">'
                          '{}</p>', obj.description)
    description_display.short_description = 'Description'
    
    def mark_acknowledged(self, request, queryset):
        """Bulk action: mark as acknowledged"""
        updated = queryset.update(is_acknowledged=True)
        self.message_user(request, f"{updated} alerts marked as acknowledged.")
    mark_acknowledged.short_description = "Mark selected as acknowledged"
    
    def mark_resolved(self, request, queryset):
        """Bulk action: mark as resolved"""
        from django.utils import timezone
        updated = queryset.update(is_resolved=True, resolved_at=timezone.now())
        self.message_user(request, f"{updated} alerts marked as resolved.")
    mark_resolved.short_description = "Mark selected as resolved"
    
    def mark_unresolved(self, request, queryset):
        """Bulk action: mark as unresolved"""
        updated = queryset.update(is_resolved=False, resolved_at=None)
        self.message_user(request, f"{updated} alerts marked as unresolved.")
    mark_unresolved.short_description = "Mark selected as unresolved"


@admin.register(ExerciseClassification)
class ExerciseClassificationAdmin(admin.ModelAdmin):
    """Admin interface for Exercise Classifications"""
    
    list_display = [
        'exercise_link',
        'classification_type_display',
        'classification_value',
        'weight',
        'created_at',
    ]
    list_filter = [
        'classification_type',
        'created_at',
    ]
    search_fields = ['exercise__name', 'classification_value']
    readonly_fields = [
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Exercise', {
            'fields': ('exercise',)
        }),
        ('Classification', {
            'fields': (
                'classification_type',
                'classification_value',
                'weight',
            )
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def exercise_link(self, obj):
        """Display exercise with link"""
        url = reverse('admin:exercises_exercise_change', args=[obj.exercise.id])
        return format_html('<a href="{}">{}</a>', url, obj.exercise.name)
    exercise_link.short_description = 'Exercise'
    
    def classification_type_display(self, obj):
        """Display classification type nicely"""
        return obj.get_classification_type_display()
    classification_type_display.short_description = 'Type'


@admin.register(JointSafetyProfile)
class JointSafetyProfileAdmin(admin.ModelAdmin):
    """Admin interface for Joint Safety Profiles"""
    
    list_display = [
        'joint_name',
        'exercise_type',
        'movement_axis',
        'angle_range_display',
        'is_active',
        'source',
    ]
    list_filter = [
        'is_active',
        'joint_name',
        'movement_axis',
    ]
    search_fields = ['joint_name', 'exercise_type', 'source']
    readonly_fields = [
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Joint Information', {
            'fields': (
                'joint_name',
                'movement_axis',
                'exercise_type',
            )
        }),
        ('Safe Angle Ranges', {
            'fields': (
                'normal_min_angle',
                'normal_max_angle',
                'conservative_min_angle',
                'conservative_max_angle',
            )
        }),
        ('Risk Thresholds', {
            'fields': (
                'warning_threshold',
                'critical_threshold',
            )
        }),
        ('Source & Notes', {
            'fields': (
                'source',
                'notes',
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def angle_range_display(self, obj):
        """Display angle range"""
        return format_html(
            '{:.0f}°-{:.0f}° (warn: ±{:.0f}°, crit: ±{:.0f}°)',
            obj.normal_min_angle,
            obj.normal_max_angle,
            obj.warning_threshold,
            obj.critical_threshold
        )
    angle_range_display.short_description = 'Angle Range'


@admin.register(UserDifficultyPreference)
class UserDifficultyPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for User Difficulty Preferences"""
    
    list_display = [
        'user_link',
        'progression_strategy',
        'min_score_threshold',
        'auto_adapt_enabled',
        'injury_risk_sensitivity',
    ]
    list_filter = [
        'progression_strategy',
        'auto_adapt_enabled',
        'injury_risk_sensitivity',
    ]
    search_fields = ['user__username']
    readonly_fields = [
        'created_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Progression Settings', {
            'fields': (
                'progression_strategy',
                'min_score_threshold',
                'consistency_threshold',
                'sessions_before_review',
            )
        }),
        ('Risk & Safety', {
            'fields': (
                'injury_risk_sensitivity',
                'max_allowed_risk_level',
                'notify_on_risk',
            )
        }),
        ('Automation', {
            'fields': ('auto_adapt_enabled',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        """Display user with link"""
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
