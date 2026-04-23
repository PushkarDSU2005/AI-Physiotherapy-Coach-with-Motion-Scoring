from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.decorators import login_required
from .models import Session, SessionExercise


class SessionListView(View):
    """Display all sessions for the logged-in user."""
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, 'sessions/not_authenticated.html', status=401)
        
        sessions = Session.objects.filter(user=request.user)
        status = request.GET.get('status', None)
        
        if status:
            sessions = sessions.filter(status=status)
        
        return render(request, 'sessions/session_list.html', {'sessions': sessions})


class SessionDetailView(View):
    """Display details for a specific session."""
    def get(self, request, session_id):
        try:
            session = Session.objects.get(id=session_id, user=request.user)
            exercises = session.exercise_records.all().order_by('order')
            return render(request, 'sessions/session_detail.html', {
                'session': session,
                'exercises': exercises
            })
        except Session.DoesNotExist:
            return render(request, 'sessions/session_not_found.html', status=404)


@login_required
def pose_capture_view(request, session_exercise_id):
    """Display live pose capture interface for an exercise."""
    try:
        session_exercise = SessionExercise.objects.get(id=session_exercise_id)
        
        # Verify user owns this session (or is admin)
        if session_exercise.session.user != request.user and not request.user.is_staff:
            return render(request, 'sessions/unauthorized.html', status=403)
        
        exercise_name = session_exercise.exercise.name
        exercise_type = session_exercise.exercise.name.lower().replace(' ', '_')
    except SessionExercise.DoesNotExist:
        # Demo mode - use fallback data
        exercise_name = "Bodyweight Squat"
        exercise_type = "squat"
    
    return render(request, 'sessions/pose_capture.html', {
        'session_exercise_id': session_exercise_id,
        'exercise_name': exercise_name,
        'exercise_type': exercise_type,
    })


def pose_capture_demo(request):
    """Display pose capture demo page."""
    return render(request, 'sessions/pose_capture_demo.html')


def pose_capture_demo_live(request):
    """Display live pose capture interface in demo mode (no login required)."""
    return render(request, 'sessions/pose_capture.html', {
        'session_exercise_id': 'demo',
        'exercise_name': 'Bodyweight Squat',
        'exercise_type': 'squat',
        'demo_mode': True,
    })


class SessionDetailView(View):
    """Display details for a specific session."""
    def get(self, request, session_id):
        try:
            session = Session.objects.get(id=session_id, user=request.user)
            exercises = session.exercise_records.all().order_by('order')
            return render(request, 'sessions/session_detail.html', {
                'session': session,
                'exercises': exercises
            })
        except Session.DoesNotExist:
            return render(request, 'sessions/session_not_found.html', status=404)
