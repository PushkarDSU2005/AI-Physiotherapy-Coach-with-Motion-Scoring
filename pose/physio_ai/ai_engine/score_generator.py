"""
Score Generator Module

High-level interface for generating exercise scores from pose data.
Coordinates all scoring components and produces actionable feedback.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json

# Import local modules
from .joint_angle_calculator import JointAngleCalculator, JointKinematics
from .ideal_angles_library import ExerciseAngleLookup, JointAngleRange
from .mistake_detector import MistakeDetector, MistakeSeverityAnalyzer
from .core_scoring import (
    CoreScoringEngine,
    ExerciseMetrics,
    ScoreComponents,
    ScoringResult,
    RepAnalyzer,
    SessionScoringAggregator
)


@dataclass
class PoseFrame:
    """Single frame of pose data."""
    frame_number: int
    timestamp: float
    landmarks: Dict[str, Dict[str, float]]  # joint_name -> {x, y, confidence}
    confidence: float


@dataclass
class ExerciseSession:
    """Collection of pose frames for an exercise."""
    exercise_id: int
    exercise_name: str
    frames: List[PoseFrame]
    reps_count: int = 0


class ScoreGenerator:
    """
    Main interface for generating scores from pose data.
    
    Usage:
        generator = ScoreGenerator()
        result = generator.score_exercise(
            exercise_id=1,
            frames=[...],
            reps=5
        )
        print(result.scores.overall_score)
    """
    
    def __init__(self):
        self.angle_calculator = JointAngleCalculator()
        self.kinematics = JointKinematics()
        self.mistake_detector = MistakeDetector()
        self.scoring_engine = CoreScoringEngine()
        self.rep_analyzer = RepAnalyzer()
    
    def score_exercise(
        self,
        exercise_id: int,
        frames: List[Dict],
        reps_count: int = 0
    ) -> Optional[ScoringResult]:
        """
        Score an exercise based on pose frames.
        
        Args:
            exercise_id: ID of the exercise
            frames: List of frame dicts with landmarks
            reps_count: Number of reps performed (optional)
            
        Returns:
            ScoringResult with scores and feedback
        """
        # Get exercise profile
        exercise_profile = ExerciseAngleLookup.get_exercise_profile(exercise_id)
        if not exercise_profile:
            return None
        
        # Convert frames to internal format
        pose_frames = [
            PoseFrame(
                frame_number=i,
                timestamp=f.get('timestamp_seconds', i * 0.033),  # ~30fps
                landmarks=f.get('detected_joint_angles', {}),
                confidence=f.get('pose_detection_confidence', 0)
            )
            for i, f in enumerate(frames)
        ]
        
        # Extract metrics
        metrics = self._extract_metrics(
            pose_frames,
            exercise_profile,
            reps_count
        )
        
        # Detect mistakes
        mistake_counts = self._detect_mistakes(metrics, exercise_profile)
        
        # Score exercise
        result = self.scoring_engine.score_exercise(
            metrics,
            exercise_profile.joint_angles,
            mistake_counts
        )
        
        return result
    
    def _extract_metrics(
        self,
        frames: List[PoseFrame],
        exercise_profile,
        reps_count: int
    ) -> ExerciseMetrics:
        """Extract metrics from pose frames."""
        
        metrics = ExerciseMetrics(
            session_exercise_id=0,
            exercise_name=exercise_profile.exercise_name,
            total_frames=len(frames)
        )
        
        joint_names = exercise_profile.get_all_joint_names()
        
        # Initialize tracking structures
        for joint in joint_names:
            metrics.joint_angles_history[joint] = []
            metrics.angle_errors[joint] = []
            metrics.angle_deviations[joint] = []
            metrics.stability_scores[joint] = 0.0
        
        previous_angles = {}
        velocities = []
        
        # Process each frame
        for frame_idx, frame in enumerate(frames):
            if not frame.landmarks:
                continue
            
            # Calculate angles for this frame
            frame_angles = {}
            for joint in joint_names:
                ideal_range = exercise_profile.get_joint_angle(joint)
                if ideal_range:
                    # For simplicity, assume landmarks contain the calculated angles
                    angle = frame.landmarks.get(joint, 0)
                    frame_angles[joint] = angle
                    
                    # Track angle history
                    metrics.joint_angles_history[joint].append(angle)
                    
                    # Calculate error from ideal range
                    error = ideal_range.get_error(angle)
                    metrics.angle_errors[joint].append(error)
                    
                    # Calculate deviation from center of range
                    range_center = (ideal_range.min_angle + ideal_range.max_angle) / 2
                    deviation = angle - range_center
                    metrics.angle_deviations[joint].append(deviation)
            
            # Calculate velocity/smoothness
            if previous_angles:
                frame_velocity = 0
                for joint, angle in frame_angles.items():
                    if joint in previous_angles:
                        angle_diff = abs(angle - previous_angles[joint])
                        frame_velocity += angle_diff
                
                velocities.append(frame_velocity)
                metrics.frame_velocities.append(frame_velocity)
            
            previous_angles = frame_angles
        
        # Calculate aggregate metrics
        if velocities:
            metrics.average_velocity = sum(velocities) / len(velocities)
            metrics.peak_velocity = max(velocities)
            # Smoothness: inverse of velocity variance
            if len(velocities) > 1:
                import statistics
                try:
                    vel_stdev = statistics.stdev(velocities)
                    metrics.movement_smoothness = max(0, 100 - vel_stdev)
                except:
                    metrics.movement_smoothness = 50
        
        # Calculate ROM
        for joint, angles in metrics.joint_angles_history.items():
            if angles:
                ideal_range = exercise_profile.get_joint_angle(joint)
                if ideal_range:
                    achieved_range = max(angles) - min(angles)
                    expected_range = ideal_range.max_angle - ideal_range.min_angle
                    
                    rom_pct = (achieved_range / expected_range * 100) if expected_range > 0 else 0
                    metrics.rom_achieved += rom_pct
                    metrics.rom_expected += 100
        
        if metrics.rom_expected > 0:
            metrics.rom_achieved = metrics.rom_achieved / len(metrics.joint_angles_history)
        
        # Set rep counts
        metrics.reps_completed = reps_count
        
        return metrics
    
    def _detect_mistakes(
        self,
        metrics: ExerciseMetrics,
        exercise_profile
    ) -> Dict:
        """Detect mistakes in exercise execution."""
        
        mistake_counts = {
            "critical": 0,
            "severe": 0,
            "moderate": 0,
            "mild": 0,
            "total": 0
        }
        
        # Check for stability issues
        for joint, angles in metrics.joint_angles_history.items():
            if len(angles) > 5:
                import statistics
                try:
                    stdev = statistics.stdev(angles)
                    if stdev > 15:
                        mistake_counts["moderate"] += 1
                    elif stdev > 25:
                        mistake_counts["severe"] += 1
                except:
                    pass
        
        # Check angle errors
        for joint, errors in metrics.angle_errors.items():
            if errors:
                avg_error = sum(errors) / len(errors)
                if avg_error > 30:
                    mistake_counts["severe"] += 1
                elif avg_error > 20:
                    mistake_counts["moderate"] += 1
                elif avg_error > 10:
                    mistake_counts["mild"] += 1
        
        # Check for incomplete ROM
        ideal_range = list(exercise_profile.joint_angles.values())[0]
        if metrics.rom_achieved < 50:
            mistake_counts["moderate"] += 1
        
        mistake_counts["total"] = sum(
            mistake_counts[k] for k in ["critical", "severe", "moderate", "mild"]
        )
        
        return mistake_counts
    
    def generate_feedback_message(
        self,
        result: ScoringResult
    ) -> Dict[str, any]:
        """
        Generate human-readable feedback.
        
        Returns:
            Dict with feedback messages
        """
        if not result:
            return {}
        
        scores = result.scores
        metrics = result.metrics
        
        feedback_data = {
            "overall_score": scores.overall_score,
            "form_score": scores.form_score,
            "consistency_score": scores.consistency_score,
            "rom_score": scores.range_of_motion_score,
            "safety_score": scores.safety_score,
            "summary": self._generate_summary(scores),
            "feedback": result.feedback,
            "recommendations": result.recommendations,
            "warnings": result.warnings,
            "metrics": {
                "total_frames": metrics.total_frames,
                "reps_completed": metrics.reps_completed,
                "rom_achieved": round(metrics.rom_achieved, 1),
                "average_velocity": round(metrics.average_velocity, 2),
                "movement_smoothness": round(metrics.movement_smoothness, 1),
            }
        }
        
        return feedback_data
    
    def _generate_summary(self, scores: ScoreComponents) -> str:
        """Generate one-line summary."""
        if scores.overall_score >= 90:
            return f"Excellent execution! Score: {scores.overall_score}/100 ⭐⭐⭐"
        elif scores.overall_score >= 80:
            return f"Great job! Score: {scores.overall_score}/100 ⭐⭐"
        elif scores.overall_score >= 70:
            return f"Good effort. Score: {scores.overall_score}/100 ⭐"
        elif scores.overall_score >= 50:
            return f"Keep improving. Score: {scores.overall_score}/100"
        else:
            return f"Focus on form. Score: {scores.overall_score}/100"
    
    def score_multiple_reps(
        self,
        exercise_id: int,
        rep_frames: List[List[Dict]]
    ) -> Dict:
        """
        Score multiple repetitions and analyze consistency.
        
        Args:
            exercise_id: Exercise ID
            rep_frames: List of frame lists, one per rep
            
        Returns:
            Results with rep breakdown
        """
        rep_results = []
        
        for rep_idx, rep in enumerate(rep_frames):
            result = self.score_exercise(exercise_id, rep, reps_count=1)
            if result:
                rep_results.append({
                    "rep_number": rep_idx + 1,
                    "score": result.scores.overall_score,
                    "form_score": result.scores.form_score,
                    "feedback": result.feedback[0] if result.feedback else ""
                })
        
        if rep_results:
            scores = [r["score"] for r in rep_results]
            avg_score = sum(scores) / len(scores)
            consistency = 100 - (max(scores) - min(scores))
            
            return {
                "total_reps": len(rep_results),
                "average_score": round(avg_score, 1),
                "best_rep": max(rep_results, key=lambda r: r["score"]),
                "worst_rep": min(rep_results, key=lambda r: r["score"]),
                "consistency_score": max(0, round(consistency, 1)),
                "rep_details": rep_results
            }
        
        return {}


class ScoringSummary:
    """Generate scoring summary and reports."""
    
    @staticmethod
    def generate_session_report(
        exercise_results: List[ScoringResult]
    ) -> Dict:
        """Generate comprehensive session report."""
        
        if not exercise_results:
            return {}
        
        aggregated = SessionScoringAggregator.aggregate_session_scores(exercise_results)
        
        report = {
            "session_summary": aggregated,
            "exercise_breakdown": [
                {
                    "name": r.metrics.exercise_name,
                    "score": r.scores.overall_score,
                    "form": r.scores.form_score,
                    "consistency": r.scores.consistency_score,
                    "rom": r.scores.range_of_motion_score,
                    "issues": len(r.metrics.mistakes_detected)
                }
                for r in exercise_results
            ],
            "key_takeaways": ScoringSummary._generate_takeaways(exercise_results),
            "next_session_focus": ScoringSummary._generate_next_focus(exercise_results)
        }
        
        return report
    
    @staticmethod
    def _generate_takeaways(results: List[ScoringResult]) -> List[str]:
        """Generate key takeaways from session."""
        takeaways = []
        
        avg_score = sum(r.scores.overall_score for r in results) / len(results)
        
        if avg_score >= 85:
            takeaways.append("Great session! Maintain your current form consistency.")
        elif avg_score >= 75:
            takeaways.append("Good performance. Focus on fine-tuning your technique.")
        else:
            takeaways.append("You're making progress. Keep practicing form.")
        
        # Check form issues
        form_issues = sum(1 for r in results if r.scores.form_score < 75)
        if form_issues > 0:
            takeaways.append(f"{form_issues} exercise(s) need form correction.")
        
        return takeaways
    
    @staticmethod
    def _generate_next_focus(results: List[ScoringResult]) -> List[str]:
        """Generate focus areas for next session."""
        focus_areas = []
        
        # Find weakest area
        weakest = min(results, key=lambda r: r.scores.overall_score)
        focus_areas.append(f"Revisit '{weakest.metrics.exercise_name}' for form refinement.")
        
        # Check for consistency issues
        consistency_issues = [r for r in results if r.scores.consistency_score < 80]
        if consistency_issues:
            focus_areas.append("Work on movement stability and control.")
        
        # Check ROM
        rom_issues = [r for r in results if r.scores.range_of_motion_score < 70]
        if rom_issues:
            focus_areas.append("Increase range of motion through full, controlled movements.")
        
        return focus_areas[:3]  # Top 3 focus areas


# Convenience function
def generate_exercise_score(
    exercise_id: int,
    frames: List[Dict],
    reps: int = 0
) -> Optional[Dict]:
    """
    Simple function to generate exercise score.
    
    Args:
        exercise_id: Exercise ID
        frames: List of pose frames
        reps: Number of reps
        
    Returns:
        Score dictionary
    """
    generator = ScoreGenerator()
    result = generator.score_exercise(exercise_id, frames, reps)
    if result:
        return generator.generate_feedback_message(result)
    return None
