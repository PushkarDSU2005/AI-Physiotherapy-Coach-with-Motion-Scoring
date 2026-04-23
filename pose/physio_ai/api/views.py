"""
Django REST Framework Views for Physio AI API

Endpoints for session management, pose analysis, scoring, feedback, and progress tracking.
"""

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Avg, Count, Q, Max, Min
from datetime import timedelta
import json

from .serializers import (
    SessionStartSerializer, SessionDetailSerializer, SessionListSerializer,
    SessionExerciseInputSerializer, SessionExerciseDetailSerializer,
    PoseAngleSubmitSerializer, PoseAnalysisDetailSerializer,
    ScoreCalculationResultSerializer, FeedbackSerializer,
    UserProgressSerializer, ProgressHistorySerializer, DailyMetricsSerializer,
    ExerciseProgressSerializer, StatusSerializer, ErrorSerializer
)

User = get_user_model()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_session_dict(session):
    """Convert session model instance to dictionary."""
    exercises = session.exercise_records.all().select_related('exercise')
    exercise_list = []
    
    for se in exercises:
        exercise_list.append({
            'id': se.id,
            'exercise_id': se.exercise_id,
            'exercise_name': se.exercise.name,
            'order_in_session': se.order_in_session,
            'status': se.status,
            'reps_performed': se.reps_performed,
            'sets_performed': se.sets_performed,
            'target_reps': se.target_reps,
            'form_score': se.form_score,
            'consistency_score': se.consistency_score,
            'range_of_motion_percentage': se.range_of_motion_percentage,
            'pain_during_exercise': se.pain_during_exercise,
            'form_issues_detected': se.form_issues_detected,
            'ai_feedback_for_exercise': se.ai_feedback_for_exercise,
            'user_difficulty_rating': se.user_difficulty_rating,
        })
    
    return {
        'id': session.id,
        'title': session.title,
        'description': session.description,
        'start_time': session.start_time,
        'end_time': session.end_time,
        'status': session.status,
        'session_type': session.session_type,
        'scheduled_duration_minutes': session.scheduled_duration_minutes,
        'overall_session_score': session.overall_session_score,
        'average_exercise_score': session.average_exercise_score,
        'completion_percentage': session.completion_percentage,
        'exercises': exercise_list,
        'pain_level_before': session.pain_level_before,
        'pain_level_after': session.pain_level_after,
        'ai_generated_feedback': session.ai_generated_feedback,
        'therapist_feedback': session.therapist_feedback,
        'improvement_areas': session.improvement_areas,
        'positive_feedback_points': session.positive_feedback_points,
        'video_recording_available': session.video_recording_available,
        'device_tracking_confidence': session.device_tracking_confidence,
    }


def calculate_exercise_score(session_exercise):
    """
    Calculate comprehensive form score for an exercise.
    
    Combines:
    - Form Score (50%): How correct the form was
    - Consistency Score (30%): How stable/consistent throughout
    - Range of Motion (20%): How complete the movement was
    """
    if not session_exercise.form_score or not session_exercise.consistency_score:
        return None
    
    rom = session_exercise.range_of_motion_percentage or 100
    score = (
        (session_exercise.form_score * 0.5) +
        (session_exercise.consistency_score * 0.3) +
        (rom * 0.2)
    )
    return round(score, 1)


def generate_ai_feedback(session):
    """Generate AI feedback based on session performance."""
    if not session.status == 'completed':
        return None
    
    exercises = session.exercise_records.filter(status='completed')
    if not exercises.exists():
        return "No exercises were completed in this session."
    
    avg_score = exercises.aggregate(Avg('form_score'))['form_score__avg']
    pain_before = session.pain_level_before
    pain_after = session.pain_level_after
    
    feedback_parts = []
    
    # Overall performance
    if avg_score >= 85:
        feedback_parts.append("Excellent form! Your technique is very solid.")
    elif avg_score >= 75:
        feedback_parts.append("Good effort! Keep working on consistency.")
    elif avg_score >= 65:
        feedback_parts.append("You're making progress. Focus on form quality.")
    else:
        feedback_parts.append("Great motivation! Let's work on proper form.")
    
    # Pain feedback
    if pain_before is not None and pain_after is not None:
        if pain_before > pain_after:
            improvement = pain_before - pain_after
            feedback_parts.append(
                f"You showed pain improvement of {improvement} points! Keep it up."
            )
        elif pain_after > pain_before:
            feedback_parts.append(
                "Pain increased slightly. Ensure proper form and rest between sets."
            )
        else:
            feedback_parts.append("Pain levels remained stable.")
    
    # Common issues
    issues = {}
    for se in exercises:
        if se.form_issues_detected:
            for issue in se.form_issues_detected:
                issue_name = issue.get('issue', 'Unknown')
                issues[issue_name] = issues.get(issue_name, 0) + 1
    
    if issues:
        top_issue = max(issues, key=issues.get)
        feedback_parts.append(f"Most common form issue: {top_issue}. Let's address this next session.")
    
    return " ".join(feedback_parts)


def generate_improvement_areas(session):
    """Identify specific areas for improvement."""
    improvements = []
    
    exercises = session.exercise_records.filter(status='completed')
    if not exercises.exists():
        return []
    
    # Find exercises with low form scores
    poor_form = exercises.filter(form_score__lt=70)
    if poor_form.exists():
        for se in poor_form:
            improvements.append({
                'exercise': se.exercise.name,
                'issue': 'Form quality',
                'score': se.form_score,
                'recommendation': f"Focus on proper positioning for {se.exercise.name}"
            })
    
    # Find exercises with poor consistency
    inconsistent = exercises.filter(consistency_score__lt=70)
    if inconsistent.exists():
        for se in inconsistent:
            improvements.append({
                'exercise': se.exercise.name,
                'issue': 'Inconsistent form',
                'score': se.consistency_score,
                'recommendation': f"Slow down and maintain consistent form throughout {se.exercise.name}"
            })
    
    return improvements


# ============================================================================
# SESSION MANAGEMENT ENDPOINTS
# ============================================================================

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def start_session(request):
    """
    Start a new physiotherapy session.
    
    POST /api/sessions/start/
    
    Request:
    {
        "title": "Daily Shoulder Work",
        "description": "Focus on shoulder stability",
        "session_type": "home_unsupervised",
        "scheduled_duration_minutes": 30,
        "pain_level_before": 4
    }
    
    Response:
    {
        "status": "success",
        "session_id": 15,
        "message": "Session started successfully",
        "data": {...session details...}
    }
    """
    serializer = SessionStartSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                'status': 'error',
                'error': 'Invalid input',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Import here to avoid circular imports
    from sessions.models import Session
    
    try:
        session = Session.objects.create(
            user=request.user,
            title=serializer.validated_data.get('title', 'Session'),
            description=serializer.validated_data.get('description', ''),
            start_time=timezone.now(),
            status='in_progress',
            session_type=serializer.validated_data.get('session_type', 'home_unsupervised'),
            scheduled_duration_minutes=serializer.validated_data.get('scheduled_duration_minutes', 30),
            pain_level_before=serializer.validated_data.get('pain_level_before'),
        )
        
        # Assign therapist if provided
        therapist_id = serializer.validated_data.get('assigned_therapist_id')
        if therapist_id:
            session.assigned_therapist_id = therapist_id
            session.save()
        
        response_serializer = SessionDetailSerializer(get_session_dict(session))
        
        return Response(
            {
                'status': 'success',
                'session_id': session.id,
                'message': 'Session started successfully',
                'data': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return Response(
            {
                'status': 'error',
                'error': 'Failed to start session',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_active_session(request):
    """
    Get the current active session for the user.
    
    GET /api/sessions/active/
    
    Response:
    {
        "status": "success",
        "data": {...session details...}
    }
    """
    from sessions.models import Session
    
    # Find the most recent in-progress session
    active_session = Session.objects.filter(
        user=request.user,
        status='in_progress'
    ).order_by('-start_time').first()
    
    if not active_session:
        return Response(
            {
                'status': 'error',
                'message': 'No active session found',
                'session_id': None
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    response_serializer = SessionDetailSerializer(get_session_dict(active_session))
    return Response(
        {
            'status': 'success',
            'data': response_serializer.data
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_session_history(request):
    """
    Get user's session history with pagination.
    
    GET /api/sessions/history/?limit=10&offset=0
    
    Query Parameters:
    - limit: Number of sessions (default: 10, max: 100)
    - offset: Skip this many sessions (default: 0)
    
    Response:
    {
        "status": "success",
        "count": 45,
        "results": [...sessions...]
    }
    """
    from sessions.models import Session
    
    limit = min(int(request.query_params.get('limit', 10)), 100)
    offset = int(request.query_params.get('offset', 0))
    
    sessions = Session.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-start_time')
    
    total_count = sessions.count()
    sessions_page = sessions[offset:offset+limit]
    
    serializer = SessionListSerializer(
        [get_session_dict(s) for s in sessions_page],
        many=True
    )
    
    return Response(
        {
            'status': 'success',
            'count': total_count,
            'limit': limit,
            'offset': offset,
            'results': serializer.data
        },
        status=status.HTTP_200_OK
    )


# ============================================================================
# POSE ANALYSIS ENDPOINTS
# ============================================================================

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def submit_pose_angles(request):
    """
    Submit pose angles from computer vision during exercise.
    
    Called repeatedly during an exercise to capture form in real-time.
    
    POST /api/pose/submit/
    
    Request:
    {
        "session_exercise_id": 42,
        "frame_number": 5,
        "timestamp_seconds": 2.5,
        "detected_joint_angles": {
            "shoulder": 92.5,
            "elbow": 178.2,
            "wrist": 2.1
        },
        "pose_detection_confidence": 94.5,
        "individual_joint_confidence": {
            "shoulder": 96.2,
            "elbow": 92.1,
            "wrist": 85.3
        },
        "body_position_description": "Peak extension",
        "is_peak_position": true
    }
    
    Response:
    {
        "status": "success",
        "analysis_id": 128,
        "message": "Pose angles recorded",
        "data": {...analysis_details...}
    }
    """
    serializer = PoseAngleSubmitSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                'status': 'error',
                'error': 'Invalid input',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from sessions.models import SessionExercise
        from ai_engine.models import PoseAnalysis
        
        # Get the session exercise
        try:
            session_exercise = SessionExercise.objects.get(
                id=serializer.validated_data['session_exercise_id'],
                session__user=request.user
            )
        except SessionExercise.DoesNotExist:
            return Response(
                {
                    'status': 'error',
                    'error': 'Session exercise not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Store the pose analysis
        pose_analysis = PoseAnalysis.objects.create(
            session_exercise=session_exercise,
            frame_number=serializer.validated_data['frame_number'],
            timestamp_seconds=serializer.validated_data['timestamp_seconds'],
            detected_joint_angles=serializer.validated_data['detected_joint_angles'],
            pose_detection_confidence=serializer.validated_data['pose_detection_confidence'],
            individual_joint_confidence=serializer.validated_data.get('individual_joint_confidence', {}),
            body_position_description=serializer.validated_data.get('body_position_description', ''),
            is_peak_position=serializer.validated_data.get('is_peak_position', False),
        )
        
        # Calculate angle errors compared to ideal
        exercise = session_exercise.exercise
        ideal_angles = exercise.ideal_joint_angles or {}
        
        angle_errors = {}
        for joint, detected_angle in serializer.validated_data['detected_joint_angles'].items():
            if joint in ideal_angles.get('peak', {}):
                ideal = ideal_angles['peak'][joint]
                error = detected_angle - ideal
                angle_errors[joint] = round(error, 2)
        
        if angle_errors:
            pose_analysis.angle_errors = angle_errors
            pose_analysis.save()
        
        response_data = {
            'id': pose_analysis.id,
            'frame_number': pose_analysis.frame_number,
            'timestamp_seconds': pose_analysis.timestamp_seconds,
            'detected_joint_angles': pose_analysis.detected_joint_angles,
            'angle_errors': pose_analysis.angle_errors,
            'pose_detection_confidence': pose_analysis.pose_detection_confidence,
            'individual_joint_confidence': pose_analysis.individual_joint_confidence,
            'form_issues': pose_analysis.form_issues,
            'body_position_description': pose_analysis.body_position_description,
            'is_peak_position': pose_analysis.is_peak_position,
        }
        
        response_serializer = PoseAnalysisDetailSerializer(response_data)
        
        return Response(
            {
                'status': 'success',
                'analysis_id': pose_analysis.id,
                'message': 'Pose angles recorded',
                'data': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return Response(
            {
                'status': 'error',
                'error': 'Failed to process pose angles',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# SCORING ENDPOINTS
# ============================================================================

@api_view(['POST'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def calculate_exercise_score_endpoint(request):
    """
    Calculate form score for a completed exercise.
    
    Uses AI analysis of pose frames to determine:
    - Form Score: How correct the positioning was
    - Consistency Score: How stable throughout the exercise
    - Range of Motion: How complete the movement was
    
    POST /api/score/calculate/
    
    Request:
    {
        "session_exercise_id": 42
    }
    
    Response:
    {
        "status": "success",
        "data": {
            "form_score": 85.5,
            "consistency_score": 82.0,
            "range_of_motion_percentage": 92.0,
            "overall_exercise_score": 85.3,
            "form_issues": [...],
            "recommendations": [...]
        }
    }
    """
    try:
        from sessions.models import SessionExercise
        
        session_exercise_id = request.data.get('session_exercise_id')
        if not session_exercise_id:
            return Response(
                {
                    'status': 'error',
                    'error': 'session_exercise_id is required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session_exercise = SessionExercise.objects.get(
            id=session_exercise_id,
            session__user=request.user
        )
        
        # Get pose analyses
        pose_analyses = session_exercise.pose_analyses.all()
        if not pose_analyses.exists():
            return Response(
                {
                    'status': 'error',
                    'error': 'No pose data available for this exercise'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate scores from AI analysis
        form_errors = []
        total_angle_deviation = 0
        peak_positions = pose_analyses.filter(is_peak_position=True)
        
        for analysis in peak_positions:
            if analysis.angle_errors:
                for joint, error in analysis.angle_errors.items():
                    total_angle_deviation += abs(error)
                    if abs(error) > 10:
                        form_errors.append({
                            'frame': analysis.frame_number,
                            'joint': joint,
                            'deviation': round(abs(error), 1),
                            'severity': 'high' if abs(error) > 20 else 'medium'
                        })
        
        # Calculate form score (100 - avg deviation)
        avg_deviation = total_angle_deviation / len(peak_positions) if peak_positions.exists() else 0
        form_score = max(0, 100 - (avg_deviation * 1.5))
        
        # Calculate consistency score (check for frame-to-frame variations)
        all_angles = []
        for analysis in pose_analyses:
            if analysis.detected_joint_angles:
                all_angles.append(analysis.detected_joint_angles)
        
        consistency_score = 85.0  # Default
        if len(all_angles) > 1:
            variations = 0
            for i in range(len(all_angles)-1):
                for joint in all_angles[i]:
                    if joint in all_angles[i+1]:
                        var = abs(all_angles[i][joint] - all_angles[i+1][joint])
                        variations += var
            avg_variation = variations / (len(all_angles) - 1)
            consistency_score = max(0, 100 - (avg_variation * 0.8))
        
        # ROM is typically 90%+ if full movement
        rom = 90.0
        
        # Store scores in database
        session_exercise.form_score = round(form_score, 1)
        session_exercise.consistency_score = round(consistency_score, 1)
        session_exercise.range_of_motion_percentage = rom
        session_exercise.form_issues_detected = form_errors
        session_exercise.save()
        
        # Generate recommendations
        recommendations = []
        if form_score < 80:
            recommendations.append("Focus on maintaining proper joint alignment")
        if consistency_score < 80:
            recommendations.append("Slow down the movement and maintain steady control")
        if form_errors:
            recommendations.append(f"Watch out for the {form_errors[0]['joint']} positioning")
        
        overall_score = calculate_exercise_score(session_exercise)
        
        response_data = {
            'session_exercise_id': session_exercise.id,
            'exercise_name': session_exercise.exercise.name,
            'form_score': session_exercise.form_score,
            'consistency_score': session_exercise.consistency_score,
            'range_of_motion_percentage': rom,
            'overall_exercise_score': overall_score,
            'form_issues': form_errors,
            'recommendations': recommendations,
        }
        
        response_serializer = ScoreCalculationResultSerializer(response_data)
        
        return Response(
            {
                'status': 'success',
                'message': 'Score calculated successfully',
                'data': response_serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {
                'status': 'error',
                'error': 'Failed to calculate score',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# FEEDBACK ENDPOINTS
# ============================================================================

@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_session_feedback(request):
    """
    Get AI-generated feedback for a completed session.
    
    GET /api/feedback/session/{session_id}/
    
    Response:
    {
        "status": "success",
        "data": {
            "overall_session_score": 85.2,
            "completion_percentage": 100.0,
            "ai_feedback": "Great session!...",
            "improvement_areas": [...],
            "positive_feedback_points": [...],
            ...
        }
    }
    """
    try:
        from sessions.models import Session
        
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response(
                {
                    'status': 'error',
                    'error': 'session_id parameter required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session = Session.objects.get(id=session_id, user=request.user)
        
        if session.status != 'completed':
            return Response(
                {
                    'status': 'error',
                    'error': 'Session is not completed yet'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exercises = session.exercise_records.filter(status='completed')
        
        # Calculate metrics
        avg_form = exercises.aggregate(Avg('form_score'))['form_score__avg'] or 0
        avg_consistency = exercises.aggregate(Avg('consistency_score'))['consistency_score__avg'] or 0
        avg_rom = exercises.aggregate(Avg('range_of_motion_percentage'))['range_of_motion_percentage__avg'] or 0
        
        pain_improvement = 0
        if session.pain_level_before and session.pain_level_after:
            pain_improvement = session.pain_level_before - session.pain_level_after
        
        # Generate feedback if not already done
        if not session.ai_generated_feedback:
            session.ai_generated_feedback = generate_ai_feedback(session)
            session.improvement_areas = generate_improvement_areas(session)
            session.save()
        
        feedback_data = {
            'session_id': session.id,
            'overall_session_score': session.overall_session_score,
            'completion_percentage': session.completion_percentage,
            'ai_feedback': session.ai_generated_feedback,
            'improvement_areas': session.improvement_areas,
            'positive_feedback_points': session.positive_feedback_points or [],
            'avg_form_score': round(avg_form, 1),
            'avg_consistency_score': round(avg_consistency, 1),
            'avg_range_of_motion': round(avg_rom, 1),
            'pain_level_before': session.pain_level_before,
            'pain_level_after': session.pain_level_after,
            'pain_improvement': pain_improvement,
            'exercises_completed': exercises.count(),
            'total_exercises': session.exercises.count(),
            'exercises_skipped': session.exercises.count() - exercises.count(),
            'recommended_focus_areas': [
                f"{area['exercise']}: {area['recommendation']}"
                for area in (session.improvement_areas or [])
            ],
            'next_session_recommendations': [
                "Increase difficulty when form score > 85 consistently",
                "Reduce range if pain increases during exercise",
                "Practice exercises with low consistency scores",
            ],
        }
        
        response_serializer = FeedbackSerializer(feedback_data)
        
        return Response(
            {
                'status': 'success',
                'data': response_serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {
                'status': 'error',
                'error': 'Failed to retrieve feedback',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# PROGRESS & HISTORY ENDPOINTS
# ============================================================================

@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_user_progress(request):
    """
    Get comprehensive user progress summary.
    
    GET /api/progress/current/
    
    Response:
    {
        "status": "success",
        "data": {
            "total_sessions_completed": 42,
            "average_session_score": 82.5,
            "current_streak_days": 5,
            "pain_improvement_percentage": 35.5,
            ...
        }
    }
    """
    try:
        from analytics.models import UserProgress
        
        progress = UserProgress.objects.get(user=request.user)
        
        recent_milestones = []
        if hasattr(request.user, 'milestones'):
            recent = request.user.milestones.all().order_by('-achievement_date')[:5]
            recent_milestones = [
                {
                    'milestone_type': m.milestone_type,
                    'description': m.description,
                    'date': m.achievement_date.strftime('%Y-%m-%d'),
                    'reward_points': m.reward_points,
                }
                for m in recent
            ]
        
        progress_data = {
            'id': progress.id,
            'user_id': request.user.id,
            'username': request.user.username,
            'total_sessions_completed': progress.total_sessions_completed,
            'total_sessions_started': progress.total_sessions_started,
            'session_completion_rate': progress.session_completion_rate,
            'average_session_score': progress.average_session_score,
            'best_session_score': progress.best_session_score,
            'worst_session_score': progress.worst_session_score,
            'average_exercise_form_score': progress.average_exercise_form_score,
            'current_streak_days': progress.current_streak_days,
            'longest_streak_days': progress.longest_streak_days,
            'last_session_date': progress.last_session_date,
            'exercises_mastered': progress.exercises_mastered,
            'avg_difficulty_of_exercises': progress.avg_difficulty_of_exercises,
            'average_pain_before_session': progress.average_pain_before_session,
            'average_pain_after_session': progress.average_pain_after_session,
            'pain_improvement_percentage': progress.pain_improvement_percentage,
            'primary_goal': progress.primary_goal,
            'goal_progress_percentage': progress.goal_progress_percentage,
            'estimated_recovery_date': progress.estimated_recovery_date,
            'sessions_this_week': progress.sessions_this_week,
            'average_score_this_week': progress.average_score_this_week,
            'total_reward_points': sum(m.get('reward_points', 0) for m in recent_milestones),
            'recent_milestones': recent_milestones,
        }
        
        response_serializer = UserProgressSerializer(progress_data)
        
        return Response(
            {
                'status': 'success',
                'data': response_serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {
                'status': 'error',
                'error': 'Failed to retrieve progress',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_progress_history(request):
    """
    Get detailed progress history over a date range.
    
    GET /api/progress/history/?days=30
    
    Query Parameters:
    - days: Number of days to look back (default: 30, max: 365)
    
    Response:
    {
        "status": "success",
        "data": {
            "total_sessions": 12,
            "total_exercises_completed": 120,
            "trend": "improving",
            "daily_metrics": [...]
        }
    }
    """
    try:
        from sessions.models import Session
        from analytics.models import DailyMetrics
        
        days = min(int(request.query_params.get('days', 30)), 365)
        start_date = timezone.now().date() - timedelta(days=days)
        end_date = timezone.now().date()
        
        # Aggregate session data
        sessions = Session.objects.filter(
            user=request.user,
            status='completed',
            start_time__date__gte=start_date,
            start_time__date__lte=end_date
        )
        
        total_sessions = sessions.count()
        total_time = sessions.aggregate(Sum('scheduled_duration_minutes'))['scheduled_duration_minutes__sum'] or 0
        avg_score = sessions.aggregate(Avg('overall_session_score'))['overall_session_score__avg'] or 0
        
        total_exercises = sessions.values('exercise_records').count()
        
        # Get daily metrics
        daily_records = DailyMetrics.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        daily_data = []
        for metric in daily_records:
            daily_data.append({
                'date': metric.date,
                'sessions_completed': metric.sessions_completed,
                'exercises_completed': metric.exercises_completed,
                'total_minutes_exercised': metric.total_minutes_exercised,
                'average_session_score': metric.average_session_score,
                'average_form_score': metric.average_form_score,
                'completion_rate': metric.completion_rate,
                'average_pain_before': metric.average_pain_before,
                'average_pain_after': metric.average_pain_after,
            })
        
        # Calculate trend
        if len(daily_data) > 1:
            first_half_scores = [d['average_session_score'] for d in daily_data[:len(daily_data)//2] if d['average_session_score']]
            second_half_scores = [d['average_session_score'] for d in daily_data[len(daily_data)//2:] if d['average_session_score']]
            
            first_avg = sum(first_half_scores) / len(first_half_scores) if first_half_scores else 0
            second_avg = sum(second_half_scores) / len(second_half_scores) if second_half_scores else 0
            
            if second_avg > first_avg + 2:
                trend = 'improving'
                trend_percentage = round(((second_avg - first_avg) / first_avg * 100), 1) if first_avg > 0 else 0
            elif second_avg < first_avg - 2:
                trend = 'declining'
                trend_percentage = round(((first_avg - second_avg) / first_avg * 100), 1) if first_avg > 0 else 0
            else:
                trend = 'stable'
                trend_percentage = 0
        else:
            trend = 'stable'
            trend_percentage = 0
        
        # Pain improvement
        pain_before_all = sessions.filter(pain_level_before__isnull=False).aggregate(Avg('pain_level_before'))['pain_level_before__avg'] or 0
        pain_after_all = sessions.filter(pain_level_after__isnull=False).aggregate(Avg('pain_level_after'))['pain_level_after__avg'] or 0
        pain_improvement = pain_before_all - pain_after_all if pain_before_all > 0 else 0
        
        history_data = {
            'date_range_start': start_date,
            'date_range_end': end_date,
            'total_sessions': total_sessions,
            'total_exercises_completed': total_exercises,
            'total_hours_exercised': round(total_time / 60, 1),
            'average_session_score': round(avg_score, 1),
            'trend': trend,
            'trend_percentage': trend_percentage,
            'best_week': f"Week of {daily_data[0]['date']}" if daily_data else "N/A",
            'worst_week': f"Week of {daily_data[-1]['date']}" if daily_data else "N/A",
            'pain_improvement_over_period': round(pain_improvement, 1),
            'starting_average_pain': round(pain_before_all, 1),
            'ending_average_pain': round(pain_after_all, 1),
            'exercises_attempted': total_exercises,
            'new_exercises_mastered': 0,  # Would need to calculate based on scores
            'difficulty_progression': 'Maintained',  # Would analyze difficulty trends
            'daily_metrics': daily_data,
        }
        
        response_serializer = ProgressHistorySerializer(history_data)
        
        return Response(
            {
                'status': 'success',
                'data': response_serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {
                'status': 'error',
                'error': 'Failed to retrieve history',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@authentication_classes([TokenAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_exercise_progress(request):
    """
    Get progress on a specific exercise.
    
    GET /api/progress/exercise/{exercise_id}/
    
    Response:
    {
        "status": "success",
        "data": {
            "exercise_name": "Shoulder Press",
            "times_performed": 15,
            "average_form_score": 82.5,
            "form_score_trend": "improving",
            ...
        }
    }
    """
    try:
        from sessions.models import SessionExercise
        from exercises.models import Exercise
        
        exercise_id = request.query_params.get('exercise_id')
        if not exercise_id:
            return Response(
                {
                    'status': 'error',
                    'error': 'exercise_id parameter required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exercise = Exercise.objects.get(id=exercise_id)
        
        # Get all attempts by this user
        attempts = SessionExercise.objects.filter(
            exercise=exercise,
            session__user=request.user,
            status='completed'
        ).order_by('created_at')
        
        if not attempts.exists():
            return Response(
                {
                    'status': 'error',
                    'error': 'No performance data for this exercise'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        scores = [a.form_score for a in attempts if a.form_score]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        recent_scores = [a.form_score for a in attempts.order_by('-created_at')[:10] if a.form_score]
        
        # Determine trend
        if len(recent_scores) > 3:
            old_avg = sum(recent_scores[-5:]) / 5 if len(recent_scores) >= 5 else avg_score
            new_avg = sum(recent_scores[:5]) / 5 if len(recent_scores) >= 5 else avg_score
            trend = 'improving' if new_avg > old_avg else ('declining' if new_avg < old_avg else 'stable')
        else:
            trend = 'stable'
        
        exercise_progress_data = {
            'exercise_id': exercise.id,
            'exercise_name': exercise.name,
            'category': exercise.category,
            'times_performed': attempts.count(),
            'average_form_score': round(avg_score, 1),
            'best_form_score': max(scores) if scores else 0,
            'worst_form_score': min(scores) if scores else 0,
            'form_score_trend': trend,
            'recent_scores': [round(s, 1) for s in recent_scores[:5]],
            'average_user_difficulty_rating': round(
                attempts.aggregate(Avg('user_difficulty_rating'))['user_difficulty_rating__avg'] or 0, 1
            ),
            'average_pain_during_exercise': round(
                attempts.aggregate(Avg('pain_during_exercise'))['pain_during_exercise__avg'] or 0, 1
            ),
            'most_common_form_issues': {},
            'recent_feedback': attempts.order_by('-created_at').first().ai_feedback_for_exercise or 'Keep practicing!',
            'recommendation': 'Great job! Keep working on consistency.' if avg_score >= 80 else 'Focus on form quality.',
        }
        
        response_serializer = ExerciseProgressSerializer(exercise_progress_data)
        
        return Response(
            {
                'status': 'success',
                'data': response_serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {
                'status': 'error',
                'error': 'Failed to retrieve exercise progress',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
