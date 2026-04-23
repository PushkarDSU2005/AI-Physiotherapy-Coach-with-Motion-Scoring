from django.contrib import admin
from django.utils.html import format_html
from therapy_plans.models import TherapyPlan, WeeklyExercise


@admin.register(TherapyPlan)
class TherapyPlanAdmin(admin.ModelAdmin):
    """Admin interface for Therapy Plans"""
    
    list_display = [
        'id',
        'user',
        'injury_type',
        'status_badge',
        'duration_weeks',
        'difficulty_level',
        'progress_display',
        'created_at',
    ]
    list_filter = ['status', 'difficulty_level', 'created_at']
    search_fields = ['user__username', 'injury_type', 'title']
    readonly_fields = ['created_at', 'updated_at', 'generated_at', 'gpt_response']
    
    fieldsets = (
        ('User & Injury Information', {
            'fields': ('user', 'injury_type', 'status', 'title', 'description')
        }),
        ('Plan Configuration', {
            'fields': (
                'duration_weeks',
                'difficulty_level',
                'start_date',
                'end_date',
                'progress_score',
            )
        }),
        ('Plan Content', {
            'fields': ('goals', 'precautions', 'progression_strategy', 'weekly_plan'),
            'classes': ('collapse',)
        }),
        ('Performance Data', {
            'fields': ('created_from_performance',),
            'classes': ('collapse',)
        }),
        ('AI Generated Data', {
            'fields': ('gpt_response',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'generated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'draft': '#999999',
            'active': '#00aa00',
            'completed': '#0000aa',
            'archived': '#aaaaaa',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#000000'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def progress_display(self, obj):
        """Display progress as a visual bar"""
        progress = int(obj.progress_score)
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}px; background-color: #00aa00; height: 20px; border-radius: 3px; text-align: center; color: white;">'
            '{}</div></div>',
            progress,
            f'{progress}%'
        )
    progress_display.short_description = 'Progress'
    
    actions = ['mark_as_completed', 'mark_as_active', 'archive_plans']
    
    def mark_as_completed(self, request, queryset):
        """Mark selected plans as completed"""
        queryset.update(status='completed')
    mark_as_completed.short_description = "Mark selected plans as completed"
    
    def mark_as_active(self, request, queryset):
        """Mark selected plans as active"""
        queryset.update(status='active')
    mark_as_active.short_description = "Mark selected plans as active"
    
    def archive_plans(self, request, queryset):
        """Archive selected plans"""
        queryset.update(status='archived')
    archive_plans.short_description = "Archive selected plans"


@admin.register(WeeklyExercise)
class WeeklyExerciseAdmin(admin.ModelAdmin):
    """Admin interface for Weekly Exercises"""
    
    list_display = [
        'id',
        'therapy_plan',
        'week_number',
        'day_of_week',
        'exercise_name',
        'sets_and_reps',
        'is_rest_day',
        'order',
    ]
    list_filter = ['week_number', 'day_of_week', 'is_rest_day', 'therapy_plan__user']
    search_fields = ['exercise_name', 'therapy_plan__user__username', 'therapy_plan__injury_type']
    
    fieldsets = (
        ('Assignment', {
            'fields': ('therapy_plan', 'week_number', 'day_of_week', 'order')
        }),
        ('Exercise Details', {
            'fields': (
                'exercise',
                'exercise_name',
                'description',
                'sets',
                'reps',
                'duration_minutes',
                'rest_seconds',
            )
        }),
        ('Guidance & Safety', {
            'fields': ('modifications', 'precautions', 'benefits'),
            'classes': ('collapse',)
        }),
        ('Progression', {
            'fields': ('progression_week', 'progression_notes'),
            'classes': ('collapse',)
        }),
        ('Options', {
            'fields': ('is_rest_day',)
        }),
    )
    
    def sets_and_reps(self, obj):
        """Display sets and reps"""
        if obj.is_rest_day:
            return format_html('<em style="color: #999;">Rest Day</em>')
        return f"{obj.sets}x{obj.reps}"
    sets_and_reps.short_description = 'Sets × Reps'
    
    actions = ['mark_as_rest_day', 'unmark_rest_day']
    
    def mark_as_rest_day(self, request, queryset):
        """Mark selected exercises as rest days"""
        queryset.update(is_rest_day=True)
    mark_as_rest_day.short_description = "Mark as rest day"
    
    def unmark_rest_day(self, request, queryset):
        """Unmark as rest day"""
        queryset.update(is_rest_day=False)
    unmark_rest_day.short_description = "Unmark as rest day"
