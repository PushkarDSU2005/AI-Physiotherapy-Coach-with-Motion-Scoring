"""
API Views for Therapy Plans

Handles endpoints for generating, retrieving, and managing personalized therapy plans.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta

from therapy_plans.models import TherapyPlan, WeeklyExercise
from therapy_plans.services import generate_therapy_plan
from api.serializers_therapy_plans import (
    TherapyPlanDetailSerializer,
    TherapyPlanListSerializer,
    GeneratePlanSerializer,
    UpdateProgressSerializer,
    WeeklyPlanSerializer,
)


class TherapyPlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing therapy plans.

    Endpoints:
    - GET /api/therapy-plans/ - List user's therapy plans
    - POST /api/therapy-plans/ - Generate new plan
    - GET /api/therapy-plans/{id}/ - Get plan details
    - PUT /api/therapy-plans/{id}/ - Update plan
    - DELETE /api/therapy-plans/{id}/ - Delete plan
    - POST /api/therapy-plans/{id}/generate/ - Generate plan from request data
    - GET /api/therapy-plans/{id}/weekly-schedule/ - Get weekly schedule
    - POST /api/therapy-plans/{id}/update-progress/ - Update progress
    - GET /api/therapy-plans/{id}/export/ - Export plan as PDF/JSON
    - GET /api/therapy-plans/active/ - Get active plan
    - GET /api/therapy-plans/completed/ - Get completed plans
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['injury_type', 'title', 'description']
    ordering_fields = ['created_at', 'progress_score', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return only the current user's therapy plans"""
        return TherapyPlan.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return TherapyPlanListSerializer
        elif self.action == 'generate':
            return GeneratePlanSerializer
        elif self.action == 'update_progress':
            return UpdateProgressSerializer
        elif self.action == 'weekly_schedule':
            return WeeklyPlanSerializer
        else:
            return TherapyPlanDetailSerializer

    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        """
        Generate a new personalized therapy plan.

        Request body:
        {
            "injury_type": "knee pain",
            "injury_severity": "moderate",
            "duration_weeks": 4,
            "difficulty_level": "intermediate",
            "goals": ["Reduce pain", "Improve mobility"]
        }

        Returns:
            201: Newly created therapy plan
            400: Validation error
            500: Plan generation error
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Generate plan using service
            therapy_plan, message = generate_therapy_plan(
                user=request.user,
                injury_type=serializer.validated_data['injury_type'],
                injury_severity=serializer.validated_data.get('injury_severity', 'moderate'),
                duration_weeks=serializer.validated_data.get('duration_weeks', 4),
                difficulty_level=serializer.validated_data.get('difficulty_level', 'intermediate'),
                goals=serializer.validated_data.get('goals'),
            )

            if therapy_plan is None:
                return Response(
                    {'error': message},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Serialize and return the created plan
            response_serializer = TherapyPlanDetailSerializer(therapy_plan)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': f'Failed to generate plan: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='weekly-schedule')
    def weekly_schedule(self, request, pk=None):
        """
        Get the structured weekly schedule for a therapy plan.

        Returns:
            {
                "weeks": [
                    {
                        "week": 1,
                        "schedule": {
                            "monday": [...exercises...],
                            "tuesday": [...],
                            ...
                        },
                        "notes": "Week-specific notes"
                    },
                    ...
                ]
            }
        """
        therapy_plan = self.get_object()

        try:
            # Get weekly exercises organized by week and day
            weekly_exercises = WeeklyExercise.objects.filter(
                therapy_plan=therapy_plan
            ).order_by('week_number', 'day_of_week', 'order')

            # Organize by week
            weeks_data = {}
            for exercise in weekly_exercises:
                week_num = exercise.week_number
                if week_num not in weeks_data:
                    weeks_data[week_num] = {
                        'week': week_num,
                        'schedule': {},
                        'notes': '',
                    }

                day = exercise.day_of_week
                if day not in weeks_data[week_num]['schedule']:
                    weeks_data[week_num]['schedule'][day] = []

                weeks_data[week_num]['schedule'][day].append({
                    'id': exercise.id,
                    'name': exercise.exercise_name,
                    'sets': exercise.sets,
                    'reps': exercise.reps,
                    'duration_minutes': exercise.duration_minutes,
                    'rest_seconds': exercise.rest_seconds,
                    'description': exercise.description,
                    'modifications': exercise.modifications,
                    'precautions': exercise.precautions,
                    'benefits': exercise.benefits,
                    'is_rest_day': exercise.is_rest_day,
                })

            # Extract notes from weekly_plan if available
            weekly_plan = therapy_plan.weekly_plan
            for week_num, week_data in weeks_data.items():
                week_key = f'week_{week_num}'
                if isinstance(weekly_plan, dict) and week_key in weekly_plan:
                    week_data['notes'] = weekly_plan[week_key].get('notes', '')

            response_data = {
                'plan_id': therapy_plan.id,
                'injury_type': therapy_plan.injury_type,
                'title': therapy_plan.title,
                'total_weeks': therapy_plan.duration_weeks,
                'weeks': sorted(weeks_data.values(), key=lambda x: x['week'])
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Failed to retrieve schedule: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='update-progress')
    def update_progress(self, request, pk=None):
        """
        Update the progress score and status of a therapy plan.

        Request body:
        {
            "progress_score": 75.5,
            "status": "active",
            "notes": "Feeling better, pain reduced by 30%"
        }

        Returns:
            200: Updated plan
            400: Validation error
        """
        therapy_plan = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Update progress
            therapy_plan.progress_score = serializer.validated_data['progress_score']
            
            if 'status' in serializer.validated_data:
                therapy_plan.status = serializer.validated_data['status']

            therapy_plan.save()

            response_serializer = TherapyPlanDetailSerializer(therapy_plan)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Failed to update progress: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='export')
    def export(self, request, pk=None):
        """
        Export therapy plan as JSON or other format.

        Query parameters:
            format: 'json' (default), 'pdf' (requires reportlab)

        Returns:
            Plan data in requested format
        """
        therapy_plan = self.get_object()
        export_format = request.query_params.get('format', 'json')

        try:
            if export_format == 'json':
                serializer = TherapyPlanDetailSerializer(therapy_plan)
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )
            elif export_format == 'pdf':
                # TODO: Implement PDF export using reportlab
                return Response(
                    {'error': 'PDF export not yet implemented'},
                    status=status.HTTP_501_NOT_IMPLEMENTED
                )
            else:
                return Response(
                    {'error': f'Unsupported format: {export_format}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response(
                {'error': f'Failed to export plan: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='active')
    def active_plans(self, request):
        """Get the user's active therapy plans"""
        active_plans = self.get_queryset().filter(status='active')
        serializer = TherapyPlanListSerializer(active_plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='completed')
    def completed_plans(self, request):
        """Get the user's completed therapy plans"""
        completed_plans = self.get_queryset().filter(status='completed')
        serializer = TherapyPlanListSerializer(completed_plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='comparison')
    def comparison(self, request, pk=None):
        """
        Compare current plan with another plan.

        Query parameters:
            compare_with: ID of another therapy plan to compare

        Returns:
            Comparison metrics
        """
        current_plan = self.get_object()
        compare_with_id = request.query_params.get('compare_with')

        if not compare_with_id:
            return Response(
                {'error': 'compare_with parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            compare_plan = TherapyPlan.objects.get(
                id=compare_with_id,
                user=request.user
            )

            comparison_data = {
                'current_plan': {
                    'id': current_plan.id,
                    'title': current_plan.title,
                    'injury_type': current_plan.injury_type,
                    'duration_weeks': current_plan.duration_weeks,
                    'difficulty_level': current_plan.difficulty_level,
                    'progress_score': current_plan.progress_score,
                    'goals_count': len(current_plan.goals),
                },
                'compare_plan': {
                    'id': compare_plan.id,
                    'title': compare_plan.title,
                    'injury_type': compare_plan.injury_type,
                    'duration_weeks': compare_plan.duration_weeks,
                    'difficulty_level': compare_plan.difficulty_level,
                    'progress_score': compare_plan.progress_score,
                    'goals_count': len(compare_plan.goals),
                },
                'differences': {
                    'duration_diff': current_plan.duration_weeks - compare_plan.duration_weeks,
                    'progress_diff': current_plan.progress_score - compare_plan.progress_score,
                    'goals_diff': len(current_plan.goals) - len(compare_plan.goals),
                }
            }

            return Response(comparison_data, status=status.HTTP_200_OK)

        except TherapyPlan.DoesNotExist:
            return Response(
                {'error': 'Comparison plan not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to compare plans: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        """Override create to use generate method"""
        return self.generate(request)

    def destroy(self, request, *args, **kwargs):
        """Archive instead of deleting"""
        therapy_plan = self.get_object()
        therapy_plan.status = 'archived'
        therapy_plan.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WeeklyExerciseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing individual weekly exercises.

    Endpoints:
    - GET /api/weekly-exercises/ - List exercises
    - GET /api/weekly-exercises/{id}/ - Get exercise details
    - PUT /api/weekly-exercises/{id}/ - Update exercise
    - DELETE /api/weekly-exercises/{id}/ - Delete exercise
    """

    permission_classes = [IsAuthenticated]
    serializer_class = WeeklyExerciseSerializer

    def get_queryset(self):
        """Return weekly exercises for user's therapy plans"""
        return WeeklyExercise.objects.filter(
            therapy_plan__user=self.request.user
        )

    @method_decorator(cache_page(60))  # Cache for 1 minute
    def list(self, request, *args, **kwargs):
        """List weekly exercises with caching"""
        return super().list(request, *args, **kwargs)
