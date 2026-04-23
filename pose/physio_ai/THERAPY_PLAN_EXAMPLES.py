"""
THERAPY PLAN GENERATION - USAGE EXAMPLES & SCENARIOS

Real-world examples showing how to use the therapy plan generation system.
"""

import os
import sys
import json
from typing import Dict, List
from datetime import datetime

# ============================================================
# SCENARIO 1: Generate a Knee Pain Recovery Plan
# ============================================================

def scenario_1_knee_pain():
    """
    Alice is a 35-year-old runner who injured her knee during a marathon.
    She wants a 4-week recovery plan to gradually return to running.
    """
    print("=" * 70)
    print("SCENARIO 1: Knee Pain Recovery Plan")
    print("=" * 70)
    
    from django.contrib.auth.models import User
    from therapy_plans.services import generate_therapy_plan
    
    # Get or create user
    user, created = User.objects.get_or_create(
        username='alice_runner',
        defaults={'email': 'alice@example.com', 'first_name': 'Alice'}
    )
    
    # Set up user profile with fitness information
    if not hasattr(user, 'profile'):
        from users.models import UserProfile
        profile = UserProfile.objects.create(
            user=user,
            age=35,
            fitness_level='advanced'  # She's an experienced runner
        )
    
    # Generate personalized plan
    print("\n📋 Generating therapy plan...")
    plan, message = generate_therapy_plan(
        user=user,
        injury_type="Knee pain - ACL strain",
        injury_severity="moderate",
        duration_weeks=4,
        difficulty_level="intermediate",
        goals=[
            "Reduce inflammation and pain",
            "Restore full range of motion",
            "Rebuild strength for running",
            "Return to marathon training"
        ]
    )
    
    if plan:
        print(f"\n✅ SUCCESS: Plan created!")
        print(f"   Plan ID: {plan.id}")
        print(f"   Title: {plan.title}")
        print(f"   Duration: {plan.duration_weeks} weeks")
        print(f"   Difficulty: {plan.difficulty_level}")
        print(f"   Status: {plan.status}")
        print(f"\n📅 Plan Details:")
        print(f"   Start Date: {plan.start_date}")
        print(f"   End Date: {plan.end_date}")
        print(f"   Goals: {', '.join(plan.goals)}")
        
        # Show sample exercises from week 1
        week_1 = plan.weekly_plan.get('week_1', {})
        print(f"\n💪 Week 1 Monday Exercises:")
        for exercise in week_1.get('monday', []):
            print(f"   - {exercise['name']} ({exercise['sets']}x{exercise['reps']})")
        
        return plan
    else:
        print(f"\n❌ FAILED: {message}")
        return None


# ============================================================
# SCENARIO 2: Shoulder Injury - Beginner to Intermediate
# ============================================================

def scenario_2_shoulder_injury():
    """
    Bob is a 45-year-old desk worker with rotator cuff pain.
    He has minimal exercise experience and needs a gentle progression plan.
    """
    print("\n" + "=" * 70)
    print("SCENARIO 2: Rotator Cuff Recovery - Beginner Level")
    print("=" * 70)
    
    from django.contrib.auth.models import User
    from therapy_plans.services import generate_therapy_plan
    
    user, created = User.objects.get_or_create(
        username='bob_desk',
        defaults={'email': 'bob@example.com', 'first_name': 'Bob'}
    )
    
    # Create beginner profile
    if not hasattr(user, 'profile') or user.profile.fitness_level == 'intermediate':
        from users.models import UserProfile
        profile = UserProfile.objects.filter(user=user).first()
        if not profile:
            profile = UserProfile.objects.create(user=user)
        profile.age = 45
        profile.fitness_level = 'beginner'
        profile.save()
    
    print("\n📋 Generating therapy plan for beginner...")
    plan, message = generate_therapy_plan(
        user=user,
        injury_type="Rotator cuff strain",
        injury_severity="mild",
        duration_weeks=6,  # Longer for careful progression
        difficulty_level="beginner",  # Start gentle
        goals=[
            "Reduce shoulder pain when typing",
            "Improve arm lifting capacity",
            "Prevent re-injury"
        ]
    )
    
    if plan:
        print(f"\n✅ SUCCESS: Beginner rotator cuff plan created!")
        print(f"   Plan ID: {plan.id}")
        print(f"   Duration: {plan.duration_weeks} weeks")
        
        # Show progression strategy
        if plan.progression_strategy:
            print(f"\n📈 Progression Strategy:")
            print(f"   {plan.progression_strategy[:200]}...")
        
        # Show safety precautions
        print(f"\n⚠️  Safety Precautions:")
        for precaution in plan.precautions[:3]:
            print(f"   • {precaution}")
        
        return plan
    else:
        print(f"\n❌ FAILED: {message}")
        return None


# ============================================================
# SCENARIO 3: Compare Two Different Plans
# ============================================================

def scenario_3_compare_plans():
    """
    Carol wants to compare two different plans for her back pain
    to choose which approach is better for her needs.
    """
    print("\n" + "=" * 70)
    print("SCENARIO 3: Compare Multiple Plans")
    print("=" * 70)
    
    from django.contrib.auth.models import User
    from therapy_plans.models import TherapyPlan
    from therapy_plans.services import generate_therapy_plan
    
    user, created = User.objects.get_or_create(
        username='carol_back',
        defaults={'email': 'carol@example.com', 'first_name': 'Carol'}
    )
    
    # Generate first plan - Conservative approach
    print("\n📋 Plan 1: Conservative approach...")
    plan1, _ = generate_therapy_plan(
        user=user,
        injury_type="Lower back pain",
        injury_severity="moderate",
        duration_weeks=6,
        difficulty_level="beginner",
        goals=["Pain relief", "Flexibility", "Stability"]
    )
    
    # Generate second plan - Aggressive approach
    print("📋 Plan 2: Progressive/Aggressive approach...")
    plan2, _ = generate_therapy_plan(
        user=user,
        injury_type="Lower back pain",
        injury_severity="mild",
        duration_weeks=4,
        difficulty_level="intermediate",
        goals=["Strength building", "Return to activity", "Long-term health"]
    )
    
    if plan1 and plan2:
        print(f"\n📊 COMPARISON RESULTS:")
        print(f"\n  Plan 1 (Conservative):")
        print(f"    • ID: {plan1.id}")
        print(f"    • Duration: {plan1.duration_weeks} weeks")
        print(f"    • Difficulty: {plan1.difficulty_level}")
        print(f"    • Goals: {len(plan1.goals)}")
        print(f"    • Precautions: {len(plan1.precautions)}")
        
        print(f"\n  Plan 2 (Progressive):")
        print(f"    • ID: {plan2.id}")
        print(f"    • Duration: {plan2.duration_weeks} weeks")
        print(f"    • Difficulty: {plan2.difficulty_level}")
        print(f"    • Goals: {len(plan2.goals)}")
        print(f"    • Precautions: {len(plan2.precautions)}")
        
        return [plan1, plan2]
    
    return None


# ============================================================
# SCENARIO 4: API Integration Example
# ============================================================

def scenario_4_api_integration():
    """
    Shows how to integrate with REST API endpoints
    """
    print("\n" + "=" * 70)
    print("SCENARIO 4: REST API Integration")
    print("=" * 70)
    
    import requests
    
    # Assuming you have a running Django server at localhost:8000
    BASE_URL = "http://localhost:8000/api"
    
    # You would need a valid JWT token
    TOKEN = "your-jwt-token-here"
    HEADERS = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("\n📡 API Example Requests:\n")
    
    # Example 1: Generate Plan
    print("1️⃣  POST /therapy-plans/generate/")
    generate_request = {
        "injury_type": "Ankle sprain",
        "injury_severity": "moderate",
        "duration_weeks": 3,
        "difficulty_level": "intermediate",
        "goals": ["Reduce swelling", "Restore balance", "Return to walking"]
    }
    print(f"   Request: {json.dumps(generate_request, indent=6)}")
    print(f"   Response: 201 Created")
    print(f"   Returns: TherapyPlan object with ID, title, weekly_plan, etc.")
    
    # Example 2: Get Weekly Schedule
    print("\n2️⃣  GET /therapy-plans/42/weekly-schedule/")
    print(f"   Response: 200 OK")
    print(f"   Returns: Organized weekly schedule with exercises by day")
    
    # Example 3: Update Progress
    print("\n3️⃣  POST /therapy-plans/42/update-progress/")
    progress_request = {
        "progress_score": 75.0,
        "status": "active",
        "notes": "Significant improvement, swelling reduced"
    }
    print(f"   Request: {json.dumps(progress_request, indent=6)}")
    print(f"   Response: 200 OK")
    
    # Example 4: Compare Plans
    print("\n4️⃣  GET /therapy-plans/42/comparison/?compare_with=43")
    print(f"   Response: 200 OK")
    print(f"   Returns: Comparison metrics between two plans")
    
    # Example 5: Export Plan
    print("\n5️⃣  GET /therapy-plans/42/export/?format=json")
    print(f"   Response: 200 OK")
    print(f"   Returns: Full plan data in JSON format")


# ============================================================
# SCENARIO 5: Tracking Progress Over Time
# ============================================================

def scenario_5_progress_tracking():
    """
    Shows how to track progress through a therapy plan over multiple weeks
    """
    print("\n" + "=" * 70)
    print("SCENARIO 5: Progress Tracking Over Time")
    print("=" * 70)
    
    from django.contrib.auth.models import User
    from therapy_plans.models import TherapyPlan
    from datetime import timedelta
    
    # Simulate tracking progress updates
    user = User.objects.get(username='alice_runner')
    plan = TherapyPlan.objects.filter(user=user, status='active').first()
    
    if not plan:
        print("No active plan found. Create one first using scenario 1.")
        return
    
    progress_updates = [
        {'week': 1, 'score': 20, 'notes': 'Starting recovery, significant pain'},
        {'week': 2, 'score': 40, 'notes': 'Pain reduced by 50%, increased mobility'},
        {'week': 3, 'score': 65, 'notes': 'Can walk without pain, light exercises ok'},
        {'week': 4, 'score': 85, 'notes': 'Ready to return to light running'},
    ]
    
    print(f"\n📊 Tracking progress for plan: {plan.title}\n")
    print(f"{'Week':<6} {'Score':<10} {'Status':<20} {'Notes':<40}")
    print("-" * 76)
    
    for update in progress_updates:
        week = update['week']
        score = update['score']
        
        # Determine status based on score
        if score < 30:
            status = "Just Started"
        elif score < 50:
            status = "Early Progress"
        elif score < 75:
            status = "Good Progress"
        else:
            status = "Near Complete"
        
        print(f"{week:<6} {score:<10.0f}% {status:<20} {update['notes']:<40}")
        
        # In real app, you would update:
        # plan.progress_score = score
        # plan.save()
    
    print(f"\n✅ Final Status: {plan.injury_type} Recovery Plan Complete!")
    print(f"   User can now return to normal activities with precautions.")


# ============================================================
# SCENARIO 6: Bulk Plan Generation for Multiple Users
# ============================================================

def scenario_6_bulk_generation():
    """
    Generate therapy plans for multiple users with similar injuries
    """
    print("\n" + "=" * 70)
    print("SCENARIO 6: Bulk Plan Generation")
    print("=" * 70)
    
    from django.contrib.auth.models import User
    from therapy_plans.services import generate_therapy_plan
    
    # List of users and their injuries
    users_to_process = [
        ('user1', 'Knee pain', 'moderate'),
        ('user2', 'Shoulder pain', 'mild'),
        ('user3', 'Lower back pain', 'moderate'),
    ]
    
    print(f"\n📋 Generating plans for {len(users_to_process)} users...\n")
    
    created_plans = []
    for username, injury, severity in users_to_process:
        user, created = User.objects.get_or_create(username=username)
        
        print(f"  → Processing {username}... ", end='')
        
        plan, message = generate_therapy_plan(
            user=user,
            injury_type=injury,
            injury_severity=severity,
            duration_weeks=4,
            difficulty_level="intermediate"
        )
        
        if plan:
            created_plans.append(plan)
            print(f"✅ Plan {plan.id} created")
        else:
            print(f"❌ Failed: {message}")
    
    print(f"\n✅ Generated {len(created_plans)} plans successfully!")
    print(f"\nSummary:")
    for plan in created_plans:
        print(f"  • {plan.user.username}: {plan.injury_type} (ID: {plan.id})")


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    import os
    import django
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'physio_ai.settings')
    django.setup()
    
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "THERAPY PLAN GENERATION - USAGE EXAMPLES" + " " * 14 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Run scenarios
    try:
        # Scenario 1: Knee pain recovery
        plan1 = scenario_1_knee_pain()
        
        # Scenario 2: Shoulder injury beginner
        plan2 = scenario_2_shoulder_injury()
        
        # Scenario 3: Compare plans
        plans_compared = scenario_3_compare_plans()
        
        # Scenario 4: API Integration example
        scenario_4_api_integration()
        
        # Scenario 5: Progress tracking
        scenario_5_progress_tracking()
        
        # Scenario 6: Bulk generation
        # Uncomment to run (may use API credits)
        # scenario_6_bulk_generation()
        
        print("\n" + "=" * 70)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running scenarios: {str(e)}")
        import traceback
        traceback.print_exc()
