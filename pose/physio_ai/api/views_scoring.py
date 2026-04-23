"""
API Views for pose detection and scoring
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import json

# Import scoring engine
from .ai_engine.score_generator import ScoreGenerator


@api_view(['POST'])
def calculate_score(request):
    """
    Calculate pose score from video frames
    
    Expected POST data:
    {
        "exercise_id": 1,
        "frames": [
            {
                "frame_number": 0,
                "timestamp": 1234567890,
                "angles": {"shoulder": 45.5, "elbow": 90.0, ...},
                "confidence": 0.95
            },
            ...
        ]
    }
    """
    try:
        data = request.data
        
        # Validate input
        if 'exercise_id' not in data or 'frames' not in data:
            return Response(
                {"error": "Missing required fields: exercise_id, frames"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exercise_id = data['exercise_id']
        frames = data['frames']
        
        if not isinstance(frames, list) or len(frames) == 0:
            return Response(
                {"error": "Frames must be non-empty list"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Convert frames to expected format
        processed_frames = []
        for frame in frames:
            processed_frame = {
                'frame_number': frame.get('frame_number', 0),
                'timestamp': frame.get('timestamp', 0),
                'detected_joint_angles': frame.get('angles', {}),
                'pose_detection_confidence': frame.get('confidence', 0.5)
            }
            processed_frames.append(processed_frame)
        
        # Score exercise using AI engine
        generator = ScoreGenerator()
        result = generator.score_exercise(
            exercise_id=exercise_id,
            frames=processed_frames,
            reps_count=1
        )
        
        if result is None:
            return Response(
                {"error": "Scoring failed - invalid exercise or frames"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate feedback
        feedback = generator.generate_feedback_message(result)
        
        return Response({
            "success": True,
            "overall_score": result.scores.overall_score,
            "form_score": result.scores.form_score,
            "consistency_score": result.scores.consistency_score,
            "range_of_motion_score": result.scores.range_of_motion_score,
            "safety_score": result.scores.safety_score,
            "summary": feedback.get('summary', ''),
            "feedback": feedback.get('feedback', []),
            "recommendations": feedback.get('recommendations', []),
            "mistakes": feedback.get('mistakes', []),
            "metrics": feedback.get('metrics', {})
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": f"Server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def score_from_landmarks(request):
    """
    Alternative endpoint that receives raw MediaPipe landmarks
    
    Expected POST data:
    {
        "exercise_id": 1,
        "landmarks": [
            {"x": 0.5, "y": 0.5, "z": 0, "visibility": 0.95},
            ...
        ]
    }
    """
    try:
        from .ai_engine.joint_angle_calculator import JointAngleCalculator
        
        data = request.data
        exercise_id = data.get('exercise_id')
        landmarks = data.get('landmarks')
        
        if not landmarks or len(landmarks) == 0:
            return Response(
                {"error": "No landmarks provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate angles from landmarks
        calculator = JointAngleCalculator()
        
        # Convert landmarks to Point2D-like format
        points = [{'x': lm['x'], 'y': lm['y']} for lm in landmarks]
        
        # Calculate joint angles using the calculator
        # This is a simple example - real implementation would use specific joint indices
        angles = {}
        
        # You can add specific angle calculations here
        # For now, just return the landmarks received
        
        return Response({
            "success": True,
            "landmarks_received": len(landmarks),
            "landmark_sample": landmarks[:5] if len(landmarks) > 5 else landmarks
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": f"Server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def pose_detector_ui(request):
    """
    Serve the pose detector HTML UI
    """
    from django.shortcuts import render
    return render(request, 'index.html')
