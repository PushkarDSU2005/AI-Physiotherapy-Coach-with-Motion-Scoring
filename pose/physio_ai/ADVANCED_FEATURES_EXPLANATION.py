"""
ADVANCED FEATURES IMPLEMENTATION GUIDE
PhysioAI - Three Advanced AI Features

This guide explains the logic, implementation, and integration of three sophisticated
features for PhysioAI:

1. Adaptive Difficulty System - Automatically adjusts exercise difficulty based on performance trends
2. Injury Risk Detection - Monitors joint angles and flags unsafe positions
3. Multi-Exercise Classification - Enables intelligent exercise matching and recommendations
"""


# ============================================================
# FEATURE 1: ADAPTIVE DIFFICULTY SYSTEM
# ============================================================

"""
PURPOSE:
Intelligently adjust exercise difficulty based on user performance trends and preferences.
Instead of static difficulty levels, the system learns user progress and adapts exercises
to maintain optimal challenge level.

BUSINESS LOGIC:
1. Collect Performance Data
   - Track last 10 form scores for each exercise
   - Calculate average score, min/max, and standard deviation
   - Monitor consistency of performance (lower variation = more consistent)

2. Analyze Trend
   - Use linear regression to determine performance trajectory
   - Classify trend as: improving, declining, stable, or plateaued
   - Calculate trend confidence using R-squared metric
   - Slope > 2.0 = strong improvement, < -2.0 = strong decline

3. Generate Recommendations
   Four recommendation types:
   
   a) INCREASE Difficulty
      Conditions: avg_score >= 85 AND consistency >= 80 AND improving trend
      Rationale: User is performing well with consistent high scores and trending up
      Example: User completes 10 squats with average 88% form score, trending up 2.5°/session
      Action: Increase sets, reps, or range of motion
      
   b) MAINTAIN Current
      Conditions: avg_score >= 80 AND consistency >= 75
      Rationale: User is performing at good level, continue building strength
      Example: User maintains 82% average with stable trend
      Action: Keep current difficulty, focus on consistency
      
   c) DECREASE Difficulty
      Conditions: avg_score < 60 AND declining trend
      Rationale: User is struggling; reduce difficulty to prevent injury/frustration
      Example: User's scores dropped from 75% to 55% over 5 sessions
      Action: Reduce range of motion, increase support, or modify movement pattern
      
   d) MODIFY Exercise
      Conditions: avg_score >= 75 AND plateaued trend
      Rationale: User has plateaued; variation prevents adaptation stalling
      Example: User maintains 78% for 10 sessions with no change
      Action: Suggest alternative exercise or form variation

4. Auto-Adapt
   - If user enables auto-adapt preference, system modifies exercise difficulty
   - Creates audit trail of all adaptations
   - Tracks adaptation count per exercise

KEY MODELS:
- DifficultyAdaptation: Stores analysis and recommendations for user-exercise pairs
- UserDifficultyPreference: User settings (progression strategy, thresholds, sensitivities)

IMPLEMENTATION EXAMPLE:

from advanced_features.services import AdaptiveDifficultySystem
from exercises.models import Exercise

# Initialize system for a user
difficulty_system = AdaptiveDifficultySystem(request.user)

# Analyze a specific exercise
analysis = difficulty_system.analyze_exercise(exercise)

# Result structure:
{
    'exercise_id': 5,
    'exercise_name': 'Bodyweight Squat',
    'current_difficulty': 'medium',
    'metrics': {
        'average_score': 86.5,
        'min_score': 80.2,
        'max_score': 92.1,
        'consistency_score': 87.3,  # High = consistent performance
        'latest_score': 88.5,
        'sessions_count': 10
    },
    'trend': {
        'trend': 'improving',
        'slope': 2.3,  # Points per session
        'direction': 'up',
        'confidence': 92.5  # R-squared % 
    },
    'recommendation': {
        'type': 'increase',
        'difficulty': 'hard',
        'reason': 'Excellent performance with improving trend',
        'confidence': 92.5
    }
}

API ENDPOINTS:
POST /api/difficulty-adaptations/analyze/
    Analyzes all exercises for a user, returns list of recommendations

POST /api/difficulty-adaptations/{id}/apply_recommendation/
    Applies the recommended difficulty change to an exercise

GET /api/difficulty-adaptations/trending_down/
    Returns exercises where user's performance is declining

GET /api/difficulty-adaptations/ready_for_progression/
    Returns exercises ready for difficulty increase (avg_score >= 85)

ALGORITHM DETAILS:

1. TREND CALCULATION (Linear Regression):
   y = mx + b
   where:
   - m = slope (trend_slope field) = average score change per session
   - x = session number
   - b = intercept
   - R² = confidence level (0-1, how well line fits data)
   
   Example:
   Sessions: [1, 2, 3, 4, 5]
   Scores:   [70, 72, 75, 78, 82]
   Slope: 3.0 (improving by 3 points per session)
   R²: 0.98 (excellent fit, 98% confidence)

2. CONSISTENCY CALCULATION:
   consistency_score = 100 - (std_dev * 5)
   
   If std_dev = 0: consistency = 100 (perfect consistency)
   If std_dev = 5: consistency = 75 (moderate variation)
   If std_dev = 20: consistency = 0 (high variation)
   
   Capped at 0-100 range

3. PROGRESSION STRATEGIES:
   - Conservative: Requires 85+ score + 85+ consistency
   - Moderate: Requires 82+ score + 80+ consistency
   - Aggressive: Requires 78+ score + 75+ consistency
   - Adaptive (default): AI determines based on trend

DATABASE QUERIES:
- Last 10 sessions: SELECT from SessionExercise WHERE exercise_id=X
                    ORDER BY session__start_time DESC LIMIT 10
- Average score: SessionExercise.objects.filter(...).aggregate(Avg('form_score'))
- Trend analysis uses numpy.polyfit() for regression

INTEGRATION POINTS:
- Session completion: Automatically analyze exercise after completing session
- Therapy plan generation: Use recommendations to personalize weekly plans
- User dashboard: Display trending exercises and recommendations
- Mobile app: Push notifications for ready-for-progression exercises
"""


# ============================================================
# FEATURE 2: INJURY RISK DETECTION SYSTEM
# ============================================================

"""
PURPOSE:
Real-time monitoring of joint angles during exercise to detect and prevent injury.
When a user's joint position exceeds safe biomechanical ranges, the system alerts
them with specific corrections.

BUSINESS LOGIC:

1. SAFE ANGLE RANGES
   Different joints have different safe ranges based on:
   - Joint type (knee, shoulder, hip, spine, etc.)
   - Movement axis (flexion/extension, abduction/adduction, rotation)
   - Exercise type (squatting, pressing, reaching, etc.)
   - User condition (healthy, post-injury, conservative recovery)
   
   Example Safe Ranges:
   - Knee flexion (squatting): 0° to 120° (safe), 0° to 90° (conservative)
   - Shoulder external rotation: 0° to 90° (safe), 0° to 60° (conservative)
   - Lumbar spine flexion: 0° to 60° (safe), 0° to 30° (conservative)

2. ANGLE MONITORING
   During each pose analysis frame:
   a) Extract joint positions from detected_joints JSON
   b) Calculate joint angle using 3D coordinate geometry
   c) Compare against safe range for the exercise
   d) Generate alert if exceeded
   e) Calculate severity based on how much exceeded

3. RISK ASSESSMENT
   Risk Level Determination:
   
   CRITICAL (Risk Level = critical)
   - Angle exceeded by > 15° from safe range
   - Example: Knee bent to 135° when safe max is 120° (exceeded by 15°)
   - Action: STOP exercise immediately, consult PT
   - Severity: 75-100
   
   HIGH (Risk Level = high)
   - Angle exceeded by 5° to 15°
   - Example: Shoulder rotated to 105° when safe max is 90° (exceeded by 15°)
   - Action: Reduce range of motion, correct form
   - Severity: 50-75
   
   MEDIUM (Risk Level = medium)
   - Angle exceeded by < 5°
   - Example: Elbow hyperextension by 3°
   - Action: Monitor carefully, minor form adjustment
   - Severity: 25-50
   
   LOW (Risk Level = low)
   - Minor deviation from safe range
   - Action: Informational only
   - Severity: 0-25

4. ALERT GENERATION
   When risk detected:
   a) Create InjuryRiskAlert database record
   b) Store joint name, current angle, safe range, severity
   c) Calculate and store severity_score (0-100)
   d) Generate user-friendly description and recommendation
   e) Trigger notification if configured

KEY MODELS:
- InjuryRiskAlert: Stores detected risks with details
- JointSafetyProfile: Defines safe angle ranges per joint/exercise
- Alert tracking: is_acknowledged, is_resolved, resolution_notes

IMPLEMENTATION EXAMPLE:

from advanced_features.services import InjuryRiskDetectionSystem
from ai_engine.models import PoseAnalysis
from sessions.models import SessionExercise

# Initialize system for a user
risk_system = InjuryRiskDetectionSystem(request.user)

# After pose analysis, check for risks
pose_analysis = PoseAnalysis.objects.latest('id')
session_exercise = SessionExercise.objects.latest('id')

alerts = risk_system.analyze_pose(pose_analysis, session_exercise)

# Result per alert:
{
    'joint_name': 'left_knee',
    'current_angle': 135.2,
    'safe_min': 0.0,
    'safe_max': 120.0,
    'exceeded_by': 15.2,
    'risk_level': 'critical',
    'alert_type': 'joint_angle',
}

# Creates database record:
InjuryRiskAlert(
    user=user,
    pose_analysis=pose_analysis,
    session_exercise=session_exercise,
    alert_type='joint_angle',
    risk_level='critical',
    joint_name='left_knee',
    current_angle=135.2,
    safe_range_min=0.0,
    safe_range_max=120.0,
    angle_exceeded_by=15.2,
    severity_score=92.0,
    description="Left knee angle exceeded safe range by 15.2°. Current: 135.2°, 
                 Safe range: 0°-120°. Risk level: CRITICAL",
    recommendation="STOP exercise immediately. Left knee position is dangerous. 
                    Consult a physical therapist before continuing."
)

API ENDPOINTS:
GET /api/injury-risks/
    List all user's injury risk alerts

GET /api/injury-risks/active/
    Get unresolved injury risks (is_resolved=False)

GET /api/injury-risks/critical/
    Get all critical risk alerts

GET /api/injury-risks/summary/
    Get summary: {total, active, critical_count, high_count, ...}

POST /api/injury-risks/{id}/acknowledge/
    Mark alert as acknowledged (user saw it)

POST /api/injury-risks/{id}/resolve/
    Mark alert as resolved with optional resolution notes

SAFETY PROFILE SETUP:
First, define safe angle ranges in database:

JointSafetyProfile(
    joint_name='left_knee',
    movement_axis='flexion_extension',
    exercise_type='squatting',
    normal_min_angle=0.0,
    normal_max_angle=120.0,
    conservative_min_angle=0.0,
    conservative_max_angle=90.0,
    warning_threshold=5.0,      # Alert if exceeded by > 5°
    critical_threshold=15.0,    # Critical if exceeded by > 15°
    source='ISO_biomechanics_standard'
)

ANGLE CALCULATION (Geometry):
Given 3D joint positions (hip, knee, ankle):
1. Create vectors: V1 = hip - knee, V2 = ankle - knee
2. Calculate angle using dot product:
   cos(θ) = (V1 · V2) / (|V1| × |V2|)
   angle = arccos(cos(θ))
3. Compare angle to safe range

INTEGRATION POINTS:
- Pose analysis pipeline: Check angles after each frame
- Session completion: Summarize all risks detected
- User notifications: Alert on critical risks immediately
- Dashboard: Visual timeline of risk events
- Therapy plan adjustment: Reduce difficulty if repeated risks detected
"""


# ============================================================
# FEATURE 3: MULTI-EXERCISE CLASSIFICATION SYSTEM
# ============================================================

"""
PURPOSE:
Enable intelligent exercise matching, substitution, and recommendation based on
multi-dimensional classification. Instead of simple exercise lists, users get
context-aware recommendations.

CLASSIFICATION DIMENSIONS:

1. MOVEMENT PATTERN
   Describes how exercise moves: bilateral, unilateral, rotation, combination
   Examples: bilateral_squat, unilateral_lunge, rotation_twist
   
2. EQUIPMENT
   What's needed: bodyweight, band, dumbbells, barbell, cable, machine
   
3. INTENSITY
   Contraction type: isometric (static hold), dynamic (moving), explosive
   
4. PLANE OF MOTION
   Direction of movement: sagittal (front-back), frontal (side-to-side), transverse (rotation)
   
5. PRIMARY JOINT
   Main joint involved: knee, shoulder, hip, spine, ankle, elbow
   
6. SECONDARY JOINT
   Supporting joints: helps identify stability requirements
   
7. STABILIZATION
   Does it require core/balance? yes/no - helps identify fall-risk exercises
   
8. COMPLEXITY LEVEL
   Cognitive/motor load: simple, intermediate, complex
   
9. RECOVERY FOCUS
   Therapeutic goal: ROM (range of motion), mobility, strength, endurance, balance

CLASSIFICATION DATABASE:
Each exercise can have MULTIPLE classifications:

Exercise: Bodyweight Squat
├─ Movement Pattern: bilateral
├─ Equipment: bodyweight
├─ Intensity: dynamic
├─ Plane of Motion: sagittal
├─ Primary Joint: knee
├─ Primary Joint: hip
├─ Stabilization: yes
├─ Complexity Level: intermediate
└─ Recovery Focus: strength

SIMILARITY MATCHING ALGORITHM:

1. WEIGHTED MATCHING
   Each classification has a weight (0-1) indicating importance
   
   weight 1.0 = primary classification (can't substitute without it)
   weight 0.5 = secondary classification
   weight 0.2 = nice-to-have

2. SIMILARITY SCORE CALCULATION
   
   For two exercises:
   - Count matching classification types weighted by importance
   - Divide by total importance weight
   - Result: similarity score 0-1
   
   Example:
   Source: Bodyweight Squat
   Target: Goblet Squat
   
   Matching classifications:
   - Movement Pattern (bilateral): ✓ weight 1.0
   - Plane of Motion (sagittal): ✓ weight 0.8
   - Primary Joint (knee, hip): ✓ weight 1.0
   - Stabilization (yes): ✓ weight 0.5
   - Recovery Focus (strength): ✓ weight 0.7
   
   Total matched weight: 4.0
   Total possible weight: 4.0
   Similarity: 4.0 / 4.0 = 1.0 (100% match)
   
   Another target: Cable Leg Press
   
   Matching:
   - Movement Pattern (bilateral): ✓ weight 1.0
   - Primary Joint (knee, hip): ✓ weight 1.0
   - Recovery Focus (strength): ✓ weight 0.7
   - Stabilization (no - differs): ✗
   
   Total matched: 2.7
   Total possible: 4.0
   Similarity: 2.7 / 4.0 = 0.675 (67.5% match)

3. FILTERING
   Find exercises with similarity >= threshold (default 0.7)
   Sort by similarity score descending
   Return top N results (default 5)

RECOMMENDATION LOGIC:

1. GOAL-BASED RECOMMENDATIONS
   User specifies therapeutic goal (ROM, strength, mobility, endurance, balance)
   
   System filters exercises where:
   - Recovery Focus classification includes the goal
   - Difficulty matches user's level
   - Sorted by priority
   
   Example:
   Goal: "mobility" + Difficulty: "medium"
   
   Find all exercises with:
   ExerciseClassification.filter(
       classification_type='recovery_focus',
       classification_value__icontains='mobility',
       exercise__difficulty_level='medium'
   )

2. PROGRESSIVE RECOMMENDATIONS
   As user improves, suggest exercises in progression:
   
   Level 1 (Easy): Bodyweight, bilateral, sagittal
   Level 2 (Medium): Bodyweight + band, unilateral elements
   Level 3 (Hard): Dumbbells/weights, explosive, multi-planar
   Level 4 (Advanced): Complex patterns, balance requirements
   
   System recommends Level N+1 when Level N performance threshold met

IMPLEMENTATION EXAMPLE:

from advanced_features.services import ExerciseClassificationSystem
from exercises.models import Exercise

# Get classifications for an exercise
exercise = Exercise.objects.get(name='Bodyweight Squat')
classifications = ExerciseClassificationSystem.get_exercise_classifications(exercise)

Result:
{
    'Movement Pattern': ['bilateral'],
    'Equipment': ['bodyweight'],
    'Intensity': ['dynamic'],
    'Plane of Motion': ['sagittal'],
    'Primary Joint': ['knee', 'hip'],
    'Stabilization': ['yes'],
    'Complexity Level': ['intermediate'],
    'Recovery Focus': ['strength']
}

# Find similar exercises
similar = ExerciseClassificationSystem.find_similar_exercises(
    exercise,
    similarity_threshold=0.7,
    max_results=5
)

Result:
[
    (Exercise(name='Goblet Squat'), 0.98),
    (Exercise(name='Smith Machine Squat'), 0.85),
    (Exercise(name='Leg Press'), 0.75),
    (Exercise(name='Bulgarian Split Squat'), 0.72),
]

# Get recommendations for goal
recommendations = ExerciseClassificationSystem.recommend_exercise_for_goal(
    goal='strength',
    difficulty='medium',
    max_results=5
)

Result: [Exercise(...), Exercise(...), ...]

# Get full exercise profile
profile = ExerciseClassificationSystem.get_exercise_profile(exercise)

Result:
{
    'id': 1,
    'name': 'Bodyweight Squat',
    'description': '...',
    'difficulty_level': 'medium',
    'muscle_groups': ['quadriceps', 'glutes', 'hamstrings'],
    'classifications': {...},  # All classifications
    'similar_exercises': [...]  # Similar exercises with scores
}

API ENDPOINTS:
GET /api/exercise-classification/exercise/{id}/profile/
    Get comprehensive profile of an exercise with all classifications

GET /api/exercise-classification/exercise/{id}/similar/?threshold=0.7&limit=5
    Find similar exercises to substitute or progress to

GET /api/exercise-classification/recommendations/?goal=strength&difficulty=medium&limit=5
    Get personalized exercise recommendations for a goal

DATABASE STRUCTURE:
ExerciseClassification table:
├─ id
├─ exercise_id (ForeignKey)
├─ classification_type (8 choices)
├─ classification_value (text)
├─ weight (0-1 importance)
└─ unique_together: (exercise, type, value)

Queries:
- Find all classifications for exercise: ExerciseClassification.filter(exercise_id=X)
- Find all exercises with classification: ExerciseClassification.filter(
    classification_type='recovery_focus',
    classification_value='strength'
).values_list('exercise_id', flat=True)

INTEGRATION WITH ADAPTIVE DIFFICULTY:
When user is ready for progression, system:
1. Gets similar exercises with higher difficulty
2. Ranks by similarity to current exercise
3. Recommends top match for progression
4. Updates therapy plan with new exercise

Example:
User: "I'm ready to progress in squats"
System:
1. Finds current: Bodyweight Squat (medium)
2. Finds similar squats (hard): Goblet Squat (0.98), Smith Machine (0.85)
3. Recommends: Goblet Squat
4. Updates therapy plan: replace Bodyweight Squat with Goblet Squat

PRACTICAL WORKFLOW:

1. SETUP (Admin):
   - Create JointSafetyProfile records for each joint/exercise combo
   - Create ExerciseClassification records for each exercise dimension
   - Set weights based on importance

2. DURING EXERCISE (Runtime):
   - Pose analysis detects joint angles
   - InjuryRiskDetectionSystem.analyze_pose() checks against profiles
   - Alerts created if angles exceed safe ranges

3. AFTER SESSION (Analysis):
   - AdaptiveDifficultySystem.analyze_exercise() calculates trends
   - Recommendations generated based on performance
   - Auto-adapt applied if enabled

4. THERAPY PLANNING:
   - ExerciseClassificationSystem suggests progressions
   - User approves recommendations
   - Plan updated with new exercises

5. USER COMMUNICATION:
   - Dashboard shows trending exercises, risks, and progressions
   - Notifications for critical risks
   - Recommendations in weekly plan
"""


# ============================================================
# INTEGRATION & ARCHITECTURE
# ============================================================

"""
SYSTEM ARCHITECTURE:

┌─────────────────────────────────────────────────────────────┐
│                    USER EXERCISE SESSION                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              AI POSE ANALYSIS ENGINE                         │
│  - Detects joint positions                                  │
│  - Calculates form score                                    │
│  - Outputs: detected_joints JSON, form_score               │
└──────┬───────────────────┬──────────────────────┬───────────┘
       │                   │                      │
       ▼                   ▼                      ▼
┌─────────────────────┐ ┌────────────────┐ ┌────────────────┐
│ INJURY RISK        │ │ ADAPTIVE       │ │ EXERCISE       │
│ DETECTION          │ │ DIFFICULTY     │ │ CLASSIFICATION │
│                    │ │                │ │                │
│ - Check angles     │ │ - Collect      │ │ - Classify     │
│   vs safe ranges   │ │   scores       │ │   dimensions   │
│ - Generate alerts  │ │ - Analyze      │ │ - Find similar │
│ - Set severity     │ │   trend        │ │ - Recommend    │
│                    │ │ - Recommend    │ │   progressions │
│ Output:            │ │   difficulty   │ │                │
│ InjuryRiskAlert    │ │                │ │ Output:        │
│                    │ │ Output:        │ │ Classification │
│                    │ │ DifficultyAdap │ │ Records        │
│                    │ │                │ │                │
└──────┬─────────────┘ └────┬───────────┘ └────┬───────────┘
       │                    │                   │
       └────────┬───────────┴─────────┬────────┘
                │                     │
                ▼                     ▼
        ┌─────────────────────────────────────┐
        │   USER NOTIFICATIONS & DASHBOARD    │
        │                                     │
        │ - Injury warnings                   │
        │ - Difficulty recommendations         │
        │ - Exercise progressions              │
        │ - Performance trends                │
        └─────────────────────────────────────┘
                │
                ▼
        ┌─────────────────────────────────────┐
        │   THERAPY PLAN AUTO-ADJUSTMENT      │
        │                                     │
        │ - Update exercise difficulty        │
        │ - Suggest new exercises             │
        │ - Modify weekly schedule            │
        └─────────────────────────────────────┘

DATA FLOW:

1. Session starts
   ↓
2. Pose analysis runs → outputs detected_joints, form_score
   ↓
3. Three systems analyze in parallel:
   a) Injury Risk: Check angles vs JointSafetyProfile
   b) Difficulty: Check score trend, generate recommendation
   c) Classification: Prepare data for next session
   ↓
4. Results aggregated
   ↓
5. Notifications sent if needed (critical injuries)
   ↓
6. Data stored for next analysis
   ↓
7. Session ends
   ↓
8. User views dashboard with alerts, trends, recommendations

WORKFLOW INTEGRATION:

Session Completion:
└─ Run InjuryRiskDetectionSystem.analyze_pose()
   ├─ Check each joint angle
   ├─ Create alerts if needed
   └─ Notify if critical
   
└─ Run AdaptiveDifficultySystem.analyze_exercise()
   ├─ Collect recent scores
   ├─ Calculate metrics & trend
   ├─ Generate recommendation
   └─ Auto-adapt if enabled

Weekly Review:
└─ Collect all analyses for user
└─ Generate therapy plan recommendations using ExerciseClassificationSystem
└─ Suggest progressions or modifications
└─ Update user's difficulty preferences
└─ Create next week's adaptive plan

Therapy Plan Generation:
└─ For each exercise slot in plan:
   ├─ Check if user has recommendation for that exercise
   ├─ If improve trend: suggest higher difficulty variant
   ├─ If decline trend: suggest lower difficulty or form focus
   ├─ Get similar exercises for flexibility
   └─ Insert recommendation

SECURITY & VALIDATION:

1. User Privacy:
   - All analysis scoped to request.user
   - Cannot view other users' alerts/trends
   - Injury alerts only created for user's own sessions

2. Data Validation:
   - PoseAnalysis must have detected_joints JSON
   - Form scores must be 0-100
   - Angles must be positive degrees
   - Safe ranges must have min < max

3. Permission Checks:
   - Only authenticated users can access own data
   - Therapists can view but not modify
   - Admins can create safety profiles and classifications

PERFORMANCE CONSIDERATIONS:

1. Caching:
   - Cache JointSafetyProfile lookups (rarely change)
   - Cache ExerciseClassification similarity calculations
   - Use select_related for foreign keys

2. Batch Processing:
   - Analyze all exercises once per session
   - Generate recommendations once weekly
   - Update difficulty recommendations asynchronously

3. Database Indexes:
   - Index on (user, exercise) for quick lookups
   - Index on detection_at for time-based queries
   - Index on risk_level for filtering

TESTING:

Unit Tests:
- Trend calculation with synthetic score sequences
- Angle comparison with boundary values
- Similarity scoring with test classifications
- Recommendation logic with various metrics

Integration Tests:
- End-to-end session → analysis → recommendation
- Injury risk alert creation and resolution
- Auto-adapt applying new difficulty
- Classification matching accuracy

"""
