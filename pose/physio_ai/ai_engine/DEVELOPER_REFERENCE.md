# AI Scoring Engine - Developer Quick Reference

## 🚀 One-Page Quick Start

### Import & Initialize
```python
from ai_engine.score_generator import ScoreGenerator

generator = ScoreGenerator()
```

### Score an Exercise (3 lines)
```python
result = generator.score_exercise(exercise_id=1, frames=pose_frames, reps_count=5)
feedback = generator.generate_feedback_message(result)
print(f"Score: {feedback['overall_score']}/100")
```

---

## 📋 Available Exercises

| ID | Name | Joints | Key Mistakes |
|:--:|------|--------|-------------|
| 1 | Shoulder Raise | Shoulder, Elbow, Wrist | Shrug, Elbow bend, Wrist deviation |
| 2 | Lateral Raise | Shoulder, Elbow, Wrist | Shrug, Forward lean, ROM |
| 3 | Internal Rotation | Shoulder (rotation) | Arm drift, Insufficient rotation |
| 4 | Bicep Curl | Elbow, Shoulder | Shrug, Swinging, Incomplete ROM |
| 5 | Tricep Extension | Elbow, Shoulder | Arm movement, Incomplete extension |
| 6 | Squat | Hip, Knee, Ankle, Spine | Knee valgus, Forward lean, Heel lift |
| 7 | Straight Leg Raise | Hip, Knee, Ankle | Knee bend, Hip rotation, Incomplete |
| 8 | Torso Rotation | Spine, Shoulder, Elbow | Arm drop, Hip rotation, Asymmetric |
| 9 | Plank | Elbow, Shoulder, Hip, Spine | Hip sag, Shoulder shrug, Head drop |
| 10 | Push Up | Elbow, Shoulder, Hip, Spine | Elbow flare, Incomplete ROM, Hip sag |

---

## 📊 Score Breakdown

```
Overall Score = (Form × 50%) + (Consistency × 30%) + (ROM × 20%)

Score Ranges:
90-100  → Excellent     ⭐⭐⭐
80-90   → Great         ⭐⭐
70-80   → Good          ⭐
50-70   → Fair
0-50    → Poor
```

---

## 🔍 Input Format

```python
frames = [{
    "frame_number": 0,
    "timestamp_seconds": 0.0,
    "detected_joint_angles": {
        "joint_name": angle_in_degrees,  # e.g., "shoulder_flexion": 45.2
        # ... more joints
    },
    "pose_detection_confidence": 0.0  # 0-100
}, ...]  # List of frames
```

---

## 📤 Output Format

```python
{
    "overall_score": 85.3,
    "form_score": 85.5,
    "consistency_score": 82.0,
    "rom_score": 92.0,
    "safety_score": 95.0,
    "summary": "Excellent execution! Score: 85.3/100 ⭐⭐⭐",
    "feedback": ["Excellent form!", "Very stable movements."],
    "recommendations": ["Maintain consistency", "Keep practicing!"],
    "warnings": [],
    "metrics": {
        "total_frames": 150,
        "reps_completed": 5,
        "rom_achieved": 89.2,
        "average_velocity": 45.2,
        "movement_smoothness": 78.5
    }
}
```

---

## 🎯 All Functions

### Main Interface (score_generator.py)

```python
# Initialize
generator = ScoreGenerator()

# Score single exercise
result = generator.score_exercise(
    exercise_id=int,         # 1-10
    frames=list,             # Pose frames
    reps_count=int           # Optional
)

# Generate feedback
feedback = generator.generate_feedback_message(result)

# Score multiple reps
multi_result = generator.score_multiple_reps(
    exercise_id=int,         # 1-10
    rep_frames=list[list]    # List of frame lists
)

# Generate session report
report = ScoringSummary.generate_session_report(results)

# Convenience function
result = generate_exercise_score(exercise_id, frames, reps=0)
```

### Angle Calculator (joint_angle_calculator.py)

```python
calculator = JointAngleCalculator()

# Calculate angle between 3 points
angle = calculator.calculate_angle_between_points(
    point_a={"x": 0, "y": 0},
    point_b={"x": 100, "y": 100},    # Vertex
    point_c={"x": 100, "y": 0}
)

# Calculate using landmarks
angle = calculator.calculate_angle_from_landmarks(
    landmarks=dict,          # Joint name -> {x, y}
    joint_a=str,
    joint_b=str,             # Vertex
    joint_c=str
)

# Movement metrics
displacement = calculator.calculate_joint_displacement(
    current_position={"x": 0, "y": 0},
    previous_position={"x": 0, "y": 0}
)

velocity = calculator.calculate_velocity(displacement, time_delta)
acceleration = calculator.calculate_acceleration(vel_current, vel_prev, time_delta)
angular_velocity = calculator.calculate_angle_velocity(angle_curr, angle_prev, time_delta)

# Stability check
is_stable, std_dev = calculator.is_angle_stable(angles_list, threshold=5.0)

# Range of motion
rom_pct = calculator.calculate_range_of_motion(angles, min_ideal, max_ideal)
```

### Exercise Database (ideal_angles_library.py)

```python
lookup = ExerciseAngleLookup()

# Get exercise
exercise = lookup.get_exercise_profile(exercise_id=1)
exercise = lookup.get_exercise_by_name("Shoulder Raise")

# Get joint range
range = lookup.get_joint_range(exercise_id=1, joint_name="shoulder_flexion")

# Check if valid
is_valid = range.is_within_range(angle)
is_within_tolerance = range.is_within_tolerance(angle)

# Get error
error = range.get_error(angle)

# Get all
all_exercises = lookup.get_all_exercises()
```

### Mistake Detection (mistake_detector.py)

```python
detector = MistakeDetector()

# Detect specific mistakes
mistake = detector.detect_excessive_shoulder_elevation(shoulder_angle, dist, normal_dist)
mistake = detector.detect_elbow_flare(shoulder_angle, elbow_angle, expected)
mistake = detector.detect_incomplete_range_of_motion(achieved_rom, expected_rom)
mistake = detector.detect_asymmetric_movement(left_angle, right_angle)
mistake = detector.detect_compensatory_movement(primary, compensatory, range, stable=True)
mistake = detector.detect_excessive_forward_lean(torso_angle, expected, tolerance)
mistake = detector.detect_knee_valgus(knee_angle, ankle_pos, hip_pos)
mistake = detector.detect_heel_lift(ankle_dorsiflexion, expected_range)
mistake = detector.detect_insufficient_joint_stability(angles, threshold=5.0)
mistake = detector.detect_wrist_deviation(wrist_angle, expected=0, tolerance=15)
mistake = detector.detect_hip_sag_in_plank(hip_angle, torso_angle)

# Analyze mistakes
report = MistakeSeverityAnalyzer.generate_mistake_report(mistakes)
score_reduction, severity = MistakeSeverityAnalyzer.calculate_form_impact(mistakes)
```

### Core Scoring (core_scoring.py)

```python
engine = CoreScoringEngine()

# Calculate components
form = engine.calculate_form_score(angle_errors, ideal_ranges)
consistency = engine.calculate_consistency_score(angles_history, threshold=5.0)
rom = engine.calculate_rom_score(achieved_rom, expected_rom)
safety = engine.calculate_safety_score(mistakes, critical=0, severe=0, moderate=0)

# Overall score
overall = engine.calculate_overall_score(
    form_score,
    consistency_score,
    rom_score,
    form_weight=0.50,
    consistency_weight=0.30,
    rom_weight=0.20
)

# Score exercise
result = engine.score_exercise(metrics, ideal_ranges, mistake_data)

# Classify rep
quality, reason = RepAnalyzer.classify_rep_quality(form, rom_a, rom_e, has_comp)

# Aggregate session
summary = SessionScoringAggregator.aggregate_session_scores(results)
```

---

## 🚨 Mistake Severity Levels

| Level | Points Loss | Examples |
|-------|------------|----------|
| MILD | 2 pts | Minor wrist deviation |
| MODERATE | 8 pts | Incomplete ROM, Asymmetry |
| SEVERE | 15 pts | Elbow flare, Compensation |
| CRITICAL | 30 pts | Knee valgus, Hip sag |

---

## 💡 Common Patterns

### Score Single Exercise
```python
result = generator.score_exercise(1, frames)
print(result.scores.overall_score)
```

### Score Multiple Reps
```python
results = []
for rep_frames in all_reps:
    r = generator.score_exercise(1, rep_frames, reps=1)
    results.append(r)
avg_score = sum(r.scores.overall_score for r in results) / len(results)
```

### Generate Full Report
```python
result = generator.score_exercise(ex_id, frames, reps)
feedback = generator.generate_feedback_message(result)

print(f"Score: {feedback['overall_score']}")
print(f"Form: {feedback['form_score']}")
print(f"Consistency: {feedback['consistency_score']}")
print(f"ROM: {feedback['rom_score']}")
print(f"\n{feedback['summary']}")
print("\nFeedback:")
for f in feedback['feedback']:
    print(f"  • {f}")
print("\nRecommendations:")
for r in feedback['recommendations']:
    print(f"  • {r}")
if feedback['warnings']:
    print("\n⚠️ WARNINGS:")
    for w in feedback['warnings']:
        print(f"  • {w}")
```

### Check Exercise Profile
```python
ex = ExerciseAngleLookup.get_exercise_profile(1)
print(f"Exercise: {ex.exercise_name}")
print(f"Joints: {ex.get_all_joint_names()}")
print(f"Common mistakes: {ex.common_mistakes}")
print(f"Phases: {ex.movement_phases}")
```

---

## 🔧 Customization

### Change Scoring Weights
```python
engine = CoreScoringEngine()
engine.FORM_WEIGHT = 0.60
engine.CONSISTENCY_WEIGHT = 0.25
engine.ROM_WEIGHT = 0.15
```

### Add Custom Exercise
```python
from ai_engine.ideal_angles_library import ExerciseAngleProfile, JointAngleRange

ex = ExerciseAngleProfile(
    exercise_id=99,
    exercise_name="Custom",
    description="...",
    joint_angles={
        "shoulder": JointAngleRange(0, 180, 90, tolerance=5),
        "elbow": JointAngleRange(170, 180, 180, tolerance=10),
    },
    common_mistakes=["Shrug", "Incomplete"],
    movement_phases=["raise", "hold", "lower"]
)

ExerciseAngleLookup.EXERCISES[99] = ex
```

---

## 📊 Performance

- Angle calculation: ~0.1ms
- Frame processing: ~5-10ms
- Full scoring: ~50-100ms
- Memory: ~1-5MB per session

---

## ❌ Error Handling

```python
try:
    result = generator.score_exercise(999, frames)  # Bad exercise ID
    if result is None:
        print("Exercise not found")
except ValueError as e:
    print(f"Invalid data: {e}")
except Exception as e:
    print(f"Error: {e}")
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| README.md | Quick start (2 min read) |
| SCORING_SYSTEM_GUIDE.md | Complete guide (20 min read) |
| IMPLEMENTATION_SUMMARY.md | What was built (5 min read) |
| This file | Developer reference |

---

## 🎓 Example: Complete Workflow

```python
from ai_engine.score_generator import ScoreGenerator, ScoringSummary

# 1. Initialize
generator = ScoreGenerator()

# 2. Get pose frames from video/camera
frames = get_pose_frames()  # Your function

# 3. Score exercise
result = generator.score_exercise(1, frames, reps=5)

# 4. Generate feedback
feedback = generator.generate_feedback_message(result)

# 5. Display results
print(f"Score: {feedback['overall_score']}/100")
print(f"Summary: {feedback['summary']}")
print("\nDetailed Scores:")
print(f"  Form: {feedback['form_score']}")
print(f"  Consistency: {feedback['consistency_score']}")
print(f"  ROM: {feedback['rom_score']}")
print("\nFeedback: {feedback['feedback'][0]}")
print("Recommendations:")
for rec in feedback['recommendations']:
    print(f"  • {rec}")
```

---

## 🔗 Integration with Django

```python
# In api/views.py
from ai_engine.score_generator import ScoreGenerator

@api_view(['POST'])
def score_exercise_view(request):
    exercise_id = request.data['exercise_id']
    frames = request.data['frames']
    reps = request.data.get('reps', 0)
    
    generator = ScoreGenerator()
    result = generator.score_exercise(exercise_id, frames, reps)
    
    if result:
        feedback = generator.generate_feedback_message(result)
        return Response(feedback)
    
    return Response({"error": "Invalid exercise ID"}, status=400)
```

---

## 🎯 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| AttributeError: 'NoneType' | Exercise ID not found (use 1-10) |
| Empty feedback | Result is None, check frames format |
| All scores 0 | Angle values not in detected_joint_angles |
| Import error | Ensure all files in ai_engine/ folder |
| Low scores | Check pose detector confidence |

---

## 🌟 Pro Tips

1. **Validate frames**: Check frame count > 10
2. **Check confidence**: Pose detection should be > 80%
3. **Use multiple reps**: More data = better analysis
4. **Cache lookups**: Get exercise profile once, reuse
5. **Batch scoring**: Score multiple exercises efficiently
6. **Monitor ROM**: Low ROM often = incomplete movement
7. **Check mistakes**: Inspect mistake list for actionable feedback
8. **Session reports**: Aggregate after all exercises scored

---

## 📞 Support Resources

- **Quick issues?** → Check this reference card
- **How to use?** → Read README.md
- **Deep dive?** → Read SCORING_SYSTEM_GUIDE.md
- **What's built?** → Read IMPLEMENTATION_SUMMARY.md
- **Code examples?** → Module docstrings have examples

---

**Last Updated**: April 20, 2026  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
