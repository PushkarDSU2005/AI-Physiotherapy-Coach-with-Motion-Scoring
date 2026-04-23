from django.contrib import admin
from .models import AIModel, PoseAnalysis, AIFeedback


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'model_type', 'accuracy_score', 'is_active']
    list_filter = ['model_type', 'is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PoseAnalysis)
class PoseAnalysisAdmin(admin.ModelAdmin):
    list_display = ['session_exercise', 'frame_number', 'form_score', 'confidence_level', 'timestamp']
    list_filter = ['form_score', 'timestamp']
    search_fields = ['session_exercise__session__title']
    readonly_fields = ['timestamp']


@admin.register(AIFeedback)
class AIFeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'overall_score', 'generated_at']
    list_filter = ['overall_score', 'generated_at']
    search_fields = ['user__username', 'feedback_text']
    readonly_fields = ['generated_at']
