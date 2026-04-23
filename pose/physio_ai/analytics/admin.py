from django.contrib import admin
from .models import UserProgress, DailyMetrics, ExerciseStatistics, Report


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_sessions_completed', 'average_form_score', 'current_streak_days']
    list_filter = ['updated_at']
    search_fields = ['user__username']
    readonly_fields = ['updated_at']


@admin.register(DailyMetrics)
class DailyMetricsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'sessions_completed', 'exercises_completed', 'average_form_score']
    list_filter = ['date']
    search_fields = ['user__username']
    date_hierarchy = 'date'


@admin.register(ExerciseStatistics)
class ExerciseStatisticsAdmin(admin.ModelAdmin):
    list_display = ['exercise_name', 'total_times_completed', 'average_form_score', 'popularity_score']
    list_filter = ['updated_at']
    search_fields = ['exercise_name']
    readonly_fields = ['updated_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'report_type', 'title', 'start_date', 'end_date', 'generated_at']
    list_filter = ['report_type', 'generated_at']
    search_fields = ['user__username', 'title']
    readonly_fields = ['generated_at']
