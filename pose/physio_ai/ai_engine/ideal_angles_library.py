"""
Ideal Angles Library

Comprehensive database of ideal joint angles for physiotherapy exercises.
These are based on standard physiotherapy guidelines and biomechanics.

Sources:
- American Academy of Orthopedic Surgeons (AAOS) Guidelines
- International Society of Biomechanics (ISB) Standards
- Evidence-based physiotherapy practices
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class JointAngleRange:
    """Represents ideal angle range for a joint movement."""
    name: str
    min_angle: float  # Minimum ideal angle
    max_angle: float  # Maximum ideal angle
    optimal_angle: Optional[float] = None  # Target angle (if specific)
    tolerance: float = 5.0  # Tolerance range in degrees
    critical_tolerance: float = 15.0  # Beyond this = critical error
    
    def is_within_range(self, angle: float) -> bool:
        """Check if angle is within acceptable range."""
        return self.min_angle <= angle <= self.max_angle
    
    def is_within_tolerance(self, angle: float) -> bool:
        """Check if angle is within tolerance band."""
        return (self.min_angle - self.tolerance <= angle <= 
                self.max_angle + self.tolerance)
    
    def get_error(self, angle: float) -> float:
        """Calculate error from ideal range."""
        if self.is_within_range(angle):
            return 0.0
        elif angle < self.min_angle:
            return self.min_angle - angle
        else:
            return angle - self.max_angle


@dataclass
class ExerciseAngleProfile:
    """Complete angle profile for an exercise."""
    exercise_id: int
    exercise_name: str
    description: str
    joint_angles: Dict[str, JointAngleRange] = field(default_factory=dict)
    peak_position_joints: Dict[str, Dict[str, float]] = field(default_factory=dict)
    common_mistakes: List[str] = field(default_factory=list)
    movement_phases: List[str] = field(default_factory=list)
    
    def get_joint_angle(self, joint_name: str) -> Optional[JointAngleRange]:
        """Get angle range for specific joint."""
        return self.joint_angles.get(joint_name)
    
    def get_all_joint_names(self) -> List[str]:
        """Get list of all tracked joints."""
        return list(self.joint_angles.keys())


class IdealAnglesLibrary:
    """Database of ideal angles for all exercises."""
    
    # =========================================================================
    # SHOULDER EXERCISES
    # =========================================================================
    
    SHOULDER_RAISE = ExerciseAngleProfile(
        exercise_id=1,
        exercise_name="Shoulder Raise (Frontal)",
        description="Raise arms forward from neutral position",
        joint_angles={
            "shoulder_flexion": JointAngleRange(
                name="Shoulder Flexion",
                min_angle=0,
                max_angle=180,
                optimal_angle=90,
                tolerance=5.0,
                critical_tolerance=15.0
            ),
            "elbow": JointAngleRange(
                name="Elbow",
                min_angle=170,
                max_angle=180,
                optimal_angle=180,
                tolerance=10.0,
                critical_tolerance=20.0
            ),
            "wrist": JointAngleRange(
                name="Wrist Neutral",
                min_angle=0,
                max_angle=30,
                optimal_angle=15,
                tolerance=10.0,
                critical_tolerance=20.0
            )
        },
        peak_position_joints={
            "shoulder_peak": {"angle": 90, "phase": "top of raise"}
        },
        common_mistakes=[
            "Shoulder hunched (upper trap domination)",
            "Elbow bent",
            "Wrist flexion/extension",
            "Asymmetric raising"
        ],
        movement_phases=["raise", "hold", "lower"]
    )
    
    LATERAL_RAISE = ExerciseAngleProfile(
        exercise_id=2,
        exercise_name="Lateral Raise (Side)",
        description="Raise arms to the side from neutral position",
        joint_angles={
            "shoulder_abduction": JointAngleRange(
                name="Shoulder Abduction",
                min_angle=0,
                max_angle=180,
                optimal_angle=90,
                tolerance=5.0,
                critical_tolerance=15.0
            ),
            "elbow": JointAngleRange(
                name="Elbow",
                min_angle=170,
                max_angle=180,
                optimal_angle=180,
                tolerance=10.0,
                critical_tolerance=20.0
            ),
            "wrist_to_elbow_rotation": JointAngleRange(
                name="Wrist Alignment",
                min_angle=0,
                max_angle=45,
                optimal_angle=20,
                tolerance=10.0,
                critical_tolerance=20.0
            )
        },
        peak_position_joints={
            "shoulder_peak": {"angle": 90, "phase": "parallel to ground"}
        },
        common_mistakes=[
            "Shoulder shrug",
            "Excessive elbow bend",
            "Arms forward (anterior positioning)",
            "Wrist extension"
        ],
        movement_phases=["raise", "hold", "lower"]
    )
    
    SHOULDER_INTERNAL_ROTATION = ExerciseAngleProfile(
        exercise_id=3,
        exercise_name="Internal Rotation",
        description="Rotate shoulder internally with elbow bent 90°",
        joint_angles={
            "shoulder_rotation": JointAngleRange(
                name="Internal Rotation",
                min_angle=0,
                max_angle=90,
                optimal_angle=70,
                tolerance=5.0,
                critical_tolerance=15.0
            ),
            "elbow_flexion": JointAngleRange(
                name="Elbow Flexion",
                min_angle=85,
                max_angle=95,
                optimal_angle=90,
                tolerance=5.0,
                critical_tolerance=10.0
            ),
            "upper_arm_abduction": JointAngleRange(
                name="Upper Arm Abduction",
                min_angle=85,
                max_angle=95,
                optimal_angle=90,
                tolerance=5.0,
                critical_tolerance=10.0
            )
        },
        peak_position_joints={
            "rotation_peak": {"angle": 70, "phase": "maximum internal rotation"}
        },
        common_mistakes=[
            "Elbow moves away from body",
            "Wrist rotation substitution",
            "Insufficient shoulder external rotation at start",
            "Upper arm not horizontal"
        ],
        movement_phases=["rotate_internal", "return"]
    )
    
    # =========================================================================
    # ELBOW EXERCISES
    # =========================================================================
    
    BICEP_CURL = ExerciseAngleProfile(
        exercise_id=4,
        exercise_name="Bicep Curl",
        description="Curl weight from extended to flexed position",
        joint_angles={
            "elbow_flexion": JointAngleRange(
                name="Elbow Flexion",
                min_angle=0,
                max_angle=150,
                optimal_angle=140,
                tolerance=5.0,
                critical_tolerance=15.0
            ),
            "shoulder_flexion": JointAngleRange(
                name="Shoulder Stability",
                min_angle=0,
                max_angle=30,
                optimal_angle=10,
                tolerance=10.0,
                critical_tolerance=20.0
            ),
            "wrist": JointAngleRange(
                name="Wrist Position",
                min_angle=-30,
                max_angle=30,
                optimal_angle=0,
                tolerance=10.0,
                critical_tolerance=20.0
            )
        },
        peak_position_joints={
            "peak_flexion": {"angle": 140, "phase": "fully flexed"}
        },
        common_mistakes=[
            "Shoulder elevation (shrug)",
            "Elbow moves forward",
            "Wrist deviation",
            "Incomplete ROM",
            "Swinging motion"
        ],
        movement_phases=["lift", "hold", "lower"]
    )
    
    TRICEP_EXTENSION = ExerciseAngleProfile(
        exercise_id=5,
        exercise_name="Tricep Extension",
        description="Extend arm from flexed to extended position",
        joint_angles={
            "elbow_extension": JointAngleRange(
                name="Elbow Extension",
                min_angle=0,
                max_angle=180,
                optimal_angle=170,
                tolerance=5.0,
                critical_tolerance=15.0
            ),
            "shoulder": JointAngleRange(
                name="Shoulder Stability",
                min_angle=0,
                max_angle=45,
                optimal_angle=20,
                tolerance=10.0,
                critical_tolerance=20.0
            ),
            "wrist": JointAngleRange(
                name="Wrist Position",
                min_angle=-20,
                max_angle=20,
                optimal_angle=0,
                tolerance=10.0,
                critical_tolerance=20.0
            )
        },
        peak_position_joints={
            "full_extension": {"angle": 170, "phase": "fully extended"}
        },
        common_mistakes=[
            "Shoulder movement",
            "Incomplete extension",
            "Wrist deviation",
            "Elbow moving outward",
            "Trunk compensation"
        ],
        movement_phases=["flex", "extend", "return"]
    )
    
    # =========================================================================
    # HIP & LEG EXERCISES
    # =========================================================================
    
    SQUAT = ExerciseAngleProfile(
        exercise_id=6,
        exercise_name="Squat",
        description="Squat from standing to 90° knee flexion",
        joint_angles={
            "hip_flexion": JointAngleRange(
                name="Hip Flexion",
                min_angle=60,
                max_angle=110,
                optimal_angle=90,
                tolerance=5.0,
                critical_tolerance=15.0
            ),
            "knee_flexion": JointAngleRange(
                name="Knee Flexion",
                min_angle=70,
                max_angle=110,
                optimal_angle=90,
                tolerance=5.0,
                critical_tolerance=15.0
            ),
            "ankle_dorsiflexion": JointAngleRange(
                name="Ankle Dorsiflexion",
                min_angle=80,
                max_angle=100,
                optimal_angle=90,
                tolerance=10.0,
                critical_tolerance=20.0
            ),
            "spine_extension": JointAngleRange(
                name="Spine Alignment",
                min_angle=170,
                max_angle=180,
                optimal_angle=175,
                tolerance=10.0,
                critical_tolerance=20.0
            )
        },
        peak_position_joints={
            "bottom_squat": {"angle": 90, "phase": "maximum depth"}
        },
        common_mistakes=[
            "Knees caving inward (valgus)",
            "Excessive forward lean",
            "Heels lifting",
            "Incomplete knee flexion",
            "Asymmetric descent"
        ],
        movement_phases=["descend", "hold", "ascend"]
    )
    
    STRAIGHT_LEG_RAISE = ExerciseAngleProfile(
        exercise_id=7,
        exercise_name="Straight Leg Raise",
        description="Raise straight leg from lying position",
        joint_angles={
            "hip_flexion": JointAngleRange(
                name="Hip Flexion",
                min_angle=0,
                max_angle=90,
                optimal_angle=75,
                tolerance=5.0,
                critical_tolerance=15.0
            ),
            "knee_extension": JointAngleRange(
                name="Knee Extension",
                min_angle=170,
                max_angle=180,
                optimal_angle=180,
                tolerance=5.0,
                critical_tolerance=10.0
            ),
            "ankle": JointAngleRange(
                name="Ankle Position",
                min_angle=-20,
                max_angle=20,
                optimal_angle=0,
                tolerance=10.0,
                critical_tolerance=20.0
            )
        },
        peak_position_joints={
            "raised_position": {"angle": 75, "phase": "leg elevated"}
        },
        common_mistakes=[
            "Knee flexion",
            "Hip rotation",
            "Excessive lower back extension",
            "Incomplete lift"
        ],
        movement_phases=["raise", "hold", "lower"]
    )
    
    # =========================================================================
    # ROTATIONAL EXERCISES
    # =========================================================================
    
    TORSO_ROTATION = ExerciseAngleProfile(
        exercise_id=8,
        exercise_name="Torso Rotation",
        description="Rotate torso from neutral with arms extended",
        joint_angles={
            "spine_rotation": JointAngleRange(
                name="Spine Rotation",
                min_angle=30,
                max_angle=90,
                optimal_angle=45,
                tolerance=5.0,
                critical_tolerance=15.0
            ),
            "shoulder_abduction": JointAngleRange(
                name="Shoulder Abduction",
                min_angle=80,
                max_angle=100,
                optimal_angle=90,
                tolerance=10.0,
                critical_tolerance=20.0
            ),
            "elbow": JointAngleRange(
                name="Elbow Extension",
                min_angle=170,
                max_angle=180,
                optimal_angle=180,
                tolerance=10.0,
                critical_tolerance=20.0
            )
        },
        peak_position_joints={
            "max_rotation": {"angle": 45, "phase": "maximum rotation"}
        },
        common_mistakes=[
            "Arm drop (loss of position)",
            "Hip rotation compensation",
            "Incomplete torso rotation",
            "Excessive lumbar extension",
            "Asymmetric rotation"
        ],
        movement_phases=["rotate_left", "return", "rotate_right"]
    )
    
    # =========================================================================
    # ADDITIONAL EXERCISES
    # =========================================================================
    
    PLANK = ExerciseAngleProfile(
        exercise_id=9,
        exercise_name="Plank Hold",
        description="Hold plank position with arms extended",
        joint_angles={
            "elbow_extension": JointAngleRange(
                name="Elbow Extension",
                min_angle=170,
                max_angle=180,
                optimal_angle=180,
                tolerance=10.0,
                critical_tolerance=20.0
            ),
            "shoulder_abduction": JointAngleRange(
                name="Shoulder Abduction",
                min_angle=70,
                max_angle=100,
                optimal_angle=90,
                tolerance=10.0,
                critical_tolerance=20.0
            ),
            "hip_extension": JointAngleRange(
                name="Hip Extension",
                min_angle=170,
                max_angle=180,
                optimal_angle=180,
                tolerance=10.0,
                critical_tolerance=20.0
            ),
            "spine_alignment": JointAngleRange(
                name="Spine Alignment",
                min_angle=170,
                max_angle=180,
                optimal_angle=175,
                tolerance=10.0,
                critical_tolerance=20.0
            )
        },
        peak_position_joints={
            "hold_position": {"angle": 0, "phase": "static hold"}
        },
        common_mistakes=[
            "Hip sag (flexion)",
            "Shoulder shrug",
            "Head position (down)",
            "Excessive lordosis",
            "Unequal weight distribution"
        ],
        movement_phases=["hold"]
    )
    
    PUSH_UP = ExerciseAngleProfile(
        exercise_id=10,
        exercise_name="Push Up",
        description="Push up from ground or elevated surface",
        joint_angles={
            "elbow_flexion": JointAngleRange(
                name="Elbow Flexion",
                min_angle=50,
                max_angle=120,
                optimal_angle=90,
                tolerance=5.0,
                critical_tolerance=15.0
            ),
            "shoulder_flexion": JointAngleRange(
                name="Shoulder Flexion",
                min_angle=70,
                max_angle=110,
                optimal_angle=90,
                tolerance=10.0,
                critical_tolerance=20.0
            ),
            "hip_extension": JointAngleRange(
                name="Hip Extension",
                min_angle=170,
                max_angle=180,
                optimal_angle=180,
                tolerance=10.0,
                critical_tolerance=20.0
            ),
            "spine_alignment": JointAngleRange(
                name="Spine Alignment",
                min_angle=170,
                max_angle=180,
                optimal_angle=175,
                tolerance=10.0,
                critical_tolerance=20.0
            )
        },
        peak_position_joints={
            "bottom_position": {"angle": 90, "phase": "lowest point"},
            "top_position": {"angle": 0, "phase": "fully extended"}
        },
        common_mistakes=[
            "Elbows flaring out excessively",
            "Hip sag",
            "Incomplete ROM",
            "Head position",
            "Asymmetric movement"
        ],
        movement_phases=["descend", "ascend"]
    )


class ExerciseAngleLookup:
    """Lookup and retrieve exercise angle profiles."""
    
    # Exercise library
    EXERCISES = {
        1: IdealAnglesLibrary.SHOULDER_RAISE,
        2: IdealAnglesLibrary.LATERAL_RAISE,
        3: IdealAnglesLibrary.SHOULDER_INTERNAL_ROTATION,
        4: IdealAnglesLibrary.BICEP_CURL,
        5: IdealAnglesLibrary.TRICEP_EXTENSION,
        6: IdealAnglesLibrary.SQUAT,
        7: IdealAnglesLibrary.STRAIGHT_LEG_RAISE,
        8: IdealAnglesLibrary.TORSO_ROTATION,
        9: IdealAnglesLibrary.PLANK,
        10: IdealAnglesLibrary.PUSH_UP,
    }
    
    @classmethod
    def get_exercise_profile(cls, exercise_id: int) -> Optional[ExerciseAngleProfile]:
        """Get angle profile for exercise."""
        return cls.EXERCISES.get(exercise_id)
    
    @classmethod
    def get_exercise_by_name(cls, name: str) -> Optional[ExerciseAngleProfile]:
        """Get angle profile by exercise name."""
        for profile in cls.EXERCISES.values():
            if profile.exercise_name.lower() == name.lower():
                return profile
        return None
    
    @classmethod
    def get_all_exercises(cls) -> Dict[int, ExerciseAngleProfile]:
        """Get all exercise profiles."""
        return cls.EXERCISES.copy()
    
    @classmethod
    def get_joint_range(cls, exercise_id: int, joint_name: str) -> Optional[JointAngleRange]:
        """Get specific joint range for exercise."""
        profile = cls.get_exercise_profile(exercise_id)
        if profile:
            return profile.get_joint_angle(joint_name)
        return None
