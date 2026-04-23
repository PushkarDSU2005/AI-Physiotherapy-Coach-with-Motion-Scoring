# Practical Django Models Examples

**Project**: Physio AI System
**Purpose**: Real-world code examples for model operations
**Date**: April 20, 2026

---

## 🔥 Quick Reference: Common Operations

### 1. CREATE - Add New Records

#### Create a New User
```python
from django.contrib.auth import get_user_model

User = get_user_model()

user = User.objects.create_user(
    username='sarah_jones',
    email='sarah@example.com',
    password='SecurePassword123!',
    first_name='Sarah',
    last_name='Jones',
    date_of_birth='1990-05-15',
    injury_type='knee_injury',
    fitness_level='intermediate',
    height_cm=165,
    weight_kg=62,
    medical_notes='ACL surgery 2 years ago. Currently pain-free.'
)
```

#### Create an Exercise
```python
from exercises.models import Exercise

shoulder_press = Exercise.objects.create(
    name='Dumbbell Shoulder Press',
    category='strengthening',
    difficulty_level='medium',
    target_muscle_groups='Deltoid, Triceps, Chest, Core',
    duration_seconds=120,
    recommended_reps=10,
    recommended_sets=3,
    rest_seconds_between_sets=90,
    primary_joints='Shoulder, Elbow',
    secondary_joints='Wrist, Core',
    ideal_joint_angles={
        'setup': {'shoulder': 90, 'elbow': 90},
        'peak': {'shoulder': 170, 'elbow': 180},
        'return': {'shoulder': 90, 'elbow': 90}
    },
    safe_angle_range={
        'shoulder': {'min': 85, 'max': 95},
        'elbow': {'min': 85, 'max': 95}
    },
    step_by_step_instructions="""
    1. Stand with feet shoulder-width apart
    2. Hold dumbbells at shoulder height with palms forward
    3. Press dumbbells up until arms are fully extended
    4. Lower back to starting position
    5. Repeat for desired reps
    """,
    common_mistakes='Leaning back excessively, not full extension, dropping elbows',
    safety_notes='Not recommended for recent shoulder surgery. Keep core tight.',
    instruction_video_url='https://youtube.com/watch?v=...',
    form_reference_image_url='https://example.com/images/shoulder-press.jpg',
    equipment_required='Dumbbells (5-15kg)',
    is_active=True
)
```

#### Create a Session
```python
from sessions.models import Session
from django.utils import timezone

session = Session.objects.create(
    user=user,
    title='Daily Shoulder Strengthening - Week 3',
    description='Focus on proper form and full range of motion',
    start_time=timezone.now(),
    status='in_progress',
    scheduled_duration_minutes=30,
    session_type='home_supervised',  # Telehealth with therapist
    pain_level_before=3
)
```

#### Add Exercises to Session
```python
from sessions.models import SessionExercise

# Get exercises for this session
exercises = Exercise.objects.filter(
    category='strengthening',
    difficulty_level__in=['easy', 'medium']
).order_by('?')[:5]

# Add to session in order
for i, exercise in enumerate(exercises, 1):
    SessionExercise.objects.create(
        session=session,
        exercise=exercise,
        order_in_session=i,
        target_reps=exercise.recommended_reps,
        status='not_started'
    )
```

---

### 2. READ - Retrieve Records

#### Get a Specific User
```python
user = User.objects.get(username='sarah_jones')
print(f"User: {user.first_name} {user.last_name}")
print(f"Injury: {user.get_injury_type_display()}")  # "Knee Injury"
print(f"Age: {user.get_age()}")
```

#### Get User's Sessions
```python
# All sessions
all_sessions = user.sessions.all().order_by('-start_time')

# Completed sessions only
completed = user.sessions.filter(status='completed')

# This week's sessions
from datetime import timedelta
from django.utils import timezone

week_ago = timezone.now() - timedelta(days=7)
this_week = user.sessions.filter(start_time__gte=week_ago)

print(f"Sessions completed this week: {this_week.count()}")
```

#### Get Exercises by Difficulty
```python
# Easy exercises
easy_exercises = Exercise.objects.filter(
    difficulty_level='easy',
    is_active=True
).order_by('name')

# Suitable for user's fitness level
suitable = Exercise.objects.filter(
    is_active=True
)
for exercise in suitable:
    if exercise.is_suitable_for_fitness_level(user.fitness_level):
        print(f"✓ {exercise.name}")
```

#### Get Session Details with Exercises
```python
session = Session.objects.get(id=5)

# Get all exercises in this session with performance data
exercises = session.exercise_records.all().select_related('exercise')

for session_exercise in exercises:
    print(f"\n{session_exercise.order_in_session}. {session_exercise.exercise.name}")
    print(f"   Status: {session_exercise.get_status_display()}")
    print(f"   Form Score: {session_exercise.form_score}")
    print(f"   Reps: {session_exercise.reps_performed}/{session_exercise.target_reps}")
    print(f"   Pain: {session_exercise.pain_during_exercise}/10")
```

---

### 3. UPDATE - Modify Records

#### Update Session During Exercise
```python
session_exercise = SessionExercise.objects.get(id=15)

# Mark as started
session_exercise.status = 'in_progress'
session_exercise.start_time = timezone.now()
session_exercise.save()

# Later: Mark as completed with results
session_exercise.end_time = timezone.now()
session_exercise.status = 'completed'
session_exercise.reps_performed = 12
session_exercise.sets_performed = 3
session_exercise.form_score = 85.5
session_exercise.consistency_score = 82.0
session_exercise.range_of_motion_percentage = 92.0
session_exercise.average_joint_angles = {
    'shoulder': 92.5,
    'elbow': 178.2,
    'wrist': 2.1
}
session_exercise.angle_deviations = {
    'shoulder': 2.5,  # 2.5° higher than ideal
    'elbow': -1.8     # 1.8° less extension
}
session_exercise.form_issues_detected = [
    {
        'issue': 'Slight shoulder elevation',
        'frames_affected': 5,
        'severity': 'low'
    }
]
session_exercise.ai_feedback_for_exercise = (
    "Great form! Keep shoulders level at the top. "
    "Very good consistency throughout the set."
)
session_exercise.pain_during_exercise = 1
session_exercise.user_difficulty_rating = 3
session_exercise.save()
```

#### Complete a Session
```python
from django.db.models import Avg

session = Session.objects.get(id=5)

# Mark as completed
session.end_time = timezone.now()
session.status = 'completed'

# Calculate scores
exercises = session.exercise_records.filter(status='completed')
if exercises.exists():
    avg_form = exercises.aggregate(Avg('form_score'))['form_score__avg']
    session.average_exercise_score = avg_form
    session.overall_session_score = avg_form * 0.95  # Slight penalty for 2 skipped
    
completed_count = exercises.count()
total_count = session.exercises.count()
session.completion_percentage = (completed_count / total_count) * 100

# Add feedback
session.ai_generated_feedback = (
    f"Good session! Completed {completed_count}/{total_count} exercises. "
    f"Average form score: {avg_form:.1f}%. "
    f"Keep working on shoulder stability."
)
session.pain_level_after = 2
session.save()
```

#### Update User Progress
```python
from django.db.models import Avg, Count, Q

user = User.objects.get(username='sarah_jones')
progress = user.progress

# Recalculate from all sessions
sessions = user.sessions.filter(status='completed')

progress.total_sessions_completed = sessions.count()
progress.average_session_score = sessions.aggregate(
    avg=Avg('overall_session_score')
)['avg'] or 0.0
progress.best_session_score = sessions.aggregate(
    max=Max('overall_session_score')
)['max'] or 0.0

# Calculate total exercise time
total_minutes = 0
for session in sessions:
    duration = session.calculate_duration()
    if duration:
        total_minutes += duration / 60

progress.total_minutes_exercised = int(total_minutes)

# Calculate pain improvement
completed_with_pain = sessions.filter(
    pain_level_before__isnull=False,
    pain_level_after__isnull=False
)
if completed_with_pain.exists():
    avg_before = completed_with_pain.aggregate(
        avg=Avg('pain_level_before')
    )['avg']
    avg_after = completed_with_pain.aggregate(
        avg=Avg('pain_level_after')
    )['avg']
    improvement = ((avg_before - avg_after) / avg_before) * 100
    progress.pain_improvement_percentage = improvement

progress.last_updated = timezone.now()
progress.save()
```

---

### 4. ANALYZE - Query and Report

#### Get User's Performance Summary
```python
def get_user_performance_summary(user):
    """Generate performance summary for user."""
    progress = user.progress
    
    summary = {
        'user': user.get_full_name(),
        'member_since': user.date_joined.date(),
        'injury': user.get_injury_type_display(),
        'fitness_level': user.get_fitness_level_display(),
        
        'statistics': {
            'total_sessions': progress.total_sessions_completed,
            'total_exercises': progress.total_exercises_completed,
            'total_hours': progress.total_minutes_exercised / 60,
            'completion_rate': f"{progress.session_completion_rate:.1f}%",
        },
        
        'scores': {
            'average': f"{progress.average_session_score:.1f}",
            'best': f"{progress.best_session_score:.1f}",
            'worst': f"{progress.worst_session_score:.1f}",
        },
        
        'progress': {
            'current_streak': progress.current_streak_days,
            'longest_streak': progress.longest_streak_days,
            'pain_improvement': f"{progress.pain_improvement_percentage:.1f}%",
        },
        
        'recent_sessions': [],
    }
    
    # Add recent sessions
    recent = user.sessions.filter(
        status='completed'
    ).order_by('-start_time')[:5]
    
    for session in recent:
        summary['recent_sessions'].append({
            'date': session.start_time.strftime('%Y-%m-%d'),
            'duration': int(session.calculate_duration() / 60) if session.calculate_duration() else 0,
            'score': session.overall_session_score or 'N/A',
            'exercises': session.exercises.count(),
        })
    
    return summary

# Use it
report = get_user_performance_summary(user)
print(f"\n=== Performance Report: {report['user']} ===")
print(f"Injury: {report['injury']}")
print(f"Sessions completed: {report['statistics']['total_sessions']}")
print(f"Average score: {report['scores']['average']}")
print(f"Pain improvement: {report['progress']['pain_improvement']}")
```

#### Find Exercises User Needs Improvement On
```python
def get_exercises_needing_improvement(user, threshold=75):
    """Find exercises where user struggles (score < threshold)."""
    from django.db.models import Avg
    
    poor_performance = SessionExercise.objects.filter(
        session__user=user,
        status='completed'
    ).values('exercise_id', 'exercise__name').annotate(
        avg_score=Avg('form_score')
    ).filter(
        avg_score__lt=threshold
    ).order_by('avg_score')
    
    results = []
    for item in poor_performance:
        exercise = Exercise.objects.get(id=item['exercise_id'])
        
        # Get latest attempt
        latest = SessionExercise.objects.filter(
            exercise_id=item['exercise_id'],
            session__user=user
        ).order_by('-created_at').first()
        
        results.append({
            'name': item['exercise__name'],
            'avg_score': item['avg_score'],
            'latest_score': latest.form_score if latest else 'N/A',
            'improvement_areas': latest.form_issues_detected if latest else [],
        })
    
    return results

# Use it
improvements_needed = get_exercises_needing_improvement(user, threshold=80)
print("\n📌 Exercises Needing Improvement (Score < 80):")
for item in improvements_needed:
    print(f"\n{item['name']}")
    print(f"  Average: {item['avg_score']:.1f}%")
    print(f"  Latest: {item['latest_score']}%")
    for issue in item['improvement_areas']:
        print(f"  ⚠️  {issue['issue']} ({issue['severity'].upper()})")
```

#### Generate Weekly Progress Report
```python
def generate_weekly_report(user, days=7):
    """Generate a weekly progress report."""
    from datetime import timedelta
    from django.db.models import Sum, Avg, Count
    
    cutoff_date = timezone.now() - timedelta(days=days)
    
    weekly_sessions = user.sessions.filter(
        status='completed',
        start_time__gte=cutoff_date
    )
    
    metrics = weekly_sessions.aggregate(
        count=Count('id'),
        avg_score=Avg('overall_session_score'),
        total_mins=Sum('scheduled_duration_minutes'),
        avg_pain_before=Avg('pain_level_before'),
        avg_pain_after=Avg('pain_level_after'),
    )
    
    report = f"""
    ╔════════════════════════════════════════╗
    ║   WEEKLY PROGRESS REPORT               ║
    ║   {user.first_name} {user.last_name}  │
    ║   {timezone.now().strftime('%B %d, %Y')}              ║
    ╚════════════════════════════════════════╝
    
    📊 SESSIONS
    ├─ Completed: {metrics['count']}
    ├─ Average Score: {metrics['avg_score']:.1f}/100
    └─ Total Time: {metrics['total_mins']}+ minutes
    
    😊 PAIN LEVELS
    ├─ Before Sessions: {metrics['avg_pain_before']:.1f}/10
    ├─ After Sessions: {metrics['avg_pain_after']:.1f}/10
    └─ Improvement: {(metrics['avg_pain_before'] - metrics['avg_pain_after']):.1f} points
    
    🏆 STREAK
    ├─ Current: {user.progress.current_streak_days} days
    └─ Personal Best: {user.progress.longest_streak_days} days
    """
    
    return report

# Generate report
print(generate_weekly_report(user))
```

---

### 5. DELETE - Remove Records

#### Delete a Session
```python
session = Session.objects.get(id=5)

# This also deletes:
# - All SessionExercise records (cascade)
# - All PoseAnalysis records for those exercises (cascade)
session.delete()

print("Session and all related data deleted")
```

---

### 6. BULK OPERATIONS

#### Bulk Create Multiple Sessions
```python
from django.utils import timezone
from datetime import timedelta

sessions_to_create = []
user = User.objects.get(username='sarah_jones')

# Create 30 sessions (one per day for a month)
for i in range(30):
    session_date = timezone.now() - timedelta(days=i)
    sessions_to_create.append(
        Session(
            user=user,
            title=f"Daily Rehabilitation - Day {i+1}",
            start_time=session_date,
            end_time=session_date + timedelta(minutes=30),
            status='completed',
            scheduled_duration_minutes=30,
            session_type='home_unsupervised',
            overall_session_score=80 + (i % 5),
            completion_percentage=100,
            pain_level_before=6 - (i // 5),
            pain_level_after=3 - (i // 10),
        )
    )

# Bulk insert (faster than creating one by one)
Session.objects.bulk_create(sessions_to_create)
print(f"Created {len(sessions_to_create)} sessions")
```

#### Bulk Update Scores
```python
# Update all sessions from yesterday with score
from datetime import timedelta

yesterday = timezone.now() - timedelta(days=1)

Session.objects.filter(
    start_time__date=yesterday.date(),
    status='completed',
    overall_session_score__isnull=True
).update(
    overall_session_score=82.5
)
```

---

### 7. ADVANCED QUERIES

#### Find Best Performing Users
```python
from django.db.models import Avg

top_users = UserProgress.objects.filter(
    total_sessions_completed__gte=5
).order_by('-average_session_score')[:10]

print("🏆 Top 10 Performers:")
for i, progress in enumerate(top_users, 1):
    print(f"{i}. {progress.user.get_full_name()}: {progress.average_session_score:.1f}%")
```

#### Find Exercises Used in Completed Sessions
```python
completed_sessions = Session.objects.filter(status='completed')

# Exercises in completed sessions
used_exercises = Exercise.objects.filter(
    sessions__in=completed_sessions
).distinct().annotate(
    usage_count=Count('sessions', filter=Q(sessions__status='completed'))
).order_by('-usage_count')[:10]

print("📋 Most Used Exercises:")
for exercise in used_exercises:
    print(f"  {exercise.name}: {exercise.usage_count} times")
```

#### Find Users at Risk (Haven't Exercised Recently)
```python
# Users with no sessions in last 7 days
from datetime import timedelta

week_ago = timezone.now() - timedelta(days=7)

at_risk_users = User.objects.exclude(
    sessions__start_time__gte=week_ago
)

print(f"⚠️  {at_risk_users.count()} users haven't exercised in 7 days")
```

---

### 8. RELATIONSHIP NAVIGATION

#### Access Related Objects
```python
# From User to Progress
user = User.objects.get(username='sarah')
progress = user.progress  # Direct 1:1 access
print(f"Average score: {progress.average_session_score}")

# From Session to Exercises
session = Session.objects.get(id=5)
exercises = session.exercises.all()  # All exercises in session
for exercise in exercises:
    print(exercise.name)

# From Exercise to All Its Sessions
exercise = Exercise.objects.get(name='Shoulder Press')
all_sessions = exercise.sessions.all()  # All sessions using this exercise
print(f"Used in {all_sessions.count()} sessions")

# Through Model - Get Individual Performance
session_exercise = SessionExercise.objects.get(
    session=session,
    exercise=exercise
)
print(f"Form score: {session_exercise.form_score}")

# Get All Pose Analyses for an Exercise Instance
pose_analyses = session_exercise.pose_analyses.all()
print(f"Analyzed {pose_analyses.count()} frames")
```

---

## 📌 Common Query Patterns

### Pattern: Get Recent Data
```python
# Last 7 days of sessions
from datetime import timedelta
week_ago = timezone.now() - timedelta(days=7)
recent = Session.objects.filter(start_time__gte=week_ago)
```

### Pattern: Aggregate Statistics
```python
from django.db.models import Avg, Sum, Count
stats = Session.objects.filter(user=user).aggregate(
    total=Count('id'),
    avg_score=Avg('overall_session_score'),
    total_time=Sum('scheduled_duration_minutes'),
)
```

### Pattern: Select Related (Avoid N+1 Query)
```python
# SLOW: Each exercise triggers a database query
exercises = SessionExercise.objects.all()
for se in exercises:
    print(se.exercise.name)  # Query! ❌

# FAST: Fetch exercise data upfront
exercises = SessionExercise.objects.select_related('exercise')
for se in exercises:
    print(se.exercise.name)  # No query ✓
```

### Pattern: Filter with Exclude
```python
# Get completed sessions (not pending/cancelled)
completed = Session.objects.exclude(
    status__in=['pending', 'cancelled']
)
```

---

**Created**: April 20, 2026
**Physio AI Project**
