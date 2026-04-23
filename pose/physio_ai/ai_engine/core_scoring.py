"""
Core Scoring Engine

Comprehensive scoring system for physiotherapy exercises based on:
- Form quality (proper joint angles and alignment)
- Consistency (stable, controlled movement)
- Range of motion (achieving full intended movement)
- Safety (no dangerous compensations)
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import statistics


@dataclass
class ExerciseMetrics:
    """Complete metrics for exercise performance."""
    session_exercise_id: int
    exercise_name: str
    total_frames: int
    
    # Angle data
    joint_angles_history: Dict[str, List[float]] = field(default_factory=dict)
    angle_errors: Dict[str, List[float]] = field(default_factory=dict)
    angle_deviations: Dict[str, List[float]] = field(default_factory=dict)
    
    # Movement data
    frame_velocities: List[float] = field(default_factory=list)
    movement_smoothness: float = 0.0
    peak_velocity: float = 0.0
    average_velocity: float = 0.0
    
    # Quality metrics
    stability_scores: Dict[str, float] = field(default_factory=dict)
    rom_achieved: float = 0.0  # Percentage
    rom_expected: float = 0.0
    
    # Mistakes and form issues
    mistakes_detected: List = field(default_factory=list)
    form_quality_points: float = 100.0
    safety_score: float = 100.0
    
    # Reps and sets
    reps_completed: int = 0
    sets_completed: int = 0
    reps_with_good_form: int = 0
    reps_with_poor_form: int = 0


@dataclass
class ScoreComponents:
    """Individual score components."""
    form_score: float  # 0-100: Quality of movement
    consistency_score: float  # 0-100: Stability and control
    range_of_motion_score: float  # 0-100: Achievement of full ROM
    safety_score: float  # 0-100: Absence of dangerous compensation
    rep_quality_score: float  # 0-100: Quality of individual reps
    overall_score: float  # 0-100: Combined weighted score


@dataclass
class ScoringResult:
    """Complete scoring result with recommendations."""
    scores: ScoreComponents
    metrics: ExerciseMetrics
    feedback: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    mistake_summary: Dict = field(default_factory=dict)


class CoreScoringEngine:
    """Main scoring engine that calculates all metrics."""
    
    # Scoring weights
    FORM_WEIGHT = 0.50  # Form quality is primary (50%)
    CONSISTENCY_WEIGHT = 0.30  # Consistency is important (30%)
    ROM_WEIGHT = 0.20  # ROM achievement (20%)
    
    @staticmethod
    def calculate_form_score(
        angle_errors: Dict[str, List[float]],
        ideal_ranges: Dict[str, 'JointAngleRange']
    ) -> float:
        """
        Calculate form score based on angle errors.
        
        Scoring:
        - 95-100: Perfect form (< 2° avg error)
        - 85-95: Excellent form (2-5° avg error)
        - 70-85: Good form (5-10° avg error)
        - 50-70: Fair form (10-20° avg error)
        - 0-50: Poor form (> 20° avg error)
        """
        if not angle_errors:
            return 0.0
        
        # Calculate average error per joint
        joint_errors = {}
        for joint, errors in angle_errors.items():
            if errors:
                avg_error = sum(errors) / len(errors)
                joint_errors[joint] = avg_error
        
        if not joint_errors:
            return 0.0
        
        # Calculate weighted average error
        total_error = sum(joint_errors.values()) / len(joint_errors)
        
        # Convert error to score using sigmoid-like function
        if total_error < 2:
            score = 100
        elif total_error < 5:
            score = 95 - (total_error - 2) * 2.5
        elif total_error < 10:
            score = 85 - (total_error - 5) * 3
        elif total_error < 20:
            score = 70 - (total_error - 10) * 2
        elif total_error < 30:
            score = 50 - (total_error - 20) * 2
        else:
            score = 30 - min(total_error - 30, 30)
        
        return max(0, round(min(100, score), 1))
    
    @staticmethod
    def calculate_consistency_score(
        joint_angles_history: Dict[str, List[float]],
        stability_threshold: float = 5.0
    ) -> float:
        """
        Calculate consistency score based on movement stability.
        
        Scoring:
        - 95-100: Very stable (< 2° std dev)
        - 85-95: Stable (2-5° std dev)
        - 70-85: Moderately stable (5-10° std dev)
        - 50-70: Somewhat unstable (10-20° std dev)
        - 0-50: Very unstable (> 20° std dev)
        """
        if not joint_angles_history:
            return 0.0
        
        # Calculate standard deviation for each joint
        joint_stabilities = {}
        for joint, angles in joint_angles_history.items():
            if len(angles) > 1:
                try:
                    std_dev = statistics.stdev(angles)
                    joint_stabilities[joint] = std_dev
                except:
                    continue
        
        if not joint_stabilities:
            return 0.0
        
        # Average stability across joints
        avg_std_dev = sum(joint_stabilities.values()) / len(joint_stabilities)
        
        # Convert to score
        if avg_std_dev < 2:
            score = 100
        elif avg_std_dev < 5:
            score = 95 - (avg_std_dev - 2) * 3.33
        elif avg_std_dev < 10:
            score = 85 - (avg_std_dev - 5) * 3
        elif avg_std_dev < 20:
            score = 70 - (avg_std_dev - 10) * 2
        elif avg_std_dev < 30:
            score = 50 - (avg_std_dev - 20)
        else:
            score = 50 - min(avg_std_dev - 30, 50)
        
        return max(0, round(min(100, score), 1))
    
    @staticmethod
    def calculate_rom_score(
        rom_achieved: float,
        rom_expected: float
    ) -> float:
        """
        Calculate range of motion score.
        
        Scoring:
        - 95-100: Full ROM (> 95%)
        - 85-95: Near full ROM (85-95%)
        - 70-85: Good ROM (70-85%)
        - 50-70: Partial ROM (50-70%)
        - 0-50: Limited ROM (< 50%)
        """
        if rom_expected == 0:
            return 0.0
        
        rom_percentage = (rom_achieved / rom_expected) * 100
        
        if rom_percentage >= 95:
            score = 100
        elif rom_percentage >= 85:
            score = 85 + (rom_percentage - 85) * 1.5
        elif rom_percentage >= 70:
            score = 70 + (rom_percentage - 70) * 1.0
        elif rom_percentage >= 50:
            score = 50 + (rom_percentage - 50) * 1.0
        else:
            score = rom_percentage
        
        return round(min(100, score), 1)
    
    @staticmethod
    def calculate_safety_score(
        mistakes_detected: List,
        critical_mistakes: int = 0,
        severe_mistakes: int = 0,
        moderate_mistakes: int = 0
    ) -> float:
        """
        Calculate safety score based on dangerous compensations.
        
        Scoring:
        - 100: No safety issues
        - 95-100: Minor issues only
        - 75-95: Moderate compensation detected
        - 50-75: Significant compensation
        - 0-50: Critical safety issues
        """
        if not mistakes_detected and critical_mistakes == 0:
            return 100.0
        
        # Penalty for mistakes by severity
        score = 100.0
        score -= critical_mistakes * 30  # Critical: -30 each
        score -= severe_mistakes * 15  # Severe: -15 each
        score -= moderate_mistakes * 5  # Moderate: -5 each
        
        return max(0, round(min(100, score), 1))
    
    @staticmethod
    def calculate_overall_score(
        form_score: float,
        consistency_score: float,
        rom_score: float,
        form_weight: float = 0.50,
        consistency_weight: float = 0.30,
        rom_weight: float = 0.20
    ) -> float:
        """
        Calculate weighted overall score.
        """
        overall = (
            (form_score * form_weight) +
            (consistency_score * consistency_weight) +
            (rom_score * rom_weight)
        )
        return round(min(100, max(0, overall)), 1)
    
    @classmethod
    def score_exercise(
        cls,
        metrics: ExerciseMetrics,
        ideal_ranges: Dict[str, 'JointAngleRange'],
        mistake_data: Dict
    ) -> ScoringResult:
        """
        Calculate complete scoring result for exercise.
        """
        # Calculate individual scores
        form_score = cls.calculate_form_score(metrics.angle_errors, ideal_ranges)
        consistency_score = cls.calculate_consistency_score(metrics.joint_angles_history)
        rom_score = cls.calculate_rom_score(metrics.rom_achieved, metrics.rom_expected)
        
        # Calculate safety score
        critical_mistakes = mistake_data.get('critical', 0)
        severe_mistakes = mistake_data.get('severe', 0)
        moderate_mistakes = mistake_data.get('moderate', 0)
        safety_score = cls.calculate_safety_score(
            metrics.mistakes_detected,
            critical_mistakes,
            severe_mistakes,
            moderate_mistakes
        )
        
        # Calculate rep quality
        if metrics.reps_completed > 0:
            rep_quality = (metrics.reps_with_good_form / metrics.reps_completed) * 100
        else:
            rep_quality = 0.0
        
        # Calculate overall score
        overall_score = cls.calculate_overall_score(
            form_score,
            consistency_score,
            rom_score,
            cls.FORM_WEIGHT,
            cls.CONSISTENCY_WEIGHT,
            cls.ROM_WEIGHT
        )
        
        # Apply safety penalty to overall score if needed
        if safety_score < 100:
            overall_score = (overall_score * 0.9) + (safety_score * 0.1)
            overall_score = round(overall_score, 1)
        
        # Create score components
        scores = ScoreComponents(
            form_score=form_score,
            consistency_score=consistency_score,
            range_of_motion_score=rom_score,
            safety_score=safety_score,
            rep_quality_score=round(rep_quality, 1),
            overall_score=overall_score
        )
        
        # Generate feedback
        feedback, recommendations, warnings = cls._generate_feedback(
            scores,
            metrics,
            mistake_data
        )
        
        return ScoringResult(
            scores=scores,
            metrics=metrics,
            feedback=feedback,
            recommendations=recommendations,
            warnings=warnings,
            mistake_summary=mistake_data
        )
    
    @staticmethod
    def _generate_feedback(
        scores: ScoreComponents,
        metrics: ExerciseMetrics,
        mistake_data: Dict
    ) -> Tuple[List[str], List[str], List[str]]:
        """Generate feedback based on scores."""
        feedback = []
        recommendations = []
        warnings = []
        
        # Form score feedback
        if scores.form_score >= 95:
            feedback.append("Excellent form! Movement is very precise.")
        elif scores.form_score >= 85:
            feedback.append("Good form overall with minor adjustments needed.")
        elif scores.form_score >= 70:
            feedback.append("Decent form, but several adjustments recommended.")
        elif scores.form_score >= 50:
            feedback.append("Form needs improvement. Focus on proper alignment.")
        else:
            feedback.append("Form requires significant correction.")
        
        # Consistency feedback
        if scores.consistency_score >= 90:
            feedback.append("Very stable, controlled movements.")
        elif scores.consistency_score >= 75:
            feedback.append("Movement is generally stable.")
        elif scores.consistency_score >= 50:
            feedback.append("Some wobbling detected. Work on stability.")
        else:
            feedback.append("Movement is jerky. Practice smooth, controlled motions.")
        
        # ROM feedback
        if scores.range_of_motion_score >= 95:
            feedback.append("Perfect range of motion achieved.")
        elif scores.range_of_motion_score >= 85:
            feedback.append("Good range achieved. Try to extend a bit more.")
        elif scores.range_of_motion_score >= 70:
            feedback.append("Partial range achieved. Increase movement range.")
        else:
            feedback.append("Limited range. Move through fuller motion.")
        
        # Safety feedback
        if scores.safety_score < 100:
            if mistake_data.get('critical', 0) > 0:
                warnings.append("CRITICAL: Dangerous form detected. Risk of injury!")
            if mistake_data.get('severe', 0) > 0:
                warnings.append("Significant compensatory movements detected.")
        
        # Rep quality
        if metrics.reps_completed > 0:
            good_form_pct = (metrics.reps_with_good_form / metrics.reps_completed) * 100
            if good_form_pct >= 80:
                recommendations.append(f"Maintain this consistency: {good_form_pct:.0f}% of reps with good form.")
            else:
                recommendations.append(f"Focus on maintaining form: Only {good_form_pct:.0f}% of reps had good form.")
        
        # Overall feedback
        if scores.overall_score >= 90:
            feedback.append("Outstanding performance!")
            recommendations.append("Keep pushing! You've got excellent form.")
        elif scores.overall_score >= 80:
            feedback.append("Great job! Keep practicing.")
        elif scores.overall_score >= 70:
            feedback.append("Good effort. Keep working on form consistency.")
        
        return feedback, recommendations, warnings


class RepAnalyzer:
    """Analyze individual repetitions."""
    
    @staticmethod
    def classify_rep_quality(
        form_score: float,
        rom_achieved: float,
        rom_expected: float,
        has_compensation: bool
    ) -> Tuple[str, str]:
        """
        Classify individual rep as good/fair/poor and provide reason.
        """
        rom_percentage = (rom_achieved / rom_expected * 100) if rom_expected > 0 else 0
        
        if form_score >= 85 and rom_percentage >= 80 and not has_compensation:
            return "good", "Full range with excellent form"
        elif form_score >= 75 and rom_percentage >= 70:
            return "fair", "Acceptable form but could be better"
        elif form_score >= 60 and rom_percentage >= 50:
            return "marginal", "Partial form, limited range"
        else:
            return "poor", "Poor form or very limited range"


class SessionScoringAggregator:
    """Aggregate scores across multiple exercises in a session."""
    
    @staticmethod
    def aggregate_session_scores(
        exercise_results: List[ScoringResult]
    ) -> Dict:
        """
        Aggregate results from multiple exercises.
        """
        if not exercise_results:
            return {}
        
        # Calculate averages
        avg_form = sum(r.scores.form_score for r in exercise_results) / len(exercise_results)
        avg_consistency = sum(r.scores.consistency_score for r in exercise_results) / len(exercise_results)
        avg_rom = sum(r.scores.range_of_motion_score for r in exercise_results) / len(exercise_results)
        avg_overall = sum(r.scores.overall_score for r in exercise_results) / len(exercise_results)
        
        # Count issues
        total_mistakes = sum(len(r.metrics.mistakes_detected) for r in exercise_results)
        critical_issues = sum(1 for r in exercise_results if any(r.warnings))
        
        return {
            "total_exercises": len(exercise_results),
            "average_form_score": round(avg_form, 1),
            "average_consistency_score": round(avg_consistency, 1),
            "average_rom_score": round(avg_rom, 1),
            "average_overall_score": round(avg_overall, 1),
            "total_mistakes_detected": total_mistakes,
            "critical_issues": critical_issues,
            "exercises_with_warnings": sum(1 for r in exercise_results if r.warnings),
            "best_exercise": max(exercise_results, key=lambda r: r.scores.overall_score).metrics.exercise_name,
            "best_score": max(r.scores.overall_score for r in exercise_results),
            "worst_exercise": min(exercise_results, key=lambda r: r.scores.overall_score).metrics.exercise_name,
            "worst_score": min(r.scores.overall_score for r in exercise_results),
        }
