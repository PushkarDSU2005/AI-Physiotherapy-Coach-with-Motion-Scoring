"""
Advanced Django Models for Physiotherapy AI System

This file contains comprehensive models with detailed explanations
for a physiotherapy AI platform focused on pose detection and exercise tracking.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json


# ============================================================================
# USER MODEL - Extended User Management
# ============================================================================

class User(AbstractUser):
    """
    Custom User model extending Django's built-in User model.
    
    WHY EXTEND USER?
    - Allows future customization without database migrations
    - Industry best practice for Django projects
    - Enables adding physiotherapy-specific fields
    
    FIELDS:
    - username: Unique identifier for login
    - email: Contact and password reset
    - first_name, last_name: Display purposes
    - is_active: Account activation status
    - is_staff: Admin access permission
    """
    
    # Profile Information
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        help_text="User's date of birth for age calculation and health assessments"
    )
    
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        help_text="Contact number for appointment reminders"
    )
    
    # Medical Information
    injury_type = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ('ankle_sprain', 'Ankle Sprain'),
            ('knee_injury', 'Knee Injury'),
            ('shoulder_injury', 'Shoulder Injury'),
            ('back_pain', 'Back Pain'),
            ('rotator_cuff', 'Rotator Cuff'),
            ('acl_injury', 'ACL Injury'),
            ('other', 'Other'),
        ],
        help_text="Primary injury being treated"
    )
    
    fitness_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner - Just starting'),
            ('intermediate', 'Intermediate - Some experience'),
            ('advanced', 'Advanced - Regular exerciser'),
        ],
        default='beginner',
        help_text="Current fitness level for exercise recommendations"
    )
    
    medical_notes = models.TextField(
        blank=True,
        help_text="Allergies, medications, or other medical conditions"
    )
    
    # Preferences
    height_cm = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(50), MaxValueValidator(300)],
        help_text="Height in centimeters for form analysis calibration"
    )
    
    weight_kg = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(20), MaxValueValidator(500)],
        help_text="Weight in kilograms for movement analysis"
    )
    
    # Tracking
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        help_text="User profile picture for identification"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp of last login or session"
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} - {self.get_full_name()}"

    def get_age(self):
        """Calculate user's age from date of birth."""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


# ============================================================================
# EXERCISE MODEL - Exercise Templates with Ideal Joint Angles
# ============================================================================

class Exercise(models.Model):
    """
    Exercise template library with anatomical details and ideal joint angles.
    
    WHY THESE FIELDS?
    - name: Identifies the exercise
    - description: Clear explanation for users
    - muscle_groups: Target areas for recommendations
    - ideal_joint_angles: AI uses these for form assessment
    - duration/reps: Prescribe workout intensity
    - difficulty_level: Match to user fitness level
    - instructions: Prevent injury with proper guidance
    - media_urls: Visual learning support
    - prerequisites: Safety - avoid incompatible exercises
    """
    
    # Basic Information
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Exercise name (e.g., 'Shoulder External Rotation')"
    )
    
    description = models.TextField(
        help_text="Detailed description of what the exercise does"
    )
    
    category = models.CharField(
        max_length=50,
        choices=[
            ('stretching', 'Stretching'),
            ('strengthening', 'Strengthening'),
            ('mobility', 'Mobility'),
            ('balance', 'Balance'),
            ('flexibility', 'Flexibility'),
            ('cardio', 'Cardio'),
            ('coordination', 'Coordination'),
        ],
        help_text="Type of exercise for categorization"
    )
    
    # Difficulty and Prescription
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
        ],
        help_text="Difficulty level relative to other exercises"
    )
    
    target_muscle_groups = models.CharField(
        max_length=500,
        help_text="Comma-separated: 'Rotator Cuff, Deltoid, Trapezius'"
    )
    
    # Duration and Intensity
    duration_seconds = models.IntegerField(
        validators=[MinValueValidator(5), MaxValueValidator(600)],
        help_text="Standard duration in seconds for exercise completion"
    )
    
    recommended_reps = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Recommended repetitions (if applicable)"
    )
    
    recommended_sets = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Recommended number of sets"
    )
    
    rest_seconds_between_sets = models.IntegerField(
        default=60,
        validators=[MinValueValidator(0), MaxValueValidator(600)],
        help_text="Recommended rest time between sets in seconds"
    )
    
    # Anatomical Information for AI
    primary_joints = models.CharField(
        max_length=200,
        help_text="Primary joints involved: 'Shoulder, Elbow' for shoulder press"
    )
    
    secondary_joints = models.CharField(
        max_length=200,
        blank=True,
        help_text="Secondary joints that assist (e.g., 'Wrist' for shoulder press)"
    )
    
    # Ideal Joint Angles (Critical for AI Form Assessment)
    ideal_joint_angles = models.JSONField(
        default=dict,
        help_text="""
        JSON format for ideal joint angles at different phases.
        Example: {
            "phase_1_setup": {"shoulder": 90, "elbow": 90},
            "phase_2_peak": {"shoulder": 170, "elbow": 180},
            "phase_3_return": {"shoulder": 90, "elbow": 90}
        }
        All angles in degrees (0-360).
        """
    )
    
    # Range of Motion and Safety
    safe_angle_range = models.JSONField(
        default=dict,
        help_text="""
        JSON format for safe ranges around ideal angles.
        Example: {
            "shoulder": {"min": 85, "max": 95},
            "elbow": {"min": 85, "max": 95}
        }
        If actual angle falls outside this range, AI flags as form issue.
        """
    )
    
    # Instructions and Safety
    step_by_step_instructions = models.TextField(
        help_text="Numbered steps: '1. Stand with feet...\n2. Hold...\n3. Lift...'"
    )
    
    common_mistakes = models.TextField(
        blank=True,
        help_text="List of common form mistakes to watch for"
    )
    
    safety_notes = models.TextField(
        blank=True,
        help_text="Warnings and contraindications"
    )
    
    # Prerequisites and Progression
    prerequisites = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='prerequisite_for',
        help_text="Exercises that should be mastered first"
    )
    
    progression_to = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='progression_from',
        help_text="Next harder exercise in progression"
    )
    
    # Media Resources
    instruction_video_url = models.URLField(
        blank=True,
        help_text="URL to instructional video"
    )
    
    form_reference_image_url = models.URLField(
        blank=True,
        help_text="URL to image showing correct form"
    )
    
    # Equipment
    equipment_required = models.CharField(
        max_length=200,
        blank=True,
        help_text="E.g., 'Dumbbells 5-10kg' or 'None (Bodyweight)'"
    )
    
    # Status and Tracking
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive exercises won't be recommended"
    )
    
    times_completed_globally = models.IntegerField(
        default=0,
        help_text="Total times completed by all users (for analytics)"
    )
    
    average_difficulty_rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="User ratings of how difficult the exercise is (0-5 stars)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Exercise'
        verbose_name_plural = 'Exercises'
        ordering = ['category', 'difficulty_level', 'name']
        indexes = [
            models.Index(fields=['category', 'difficulty_level']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.difficulty_level})"

    def is_suitable_for_fitness_level(self, user_fitness_level):
        """Check if exercise is appropriate for user's fitness level."""
        fitness_progression = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
        difficulty_progression = {'easy': 1, 'medium': 2, 'hard': 3}
        
        user_level = fitness_progression.get(user_fitness_level, 1)
        exercise_level = difficulty_progression.get(self.difficulty_level, 2)
        
        return exercise_level <= (user_level + 1)  # Allow one level harder


# ============================================================================
# SESSION MODEL - Exercise Session with Scoring and Feedback
# ============================================================================

class Session(models.Model):
    """
    Represents a complete physiotherapy session with multiple exercises.
    
    WHY THESE FIELDS?
    - user: Track who performed the session
    - start_time: Record when session occurred
    - status: Workflow management (pending→in_progress→completed)
    - exercises: Track which exercises were done
    - session_score: Overall quality metric
    - feedback: AI or therapist recommendations
    - duration: Progress metric and prescription adherence
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending - Not Started'),
        ('in_progress', 'In Progress - Currently Running'),
        ('completed', 'Completed - Finished'),
        ('cancelled', 'Cancelled - Not Completed'),
        ('skipped', 'Skipped - User Opted Out'),
    ]
    
    # User and Session Identification
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions',
        help_text="User who performed this session"
    )
    
    title = models.CharField(
        max_length=200,
        help_text="Session title: 'Daily Shoulder Workout' or 'PT Session 5'"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Session notes or instructions from therapist"
    )
    
    # Timing and Status
    start_time = models.DateTimeField(
        help_text="When the session began"
    )
    
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the session ended (null if not completed)"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current state of the session"
    )
    
    scheduled_duration_minutes = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(180)],
        help_text="How long the session was scheduled to last"
    )
    
    # Exercise List
    exercises = models.ManyToManyField(
        Exercise,
        through='SessionExercise',
        related_name='sessions',
        help_text="Exercises included in this session"
    )
    
    # Scoring and Assessment
    overall_session_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall form/quality score for entire session (0-100)"
    )
    
    average_exercise_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Average of all individual exercise scores"
    )
    
    completion_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="% of planned exercises completed"
    )
    
    # Feedback
    ai_generated_feedback = models.TextField(
        blank=True,
        help_text="Automated feedback from AI analysis"
    )
    
    therapist_feedback = models.TextField(
        blank=True,
        help_text="Manual feedback from assigned therapist"
    )
    
    user_notes = models.TextField(
        blank=True,
        help_text="User's own notes about how they felt"
    )
    
    # Improvement Areas (JSON for flexibility)
    improvement_areas = models.JSONField(
        default=list,
        help_text="""
        List of areas flagged for improvement:
        [
            {"area": "Shoulder alignment", "severity": "high", "tip": "Keep shoulder back"},
            {"area": "Elbow extension", "severity": "medium", "tip": "Extend fully"}
        ]
        """
    )
    
    positive_feedback_points = models.JSONField(
        default=list,
        help_text="List of things the user did well"
    )
    
    # Session Quality Metrics
    device_tracking_confidence = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="How confident the camera was in tracking (0-100%)"
    )
    
    video_recording_available = models.BooleanField(
        default=False,
        help_text="Whether session was recorded for review"
    )
    
    video_file = models.FileField(
        upload_to='session_videos/',
        null=True,
        blank=True,
        help_text="Recorded video of the session"
    )
    
    # Metadata
    assigned_therapist = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='supervised_sessions',
        limit_choices_to={'is_staff': True},
        help_text="PT assigned to this session"
    )
    
    session_type = models.CharField(
        max_length=50,
        choices=[
            ('home_unsupervised', 'Home - Unsupervised'),
            ('home_supervised', 'Home - Supervised/Telehealth'),
            ('clinic_session', 'Clinic - In-Person'),
        ],
        help_text="Where and how the session took place"
    )
    
    pain_level_before = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="User reported pain before session (0-10 scale)"
    )
    
    pain_level_after = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="User reported pain after session (0-10 scale)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', '-start_time']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_therapist']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.start_time.strftime('%Y-%m-%d')})"

    def calculate_duration(self):
        """Calculate actual session duration in minutes."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds() / 60
        return None

    def is_overdue(self):
        """Check if session should have ended by now."""
        if self.status not in ['completed', 'cancelled']:
            scheduled_end = self.start_time.replace(
                minute=self.start_time.minute + self.scheduled_duration_minutes
            )
            return timezone.now() > scheduled_end
        return False


# ============================================================================
# SESSION EXERCISE - Individual Exercise Performance Within Session
# ============================================================================

class SessionExercise(models.Model):
    """
    Through model tracking performance of each exercise within a session.
    
    WHY SEPARATE MODEL?
    - Exercise can be in many sessions with different results
    - Tracks individual exercise performance
    - Stores AI analysis specific to that exercise instance
    - Allows historical comparison across sessions
    """
    
    COMPLETION_STATUS = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
        ('failed', 'Failed - Injury/Pain'),
    ]
    
    # Relationships
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='exercise_records',
        help_text="Session this exercise was part of"
    )
    
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='session_performances',
        help_text="The exercise template being performed"
    )
    
    # Order and Sequencing
    order_in_session = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Position in session (1st, 2nd, 3rd...)"
    )
    
    # Performance Tracking
    status = models.CharField(
        max_length=20,
        choices=COMPLETION_STATUS,
        default='not_started',
        help_text="Completion status of this exercise"
    )
    
    start_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When user started this exercise"
    )
    
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When user finished this exercise"
    )
    
    # Execution Metrics
    reps_performed = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of repetitions actually performed"
    )
    
    sets_performed = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of sets actually performed"
    )
    
    target_reps = models.IntegerField(
        null=True,
        blank=True,
        help_text="Target reps for this session instance"
    )
    
    # Form Quality Scoring
    form_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="AI-assessed form quality (0-100)"
    )
    
    consistency_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="How consistent form was across reps (0-100)"
    )
    
    range_of_motion_percentage = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="% of ideal range of motion achieved"
    )
    
    # Joint Angle Tracking
    average_joint_angles = models.JSONField(
        default=dict,
        help_text="""
        Average angles recorded during exercise:
        {
            "shoulder_avg": 92.5,
            "elbow_avg": 175.0,
            "wrist_avg": 45.2
        }
        """
    )
    
    angle_deviations = models.JSONField(
        default=dict,
        help_text="""
        How much user deviated from ideal angles:
        {
            "shoulder_deviation": 2.5,
            "elbow_deviation": -5.0
        }
        Negative = under-extension, Positive = over-extension
        """
    )
    
    # Detected Issues
    form_issues_detected = models.JSONField(
        default=list,
        help_text="""
        List of form issues detected by AI:
        [
            {"issue": "Shoulder not level", "frames_affected": 5, "severity": "medium"},
            {"issue": "Elbow drops", "frames_affected": 10, "severity": "high"}
        ]
        """
    )
    
    # Feedback
    ai_feedback_for_exercise = models.TextField(
        blank=True,
        help_text="Specific feedback for this exercise performance"
    )
    
    # User Experience
    user_difficulty_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="How difficult user found it (1=easy, 5=very hard)"
    )
    
    pain_during_exercise = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Pain level during exercise (0-10)"
    )
    
    user_notes = models.TextField(
        blank=True,
        help_text="User notes about this exercise"
    )
    
    # Video and Data
    frames_analyzed = models.IntegerField(
        default=0,
        help_text="Number of video frames analyzed by AI"
    )
    
    pose_data_captured = models.BooleanField(
        default=True,
        help_text="Whether pose data was successfully captured"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Session Exercise'
        verbose_name_plural = 'Session Exercises'
        ordering = ['session', 'order_in_session']
        unique_together = ['session', 'exercise', 'order_in_session']
        indexes = [
            models.Index(fields=['session']),
            models.Index(fields=['exercise']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.session} - {self.exercise.name} (Rep {self.order_in_session})"

    def get_duration(self):
        """Calculate time spent on this exercise in seconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def get_rep_completion_percentage(self):
        """Calculate % of target reps completed."""
        if self.target_reps and self.target_reps > 0:
            return (self.reps_performed / self.target_reps) * 100
        return 0


# ============================================================================
# PROGRESS TRACKING MODEL - User Progress Over Time
# ============================================================================

class UserProgress(models.Model):
    """
    Aggregated progress tracking for each user.
    
    WHY SEPARATE FROM USER?
    - Denormalized for fast queries/reporting
    - Aggregates data from many sessions/exercises
    - Updated periodically (not on every session)
    - Enables trend analysis and milestone tracking
    """
    
    # User Reference
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='progress',
        help_text="User whose progress is tracked"
    )
    
    # Overall Statistics
    total_sessions_completed = models.IntegerField(
        default=0,
        help_text="Total number of completed sessions"
    )
    
    total_sessions_started = models.IntegerField(
        default=0,
        help_text="Total sessions initiated"
    )
    
    session_completion_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="% of started sessions that were completed"
    )
    
    total_exercises_completed = models.IntegerField(
        default=0,
        help_text="Lifetime count of exercise completions"
    )
    
    total_minutes_exercised = models.IntegerField(
        default=0,
        help_text="Total time spent exercising in minutes"
    )
    
    # Performance Metrics
    average_session_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Average session score across all sessions"
    )
    
    average_exercise_form_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Average form quality across all exercises"
    )
    
    best_session_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Highest session score achieved"
    )
    
    worst_session_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Lowest session score achieved"
    )
    
    # Streak Tracking
    current_streak_days = models.IntegerField(
        default=0,
        help_text="Consecutive days with completed sessions"
    )
    
    longest_streak_days = models.IntegerField(
        default=0,
        help_text="Longest consecutive day streak ever"
    )
    
    last_session_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of most recent session"
    )
    
    # Progression
    exercises_mastered = models.IntegerField(
        default=0,
        help_text="Count of exercises with consistently high scores (>85%)"
    )
    
    avg_difficulty_of_exercises = models.CharField(
        max_length=50,
        choices=[
            ('easy', 'Easy'),
            ('easy-medium', 'Easy to Medium'),
            ('medium', 'Medium'),
            ('medium-hard', 'Medium to Hard'),
            ('hard', 'Hard'),
        ],
        default='easy',
        help_text="Average difficulty level of exercises user is doing"
    )
    
    # Pain and Comfort
    average_pain_before_session = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Average pain level before sessions (0-10)"
    )
    
    average_pain_after_session = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Average pain level after sessions (0-10)"
    )
    
    pain_improvement_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(-100), MaxValueValidator(100)],
        help_text="% improvement in pain (negative = worse)"
    )
    
    # Goals and Milestones
    primary_goal = models.CharField(
        max_length=200,
        blank=True,
        help_text="User's primary rehabilitation goal"
    )
    
    goal_progress_percentage = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Estimated progress toward primary goal"
    )
    
    # Weekly Data (for trending)
    sessions_this_week = models.IntegerField(
        default=0,
        help_text="Sessions completed this week"
    )
    
    average_score_this_week = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Average session score this week"
    )
    
    # Metadata
    membership_duration_days = models.IntegerField(
        default=0,
        help_text="Days since user joined"
    )
    
    estimated_recovery_date = models.DateField(
        null=True,
        blank=True,
        help_text="Estimated date for full recovery based on progress"
    )
    
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="When progress stats were last recalculated"
    )

    class Meta:
        verbose_name = 'User Progress'
        verbose_name_plural = 'User Progress'

    def __str__(self):
        return f"Progress for {self.user.username}"

    def calculate_session_completion_rate(self):
        """Recalculate session completion rate."""
        if self.total_sessions_started > 0:
            self.session_completion_rate = (
                self.total_sessions_completed / self.total_sessions_started
            ) * 100
        else:
            self.session_completion_rate = 0.0
        return self.session_completion_rate

    def calculate_pain_improvement(self):
        """Calculate improvement in pain levels."""
        if self.average_pain_before_session > 0:
            improvement = (
                (self.average_pain_before_session - self.average_pain_after_session)
                / self.average_pain_before_session
            ) * 100
            self.pain_improvement_percentage = improvement
        else:
            self.pain_improvement_percentage = 0.0
        return self.pain_improvement_percentage

    def update_from_latest_sessions(self):
        """Recalculate all metrics from recent session data."""
        from django.db.models import Avg, Count, Q
        
        # Get all sessions for this user
        sessions = Session.objects.filter(user=self.user)
        completed_sessions = sessions.filter(status='completed')
        
        # Update counts
        self.total_sessions_started = sessions.count()
        self.total_sessions_completed = completed_sessions.count()
        
        # Update completion rate
        self.calculate_session_completion_rate()
        
        # Update average scores
        avg_data = completed_sessions.aggregate(
            avg_score=Avg('overall_session_score'),
            max_score=Max('overall_session_score'),
            min_score=Min('overall_session_score'),
        )
        self.average_session_score = avg_data['avg_score'] or 0.0
        self.best_session_score = avg_data['max_score'] or 0.0
        self.worst_session_score = avg_data['min_score'] or 0.0
        
        # Save changes
        self.save()


# ============================================================================
# DAILY METRICS MODEL - Daily Aggregated Statistics
# ============================================================================

class DailyMetrics(models.Model):
    """
    Daily snapshot of user metrics for trend analysis.
    
    WHY DAILY AGGREGATION?
    - Fast loading of progress charts
    - Stores historical data without querying all sessions
    - One record per user per day for efficient queries
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='daily_metrics',
        help_text="User these metrics are for"
    )
    
    date = models.DateField(
        help_text="Date of the metrics"
    )
    
    # Session Activity
    sessions_completed = models.IntegerField(
        default=0,
        help_text="Number of sessions completed this day"
    )
    
    exercises_completed = models.IntegerField(
        default=0,
        help_text="Total exercises completed this day"
    )
    
    total_minutes_exercised = models.IntegerField(
        default=0,
        help_text="Total exercise time in minutes"
    )
    
    # Performance
    average_session_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Average score for sessions that day"
    )
    
    average_form_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Average form quality score"
    )
    
    # Consistency
    completion_rate = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="% of scheduled sessions completed"
    )
    
    # Pain
    average_pain_before = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Average pain before sessions (0-10)"
    )
    
    average_pain_after = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Average pain after sessions (0-10)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Daily Metrics'
        verbose_name_plural = 'Daily Metrics'
        unique_together = ['user', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', '-date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date}"


# ============================================================================
# POSE ANALYSIS MODEL - Frame-by-Frame AI Analysis
# ============================================================================

class PoseAnalysis(models.Model):
    """
    Stores AI analysis for each video frame during exercise.
    
    WHY THIS MODEL?
    - One record per frame enables detailed form assessment
    - Tracks joint angles over time
    - Identifies specific moments of poor form
    - Enables AI to compare form progression across sessions
    """
    
    # Related Data
    session_exercise = models.ForeignKey(
        SessionExercise,
        on_delete=models.CASCADE,
        related_name='pose_analyses',
        help_text="The exercise instance being analyzed"
    )
    
    # Frame Information
    frame_number = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Sequential frame number in the video"
    )
    
    timestamp_seconds = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text="Time in seconds from start of exercise"
    )
    
    # Joint Angles (Detected by AI)
    detected_joint_angles = models.JSONField(
        default=dict,
        help_text="""
        Actual joint angles detected in this frame:
        {
            "shoulder": 95.2,
            "elbow": 168.7,
            "wrist": 12.3,
            "hip": 90.0
        }
        """
    )
    
    # Comparison to Ideal
    angle_errors = models.JSONField(
        default=dict,
        help_text="""
        Difference between detected and ideal angles:
        {
            "shoulder": 5.2,  # +5.2° from ideal
            "elbow": -11.3    # -11.3° from ideal (insufficient extension)
        }
        """
    )
    
    # Confidence Scores
    pose_detection_confidence = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="How confident AI is in pose detection (0-100%)"
    )
    
    individual_joint_confidence = models.JSONField(
        default=dict,
        help_text="""
        Per-joint confidence scores:
        {
            "shoulder": 95.5,
            "elbow": 87.3,
            "wrist": 72.1
        }
        """
    )
    
    # Issues Detected
    form_issues = models.JSONField(
        default=list,
        help_text="""
        Form problems detected in this frame:
        [
            {"joint": "shoulder", "issue": "too_high", "severity": "medium"},
            {"joint": "elbow": "not_extended", "severity": "high"}
        ]
        """
    )
    
    # Body Position (for context)
    body_position_description = models.CharField(
        max_length=200,
        blank=True,
        help_text="Text description: 'Peak contraction' or 'Lowering'"
    )
    
    is_peak_position = models.BooleanField(
        default=False,
        help_text="Whether this frame is at the exercise's peak position"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pose Analysis'
        verbose_name_plural = 'Pose Analyses'
        ordering = ['session_exercise', 'frame_number']
        unique_together = ['session_exercise', 'frame_number']
        indexes = [
            models.Index(fields=['session_exercise', 'frame_number']),
        ]

    def __str__(self):
        return f"{self.session_exercise} - Frame {self.frame_number}"

    def get_overall_form_quality(self):
        """Calculate form quality based on angle errors and confidence."""
        if not self.angle_errors:
            return 100.0
        
        # Calculate average absolute angle error
        errors = [abs(err) for err in self.angle_errors.values()]
        avg_error = sum(errors) / len(errors) if errors else 0
        
        # Convert to 0-100 score (lower error = higher score)
        # Assume ±20° is failing (0), ±0° is perfect (100)
        form_score = max(0, 100 - (avg_error * 5))
        
        # Adjust by confidence
        avg_confidence = sum(self.individual_joint_confidence.values()) / len(
            self.individual_joint_confidence
        ) if self.individual_joint_confidence else 100
        
        adjusted_score = form_score * (avg_confidence / 100)
        
        return min(100, adjusted_score)


# ============================================================================
# MILESTONE AND ACHIEVEMENT TRACKING
# ============================================================================

class Milestone(models.Model):
    """
    Track user achievements and milestones for gamification.
    """
    
    MILESTONE_TYPES = [
        ('streak', 'Streak - Consecutive days'),
        ('session_count', 'Session milestone'),
        ('score_threshold', 'Score achievement'),
        ('exercise_mastery', 'Exercise mastery'),
        ('pain_improvement', 'Pain reduction'),
        ('recovery_phase', 'Recovery phase reached'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='milestones'
    )
    
    milestone_type = models.CharField(max_length=50, choices=MILESTONE_TYPES)
    
    description = models.CharField(max_length=200, help_text="User-friendly milestone description")
    
    achievement_date = models.DateTimeField(auto_now_add=True)
    
    icon_emoji = models.CharField(max_length=10, default='🎉', help_text="Emoji for display")
    
    reward_points = models.IntegerField(default=10, help_text="Gamification points awarded")

    class Meta:
        ordering = ['-achievement_date']

    def __str__(self):
        return f"{self.user.username} - {self.description}"
