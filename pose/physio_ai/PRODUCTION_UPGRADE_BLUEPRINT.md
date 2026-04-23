# Physio AI Production Upgrade Blueprint

## 1. Upgraded Architecture

### Frontend
- Django templates upgraded into a SaaS-style UI using Tailwind CDN plus custom glassmorphism styling.
- Real-time capture page split into:
  - `static/js/pose_detector.js` for MediaPipe camera orchestration and overlay rendering
  - `static/js/pose_metrics_worker.js` for off-main-thread metric computation
  - `static/js/pose_capture_experience.js` for dashboard binding, TTS, adaptive sync, and chart updates
- Dashboard and analytics use Chart.js for trend visualization and live cards.

### Backend
- `analytics/services.py` now acts as the aggregation layer for dashboard, analytics, and therapy-plan views.
- `ai_engine/live_feedback_engine.py` adds context-aware coaching, risk-trend awareness, historical comparison, and difficulty-adjustment logic.
- `sessions/api_views.py` now returns richer live payloads:
  - calculated joint angles
  - prioritized feedback
  - coaching messages
  - stability and fatigue signals
- `api/dashboard_views.py` exposes dashboard metrics and chart-ready analytics data.

### AI / Intelligence Layer
- Real-time pose stream remains MediaPipe-driven.
- Live intelligence combines:
  - exercise-aware target angle ranges
  - issue severity prioritization
  - historical form averages
  - injury-risk trend analysis
  - adaptive progression recommendations

## 2. Step-by-Step Implementation Plan

1. Keep the existing Django models and routes intact.
2. Route dashboard, analytics, and therapy views through shared service builders.
3. Upgrade the live capture UI with worker-based metric processing.
4. Layer in intelligent feedback via `LiveFeedbackEngine`.
5. Expose chart-ready dashboard endpoints for async refresh.
6. Add PDF export and WebSocket consumers as the next production hardening step.
7. Add deployment observability, Redis, and background task processing for scale.

## 3. Code Areas Added or Upgraded

### Enhanced Pose Detection UI
- `templates/sessions/pose_capture.html`
- `static/js/pose_detector.js`
- `static/js/pose_metrics_worker.js`
- `static/js/pose_capture_experience.js`

### Real-Time Dashboard
- `templates/dashboard/dashboard.html`
- `static/dashboard/js/dashboard.js`
- `api/dashboard_views.py`
- `analytics/services.py`

### AI Feedback Engine
- `ai_engine/live_feedback_engine.py`
- `sessions/api_views.py`

## 4. Folder Structure Changes

```text
physio_ai/
├── PRODUCTION_UPGRADE_BLUEPRINT.md
├── analytics/
│   └── services.py
├── ai_engine/
│   └── live_feedback_engine.py
├── api/
│   └── dashboard_views.py
├── static/
│   └── js/
│       ├── pose_capture_experience.js
│       ├── pose_detector.js
│       └── pose_metrics_worker.js
├── static/
│   └── dashboard/
│       └── js/
│           └── dashboard.js
└── templates/
    ├── analytics/index.html
    ├── dashboard/dashboard.html
    ├── home.html
    ├── sessions/pose_capture.html
    └── therapy_plans/index.html
```

## 5. Required Libraries

### Already used / should be installed
- `Django`
- `djangorestframework`
- `numpy`
- `mediapipe`

### Recommended for production next step
- `channels`
- `daphne`
- `redis`
- `channels-redis`
- `weasyprint` or `reportlab`

## 6. Testing Checklist

### Live capture
- Camera loads on Chrome and Edge.
- Full body remains detected during exercise.
- Overlay keeps rendering above 20 FPS.
- Incorrect joints turn red and correct joints stay green.
- Motion trail is visible and does not flicker.
- Joint angle badges update while moving.

### Feedback
- Prioritized issue list changes when posture worsens.
- Voice prompts are throttled and do not spam.
- Adaptive progression messaging changes with score quality.
- Fatigue score rises when movement slows late in a set.

### Dashboard / analytics
- Dashboard renders with authenticated users and demo fallback.
- Charts render with empty-state safety.
- Analytics and therapy pages show real model-backed summaries.
- Dashboard API routes return valid JSON.

### Regression
- Existing capture upload endpoint still stores `PoseAnalysis`.
- Existing session and therapy routes still resolve.
- Templates render even if a user has no data yet.

## 7. Deployment Steps

1. Install Python dependencies, including `mediapipe`.
2. Collect static assets with `python manage.py collectstatic`.
3. Serve Django with ASGI for the next WebSocket phase.
4. Add Redis for Channels and future event streaming.
5. Put Nginx in front of Daphne or Uvicorn for TLS and static caching.
6. Enable gzip or brotli for JS payloads.
7. Add Sentry, structured logging, and health checks.
8. Add HTTPS camera permissions and a secure allowed-origins setup.

## 8. Next Production Hardening

- Replace polling with WebSocket session streams backed by Django Channels.
- Persist live dashboard snapshots in Redis for therapist monitoring.
- Add multilingual voice prompt selection per user profile.
- Add PDF export using `weasyprint` for clinical summaries.
- Move heavy analytics recalculation into background tasks.
