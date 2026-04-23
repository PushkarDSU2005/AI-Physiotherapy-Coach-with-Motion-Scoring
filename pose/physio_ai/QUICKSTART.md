# Quick Start Guide - Get Running in 5 Minutes

## Step 1: Prepare Your Environment

### Windows
```bash
# Navigate to project folder
cd c:\Users\Abhinav Mehta\Downloads\pose\physio_ai

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate
```

### macOS/Linux
```bash
cd ~/Downloads/pose/physio_ai
python3 -m venv venv
source venv/bin/activate
```

## Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 3: Set Up Database
```bash
# Create tables from models
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate
```

**What's happening**: Django is creating the database structure (tables) based on your models.

## Step 4: Create Admin Account
```bash
python manage.py createsuperuser
```

**Follow prompts**:
- Username: `admin`
- Email: `admin@example.com`
- Password: Create a password

## Step 5: Start the Server
```bash
python manage.py runserver
```

**Output**: You'll see something like:
```
Starting development server at http://127.0.0.1:8000/
Press CTRL+C to quit.
```

## Step 6: Access the Application

### Admin Panel
- **URL**: http://localhost:8000/admin/
- **Login**: Use the credentials from Step 4
- **What you can do**: Manage users, exercises, sessions, analytics

### App URLs
- Users: http://localhost:8000/users/
- Exercises: http://localhost:8000/exercises/
- Sessions: http://localhost:8000/sessions/
- AI Engine: http://localhost:8000/ai/
- Analytics: http://localhost:8000/analytics/

## Common Issues & Solutions

### Issue: "Command not found: python"
**Solution**: Use `python3` instead of `python` on macOS/Linux

### Issue: "Module not found: django"
**Solution**: Make sure virtual environment is activated
```bash
# Activate it
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

### Issue: "Port 8000 already in use"
**Solution**: Use a different port
```bash
python manage.py runserver 8001
```

### Issue: "Database doesn't exist"
**Solution**: Run migrations again
```bash
python manage.py migrate
```

### Issue: "Admin account doesn't work"
**Solution**: Create a new superuser
```bash
python manage.py createsuperuser
```

## How to Stop the Server
Press `CTRL+C` in the terminal where the server is running.

## Adding Sample Data

### In Admin Panel (Easiest)
1. Go to http://localhost:8000/admin/
2. Click "Exercises" → "Add Exercise"
3. Fill in the form and save
4. Repeat for other models

### Using Django Shell (Advanced)
```bash
python manage.py shell
```

Then in the Python shell:
```python
from exercises.models import Exercise

# Create an exercise
exercise = Exercise.objects.create(
    name="Shoulder Press",
    description="Push weight above head",
    difficulty_level="intermediate",
    duration_seconds=60,
    muscle_groups="Shoulders, Triceps",
    instructions="1. Stand with feet apart\n2. Hold weights at shoulder height\n3. Push up"
)

# Create a user
from django.contrib.auth.models import User
user = User.objects.create_user(
    username='john',
    email='john@example.com',
    password='password123'
)

# View all exercises
Exercise.objects.all()

# Exit shell
exit()
```

## File Structure Quick Reference

```
physio_ai/
├── manage.py              # Run: python manage.py ...
├── requirements.txt       # pip install -r requirements.txt
├── settings.py            # Project configuration
│
├── users/                 # User management
├── exercises/             # Exercise library
├── sessions/              # Exercise sessions
├── ai_engine/             # AI analysis
└── analytics/             # Progress tracking
```

## Important Django Commands

```bash
# Run server
python manage.py runserver

# Create database changes
python manage.py makemigrations

# Apply database changes
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Open interactive Python shell
python manage.py shell

# Run tests
python manage.py test

# Create empty app
python manage.py startapp app_name

# Collect static files (production)
python manage.py collectstatic

# Create a backup
python manage.py dumpdata > backup.json

# Restore from backup
python manage.py loaddata backup.json
```

## Development Workflow

### Day 1: Set Up
```bash
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Daily: Start Development
```bash
venv\Scripts\activate
python manage.py runserver
```

### When You Modify Models
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Next Steps

1. **Read [FILE_GUIDE.md](FILE_GUIDE.md)** - Detailed explanation of each file
2. **Read [README.md](README.md)** - Complete documentation
3. **Add sample data** in admin panel
4. **Create templates** for your views
5. **Add static files** (CSS, JavaScript, images)

## Useful Links

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Models Documentation](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [Django Views Documentation](https://docs.djangoproject.com/en/stable/topics/http/views/)
- [Django Admin Documentation](https://docs.djangoproject.com/en/stable/ref/contrib/admin/)

## Deactivate Virtual Environment

When you're done working:
```bash
deactivate
```

---

**You're all set! Start developing! 🚀**
