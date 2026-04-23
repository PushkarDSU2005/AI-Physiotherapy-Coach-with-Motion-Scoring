# API Quick Reference

**Physio AI REST API**
**Date**: April 20, 2026

---

## 📁 API Files Created

```
physio_ai/
├── requirements.txt                  ← Updated with DRF
├── api/                              ← NEW
│   ├── __init__.py                  ← Package init
│   ├── serializers.py               ← Data validation (1,100 lines)
│   ├── views.py                     ← Endpoints (1,200 lines)
│   └── urls.py                      ← Routing (80 lines)
├── API_DOCUMENTATION.md             ← Full reference (650 lines)
├── API_INTEGRATION_GUIDE.md         ← Setup guide (450 lines)
├── API_CLIENT_EXAMPLES.md           ← Client libs (500 lines)
├── API_SUMMARY.md                   ← This summary (300+ lines)
└── API_QUICK_REFERENCE.md           ← Quick lookup (this file)
```

---

## 🚀 Get Started in 5 Minutes

### 1. Install
```bash
pip install -r requirements.txt
# Or: pip install djangorestframework==3.14.0 django-cors-headers==4.0.0
```

### 2. Configure (settings.py)
```python
INSTALLED_APPS += [
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'api',
]

MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware'] + MIDDLEWARE

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

CORS_ALLOWED_ORIGINS = ['http://localhost:3000', 'http://localhost:8000']
```

### 3. Include URLs (urls.py)
```python
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('api-token-auth/', obtain_auth_token),
    path('api/', include('api.urls')),
]
```

### 4. Create User & Token
```bash
python manage.py shell
```
```python
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()
u = User.objects.create_user('sarah', 'sarah@example.com', 'pass')
t = Token.objects.create(user=u)
print(t.key)  # Save this!
```

### 5. Test
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/progress/current/
```

---

## 🔑 API Token

**Get Token**:
```bash
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"sarah","password":"pass"}'
```

**Use Token**:
```bash
curl -H "Authorization: Token abc123..." \
  http://localhost:8000/api/endpoint/
```

**Python**:
```python
headers = {"Authorization": "Token abc123..."}
requests.get("http://localhost:8000/api/progress/current/", headers=headers)
```

---

## 📍 All Endpoints

### Sessions
```
POST   /api/sessions/start/              Start new session
GET    /api/sessions/active/             Get active session  
GET    /api/sessions/history/            Get completed sessions
```

### Pose Analysis
```
POST   /api/pose/submit/                 Submit joint angles
```

### Scoring
```
POST   /api/score/calculate/             Calculate form score
```

### Feedback
```
GET    /api/feedback/session/            Get AI feedback
```

### Progress
```
GET    /api/progress/current/            Current metrics
GET    /api/progress/history/            Historical data
GET    /api/progress/exercise/           Exercise progress
```

---

## 📨 Common Requests

### Start Session
```bash
curl -X POST http://localhost:8000/api/sessions/start/ \
  -H "Authorization: Token TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Shoulder Work",
    "pain_level_before": 4,
    "scheduled_duration_minutes": 30
  }'
```

### Submit Pose
```bash
curl -X POST http://localhost:8000/api/pose/submit/ \
  -H "Authorization: Token TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_exercise_id": 1,
    "frame_number": 5,
    "timestamp_seconds": 2.5,
    "detected_joint_angles": {"shoulder": 92.5, "elbow": 178.2},
    "pose_detection_confidence": 94.5
  }'
```

### Calculate Score
```bash
curl -X POST http://localhost:8000/api/score/calculate/ \
  -H "Authorization: Token TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_exercise_id": 1}'
```

### Get Feedback
```bash
curl -X GET "http://localhost:8000/api/feedback/session/?session_id=1" \
  -H "Authorization: Token TOKEN"
```

### Get Progress
```bash
curl -X GET http://localhost:8000/api/progress/current/ \
  -H "Authorization: Token TOKEN"
```

### Get History
```bash
curl -X GET "http://localhost:8000/api/progress/history/?days=30" \
  -H "Authorization: Token TOKEN"
```

### Get Exercise Progress
```bash
curl -X GET "http://localhost:8000/api/progress/exercise/?exercise_id=5" \
  -H "Authorization: Token TOKEN"
```

---

## 📋 Request/Response Examples

### Session Start
**Request**:
```json
{
  "title": "Shoulder Strengthening",
  "pain_level_before": 4,
  "description": "Focus on stability",
  "scheduled_duration_minutes": 30
}
```

**Response** (201):
```json
{
  "status": "success",
  "session_id": 42,
  "data": {
    "id": 42,
    "title": "Shoulder Strengthening",
    "start_time": "2026-04-20T14:30:00Z",
    "status": "in_progress",
    "exercises": [],
    "pain_level_before": 4
  }
}
```

### Score Calculation
**Response**:
```json
{
  "status": "success",
  "data": {
    "form_score": 85.5,
    "consistency_score": 82.0,
    "range_of_motion_percentage": 92.0,
    "overall_exercise_score": 85.3,
    "form_issues": [
      {"frame": 3, "joint": "shoulder", "deviation": 12.5}
    ],
    "recommendations": [
      "Focus on maintaining proper joint alignment"
    ]
  }
}
```

### Progress
**Response**:
```json
{
  "status": "success",
  "data": {
    "total_sessions_completed": 42,
    "average_session_score": 82.5,
    "current_streak_days": 5,
    "pain_improvement_percentage": 46.2,
    "sessions_this_week": 4,
    "average_score_this_week": 84.1
  }
}
```

---

## ⚠️ Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Missing/invalid token | Add `-H "Authorization: Token XXX"` |
| 404 Not Found | Wrong URL or resource missing | Check endpoint URL and ID |
| 400 Bad Request | Invalid data format | Check JSON structure |
| 429 Too Many Requests | Rate limit exceeded | Wait before retrying |
| 500 Server Error | Server problem | Check server logs |

---

## 🐍 Python Quick Example

```python
import requests

TOKEN = "YOUR_TOKEN_HERE"
BASE_URL = "http://localhost:8000/api"
headers = {"Authorization": f"Token {TOKEN}"}

# Start session
resp = requests.post(
    f"{BASE_URL}/sessions/start/",
    headers=headers,
    json={"title": "Work", "pain_level_before": 4}
)
session_id = resp.json()["session_id"]

# Submit pose
for frame in range(10):
    requests.post(
        f"{BASE_URL}/pose/submit/",
        headers=headers,
        json={
            "session_exercise_id": 1,
            "frame_number": frame,
            "timestamp_seconds": frame * 0.1,
            "detected_joint_angles": {"shoulder": 90 + frame},
            "pose_detection_confidence": 94.5
        }
    )

# Calculate score
resp = requests.post(
    f"{BASE_URL}/score/calculate/",
    headers=headers,
    json={"session_exercise_id": 1}
)
score = resp.json()["data"]["form_score"]
print(f"Form score: {score}")

# Get feedback
resp = requests.get(
    f"{BASE_URL}/feedback/session/",
    headers=headers,
    params={"session_id": session_id}
)
feedback = resp.json()["data"]["ai_feedback"]
print(f"Feedback: {feedback}")

# Check progress
resp = requests.get(
    f"{BASE_URL}/progress/current/",
    headers=headers
)
progress = resp.json()["data"]
print(f"Sessions: {progress['total_sessions_completed']}")
```

---

## 📚 Documentation Files

| File | Purpose | Read Time |
|------|---------|-----------|
| API_DOCUMENTATION.md | Complete endpoint reference | 20 min |
| API_INTEGRATION_GUIDE.md | Setup instructions | 15 min |
| API_CLIENT_EXAMPLES.md | Code examples | 10 min |
| API_SUMMARY.md | Overview | 5 min |
| API_QUICK_REFERENCE.md | This file | 2 min |

**Start with**: API_INTEGRATION_GUIDE.md for setup

---

## ✅ Setup Verification

```bash
# 1. Check DRF installed
python -c "import rest_framework; print('✓ DRF')"

# 2. Check settings updated
python manage.py shell -c "from django.conf import settings; print('✓ REST_FRAMEWORK' if 'rest_framework' in settings.INSTALLED_APPS else '✗ Not configured')"

# 3. Check migrations
python manage.py migrate

# 4. Create token
python manage.py shell -c "from rest_framework.authtoken.models import Token; print('✓ Token' if Token.objects.exists() else '✗ No tokens')"

# 5. Test endpoint
curl http://localhost:8000/api/sessions/start/  # Should show auth error, not 404
```

---

## 🔒 Production Checklist

- [ ] Change DEBUG = False
- [ ] Set ALLOWED_HOSTS properly
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Set secure cookies
- [ ] Update CORS_ALLOWED_ORIGINS
- [ ] Set SECRET_KEY from environment
- [ ] Configure email for errors
- [ ] Set up logging
- [ ] Test all endpoints
- [ ] Load test for performance
- [ ] Set up monitoring
- [ ] Document API keys/tokens
- [ ] Backup database

---

## 🔍 Debugging

### View all tokens
```bash
python manage.py shell
from rest_framework.authtoken.models import Token
for t in Token.objects.all():
    print(f"{t.user}: {t.key}")
```

### Test API directly
```bash
python manage.py runserver
# Visit http://localhost:8000/api/ in browser
```

### View SQL queries
```python
from django.db import connection
print(connection.queries)
```

### Check permissions
```python
from rest_framework.permissions import IsAuthenticated
IsAuthenticated().has_permission(request, view)
```

---

## 📊 Performance Tips

1. **Batch pose submissions**: Send 30 frames at a time
2. **Cache progress**: Don't call every second
3. **Paginate results**: Use limit/offset
4. **Select related**: Reduce database queries
5. **Monitor rate limits**: Stay under 1000/hour

---

## 🎯 Common Workflow

```
1. Get Token
   POST /api-token-auth/

2. Start Session
   POST /api/sessions/start/
   
3. Get Active Session
   GET /api/sessions/active/

4. During Exercise (Repeat)
   POST /api/pose/submit/ (per frame)

5. After Exercise
   POST /api/score/calculate/

6. After Session
   GET /api/feedback/session/
   GET /api/progress/current/
```

---

## 📞 Need Help?

1. **Setup Issues**: See API_INTEGRATION_GUIDE.md
2. **Endpoint Usage**: See API_DOCUMENTATION.md
3. **Code Examples**: See API_CLIENT_EXAMPLES.md
4. **Overview**: See API_SUMMARY.md
5. **Quick Lookup**: This file

---

## ⚡ One-Liner Commands

```bash
# Get token
curl -X POST http://localhost:8000/api-token-auth/ -d '{"username":"s","password":"p"}'

# Start session
curl -X POST http://localhost:8000/api/sessions/start/ -H "Authorization: Token TOK" -d '{"title":"Work","pain_level_before":4}'

# Get progress
curl http://localhost:8000/api/progress/current/ -H "Authorization: Token TOK"

# Test API (no auth)
curl http://localhost:8000/api/sessions/start/
```

---

## 📈 Endpoint Usage Frequency

*Recommended call frequency for typical session:*

| Endpoint | Frequency | Notes |
|----------|-----------|-------|
| start | 1x/session | Beginning |
| submit_pose | 30x/session | Per frame |
| calculate_score | 1x/exercise | After each |
| get_feedback | 1x/session | End of session |
| get_progress | 1x/session | For summary |
| get_history | On demand | Dashboard |

---

## 🎓 Learning Path

1. **Beginner**: Read API_INTEGRATION_GUIDE.md (15 min)
2. **Intermediate**: Run example from this file (10 min)
3. **Advanced**: Study API_DOCUMENTATION.md (20 min)
4. **Expert**: Review api/views.py code (30 min)

---

**Last Updated**: April 20, 2026
**Status**: ✅ Ready to Use

For detailed information, see the full documentation files in the project directory.
