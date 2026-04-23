"""
Advanced Features Services for PhysioAI

Implements:
1. Adaptive Difficulty System - Analyzes performance trends and recommends difficulty adjustments
2. Injury Risk Detection - Monitors joint angles and flags unsafe positions
3. Exercise Classification - Multi-dimensional exercise matching and recommendations
"""

import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db.models import Q, Avg, StdDev

from exercises.models import Exercise
from sessions.models import Session, SessionExercise
from ai_engine.models import PoseAnalysis
from advanced_features.models import (
    DifficultyAdaptation,
    InjuryRiskAlert,
    JointSafetyProfile,
    ExerciseClassification,
    UserDifficultyPreference,
)

logger = logging.getLogger(__name__)


# ============================================================
# 1. ADAPTIVE DIFFICULTY SYSTEM
# ============================================================

class AdaptiveDifficultySystem:
    """
    Analyzes user performance trends and recommends difficulty adjustments.
    
    Algorithm:
    1. Collect recent performance scores (last 10 sessions)
    2. Calculate trend (linear regression)
    3. Evaluate consistency
    4. Generate recommendation
    5. Auto-adapt if user preference enabled
    """

    def __init__(self, user: User):
        """Initialize adaptive difficulty system for a user"""
        self.user = user
        self.logger = logger
        self.preference = self._get_or_create_preference()

    def _get_or_create_preference(self) -> UserDifficultyPreference:
        """Get or create user difficulty preference"""
        preference, _ = UserDifficultyPreference.objects.get_or_create(user=self.user)
        return preference

    def analyze_exercise(self, exercise: Exercise) -> Dict:
        """
        Analyze and adapt difficulty for a specific exercise.
        
        Returns:
            Dict with trend analysis, recommendations, and current status
        """
        try:
            # Get or create adaptation record
            adaptation, created = DifficultyAdaptation.objects.get_or_create(
                user=self.user,
                exercise=exercise
            )

            # Collect recent performance data
            performance_scores = self._collect_recent_scores(exercise)
            
            if len(performance_scores) == 0:
                return {
                    'exercise_id': exercise.id,
                    'status': 'insufficient_data',
                    'message': 'Not enough performance data yet',
                    'recommendation': 'maintain'
                }

            # Calculate performance metrics
            metrics = self._calculate_metrics(performance_scores)
            
            # Analyze trend
            trend_data = self._analyze_trend(performance_scores)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(metrics, trend_data)
            
            # Update adaptation record
            self._update_adaptation(adaptation, metrics, trend_data, recommendation)
            
            self.logger.info(
                f"Analyzed {exercise.name} for {self.user.username}: "
                f"trend={trend_data['trend']}, recommendation={recommendation['type']}"
            )

            return {
                'exercise_id': exercise.id,
                'exercise_name': exercise.name,
                'current_difficulty': exercise.difficulty_level,
                'metrics': metrics,
                'trend': trend_data,
                'recommendation': recommendation,
                'last_updated': datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error analyzing exercise {exercise.id}: {str(e)}")
            return {'error': str(e)}

    def _collect_recent_scores(self, exercise: Exercise, limit: int = 10) -> List[float]:
        """
        Collect recent form scores for an exercise (last N sessions).
        
        Args:
            exercise: Exercise to analyze
            limit: Number of recent sessions to retrieve
            
        Returns:
            List of form scores in chronological order
        """
        try:
            recent_sessions = SessionExercise.objects.filter(
                exercise=exercise,
                session__user=self.user,
                status='completed',
                form_score__isnull=False
            ).order_by('-session__start_time')[:limit]

            scores = [float(se.form_score) for se in recent_sessions]
            self.logger.debug(f"Collected {len(scores)} scores for {exercise.name}")
            
            return list(reversed(scores))  # Chronological order

        except Exception as e:
            self.logger.error(f"Error collecting scores: {str(e)}")
            return []

    def _calculate_metrics(self, scores: List[float]) -> Dict:
        """
        Calculate performance metrics from scores.
        
        Returns:
            Dict with average, min, max, std dev, consistency score
        """
        try:
            scores_array = np.array(scores)
            
            return {
                'average_score': float(np.mean(scores_array)),
                'min_score': float(np.min(scores_array)),
                'max_score': float(np.max(scores_array)),
                'std_dev': float(np.std(scores_array)),
                'consistency_score': self._calculate_consistency(scores),
                'latest_score': float(scores[-1]) if scores else 0.0,
                'sessions_count': len(scores),
            }

        except Exception as e:
            self.logger.error(f"Error calculating metrics: {str(e)}")
            return {}

    def _calculate_consistency(self, scores: List[float]) -> float:
        """
        Calculate consistency score (lower std dev = higher consistency).
        
        Returns:
            Consistency score 0-100 (100 = most consistent)
        """
        try:
            if len(scores) < 2:
                return 50.0

            std_dev = np.std(scores)
            # Normalize std dev: 0 std dev = 100 consistency, >20 = 0 consistency
            consistency = max(0, 100 - (std_dev * 5))
            return float(min(100, consistency))

        except:
            return 50.0

    def _analyze_trend(self, scores: List[float]) -> Dict:
        """
        Analyze performance trend using linear regression.
        
        Returns:
            Dict with trend type, slope, direction, and confidence
        """
        try:
            if len(scores) < 2:
                return {
                    'trend': 'stable',
                    'slope': 0.0,
                    'direction': 'neutral',
                    'confidence': 0.0,
                }

            # Perform linear regression
            x = np.arange(len(scores))
            y = np.array(scores)
            coefficients = np.polyfit(x, y, 1)
            slope = float(coefficients[0])
            
            # Calculate trend confidence (R-squared)
            y_pred = np.polyval(coefficients, x)
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = float(1 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0
            
            # Determine trend type
            if slope > 2.0:
                trend = 'improving'
                direction = 'up'
            elif slope > 0.5:
                trend = 'slightly_improving'
                direction = 'up'
            elif slope < -2.0:
                trend = 'declining'
                direction = 'down'
            elif slope < -0.5:
                trend = 'slightly_declining'
                direction = 'down'
            else:
                trend = 'stable'
                direction = 'neutral'

            return {
                'trend': trend,
                'slope': slope,
                'direction': direction,
                'confidence': r_squared * 100,
            }

        except Exception as e:
            self.logger.error(f"Error analyzing trend: {str(e)}")
            return {'trend': 'stable', 'slope': 0.0, 'confidence': 0.0}

    def _generate_recommendation(self, metrics: Dict, trend_data: Dict) -> Dict:
        """
        Generate difficulty recommendation based on metrics and trends.
        
        Logic:
        - If avg_score > 85 AND consistent AND improving → increase
        - If avg_score > 80 AND consistent → maintain or slight increase
        - If avg_score < 60 AND declining → decrease
        - If avg_score < 70 → maintain or slight decrease
        - If plateaued → suggest variant
        """
        try:
            avg_score = metrics.get('average_score', 0)
            consistency = metrics.get('consistency_score', 0)
            trend = trend_data.get('trend', 'stable')
            min_threshold = self.preference.min_score_threshold
            consistency_threshold = self.preference.consistency_threshold

            # Generate recommendation
            if avg_score >= 85 and consistency >= consistency_threshold and trend in ['improving', 'slightly_improving']:
                recommendation_type = 'increase'
                reason = f"Excellent performance (avg: {avg_score:.1f}) with improving trend"
                difficulty = 'hard' if metrics.get('average_score', 0) > 90 else 'medium'

            elif avg_score >= 80 and consistency >= 75:
                recommendation_type = 'maintain'
                reason = f"Solid consistent performance (avg: {avg_score:.1f})"
                difficulty = None

            elif avg_score < min_threshold and trend in ['declining', 'slightly_declining']:
                recommendation_type = 'decrease'
                reason = f"Declining performance ({avg_score:.1f}) below threshold ({min_threshold})"
                difficulty = 'easy'

            elif avg_score < min_threshold:
                recommendation_type = 'decrease'
                reason = f"Performance below threshold ({avg_score:.1f} < {min_threshold})"
                difficulty = 'easy'

            elif trend == 'stable' and avg_score >= 75:
                recommendation_type = 'modify'
                reason = f"Plateaued performance. Suggest exercise variation or form focus."
                difficulty = None

            else:
                recommendation_type = 'maintain'
                reason = "Continue current difficulty"
                difficulty = None

            return {
                'type': recommendation_type,
                'difficulty': difficulty,
                'reason': reason,
                'confidence': trend_data.get('confidence', 0),
            }

        except Exception as e:
            self.logger.error(f"Error generating recommendation: {str(e)}")
            return {'type': 'maintain', 'difficulty': None, 'reason': 'Error in analysis'}

    def _update_adaptation(
        self,
        adaptation: DifficultyAdaptation,
        metrics: Dict,
        trend_data: Dict,
        recommendation: Dict
    ) -> None:
        """Update difficulty adaptation record in database"""
        try:
            adaptation.last_10_scores = [metrics.get('average_score', 0)]  # Would include all 10
            adaptation.average_score = metrics.get('average_score', 0)
            adaptation.min_score = metrics.get('min_score', 0)
            adaptation.max_score = metrics.get('max_score', 0)
            adaptation.consistency_score = metrics.get('consistency_score', 0)
            
            adaptation.trend = trend_data.get('trend', 'stable')
            adaptation.trend_slope = trend_data.get('slope', 0)
            
            adaptation.recommendation = recommendation['type']
            adaptation.recommended_difficulty = recommendation['difficulty']
            adaptation.recommendation_reason = recommendation['reason']
            
            adaptation.total_sessions = metrics.get('sessions_count', 0)
            adaptation.last_adapted_at = datetime.now()
            adaptation.adaptation_count += 1
            
            adaptation.save()

        except Exception as e:
            self.logger.error(f"Error updating adaptation: {str(e)}")

    def auto_adapt_if_needed(self, exercise: Exercise) -> Optional[str]:
        """
        Auto-adapt difficulty if user preference allows.
        
        Returns:
            New difficulty level if adapted, None otherwise
        """
        try:
            if not self.preference.auto_adapt_enabled:
                return None

            analysis = self.analyze_exercise(exercise)
            recommendation = analysis.get('recommendation', {})
            
            if recommendation.get('type') in ['increase', 'decrease']:
                new_difficulty = recommendation.get('difficulty')
                if new_difficulty and new_difficulty != exercise.difficulty_level:
                    exercise.difficulty_level = new_difficulty
                    exercise.save()
                    
                    self.logger.info(
                        f"Auto-adapted {exercise.name} from {exercise.difficulty_level} to {new_difficulty}"
                    )
                    return new_difficulty

            return None

        except Exception as e:
            self.logger.error(f"Error auto-adapting: {str(e)}")
            return None


# ============================================================
# 2. INJURY RISK DETECTION SYSTEM
# ============================================================

class InjuryRiskDetectionSystem:
    """
    Monitors joint angles and positions during exercise.
    Detects and alerts when angles exceed safe ranges.
    """

    def __init__(self, user: User):
        """Initialize injury risk detection for a user"""
        self.user = user
        self.logger = logger

    def analyze_pose(
        self,
        pose_analysis: PoseAnalysis,
        session_exercise: SessionExercise
    ) -> Optional[List[Dict]]:
        """
        Analyze a single pose for injury risks.
        
        Returns:
            List of detected risks, or None if analysis fails
        """
        try:
            detected_joints = pose_analysis.detected_joints
            if not detected_joints:
                return []

            alerts = []
            
            # Check each joint in the detected pose
            for joint_name, joint_data in detected_joints.items():
                alert = self._check_joint_safety(
                    joint_name,
                    joint_data,
                    session_exercise
                )
                if alert:
                    alerts.append(alert)

            if alerts:
                self.logger.warning(
                    f"Detected {len(alerts)} injury risks for {self.user.username} "
                    f"in exercise {session_exercise.exercise.name}"
                )

            return alerts

        except Exception as e:
            self.logger.error(f"Error analyzing pose: {str(e)}")
            return []

    def _check_joint_safety(
        self,
        joint_name: str,
        joint_data: Dict,
        session_exercise: SessionExercise
    ) -> Optional[Dict]:
        """
        Check if a single joint's current position is safe.
        
        Returns:
            Alert dict if risk detected, None otherwise
        """
        try:
            current_angle = joint_data.get('angle')
            if current_angle is None:
                return None

            # Get safe range for this joint/exercise combination
            exercise = session_exercise.exercise
            safe_profile = JointSafetyProfile.objects.filter(
                joint_name=joint_name,
                exercise_type=exercise.name,
                is_active=True
            ).first()

            if not safe_profile:
                # Try generic joint profile
                safe_profile = JointSafetyProfile.objects.filter(
                    joint_name=joint_name,
                    exercise_type='generic',
                    is_active=True
                ).first()

            if not safe_profile:
                return None  # No safety profile for this joint

            # Check if angle is within safe range
            min_safe = safe_profile.normal_min_angle
            max_safe = safe_profile.normal_max_angle
            critical_threshold = safe_profile.critical_threshold
            warning_threshold = safe_profile.warning_threshold

            exceeded_by = None
            risk_level = 'low'
            alert_type = 'joint_angle'

            if current_angle < min_safe:
                exceeded_by = min_safe - current_angle
            elif current_angle > max_safe:
                exceeded_by = current_angle - max_safe

            if exceeded_by is None:
                return None  # Within safe range

            # Determine risk level
            if exceeded_by > critical_threshold:
                risk_level = 'critical'
            elif exceeded_by > warning_threshold:
                risk_level = 'high'
            else:
                risk_level = 'medium'

            return {
                'joint_name': joint_name,
                'current_angle': current_angle,
                'safe_min': min_safe,
                'safe_max': max_safe,
                'exceeded_by': exceeded_by,
                'risk_level': risk_level,
                'alert_type': alert_type,
            }

        except Exception as e:
            self.logger.error(f"Error checking joint safety: {str(e)}")
            return None

    def create_risk_alert(
        self,
        alert_data: Dict,
        pose_analysis: PoseAnalysis,
        session_exercise: SessionExercise
    ) -> InjuryRiskAlert:
        """Create an injury risk alert in the database"""
        try:
            severity_score = self._calculate_severity(alert_data)
            
            alert = InjuryRiskAlert.objects.create(
                user=self.user,
                pose_analysis=pose_analysis,
                session_exercise=session_exercise,
                alert_type=alert_data['alert_type'],
                risk_level=alert_data['risk_level'],
                joint_name=alert_data['joint_name'],
                current_angle=alert_data['current_angle'],
                safe_range_min=alert_data['safe_min'],
                safe_range_max=alert_data['safe_max'],
                angle_exceeded_by=alert_data['exceeded_by'],
                severity_score=severity_score,
                description=self._generate_description(alert_data),
                recommendation=self._generate_recommendation(alert_data),
            )

            self.logger.info(
                f"Created injury risk alert {alert.id} for {self.user.username}: "
                f"{alert.joint_name} exceeded by {alert_data['exceeded_by']:.1f}°"
            )
            
            return alert

        except Exception as e:
            self.logger.error(f"Error creating risk alert: {str(e)}")
            return None

    def _calculate_severity(self, alert_data: Dict) -> float:
        """Calculate severity score (0-100) for a risk"""
        try:
            risk_level_map = {'low': 25, 'medium': 50, 'high': 75, 'critical': 100}
            base_severity = risk_level_map.get(alert_data['risk_level'], 50)
            
            # Adjust by how much it exceeds safe range
            exceeded_by = alert_data['exceeded_by']
            adjustment = min(exceeded_by * 2, 25)  # Cap adjustment at 25
            
            severity = base_severity + adjustment
            return float(min(100, severity))

        except:
            return 50.0

    def _generate_description(self, alert_data: Dict) -> str:
        """Generate description of the risk"""
        joint = alert_data['joint_name']
        angle = alert_data['current_angle']
        safe_range = f"{alert_data['safe_min']}°-{alert_data['safe_max']}°"
        exceeded = alert_data['exceeded_by']
        
        return (
            f"{joint} angle exceeded safe range by {exceeded:.1f}°. "
            f"Current: {angle:.1f}°, Safe range: {safe_range}. "
            f"Risk level: {alert_data['risk_level'].upper()}"
        )

    def _generate_recommendation(self, alert_data: Dict) -> str:
        """Generate recommendation to reduce risk"""
        risk_level = alert_data['risk_level']
        joint = alert_data['joint_name']
        
        recommendations = {
            'critical': f"STOP exercise immediately. {joint} position is dangerous. "
                        f"Consult a physical therapist before continuing.",
            'high': f"Reduce range of motion on {joint}. "
                   f"Focus on controlled movement within safe range.",
            'medium': f"Be cautious with {joint} positioning. "
                     f"Maintain alignment and avoid forcing movement.",
        }
        
        return recommendations.get(risk_level, "Monitor joint positioning carefully.")


# ============================================================
# 3. EXERCISE CLASSIFICATION SYSTEM
# ============================================================

class ExerciseClassificationSystem:
    """
    Multi-dimensional exercise classification and matching system.
    Enables intelligent exercise recommendations and substitutions.
    """

    @staticmethod
    def get_exercise_classifications(exercise: Exercise) -> Dict[str, List[str]]:
        """
        Get all classifications for an exercise, organized by type.
        
        Returns:
            Dict mapping classification type to list of values
        """
        try:
            classifications = ExerciseClassification.objects.filter(exercise=exercise)
            
            result = {}
            for classification in classifications:
                key = classification.get_classification_type_display()
                if key not in result:
                    result[key] = []
                result[key].append(classification.classification_value)

            return result

        except Exception as e:
            logger.error(f"Error getting classifications: {str(e)}")
            return {}

    @staticmethod
    def find_similar_exercises(
        exercise: Exercise,
        similarity_threshold: float = 0.7,
        max_results: int = 5
    ) -> List[Tuple[Exercise, float]]:
        """
        Find exercises similar to the given exercise based on classifications.
        
        Returns:
            List of (exercise, similarity_score) tuples, sorted by score
        """
        try:
            source_classifications = ExerciseClassification.objects.filter(
                exercise=exercise
            ).values_list('classification_type', 'classification_value', 'weight')

            if not source_classifications:
                return []

            # Build query for similar exercises
            all_exercises = Exercise.objects.filter(is_active=True).exclude(id=exercise.id)
            similar = []

            for other_exercise in all_exercises:
                similarity = ExerciseClassificationSystem._calculate_similarity(
                    source_classifications,
                    other_exercise
                )
                
                if similarity >= similarity_threshold:
                    similar.append((other_exercise, similarity))

            # Sort by similarity score descending
            similar.sort(key=lambda x: x[1], reverse=True)
            return similar[:max_results]

        except Exception as e:
            logger.error(f"Error finding similar exercises: {str(e)}")
            return []

    @staticmethod
    def _calculate_similarity(
        source_classifications,
        target_exercise: Exercise
    ) -> float:
        """Calculate similarity score between two exercises (0-1)"""
        try:
            target_classifications = ExerciseClassification.objects.filter(
                exercise=target_exercise
            ).values_list('classification_type', 'classification_value', 'weight')

            if not target_classifications:
                return 0.0

            # Convert to dicts for easier comparison
            source_dict = {(ct, cv): w for ct, cv, w in source_classifications}
            target_dict = {(ct, cv): w for ct, cv, w in target_classifications}

            # Calculate weighted overlap
            total_weight = sum(source_dict.values())
            if total_weight == 0:
                return 0.0

            matched_weight = 0.0
            for key, weight in source_dict.items():
                if key in target_dict:
                    matched_weight += weight

            return matched_weight / total_weight

        except:
            return 0.0

    @staticmethod
    def recommend_exercise_for_goal(
        goal: str,
        difficulty: str = 'medium',
        max_results: int = 5
    ) -> List[Exercise]:
        """
        Recommend exercises for a specific therapeutic goal.
        
        Args:
            goal: Therapeutic goal (e.g., 'ROM', 'strength', 'mobility')
            difficulty: Exercise difficulty level
            max_results: Maximum exercises to return
            
        Returns:
            List of recommended exercises
        """
        try:
            # Find exercises with matching goal classification
            matching_classifications = ExerciseClassification.objects.filter(
                classification_type='recovery_focus',
                classification_value__icontains=goal
            ).values_list('exercise_id', flat=True)

            exercises = Exercise.objects.filter(
                id__in=matching_classifications,
                difficulty_level=difficulty,
                is_active=True
            )[:max_results]

            return list(exercises)

        except Exception as e:
            logger.error(f"Error recommending exercises: {str(e)}")
            return []

    @staticmethod
    def get_exercise_profile(exercise: Exercise) -> Dict:
        """
        Get comprehensive profile of an exercise including all classifications.
        
        Returns:
            Dict with exercise details and classifications
        """
        try:
            classifications = ExerciseClassificationSystem.get_exercise_classifications(exercise)
            similar = ExerciseClassificationSystem.find_similar_exercises(exercise)
            
            return {
                'id': exercise.id,
                'name': exercise.name,
                'description': exercise.description,
                'difficulty_level': exercise.difficulty_level,
                'duration_seconds': exercise.duration_seconds,
                'muscle_groups': exercise.muscle_groups.split(',') if exercise.muscle_groups else [],
                'classifications': classifications,
                'similar_exercises': [
                    {
                        'id': ex.id,
                        'name': ex.name,
                        'similarity': float(score)
                    }
                    for ex, score in similar
                ],
            }

        except Exception as e:
            logger.error(f"Error getting exercise profile: {str(e)}")
            return {}


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def analyze_user_progress(user: User) -> Dict:
    """
    Comprehensive analysis of a user's progress across all advanced features.
    
    Returns:
        Dict with adaptive difficulty, injury risks, and recommendations
    """
    try:
        # Analyze all exercises
        exercises = Exercise.objects.filter(is_active=True)
        difficulty_analysis = []
        risk_summary = {}
        
        difficulty_system = AdaptiveDifficultySystem(user)
        
        for exercise in exercises:
            analysis = difficulty_system.analyze_exercise(exercise)
            if 'error' not in analysis:
                difficulty_analysis.append(analysis)
        
        # Get recent injury risks
        recent_alerts = InjuryRiskAlert.objects.filter(
            user=user,
            is_resolved=False
        ).order_by('-detected_at')[:5]
        
        risk_summary = {
            'active_alerts': len(recent_alerts),
            'critical_count': sum(1 for a in recent_alerts if a.risk_level == 'critical'),
            'recent_alerts': [
                {
                    'id': a.id,
                    'type': a.alert_type,
                    'risk_level': a.risk_level,
                    'joint': a.joint_name,
                }
                for a in recent_alerts
            ]
        }
        
        return {
            'user_id': user.id,
            'username': user.username,
            'difficulty_analysis': difficulty_analysis,
            'risk_summary': risk_summary,
            'timestamp': datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error analyzing user progress: {str(e)}")
        return {'error': str(e)}
