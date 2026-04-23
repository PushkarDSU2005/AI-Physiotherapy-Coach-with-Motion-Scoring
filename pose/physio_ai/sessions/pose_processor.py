"""
Pose Detection & Processing Module
Handles MediaPipe pose detection and analysis
"""

import mediapipe as mp
import numpy as np
import json
from typing import Dict, List, Tuple
import math


class PoseProcessor:
    """Process pose data from MediaPipe and extract angles/information."""
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
    
    def extract_landmarks(self, frame_data: Dict) -> Dict:
        """Extract and normalize MediaPipe landmarks."""
        try:
            landmarks = {}
            landmark_names = [
                'nose', 'left_eye_inner', 'left_eye', 'left_eye_outer',
                'right_eye_inner', 'right_eye', 'right_eye_outer',
                'left_ear', 'right_ear', 'mouth_left', 'mouth_right',
                'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
                'left_wrist', 'right_wrist', 'left_pinky', 'right_pinky',
                'left_index', 'right_index', 'left_thumb', 'right_thumb',
                'left_hip', 'right_hip', 'left_knee', 'right_knee',
                'left_ankle', 'right_ankle', 'left_heel', 'right_heel',
                'left_foot_index', 'right_foot_index'
            ]
            
            for i, name in enumerate(landmark_names):
                if 'landmarks' in frame_data and i < len(frame_data['landmarks']):
                    lm = frame_data['landmarks'][i]
                    landmarks[name] = {
                        'x': float(lm[0]),
                        'y': float(lm[1]),
                        'z': float(lm[2]) if len(lm) > 2 else 0.0,
                        'visibility': float(lm[3]) if len(lm) > 3 else 1.0
                    }
            
            return landmarks
        except Exception as e:
            print(f"Error extracting landmarks: {e}")
            return {}
    
    @staticmethod
    def calculate_angle(p1: Dict, p2: Dict, p3: Dict) -> float:
        """
        Calculate angle at p2 formed by points p1-p2-p3.
        Returns angle in degrees (0-180).
        """
        try:
            # Convert to numpy arrays
            a = np.array([p1['x'], p1['y'], p1['z']])
            b = np.array([p2['x'], p2['y'], p2['z']])
            c = np.array([p3['x'], p3['y'], p3['z']])
            
            # Vectors
            ba = a - b
            bc = c - b
            
            # Angle
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
            angle = np.degrees(np.arccos(cosine_angle))
            
            return float(angle)
        except:
            return 0.0
    
    @staticmethod
    def calculate_form_score(landmarks: Dict, exercise_type: str = 'squat') -> float:
        """Calculate form score (0-100) based on landmarks."""
        try:
            score = 100.0
            
            if exercise_type == 'squat':
                # Check various form aspects
                if 'left_knee' in landmarks and 'left_hip' in landmarks:
                    knee_y = landmarks['left_knee']['y']
                    hip_y = landmarks['left_hip']['y']
                    # Deduct if knee not below hip
                    if knee_y < hip_y:
                        score -= 5
                
                # Check posture (torso should be relatively upright)
                if 'left_shoulder' in landmarks and 'left_hip' in landmarks:
                    shoulder_x = landmarks['left_shoulder']['x']
                    hip_x = landmarks['left_hip']['x']
                    # Deduct for excessive forward lean
                    if abs(shoulder_x - hip_x) > 0.15:
                        score -= 10
            
            return max(0, min(100, score))
        except:
            return 75.0
    
    def detect_posture_issues(self, landmarks: Dict, exercise_type: str = 'squat') -> List[Dict]:
        """Detect common posture issues."""
        issues = []
        
        try:
            if exercise_type == 'squat':
                # Issue 1: Knee hyperextension
                if all(k in landmarks for k in ['left_hip', 'left_knee', 'left_ankle']):
                    knee_angle = self.calculate_angle(
                        landmarks['left_hip'],
                        landmarks['left_knee'],
                        landmarks['left_ankle']
                    )
                    if knee_angle > 160:  # Extended beyond safe range
                        issues.append({
                            'type': 'knee_hyperextension',
                            'severity': 'high' if knee_angle > 175 else 'medium',
                            'joint': 'left_knee',
                            'angle': round(knee_angle, 1),
                            'safe_range': '0-120',
                            'message': 'Keep knees slightly bent, avoid locking'
                        })
                
                # Issue 2: Forward lean
                if all(k in landmarks for k in ['left_shoulder', 'left_hip']):
                    if abs(landmarks['left_shoulder']['x'] - landmarks['left_hip']['x']) > 0.2:
                        issues.append({
                            'type': 'forward_lean',
                            'severity': 'medium',
                            'message': 'Keep torso upright, lean less forward'
                        })
                
                # Issue 3: Feet position
                if all(k in landmarks for k in ['left_ankle', 'right_ankle']):
                    issues.append({
                        'type': 'foot_position',
                        'severity': 'low',
                        'message': 'Keep feet shoulder-width apart'
                    })
        
        except Exception as e:
            print(f"Error detecting issues: {e}")
        
        return issues


# Singleton instance
_pose_processor = None

def get_pose_processor():
    """Get or create pose processor instance."""
    global _pose_processor
    if _pose_processor is None:
        _pose_processor = PoseProcessor()
    return _pose_processor
