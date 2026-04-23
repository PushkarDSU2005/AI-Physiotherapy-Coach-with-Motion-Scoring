# Physio AI REST API Documentation

**Project**: Physio AI - Physiotherapy AI System
**Version**: 1.0.0
**Status**: Production Ready
**Date**: April 20, 2026

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL](#base-url)
4. [Response Format](#response-format)
5. [Session Endpoints](#session-endpoints)
6. [Pose Analysis Endpoints](#pose-analysis-endpoints)
7. [Scoring Endpoints](#scoring-endpoints)
8. [Feedback Endpoints](#feedback-endpoints)
9. [Progress Endpoints](#progress-endpoints)
10. [Error Handling](#error-handling)
11. [Usage Examples](#usage-examples)
12. [Rate Limiting](#rate-limiting)

---

## Overview

The Physio AI REST API provides complete functionality for physiotherapy sessions with AI-powered form analysis:

- **Session Management**: Create, track, and complete therapy sessions
- **Pose Detection**: Capture real-time joint angles from video
- **Intelligent Scoring**: AI calculates form quality automatically
- **Smart Feedback**: Generate personalized recommendations
- **Progress Tracking**: Monitor improvement over time

### Key Features

✅ Token-based authentication
✅ Real-time pose angle capture
✅ Automated form scoring (form, consistency, ROM)
✅ AI-generated feedback with improvement areas
✅ Comprehensive progress analytics
✅ Daily metrics tracking
✅ Exercise-specific performance analysis

---

## Authentication

All API endpoints require authentication using either:

### Option 1: Token Authentication (Recommended)

```bash
# Get token (run once after user creation)
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "sarah_jones", "password": "password123"}'

# Response
{
  "token": "abc123def456..."
}

# Use token in subsequent requests
curl -H "Authorization: Token abc123def456..." \
  http://localhost:8000/api/sessions/start/
```

### Option 2: Session Authentication

```bash
# Login via session
curl -X POST http://localhost:8000/api-auth/login/ \
  -d 'username=sarah_jones&password=password123'

# Use session cookies automatically
curl -b cookies.txt http://localhost:8000/api/sessions/start/
```

---

## Base URL

```
http://localhost:8000/api/
https://physio-ai.example.com/api/  (production)
```

All endpoints use relative paths from this base.

---

## Response Format

All endpoints return standardized JSON responses:

### Success Response (2xx)

```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "data": {
    "key": "value",
    "nested": {
      "field": "data"
    }
  },
  "timestamp": "2026-04-20T14:30:00Z"
}
```

### Error Response (4xx, 5xx)

```json
{
  "status": "error",
  "error": "Error type",
  "detail": "Detailed error message",
  "code": "ERROR_CODE"
}
```

### Pagination Response

```json
{
  "status": "success",
  "count": 150,
  "limit": 10,
  "offset": 0,
  "results": [...]
}
```

---

## Session Endpoints

### 1. Start Session

**Endpoint**: `POST /sessions/start/`

**Authentication**: Required (Token or Session)

**Purpose**: Create and start a new therapy session

**Request**:

```json
{
  "title": "Daily Shoulder Strengthening",
  "description": "Focus on stability and strength",
  "session_type": "home_supervised",
  "scheduled_duration_minutes": 30,
  "pain_level_before": 4
}
```

**Request Fields**:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| title | string | No | Session name | "Shoulder Work" |
| description | string | No | Session details | "Focus on ROM" |
| session_type | enum | No | Session category | "home_unsupervised" |
| scheduled_duration_minutes | integer | No | Expected duration | 30 |
| pain_level_before | integer | Yes | Starting pain (0-10) | 4 |
| assigned_therapist_id | integer | No | Therapist to supervise | 5 |

**session_type Options**:
- `home_unsupervised` - User exercises at home alone
- `home_supervised` - User exercises at home with telehealth supervision
- `clinic` - In-person clinic session
- `telehealth` - Video call with therapist

**Response** (201 Created):

```json
{
  "status": "success",
  "session_id": 42,
  "message": "Session started successfully",
  "data": {
    "id": 42,
    "title": "Daily Shoulder Strengthening",
    "start_time": "2026-04-20T14:30:00Z",
    "status": "in_progress",
    "exercises": [],
    "overall_session_score": null,
    "pain_level_before": 4
  }
}
```

**cURL Example**:

```bash
curl -X POST http://localhost:8000/api/sessions/start/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Shoulder Session",
    "pain_level_before": 3,
    "scheduled_duration_minutes": 30
  }'
```

---

### 2. Get Active Session

**Endpoint**: `GET /sessions/active/`

**Authentication**: Required

**Purpose**: Get the user's currently active (in-progress) session

**Query Parameters**: None

**Response** (200 OK):

```json
{
  "status": "success",
  "data": {
    "id": 42,
    "title": "Daily Shoulder Strengthening",
    "start_time": "2026-04-20T14:30:00Z",
    "status": "in_progress",
    "exercises": [
      {
        "id": 1,
        "exercise_id": 5,
        "exercise_name": "Shoulder Press",
        "order_in_session": 1,
        "status": "not_started"
      }
    ]
  }
}
```

**Error Response** (404 Not Found):

```json
{
  "status": "error",
  "message": "No active session found",
  "session_id": null
}
```

**cURL Example**:

```bash
curl -X GET http://localhost:8000/api/sessions/active/ \
  -H "Authorization: Token YOUR_TOKEN"
```

---

### 3. Get Session History

**Endpoint**: `GET /sessions/history/`

**Authentication**: Required

**Purpose**: Get paginated list of completed sessions

**Query Parameters**:

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| limit | integer | 10 | 100 | Results per page |
| offset | integer | 0 | - | Skip this many results |

**Response** (200 OK):

```json
{
  "status": "success",
  "count": 45,
  "limit": 10,
  "offset": 0,
  "results": [
    {
      "id": 40,
      "title": "Shoulder Session",
      "start_time": "2026-04-19T14:30:00Z",
      "end_time": "2026-04-19T15:00:00Z",
      "status": "completed",
      "overall_session_score": 85.2,
      "completion_percentage": 100.0,
      "exercise_count": 5,
      "pain_level_before": 4,
      "pain_level_after": 2
    },
    ...
  ]
}
```

**cURL Example**:

```bash
curl -X GET "http://localhost:8000/api/sessions/history/?limit=20&offset=0" \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## Pose Analysis Endpoints

### Submit Pose Angles

**Endpoint**: `POST /pose/submit/`

**Authentication**: Required

**Purpose**: Submit detected joint angles from computer vision during exercise

**Called**: Repeatedly during an exercise (every frame or periodically)

**Request**:

```json
{
  "session_exercise_id": 42,
  "frame_number": 5,
  "timestamp_seconds": 2.5,
  "detected_joint_angles": {
    "shoulder": 92.5,
    "elbow": 178.2,
    "wrist": 2.1,
    "hip": 95.0,
    "knee": 170.5
  },
  "pose_detection_confidence": 94.5,
  "individual_joint_confidence": {
    "shoulder": 96.2,
    "elbow": 92.1,
    "wrist": 85.3,
    "hip": 89.5,
    "knee": 91.2
  },
  "body_position_description": "Peak extension, arms overhead",
  "is_peak_position": true
}
```

**Request Fields**:

| Field | Type | Required | Range | Description |
|-------|------|----------|-------|-------------|
| session_exercise_id | int | Yes | - | ID of SessionExercise |
| frame_number | int | Yes | 0+ | Video frame index |
| timestamp_seconds | float | Yes | 0+ | Time in seconds |
| detected_joint_angles | object | Yes | - | Joint angles (degrees) |
| pose_detection_confidence | float | Yes | 0-100 | Overall confidence % |
| individual_joint_confidence | object | No | 0-100 | Per-joint confidence |
| body_position_description | string | No | - | Position description |
| is_peak_position | bool | No | - | Peak of movement? |

**Joint Angle Format**: Dictionary of joint names to angles in degrees (0-360)

```json
{
  "shoulder": 92.5,
  "elbow": 178.2,
  "wrist": 2.1,
  "hip": 95.0,
  "knee": 170.5,
  "ankle": 90.0
}
```

**Response** (201 Created):

```json
{
  "status": "success",
  "analysis_id": 128,
  "message": "Pose angles recorded",
  "data": {
    "id": 128,
    "frame_number": 5,
    "timestamp_seconds": 2.5,
    "detected_joint_angles": {
      "shoulder": 92.5,
      "elbow": 178.2,
      "wrist": 2.1
    },
    "angle_errors": {
      "shoulder": 2.5,
      "elbow": -1.8
    },
    "pose_detection_confidence": 94.5,
    "form_issues": []
  }
}
```

**cURL Example**:

```bash
curl -X POST http://localhost:8000/api/pose/submit/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_exercise_id": 42,
    "frame_number": 5,
    "timestamp_seconds": 2.5,
    "detected_joint_angles": {
      "shoulder": 92.5,
      "elbow": 178.2
    },
    "pose_detection_confidence": 94.5,
    "is_peak_position": true
  }'
```

**Python Example**:

```python
import requests

token = "YOUR_TOKEN"
headers = {"Authorization": f"Token {token}"}

# Send pose data during exercise
response = requests.post(
    "http://localhost:8000/api/pose/submit/",
    headers=headers,
    json={
        "session_exercise_id": 42,
        "frame_number": 5,
        "timestamp_seconds": 2.5,
        "detected_joint_angles": {
            "shoulder": 92.5,
            "elbow": 178.2
        },
        "pose_detection_confidence": 94.5
    }
)

analysis = response.json()
print(f"Recorded frame {analysis['data']['frame_number']}")
```

---

## Scoring Endpoints

### Calculate Exercise Score

**Endpoint**: `POST /score/calculate/`

**Authentication**: Required

**Purpose**: Calculate comprehensive form score for a completed exercise

**Called**: After user finishes an exercise

**Request**:

```json
{
  "session_exercise_id": 42
}
```

**Request Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| session_exercise_id | int | Yes | ID of SessionExercise |

**Response** (200 OK):

```json
{
  "status": "success",
  "message": "Score calculated successfully",
  "data": {
    "session_exercise_id": 42,
    "exercise_name": "Shoulder Press",
    "form_score": 85.5,
    "consistency_score": 82.0,
    "range_of_motion_percentage": 92.0,
    "overall_exercise_score": 85.3,
    "form_issues": [
      {
        "frame": 3,
        "joint": "shoulder",
        "deviation": 12.5,
        "severity": "medium"
      }
    ],
    "recommendations": [
      "Focus on maintaining proper joint alignment",
      "Watch out for the shoulder positioning"
    ]
  }
}
```

**Score Components**:

- **Form Score** (50% weight): How correct the positioning was compared to ideal
- **Consistency Score** (30% weight): How stable the form remained throughout
- **Range of Motion** (20% weight): How complete the movement was

**Overall Formula**: `(form * 0.5) + (consistency * 0.3) + (ROM * 0.2)`

**cURL Example**:

```bash
curl -X POST http://localhost:8000/api/score/calculate/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_exercise_id": 42}'
```

---

## Feedback Endpoints

### Get Session Feedback

**Endpoint**: `GET /feedback/session/?session_id=42`

**Authentication**: Required

**Purpose**: Get AI-generated feedback for a completed session

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| session_id | int | Yes | ID of completed session |

**Response** (200 OK):

```json
{
  "status": "success",
  "data": {
    "session_id": 42,
    "overall_session_score": 85.2,
    "completion_percentage": 100.0,
    "ai_feedback": "Excellent form! Your technique is very solid. You showed pain improvement of 2 points! Keep it up. Most common form issue: Slight shoulder elevation. Let's address this next session.",
    "improvement_areas": [
      {
        "exercise": "Shoulder Press",
        "issue": "Form quality",
        "score": 78.5,
        "recommendation": "Focus on proper positioning for Shoulder Press"
      },
      {
        "exercise": "Lateral Raise",
        "issue": "Inconsistent form",
        "score": 72.3,
        "recommendation": "Slow down and maintain consistent form throughout Lateral Raise"
      }
    ],
    "positive_feedback_points": [
      "Great consistency on Bicep Curls",
      "Excellent range of motion on Shoulder Press",
      "Pain improvement of 2 points"
    ],
    "avg_form_score": 82.3,
    "avg_consistency_score": 79.8,
    "avg_range_of_motion": 91.2,
    "pain_level_before": 4,
    "pain_level_after": 2,
    "pain_improvement": 2,
    "exercises_completed": 5,
    "total_exercises": 5,
    "exercises_skipped": 0,
    "recommended_focus_areas": [
      "Shoulder Press: Focus on proper positioning for Shoulder Press",
      "Lateral Raise: Slow down and maintain consistent form throughout Lateral Raise"
    ],
    "next_session_recommendations": [
      "Increase difficulty when form score > 85 consistently",
      "Reduce range if pain increases during exercise",
      "Practice exercises with low consistency scores"
    ]
  }
}
```

**cURL Example**:

```bash
curl -X GET "http://localhost:8000/api/feedback/session/?session_id=42" \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## Progress Endpoints

### Get Current Progress

**Endpoint**: `GET /progress/current/`

**Authentication**: Required

**Purpose**: Get comprehensive current user progress metrics

**Query Parameters**: None

**Response** (200 OK):

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "user_id": 5,
    "username": "sarah_jones",
    "total_sessions_completed": 42,
    "total_sessions_started": 45,
    "session_completion_rate": 93.3,
    "average_session_score": 82.5,
    "best_session_score": 95.2,
    "worst_session_score": 65.3,
    "average_exercise_form_score": 81.2,
    "current_streak_days": 5,
    "longest_streak_days": 12,
    "last_session_date": "2026-04-20",
    "exercises_mastered": 8,
    "avg_difficulty_of_exercises": "intermediate",
    "average_pain_before_session": 5.2,
    "average_pain_after_session": 2.8,
    "pain_improvement_percentage": 46.2,
    "primary_goal": "Return to full activity",
    "goal_progress_percentage": 72.5,
    "estimated_recovery_date": "2026-05-15",
    "sessions_this_week": 4,
    "average_score_this_week": 84.1,
    "total_reward_points": 2450,
    "recent_milestones": [
      {
        "milestone_type": "consecutive_perfect_sessions",
        "description": "Completed 3 sessions with >85 score",
        "date": "2026-04-20",
        "reward_points": 100
      }
    ]
  }
}
```

**cURL Example**:

```bash
curl -X GET http://localhost:8000/api/progress/current/ \
  -H "Authorization: Token YOUR_TOKEN"
```

---

### Get Progress History

**Endpoint**: `GET /progress/history/?days=30`

**Authentication**: Required

**Purpose**: Get detailed progress history over a date range

**Query Parameters**:

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| days | int | 30 | 365 | Days to look back |

**Response** (200 OK):

```json
{
  "status": "success",
  "data": {
    "date_range_start": "2026-03-21",
    "date_range_end": "2026-04-20",
    "total_sessions": 12,
    "total_exercises_completed": 120,
    "total_hours_exercised": 6.5,
    "average_session_score": 83.2,
    "trend": "improving",
    "trend_percentage": 5.8,
    "best_week": "Week of 2026-04-14",
    "worst_week": "Week of 2026-03-28",
    "pain_improvement_over_period": 2.1,
    "starting_average_pain": 5.3,
    "ending_average_pain": 3.2,
    "exercises_attempted": 15,
    "new_exercises_mastered": 3,
    "difficulty_progression": "Progressed from easy to intermediate",
    "daily_metrics": [
      {
        "date": "2026-04-20",
        "sessions_completed": 1,
        "exercises_completed": 5,
        "total_minutes_exercised": 35,
        "average_session_score": 85.2,
        "average_form_score": 83.5,
        "completion_rate": 100.0,
        "average_pain_before": 4.0,
        "average_pain_after": 2.0
      },
      ...
    ]
  }
}
```

**cURL Example**:

```bash
curl -X GET "http://localhost:8000/api/progress/history/?days=90" \
  -H "Authorization: Token YOUR_TOKEN"
```

---

### Get Exercise Progress

**Endpoint**: `GET /progress/exercise/?exercise_id=5`

**Authentication**: Required

**Purpose**: Get performance history on a specific exercise

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| exercise_id | int | Yes | ID of exercise |

**Response** (200 OK):

```json
{
  "status": "success",
  "data": {
    "exercise_id": 5,
    "exercise_name": "Shoulder Press",
    "category": "strengthening",
    "times_performed": 15,
    "average_form_score": 82.5,
    "best_form_score": 95.2,
    "worst_form_score": 65.3,
    "form_score_trend": "improving",
    "recent_scores": [
      95.2,
      92.1,
      87.5,
      84.3,
      82.1
    ],
    "average_user_difficulty_rating": 5.5,
    "average_pain_during_exercise": 2.3,
    "most_common_form_issues": {
      "Shoulder elevation": 5,
      "Incomplete extension": 3
    },
    "recent_feedback": "Great form! Keep shoulders level at the top.",
    "recommendation": "Great job! Keep working on consistency."
  }
}
```

**cURL Example**:

```bash
curl -X GET "http://localhost:8000/api/progress/exercise/?exercise_id=5" \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## Error Handling

### Common Error Codes

| Status | Code | Meaning | Solution |
|--------|------|---------|----------|
| 400 | INVALID_INPUT | Missing required fields | Check request format |
| 400 | VALIDATION_ERROR | Invalid field values | Check value ranges |
| 401 | UNAUTHORIZED | Missing/invalid token | Get new token |
| 403 | FORBIDDEN | No permission | Check permissions |
| 404 | NOT_FOUND | Resource doesn't exist | Check ID/URL |
| 500 | SERVER_ERROR | Server error | Retry later |

### Error Response Format

```json
{
  "status": "error",
  "error": "Invalid input",
  "details": {
    "pain_level_before": ["Ensure this value is less than or equal to 10."]
  }
}
```

### Handling Errors in Code

**Python Example**:

```python
import requests

token = "YOUR_TOKEN"
headers = {"Authorization": f"Token {token}"}

response = requests.get(
    "http://localhost:8000/api/sessions/active/",
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    print(f"Session: {data['data']['title']}")
elif response.status_code == 404:
    print("No active session")
else:
    error = response.json()
    print(f"Error: {error['error']}")
```

---

## Usage Examples

### Complete Workflow: Exercise Session

#### 1. Start Session

```bash
curl -X POST http://localhost:8000/api/sessions/start/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Shoulder Session",
    "pain_level_before": 4,
    "scheduled_duration_minutes": 30
  }'

# Response: {"status": "success", "session_id": 42, ...}
SESSION_ID=42
```

#### 2. Get Active Session

```bash
curl -X GET http://localhost:8000/api/sessions/active/ \
  -H "Authorization: Token YOUR_TOKEN"

# Response: {"status": "success", "data": {"exercises": [...]}}
SESSION_EXERCISE_ID=1
```

#### 3. During Exercise: Submit Pose Angles (Repeat Every Frame)

```bash
curl -X POST http://localhost:8000/api/pose/submit/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_exercise_id": '"$SESSION_EXERCISE_ID"',
    "frame_number": 5,
    "timestamp_seconds": 2.5,
    "detected_joint_angles": {
      "shoulder": 92.5,
      "elbow": 178.2
    },
    "pose_detection_confidence": 94.5,
    "is_peak_position": true
  }'
```

#### 4. After Exercise: Calculate Score

```bash
curl -X POST http://localhost:8000/api/score/calculate/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_exercise_id": '"$SESSION_EXERCISE_ID"'}'

# Response: {"status": "success", "data": {"form_score": 85.5, ...}}
```

#### 5. After Session: Get Feedback

```bash
curl -X GET "http://localhost:8000/api/feedback/session/?session_id=$SESSION_ID" \
  -H "Authorization: Token YOUR_TOKEN"

# Response: {"status": "success", "data": {"ai_feedback": "Great session!...", ...}}
```

#### 6. Check Progress

```bash
curl -X GET http://localhost:8000/api/progress/current/ \
  -H "Authorization: Token YOUR_TOKEN"

# Response: {"status": "success", "data": {"total_sessions_completed": 42, ...}}
```

### Python Client Example

```python
import requests
import json
from datetime import datetime

class PhysioAIClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Token {token}"}
    
    def start_session(self, title, pain_before, duration=30):
        """Start a new session."""
        response = requests.post(
            f"{self.base_url}/sessions/start/",
            headers=self.headers,
            json={
                "title": title,
                "pain_level_before": pain_before,
                "scheduled_duration_minutes": duration
            }
        )
        return response.json()
    
    def submit_pose(self, session_exercise_id, frame, timestamp, angles):
        """Submit pose angles during exercise."""
        response = requests.post(
            f"{self.base_url}/pose/submit/",
            headers=self.headers,
            json={
                "session_exercise_id": session_exercise_id,
                "frame_number": frame,
                "timestamp_seconds": timestamp,
                "detected_joint_angles": angles,
                "pose_detection_confidence": 94.5
            }
        )
        return response.json()
    
    def calculate_score(self, session_exercise_id):
        """Calculate score for exercise."""
        response = requests.post(
            f"{self.base_url}/score/calculate/",
            headers=self.headers,
            json={"session_exercise_id": session_exercise_id}
        )
        return response.json()
    
    def get_feedback(self, session_id):
        """Get session feedback."""
        response = requests.get(
            f"{self.base_url}/feedback/session/",
            headers=self.headers,
            params={"session_id": session_id}
        )
        return response.json()
    
    def get_progress(self):
        """Get current progress."""
        response = requests.get(
            f"{self.base_url}/progress/current/",
            headers=self.headers
        )
        return response.json()

# Usage
client = PhysioAIClient("http://localhost:8000/api", "YOUR_TOKEN")

# Start session
session = client.start_session("Shoulder Work", pain_before=4)
print(f"Session started: {session['session_id']}")

# Simulate exercise with pose frames
for frame in range(10):
    pose = client.submit_pose(
        session_exercise_id=1,
        frame=frame,
        timestamp=frame * 0.5,
        angles={"shoulder": 90 + frame, "elbow": 170}
    )

# Calculate score
score = client.calculate_score(session_exercise_id=1)
print(f"Form score: {score['data']['form_score']}")

# Get feedback
feedback = client.get_feedback(session['session_id'])
print(f"Feedback: {feedback['data']['ai_feedback']}")

# Check progress
progress = client.get_progress()
print(f"Sessions completed: {progress['data']['total_sessions_completed']}")
```

---

## Rate Limiting

**Current Limits** (can be configured):

- **Unauthenticated**: 60 requests/hour
- **Authenticated**: 1000 requests/hour
- **Pose submissions**: 300 requests/minute (for real-time tracking)

**Rate Limit Headers**:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1692820800
```

**Handling Rate Limits**:

```python
if response.status_code == 429:
    retry_after = int(response.headers['X-RateLimit-Reset'])
    print(f"Rate limited. Retry after {retry_after}")
```

---

## Webhook Events (Future)

Future versions will support webhooks for real-time notifications:

- Session started
- Session completed
- Score calculated
- Feedback generated
- Milestone achieved

---

## SDK/Libraries

### Official SDKs

- **Python**: `pip install physio-ai-sdk`
- **JavaScript**: `npm install physio-ai-client`
- **Swift (iOS)**: CocoaPods coming soon
- **Kotlin (Android)**: Coming soon

### Community Libraries

Check GitHub for community-maintained SDKs

---

## Support & Documentation

- **API Docs**: https://docs.physio-ai.com/api
- **GitHub Issues**: https://github.com/physio-ai/api/issues
- **Slack Community**: https://physio-ai.slack.com
- **Email**: api-support@physio-ai.com

---

**Last Updated**: April 20, 2026
**API Version**: 1.0.0
**Status**: Production Ready ✅
