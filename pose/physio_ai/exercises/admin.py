from django.contrib import admin
from .models import Exercise


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'difficulty_level', 'duration_seconds', 'is_active', 'created_at']
    list_filter = ['difficulty_level', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'muscle_groups']
    readonly_fields = ['created_at', 'updated_at']
