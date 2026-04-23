# Personalized Therapy Plan Generation System

> **AI-Powered Physiotherapy Planning** - Generate customized rehabilitation plans using GPT-4 based on injury type and performance history.

## 🎯 Overview

This system creates **intelligent, personalized therapy plans** for physiotherapy patients by:

1. **Analyzing** injury type, severity, and user performance history
2. **Generating** structured weekly exercise plans using GPT-4
3. **Providing** progression strategies, safety precautions, and specific goals
4. **Tracking** user progress and allowing plan adjustments

## ✨ Key Features

### 🤖 AI-Powered Generation
- Uses GPT-4/GPT-3.5-turbo for intelligent plan creation
- Considers injury severity, patient fitness level, and goals
- Generates evidence-based exercise recommendations
- Includes modification options for different ability levels

### 📅 Structured Weekly Plans
- Day-by-day exercise assignments
- Automatic rest days
- Progressive difficulty increases
- Clear exercise descriptions, sets/reps, and duration

### 📊 Comprehensive Data Collection
- **Performance History**: Sessions completed, form scores, current streak
- **User Profile**: Age, fitness level, previous injuries
- **Recent Activity**: Last 2 weeks of exercise data
- All data used to personalize the plan

### 🔄 Full REST API
- Generate, retrieve, update, and delete plans
- Get weekly schedules
- Track and update progress
- Export plans
- Compare multiple plans
- Search and filter capabilities

### 👨‍💼 Admin Interface
- Beautiful Django admin with visual indicators
- Color-coded status badges and progress bars
- Comprehensive filtering and search
- Bulk actions for plan management

### 🛡️ Production Ready
- Error handling and retry logic
- Comprehensive logging
- Database transactions for data integrity
- Performance optimizations and caching
- Thorough API validation

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r THERAPY_PLAN_REQUIREMENTS.txt

# Add to Django settings.py
INSTALLED_APPS = [
    ...
    'therapy_plans',
]
```

### 2. Configuration

```bash
# Set OpenAI API key
export OPENAI_API_KEY="sk-your-api-key-here"

# Run migrations
python manage.py makemigrations therapy_plans
python manage.py migrate
```

### 3. Generate a Plan

```python
from django.contrib.auth.models import User
from therapy_plans.services import generate_therapy_plan

user = User.objects.get(username='john_doe')

plan, message = generate_therapy_plan(
    user=user,
    injury_type="knee pain",
    injury_severity="moderate",
    duration_weeks=4,
    difficulty_level="intermediate",
    goals=["Reduce pain", "Improve mobility", "Return to sports"]
)

if plan:
    print(f"✅ Plan created: {plan.title}")
else:
    print(f"❌ Error: {message}")
```

### 4. Use the API

```bash
# Generate a plan
curl -X POST http://localhost:8000/api/therapy-plans/generate/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "injury_type": "knee pain",
    "injury_severity": "moderate",
    "duration_weeks": 4,
    "goals": ["Reduce pain", "Improve mobility"]
  }'

# Get weekly schedule
curl http://localhost:8000/api/therapy-plans/42/weekly-schedule/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update progress
curl -X POST http://localhost:8000/api/therapy-plans/42/update-progress/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "progress_score": 65.5,
    "status": "active"
  }'
```

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [THERAPY_PLAN_GENERATION.md](THERAPY_PLAN_GENERATION.md) | Complete API reference and guide |
| [THERAPY_PLAN_INTEGRATION.md](THERAPY_PLAN_INTEGRATION.md) | Step-by-step integration instructions |
| [THERAPY_PLAN_EXAMPLES.py](THERAPY_PLAN_EXAMPLES.py) | Real-world usage scenarios |
| [THERAPY_PLAN_SUMMARY.md](THERAPY_PLAN_SUMMARY.md) | Architecture and technical overview |
| [therapy_plan_api_examples.sh](therapy_plan_api_examples.sh) | curl examples for API testing |

## 📚 API Endpoints

### Plan Management
- `POST /api/therapy-plans/generate/` - Create new plan
- `GET /api/therapy-plans/` - List user's plans
- `GET /api/therapy-plans/{id}/` - Get plan details
- `PUT /api/therapy-plans/{id}/` - Update plan
- `DELETE /api/therapy-plans/{id}/` - Archive plan

### Plan Features
- `GET /api/therapy-plans/{id}/weekly-schedule/` - Get weekly exercises
- `POST /api/therapy-plans/{id}/update-progress/` - Track progress
- `GET /api/therapy-plans/{id}/export/` - Export plan
- `GET /api/therapy-plans/{id}/comparison/` - Compare plans

### Filtering & Search
- `GET /api/therapy-plans/active/` - Get active plans
- `GET /api/therapy-plans/completed/` - Get completed plans
- `GET /api/therapy-plans/?search=knee` - Search plans
- `GET /api/therapy-plans/?status=active` - Filter by status

## 🗄️ Database Schema

### TherapyPlan
Main model storing the generated plan

```python
- id (Primary Key)
- user (Foreign Key)
- injury_type (string)
- status (draft/active/completed/archived)
- title, description (text)
- duration_weeks (int)
- difficulty_level (beginner/intermediate/advanced)
- weekly_plan (JSON - structured exercises by week/day)
- goals (JSON - list of therapeutic goals)
- precautions (JSON - list of safety warnings)
- progression_strategy (text)
- progress_score (0-100)
- start_date, end_date (date)
- created_at, updated_at, generated_at (datetime)
```

### WeeklyExercise
Individual exercise assignments

```python
- id (Primary Key)
- therapy_plan (Foreign Key)
- week_number (int)
- day_of_week (monday-sunday)
- exercise_name (string)
- description (text)
- sets, reps (int)
- duration_minutes (int)
- rest_seconds (int)
- modifications (text)
- precautions (text)
- benefits (text)
- is_rest_day (bool)
- order (int)
```

## 🔍 How It Works

```
User provides injury info
        ↓
Collect performance data (sessions, form scores, fitness level)
        ↓
Build comprehensive GPT prompt with all context
        ↓
Call GPT-4 API with structured JSON request
        ↓
Parse and validate JSON response from GPT
        ↓
Save plan to database (atomic transaction)
        ↓
Create WeeklyExercise records for each day
        ↓
Return serialized plan with 201 status
```

## 📊 Data Collection

Automatically collects:
- **Sessions**: Total completed, average form scores
- **Recent Activity**: Last 2 weeks of metrics
- **User Profile**: Age, fitness level, previous injuries
- **Streaks**: Current and longest exercise streaks
- **Exercise Time**: Average daily minutes spent exercising

All data is used to personalize the generated plan.

## 🛠️ Configuration

### Environment Variables
```bash
OPENAI_API_KEY=sk-...           # Required: OpenAI API key
THERAPY_PLAN_MODEL=gpt-4        # Optional: default is gpt-4
DEBUG=False                      # Optional: Django debug mode
LOG_LEVEL=INFO                   # Optional: logging level
```

### Django Settings
```python
INSTALLED_APPS = [
    ...
    'therapy_plans',
]

LOGGING = {
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'therapy_plans.log',
        },
    },
    'loggers': {
        'therapy_plans': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

## 🔐 Security

- ✅ Authentication required for all endpoints
- ✅ Users can only access their own plans
- ✅ Input validation with serializers
- ✅ Proper permission checks
- ✅ Secure API token handling

## 📈 Performance

- Weekly schedules cached for 1 minute
- Database indexes on user + status lookups
- Atomic transactions for data integrity
- Pagination on list endpoints
- Minimal API response times

## 🐛 Troubleshooting

### API Key Issues
```bash
# Set API key
export OPENAI_API_KEY="sk-your-key"

# Or in .env file
OPENAI_API_KEY=sk-your-key
```

### Rate Limiting
- GPT API has rate limits
- Plan generation takes 5-10 seconds
- Consider async task queue for production

### Missing Performance Data
- If user has no history, defaults are used
- Plans still generate with baseline values
- More customization as user data accumulates

See [THERAPY_PLAN_GENERATION.md](THERAPY_PLAN_GENERATION.md#troubleshooting) for detailed troubleshooting.

## 📝 Admin Interface

Access at `/admin/therapy_plans/`:
- View all therapy plans
- Search by username, injury, or title
- Filter by status, difficulty, date
- Color-coded status badges
- Visual progress bars
- Edit plan details
- Bulk actions (complete, archive)

## 🚢 Deployment

### Prerequisites
- OpenAI API key with GPT-4 access
- Django 3.2+ with DRF
- Python 3.8+
- PostgreSQL recommended

### Deployment Checklist
- [ ] Add 'therapy_plans' to INSTALLED_APPS
- [ ] Set OPENAI_API_KEY environment variable
- [ ] Run migrations: `makemigrations` + `migrate`
- [ ] Create superuser: `createsuperuser`
- [ ] Configure cache (Redis recommended)
- [ ] Test API endpoints
- [ ] Set up logging
- [ ] Monitor API usage/costs

## 📚 Example Scenarios

### Scenario 1: Athlete Recovering from Injury
```python
plan, msg = generate_therapy_plan(
    user=athlete,
    injury_type="ACL tear",
    injury_severity="severe",
    duration_weeks=12,
    difficulty_level="intermediate",
    goals=["Return to sport", "Full strength recovery"]
)
```

### Scenario 2: Desk Worker with Shoulder Pain
```python
plan, msg = generate_therapy_plan(
    user=worker,
    injury_type="Rotator cuff strain",
    injury_severity="mild",
    duration_weeks=6,
    difficulty_level="beginner",
    goals=["Reduce pain when typing", "Improve posture"]
)
```

### Scenario 3: Senior with Back Pain
```python
plan, msg = generate_therapy_plan(
    user=senior,
    injury_type="Lower back pain",
    injury_severity="moderate",
    duration_weeks=8,
    difficulty_level="beginner",
    goals=["Reduce pain", "Improve flexibility", "Daily activities"]
)
```

## 🎓 Testing

### Unit Test Example
```python
from django.test import TestCase
from therapy_plans.services import generate_therapy_plan

class TherapyPlanTest(TestCase):
    def test_generate_plan(self):
        plan, msg = generate_therapy_plan(
            user=self.user,
            injury_type="knee pain",
            injury_severity="moderate"
        )
        self.assertIsNotNone(plan)
        self.assertEqual(plan.injury_type, "knee pain")
```

### API Test Example
```python
from rest_framework.test import APITestCase

class TherapyPlanAPITest(APITestCase):
    def test_generate_plan_api(self):
        response = self.client.post('/api/therapy-plans/generate/', {
            'injury_type': 'knee pain',
            'injury_severity': 'moderate'
        })
        self.assertEqual(response.status_code, 201)
```

## 🎯 Future Enhancements

- [ ] PDF export with visual schedules
- [ ] Email notifications for milestones
- [ ] Wearable device integration
- [ ] Machine learning for injury prediction
- [ ] Group therapy plans
- [ ] Video demonstrations
- [ ] Mobile app support
- [ ] Multi-language support

## 📞 Support

For issues or questions:
1. Check [THERAPY_PLAN_GENERATION.md](THERAPY_PLAN_GENERATION.md)
2. Review [THERAPY_PLAN_EXAMPLES.py](THERAPY_PLAN_EXAMPLES.py)
3. Check logs: `therapy_plans.log`
4. Review error responses from API

## 📄 License

Part of PhysioAI project. See project LICENSE for details.

---

**Created**: 2024  
**Last Updated**: April 2026  
**Status**: Production Ready ✅
