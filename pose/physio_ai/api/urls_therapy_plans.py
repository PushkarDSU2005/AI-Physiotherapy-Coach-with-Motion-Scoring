"""
URL configuration for therapy_plans app.

Routes:
    GET  /api/therapy-plans/               - List all user's therapy plans
    POST /api/therapy-plans/               - Generate new therapy plan
    GET  /api/therapy-plans/<id>/          - Retrieve specific plan
    PUT  /api/therapy-plans/<id>/          - Update plan
    DELETE /api/therapy-plans/<id>/        - Archive plan
    GET  /api/therapy-plans/active/        - Get active plans
    GET  /api/therapy-plans/completed/     - Get completed plans
    GET  /api/therapy-plans/<id>/weekly-schedule/  - Get weekly schedule
    POST /api/therapy-plans/<id>/update-progress/  - Update progress
    GET  /api/therapy-plans/<id>/export/   - Export plan
    GET  /api/therapy-plans/<id>/comparison/  - Compare with other plan
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views_therapy_plans import TherapyPlanViewSet, WeeklyExerciseViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'therapy-plans', TherapyPlanViewSet, basename='therapyplan')
router.register(r'weekly-exercises', WeeklyExerciseViewSet, basename='weeklyexercise')

urlpatterns = [
    path('', include(router.urls)),
]
