"""
Advanced Features Usage Examples & Integration Guide

This file demonstrates real-world usage patterns for the three advanced features.
"""

import logging
from django.contrib.auth.models import User
from exercises.models import Exercise
from sessions.models import SessionExercise, Session
from ai_engine.models import PoseAnalysis
from advanced_features.models import (
    DifficultyAdaptation,
    InjuryRiskAlert,
    JointSafetyProfile,
    ExerciseClassification,
    UserDifficultyPreference,
)
from advanced_features.services import (
    AdaptiveDifficultySystem,
    InjuryRiskDetectionSystem,
    ExerciseClassificationSystem,
    analyze_user_progress,
)


logger = logging.getLogger(__name__)


# ============================================================
# EXAMPLE 1: SETUP - Initialize Exercises & Classifications
# ============================================================

def setup_exercises_with_classifications():
    """
    Setup exercise database with classifications and safety profiles.
    Run once during initial setup.
    """
    
    # Create base exercises
    squat = Exercise.objects.create(
        name='Bodyweight Squat',
        description='Basic squat using body weight',
        difficulty_level='medium',
        muscle_groups='quadriceps,glutes,hamstrings',
        duration_seconds=45,
    )
    
    goblet_squat = Exercise.objects.create(
        name='Goblet Squat',
        description='Squat holding a weight at chest',
        difficulty_level='medium',
        muscle_groups='quadriceps,glutes,hamstrings,core',
        duration_seconds=45,
    )
    
    leg_press = Exercise.objects.create(
        name='Leg Press',
        description='Machine-based leg pressing',
        difficulty_level='easy',
        muscle_groups='quadriceps,glutes',
        duration_seconds=60,
    )
    
    # Add classifications for Bodyweight Squat
    ExerciseClassification.objects.create(
        exercise=squat,
        classification_type='movement_pattern',
        classification_value='bilateral',
        weight=1.0,
        description='Two-legged movement'
    )
    
    ExerciseClassification.objects.create(
        exercise=squat,
        classification_type='equipment',
        classification_value='bodyweight',
        weight=1.0,
    )
    
    ExerciseClassification.objects.create(
        exercise=squat,
        classification_type='intensity',
        classification_value='dynamic',
        weight=0.8,
    )
    
    ExerciseClassification.objects.create(
        exercise=squat,
        classification_type='plane_of_motion',
        classification_value='sagittal',
        weight=1.0,
    )
    
    ExerciseClassification.objects.create(
        exercise=squat,
        classification_type='primary_joint',
        classification_value='knee',
        weight=1.0,
    )
    
    ExerciseClassification.objects.create(
        exercise=squat,
        classification_type='primary_joint',
        classification_value='hip',
        weight=1.0,
    )
    
    ExerciseClassification.objects.create(
        exercise=squat,
        classification_type='stabilization',
        classification_value='yes',
        weight=0.6,
    )
    
    ExerciseClassification.objects.create(
        exercise=squat,
        classification_type='complexity_level',
        classification_value='intermediate',
        weight=0.7,
    )
    
    ExerciseClassification.objects.create(
        exercise=squat,
        classification_type='recovery_focus',
        classification_value='strength',
        weight=1.0,
    )
    
    # Add similar classifications for Goblet Squat (easier progression)
    for classification in ExerciseClassification.objects.filter(exercise=squat):
        ExerciseClassification.objects.create(
            exercise=goblet_squat,
            classification_type=classification.classification_type,
            classification_value=classification.classification_value,
            weight=classification.weight,
        )
    
    # Add Leg Press classifications (different approach, similar outcome)
    ExerciseClassification.objects.create(
        exercise=leg_press,
        classification_type='movement_pattern',
        classification_value='bilateral',
        weight=1.0,
    )
    
    ExerciseClassification.objects.create(
        exercise=leg_press,
        classification_type='equipment',
        classification_value='machine',
        weight=1.0,
    )
    
    ExerciseClassification.objects.create(
        exercise=leg_press,
        classification_type='primary_joint',
        classification_value='knee',
        weight=1.0,
    )
    
    ExerciseClassification.objects.create(
        exercise=leg_press,
        classification_type='recovery_focus',
        classification_value='strength',
        weight=1.0,
    )
    
    ExerciseClassification.objects.create(
        exercise=leg_press,
        classification_type='stabilization',
        classification_value='no',
        weight=0.3,
    )
    
    print("✓ Exercises and classifications created")


def setup_joint_safety_profiles():
    """
    Setup safe angle ranges for joint positions.
    Based on biomechanical standards and clinical guidelines.
    """
    
    # Knee flexion/extension (squatting movement)
    JointSafetyProfile.objects.create(
        joint_name='left_knee',
        movement_axis='flexion_extension',
        exercise_type='squatting',
        normal_min_angle=0.0,
        normal_max_angle=120.0,
        conservative_min_angle=0.0,
        conservative_max_angle=90.0,
        warning_threshold=5.0,
        critical_threshold=15.0,
        source='ISO_biomechanics_standard'
    )
    
    JointSafetyProfile.objects.create(
        joint_name='right_knee',
        movement_axis='flexion_extension',
        exercise_type='squatting',
        normal_min_angle=0.0,
        normal_max_angle=120.0,
        conservative_min_angle=0.0,
        conservative_max_angle=90.0,
        warning_threshold=5.0,
        critical_threshold=15.0,
        source='ISO_biomechanics_standard'
    )
    
    # Shoulder external rotation (pressing movements)
    JointSafetyProfile.objects.create(
        joint_name='left_shoulder',
        movement_axis='rotation',
        exercise_type='pressing',
        normal_min_angle=0.0,
        normal_max_angle=90.0,
        conservative_min_angle=0.0,
        conservative_max_angle=60.0,
        warning_threshold=10.0,
        critical_threshold=20.0,
        source='APTA_clinical_guidelines'
    )
    
    JointSafetyProfile.objects.create(
        joint_name='right_shoulder',
        movement_axis='rotation',
        exercise_type='pressing',
        normal_min_angle=0.0,
        normal_max_angle=90.0,
        conservative_min_angle=0.0,
        conservative_max_angle=60.0,
        warning_threshold=10.0,
        critical_threshold=20.0,
        source='APTA_clinical_guidelines'
    )
    
    # Lumbar spine flexion
    JointSafetyProfile.objects.create(
        joint_name='lumbar_spine',
        movement_axis='flexion_extension',
        exercise_type='bending',
        normal_min_angle=0.0,
        normal_max_angle=60.0,
        conservative_min_angle=0.0,
        conservative_max_angle=30.0,
        warning_threshold=5.0,
        critical_threshold=15.0,
        source='Spine_research_institute'
    )
    
    print("✓ Joint safety profiles created")


# ============================================================
# EXAMPLE 2: ADAPTIVE DIFFICULTY - Analyzing Performance
# ============================================================

def example_adaptive_difficulty_analysis():
    """
    Example: Analyze a user's performance on an exercise
    and get adaptive difficulty recommendations.
    """
    
    # Get user and exercise
    user = User.objects.get(username='john_doe')
    exercise = Exercise.objects.get(name='Bodyweight Squat')
    
    # Initialize adaptive difficulty system
    difficulty_system = AdaptiveDifficultySystem(user)
    
    # Analyze exercise
    analysis = difficulty_system.analyze_exercise(exercise)
    
    # Example output
    print("\n=== ADAPTIVE DIFFICULTY ANALYSIS ===")
    print(f"Exercise: {analysis.get('exercise_name')}")
    print(f"Current Difficulty: {analysis.get('current_difficulty')}")
    print(f"\nPerformance Metrics:")
    print(f"  Average Score: {analysis['metrics']['average_score']:.1f}%")
    print(f"  Consistency: {analysis['metrics']['consistency_score']:.1f}%")
    print(f"  Sessions Completed: {analysis['metrics']['sessions_count']}")
    print(f"\nTrend Analysis:")
    print(f"  Trend: {analysis['trend']['trend']}")
    print(f"  Slope: {analysis['trend']['slope']:.2f} points/session")
    print(f"  Confidence: {analysis['trend']['confidence']:.1f}%")
    print(f"\nRecommendation:")
    print(f"  Type: {analysis['recommendation']['type'].upper()}")
    print(f"  Suggested Difficulty: {analysis['recommendation']['difficulty']}")
    print(f"  Reason: {analysis['recommendation']['reason']}")
    
    return analysis


def example_auto_adapt_exercise():
    """
    Example: Automatically adapt exercise difficulty based on recommendation.
    """
    
    user = User.objects.get(username='john_doe')
    exercise = Exercise.objects.get(name='Bodyweight Squat')
    
    difficulty_system = AdaptiveDifficultySystem(user)
    
    # Check if user has auto-adapt enabled
    if difficulty_system.preference.auto_adapt_enabled:
        # Auto-adapt will be applied
        new_difficulty = difficulty_system.auto_adapt_if_needed(exercise)
        
        if new_difficulty:
            print(f"✓ Exercise auto-adapted to: {new_difficulty}")
        else:
            print("✓ No adaptation needed at this time")
    else:
        print("✓ Auto-adapt is disabled for this user")


def example_apply_recommendation_manually():
    """
    Example: Manually apply a difficulty recommendation via API.
    """
    
    user = User.objects.get(username='john_doe')
    exercise = Exercise.objects.get(name='Bodyweight Squat')
    
    # Get the adaptation
    adaptation = DifficultyAdaptation.objects.get(user=user, exercise=exercise)
    
    # Check if recommendation is to increase
    if adaptation.recommendation == 'increase':
        # Apply the recommendation
        old_difficulty = exercise.difficulty_level
        exercise.difficulty_level = adaptation.recommended_difficulty
        exercise.save()
        
        adaptation.adaptation_count += 1
        adaptation.save()
        
        print(f"✓ Difficulty changed from {old_difficulty} to {adaptation.recommended_difficulty}")
        print(f"  Reason: {adaptation.recommendation_reason}")
    else:
        print(f"✓ Current recommendation is '{adaptation.recommendation}'")


def example_get_exercises_ready_for_progression():
    """
    Example: Find all exercises user is ready to progress in.
    """
    
    user = User.objects.get(username='john_doe')
    
    # Find exercises with 'increase' recommendation
    ready_exercises = DifficultyAdaptation.objects.filter(
        user=user,
        recommendation='increase',
        average_score__gte=85.0
    )
    
    print("\n=== EXERCISES READY FOR PROGRESSION ===")
    for adaptation in ready_exercises:
        print(f"• {adaptation.exercise.name}")
        print(f"  Current Score: {adaptation.average_score:.1f}%")
        print(f"  Current Difficulty: {adaptation.exercise.difficulty_level}")
        print(f"  Recommended: {adaptation.recommended_difficulty}")
        print()


# ============================================================
# EXAMPLE 3: INJURY RISK DETECTION - Monitoring Safety
# ============================================================

def example_detect_injury_risks():
    """
    Example: Analyze a pose for injury risks.
    """
    
    user = User.objects.get(username='john_doe')
    
    # Get latest pose analysis and session
    pose_analysis = PoseAnalysis.objects.latest('id')
    session_exercise = SessionExercise.objects.latest('id')
    
    # Initialize risk detection system
    risk_system = InjuryRiskDetectionSystem(user)
    
    # Analyze pose for risks
    alerts = risk_system.analyze_pose(pose_analysis, session_exercise)
    
    print("\n=== INJURY RISK DETECTION ===")
    if alerts:
        for alert in alerts:
            print(f"⚠ {alert['alert_type'].upper()}")
            print(f"  Joint: {alert['joint_name']}")
            print(f"  Current Angle: {alert['current_angle']:.1f}°")
            print(f"  Safe Range: {alert['safe_min']:.1f}° - {alert['safe_max']:.1f}°")
            print(f"  Exceeded By: {alert['exceeded_by']:.1f}°")
            print(f"  Risk Level: {alert['risk_level'].upper()}")
            
            # Create alert in database
            risk_system.create_risk_alert(alert, pose_analysis, session_exercise)
            print(f"  ✓ Alert recorded in database")
    else:
        print("✓ No injury risks detected - form is good!")


def example_get_active_injury_alerts():
    """
    Example: Get all unresolved injury alerts for a user.
    """
    
    user = User.objects.get(username='john_doe')
    
    # Get active alerts
    active_alerts = InjuryRiskAlert.objects.filter(
        user=user,
        is_resolved=False
    ).order_by('-severity_score')
    
    print("\n=== ACTIVE INJURY ALERTS ===")
    print(f"Total Active Alerts: {active_alerts.count()}\n")
    
    # Group by risk level
    critical = active_alerts.filter(risk_level='critical')
    high = active_alerts.filter(risk_level='high')
    
    if critical:
        print(f"🔴 CRITICAL ({critical.count()}):")
        for alert in critical:
            print(f"  • {alert.joint_name}: exceeded by {alert.angle_exceeded_by:.1f}°")
    
    if high:
        print(f"🟠 HIGH ({high.count()}):")
        for alert in high:
            print(f"  • {alert.joint_name}: exceeded by {alert.angle_exceeded_by:.1f}°")


def example_resolve_injury_alert():
    """
    Example: Resolve an injury alert after correction.
    """
    
    user = User.objects.get(username='john_doe')
    
    # Get latest alert
    alert = InjuryRiskAlert.objects.filter(
        user=user,
        is_resolved=False
    ).latest('detected_at')
    
    # Mark as acknowledged
    alert.is_acknowledged = True
    alert.save()
    print("✓ Alert acknowledged")
    
    # Later, mark as resolved
    alert.is_resolved = True
    alert.resolution_notes = "User corrected form and repeated exercise successfully"
    alert.save()
    print("✓ Alert resolved")


# ============================================================
# EXAMPLE 4: EXERCISE CLASSIFICATION - Intelligent Matching
# ============================================================

def example_get_exercise_classifications():
    """
    Example: Get all classifications for an exercise.
    """
    
    exercise = Exercise.objects.get(name='Bodyweight Squat')
    
    classifications = ExerciseClassificationSystem.get_exercise_classifications(exercise)
    
    print("\n=== EXERCISE CLASSIFICATIONS ===")
    print(f"Exercise: {exercise.name}\n")
    for classification_type, values in classifications.items():
        print(f"{classification_type}:")
        for value in values:
            print(f"  • {value}")


def example_find_similar_exercises():
    """
    Example: Find similar exercises for substitution/progression.
    """
    
    exercise = Exercise.objects.get(name='Bodyweight Squat')
    
    # Find similar exercises with 70%+ similarity
    similar = ExerciseClassificationSystem.find_similar_exercises(
        exercise,
        similarity_threshold=0.7,
        max_results=5
    )
    
    print("\n=== SIMILAR EXERCISES ===")
    print(f"Base Exercise: {exercise.name}\n")
    print("Recommended Alternatives:")
    for similar_exercise, similarity_score in similar:
        print(f"  • {similar_exercise.name}")
        print(f"    Similarity: {similarity_score*100:.1f}%")
        print(f"    Difficulty: {similar_exercise.difficulty_level}")


def example_recommend_exercises_for_goal():
    """
    Example: Get exercise recommendations for a therapeutic goal.
    """
    
    # Recommend strength exercises at medium difficulty
    recommendations = ExerciseClassificationSystem.recommend_exercise_for_goal(
        goal='strength',
        difficulty='medium',
        max_results=5
    )
    
    print("\n=== EXERCISE RECOMMENDATIONS ===")
    print("Goal: Strength Training (Medium Difficulty)\n")
    for exercise in recommendations:
        print(f"• {exercise.name}")
        print(f"  Duration: {exercise.duration_seconds}s")
        print(f"  Muscle Groups: {exercise.muscle_groups}")


def example_get_exercise_profile():
    """
    Example: Get comprehensive exercise profile with recommendations.
    """
    
    exercise = Exercise.objects.get(name='Bodyweight Squat')
    
    profile = ExerciseClassificationSystem.get_exercise_profile(exercise)
    
    print("\n=== EXERCISE PROFILE ===")
    print(f"Name: {profile['name']}")
    print(f"Difficulty: {profile['difficulty_level']}")
    print(f"Duration: {profile['duration_seconds']}s")
    print(f"\nClassifications:")
    for class_type, values in profile['classifications'].items():
        print(f"  {class_type}: {', '.join(values)}")
    print(f"\nSimilar Exercises:")
    for similar in profile['similar_exercises']:
        print(f"  • {similar['name']} ({similar['similarity']*100:.0f}%)")


# ============================================================
# EXAMPLE 5: COMPREHENSIVE USER PROGRESS ANALYSIS
# ============================================================

def example_comprehensive_user_analysis():
    """
    Example: Get comprehensive progress analysis across all features.
    """
    
    user = User.objects.get(username='john_doe')
    
    # Get comprehensive analysis
    analysis = analyze_user_progress(user)
    
    print("\n=== COMPREHENSIVE USER PROGRESS ===")
    print(f"User: {analysis['username']}\n")
    
    print("Difficulty Adaptations:")
    for exercise_analysis in analysis['difficulty_analysis']:
        if 'error' not in exercise_analysis:
            print(f"  • {exercise_analysis['exercise_name']}")
            print(f"    Score: {exercise_analysis['metrics']['average_score']:.1f}%")
            print(f"    Recommendation: {exercise_analysis['recommendation']['type']}")
    
    print(f"\nInjury Risk Summary:")
    print(f"  Active Alerts: {analysis['risk_summary']['active_alerts']}")
    print(f"  Critical Count: {analysis['risk_summary']['critical_count']}")


# ============================================================
# EXAMPLE 6: INTEGRATION - Complete Session Workflow
# ============================================================

def example_complete_session_workflow():
    """
    Example: Complete workflow after a user completes an exercise session.
    This shows how all three systems work together.
    """
    
    user = User.objects.get(username='john_doe')
    exercise = Exercise.objects.get(name='Bodyweight Squat')
    
    print("\n=== COMPLETE SESSION WORKFLOW ===\n")
    
    # 1. User completes exercise, pose analysis is created
    print("1. User completed exercise session")
    print("   Pose analysis complete with form_score and joint angles\n")
    
    # 2. Check for injury risks
    print("2. Checking for injury risks...")
    risk_system = InjuryRiskDetectionSystem(user)
    pose_analysis = PoseAnalysis.objects.filter(
        session_exercise__exercise=exercise,
        session_exercise__session__user=user
    ).latest('id')
    session_exercise = pose_analysis.session_exercise
    
    alerts = risk_system.analyze_pose(pose_analysis, session_exercise)
    if alerts:
        for alert in alerts:
            risk_system.create_risk_alert(alert, pose_analysis, session_exercise)
        print(f"   ⚠ {len(alerts)} safety alerts generated\n")
    else:
        print("   ✓ No safety issues detected\n")
    
    # 3. Analyze adaptive difficulty
    print("3. Analyzing performance and difficulty...")
    difficulty_system = AdaptiveDifficultySystem(user)
    analysis = difficulty_system.analyze_exercise(exercise)
    print(f"   Trend: {analysis['trend']['trend']}")
    print(f"   Recommendation: {analysis['recommendation']['type']}\n")
    
    # 4. Check for progression
    if analysis['recommendation']['type'] == 'increase':
        print("4. User is ready for progression!")
        similar = ExerciseClassificationSystem.find_similar_exercises(
            exercise,
            similarity_threshold=0.7,
            max_results=3
        )
        print(f"   Suggested progressions:")
        for similar_exercise, score in similar[:3]:
            print(f"     • {similar_exercise.name} ({score*100:.0f}% match)")
    else:
        print("4. Progression not recommended at this time\n")
    
    print("5. ✓ Session analysis complete")


# ============================================================
# RUN EXAMPLES
# ============================================================

if __name__ == '__main__':
    """
    To run these examples in Django shell:
    
    python manage.py shell
    exec(open('advanced_features/examples.py').read())
    
    Then run individual functions:
    setup_exercises_with_classifications()
    example_adaptive_difficulty_analysis()
    example_detect_injury_risks()
    etc.
    """
    
    print("""
    Advanced Features Examples
    ==========================
    
    Available functions to run:
    
    Setup Functions:
      - setup_exercises_with_classifications()
      - setup_joint_safety_profiles()
    
    Adaptive Difficulty Examples:
      - example_adaptive_difficulty_analysis()
      - example_auto_adapt_exercise()
      - example_get_exercises_ready_for_progression()
    
    Injury Risk Examples:
      - example_detect_injury_risks()
      - example_get_active_injury_alerts()
      - example_resolve_injury_alert()
    
    Classification Examples:
      - example_get_exercise_classifications()
      - example_find_similar_exercises()
      - example_recommend_exercises_for_goal()
      - example_get_exercise_profile()
    
    Comprehensive Examples:
      - example_comprehensive_user_analysis()
      - example_complete_session_workflow()
    """)
