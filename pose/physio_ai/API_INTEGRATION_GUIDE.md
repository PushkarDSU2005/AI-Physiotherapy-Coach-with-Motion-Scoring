# Django REST API Integration Guide

**Project**: Physio AI
**Purpose**: Integration instructions for enabling REST API
**Date**: April 20, 2026

---

## 📋 Quick Integration Checklist

- [ ] Install `djangorestframework` (add to requirements.txt)
- [ ] Add `rest_framework` to INSTALLED_APPS in settings.py
- [ ] Configure authentication in settings.py
- [ ] Include API URLs in main urls.py
- [ ] Create token for user (for authentication)
- [ ] Test endpoints with curl or Postman

---

## Step 1: Install Django REST Framework

### Update requirements.txt

```bash
pip install djangorestframework==3.14.0 django-cors-headers==4.0.0
```

Or manually add to `requirements.txt`:

```
Django==4.2.0
djangorestframework==3.14.0
django-cors-headers==4.0.0
Pillow==9.5.0
sqlparse==0.4.4
asgiref==3.7.1
pytz==2024.1
```

Then install:

```bash
pip install -r requirements.txt
```

---

## Step 2: Update Django Settings

Edit `physio_ai/settings.py`:

### Add to INSTALLED_APPS

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',
    
    # Your apps
    'users.apps.UsersConfig',
    'exercises.apps.ExercisesConfig',
    'sessions.apps.SessionsConfig',
    'ai_engine.apps.AiEngineConfig',
    'analytics.apps.AnalyticsConfig',
    'api.apps.ApiConfig',  # NEW
]
```

### Add Middleware for CORS

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # NEW - Add before common
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### Add REST Framework Configuration

```python
# ============================================================================
# REST FRAMEWORK CONFIGURATION
# ============================================================================

REST_FRAMEWORK = {
    # Default authentication methods
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # Token auth
        'rest_framework.authentication.SessionAuthentication',  # Session auth
    ],
    
    # Default permission classes
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Require auth by default
    ],
    
    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    
    # Filtering
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
    # Throttling (rate limiting)
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    },
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",      # React development
    "http://localhost:8000",      # Django development
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True

# Add in production
# CORS_ALLOWED_ORIGINS = [
#     "https://physio-ai.example.com",
#     "https://app.physio-ai.com",
# ]
```

### Add Token Auth (for API authentication)

```python
# After REST_FRAMEWORK config, add:

# Token expiration (optional)
from datetime import timedelta

REST_FRAMEWORK = {
    # ... existing config ...
    'DEFAULT_TOKEN_EXPIRE_TIME': timedelta(days=30),
}
```

---

## Step 3: Include API URLs in Main Project

Edit `physio_ai/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # REST Framework authentication
    # Browser browsable API login
    path('api-auth/', include('rest_framework.urls')),
    
    # Token authentication endpoint
    # POST /api-token-auth/ with {username, password}
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    
    # API endpoints
    path('api/', include('api.urls', namespace='api')),
    
    # App URLs (if needed for non-API views)
    path('users/', include('users.urls')),
    path('exercises/', include('exercises.urls')),
    path('sessions/', include('sessions.urls')),
    path('ai/', include('ai_engine.urls')),
    path('analytics/', include('analytics.urls')),
]

# Serve media files in development
if DEBUG:
    from django.conf.urls.static import static
    from django.conf import settings
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## Step 4: Create API App (if not already created)

```bash
python manage.py startapp api
```

This creates the `api` directory. Move your `serializers.py`, `views.py`, and `urls.py` files there.

---

## Step 5: Update Django Admin for API

Edit `api/admin.py`:

```python
from django.contrib import admin
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    """Manage API tokens in admin panel."""
    list_display = ['user', 'key', 'created']
    fields = ['user', 'key', 'created']
    readonly_fields = ['key', 'created']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields
        return []  # Creating new object
```

---

## Step 6: Apply Migrations

```bash
# Create Token table
python manage.py migrate

# Check it worked
python manage.py migrate --check
```

---

## Step 7: Create User and Get Token

### Option A: Django Shell

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

# Create user if doesn't exist
user, created = User.objects.get_or_create(
    username='sarah_jones',
    defaults={'email': 'sarah@example.com'}
)

if created:
    user.set_password('SecurePassword123!')
    user.first_name = 'Sarah'
    user.last_name = 'Jones'
    user.save()
    print(f"Created user: {user}")

# Get or create token
token, created = Token.objects.get_or_create(user=user)
print(f"Token: {token.key}")
```

### Option B: Admin Panel

1. Go to `http://localhost:8000/admin/`
2. Create a User
3. Go to "Tokens" section
4. Click "Add Token"
5. Select the user
6. Copy the token key

---

## Step 8: Test the API

### Get Token

```bash
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "sarah_jones",
    "password": "SecurePassword123!"
  }'

# Response:
# {"token":"abc123def456..."}
```

### Start Session

```bash
TOKEN="abc123def456..."

curl -X POST http://localhost:8000/api/sessions/start/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Session",
    "pain_level_before": 5,
    "scheduled_duration_minutes": 30
  }'

# Response:
# {"status":"success","session_id":1,"data":{...}}
```

### Get Active Session

```bash
curl -X GET http://localhost:8000/api/sessions/active/ \
  -H "Authorization: Token $TOKEN"
```

---

## Step 9: Set up in Production

### settings.py

```python
# Security
DEBUG = False
ALLOWED_HOSTS = ['physio-ai.example.com']

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# CORS - Restricted to production domain
CORS_ALLOWED_ORIGINS = [
    "https://physio-ai.example.com",
    "https://app.physio-ai.com",
]

# Security Headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

### Environment Variables

```bash
# .env
DEBUG=False
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=physio-ai.example.com,app.physio-ai.com

# Database (use PostgreSQL in production)
DATABASE_URL=postgresql://user:password@localhost:5432/physio_ai

# CORS
CORS_ALLOWED_ORIGINS=https://physio-ai.example.com,https://app.physio-ai.com
```

---

## Step 10: API Documentation

Access Browsable API:

- `http://localhost:8000/api/`
- `http://localhost:8000/api/sessions/start/`
- `http://localhost:8000/api/progress/current/`

All endpoints can be tested directly in the browser!

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'rest_framework'"

**Solution**: Install Django REST Framework

```bash
pip install djangorestframework==3.14.0
```

### Issue: "Authentication credentials were not provided"

**Solution**: Add token to request header

```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
  http://localhost:8000/api/sessions/active/
```

### Issue: "CORS policy: No 'Access-Control-Allow-Origin' header"

**Solution**: Add frontend URL to CORS_ALLOWED_ORIGINS in settings.py

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
]
```

### Issue: Token not found for user

**Solution**: Create token in shell

```bash
python manage.py shell
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='sarah_jones')
token, _ = Token.objects.get_or_create(user=user)
print(token.key)
```

---

## Complete settings.py Example

```python
"""
Django settings for physio_ai project.

Generated by Django-admin startproject using Django 4.2.0.
"""

from pathlib import Path
from datetime import timedelta
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    
    # Local apps
    'users.apps.UsersConfig',
    'exercises.apps.ExercisesConfig',
    'sessions.apps.SessionsConfig',
    'ai_engine.apps.AiEngineConfig',
    'analytics.apps.AnalyticsConfig',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'physio_ai.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'physio_ai.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'


# ============================================================================
# REST FRAMEWORK CONFIGURATION
# ============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    },
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True


# ============================================================================
# LOGGING
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'api': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}
```

---

## Next Steps

1. ✅ Install DRF and dependencies
2. ✅ Update settings.py
3. ✅ Include API URLs
4. ✅ Create API app
5. ✅ Run migrations
6. ✅ Create user and token
7. ✅ Test endpoints
8. ✅ Deploy to production

---

## Useful Commands

```bash
# Test API in shell
python manage.py shell

# View all tokens
python manage.py shell -c "from rest_framework.authtoken.models import Token; [print(f'{t.user}: {t.key}') for t in Token.objects.all()]"

# Delete token
python manage.py shell -c "from rest_framework.authtoken.models import Token; Token.objects.filter(user__username='sarah_jones').delete()"

# Run server
python manage.py runserver

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files (production)
python manage.py collectstatic --noinput
```

---

## Resources

- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [Token Authentication](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)
- [CORS Headers](https://github.com/adamchainz/django-cors-headers)
- [Settings Reference](https://www.django-rest-framework.org/api-guide/settings/)

---

**Created**: April 20, 2026
**For**: Physio AI Project
**Status**: Ready for Integration ✅
