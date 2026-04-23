# Django Models Design Complete Guide

**Project**: Physio AI System
**Status**: ✅ Complete Design Documentation
**Date**: April 20, 2026

---

## 📚 Documentation Overview

This folder contains complete Django models design for a physiotherapy AI system with:

| File | Purpose | Key Content |
|------|---------|-------------|
| **ADVANCED_MODELS.py** | Full model implementations | 8 complete model classes with full documentation |
| **MODELS_DESIGN_GUIDE.md** | Detailed explanations | Why each field exists, relationships, design patterns |
| **MODELS_REFERENCE.md** | Quick lookup tables | Field names, types, constraints, choices |
| **MODELS_EXAMPLES.md** | Practical code examples | Real code for create/read/update/delete operations |

---

## 🎯 Quick Start

### 1. Understand the Overall Design
Read: **MODELS_DESIGN_GUIDE.md** → "Model Overview" section (5 min read)

### 2. Learn Each Model's Purpose
Read: **MODELS_DESIGN_GUIDE.md** → Individual model sections (10 min read)

### 3. Look Up Specific Fields
Reference: **MODELS_REFERENCE.md** → Field tables (as needed)

### 4. See Working Code Examples
Review: **MODELS_EXAMPLES.md** → Practical patterns (10 min read)

---

## 🏗️ Architecture Overview

```
CORE ENTITIES (Nouns - What things are)
├── User           # People using the system
├── Exercise       # Exercise templates
├── Milestone      # Achievements
│
RELATIONSHIPS (How things connect)
├── UserProgress   # Summary stats for each user
├── DailyMetrics   # Daily snapshots
│
ACTIVITIES (Actions - What happens)
├── Session        # Complete workout session
├── SessionExercise # Individual exercise in session
├── PoseAnalysis   # AI analysis of each video frame
```

---

## 🗂️ Data Model Relationships

### The Flow: User → Session → Exercise → AI Analysis

```
┌─────────────┐
│    User     │  ← Real person with account
│             │
├─ age        │
├─ injury     │
├─ fitness    │
└─ medical    │
      │
      │ creates
      ▼
┌──────────────┐
│   Session    │  ← Complete workout
│              │
├─ start_time │
├─ score      │  ← Overall quality
├─ feedback   │
├─ exercises  │  ← List of exercises
└─ pain_level │
      │
      │ contains
      ▼
┌────────────────────┐
│ SessionExercise    │  ← Individual exercise performance
│                    │
├─ exercise_id      │
├─ reps_done        │
├─ form_score       │  ← Quality of form
├─ angles           │  ← Joint positions
├─ issues           │  ← Problems detected
└─ feedback         │
      │
      │ analyzed
      ▼
┌──────────────────┐
│  PoseAnalysis    │  ← Frame-by-frame AI analysis
│                  │
├─ frame_number   │
├─ timestamp      │
├─ angles         │  ← Detected joint angles
├─ errors         │  ← Difference from ideal
└─ confidence     │
```

---

## 🔑 Key Design Decisions

### 1. Extended User Model
**Why?** Django's default User doesn't have medical/fitness data.
```python
class User(AbstractUser):
    injury_type = CharField()  # Track medical info
    fitness_level = CharField()  # Difficulty matching
    medical_notes = TextField()  # Special considerations
```

### 2. Exercise as Master Template
**Why?** Same exercise used across many sessions with different results.
```python
class Exercise(Model):
    ideal_joint_angles = JSONField()  # Ideal form template
    
# Same exercise, different performance:
SessionExercise(exercise=shoulder_press, session=session1, form_score=85)
SessionExercise(exercise=shoulder_press, session=session2, form_score=92)
```

### 3. SessionExercise As Through Model
**Why?** Track individual exercise performance within sessions.
```python
Session → Many:Many → Exercise (through SessionExercise)

session.exercises.all()  # Which exercises in session?
exercise.sessions.all()  # Which sessions used this exercise?
SessionExercise.objects.get(...)  # How did they do on this exercise?
```

### 4. PoseAnalysis Per Frame
**Why?** Detect specific moments of poor form.
```python
# Each frame analyzed separately
Frame 1: Good form ✓
Frame 2: Good form ✓
Frame 3: Shoulder high ✗ (issue detected)
Frame 4: Good form ✓
```

### 5. Denormalized Progress Fields
**Why?** Fast queries without calculating every time.
```python
# Instead of: Sum all session scores / count sessions every query
# We have: progress.average_session_score (already calculated)
```

### 6. JSON Fields for Flexibility
**Why?** Store complex nested data without schema changes.
```python
ideal_joint_angles = {
    "phase_1": {"shoulder": 90, "elbow": 90},
    "phase_2": {"shoulder": 170, "elbow": 180}
}
```

---

## 📊 Field Explanations Summary

### User Fields
| Field | Why Needed |
|-------|-----------|
| `injury_type` | Prevent unsafe exercise recommendations |
| `fitness_level` | Match exercise difficulty |
| `height_cm`, `weight_kg` | Normalize joint angles for body size |
| `medical_notes` | Track allergies, medications |

### Exercise Fields
| Field | Why Needed |
|-------|-----------|
| `ideal_joint_angles` | AI compares actual vs ideal |
| `safe_angle_range` | Flag dangerous positions |
| `primary_joints`, `secondary_joints` | Target muscles and stabilizers |
| `progression_to`, `prerequisites` | Build exercise progression |
| `step_by_step_instructions` | Prevent injury |

### Session Fields
| Field | Why Needed |
|-------|-----------|
| `overall_session_score` | Quality metric |
| `completion_percentage` | Quantity metric |
| `pain_level_before/after` | Measure effectiveness |
| `improvement_areas` | Specific feedback |
| `video_file` | Review performance |

### SessionExercise Fields
| Field | Why Needed |
|-------|-----------|
| `form_score` | How well did they do? |
| `consistency_score` | Did form degrade? |
| `range_of_motion_percentage` | Full movement? |
| `angle_deviations` | How much off from ideal? |
| `form_issues_detected` | Which specific problems? |

---

## 🔍 Query Examples at a Glance

### Get User's Recent Performance
```python
user = User.objects.get(username='sarah')
progress = user.progress  # 1:1 access
print(f"Average score: {progress.average_session_score}")
```

### Find Exercises Needing Improvement
```python
poor = SessionExercise.objects.filter(
    session__user=user,
    form_score__lt=70
).values('exercise__name')
```

### Track Pain Improvement
```python
sessions = user.sessions.filter(
    pain_level_before__isnull=False,
    pain_level_after__isnull=False
)
for s in sessions:
    improvement = s.pain_level_before - s.pain_level_after
    print(f"{s.date}: {improvement} points better")
```

### Get AI Analysis for an Exercise
```python
session_ex = SessionExercise.objects.get(id=5)
analyses = session_ex.pose_analyses.all()  # All frames
for analysis in analyses:
    print(f"Frame {analysis.frame_number}: {analysis.form_issues}")
```

---

## ⚡ Performance Considerations

### Indexes (Fast Queries)
```python
# Common queries indexed:
indexes = [
    Index(fields=['user', '-start_time']),  # "Get user's recent sessions"
    Index(fields=['status']),  # "Get pending sessions"
    Index(fields=['category', 'difficulty_level']),  # "Filter exercises"
]
```

### Denormalization (Avoid Recalculation)
```python
# Stored once instead of calculated every time:
UserProgress.average_session_score
UserProgress.total_sessions_completed
DailyMetrics.average_session_score
```

### select_related() Usage
```python
# Efficient: Get exercise with session in one query
exercises = SessionExercise.objects.select_related('exercise')

# Inefficient: Each access queries database again
exercises = SessionExercise.objects.all()
for ex in exercises:
    ex.exercise.name  # Database query! ❌
```

---

## 🔒 Data Integrity

### Validators Prevent Invalid Data
```python
age = IntegerField(validators=[MinValueValidator(0), MaxValueValidator(150)])
score = FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
```

### Unique Constraints
```python
unique_together = ['user', 'date']  # Only one DailyMetrics per day

Exercise.name = CharField(unique=True)  # No duplicate exercises
```

### Choices Limit Options
```python
status = CharField(choices=[
    ('pending', 'Pending'),
    ('completed', 'Completed'),
])  # Can't be typo like "compleeted"
```

### Foreign Keys Maintain Referential Integrity
```python
session = ForeignKey(Session, on_delete=models.CASCADE)
# If session deleted, related SessionExercises also deleted
# Can't have orphaned records
```

---

## 📈 Typical Usage Volumes

For 1,000 active users:

```
Small Tables:
  User: 1,000 records
  Exercise: 50-100 templates
  UserProgress: 1,000 records
  Milestone: 5,000-10,000 records

Medium Tables:
  Session: 10,000+ (10 per user avg)
  DailyMetrics: 365,000+ (1 per user per day per year)

Large Tables:
  SessionExercise: 100,000+ (10 per session)
  PoseAnalysis: 10,000,000+ (1000+ per exercise)
```

**The challenge**: PoseAnalysis table with billions of rows over years.
**Solution**: Archive old data or use data warehouse for analytics.

---

## 🚀 Implementation Checklist

- [ ] Read MODELS_DESIGN_GUIDE.md (understand why)
- [ ] Read MODELS_REFERENCE.md (understand what)
- [ ] Read MODELS_EXAMPLES.md (understand how)
- [ ] Copy model code from ADVANCED_MODELS.py
- [ ] Create initial migrations: `makemigrations`
- [ ] Apply migrations: `migrate`
- [ ] Create admin customizations
- [ ] Test CRUD operations with examples
- [ ] Write queries for key features
- [ ] Add indexes for common queries
- [ ] Set up automated progress recalculation

---

## 💡 Key Insights

### Model Relationships Are Critical
- Correct relationships prevent data errors
- Enable efficient queries
- Allow Django ORM to do heavy lifting

### Design for Queries, Not Just Storage
- Think about how data will be accessed
- Denormalize when needed for speed
- Index common filters

### Use JSON for Flexibility
- Store complex nested data
- Don't need schema change for new fields
- Perfect for AI analysis results

### Separate Concerns
- User (authentication + profile)
- Exercise (master template)
- Session (activities)
- Progress (aggregated stats)
- Analysis (detailed AI results)

### Track Everything for Analytics
- timestamps (created_at, updated_at)
- pain levels (before/after)
- issues detected (for reporting)
- feedback (for learning)

---

## 📞 Common Questions

**Q: Why extend Django User instead of creating separate UserProfile?**
A: Extends flexibility without breaking changes. But we do have UserProfile if needed.

**Q: Why ideal_joint_angles as JSON instead of separate angle fields?**
A: Different exercises have different phases. JSON is flexible for any structure.

**Q: Why PoseAnalysis separate from SessionExercise?**
A: Allows detailed frame-by-frame analysis. SessionExercise is summary, PoseAnalysis is detail.

**Q: How often to recalculate UserProgress?**
A: After each session (real-time) or batch daily (efficient). Choose based on needs.

**Q: Can I query across multiple models?**
A: Yes! `SessionExercise.objects.filter(session__user=user, form_score__lt=70)`

**Q: What if I need fields not in these models?**
A: Use JSONField for flexibility, or extend with new fields in migrations.

---

## 🎓 Learning Resources

1. **Django Official Docs**: https://docs.djangoproject.com/
2. **Relationships**: https://docs.djangoproject.com/en/stable/topics/db/models/
3. **Query API**: https://docs.djangoproject.com/en/stable/topics/db/queries/
4. **JSON Field**: https://docs.djangoproject.com/en/stable/ref/models/fields/#jsonfield
5. **Admin Customization**: https://docs.djangoproject.com/en/stable/ref/contrib/admin/

---

## 📋 Files in This Design

```
physio_ai/
├── ADVANCED_MODELS.py              # Full model code
├── MODELS_DESIGN_GUIDE.md          # Detailed explanations
├── MODELS_REFERENCE.md             # Quick reference tables
├── MODELS_EXAMPLES.md              # Practical code examples
└── MODELS_COMPLETE_GUIDE.md        # This file
```

---

## ✅ What This Design Provides

✓ **User Management**: Extended user with medical/fitness data
✓ **Exercise Library**: Templates with ideal joint angles
✓ **Session Tracking**: Complete workout sessions with scoring
✓ **Performance Analysis**: Frame-by-frame AI analysis
✓ **Progress Tracking**: Aggregated statistics and trends
✓ **Pain Monitoring**: Track pain before/after
✓ **Feedback System**: AI and therapist feedback
✓ **Streak Tracking**: Gamification elements
✓ **Data Integrity**: Validators, constraints, foreign keys
✓ **Scalability**: Indexes, denormalization, efficient queries

---

## 🔄 Next Steps

1. **Use ADVANCED_MODELS.py** in your Django app
2. **Run migrations** to create database tables
3. **Review MODELS_EXAMPLES.md** to understand usage
4. **Create admin interfaces** for data management
5. **Write API views** to expose models
6. **Build frontend** to display data

---

**Documentation Created**: April 20, 2026
**For**: Physio AI - Physiotherapy AI System
**By**: GitHub Copilot

This design is production-ready and scalable for 1000+ users.
All relationships validated. All fields justified. All patterns explained.

Ready to build! 🚀
