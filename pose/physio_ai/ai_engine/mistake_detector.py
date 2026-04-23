"""
Mistake Detector Module

Identifies form mistakes and issues in exercise execution based on joint angles.
Provides detailed feedback on what went wrong and severity levels.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class MistakeSeverity(Enum):
    """Severity levels for detected mistakes."""
    MILD = 1  # Small deviation, doesn't significantly impact effectiveness
    MODERATE = 2  # Noticeable deviation, affects effectiveness
    SEVERE = 3  # Critical error, can cause injury or major ineffectiveness
    CRITICAL = 4  # Dangerous error, high injury risk


@dataclass
class MistakeDetection:
    """Represents a detected mistake."""
    mistake_id: str
    name: str
    description: str
    severity: MistakeSeverity
    affected_joints: List[str]
    angle_deviations: Dict[str, float]  # Joint -> deviation in degrees
    frame_number: int
    recommendation: str
    prevention_tip: str


class MistakeDetector:
    """Detects and classifies form mistakes."""
    
    @staticmethod
    def detect_angle_error(
        measured_angle: float,
        ideal_range: 'JointAngleRange'
    ) -> Tuple[bool, float, str]:
        """
        Detect if angle is outside ideal range.
        
        Returns:
            (has_error, error_magnitude, severity_level)
        """
        error = ideal_range.get_error(measured_angle)
        
        if error == 0:
            return False, 0.0, "perfect"
        
        if error <= ideal_range.tolerance:
            return True, error, "mild"
        elif error <= ideal_range.critical_tolerance:
            return True, error, "moderate"
        else:
            return True, error, "severe"
    
    @staticmethod
    def detect_excessive_shoulder_elevation(
        shoulder_angle: float,
        neck_shoulder_distance: float,
        normal_distance: float
    ) -> Optional[MistakeDetection]:
        """
        Detect if shoulders are shrugged (elevated).
        
        Args:
            shoulder_angle: Angle at shoulder joint
            neck_shoulder_distance: Current distance from neck to shoulder
            normal_distance: Normal resting distance
        """
        elevation_ratio = neck_shoulder_distance / normal_distance if normal_distance > 0 else 1.0
        
        if elevation_ratio < 0.85:  # Shoulders elevated by 15%+
            return MistakeDetection(
                mistake_id="shoulder_elevation",
                name="Shoulder Shrug",
                description="Shoulders are elevated (shrugged)",
                severity=MistakeSeverity.MODERATE,
                affected_joints=["shoulder", "trapezius"],
                angle_deviations={"shoulder": -(1 - elevation_ratio) * 100},
                frame_number=0,
                recommendation="Lower shoulders away from ears",
                prevention_tip="Depress scapulae before starting movement"
            )
        return None
    
    @staticmethod
    def detect_elbow_flare(
        shoulder_angle: float,
        elbow_angle: float,
        expected_elbow_angle: float
    ) -> Optional[MistakeDetection]:
        """
        Detect if elbows are flaring out excessively during pressing movements.
        """
        elbow_deviation = abs(elbow_angle - expected_elbow_angle)
        
        if elbow_deviation > 20:
            return MistakeDetection(
                mistake_id="elbow_flare",
                name="Excessive Elbow Flare",
                description="Elbows are positioning away from body excessively",
                severity=MistakeSeverity.MODERATE,
                affected_joints=["elbow", "shoulder"],
                angle_deviations={"elbow": elbow_deviation},
                frame_number=0,
                recommendation="Keep elbows at ~45° angle from body",
                prevention_tip="Maintain elbows tucked closer to torso"
            )
        return None
    
    @staticmethod
    def detect_incomplete_range_of_motion(
        achieved_range: float,
        expected_range: float
    ) -> Optional[MistakeDetection]:
        """
        Detect if range of motion is incomplete.
        """
        rom_percentage = (achieved_range / expected_range * 100) if expected_range > 0 else 100
        
        if rom_percentage < 80:
            return MistakeDetection(
                mistake_id="incomplete_rom",
                name="Incomplete Range of Motion",
                description=f"Only achieving {rom_percentage:.1f}% of expected range",
                severity=MistakeSeverity.MODERATE,
                affected_joints=["primary_joint"],
                angle_deviations={"range": expected_range - achieved_range},
                frame_number=0,
                recommendation="Increase movement range to full motion",
                prevention_tip="Move through complete range without compensation"
            )
        return None
    
    @staticmethod
    def detect_asymmetric_movement(
        left_angle: float,
        right_angle: float,
        tolerance: float = 10.0
    ) -> Optional[MistakeDetection]:
        """
        Detect if left and right sides are unbalanced.
        """
        angle_difference = abs(left_angle - right_angle)
        
        if angle_difference > tolerance:
            return MistakeDetection(
                mistake_id="asymmetric_movement",
                name="Asymmetric Movement",
                description=f"Left and right sides differ by {angle_difference:.1f}°",
                severity=MistakeSeverity.MODERATE,
                affected_joints=["left_side", "right_side"],
                angle_deviations={"asymmetry": angle_difference},
                frame_number=0,
                recommendation="Balance movement on both sides equally",
                prevention_tip="Control each side independently, match angles"
            )
        return None
    
    @staticmethod
    def detect_compensatory_movement(
        primary_angle: float,
        compensatory_angle: float,
        primary_range: Tuple[float, float],
        should_be_stable: bool = True
    ) -> Optional[MistakeDetection]:
        """
        Detect if other joints are compensating for primary joint.
        
        Args:
            primary_angle: Angle of primary joint being worked
            compensatory_angle: Angle of joint that shouldn't move
            primary_range: Expected range of primary movement
            should_be_stable: If True, compensatory joint should not move
        """
        if should_be_stable and abs(compensatory_angle) > 10:
            return MistakeDetection(
                mistake_id="compensatory_movement",
                name="Compensatory Movement",
                description="Other joints are moving to compensate",
                severity=MistakeSeverity.SEVERE,
                affected_joints=["primary", "compensatory"],
                angle_deviations={"compensatory": compensatory_angle},
                frame_number=0,
                recommendation="Isolate primary joint, keep supporting joints stable",
                prevention_tip="Use proper form and reduce load if needed"
            )
        return None
    
    @staticmethod
    def detect_excessive_forward_lean(
        torso_angle: float,
        expected_angle: float,
        tolerance: float = 15.0
    ) -> Optional[MistakeDetection]:
        """
        Detect if torso is leaning forward excessively.
        """
        angle_deviation = abs(torso_angle - expected_angle)
        
        if angle_deviation > tolerance:
            return MistakeDetection(
                mistake_id="excessive_forward_lean",
                name="Excessive Forward Lean",
                description="Torso is leaning too far forward",
                severity=MistakeSeverity.SEVERE,
                affected_joints=["spine", "hip"],
                angle_deviations={"torso": angle_deviation},
                frame_number=0,
                recommendation="Maintain upright torso position",
                prevention_tip="Engage core, keep chest up"
            )
        return None
    
    @staticmethod
    def detect_knee_valgus(
        knee_angle_frontal: float,
        ankle_position: Dict[str, float],
        hip_position: Dict[str, float]
    ) -> Optional[MistakeDetection]:
        """
        Detect if knee is caving inward (valgus collapse).
        """
        # Calculate if knee is medial to ankle (valgus position)
        knee_x = 0  # Assume knee at center
        ankle_x = ankle_position.get('x', 0)
        hip_x = hip_position.get('x', 0)
        
        # If ankle is lateral to hip, knee shouldn't cross midline
        if hip_x > 0 and ankle_x > hip_x and knee_x < hip_x:
            return MistakeDetection(
                mistake_id="knee_valgus",
                name="Knee Valgus (Inward Cave)",
                description="Knee is caving inward, not tracking over ankle",
                severity=MistakeSeverity.CRITICAL,
                affected_joints=["knee", "hip", "ankle"],
                angle_deviations={"knee_alignment": 15.0},
                frame_number=0,
                recommendation="Track knee over middle toe, push knees outward",
                prevention_tip="Activate glutes, maintain hip abduction"
            )
        return None
    
    @staticmethod
    def detect_heel_lift(
        ankle_dorsiflexion: float,
        expected_range: Tuple[float, float]
    ) -> Optional[MistakeDetection]:
        """
        Detect if heels are lifting off ground.
        """
        if ankle_dorsiflexion < expected_range[0]:
            return MistakeDetection(
                mistake_id="heel_lift",
                name="Heel Lift",
                description="Heel is lifting off the ground",
                severity=MistakeSeverity.MODERATE,
                affected_joints=["ankle"],
                angle_deviations={"ankle": expected_range[0] - ankle_dorsiflexion},
                frame_number=0,
                recommendation="Keep heels planted on ground",
                prevention_tip="Maintain ankle dorsiflexion throughout movement"
            )
        return None
    
    @staticmethod
    def detect_insufficient_joint_stability(
        angle_variations: List[float],
        stability_threshold: float = 5.0
    ) -> Optional[MistakeDetection]:
        """
        Detect if a joint is too wobbly/unstable.
        """
        if not angle_variations or len(angle_variations) < 2:
            return None
        
        import statistics
        std_dev = statistics.stdev(angle_variations) if len(angle_variations) > 1 else 0
        
        if std_dev > stability_threshold:
            return MistakeDetection(
                mistake_id="insufficient_stability",
                name="Insufficient Stability",
                description=f"Joint movement is unstable (std dev: {std_dev:.1f}°)",
                severity=MistakeSeverity.MODERATE,
                affected_joints=["primary"],
                angle_deviations={"stability": std_dev},
                frame_number=0,
                recommendation="Stabilize the movement, reduce speed if needed",
                prevention_tip="Use controlled tempo, engage stabilizer muscles"
            )
        return None
    
    @staticmethod
    def detect_wrist_deviation(
        wrist_angle: float,
        expected_neutral: float = 0.0,
        tolerance: float = 15.0
    ) -> Optional[MistakeDetection]:
        """
        Detect if wrist is flexed/extended/deviated when should be neutral.
        """
        wrist_deviation = abs(wrist_angle - expected_neutral)
        
        if wrist_deviation > tolerance:
            direction = "flexed" if wrist_angle > expected_neutral else "extended"
            return MistakeDetection(
                mistake_id="wrist_deviation",
                name="Wrist Deviation",
                description=f"Wrist is {direction} (deviation: {wrist_deviation:.1f}°)",
                severity=MistakeSeverity.MILD,
                affected_joints=["wrist"],
                angle_deviations={"wrist": wrist_deviation},
                frame_number=0,
                recommendation="Keep wrist neutral and straight",
                prevention_tip="Maintain straight line from hand to forearm"
            )
        return None
    
    @staticmethod
    def detect_hip_sag_in_plank(
        hip_angle: float,
        torso_angle: float
    ) -> Optional[MistakeDetection]:
        """
        Detect if hips are sagging in plank position.
        """
        hip_torso_angle = abs(hip_angle - torso_angle)
        
        if hip_torso_angle > 15:  # Significant sag
            return MistakeDetection(
                mistake_id="hip_sag",
                name="Hip Sag",
                description="Hips are dropping, losing neutral spine",
                severity=MistakeSeverity.SEVERE,
                affected_joints=["hip", "spine"],
                angle_deviations={"hip": -hip_torso_angle},
                frame_number=0,
                recommendation="Engage core, maintain straight line",
                prevention_tip="Squeeze glutes, draw navel to spine"
            )
        return None


class MistakeSeverityAnalyzer:
    """Analyze overall mistake severity and impact."""
    
    @staticmethod
    def calculate_form_impact(
        mistakes: List[MistakeDetection]
    ) -> Tuple[float, str]:
        """
        Calculate how much mistakes impact overall form score.
        
        Returns:
            (score_reduction, severity_summary)
        """
        if not mistakes:
            return 0.0, "perfect"
        
        # Weight by severity
        severe_count = sum(1 for m in mistakes if m.severity == MistakeSeverity.CRITICAL)
        moderate_count = sum(1 for m in mistakes if m.severity == MistakeSeverity.SEVERE)
        mild_count = sum(1 for m in mistakes if m.severity == MistakeSeverity.MODERATE)
        minor_count = sum(1 for m in mistakes if m.severity == MistakeSeverity.MILD)
        
        # Calculate score reduction
        score_reduction = (severe_count * 25) + (moderate_count * 15) + (mild_count * 8) + (minor_count * 2)
        score_reduction = min(100, score_reduction)  # Cap at 100
        
        # Determine severity summary
        if severe_count > 0:
            severity_summary = "critical"
        elif moderate_count >= 2:
            severity_summary = "severe"
        elif moderate_count >= 1 or mild_count >= 3:
            severity_summary = "moderate"
        else:
            severity_summary = "minor"
        
        return score_reduction, severity_summary
    
    @staticmethod
    def generate_mistake_report(
        mistakes: List[MistakeDetection]
    ) -> Dict:
        """Generate comprehensive mistake report."""
        if not mistakes:
            return {
                "total_mistakes": 0,
                "severity_breakdown": {},
                "recommendations": [],
                "overall_assessment": "Excellent form!"
            }
        
        # Count by severity
        severity_counts = {
            "critical": sum(1 for m in mistakes if m.severity == MistakeSeverity.CRITICAL),
            "severe": sum(1 for m in mistakes if m.severity == MistakeSeverity.SEVERE),
            "moderate": sum(1 for m in mistakes if m.severity == MistakeSeverity.MODERATE),
            "mild": sum(1 for m in mistakes if m.severity == MistakeSeverity.MILD),
        }
        
        # Sort by severity
        sorted_mistakes = sorted(
            mistakes,
            key=lambda m: (m.severity.value, m.name),
            reverse=True
        )
        
        # Get unique recommendations
        recommendations = []
        seen = set()
        for mistake in sorted_mistakes:
            if mistake.recommendation not in seen:
                recommendations.append(mistake.recommendation)
                seen.add(mistake.recommendation)
        
        return {
            "total_mistakes": len(mistakes),
            "severity_breakdown": severity_counts,
            "mistakes_by_frame": {
                m.mistake_id: {
                    "name": m.name,
                    "severity": m.severity.name,
                    "description": m.description,
                    "recommendation": m.recommendation
                }
                for m in sorted_mistakes
            },
            "recommendations": recommendations[:5],  # Top 5 recommendations
            "overall_assessment": "Focus on form improvements" if mistakes else "Great form!"
        }
