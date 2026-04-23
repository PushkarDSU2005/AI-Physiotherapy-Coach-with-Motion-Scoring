# Django Models Relationships & Field Reference

**Project**: Physio AI System
**Date**: April 20, 2026

---

## 📊 Complete Model Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE SCHEMA                                 │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ┌──────────┐
                                    │  USER    │
                                    └──────────┘
                                         │
        ┌────────────────────┬──────────┼──────────┬────────────────────┐
        │                    │          │          │                    │
    1:1 │              1:Many│      1:Many│    1:Many│                   │ 1:Many
        │                    │          │          │                    │
        ▼                    ▼          ▼          ▼                    ▼
┌─────────────┐    ┌──────────────┐ ┌───────┐ ┌────────────┐    ┌─────────────┐
│UserProgress │    │   SESSION    │ │MILESTONE│ DailyMetrics   │  Supervised │
│ (1:1)       │    │              │ │        │              │   │  Sessions   │
│ • Total     │    │ • title      │ │• type  │ • sessions_  │   │ (foreign)   │
│   Sessions  │    │ • start_time │ │• desc  │   completed  │   │             │
│ • Avg Score │    │ • end_time   │ │• date  │ • avg_score  │   │             │
│ • Streaks   │    │ • status     │ │        │ • total_mins │   └─────────────┘
│ • Pain      │    │ • pain_before│ │        │              │
│   Improve   │    │ • pain_after │ │        └──────────────┘
└─────────────┘    │ • ai_feedback│
                   │ • score      │
                   │ • completion%│
                   └──────────────┘
                          │
                    Many:Many (through)
                          │
                   ┌──────────────────┐
                   │ SessionExercise  │
                   │                  │
                   │ • order_in_sesh  │
                   │ • status         │
                   │ • form_score     │
                   │ • consistency    │
                   │ • ROM%           │
                   │ • angles         │
                   │ • issues         │
                   │ • feedback       │
                   │ • pain_during    │
                   │ • reps_performed │
                   └──────────────────┘
                          │
                    Many:1 │
                          │
                   ┌──────────────────┐         ┌──────────────┐
                   │   EXERCISE       │◄────────┤ Progression  │
                   │ (Shared Master)  │         │   To/From    │
                   │                  │         └──────────────┘
                   │ • name           │
                   │ • category       │         ┌──────────────┐
                   │ • difficulty     │◄────────┤Prerequisites│
                   │ • target_muscles │         │   (Many:M)   │
                   │ • duration       │         └──────────────┘
                   │ • ideal_angles   │
                   │ • safe_ranges    │
                   │ • instructions   │
                   │ • video_url      │
                   │ • equipment      │
                   └──────────────────┘
                          │
                    1:Many │
                          │
                   ┌──────────────────┐
                   │  PoseAnalysis    │
                   │ (Per Frame)      │
                   │                  │
                   │ • frame_number   │
                   │ • timestamp      │
                   │ • detected_      │
                   │   angles         │
                   │ • angle_errors   │
                   │ • confidence     │
                   │ • issues         │
                   │ • position_desc  │
                   └──────────────────┘
```

---

## 🔄 Complete Field Reference

### USER Model
```
Field Name               | Type           | Required | Unique | Purpose
────────────────────────────────────────────────────────────────────────────────
id                       | Auto           | Auto     | Yes    | Primary key
username                 | CharField(150) | Yes      | Yes    | Login identifier
email                    | EmailField     | Yes      | Yes    | Contact/password reset
password                 | CharField(128) | Yes      | No     | Authentication
first_name              | CharField(150) | No       | No     | Display name
last_name               | CharField(150) | No       | No     | Display name
is_active               | Boolean        | Yes      | No     | Account active?
is_staff                | Boolean        | Yes      | No     | Admin access?
is_superuser            | Boolean        | Yes      | No     | Full admin?
date_joined             | DateTime       | Yes      | No     | Account creation
last_login              | DateTime       | No       | No     | Last login time
─────────────────────────────────────────────────────────────────────────────
date_of_birth           | DateField      | No       | No     | Age calculation
phone_number            | CharField(15)  | No       | No     | Contact number
injury_type             | CharField(100) | No       | No     | Injury being treated
fitness_level           | CharField(20)  | Yes      | No     | Exercise difficulty
medical_notes           | TextField      | No       | No     | Allergies, meds
height_cm               | IntegerField   | No       | No     | AI calibration
weight_kg               | FloatField     | No       | No     | Movement analysis
profile_picture         | ImageField     | No       | No     | Avatar
created_at              | DateTime       | Auto     | No     | Record creation
updated_at              | DateTime       | Auto     | No     | Last modification
last_activity           | DateTime       | Yes      | No     | Last engagement
```

**Field Choices:**
- **injury_type**: ankle_sprain, knee_injury, shoulder_injury, back_pain, rotator_cuff, acl_injury, other
- **fitness_level**: beginner, intermediate, advanced

---

### EXERCISE Model
```
Field Name                  | Type          | Required | Unique | Purpose
─────────────────────────────────────────────────────────────────────────────────
id                          | Auto          | Auto     | Yes    | Primary key
name                        | CharField(200)| Yes      | Yes    | Exercise name
description                 | TextField     | Yes      | No     | What it does
category                    | CharField(50) | Yes      | No     | Type (stretch/strength)
difficulty_level            | CharField(20) | Yes      | No     | Easy/medium/hard
target_muscle_groups        | CharField(500)| Yes      | No     | Muscles targeted
duration_seconds            | IntegerField  | Yes      | No     | Standard time
recommended_reps            | IntegerField  | No       | No     | Target reps
recommended_sets            | IntegerField  | Yes      | No     | Target sets
rest_seconds_between_sets   | IntegerField  | Yes      | No     | Rest time
primary_joints              | CharField(200)| Yes      | No     | Main joints
secondary_joints            | CharField(200)| No       | No     | Helper joints
ideal_joint_angles          | JSONField     | Yes      | No     | Perfect angles
safe_angle_range            | JSONField     | Yes      | No     | Acceptable ranges
step_by_step_instructions   | TextField     | Yes      | No     | How to do it
common_mistakes             | TextField     | No       | No     | What to avoid
safety_notes                | TextField     | No       | No     | Warnings
equipment_required          | CharField(200)| No       | No     | What you need
instruction_video_url       | URLField      | No       | No     | Video link
form_reference_image_url    | URLField      | No       | No     | Photo link
progression_to              | ForeignKey    | No       | No     | Harder exercise
is_active                   | Boolean       | Yes      | No     | Available?
times_completed_globally    | IntegerField  | Yes      | No     | Usage count
average_difficulty_rating   | FloatField    | Yes      | No     | User ratings
created_at                  | DateTime      | Auto     | No     | Created when
updated_at                  | DateTime      | Auto     | No     | Last edit
```

**Field Choices:**
- **category**: stretching, strengthening, mobility, balance, flexibility, cardio, coordination
- **difficulty_level**: easy, medium, hard

**Example ideal_joint_angles (JSON):**
```json
{
    "phase_1_setup": {
        "shoulder": 90,
        "elbow": 90,
        "wrist": 0
    },
    "phase_2_peak": {
        "shoulder": 170,
        "elbow": 180,
        "wrist": 0
    },
    "phase_3_return": {
        "shoulder": 90,
        "elbow": 90,
        "wrist": 0
    }
}
```

---

### SESSION Model
```
Field Name                   | Type           | Required | Unique | Purpose
─────────────────────────────────────────────────────────────────────────────────
id                           | Auto           | Auto     | Yes    | Primary key
user_id                      | ForeignKey     | Yes      | No     | Which user
title                        | CharField(200) | Yes      | No     | Session name
description                  | TextField      | No       | No     | Notes
start_time                   | DateTime       | Yes      | No     | When started
end_time                     | DateTime       | No       | No     | When ended
status                       | CharField(20)  | Yes      | No     | Workflow state
scheduled_duration_minutes   | IntegerField   | Yes      | No     | Planned length
overall_session_score        | FloatField     | No       | No     | Quality (0-100)
average_exercise_score       | FloatField     | No       | No     | Avg exercise score
completion_percentage        | FloatField     | Yes      | No     | % exercises done
ai_generated_feedback        | TextField      | No       | No     | Automated feedback
therapist_feedback           | TextField      | No       | No     | PT feedback
user_notes                   | TextField      | No       | No     | User comments
improvement_areas            | JSONField      | Yes      | No     | Issues found
positive_feedback_points     | JSONField      | Yes      | No     | Things done well
device_tracking_confidence   | FloatField     | Yes      | No     | AI certainty %
video_recording_available    | Boolean        | Yes      | No     | Video saved?
video_file                   | FileField      | No       | No     | Video file
assigned_therapist_id        | ForeignKey     | No       | No     | PT staff member
session_type                 | CharField(50)  | Yes      | No     | Where/how
pain_level_before            | IntegerField   | No       | No     | Pain before (0-10)
pain_level_after             | IntegerField   | No       | No     | Pain after (0-10)
created_at                   | DateTime       | Auto     | No     | Record creation
updated_at                   | DateTime       | Auto     | No     | Last edit
```

**Field Choices:**
- **status**: pending, in_progress, completed, cancelled, skipped
- **session_type**: home_unsupervised, home_supervised, clinic_session

**Example improvement_areas (JSON):**
```json
[
    {
        "area": "Shoulder alignment",
        "severity": "high",
        "tip": "Keep shoulder back"
    },
    {
        "area": "Elbow extension",
        "severity": "medium",
        "tip": "Extend fully"
    }
]
```

---

### SESSIONEXERCISE Model (Through Model)
```
Field Name                  | Type           | Required | Unique     | Purpose
─────────────────────────────────────────────────────────────────────────────────
id                          | Auto           | Auto     | Yes        | Primary key
session_id                  | ForeignKey     | Yes      | (composite)| Which session
exercise_id                 | ForeignKey     | Yes      | (composite)| Which exercise
order_in_session            | IntegerField   | Yes      | No         | Position
status                      | CharField(20)  | Yes      | No         | Completion state
start_time                  | DateTime       | No       | No         | When started
end_time                    | DateTime       | No       | No         | When ended
reps_performed              | IntegerField   | Yes      | No         | Actual reps
sets_performed              | IntegerField   | Yes      | No         | Actual sets
target_reps                 | IntegerField   | No       | No         | Planned reps
form_score                  | FloatField     | No       | No         | Form quality (0-100)
consistency_score           | FloatField     | No       | No         | Form consistency (0-100)
range_of_motion_percentage  | FloatField     | No       | No         | ROM % (0-100)
average_joint_angles        | JSONField      | Yes      | No         | Actual angles
angle_deviations            | JSONField      | Yes      | No         | vs ideal
form_issues_detected        | JSONField      | Yes      | No         | Issues found
ai_feedback_for_exercise    | TextField      | No       | No         | AI feedback
user_difficulty_rating      | IntegerField   | No       | No         | Difficulty (1-5)
pain_during_exercise        | IntegerField   | No       | No         | Pain level (0-10)
user_notes                  | TextField      | No       | No         | User notes
frames_analyzed             | IntegerField   | Yes      | No         | Video frames
pose_data_captured          | Boolean        | Yes      | No         | Data captured?
created_at                  | DateTime       | Auto     | No         | Record creation
updated_at                  | DateTime       | Auto     | No         | Last edit
```

**Field Choices:**
- **status**: not_started, in_progress, completed, skipped, failed

---

### USERPROGRESS Model
```
Field Name                          | Type       | Required | Purpose
─────────────────────────────────────────────────────────────────────────────────
id                                  | Auto       | Auto     | Primary key
user_id                             | OneToOne   | Yes      | Which user
total_sessions_completed            | IntegerField| Yes      | Lifetime sessions
total_sessions_started              | IntegerField| Yes      | Sessions begun
session_completion_rate             | FloatField | Yes      | % completed
total_exercises_completed           | IntegerField| Yes      | Exercise count
total_minutes_exercised             | IntegerField| Yes      | Total time
average_session_score               | FloatField | Yes      | Mean score
average_exercise_form_score         | FloatField | Yes      | Form mean
best_session_score                  | FloatField | Yes      | Personal best
worst_session_score                 | FloatField | Yes      | Low point
current_streak_days                 | IntegerField| Yes      | Consecutive days
longest_streak_days                 | IntegerField| Yes      | All-time streak
last_session_date                   | DateField  | No       | Last session
exercises_mastered                  | IntegerField| Yes      | Mastered count
avg_difficulty_of_exercises         | CharField(50)| Yes     | Current level
average_pain_before_session         | FloatField | Yes      | Pain before
average_pain_after_session          | FloatField | Yes      | Pain after
pain_improvement_percentage         | FloatField | Yes      | Improvement %
primary_goal                        | CharField(200)| No     | Main goal
goal_progress_percentage            | FloatField | Yes      | Goal %
sessions_this_week                  | IntegerField| Yes      | Weekly count
average_score_this_week             | FloatField | Yes      | Weekly avg
membership_duration_days            | IntegerField| Yes      | Days member
estimated_recovery_date             | DateField  | No       | Recovery ETA
last_updated                        | DateTime   | Auto     | Last calc
```

**Field Choices:**
- **avg_difficulty_of_exercises**: easy, easy-medium, medium, medium-hard, hard

---

### DAILYMETRICS Model
```
Field Name                  | Type        | Required | Unique      | Purpose
─────────────────────────────────────────────────────────────────────────────────
id                          | Auto        | Auto     | Yes         | Primary key
user_id                     | ForeignKey  | Yes      | (composite) | Which user
date                        | DateField   | Yes      | (composite) | Which date
sessions_completed          | IntegerField| Yes      | No          | Today's sessions
exercises_completed         | IntegerField| Yes      | No          | Today's exercises
total_minutes_exercised     | IntegerField| Yes      | No          | Today's time
average_session_score       | FloatField  | Yes      | No          | Today's avg
average_form_score          | FloatField  | Yes      | No          | Form avg
completion_rate             | FloatField  | Yes      | No          | % completed
average_pain_before         | FloatField  | Yes      | No          | Pain before
average_pain_after          | FloatField  | Yes      | No          | Pain after
created_at                  | DateTime    | Auto     | No          | Record creation
updated_at                  | DateTime    | Auto     | No          | Last edit
```

---

### POSEANALYSIS Model
```
Field Name                      | Type       | Required | Unique      | Purpose
─────────────────────────────────────────────────────────────────────────────────
id                              | Auto       | Auto     | Yes         | Primary key
session_exercise_id             | ForeignKey | Yes      | (composite) | Which exercise
frame_number                    | IntegerField| Yes     | (composite) | Frame #
timestamp_seconds               | FloatField | Yes      | No          | Time in video
detected_joint_angles           | JSONField  | Yes      | No          | Detected angles
angle_errors                    | JSONField  | Yes      | No          | vs ideal
pose_detection_confidence       | FloatField | Yes      | No          | AI certainty %
individual_joint_confidence     | JSONField  | Yes      | No          | Per-joint certainty
form_issues                     | JSONField  | Yes      | No          | Issues detected
body_position_description       | CharField(200)| No   | No          | Position desc
is_peak_position                | Boolean    | Yes      | No          | Peak position?
created_at                      | DateTime   | Auto     | No          | Analysis time
```

---

## 🔗 Relationship Summary

| From | To | Type | Through | Meaning |
|------|----|----|---------|---------|
| User | Session | 1:Many | - | One user has many sessions |
| User | UserProgress | 1:1 | - | One user has one progress record |
| User | DailyMetrics | 1:Many | - | One user has many daily records |
| User | Milestone | 1:Many | - | One user can have many achievements |
| Session | Exercise | Many:Many | SessionExercise | Sessions have exercises, exercises in many sessions |
| Session | SessionExercise | 1:Many | - | One session has many exercise records |
| SessionExercise | Exercise | Many:1 | - | Many performances of same exercise |
| SessionExercise | PoseAnalysis | 1:Many | - | One exercise performance has many frame analyses |
| Exercise | Exercise | Self | - | Exercise can have prerequisite/progression exercises |
| User (therapist) | Session | 1:Many | - | Therapist supervises many sessions |

---

## 💾 Data Validation Rules

### User Model
- `age`: 0-150 years
- `height_cm`: 50-300 cm
- `weight_kg`: 20-500 kg

### Exercise Model
- `duration_seconds`: 5-600 seconds (5 min max)
- `recommended_reps`: 1-100
- `recommended_sets`: 1-10
- `rest_seconds_between_sets`: 0-600

### Session Model
- `pain_level_before`: 0-10
- `pain_level_after`: 0-10
- `scheduled_duration_minutes`: 1-180 minutes
- `overall_session_score`: 0-100
- `completion_percentage`: 0-100

### SessionExercise Model
- `form_score`: 0-100
- `consistency_score`: 0-100
- `range_of_motion_percentage`: 0-100
- `user_difficulty_rating`: 1-5
- `pain_during_exercise`: 0-10

### UserProgress Model
- `session_completion_rate`: 0-100%
- `average_session_score`: 0-100
- `average_pain_before_session`: 0-10
- `average_pain_after_session`: 0-10
- `pain_improvement_percentage`: -100 to 100%

---

## 📋 Unique Constraints

| Model | Unique On | Reason |
|-------|-----------|--------|
| User | username | Can't have duplicate login names |
| User | email | Can't have duplicate email addresses |
| Exercise | name | Each exercise template is unique |
| SessionExercise | (session, exercise, order) | Only one instance per position |
| DailyMetrics | (user, date) | One record per user per day |
| PoseAnalysis | (session_exercise, frame_number) | One analysis per frame |

---

## 🔄 Foreign Key References

```python
# USER → SESSION (1:Many)
session.user  # Which user did this session
user.sessions.all()  # All sessions by this user

# SESSION → EXERCISE (Many:Many through SessionExercise)
session.exercises.all()  # All exercises in session
exercise.sessions.all()  # All sessions using exercise

# SESSIONEXERCISE → EXERCISE (Many:1)
session_exercise.exercise  # Which exercise
exercise.session_performances.all()  # All performances of this exercise

# SESSIONEXERCISE → POSEANALYSIS (1:Many)
session_exercise.pose_analyses.all()  # All frame analyses
pose_analysis.session_exercise  # Which exercise instance

# USER → USERPROGRESS (1:1)
user.progress  # Direct access
progress.user  # Back reference

# USER (therapist) → SESSION (1:Many)
session.assigned_therapist  # Assigned PT
user.supervised_sessions.all()  # Sessions supervised by PT
```

---

## 📊 Typical Data Volume Examples

```
For 1,000 users:
  - User records: 1,000
  - Session records: ~10,000 (10 per user)
  - SessionExercise records: ~100,000 (10 exercises per session)
  - PoseAnalysis records: ~10,000,000+ (100-1000 frames per exercise)
  - DailyMetrics: ~365,000 (365 per user per year)
  - UserProgress: 1,000 (1 per user)

Total: ~10 million records
Largest table: PoseAnalysis (one record per video frame!)
```

---

**Created**: April 20, 2026
**Physio AI Project**
