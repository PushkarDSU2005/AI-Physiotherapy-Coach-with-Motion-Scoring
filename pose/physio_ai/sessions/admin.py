from django.contrib import admin
from .models import Session, SessionExercise


class SessionExerciseInline(admin.TabularInline):
    """Inline admin for session exercises."""
    model = SessionExercise
    extra = 1
    fields = ['exercise', 'order', 'status', 'reps_completed', 'form_score']


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'start_time', 'duration_minutes', 'created_at']
    list_filter = ['status', 'start_time', 'created_at']
    search_fields = ['user__username', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SessionExerciseInline]


@admin.register(SessionExercise)
class SessionExerciseAdmin(admin.ModelAdmin):
    list_display = ['session', 'exercise', 'order', 'status', 'form_score']
    list_filter = ['status', 'completed_at']
    search_fields = ['session__title', 'exercise__name']
