"""
API Views for Advanced Features

REST API endpoints for:
1. Adaptive Difficulty System
2. Injury Risk Detection
3. Exercise Classification & Recommendations
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q

from exercises.models import Exercise
from advanced_features.models import (
    DifficultyAdaptation,
    InjuryRiskAlert,
    ExerciseClassification,
    UserDifficultyPreference,
)
from advanced_features.services import (
    AdaptiveDifficultySystem,
    InjuryRiskDetectionSystem,
    ExerciseClassificationSystem,
    analyze_user_progress,
)


class DifficultyAdaptationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing difficulty adaptation analysis.
    
    Endpoints:
    - GET /api/difficulty-adaptations/ - List all user's adaptations
    - GET /api/difficulty-adaptations/{id}/ - Get specific adaptation
    - POST /api/difficulty-adaptations/analyze/ - Analyze all exercises
    - POST /api/difficulty-adaptations/{id}/apply/ - Apply recommendation
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['exercise__name']
    ordering_fields = ['trend', 'average_score', 'updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        """Return only current user's adaptations"""
        return DifficultyAdaptation.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """
        Analyze all exercises for the user and generate recommendations.
        
        Returns:
            List of analysis results for all user exercises
        """
        try:
            difficulty_system = AdaptiveDifficultySystem(request.user)
            exercises = Exercise.objects.filter(is_active=True)
            
            results = []
            for exercise in exercises:
                analysis = difficulty_system.analyze_exercise(exercise)
                results.append(analysis)

            return Response({
                'user_id': request.user.id,
                'total_exercises_analyzed': len(results),
                'analyses': results,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Analysis failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def apply_recommendation(self, request, pk=None):
        """
        Apply the difficulty recommendation to an exercise.
        
        Updates the exercise difficulty level based on analysis.
        """
        try:
            adaptation = self.get_object()
            
            if not adaptation.recommended_difficulty:
                return Response(
                    {'error': 'No difficulty recommendation available'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            exercise = adaptation.exercise
            old_difficulty = exercise.difficulty_level
            new_difficulty = adaptation.recommended_difficulty
            
            exercise.difficulty_level = new_difficulty
            exercise.save()
            
            adaptation.adaptation_count += 1
            adaptation.save()

            return Response({
                'exercise_id': exercise.id,
                'exercise_name': exercise.name,
                'old_difficulty': old_difficulty,
                'new_difficulty': new_difficulty,
                'reason': adaptation.recommendation_reason,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Failed to apply recommendation: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def trending_down(self, request):
        """Get exercises where user's performance is declining"""
        declining = self.get_queryset().filter(
            Q(trend='declining') | Q(trend='slightly_declining')
        )
        
        from api.serializers_advanced_features import DifficultyAdaptationSerializer
        serializer = DifficultyAdaptationSerializer(declining, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def ready_for_progression(self, request):
        """Get exercises ready for difficulty increase"""
        ready = self.get_queryset().filter(
            recommendation='increase',
            average_score__gte=85.0
        )
        
        from api.serializers_advanced_features import DifficultyAdaptationSerializer
        serializer = DifficultyAdaptationSerializer(ready, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class InjuryRiskAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing injury risk alerts.
    
    Endpoints:
    - GET /api/injury-risks/ - List all user's alerts
    - GET /api/injury-risks/{id}/ - Get specific alert
    - GET /api/injury-risks/active/ - Get unresolved alerts
    - POST /api/injury-risks/{id}/acknowledge/ - Mark as acknowledged
    - POST /api/injury-risks/{id}/resolve/ - Mark as resolved
    """

    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['joint_name', 'alert_type']
    ordering_fields = ['risk_level', 'detected_at', 'severity_score']
    ordering = ['-detected_at']

    def get_queryset(self):
        """Return only current user's injury alerts"""
        return InjuryRiskAlert.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get unresolved injury risk alerts"""
        active_alerts = self.get_queryset().filter(is_resolved=False)
        
        from api.serializers_advanced_features import InjuryRiskAlertSerializer
        serializer = InjuryRiskAlertSerializer(active_alerts, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def critical(self, request):
        """Get all critical risk alerts"""
        critical_alerts = self.get_queryset().filter(risk_level='critical')
        
        from api.serializers_advanced_features import InjuryRiskAlertSerializer
        serializer = InjuryRiskAlertSerializer(critical_alerts, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Mark an alert as acknowledged"""
        try:
            alert = self.get_object()
            alert.is_acknowledged = True
            alert.save()
            
            from api.serializers_advanced_features import InjuryRiskAlertSerializer
            serializer = InjuryRiskAlertSerializer(alert)
            
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Failed to acknowledge: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark an alert as resolved"""
        try:
            alert = self.get_object()
            alert.is_resolved = True
            alert.resolution_notes = request.data.get('notes', '')
            alert.save()
            
            from api.serializers_advanced_features import InjuryRiskAlertSerializer
            serializer = InjuryRiskAlertSerializer(alert)
            
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Failed to resolve: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of injury risk alerts"""
        all_alerts = self.get_queryset()
        
        return Response({
            'total_alerts': all_alerts.count(),
            'active_alerts': all_alerts.filter(is_resolved=False).count(),
            'critical': all_alerts.filter(risk_level='critical', is_resolved=False).count(),
            'high': all_alerts.filter(risk_level='high', is_resolved=False).count(),
            'medium': all_alerts.filter(risk_level='medium', is_resolved=False).count(),
            'low': all_alerts.filter(risk_level='low', is_resolved=False).count(),
        }, status=status.HTTP_200_OK)


class ExerciseClassificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for exercise classification and recommendations.
    
    Endpoints:
    - GET /api/exercise-classification/{exercise_id}/profile/ - Get exercise profile
    - GET /api/exercise-classification/{exercise_id}/similar/ - Find similar exercises
    - GET /api/exercise-classification/recommendations/ - Get personalized recommendations
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='exercise/(?P<exercise_id>[^/.]+)/profile')
    def exercise_profile(self, request, exercise_id=None):
        """Get comprehensive profile of an exercise"""
        try:
            exercise = get_object_or_404(Exercise, id=exercise_id, is_active=True)
            profile = ExerciseClassificationSystem.get_exercise_profile(exercise)
            
            return Response(profile, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Failed to get exercise profile: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='exercise/(?P<exercise_id>[^/.]+)/similar')
    def similar_exercises(self, request, exercise_id=None):
        """Find exercises similar to the specified one"""
        try:
            exercise = get_object_or_404(Exercise, id=exercise_id, is_active=True)
            similarity_threshold = float(request.query_params.get('threshold', 0.7))
            max_results = int(request.query_params.get('limit', 5))
            
            similar = ExerciseClassificationSystem.find_similar_exercises(
                exercise,
                similarity_threshold=similarity_threshold,
                max_results=max_results
            )
            
            return Response({
                'source_exercise': {
                    'id': exercise.id,
                    'name': exercise.name,
                },
                'similar_exercises': [
                    {
                        'id': ex.id,
                        'name': ex.name,
                        'similarity_score': float(score),
                        'difficulty': ex.difficulty_level,
                    }
                    for ex, score in similar
                ],
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Failed to find similar exercises: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Get personalized exercise recommendations"""
        try:
            goal = request.query_params.get('goal', 'strength')
            difficulty = request.query_params.get('difficulty', 'medium')
            limit = int(request.query_params.get('limit', 5))
            
            exercises = ExerciseClassificationSystem.recommend_exercise_for_goal(
                goal=goal,
                difficulty=difficulty,
                max_results=limit
            )
            
            return Response({
                'goal': goal,
                'difficulty': difficulty,
                'recommendations': [
                    {
                        'id': ex.id,
                        'name': ex.name,
                        'description': ex.description[:100],
                        'muscle_groups': ex.muscle_groups,
                    }
                    for ex in exercises
                ],
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Failed to get recommendations: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProgressAnalysisViewSet(viewsets.ViewSet):
    """
    Comprehensive analysis of user progress across all advanced features.
    
    Endpoints:
    - GET /api/progress/analysis/ - Get comprehensive analysis
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def analysis(self, request):
        """Get comprehensive progress analysis for the user"""
        try:
            analysis = analyze_user_progress(request.user)
            return Response(analysis, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Analysis failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
