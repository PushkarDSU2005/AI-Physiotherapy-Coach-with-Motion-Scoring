"""
URL Routing for Physio AI REST API

Maps endpoints to views for:
- Session management (start, history, active)
- Pose angle submission (real-time form capture)
- Score calculation (form assessment)
- Feedback generation (AI recommendations)
- Progress tracking (history and analytics)
"""

from django.urls import path
from . import views
from . import dashboard_views

app_name = 'api'

urlpatterns = [
    # ========================================================================
    # SESSION MANAGEMENT ENDPOINTS
    # ========================================================================
    
    # Start a new session
    # POST /api/sessions/start/
    # Request: {title, description, session_type, scheduled_duration_minutes, pain_level_before}
    # Response: {status, session_id, data}
    path('sessions/start/', views.start_session, name='session_start'),
    
    # Get currently active session
    # GET /api/sessions/active/
    # Response: {status, data: {session details}}
    path('sessions/active/', views.get_active_session, name='session_active'),
    
    # Get session history for user
    # GET /api/sessions/history/?limit=10&offset=0
    # Query params: limit (default 10), offset (default 0)
    # Response: {status, count, results: [session list]}
    path('sessions/history/', views.get_session_history, name='session_history'),
    
    
    # ========================================================================
    # POSE ANALYSIS ENDPOINTS
    # ========================================================================
    
    # Submit pose angles from video frame
    # POST /api/pose/submit/
    # Request: {session_exercise_id, frame_number, timestamp_seconds, detected_joint_angles, ...}
    # Response: {status, analysis_id, data}
    # Called repeatedly during exercise to capture form data
    path('pose/submit/', views.submit_pose_angles, name='pose_submit'),
    
    
    # ========================================================================
    # SCORING ENDPOINTS
    # ========================================================================
    
    # Calculate form score for completed exercise
    # POST /api/score/calculate/
    # Request: {session_exercise_id}
    # Response: {status, data: {form_score, consistency_score, range_of_motion, ...}}
    # Analyzes all pose frames to generate comprehensive score
    path('score/calculate/', views.calculate_exercise_score_endpoint, name='score_calculate'),
    
    
    # ========================================================================
    # FEEDBACK ENDPOINTS
    # ========================================================================
    
    # Get AI-generated feedback for completed session
    # GET /api/feedback/session/?session_id=123
    # Query params: session_id (required)
    # Response: {status, data: {ai_feedback, improvement_areas, positive_feedback, ...}}
    path('feedback/session/', views.get_session_feedback, name='feedback_session'),
    
    
    # ========================================================================
    # PROGRESS TRACKING ENDPOINTS
    # ========================================================================
    
    # Get current user progress summary
    # GET /api/progress/current/
    # Response: {status, data: {total_sessions_completed, average_session_score, ...}}
    path('progress/current/', views.get_user_progress, name='progress_current'),
    
    # Get detailed progress history over date range
    # GET /api/progress/history/?days=30
    # Query params: days (default 30, max 365)
    # Response: {status, data: {total_sessions, trend, daily_metrics, ...}}
    path('progress/history/', views.get_progress_history, name='progress_history'),
    
    # Get progress on specific exercise
    # GET /api/progress/exercise/?exercise_id=5
    # Query params: exercise_id (required)
    # Response: {status, data: {exercise_name, times_performed, average_form_score, trend, ...}}
    path('progress/exercise/', views.get_exercise_progress, name='progress_exercise'),

    # Dashboard/live analytics endpoints
    path('dashboard/metrics/', dashboard_views.get_dashboard_metrics, name='dashboard_metrics'),
    path('dashboard/chart-data/', dashboard_views.get_chart_data, name='dashboard_chart_data'),
]
