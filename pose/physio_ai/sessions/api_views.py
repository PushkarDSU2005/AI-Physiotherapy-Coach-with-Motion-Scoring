"""
API Views for Pose Detection and Analysis
REST endpoints for pose frame uploads and processing
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from ai_engine.live_feedback_engine import LiveFeedbackEngine
from sessions.pose_processor import get_pose_processor
from ai_engine.models import PoseAnalysis
from sessions.models import SessionExercise
from advanced_features.models import InjuryRiskAlert


def _calculate_joint_angles(processor, landmarks):
    joint_triplets = {
        'left_elbow': ('left_shoulder', 'left_elbow', 'left_wrist'),
        'right_elbow': ('right_shoulder', 'right_elbow', 'right_wrist'),
        'left_knee': ('left_hip', 'left_knee', 'left_ankle'),
        'right_knee': ('right_hip', 'right_knee', 'right_ankle'),
        'left_hip': ('left_shoulder', 'left_hip', 'left_knee'),
        'right_hip': ('right_shoulder', 'right_hip', 'right_knee'),
        'spine': ('left_shoulder', 'left_hip', 'left_knee'),
    }
    angles = {}
    for joint_name, point_names in joint_triplets.items():
        if all(point in landmarks for point in point_names):
            angles[joint_name] = round(
                processor.calculate_angle(
                    landmarks[point_names[0]],
                    landmarks[point_names[1]],
                    landmarks[point_names[2]],
                ),
                1,
            )
    return angles


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def upload_pose_frame(request):
    """
    Upload and process a pose frame.
    
    Expected JSON:
    {
        "session_exercise_id": 1,
        "frame_number": 5,
        "landmarks": [[x,y,z,visibility], ...],
        "exercise_type": "squat"
    }
    
    Returns:
    {
        "success": true,
        "form_score": 85.5,
        "issues": [...],
        "alerts": [...]
    }
    """
    try:
        data = json.loads(request.body)
        
        session_exercise_id = data.get('session_exercise_id')
        frame_number = data.get('frame_number', 0)
        landmarks = data.get('landmarks', [])
        exercise_type = data.get('exercise_type', 'squat')
        
        # Get pose processor
        processor = get_pose_processor()
        
        # Extract landmarks
        frame_data = {'landmarks': landmarks}
        landmark_dict = processor.extract_landmarks(frame_data)
        
        # Calculate form score
        form_score = processor.calculate_form_score(landmark_dict, exercise_type)
        joint_angles = _calculate_joint_angles(processor, landmark_dict)
        
        # Detect issues
        issues = processor.detect_posture_issues(landmark_dict, exercise_type)
        
        # Get session exercise
        try:
            session_exercise = SessionExercise.objects.get(id=session_exercise_id)
        except SessionExercise.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Session exercise not found'
            }, status=404)
        
        # Store in database
        pose_analysis = PoseAnalysis.objects.create(
            session_exercise=session_exercise,
            frame_number=frame_number,
            form_score=form_score,
            confidence_level=95.0,
            detected_joints={
                'landmarks': landmark_dict,
                'angles': joint_angles,
            },
            issues_detected=[issue['type'] for issue in issues],
            recommendations='; '.join([issue['message'] for issue in issues])
        )
        
        # Generate alerts for critical issues
        alerts = []
        for issue in issues:
            if issue['severity'] in ['high', 'critical']:
                alert = {
                    'type': issue['type'],
                    'severity': issue['severity'],
                    'message': issue['message'],
                    'joint': issue.get('joint', ''),
                    'angle': issue.get('angle', 0),
                    'safe_range': issue.get('safe_range', ''),
                }
                alerts.append(alert)
                
                # Store in database
                if 'joint' in issue:
                    InjuryRiskAlert.objects.create(
                        user=request.user,
                        pose_analysis=pose_analysis,
                        session_exercise=session_exercise,
                        alert_type='joint_angle',
                        risk_level=issue['severity'],
                        joint_name=issue['joint'],
                        current_angle=issue.get('angle', 0),
                        safe_range_min=0,
                        safe_range_max=float(issue.get('safe_range', '0-120').split('-')[1]),
                        severity_score=75 if issue['severity'] == 'high' else 85,
                        description=issue['message'],
                        recommendation=issue['message']
                    )

        history = [
            {'score': float(item.form_score)}
            for item in session_exercise.pose_analyses.order_by('-frame_number')[:12]
        ]
        feedback_engine = LiveFeedbackEngine(request.user)
        feedback_payload = feedback_engine.generate(
            session_exercise=session_exercise,
            form_score=form_score,
            confidence=95.0,
            issues=issues,
            angles=joint_angles,
            history=list(reversed(history)),
        )
        
        return JsonResponse({
            'success': True,
            'form_score': round(form_score, 1),
            'joint_angles': joint_angles,
            'issues': issues,
            'alerts': alerts,
            'feedback': feedback_payload,
            'pose_analysis_id': pose_analysis.id
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_pose_capture_page(request, session_exercise_id):
    """Render pose capture page for a session exercise."""
    try:
        session_exercise = SessionExercise.objects.get(id=session_exercise_id)
        exercise_type = session_exercise.exercise.name.lower().replace(' ', '_')
        
        return JsonResponse({
            'success': True,
            'session_exercise_id': session_exercise_id,
            'exercise_name': session_exercise.exercise.name,
            'exercise_type': exercise_type,
            'duration': session_exercise.session.duration or 300,  # Default 5 min
        })
    except SessionExercise.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Session exercise not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
