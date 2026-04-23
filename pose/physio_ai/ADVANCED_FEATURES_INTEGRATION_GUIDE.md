# Advanced Features Implementation Guide

## Overview

This document provides comprehensive integration instructions for the three advanced AI features added to PhysioAI:

1. **Adaptive Difficulty System** - Intelligently adjust exercise difficulty based on performance trends
2. **Injury Risk Detection** - Monitor joint angles and prevent unsafe positions  
3. **Multi-Exercise Classification** - Enable intelligent exercise matching and recommendations

---

## Installation & Setup

### 1. Add to Django Settings

```python
# settings.py

INSTALLED_APPS = [
    # ... other apps
    'advanced_features',
]
```

### 2. Install Dependencies

```bash
pip install numpy  # For trend analysis calculations
```

### 3. Create Migrations

```bash
python manage.py makemigrations advanced_features
python manage.py migrate advanced_features
```

### 4. Register in Admin

The app includes complete Django admin interfaces. Access via:
- http://localhost:8000/admin/advanced_features/

### 5. Register API Endpoints

```python
# api/urls.py

from rest_framework.routers import DefaultRouter
from api.views_advanced_features import (
    DifficultyAdaptationViewSet,
    InjuryRiskAlertViewSet,
    ExerciseClassificationViewSet,
    UserProgressAnalysisViewSet,
)

router = DefaultRouter()
router.register(r'difficulty-adaptations', DifficultyAdaptationViewSet, basename='difficulty-adaptation')
router.register(r'injury-risks', InjuryRiskAlertViewSet, basename='injury-risk')
router.register(r'exercise-classification', ExerciseClassificationViewSet, basename='exercise-classification')
router.register(r'progress', UserProgressAnalysisViewSet, basename='user-progress')

urlpatterns = [
    # ... other patterns
    path('api/', include(router.urls)),
]
```

---

## Feature 1: Adaptive Difficulty System

### Purpose
Automatically recommend and apply exercise difficulty adjustments based on performance trends.

### Key Concepts

**Performance Metrics:**
- Form scores collected from each session (0-100 range)
- Consistency score (lower variation = higher consistency)
- Trend slope (points improved per session)

**Recommendation Types:**
- `increase` - User ready for harder difficulty (avg_score ≥ 85, improving trend)
- `maintain` - Continue current difficulty (avg_score ≥ 80, consistent)
- `decrease` - User struggling (avg_score < 60, declining trend)
- `modify` - Plateaued, suggest variation (stable performance, avg_score ≥ 75)

### Integration Steps

#### Step 1: Set User Preferences

```python
from advanced_features.models import UserDifficultyPreference
from django.contrib.auth.models import User

user = User.objects.get(username='john_doe')

# Auto-created on first access, but can customize
preference = UserDifficultyPreference.objects.get(user=user)
preference.progression_strategy = 'adaptive'  # or 'conservative', 'moderate', 'aggressive'
preference.min_score_threshold = 75.0  # Score needed for recommendations
preference.auto_adapt_enabled = True   # Auto-change difficulty
preference.sessions_before_review = 5  # Analyze every N sessions
preference.save()
```

#### Step 2: Analyze Exercise Performance

```python
from advanced_features.services import AdaptiveDifficultySystem
from exercises.models import Exercise

user = User.objects.get(username='john_doe')
exercise = Exercise.objects.get(name='Bodyweight Squat')

difficulty_system = AdaptiveDifficultySystem(user)
analysis = difficulty_system.analyze_exercise(exercise)

# Analysis structure:
{
    'exercise_id': 5,
    'exercise_name': 'Bodyweight Squat',
    'current_difficulty': 'medium',
    'metrics': {
        'average_score': 86.5,
        'consistency_score': 87.3,
        'sessions_count': 10,
    },
    'trend': {
        'trend': 'improving',
        'slope': 2.3,        # Points per session
        'confidence': 92.5,  # R-squared percentage
    },
    'recommendation': {
        'type': 'increase',
        'difficulty': 'hard',
        'reason': 'Excellent performance with improving trend',
        'confidence': 92.5,
    }
}
```

#### Step 3: Apply Recommendation

**Option A: Auto-Apply (if enabled)**
```python
new_difficulty = difficulty_system.auto_adapt_if_needed(exercise)
if new_difficulty:
    print(f"Difficulty auto-adapted to: {new_difficulty}")
```

**Option B: Manual Apply (via API)**
```bash
# Using curl or any HTTP client
POST /api/difficulty-adaptations/{adaptation_id}/apply_recommendation/

# Response:
{
    "exercise_id": 5,
    "exercise_name": "Bodyweight Squat",
    "old_difficulty": "medium",
    "new_difficulty": "hard",
    "reason": "Excellent performance with improving trend"
}
```

#### Step 4: Monitor Trends

```bash
# Get exercises ready for progression
GET /api/difficulty-adaptations/ready_for_progression/

# Get exercises with declining performance
GET /api/difficulty-adaptations/trending_down/

# Get specific adaptation details
GET /api/difficulty-adaptations/{id}/
```

---

## Feature 2: Injury Risk Detection

### Purpose
Real-time monitoring of joint positions to prevent unsafe movements.

### Key Concepts

**Safe Angle Ranges:**
- Each joint has defined safe ranges (e.g., knee flexion: 0-120°)
- Ranges vary by exercise type and user condition
- Conservative ranges for post-injury recovery

**Risk Levels:**
- `critical` - Exceeded by >15° - STOP exercise immediately
- `high` - Exceeded by 5-15° - Reduce range of motion
- `medium` - Exceeded by <5° - Monitor and correct form
- `low` - Minor deviation - Informational only

### Integration Steps

#### Step 1: Define Joint Safety Profiles

```python
from advanced_features.models import JointSafetyProfile

# Define safe ranges for knee in squatting
JointSafetyProfile.objects.create(
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
```

#### Step 2: Analyze Poses During Session

```python
from advanced_features.services import InjuryRiskDetectionSystem
from ai_engine.models import PoseAnalysis

user = User.objects.get(username='john_doe')
pose_analysis = PoseAnalysis.objects.latest('id')
session_exercise = pose_analysis.session_exercise

risk_system = InjuryRiskDetectionSystem(user)
alerts = risk_system.analyze_pose(pose_analysis, session_exercise)

# Each alert contains:
for alert in alerts:
    # alert['joint_name']
    # alert['current_angle']
    # alert['safe_min']
    # alert['safe_max']
    # alert['exceeded_by']
    # alert['risk_level']  # critical, high, medium, low
    
    # Create database record
    risk_system.create_risk_alert(alert, pose_analysis, session_exercise)
```

#### Step 3: Monitor Alerts via API

```bash
# Get all alerts for user
GET /api/injury-risks/

# Get unresolved alerts
GET /api/injury-risks/active/

# Get critical alerts
GET /api/injury-risks/critical/

# Get summary
GET /api/injury-risks/summary/
# Response:
{
    "total_alerts": 15,
    "active_alerts": 3,
    "critical": 1,
    "high": 2,
    "medium": 0,
    "low": 0
}
```

#### Step 4: Acknowledge & Resolve

```bash
# Acknowledge alert (user saw it)
POST /api/injury-risks/{alert_id}/acknowledge/

# Resolve alert (issue corrected)
POST /api/injury-risks/{alert_id}/resolve/
{
    "notes": "User corrected form and repeated successfully"
}
```

---

## Feature 3: Multi-Exercise Classification

### Purpose
Enable intelligent exercise recommendations and substitutions based on multi-dimensional similarity.

### Key Concepts

**Classification Dimensions:**
1. Movement Pattern (bilateral, unilateral, rotation)
2. Equipment (bodyweight, band, dumbbells, machine)
3. Intensity (isometric, dynamic, explosive)
4. Plane of Motion (sagittal, frontal, transverse)
5. Primary Joint (knee, shoulder, hip, spine)
6. Stabilization (yes/no)
7. Complexity Level (simple, intermediate, complex)
8. Recovery Focus (ROM, strength, mobility, endurance)

**Similarity Matching:**
- Each classification weighted by importance (0-1)
- Similarity score = matched_weight / total_weight
- Results sorted by score (0-1 range)

### Integration Steps

#### Step 1: Create Exercise Classifications

```python
from advanced_features.models import ExerciseClassification
from exercises.models import Exercise

exercise = Exercise.objects.get(name='Bodyweight Squat')

ExerciseClassification.objects.create(
    exercise=exercise,
    classification_type='movement_pattern',
    classification_value='bilateral',
    weight=1.0,  # High importance
)

ExerciseClassification.objects.create(
    exercise=exercise,
    classification_type='primary_joint',
    classification_value='knee',
    weight=1.0,
)

ExerciseClassification.objects.create(
    exercise=exercise,
    classification_type='recovery_focus',
    classification_value='strength',
    weight=0.8,  # Medium importance
)
```

#### Step 2: Get Exercise Profile

```python
from advanced_features.services import ExerciseClassificationSystem

exercise = Exercise.objects.get(name='Bodyweight Squat')

profile = ExerciseClassificationSystem.get_exercise_profile(exercise)

# Profile includes:
# - All classifications
# - Similar exercises with similarity scores
# - Difficulty level, muscle groups, etc.
```

#### Step 3: Find Similar Exercises

```bash
# Get exercises similar to Bodyweight Squat
GET /api/exercise-classification/exercise/5/similar/?threshold=0.7&limit=5

# Response:
{
    "source_exercise": {
        "id": 5,
        "name": "Bodyweight Squat"
    },
    "similar_exercises": [
        {
            "id": 8,
            "name": "Goblet Squat",
            "similarity_score": 0.98,
            "difficulty": "medium"
        },
        {
            "id": 12,
            "name": "Smith Machine Squat",
            "similarity_score": 0.85,
            "difficulty": "easy"
        }
    ]
}
```

#### Step 4: Get Goal-Based Recommendations

```bash
# Recommend strength exercises at medium difficulty
GET /api/exercise-classification/recommendations/?goal=strength&difficulty=medium&limit=5

# Response:
{
    "goal": "strength",
    "difficulty": "medium",
    "recommendations": [
        {
            "id": 5,
            "name": "Bodyweight Squat",
            "description": "Basic squat using body weight",
            "muscle_groups": "quadriceps,glutes,hamstrings"
        },
        ...
    ]
}
```

---

## Complete Workflow Example

### Session Completion Workflow

When a user completes an exercise session:

```python
from advanced_features.services import (
    AdaptiveDifficultySystem,
    InjuryRiskDetectionSystem,
)

user = User.objects.get(username='john_doe')
exercise = Exercise.objects.get(name='Bodyweight Squat')

# 1. Check for safety issues
risk_system = InjuryRiskDetectionSystem(user)
pose_analysis = PoseAnalysis.objects.latest('id')
session_exercise = pose_analysis.session_exercise

alerts = risk_system.analyze_pose(pose_analysis, session_exercise)
for alert in alerts:
    risk_system.create_risk_alert(alert, pose_analysis, session_exercise)

if alerts and any(a['risk_level'] == 'critical' for a in alerts):
    # Send critical alert notification
    notify_user_critical_risk(user)

# 2. Analyze performance trend
difficulty_system = AdaptiveDifficultySystem(user)
analysis = difficulty_system.analyze_exercise(exercise)

# 3. Check if auto-adapt needed
if analysis['recommendation']['type'] in ['increase', 'decrease']:
    new_difficulty = difficulty_system.auto_adapt_if_needed(exercise)

# 4. Prepare recommendations for therapy plan
if analysis['recommendation']['type'] == 'increase':
    similar = ExerciseClassificationSystem.find_similar_exercises(
        exercise,
        similarity_threshold=0.7
    )
    suggest_progression(user, exercise, similar)
```

---

## API Endpoints Reference

### Difficulty Adaptations
```
GET    /api/difficulty-adaptations/
GET    /api/difficulty-adaptations/{id}/
POST   /api/difficulty-adaptations/analyze/
POST   /api/difficulty-adaptations/{id}/apply_recommendation/
GET    /api/difficulty-adaptations/trending_down/
GET    /api/difficulty-adaptations/ready_for_progression/
```

### Injury Risk Alerts
```
GET    /api/injury-risks/
GET    /api/injury-risks/{id}/
GET    /api/injury-risks/active/
GET    /api/injury-risks/critical/
GET    /api/injury-risks/summary/
POST   /api/injury-risks/{id}/acknowledge/
POST   /api/injury-risks/{id}/resolve/
```

### Exercise Classification
```
GET    /api/exercise-classification/exercise/{id}/profile/
GET    /api/exercise-classification/exercise/{id}/similar/
GET    /api/exercise-classification/recommendations/
```

### User Progress
```
GET    /api/progress/analysis/
```

---

## Admin Interface

Access Django admin at `/admin/advanced_features/` to:

- **View & manage difficulty adaptations** - See trends and recommendations
- **Monitor injury alerts** - Track safety issues
- **Define joint safety profiles** - Configure safe angle ranges
- **Create exercise classifications** - Define exercise dimensions
- **Configure user preferences** - Customize difficulty progression

### Admin Features

- Color-coded trend badges (↗ improving, → stable, ↘ declining)
- Severity scores with visual indicators
- Bulk actions (acknowledge, resolve, mark unresolved)
- Search and filtering by user, exercise, date
- Read-only analysis fields to prevent data corruption

---

## Testing

### Unit Tests

```python
# test_advanced_features.py

from django.test import TestCase
from advanced_features.services import AdaptiveDifficultySystem
from exercises.models import Exercise

class AdaptiveDifficultyTestCase(TestCase):
    def test_trend_analysis(self):
        # Test with synthetic scores
        scores = [70, 72, 75, 78, 82]  # Improving trend
        trend = self._analyze_trend(scores)
        self.assertGreater(trend['slope'], 0)
        self.assertEqual(trend['trend'], 'improving')
    
    def test_consistency_calculation(self):
        # Test consistency calculation
        high_consistency = [80, 81, 80, 82, 79]  # Consistent
        low_consistency = [70, 90, 60, 100, 55]  # Inconsistent
        
        # Should differ significantly
        self.assertGreater(
            self._calculate_consistency(high_consistency),
            self._calculate_consistency(low_consistency)
        )
```

### Integration Tests

```bash
# Test complete workflow
python manage.py test advanced_features.tests.IntegrationTests

# Test API endpoints
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/difficulty-adaptations/
```

---

## Performance Optimization

### Caching

```python
from django.core.cache import cache

# Cache safety profiles (rarely change)
def get_safety_profile(joint_name, exercise_type):
    cache_key = f'safety_profile:{joint_name}:{exercise_type}'
    profile = cache.get(cache_key)
    if profile is None:
        profile = JointSafetyProfile.objects.get(
            joint_name=joint_name,
            exercise_type=exercise_type
        )
        cache.set(cache_key, profile, 3600)  # 1 hour
    return profile
```

### Database Indexes

```python
# Already configured in models, but verify:
# - DifficultyAdaptation: (user, exercise)
# - InjuryRiskAlert: (user, -detected_at), (risk_level), (is_resolved)
# - ExerciseClassification: (exercise), (classification_type)
```

### Batch Processing

```python
# Analyze all user exercises asynchronously
from celery import shared_task

@shared_task
def analyze_all_user_exercises(user_id):
    """Analyze all exercises for user (run weekly)"""
    user = User.objects.get(id=user_id)
    difficulty_system = AdaptiveDifficultySystem(user)
    
    for exercise in Exercise.objects.filter(is_active=True):
        difficulty_system.analyze_exercise(exercise)
```

---

## Troubleshooting

### Issue: No recommendations generated
**Solution:** Ensure user has at least 10 form scores recorded
```python
SessionExercise.objects.filter(user=user, exercise=exercise).count()
# Should be >= 10
```

### Issue: Injury alerts not created
**Solution:** Verify JointSafetyProfile exists for the joint
```python
JointSafetyProfile.objects.filter(joint_name='left_knee').count()
# Should be > 0
```

### Issue: Classification similarity always 0
**Solution:** Ensure exercises have matching classifications
```python
ExerciseClassification.objects.filter(exercise=exercise).count()
# Should be > 0
```

---

## Data Migration

If adding to existing PhysioAI installation:

```bash
# 1. Install app
pip install advanced-features

# 2. Add to settings
INSTALLED_APPS += ['advanced_features']

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Create safety profiles (if using injury detection)
python manage.py shell
exec(open('advanced_features/examples.py').read())
setup_joint_safety_profiles()

# 5. Create user preferences (auto-created on first use)
# OR manually:
from advanced_features.models import UserDifficultyPreference
for user in User.objects.all():
    UserDifficultyPreference.objects.get_or_create(user=user)
```

---

## Support & Documentation

- See `ADVANCED_FEATURES_EXPLANATION.py` for detailed feature logic
- See `advanced_features/examples.py` for code samples
- Check Django admin interface for data inspection
- Review API responses for detailed field documentation

---

## License

These advanced features are part of PhysioAI and follow the same license terms.
