# File Explanations - Physio AI Project

## Core Project Files

### `manage.py`
**Purpose**: Django's command-line management tool.
**Simple Explanation**: Like a remote control for your Django project. You use commands like `python manage.py runserver` to start the server.
**Key Commands**:
- `runserver` - Start development server
- `makemigrations` - Create database changes
- `migrate` - Apply database changes to the database
- `createsuperuser` - Create admin account

---

### `physio_ai/settings.py`
**Purpose**: Central configuration for the entire Django project.
**Simple Explanation**: This is like the settings/preferences file for your project. It tells Django:
- Which apps to use
- What database to use (SQLite, PostgreSQL, etc.)
- Security settings
- Where to find templates and static files
**Key Settings**:
- `DEBUG = True` - Shows detailed errors (set to False for production)
- `SECRET_KEY` - Security token (keep it secret!)
- `INSTALLED_APPS` - List of all active apps
- `DATABASES` - Database configuration
- `ALLOWED_HOSTS` - Which domains can access the site

---

### `physio_ai/urls.py`
**Purpose**: Main URL router for the entire project.
**Simple Explanation**: When someone visits a URL like `/users/`, this file decides which app handles it.
**How It Works**: 
```
/users/          → routes to users app
/exercises/      → routes to exercises app
/sessions/       → routes to sessions app
/ai/             → routes to ai_engine app
/analytics/      → routes to analytics app
/admin/          → Django admin panel
```

---

### `physio_ai/wsgi.py` & `asgi.py`
**Purpose**: Application entry points for web servers.
**Simple Explanation**: 
- WSGI = Traditional web server format (production use)
- ASGI = Modern async web server format (real-time features)
**You won't edit these directly** - They're used when deploying to production servers.

---

## App Structure

Each app (users, exercises, sessions, ai_engine, analytics) contains:

### `models.py`
**Purpose**: Defines database tables and fields.
**Simple Explanation**: Think of it as creating blueprints for your database tables.
**Example**: 
```python
class Exercise(models.Model):
    name = CharField()           # Like a spreadsheet column for exercise name
    difficulty_level = CharField()
    duration_seconds = IntegerField()
```
When you run `makemigrations`, Django converts this into actual database tables.

---

### `views.py`
**Purpose**: Contains logic to process requests and return responses.
**Simple Explanation**: Views are like workers that handle customer requests. They fetch data from the database and return HTML or JSON.
**Example Flow**:
1. User visits `/exercises/`
2. `ExerciseListView` runs
3. It queries the database for exercises
4. It returns an HTML page with the exercise list

---

### `urls.py`
**Purpose**: Routes URLs specific to this app.
**Simple Explanation**: Each app has its own URL router that handles URLs for that app.
**Example**:
```python
path('', views.ExerciseListView.as_view())    # /exercises/
path('<int:exercise_id>/', views.ExerciseDetailView.as_view())  # /exercises/1/
```

---

### `admin.py`
**Purpose**: Customizes how your data appears in Django's admin panel.
**Simple Explanation**: Makes the admin panel user-friendly for managing data.
**Example Features**:
- Which columns to display
- Search functionality
- Filtering options
- Read-only fields

You can manage all your data at `/admin/` without writing extra code!

---

### `apps.py`
**Purpose**: App configuration file.
**Simple Explanation**: Just metadata about the app. Usually auto-generated and you don't need to edit it.

---

### `__init__.py`
**Purpose**: Makes the folder a Python package.
**Simple Explanation**: Python needs this file to treat a folder as a package. It can be empty.

---

## Project Structure File

### `requirements.txt`
**Purpose**: Lists all Python packages needed for the project.
**Simple Explanation**: Like a shopping list for Python packages.
**How to Use**:
```bash
pip install -r requirements.txt
```
This installs all packages listed in the file.
**Current Packages**:
- Django 4.2.0 - The web framework
- sqlparse - SQL parsing library
- asgiref - ASGI support

---

### `README.md`
**Purpose**: Project documentation.
**Simple Explanation**: A guide for anyone (including future you!) to understand and use the project.
**Contains**:
- Installation instructions
- How to run the project
- Project structure overview
- Common commands
- Troubleshooting tips

---

### `.gitignore`
**Purpose**: Tells Git which files to ignore.
**Simple Explanation**: Some files (like `db.sqlite3`, `__pycache__`) shouldn't be uploaded to Git. This file tells Git to ignore them.
**Common Ignored Items**:
- Virtual environment folder (`venv/`)
- Database files (`*.sqlite3`)
- Python cache (`__pycache__/`)
- Environment variables (`.env`)

---

## Database Models at a Glance

### Users App
- **UserProfile**: Extends Django User with age, fitness level, injury history

### Exercises App
- **Exercise**: Exercise templates with name, difficulty, duration, instructions

### Sessions App
- **Session**: A complete physiotherapy session
- **SessionExercise**: Individual exercises within a session (tracks form scores, completion)

### AI Engine App
- **AIModel**: Different AI models for pose detection
- **PoseAnalysis**: Frame-by-frame analysis results (form scores, detected joints, recommendations)
- **AIFeedback**: AI-generated feedback for users

### Analytics App
- **UserProgress**: Overall progress (sessions completed, streaks, average scores)
- **DailyMetrics**: Daily aggregated statistics
- **ExerciseStatistics**: Exercise popularity and average performance
- **Report**: Weekly/monthly progress reports

---

## Quick Start Commands

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate    # Windows
source venv/bin/activate # macOS/Linux

# 3. Install requirements
pip install -r requirements.txt

# 4. Create database tables
python manage.py makemigrations
python manage.py migrate

# 5. Create admin account
python manage.py createsuperuser

# 6. Run the server
python manage.py runserver

# 7. Visit admin panel
# Go to: http://localhost:8000/admin/
```

---

## Migration System Explained

**What is a migration?**
It's a way to track changes to your database structure.

**How it works**:
1. You modify a model (e.g., add a new field)
2. Run `python manage.py makemigrations` - Django creates a migration file
3. Run `python manage.py migrate` - Django applies the change to the database
4. Git can track these migration files to version control your database schema

**Example**:
```bash
# You add a new field to the Exercise model
python manage.py makemigrations
# Output: Migrations for 'exercises': 0002_add_new_field.py

python manage.py migrate
# Database is now updated!
```

---

## Next Steps to Extend the Project

1. **Create Templates** - HTML files for displaying data
   - Create `templates/` folder in each app
   - Create `.html` files matching your views

2. **Add Forms** - For user input
   - Create `forms.py` in each app
   - Create forms for creating/editing data

3. **Add API** - Make it accessible to mobile apps
   - Use Django REST Framework
   - Create serializers and viewsets

4. **Add Authentication** - Secure login system
   - Use Django's built-in authentication
   - Add login/logout views and decorators

5. **Add Tests** - Ensure everything works
   - Create `tests.py` in each app
   - Write unit and integration tests

---

## Key Concepts

**Model**: Blueprint for database table
**View**: Logic to handle requests
**URL**: Route to connect URLs to views
**Admin**: Web interface to manage data
**Migration**: Track database schema changes
**App**: Self-contained piece of functionality

---

Created: April 20, 2026
Project: Physio AI - Physiotherapy AI System
