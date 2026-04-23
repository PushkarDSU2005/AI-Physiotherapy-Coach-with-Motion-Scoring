# Django Models Design - Comprehensive Explanation

**Location**: `ADVANCED_MODELS.py`
**Purpose**: Show professional-grade Django models for physiotherapy AI system
**Date Created**: April 20, 2026

---

## 📋 Table of Contents
1. [Model Overview](#model-overview)
2. [User Model](#user-model)
3. [Exercise Model](#exercise-model)
4. [Session Model](#session-model)
5. [SessionExercise Model](#sessionexercise-model)
6. [Progress Tracking Models](#progress-tracking-models)
7. [Data Relationships](#data-relationships)
8. [Field Choices Explained](#field-choices-explained)
9. [Query Examples](#query-examples)

---

## 🎯 Model Overview

| Model | Purpose | Key Records Per User |
|-------|---------|---------------------|
| **User** | Account, profile, medical info | 1 |
| **Exercise** | Exercise templates (shared) | N/A (global) |
| **Session** | Complete workout session | Many (1 per day) |
| **SessionExercise** | Individual exercise in session | Many (5-10 per session) |
| **UserProgress** | Aggregated statistics | 1 |
| **DailyMetrics** | Daily snapshot | 1 per day |
| **PoseAnalysis** | Frame-by-frame AI analysis | Hundreds per session |
| **Milestone** | Achievements | Many over time |

---

## 👤 USER MODEL

### Purpose
Extended user model that handles authentication + physiotherapy-specific data.

### Why Extend Django User?
```python
# ❌ Bad: Using Django's default User
user = User.objects.create_user(username='john')
# Can't store: age, fitness_level, medical_notes, etc.

# ✅ Good: Extended User model
class User(AbstractUser):
    age = IntegerField()
    injury_type = CharField()
    # Plus all Django User fields: username, email, password, etc.
```

### Key Fields Explained

#### Medical Information
```python
injury_type = CharField(choices=[
    ('ankle_sprain', 'Ankle Sprain'),
    ('knee_injury', 'Knee Injury'),
    ...
])
```
**Why**: AI recommends exercises based on injury. Can't prescribe knee exercises to ankle injury patient.

```python
fitness_level = CharField(choices=[
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
])
```
**Why**: Exercise difficulty matching. Beginner shouldn't get advanced exercises initially.

```python
medical_notes = TextField()
```
**Why**: Track allergies, medications, contraindications. Free-form allows flexibility.

#### Physical Measurements
```python
height_cm = IntegerField(validators=[MinValueValidator(50), MaxValueValidator(300)])
weight_kg = FloatField(validators=[MinValueValidator(20), MaxValueValidator(500)])
```
**Why**: 
- Joint angles are proportional to body size
- AI normalizes measurements for accurate form assessment
- Without this, 6ft person and 5ft person would be compared unfairly

#### Activity Tracking
```python
last_activity = DateTimeField(default=timezone.now)
```
**Why**: 
- Know which users are active
- Identify inactive users for engagement
- Calculate streak logic

### User Model Example
```python
# Create new user
user = User.objects.create_user(
    username='sarah',
    email='sarah@example.com',
    password='secure_pass123',
    injury_type='knee_injury',
    fitness_level='beginner',
    height_cm=165,
    weight_kg=62
)

# Query exercises suitable for this user
from exercises.models import Exercise
suitable_exercises = Exercise.objects.filter(
    difficulty_level='easy',
    is_active=True
)

# Access extended field
print(user.injury_type)  # 'knee_injury'
print(user.get_age())    # Calculated from date_of_birth
```

---

## 🏋️ EXERCISE MODEL

### Purpose
Master template library for all exercises in the system.

### Why These Fields?

#### Basic Information
```python
name = CharField(max_length=200, unique=True)
description = TextField()
category = CharField(choices=[
    ('stretching', 'Stretching'),
    ('strengthening', 'Strengthening'),
    ...
])
```
**Why**: 
- Unique name prevents duplicates (can't have 2 "Shoulder Press")
- Category enables filtering: "Show me strengthening exercises"
- Description explains what exercise does

#### Anatomical Data (Critical for AI)
```python
primary_joints = CharField()  # "Shoulder, Elbow"
secondary_joints = CharField()  # "Wrist"

ideal_joint_angles = JSONField(default=dict)  # Example:
# {
#     "phase_1_setup": {"shoulder": 90, "elbow": 90},
#     "phase_2_peak": {"shoulder": 170, "elbow": 180},
#     "phase_3_return": {"shoulder": 90, "elbow": 90}
# }
```

**Why This JSON Structure?**
- Exercises have multiple phases (not one fixed position)
- Each phase has different ideal angles
- JSON is flexible for different exercise types

**Real World Example - Shoulder Press:**
```python
ideal_joint_angles = {
    "start_position": {
        "shoulder": 90,      # Arm at 90°
        "elbow": 90,         # Elbow bent
        "wrist": 0,          # Neutral
        "torso_tilt": 0      # Upright
    },
    "peak_position": {
        "shoulder": 170,     # Arm extended up
        "elbow": 180,        # Fully extended
        "wrist": 0,
        "torso_tilt": -5     # Slight forward lean is ok
    }
}
```

#### Safe Angle Ranges
```python
safe_angle_range = JSONField()  # Example:
# {
#     "shoulder": {"min": 85, "max": 95},
#     "elbow": {"min": 85, "max": 95}
# }
```

**Why?**
- Perfect form (90°) is unrealistic - small variations are okay
- If angle goes outside safe range → AI flags as form issue
- Prevents injury by catching dangerous angles

**Example Logic:**
```python
# During exercise, AI measures shoulder at 110°
# Safe range: 85-95°
# Result: Form issue detected! (Too high)
```

#### Difficulty and Progression
```python
difficulty_level = CharField(choices=[
    ('easy', 'Easy'),
    ('medium', 'Medium'),
    ('hard', 'Hard'),
])

progression_to = ForeignKey('self')  # Links to harder exercise
prerequisites = ManyToManyField('self')  # Exercises that should come first
```

**Why?**
- Prevents giving hard exercises to beginners
- Creates exercise progression paths
- Example: Beginner → Wall Push-ups → Push-ups → Archer Push-ups

#### Prescription Data
```python
recommended_reps = IntegerField()  # "12 reps"
recommended_sets = IntegerField()  # "3 sets"
rest_seconds_between_sets = IntegerField()  # "60 seconds"
duration_seconds = IntegerField()  # Total exercise time
```

**Why?**
- Tells user exactly what to do
- System can track completion vs prescription
- Can adjust if user can't meet targets

#### Media and Instructions
```python
step_by_step_instructions = TextField()  # "1. Stand with feet...\n2. Hold..."
instruction_video_url = URLField()  # Link to YouTube/demo
form_reference_image_url = URLField()  # Photo of correct form
```

**Why?**
- Prevents injuries from wrong technique
- Visual + text learning
- Can reference during session

#### Safety
```python
common_mistakes = TextField()  # "Don't lock knees, don't lean back"
safety_notes = TextField()  # "Contraindicated for shoulder dislocation"
equipment_required = CharField()  # "Dumbbells 5-10kg" or "None"
```

**Why?**
- Therapist knowledge captured
- Alerts users to watch out for
- Equipment availability check

### Exercise Model Example
```python
# Create an exercise
shoulder_press = Exercise.objects.create(
    name="Dumbbell Shoulder Press",
    category="strengthening",
    difficulty_level="medium",
    target_muscle_groups="Deltoid, Triceps, Chest",
    duration_seconds=120,
    recommended_reps=10,
    recommended_sets=3,
    primary_joints="Shoulder, Elbow",
    ideal_joint_angles={
        "start": {"shoulder": 90, "elbow": 90},
        "peak": {"shoulder": 170, "elbow": 180},
    },
    safe_angle_range={
        "shoulder": {"min": 85, "max": 95},
        "elbow": {"min": 85, "max": 95}
    },
    instructions="1. Stand upright\n2. Hold dumbbells at shoulder...",
    is_active=True
)

# Check if suitable for user
user = User.objects.get(username='john')
if shoulder_press.is_suitable_for_fitness_level(user.fitness_level):
    print("Good exercise for this user")
```

---

## 🎥 SESSION MODEL

### Purpose
Records a complete exercise session with overall metrics and feedback.

### Key Fields Explained

#### Timing and Status
```python
start_time = DateTimeField()
end_time = DateTimeField(null=True)  # null = still in progress

status = CharField(choices=[
    ('pending', 'Not started'),
    ('in_progress', 'Currently running'),
    ('completed', 'Finished'),
    ('cancelled', 'Not finished'),
])
```

**Why?**
- Track workflow: pending → in_progress → completed
- Calculate actual duration (if end_time exists)
- Query "all pending sessions" to show user

#### Scoring System
```python
overall_session_score = FloatField(0-100)  # Average of all exercises
average_exercise_score = FloatField(0-100)  # Mean score
completion_percentage = FloatField(0-100)   # How many exercises done
```

**Why Multiple Scores?**
- overall_session_score = Quality (how well did they do?)
- completion_percentage = Quantity (how much did they do?)
- User could have 85% quality but only completed 60% (skipped 2 exercises)

**Example:**
```python
# Session with 5 exercises
# User completed 3 exercises: scores 90, 85, 92
# overall_session_score = (90 + 85 + 92) / 5 = 61.4
# (divided by 5 because 2 not done)
# completion_percentage = 3/5 = 60%
```

#### Feedback Fields
```python
ai_generated_feedback = TextField()
therapist_feedback = TextField()
user_notes = TextField()
```

**Why Separate?**
- AI feedback is automated (consistent, immediate)
- Therapist feedback adds professional judgment
- User notes track subjective experience
- Each source valuable for different purposes

#### Improvement Tracking
```python
improvement_areas = JSONField()  # List of issues
# [
#     {"area": "Shoulder alignment", "severity": "high", "tip": "Keep shoulder back"},
#     {"area": "Elbow extension", "severity": "medium", "tip": "Extend fully"}
# ]

positive_feedback_points = JSONField()
# ["Great consistency", "Full range of motion achieved"]
```

**Why JSON Lists?**
- Flexible number of items
- Each item has structure (area, severity, tip)
- Can iterate and display easily
- Stores multiple points of feedback

#### Pain Tracking
```python
pain_level_before = IntegerField(0-10)  # Before session
pain_level_after = IntegerField(0-10)   # After session
```

**Why?**
- Measure therapy effectiveness
- If pain increases → adjust exercise intensity
- Trends show if therapy is working

#### Session Context
```python
assigned_therapist = ForeignKey(User)  # PT assigned
session_type = CharField(choices=[
    ('home_unsupervised', 'Home - Unsupervised'),
    ('home_supervised', 'Home - Telehealth'),
    ('clinic_session', 'Clinic - In-Person'),
])
```

**Why?**
- Track accountability
- Different recommendations per setting
- In-clinic data more accurate (therapist watching)

### Session Model Example
```python
from django.utils import timezone
from datetime import timedelta

# Create a session
session = Session.objects.create(
    user=john_user,
    title="Shoulder Rehabilitation - Day 15",
    start_time=timezone.now(),
    status='in_progress',
    scheduled_duration_minutes=30,
    session_type='home_unsupervised',
    pain_level_before=6
)

# Later, mark as completed
session.end_time = timezone.now()
session.status = 'completed'
session.overall_session_score = 87.5
session.ai_generated_feedback = "Great form! Keep the shoulder steady."
session.pain_level_after = 4
session.save()

# Query sessions for user
user_sessions = Session.objects.filter(
    user=john_user,
    status='completed'
).order_by('-start_time')  # Most recent first
```

---

## 🏃 SESSIONEXERCISE MODEL

### Purpose
Through model - tracks individual exercise performance within a session.

### Why Separate Model?
```python
# ❌ Bad: Exercise has only one score
exercise.score = 87  # But which session? Different sessions = different scores!

# ✅ Good: SessionExercise links exercise to specific session + performance
session_exercise = SessionExercise.objects.create(
    session=session1,
    exercise=shoulder_press,
    form_score=87
)

session_exercise2 = SessionExercise.objects.create(
    session=session2,
    exercise=shoulder_press,
    form_score=92  # Same exercise, different session, different score
)
```

### Key Fields Explained

#### Sequencing and Timing
```python
order_in_session = IntegerField()  # 1st, 2nd, 3rd exercise
start_time = DateTimeField()
end_time = DateTimeField()
```

**Why?**
- Preserves exercise order (important for warm-up)
- Calculate time spent per exercise
- Progressive fatigue analysis (form worse in later exercises)

#### Performance Execution
```python
reps_performed = IntegerField()  # Actually did 10 reps
sets_performed = IntegerField()  # Actually did 3 sets
target_reps = IntegerField()     # Supposed to do 12 reps

# Can calculate adherence:
adherence = (10 / 12) * 100 = 83.3%
```

**Why?**
- User might do fewer/more reps than prescribed
- Track if user is struggling or over-confident
- Adjust future prescriptions

#### Form Quality Scores
```python
form_score = FloatField(0-100)  # Overall form quality
consistency_score = FloatField(0-100)  # Was form consistent across reps?
range_of_motion_percentage = FloatField(0-100)  # Did they move enough?
```

**Why Multiple Scores?**
- form_score = How close to ideal angles
- consistency_score = Reps 1-10 equally good? Or did form degrade?
- range_of_motion_percentage = 100% = full range, 60% = limited

**Example - Shoulder Press with 10 reps:**
```python
# Rep 1-3: Perfect form (95%)
# Rep 4-7: Good form (85%)
# Rep 8-10: Tired, form drops (70%)
# average form_score = 85%
# consistency_score = 70% (significant drop by end)
# range_of_motion = 90% (nearly full extension)
```

#### Angle Tracking
```python
average_joint_angles = JSONField()  # {shoulder_avg: 92.5, elbow_avg: 175}
angle_deviations = JSONField()  # {shoulder_dev: 2.5, elbow_dev: -5}
```

**Why?**
- average_joint_angles = What angles did they actually achieve?
- angle_deviations = How far from ideal? (negative = under, positive = over)

#### Issue Detection
```python
form_issues_detected = JSONField()
# [
#     {
#         "issue": "Shoulder not level",
#         "frames_affected": 5,
#         "severity": "medium"
#     },
#     {
#         "issue": "Elbow drops",
#         "frames_affected": 10,
#         "severity": "high"
#     }
# ]
```

**Why?**
- Not just a score, but **which** aspects are wrong
- AI can give specific feedback: "Fix your shoulder position"
- Frames affected shows how often it happened

#### User Experience
```python
user_difficulty_rating = IntegerField(1-5)  # "How hard was this?"
pain_during_exercise = IntegerField(0-10)   # "Did it hurt?"
```

**Why?**
- Subjective experience vs objective AI assessment
- If pain_during > pain_before significantly: reduce intensity
- User rating vs difficulty_level → too hard or too easy?

### SessionExercise Model Example
```python
# Create session exercise
session_ex = SessionExercise.objects.create(
    session=session,
    exercise=shoulder_press,
    order_in_session=1,
    start_time=timezone.now(),
    target_reps=12,
    status='in_progress'
)

# Later, update with results
session_ex.end_time = timezone.now()
session_ex.reps_performed = 10
session_ex.form_score = 85
session_ex.consistency_score = 78
session_ex.angle_deviations = {
    "shoulder": 5.2,  # +5.2° too high
    "elbow": -3.1     # -3.1° not fully extended
}
session_ex.form_issues_detected = [
    {
        "issue": "Shoulder elevation",
        "frames_affected": 8,
        "severity": "medium"
    }
]
session_ex.status = 'completed'
session_ex.save()

# Query to find exercises with poor form
poor_form_exercises = SessionExercise.objects.filter(
    form_score__lt=70  # Score below 70
).select_related('exercise')
```

---

## 📊 PROGRESS TRACKING MODELS

### UserProgress Model

**Purpose**: Denormalized aggregation of user stats for fast queries.

**Why Denormalized?**
```python
# ❌ Slow: Calculate every time
sessions = Session.objects.filter(user=user, status='completed')
avg_score = sessions.aggregate(Avg('overall_session_score'))

# ✅ Fast: Already calculated and stored
progress = UserProgress.objects.get(user=user)
avg_score = progress.average_session_score
```

#### Key Fields

```python
total_sessions_completed = IntegerField()  # Cumulative count
session_completion_rate = FloatField(0-100)  # 85% completion

average_session_score = FloatField(0-100)  # Mean across all
best_session_score = FloatField(0-100)  # Personal best
worst_session_score = FloatField(0-100)  # Low point

current_streak_days = IntegerField()  # Consecutive days
longest_streak_days = IntegerField()  # All-time best

pain_improvement_percentage = FloatField()  # Before vs after
estimated_recovery_date = DateField()  # Projected recovery
```

#### Update Logic
```python
def update_from_latest_sessions(self):
    """Recalculate metrics from session data."""
    sessions = Session.objects.filter(user=self.user)
    completed = sessions.filter(status='completed')
    
    # Update aggregates
    self.total_sessions_completed = completed.count()
    self.average_session_score = completed.aggregate(
        Avg('overall_session_score')
    )['overall_session_score__avg']
    
    self.save()
```

### DailyMetrics Model

**Purpose**: Daily snapshot for charting progress over time.

**Why?**
- One record per user per day = easy to chart
- Don't need to query all sessions for "last 30 days"
- Efficient time-series data

```python
date = DateField()  # One per user per day (unique_together)
sessions_completed = IntegerField()  # Today's count
average_session_score = FloatField()  # Today's score
total_minutes_exercised = IntegerField()  # Today's total
completion_rate = FloatField()  # Today's %
```

**Example Query - Last 30 Days Progress:**
```python
from datetime import timedelta
from django.utils import timezone

user = User.objects.get(username='john')
thirty_days_ago = timezone.now().date() - timedelta(days=30)

daily_metrics = DailyMetrics.objects.filter(
    user=user,
    date__gte=thirty_days_ago
).order_by('date')

# Now can easily chart:
# X-axis: date
# Y-axis: average_session_score
# Shows trend without querying 100+ sessions
```

---

## 🔍 DATA RELATIONSHIPS

### Visual Relationship Map

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ username, email, password, injury_type, age, etc.   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
           │ 1:1               │ 1:Many            │ 1:Many
           ▼                    ▼                    ▼
    ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐
    │UserProgress  │   │   Session    │   │  DailyMetrics    │
    │              │   │              │   │  (one per day)   │
    └──────────────┘   └──────────────┘   └──────────────────┘
                              │
                              │ Many:Many
                              │ (through SessionExercise)
                              ▼
                       ┌──────────────────┐
                       │    Exercise      │
                       │ (Shared across   │
                       │  all users)      │
                       └──────────────────┘
                              ▲
                              │ 1:Many
                              │
                    ┌─────────────────────┐
                    │ SessionExercise     │
                    │ (Individual perf.)  │
                    └─────────────────────┘
                              │
                              │ 1:Many
                              ▼
                       ┌──────────────────┐
                       │ PoseAnalysis     │
                       │ (Per frame)      │
                       └──────────────────┘
```

### Specific Relationships

#### One-to-One (1:1)
```python
class UserProgress(Model):
    user = OneToOneField(User)  # One progress per user

# Usage: Get user's progress
progress = user.progress  # Direct access!
print(progress.average_session_score)
```

#### One-to-Many (1:Many)
```python
class Session(Model):
    user = ForeignKey(User)  # Many sessions per user

# Usage:
sessions = user.sessions.all()  # All sessions for user
session = user.sessions.filter(status='completed')
```

#### Many-to-Many (M:M)
```python
class Session(Model):
    exercises = ManyToManyField(Exercise, through='SessionExercise')

# Usage:
session.exercises.all()  # All exercises in session
exercise.sessions.all()  # All sessions containing this exercise

# Access through model:
session_exercise = SessionExercise.objects.get(
    session=session,
    exercise=exercise
)
print(session_exercise.form_score)  # Individual performance
```

---

## 🎛️ FIELD CHOICES EXPLAINED

### Why Use Choices?

```python
# ❌ Bad: Free text
status = CharField()  # Could be "completed", "Completed", "DONE", "done"
# Database has 4 values meaning the same thing!

# ✅ Good: Limited choices
status = CharField(choices=[
    ('completed', 'Completed'),
    ('pending', 'Pending'),
])
# Only 2 options, consistent data
```

### Field Choice Examples

#### User.fitness_level
```python
FITNESS_CHOICES = [
    ('beginner', 'Beginner - Just starting'),
    ('intermediate', 'Intermediate - Some experience'),
    ('advanced', 'Advanced - Regular exerciser'),
]
```
**Used for**: Exercise recommendations, difficulty matching

#### Exercise.category
```python
CATEGORY_CHOICES = [
    ('stretching', 'Stretching'),
    ('strengthening', 'Strengthening'),
    ('mobility', 'Mobility'),
    ('balance', 'Balance'),
    ('flexibility', 'Flexibility'),
    ('cardio', 'Cardio'),
    ('coordination', 'Coordination'),
]
```
**Used for**: Filtering exercises, PT planning

#### Session.status
```python
STATUS_CHOICES = [
    ('pending', 'Pending - Not Started'),
    ('in_progress', 'In Progress - Currently Running'),
    ('completed', 'Completed - Finished'),
    ('cancelled', 'Cancelled - Not Completed'),
    ('skipped', 'Skipped - User Opted Out'),
]
```
**Used for**: Workflow management, analytics

---

## 💡 QUERY EXAMPLES

### Example 1: Get User's Last Week of Sessions
```python
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg

user = User.objects.get(username='sarah')
week_ago = timezone.now() - timedelta(days=7)

sessions = Session.objects.filter(
    user=user,
    status='completed',
    start_time__gte=week_ago
).order_by('-start_time')

# Calculate average
avg_score = sessions.aggregate(
    Avg('overall_session_score')
)['overall_session_score__avg']

print(f"Last week: {sessions.count()} sessions, avg score: {avg_score:.1f}")
```

### Example 2: Find Poor Form Exercises
```python
poor_form = SessionExercise.objects.filter(
    form_score__lt=70,
    status='completed'
).select_related('exercise').values('exercise__name').distinct()

# Show which exercises user struggles with
for item in poor_form:
    print(f"Needs improvement: {item['exercise__name']}")
```

### Example 3: Track Pain Improvement
```python
# Get sessions with pain data
sessions = Session.objects.filter(
    user=user,
    pain_level_before__isnull=False,
    pain_level_after__isnull=False
).order_by('start_time')

for session in sessions:
    improvement = session.pain_level_before - session.pain_level_after
    print(f"{session.start_time.date()}: {session.pain_level_before} → {session.pain_level_after} (improved {improvement} points)")
```

### Example 4: Recommend Next Exercise
```python
# Find exercises user has mastered
from django.db.models import Avg

mastered = SessionExercise.objects.filter(
    session__user=user,
    form_score__gte=85
).values('exercise_id').distinct()

mastered_exercise_ids = [item['exercise_id'] for item in mastered]

# Get progression exercises
next_exercises = Exercise.objects.filter(
    progression_from__in=mastered_exercise_ids,
    is_active=True
)

print("Ready for these exercises:", next_exercises.values_list('name', flat=True))
```

### Example 5: Calculate Session Adherence
```python
# Get sessions and their exercises
session = Session.objects.get(id=5)
exercise_records = session.exercise_records.all()

total_exercises = session.exercises.count()
completed_exercises = exercise_records.filter(status='completed').count()
adherence_percent = (completed_exercises / total_exercises) * 100

print(f"Completed {completed_exercises}/{total_exercises} exercises ({adherence_percent:.0f}%)")
```

---

## 🔐 Data Integrity Features

### Validators
```python
# Prevent invalid data
age = IntegerField(validators=[
    MinValueValidator(0),
    MaxValueValidator(150)
])  # Age can't be negative or 150+

score = FloatField(validators=[
    MinValueValidator(0),
    MaxValueValidator(100)
])  # Scores must be 0-100
```

### Unique Constraints
```python
class Exercise(Model):
    name = CharField(unique=True)  # Can't have duplicate exercise names

class DailyMetrics(Model):
    unique_together = ['user', 'date']  # One record per user per day
```

### Choices Limit Options
```python
status = CharField(choices=STATUS_CHOICES)
# Can only be one of the choices, prevents typos
```

### Foreign Keys Ensure Referential Integrity
```python
session = ForeignKey(Session, on_delete=models.CASCADE)
# If session deleted, all related SessionExercises deleted too
# Can't have orphaned records
```

---

## 📈 Benefits of This Design

| Benefit | How Achieved |
|---------|-------------|
| **Performance** | Denormalized progress fields, indexes on common queries |
| **Accuracy** | Validators, choices, unique constraints |
| **Flexibility** | JSON fields for extensibility without schema changes |
| **Auditing** | created_at, updated_at timestamps on all models |
| **Relationships** | Clear ForeignKey and ManyToMany links prevent data errors |
| **AI Integration** | Dedicated PoseAnalysis and detailed angle tracking |
| **User Experience** | Feedback fields, improvement areas, pain tracking |
| **Analytics** | Daily snapshots and progress aggregation |
| **Security** | User ownership prevents cross-user data access |

---

## 🚀 How to Implement

### Step 1: Replace Models
Replace the basic models in your apps with these advanced ones:
```bash
# Copy ADVANCED_MODELS.py structure into:
# users/models.py
# exercises/models.py
# sessions/models.py
# analytics/models.py
```

### Step 2: Create Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Test Queries
Use the examples above to ensure everything works.

### Step 4: Admin Customization
Add admin.py customization for new fields:
```python
class SessionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'status',
        'overall_session_score', 'completion_percentage'
    ]
    list_filter = ['status', 'start_time']
    readonly_fields = ['created_at', 'updated_at']
```

---

**Created**: April 20, 2026
**Project**: Physio AI - Advanced Django Models
