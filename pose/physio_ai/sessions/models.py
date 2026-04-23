from django.db import models
from django.contrib.auth.models import User
from exercises.models import Exercise


class Session(models.Model):
    """
    Represents a physiotherapy session where a user completes exercises.
    Tracks session metadata and results.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    exercises = models.ManyToManyField(Exercise, through='SessionExercise', related_name='sessions')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    class Meta:
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'
        ordering = ['-start_time']


class SessionExercise(models.Model):
    """
    Through model for the many-to-many relationship between sessions and exercises.
    Tracks which exercises are in a session and their completion status.
    """
    COMPLETION_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='exercise_records')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.IntegerField(help_text="Order in the session")
    status = models.CharField(max_length=20, choices=COMPLETION_CHOICES, default='not_started')
    reps_completed = models.IntegerField(default=0, null=True, blank=True)
    form_score = models.FloatField(null=True, blank=True, help_text="0-100 form quality score from AI")
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.session} - {self.exercise.name}"

    class Meta:
        verbose_name = 'Session Exercise'
        verbose_name_plural = 'Session Exercises'
        unique_together = ['session', 'exercise']
