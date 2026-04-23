# AI Scoring Engine - Architecture & Data Flow

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PHYSIO AI - SCORING ENGINE                           │
│                                                                               │
│  Input: Pose Landmarks from Video  → Output: Score (0-100) + Feedback      │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ┌──────────────────┐
                                    │  Raw Pose Data   │
                                    │  (landmarks x,y) │
                                    └────────┬─────────┘
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      │                                             │
                      ▼                                             ▼
        ┌──────────────────────────────┐         ┌──────────────────────────┐
        │ JOINT ANGLE CALCULATOR       │         │ IDEAL ANGLES LIBRARY     │
        │                              │         │                          │
        │ • Calculate angles           │         │ • Exercise definitions   │
        │ • Velocity/acceleration      │         │ • 10 exercises           │
        │ • Stability detection        │         │ • Joint angle ranges     │
        │ • ROM calculation            │         │ • Common mistakes        │
        │                              │         │                          │
        │ Output: Angle values         │         │ Output: Ideal ranges     │
        │         Velocities           │         │         Mistakes list    │
        │         Stability scores     │         │                          │
        └────────┬─────────────────────┘         └────────┬────────────────┘
                 │                                        │
                 │                                        │
                 │         ┌────────────────────────────┐ │
                 └────────►│  EXERCISE METRICS          │◄┘
                           │  (intermediate storage)    │
                           │                            │
                           │ • Angle history            │
                           │ • Velocity history         │
                           │ • ROM achieved             │
                           │ • Movement phase           │
                           │                            │
                           └────────────┬───────────────┘
                                        │
                      ┌─────────────────┴──────────────────┐
                      │                                    │
                      ▼                                    ▼
        ┌──────────────────────────────┐   ┌──────────────────────────────┐
        │  MISTAKE DETECTOR            │   │  CORE SCORING ENGINE         │
        │                              │   │                              │
        │ • Angle errors detection     │   │ • Form score (0-100)         │
        │ • 15+ mistake types          │   │ • Consistency score (0-100)  │
        │ • Severity classification    │   │ • ROM score (0-100)          │
        │ • Recommendations            │   │ • Safety score (penalty)     │
        │                              │   │ • Overall score calculation  │
        │ Output: Mistakes detected    │   │                              │
        │         Severity levels      │   │ Output: Score components     │
        │         Recommendations      │   │         Combined score       │
        └────────┬─────────────────────┘   └────────┬────────────────────┘
                 │                                   │
                 │                                   │
                 └──────────────────────┬────────────┘
                                        │
                                        ▼
                        ┌────────────────────────────┐
                        │  SCORING RESULT            │
                        │  (ScoringResult)           │
                        │                            │
                        │ • All score components     │
                        │ • Metrics/statistics       │
                        │ • Mistakes detected        │
                        │ • Feedback & warnings      │
                        │ • Recommendations          │
                        │                            │
                        └────────┬───────────────────┘
                                 │
                                 ▼
                        ┌────────────────────────────┐
                        │  SCORE GENERATOR           │
                        │  (Main Interface)          │
                        │                            │
                        │ • Generate feedback        │
                        │ • Create summary           │
                        │ • Format output            │
                        │ • Session aggregation      │
                        │                            │
                        └────────┬───────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
        ┌──────────────────────┐   ┌──────────────────────┐
        │  User Feedback       │   │  Session Report      │
        │                      │   │                      │
        │ • Overall score      │   │ • Avg scores         │
        │ • Score breakdown    │   │ • Key takeaways      │
        │ • Summary message    │   │ • Next focus areas   │
        │ • Recommendations    │   │ • Exercise summary   │
        │ • Warnings           │   │ • Improvement areas  │
        │ • Metrics            │   │                      │
        └──────────────────────┘   └──────────────────────┘
                    │                         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Final Output (JSON)   │
                    │  → API Response        │
                    │  → Database Storage    │
                    │  → User Display        │
                    └────────────────────────┘
```

---

## 📊 Module Dependencies

```
┌──────────────────────────────────────────────────────────────┐
│                   Score Generator (Main)                     │
│                  (score_generator.py)                        │
└─────────────────────────────────────────────────────────────┘
                      │         │          │
           ┌──────────┴──┬──────┴──┬───────┴──┐
           │             │         │          │
           ▼             ▼         ▼          ▼
    ┌────────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐
    │ Angle      │ │ Ideal   │ │Mistake  │ │  Core    │
    │ Calculator │ │ Angles  │ │Detector │ │Scoring   │
    │            │ │Library  │ │         │ │          │
    └────────────┘ └─────────┘ └─────────┘ └──────────┘


Independent Modules (can be used separately):

┌────────────────────────────────────────────────────────────┐
│            Joint Angle Calculator                          │
│                                                            │
│  Computes angles, velocity, acceleration, ROM, etc.       │
│  Can be used independently for math operations            │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│            Ideal Angles Library                            │
│                                                            │
│  Database of exercises and their angle ranges             │
│  Can be queried independently for reference data          │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│            Mistake Detector                                │
│                                                            │
│  Identifies errors from angle data                        │
│  Can be used independently for form checking              │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│            Core Scoring Engine                             │
│                                                            │
│  Calculates scores from metrics and mistakes              │
│  Can be used independently for scoring logic              │
└────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow - Detailed

```
STEP 1: INPUT VALIDATION
────────────────────────
frames = [
    {frame_number, timestamp, landmarks, confidence},
    ...
]
    │
    ▼
[Valid? Check format, landmarks present, confidence > 0]
    │
    ├─ YES ─► Continue
    │
    └─ NO ──► Return None


STEP 2: CONVERT TO INTERNAL FORMAT
───────────────────────────────────
frames → PoseFrame objects
    │
    ▼
[Extract landmarks, timestamps, confidence]


STEP 3: GET EXERCISE PROFILE
─────────────────────────────
exercise_id
    │
    ▼
ExerciseAngleLookup.get_exercise_profile(id)
    │
    ▼
ExerciseAngleProfile {
    name, description,
    joint_angles {ideal ranges},
    common_mistakes,
    movement_phases
}


STEP 4: EXTRACT METRICS
───────────────────────
For each frame:
    landmarks → JointAngleCalculator
        │
        ├─ Calculate angles (joint A-B-C)
        ├─ Calculate velocities
        ├─ Calculate acceleration
        ├─ Detect stability
        └─ Track ROM
    │
    ▼
ExerciseMetrics {
    angle_history: {joint: [angles]},
    velocities: [values],
    rom_achieved: float,
    movement_smoothness: float
}


STEP 5: DETECT MISTAKES
───────────────────────
For each metric:
    metric → MistakeDetector
        │
        ├─ Check angle errors
        ├─ Check stability
        ├─ Check ROM
        ├─ Check compensations
        ├─ Check symmetry
        └─ Check dangerous forms
    │
    ▼
mistakes = [
    {name, severity, recommendation},
    ...
]


STEP 6: CALCULATE SCORES
────────────────────────
metrics + ideal_ranges + mistakes → CoreScoringEngine
    │
    ├─ form_score = calculate_form_score(angle_errors)
    ├─ consistency_score = calculate_consistency_score(angle_history)
    ├─ rom_score = calculate_rom_score(rom_achieved, rom_expected)
    ├─ safety_score = calculate_safety_score(mistakes)
    │
    ├─ overall_score = weighted combination
    │
    └─ Apply safety penalty if needed
    │
    ▼
ScoreComponents {
    form_score: 85.5,
    consistency_score: 82.0,
    rom_score: 92.0,
    safety_score: 95.0,
    overall_score: 85.3
}


STEP 7: GENERATE FEEDBACK
──────────────────────────
ScoreComponents + ScoringResult → ScoreGenerator
    │
    ├─ Generate summary message
    ├─ Create feedback points
    ├─ Generate recommendations
    ├─ Add warnings if needed
    └─ Format metrics
    │
    ▼
feedback_dict {
    overall_score: 85.3,
    form_score: 85.5,
    consistency_score: 82.0,
    rom_score: 92.0,
    safety_score: 95.0,
    summary: "Excellent execution!",
    feedback: [...],
    recommendations: [...],
    warnings: [...],
    metrics: {...}
}


STEP 8: RETURN OUTPUT
─────────────────────
feedback_dict → JSON → API Response
                   ↓
                API Client
                   ↓
          Display to User / Store in DB
```

---

## 🎯 Module Responsibilities

### 1. Joint Angle Calculator
**Responsibility**: Pure math/geometry
```
INPUT:  2D landmarks {x, y}
OUTPUT: Angles (degrees), velocities, accelerations
WHERE:  No exercise knowledge, no scoring
```

### 2. Ideal Angles Library  
**Responsibility**: Knowledge base
```
INPUT:  Exercise ID
OUTPUT: Ideal angle ranges, common mistakes
WHERE:  Static data, no computation
```

### 3. Mistake Detector
**Responsibility**: Error identification
```
INPUT:  Angle data + Ideal ranges
OUTPUT: Detected mistakes with severity
WHERE:  Form validation, no scoring
```

### 4. Core Scoring Engine
**Responsibility**: Score calculation
```
INPUT:  Metrics + Mistakes + Ideal ranges
OUTPUT: Score components (0-100 each)
WHERE:  Scoring algorithms, weighted calculation
```

### 5. Score Generator
**Responsibility**: Orchestration & user interface
```
INPUT:  Raw pose frames
OUTPUT: Formatted feedback with recommendations
WHERE:  Coordinates all modules, generates user-friendly output
```

---

## 🔀 Cross-Module Communication

```
Joint Angle Calculator
        ↑
        │ provides angles
        │
Mistake Detector ─────────────────┐
        ↑                         │
        │ provides mistakes       │
        │                         │
Core Scoring Engine ◄─────────────┘
        ↑
        │ provides scores
        │
Score Generator ◄─────────────────┐
        │                         │
        └────────► uses all   ────┤
                  modules         │
                                  │
                        ◄─────────┘
                  (coordinates)
```

---

## 📦 Class Hierarchies

```
DataClasses (stored data):
├── Point2D
├── JointAngleRange
├── ExerciseAngleProfile
├── PoseFrame
├── ExerciseSession
├── ExerciseMetrics
├── ScoreComponents
├── MistakeDetection
└── ScoringResult

Engines (business logic):
├── JointAngleCalculator
│   └── JointKinematics
├── ExerciseAngleLookup
├── MistakeDetector
│   └── MistakeSeverityAnalyzer
├── CoreScoringEngine
│   ├── RepAnalyzer
│   └── SessionScoringAggregator
└── ScoreGenerator
    └── ScoringSummary
```

---

## 🔗 Integration Points

```
┌─────────────────────────────────────────────────────────┐
│              EXTERNAL SYSTEMS                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────┐                                 │
│  │  Django ORM       │                                 │
│  │                   │                                 │
│  │ • PoseAnalysis    │                                 │
│  │ • SessionExercise │                                 │
│  │ • User/Progress   │                                 │
│  └──────────┬────────┘                                 │
│             │ stores                                   │
│             │ scores                                   │
│             ▼                                          │
│  ┌───────────────────┐                                 │
│  │  REST API         │                                 │
│  │                   │                                 │
│  │ /score/calculate/ │ ◄─────── ScoreGenerator        │
│  │ /feedback/        │          returns                │
│  │ /progress/        │          JSON                   │
│  └───────────────────┘                                 │
│             │                                          │
│             ▼                                          │
│  ┌───────────────────┐                                 │
│  │  Frontend         │                                 │
│  │                   │                                 │
│  │  React/Vue/etc.   │                                 │
│  │  Display score    │                                 │
│  │  Show feedback    │                                 │
│  └───────────────────┘                                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Data Flow - Sequence Diagram

```
User's Phone          Pose Detector         Django API         AI Engine
     │                    │                     │                  │
     ├─ Video Stream ────►│                     │                  │
     │                    │                     │                  │
     │                    ├─ Landmarks ────────►│                  │
     │                    │                     │                  │
     │                    │                     ├─ Frame List ────►│
     │                    │                     │   (10+ frames)    │
     │                    │                     │                  │
     │                    │                     │  ┌──────────────┐│
     │                    │                     │  │ Score Module ││
     │                    │                     │  │ Processes... ││
     │                    │                     │  └──────────────┘│
     │                    │                     │                  │
     │                    │                     │◄─ ScoringResult ─│
     │                    │                     │   (all scores    │
     │                    │                     │    & feedback)   │
     │                    │                     │                  │
     │                    │                     ├─ Save to DB      │
     │                    │                     │                  │
     │◄─ JSON Response ───────────────────────┤                  │
     │   {score, feedback, recommendations}    │                  │
     │                                          │                  │
     ├─ Display Results ──────────────────────┐                  │
     │                                        │                  │
     │ "Great job! Score 85.3"               │                  │
     │ "Focus on form consistency"            │                  │
     │                                        │                  │
```

---

## 📈 Complexity Analysis

| Module | Time | Space | Notes |
|--------|------|-------|-------|
| JointAngleCalculator | O(1) | O(1) | Per angle calculation |
| ExerciseMetrics | O(n) | O(n) | n = number of frames |
| MistakeDetector | O(n) | O(1) | Linear scan of metrics |
| CoreScoringEngine | O(j) | O(j) | j = number of joints |
| ScoreGenerator | O(n) | O(n) | Orchestrates all |
| **Total** | **O(n)** | **O(n)** | n = frames |

---

## 🔒 Error Handling Flow

```
Input Frames
    │
    ├─ Format Valid?
    │   └─ No → Return None
    │
    ├─ Landmarks Present?
    │   └─ No → Return None
    │
    ├─ Exercise ID Valid?
    │   └─ No → Return None
    │
    ├─ Confidence > 0?
    │   └─ No → Return None
    │
    ├─ Frame Count > 0?
    │   └─ No → Return None
    │
    ▼
Process Safely
    │
    └─ Return ScoringResult
       or catch exception
```

---

## 🎯 Design Patterns Used

1. **Strategy Pattern**: Different scoring algorithms for different components
2. **Template Method**: Exercise scoring workflow
3. **Factory Pattern**: Exercise lookup and creation
4. **Data Class Pattern**: Clean data structures
5. **Composition**: Modules composed together
6. **Single Responsibility**: Each module has one job

---

## 📊 Example Execution Timeline

```
T=0ms   ─ Input frames received
T=5ms   ─ Frames validated  
T=10ms  ─ Exercise profile loaded
T=50ms  ─ Angles calculated for all frames
T=100ms ─ Mistakes detected
T=150ms ─ Scores calculated
T=200ms ─ Feedback generated
T=210ms ─ JSON formatted
T=220ms ─ Response sent

Total: ~220ms for full processing
```

---

**Architecture Version**: 1.0.0  
**Created**: April 20, 2026  
**Status**: ✅ Production Ready
