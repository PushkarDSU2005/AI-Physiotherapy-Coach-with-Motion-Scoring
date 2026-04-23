# Therapy Plan Generation with GPT

## Overview

The Therapy Plan Generator creates personalized physiotherapy plans using GPT-4/3.5-turbo AI. It analyzes:
- **Injury type and severity**
- **User performance history** (past sessions, form scores, fitness level)
- **User preferences** (specific goals, fitness level)

It generates a **structured weekly plan** with:
- Day-by-day exercise assignments
- Rest days
- Progressively increasing difficulty
- Safety precautions
- Exercise modifications

## Architecture

### Components

#### 1. **Models** (`therapy_plans/models.py`)
- **TherapyPlan**: Main model storing the plan metadata and weekly structure
- **WeeklyExercise**: Individual exercise assignments for each day of each week

#### 2. **Service Layer** (`therapy_plans/services.py`)
- **TherapyPlanGenerator**: Core class that orchestrates plan generation
- **generate_therapy_plan()**: Convenience function for generating plans

#### 3. **API Layer** (`api/`)
- **TherapyPlanViewSet**: REST endpoints for CRUD operations
- **WeeklyExerciseViewSet**: Endpoints for exercise details
- Serializers for request/response validation

#### 4. **Integration**
- Admin interface for manual plan management
- Signals for cache invalidation
- Comprehensive logging

## Usage

### Basic Usage (Function Call)

```python
from django.contrib.auth.models import User
from therapy_plans.services import generate_therapy_plan

# Get user
user = User.objects.get(username='john_doe')

# Generate plan
plan, message = generate_therapy_plan(
    user=user,
    injury_type="knee pain",
    injury_severity="moderate",
    duration_weeks=4,
    difficulty_level="intermediate",
    goals=["Reduce pain", "Improve mobility", "Return to sports"]
)

if plan:
    print(f"✓ Plan created: {plan.title}")
    print(f"  ID: {plan.id}")
    print(f"  Duration: {plan.duration_weeks} weeks")
else:
    print(f"✗ Error: {message}")
```

### API Endpoints

#### 1. **Generate a Therapy Plan**

```bash
POST /api/therapy-plans/generate/

Request Body:
{
    "injury_type": "knee pain",
    "injury_severity": "moderate",
    "duration_weeks": 4,
    "difficulty_level": "intermediate",
    "goals": ["Reduce pain", "Improve mobility", "Return to sports"]
}

Response (201 Created):
{
    "id": 42,
    "user_username": "john_doe",
    "injury_type": "knee pain",
    "status": "active",
    "title": "Personalized knee pain Recovery Plan",
    "description": "A progressive rehabilitation program...",
    "duration_weeks": 4,
    "difficulty_level": "intermediate",
    "weekly_plan": { ... },
    "goals": ["Reduce pain", "Improve mobility", "Return to sports"],
    "precautions": ["Avoid high-impact activities", ...],
    "progression_strategy": "Week 1-2: Build foundation...",
    "exercise_assignments": [...],
    "start_date": "2024-01-15",
    "end_date": "2024-02-12",
    "progress_score": 0.0,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

#### 2. **Get Weekly Schedule**

```bash
GET /api/therapy-plans/42/weekly-schedule/

Response:
{
    "plan_id": 42,
    "injury_type": "knee pain",
    "title": "Personalized knee pain Recovery Plan",
    "total_weeks": 4,
    "weeks": [
        {
            "week": 1,
            "schedule": {
                "monday": [
                    {
                        "id": 123,
                        "name": "Quadriceps Stretch",
                        "sets": 3,
                        "reps": 15,
                        "duration_minutes": 1,
                        "rest_seconds": 60,
                        "description": "Gentle quadriceps stretching...",
                        "modifications": "Can be done against a wall...",
                        "precautions": "Do not force the stretch",
                        "benefits": "Improves knee flexibility",
                        "is_rest_day": false
                    }
                ],
                "tuesday": [
                    {
                        "name": "Rest Day",
                        "is_rest_day": true
                    }
                ],
                ...
            },
            "notes": "Focus on gentle movements to build baseline mobility"
        },
        ...
    ]
}
```

#### 3. **Update Progress**

```bash
POST /api/therapy-plans/42/update-progress/

Request Body:
{
    "progress_score": 65.5,
    "status": "active",
    "notes": "Pain reduced by 30%, able to walk without limp"
}

Response (200 OK):
{
    "id": 42,
    ...
    "progress_score": 65.5,
    "status": "active",
    ...
}
```

#### 4. **List User's Plans**

```bash
GET /api/therapy-plans/

Query Parameters:
- status: active, completed, draft, archived
- ordering: -created_at (default), progress_score
- search: injury_type

Response (200 OK):
[
    {
        "id": 42,
        "user_username": "john_doe",
        "injury_type": "knee pain",
        "title": "Personalized knee pain Recovery Plan",
        "status": "active",
        "duration_weeks": 4,
        "difficulty_level": "intermediate",
        "progress_score": 65.5,
        "start_date": "2024-01-15",
        "end_date": "2024-02-12",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-18T15:45:00Z"
    }
]
```

#### 5. **Get Active Plans**

```bash
GET /api/therapy-plans/active/

Response (200 OK):
[
    { ... plan data ... }
]
```

#### 6. **Export Plan**

```bash
GET /api/therapy-plans/42/export/?format=json

Response:
{
    "id": 42,
    ...full plan data...
}
```

#### 7. **Compare Plans**

```bash
GET /api/therapy-plans/42/comparison/?compare_with=43

Response:
{
    "current_plan": {
        "id": 42,
        "title": "Personalized knee pain Recovery Plan",
        "injury_type": "knee pain",
        "duration_weeks": 4,
        "difficulty_level": "intermediate",
        "progress_score": 65.5,
        "goals_count": 3
    },
    "compare_plan": {
        "id": 43,
        ...
    },
    "differences": {
        "duration_diff": 0,
        "progress_diff": 15.5,
        "goals_diff": 0
    }
}
```

## Plan Generation Process

### Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ 1. API Request (injury_type, severity, goals, etc)     │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Collect User Performance Data                        │
│   - Sessions completed                                  │
│   - Average form score                                  │
│   - Fitness level                                       │
│   - Previous injuries                                   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Build GPT Prompt with All Context                    │
│   - Injury info                                         │
│   - User performance                                    │
│   - Goals & preferences                                 │
│   - Required output format (JSON)                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Call GPT-4 API                                       │
│   - Model: gpt-4 or gpt-3.5-turbo                       │
│   - Response format: JSON                               │
│   - Max tokens: 4000                                    │
│   - Temperature: 0.7                                    │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 5. Parse GPT Response                                   │
│   - Validate JSON format                                │
│   - Validate required fields                            │
│   - Handle errors gracefully                            │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 6. Save to Database (Atomic Transaction)                │
│   - Create TherapyPlan record                           │
│   - Create WeeklyExercise records                       │
│   - Link to existing Exercise models where possible     │
│   - Store metadata & performance data                   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 7. Return Plan to User                                  │
│   - Serialize full plan data                            │
│   - Status: 201 Created                                 │
└─────────────────────────────────────────────────────────┘
```

## Performance Data Collected

The system automatically collects and analyzes:

```python
{
    'total_sessions_completed': int,        # Total sessions user completed
    'average_form_score': float,            # Overall average form quality (0-100)
    'average_form_score_recent': float,     # Last 2 weeks average
    'current_streak_days': int,             # Current consecutive exercise days
    'fitness_level': str,                   # 'beginner', 'intermediate', 'advanced'
    'age': int,                             # User's age
    'previous_injuries': str,               # Injury history from profile
    'average_daily_minutes': float,         # Avg exercise time per day
    'data_collection_date': str,            # ISO timestamp
}
```

## Weekly Plan Structure

The generated plan follows this JSON structure:

```json
{
  "weekly_plan": {
    "week_1": {
      "monday": [
        {
          "name": "Exercise Name",
          "sets": 3,
          "reps": 10,
          "description": "How to perform...",
          "modifications": "Easier or harder versions",
          "precautions": "Important warnings",
          "benefits": "Why this exercise",
          "duration": 1
        }
      ],
      "tuesday": [
        {
          "name": "Rest Day",
          "is_rest": true
        }
      ],
      "wednesday": [
        { ... exercise ... }
      ],
      ...
      "notes": "Week-specific guidance"
    },
    "week_2": { ... },
    ...
  }
}
```

## Configuration

### Environment Variables

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-xxxxxxxx...

# Optional: Specify model (default: gpt-4)
THERAPY_PLAN_MODEL=gpt-4  # or gpt-3.5-turbo

# Optional: Logging level (default: INFO)
LOG_LEVEL=INFO
```

### Django Settings

```python
# settings.py

INSTALLED_APPS = [
    ...
    'therapy_plans',
    ...
]

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'therapy_plans.log',
        },
    },
    'loggers': {
        'therapy_plans': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Error Handling

### Common Errors and Solutions

#### 1. **OpenAI API Key Error**

```
Error: GPT API authentication failed - check API key
```

**Solution:**
```bash
# Ensure environment variable is set
export OPENAI_API_KEY="sk-..."

# Or in Django settings:
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
```

#### 2. **Rate Limit Error**

```
Error: GPT API rate limit exceeded
```

**Solution:**
- Implement retry logic with exponential backoff
- Use OpenAI's usage metrics to monitor API calls
- Consider upgrading API plan

#### 3. **Invalid JSON Response**

```
Error: Failed to parse GPT response as JSON
```

**Solution:**
- GPT sometimes returns malformed JSON
- Automatically logged with `logger.error()`
- Retry generation or adjust prompt

## Testing

### Unit Test Example

```python
from django.test import TestCase
from django.contrib.auth.models import User
from therapy_plans.services import generate_therapy_plan

class TherapyPlanGenerationTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_generate_therapy_plan(self):
        plan, message = generate_therapy_plan(
            user=self.user,
            injury_type="knee pain",
            injury_severity="moderate",
            duration_weeks=2,
        )
        
        self.assertIsNotNone(plan)
        self.assertEqual(plan.injury_type, "knee pain")
        self.assertEqual(plan.duration_weeks, 2)
        self.assertEqual(plan.user, self.user)
        self.assertEqual(plan.status, 'active')
```

### API Test Example

```python
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class TherapyPlanAPITest(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_generate_plan_via_api(self):
        response = self.client.post('/api/therapy-plans/generate/', {
            'injury_type': 'knee pain',
            'injury_severity': 'moderate',
            'duration_weeks': 4,
            'goals': ['Reduce pain', 'Improve mobility']
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['injury_type'], 'knee pain')
```

## Admin Interface Features

- **List View**: View all plans with status badges and progress bars
- **Search**: Search by username, injury type, or title
- **Filter**: Filter by status, difficulty level, creation date
- **Actions**: Mark as completed, mark as active, archive plans
- **Detailed View**: Edit all plan fields including JSON structures

## Logging

All events are logged to help debug issues:

```
therapy_plans.log:

2024-01-15 10:30:00 - INFO - Generating therapy plan for user john_doe: injury=knee pain, severity=moderate
2024-01-15 10:30:05 - INFO - Successfully received response from GPT API
2024-01-15 10:30:06 - INFO - Saved therapy plan 42
2024-01-15 10:30:06 - INFO - Created 84 weekly exercise records
```

## Performance Optimization

1. **Caching**: Weekly schedules are cached for 1 minute
2. **Database**: Indexed queries for user + status lookups
3. **Pagination**: ListViewSet automatically paginates results
4. **Atomic Transactions**: Plan creation is atomic (all-or-nothing)

## Future Enhancements

- [ ] PDF export with visual schedules
- [ ] Email notifications for plan milestones
- [ ] Integration with wearables for real-time feedback
- [ ] Machine learning model for injury risk prediction
- [ ] Group therapy plan recommendations
- [ ] Multi-language support
- [ ] Video demonstrations of exercises
- [ ] Progress tracking with milestones

## Support & Troubleshooting

For issues or questions:
1. Check logs: `therapy_plans.log`
2. Review error messages in API responses
3. Ensure OpenAI API key is valid
4. Verify user has performance history (otherwise defaults are used)
