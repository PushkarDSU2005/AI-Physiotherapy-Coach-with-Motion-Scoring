# API Client Implementation Examples

**Project**: Physio AI
**Purpose**: Client library examples for different platforms
**Date**: April 20, 2026

---

## 📱 Client Examples for Different Platforms

---

## Python Client

### Installation

```bash
pip install requests
```

### Complete Python Client

```python
"""
Physio AI Python Client

Complete client library for interacting with the Physio AI REST API.
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SessionData:
    """Session response data."""
    id: int
    title: str
    start_time: str
    status: str
    overall_session_score: Optional[float]
    exercises: List[Dict]


class PhysioAIClient:
    """Official Python client for Physio AI REST API."""
    
    def __init__(self, base_url: str, token: str):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of API (e.g., 'http://localhost:8000/api')
            token: API token for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        }
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                params: Optional[Dict] = None) -> Dict:
        """Make HTTP request to API."""
        url = f"{self.base_url}{endpoint}"
        
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=data,
            params=params
        )
        
        if response.status_code >= 400:
            error_data = response.json()
            raise Exception(f"API Error: {error_data.get('error', 'Unknown error')}")
        
        return response.json()
    
    # ========================================================================
    # SESSION MANAGEMENT
    # ========================================================================
    
    def start_session(self, title: str, pain_level_before: int,
                     description: str = '', duration: int = 30) -> Dict:
        """
        Start a new therapy session.
        
        Args:
            title: Session title
            pain_level_before: Pain level 0-10
            description: Optional description
            duration: Session duration in minutes
        
        Returns:
            Session data with ID
        """
        data = {
            'title': title,
            'pain_level_before': pain_level_before,
            'description': description,
            'scheduled_duration_minutes': duration,
            'session_type': 'home_unsupervised'
        }
        return self._request('POST', '/sessions/start/', data=data)
    
    def get_active_session(self) -> Dict:
        """Get currently active session."""
        return self._request('GET', '/sessions/active/')
    
    def get_session_history(self, limit: int = 10, offset: int = 0) -> Dict:
        """
        Get session history with pagination.
        
        Args:
            limit: Number of results (max 100)
            offset: Number of results to skip
        """
        return self._request(
            'GET',
            '/sessions/history/',
            params={'limit': limit, 'offset': offset}
        )
    
    # ========================================================================
    # POSE ANALYSIS
    # ========================================================================
    
    def submit_pose_angles(self, session_exercise_id: int, frame_number: int,
                          timestamp: float, angles: Dict[str, float],
                          confidence: float = 95.0,
                          is_peak: bool = False) -> Dict:
        """
        Submit detected pose angles from computer vision.
        
        Args:
            session_exercise_id: ID of exercise being performed
            frame_number: Frame number in video
            timestamp: Timestamp in seconds
            angles: Dict of joint angles {'shoulder': 90.5, 'elbow': 178.2}
            confidence: Pose detection confidence 0-100
            is_peak: Whether this is peak position
        """
        data = {
            'session_exercise_id': session_exercise_id,
            'frame_number': frame_number,
            'timestamp_seconds': timestamp,
            'detected_joint_angles': angles,
            'pose_detection_confidence': confidence,
            'is_peak_position': is_peak
        }
        return self._request('POST', '/pose/submit/', data=data)
    
    # ========================================================================
    # SCORING
    # ========================================================================
    
    def calculate_score(self, session_exercise_id: int) -> Dict:
        """
        Calculate form score for completed exercise.
        
        Args:
            session_exercise_id: ID of exercise to score
        
        Returns:
            Score data with form, consistency, ROM
        """
        data = {'session_exercise_id': session_exercise_id}
        return self._request('POST', '/score/calculate/', data=data)
    
    # ========================================================================
    # FEEDBACK
    # ========================================================================
    
    def get_session_feedback(self, session_id: int) -> Dict:
        """
        Get AI-generated feedback for session.
        
        Args:
            session_id: ID of completed session
        """
        return self._request(
            'GET',
            '/feedback/session/',
            params={'session_id': session_id}
        )
    
    # ========================================================================
    # PROGRESS
    # ========================================================================
    
    def get_progress(self) -> Dict:
        """Get current user progress metrics."""
        return self._request('GET', '/progress/current/')
    
    def get_progress_history(self, days: int = 30) -> Dict:
        """
        Get progress history over date range.
        
        Args:
            days: Number of days to look back (max 365)
        """
        return self._request(
            'GET',
            '/progress/history/',
            params={'days': min(days, 365)}
        )
    
    def get_exercise_progress(self, exercise_id: int) -> Dict:
        """Get progress on specific exercise."""
        return self._request(
            'GET',
            '/progress/exercise/',
            params={'exercise_id': exercise_id}
        )


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_complete_session():
    """Example: Complete exercise session workflow."""
    
    # Initialize client
    client = PhysioAIClient(
        base_url='http://localhost:8000/api',
        token='YOUR_TOKEN_HERE'
    )
    
    # 1. Start session
    print("Starting session...")
    session_resp = client.start_session(
        title='Shoulder Strengthening',
        pain_level_before=4,
        description='Focus on stability',
        duration=30
    )
    session_id = session_resp['session_id']
    print(f"✓ Session started: {session_id}")
    
    # 2. Simulate exercise with pose frames
    print("\nSubmitting pose data...")
    session_exercise_id = 1
    
    for frame in range(20):  # 20 frames of exercise
        timestamp = frame * 0.1  # 0.1 sec per frame
        
        # Simulated joint angles
        angles = {
            'shoulder': 90 + (frame * 2),  # Increasing angle
            'elbow': 170 + (frame * 1),
            'wrist': 0
        }
        
        response = client.submit_pose_angles(
            session_exercise_id=session_exercise_id,
            frame_number=frame,
            timestamp=timestamp,
            angles=angles,
            confidence=92.5,
            is_peak=(frame == 10)  # Peak at middle
        )
        
        if frame % 5 == 0:
            print(f"  Frame {frame}: {response['data']['pose_detection_confidence']}% confidence")
    
    print("✓ Pose data submitted")
    
    # 3. Calculate score
    print("\nCalculating score...")
    score_resp = client.calculate_score(session_exercise_id)
    score_data = score_resp['data']
    print(f"✓ Form Score: {score_data['form_score']}")
    print(f"✓ Consistency: {score_data['consistency_score']}")
    print(f"✓ ROM: {score_data['range_of_motion_percentage']}%")
    
    # 4. Get feedback
    print("\nGetting feedback...")
    feedback_resp = client.get_session_feedback(session_id)
    feedback = feedback_resp['data']
    print(f"✓ AI Feedback: {feedback['ai_feedback'][:100]}...")
    print(f"✓ Pain improvement: {feedback['pain_improvement']} points")
    
    # 5. Check progress
    print("\nGetting progress...")
    progress_resp = client.get_progress()
    progress = progress_resp['data']
    print(f"✓ Sessions completed: {progress['total_sessions_completed']}")
    print(f"✓ Average score: {progress['average_session_score']}")
    print(f"✓ Current streak: {progress['current_streak_days']} days")
    
    # 6. Get history
    print("\nGetting 7-day history...")
    history_resp = client.get_progress_history(days=7)
    history = history_resp['data']
    print(f"✓ Total sessions (7d): {history['total_sessions']}")
    print(f"✓ Trend: {history['trend']} ({history['trend_percentage']}%)")


if __name__ == '__main__':
    try:
        example_complete_session()
    except Exception as e:
        print(f"❌ Error: {e}")
```

### Quick Start

```python
from physio_ai_client import PhysioAIClient

# Initialize
client = PhysioAIClient('http://localhost:8000/api', 'YOUR_TOKEN')

# Start session
session = client.start_session('Shoulder Work', pain_level_before=4)
print(f"Session {session['session_id']} started")

# Get progress
progress = client.get_progress()
print(f"Average score: {progress['data']['average_session_score']}")
```

---

## JavaScript / Node.js Client

### Installation

```bash
npm install axios
```

### JavaScript Client

```javascript
/**
 * Physio AI JavaScript Client
 * Complete client for consuming the REST API
 */

class PhysioAIClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.token = token;
        this.headers = {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
        };
    }

    async request(method, endpoint, data = null, params = null) {
        const url = new URL(`${this.baseUrl}${endpoint}`);
        if (params) {
            Object.keys(params).forEach(key =>
                url.searchParams.append(key, params[key])
            );
        }

        const options = {
            method,
            headers: this.headers,
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'API Error');
        }

        return result;
    }

    // SESSION ENDPOINTS

    async startSession(title, painLevelBefore, options = {}) {
        const data = {
            title,
            pain_level_before: painLevelBefore,
            description: options.description || '',
            scheduled_duration_minutes: options.duration || 30,
            session_type: options.sessionType || 'home_unsupervised'
        };
        return this.request('POST', '/sessions/start/', data);
    }

    async getActiveSession() {
        return this.request('GET', '/sessions/active/');
    }

    async getSessionHistory(limit = 10, offset = 0) {
        return this.request('GET', '/sessions/history/', null, { limit, offset });
    }

    // POSE ENDPOINTS

    async submitPoseAngles(sessionExerciseId, frameNumber, timestamp, angles, options = {}) {
        const data = {
            session_exercise_id: sessionExerciseId,
            frame_number: frameNumber,
            timestamp_seconds: timestamp,
            detected_joint_angles: angles,
            pose_detection_confidence: options.confidence || 95.0,
            is_peak_position: options.isPeak || false
        };
        return this.request('POST', '/pose/submit/', data);
    }

    // SCORING ENDPOINTS

    async calculateScore(sessionExerciseId) {
        return this.request('POST', '/score/calculate/', {
            session_exercise_id: sessionExerciseId
        });
    }

    // FEEDBACK ENDPOINTS

    async getSessionFeedback(sessionId) {
        return this.request('GET', '/feedback/session/', null, {
            session_id: sessionId
        });
    }

    // PROGRESS ENDPOINTS

    async getProgress() {
        return this.request('GET', '/progress/current/');
    }

    async getProgressHistory(days = 30) {
        return this.request('GET', '/progress/history/', null, {
            days: Math.min(days, 365)
        });
    }

    async getExerciseProgress(exerciseId) {
        return this.request('GET', '/progress/exercise/', null, {
            exercise_id: exerciseId
        });
    }
}

// ============================================================================
// USAGE EXAMPLE
// ============================================================================

async function completeSessionWorkflow() {
    const client = new PhysioAIClient(
        'http://localhost:8000/api',
        'YOUR_TOKEN_HERE'
    );

    try {
        // 1. Start session
        console.log('Starting session...');
        const sessionResp = await client.startSession('Shoulder Work', 4, {
            description: 'Focus on stability',
            duration: 30
        });
        const sessionId = sessionResp.session_id;
        console.log(`✓ Session started: ${sessionId}`);

        // 2. Submit pose data
        console.log('\nSubmitting pose data...');
        for (let frame = 0; frame < 20; frame++) {
            const angles = {
                shoulder: 90 + (frame * 2),
                elbow: 170 + (frame * 1),
                wrist: 0
            };

            await client.submitPoseAngles(
                1,  // session_exercise_id
                frame,
                frame * 0.1,
                angles,
                { confidence: 92.5, isPeak: frame === 10 }
            );

            if (frame % 5 === 0) {
                console.log(`  Frame ${frame} submitted`);
            }
        }
        console.log('✓ Pose data complete');

        // 3. Calculate score
        console.log('\nCalculating score...');
        const scoreResp = await client.calculateScore(1);
        const score = scoreResp.data;
        console.log(`✓ Form Score: ${score.form_score}`);
        console.log(`✓ Consistency: ${score.consistency_score}`);

        // 4. Get feedback
        console.log('\nGetting feedback...');
        const feedbackResp = await client.getSessionFeedback(sessionId);
        console.log(`✓ Feedback: ${feedbackResp.data.ai_feedback.substring(0, 100)}...`);

        // 5. Get progress
        console.log('\nGetting progress...');
        const progressResp = await client.getProgress();
        const progress = progressResp.data;
        console.log(`✓ Sessions: ${progress.total_sessions_completed}`);
        console.log(`✓ Avg Score: ${progress.average_session_score}`);

    } catch (error) {
        console.error('❌ Error:', error.message);
    }
}

// Run example
completeSessionWorkflow();
```

### React Hook Example

```javascript
import { useState, useCallback } from 'react';

function usePhysioAI(token) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const client = new PhysioAIClient('http://localhost:8000/api', token);

    const startSession = useCallback(async (title, pain) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await client.startSession(title, pain);
            return resp;
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    const submitPose = useCallback(async (sessionExerciseId, frame, timestamp, angles) => {
        try {
            return await client.submitPoseAngles(sessionExerciseId, frame, timestamp, angles);
        } catch (err) {
            setError(err.message);
        }
    }, []);

    return { startSession, submitPose, loading, error };
}

// Usage in component
function ExerciseTracker() {
    const { startSession, submitPose } = usePhysioAI('YOUR_TOKEN');
    const [sessionId, setSessionId] = useState(null);

    const handleStartSession = async () => {
        const resp = await startSession('Shoulder Press', 4);
        setSessionId(resp.session_id);
    };

    return (
        <div>
            <button onClick={handleStartSession}>Start Session</button>
            {sessionId && <p>Session: {sessionId}</p>}
        </div>
    );
}
```

---

## cURL Commands

### Get Token

```bash
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "sarah_jones",
    "password": "password123"
  }'
```

### Start Session

```bash
TOKEN="abc123def456..."

curl -X POST http://localhost:8000/api/sessions/start/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Shoulder Session",
    "pain_level_before": 4,
    "scheduled_duration_minutes": 30
  }'
```

### Submit Pose Angles

```bash
curl -X POST http://localhost:8000/api/pose/submit/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_exercise_id": 1,
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

### Calculate Score

```bash
curl -X POST http://localhost:8000/api/score/calculate/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_exercise_id": 1}'
```

### Get Feedback

```bash
curl -X GET "http://localhost:8000/api/feedback/session/?session_id=1" \
  -H "Authorization: Token $TOKEN"
```

### Get Progress

```bash
curl -X GET http://localhost:8000/api/progress/current/ \
  -H "Authorization: Token $TOKEN"
```

---

## Postman Collection

Import this collection into Postman:

```json
{
  "info": {
    "name": "Physio AI API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Get Token",
          "request": {
            "method": "POST",
            "header": [],
            "body": {
              "mode": "raw",
              "raw": "{\"username\":\"sarah_jones\",\"password\":\"password123\"}"
            },
            "url": {
              "raw": "{{base_url}}/api-token-auth/",
              "host": ["{{base_url}}"],
              "path": ["api-token-auth"]
            }
          }
        }
      ]
    },
    {
      "name": "Sessions",
      "item": [
        {
          "name": "Start Session",
          "request": {
            "method": "POST",
            "header": [{"key": "Authorization", "value": "Token {{token}}"}],
            "body": {
              "mode": "raw",
              "raw": "{\"title\":\"Shoulder Work\",\"pain_level_before\":4}"
            },
            "url": {
              "raw": "{{base_url}}/api/sessions/start/",
              "host": ["{{base_url}}"],
              "path": ["api", "sessions", "start"]
            }
          }
        },
        {
          "name": "Get Active Session",
          "request": {
            "method": "GET",
            "header": [{"key": "Authorization", "value": "Token {{token}}"}],
            "url": {
              "raw": "{{base_url}}/api/sessions/active/",
              "host": ["{{base_url}}"],
              "path": ["api", "sessions", "active"]
            }
          }
        }
      ]
    },
    {
      "name": "Progress",
      "item": [
        {
          "name": "Get Current Progress",
          "request": {
            "method": "GET",
            "header": [{"key": "Authorization", "value": "Token {{token}}"}],
            "url": {
              "raw": "{{base_url}}/api/progress/current/",
              "host": ["{{base_url}}"],
              "path": ["api", "progress", "current"]
            }
          }
        }
      ]
    }
  ],
  "variable": [
    {"key": "base_url", "value": "http://localhost:8000"},
    {"key": "token", "value": ""}
  ]
}
```

---

## Best Practices

### 1. Error Handling

```python
try:
    session = client.start_session('Work', 4)
except Exception as e:
    logger.error(f"Failed to start session: {e}")
    # Notify user
```

### 2. Batch Pose Submissions

```python
# Send in batches for efficiency
batch_size = 30
for i in range(0, len(frames), batch_size):
    for frame in frames[i:i+batch_size]:
        client.submit_pose_angles(...)
```

### 3. Caching Progress

```python
# Cache progress to reduce API calls
class CachedClient(PhysioAIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._progress_cache = None
        self._cache_time = 0
    
    def get_progress(self):
        now = time.time()
        if now - self._cache_time < 60:  # Cache for 60 sec
            return self._progress_cache
        self._progress_cache = super().get_progress()
        self._cache_time = now
        return self._progress_cache
```

### 4. Rate Limiting Handling

```javascript
async function retryWithBackoff(fn, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            return await fn();
        } catch (error) {
            if (error.status === 429 && i < maxRetries - 1) {
                await new Promise(r => setTimeout(r, 1000 * Math.pow(2, i)));
            } else {
                throw error;
            }
        }
    }
}
```

---

**Created**: April 20, 2026
**For**: Physio AI Project
**Status**: Ready to Use ✅
