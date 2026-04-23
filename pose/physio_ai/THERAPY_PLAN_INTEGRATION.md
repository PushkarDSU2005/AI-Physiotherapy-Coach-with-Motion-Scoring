"""
Quick Integration Guide for Therapy Plan Generation

This file shows the minimal changes needed to integrate the therapy plan
generation system into your existing PhysioAI Django project.
"""

# ============================================================
# STEP 1: Update settings.py
# ============================================================

# In your physio_ai/settings.py, add:

INSTALLED_APPS = [
    # ... existing apps ...
    'therapy_plans',  # Add this line
]

# Add OpenAI API key (use environment variable)
import os
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Optional: Configure logging for therapy plans
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


# ============================================================
# STEP 2: Update Main URLs (physio_ai/urls.py)
# ============================================================

# In your main urls.py, add the therapy plans URLs:

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # Existing API URLs
    
    # Add this line for therapy plan APIs:
    path('api/', include('api.urls_therapy_plans')),
]


# ============================================================
# STEP 3: Create Database Migrations
# ============================================================

# In terminal, run:
# python manage.py makemigrations therapy_plans
# python manage.py migrate


# ============================================================
# STEP 4: Set Environment Variable
# ============================================================

# Linux/macOS:
# export OPENAI_API_KEY="sk-your-api-key-here"

# Windows (PowerShell):
# $env:OPENAI_API_KEY="sk-your-api-key-here"

# Or add to .env file and use python-dotenv


# ============================================================
# STEP 5: Usage Examples
# ============================================================

# Example 1: Generate plan from Python shell
# python manage.py shell
"""
from django.contrib.auth.models import User
from therapy_plans.services import generate_therapy_plan

user = User.objects.get(username='john_doe')
plan, message = generate_therapy_plan(
    user=user,
    injury_type="knee pain",
    injury_severity="moderate",
    duration_weeks=4,
    difficulty_level="intermediate",
    goals=["Reduce pain", "Improve mobility"]
)

if plan:
    print(f"✓ Plan created: {plan.title}")
else:
    print(f"✗ Error: {message}")
"""

# Example 2: Generate plan via API
"""
curl -X POST http://localhost:8000/api/therapy-plans/generate/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "injury_type": "knee pain",
    "injury_severity": "moderate",
    "duration_weeks": 4,
    "difficulty_level": "intermediate",
    "goals": ["Reduce pain", "Improve mobility", "Return to sports"]
  }'
"""

# Example 3: Get weekly schedule
"""
curl -X GET http://localhost:8000/api/therapy-plans/42/weekly-schedule/ \
  -H "Authorization: Bearer YOUR_TOKEN"
"""


# ============================================================
# STEP 6: Dependencies
# ============================================================

# Add to requirements.txt:
"""
openai>=0.27.0
django-rest-framework>=3.14.0
python-dotenv>=0.21.0  # For environment variables
"""

# Install:
# pip install -r requirements.txt


# ============================================================
# STEP 7: Verify Installation
# ============================================================

# Test in Django admin:
# 1. Go to http://localhost:8000/admin
# 2. Look for "Therapy Plans" and "Weekly Exercises" sections
# 3. Should be able to view, edit, and filter plans

# Test via API:
# 1. Get authentication token
# 2. POST to /api/therapy-plans/generate/
# 3. Verify 201 response with plan data


# ============================================================
# NEXT STEPS
# ============================================================

# 1. Add frontend components to display plans
# 2. Create a therapy plan dashboard
# 3. Add email notifications for milestones
# 4. Implement PDF export
# 5. Add plan comparison features
# 6. Create progress tracking views
# 7. Add integration with user sessions


# ============================================================
# TROUBLESHOOTING
# ============================================================

# Issue: ImportError: No module named 'therapy_plans'
# Solution: Make sure therapy_plans is in INSTALLED_APPS

# Issue: "No API key provided"
# Solution: Set OPENAI_API_KEY environment variable

# Issue: 401 Unauthorized on API
# Solution: Include valid JWT/Token in Authorization header

# Issue: 400 Bad Request when generating plan
# Solution: Check request body format matches schema

# For detailed logs, check: therapy_plans.log
