"""
Physio AI REST API Package

Complete REST API for physiotherapy AI system with:
- Session management (create, track, complete)
- Real-time pose angle capture from computer vision
- Automated form scoring based on AI analysis
- AI-generated feedback and recommendations
- Comprehensive progress tracking and history

Key Endpoints:
- /api/sessions/start/ - Create new session
- /api/pose/submit/ - Send pose angles
- /api/score/calculate/ - Calculate form score
- /api/feedback/session/ - Get feedback
- /api/progress/ - Get progress data
"""

default_app_config = 'api.apps.ApiConfig'
