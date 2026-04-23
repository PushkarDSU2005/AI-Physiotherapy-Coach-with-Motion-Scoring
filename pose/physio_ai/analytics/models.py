from django.db import models
from django.contrib.auth.models import User


class UserProgress(models.Model):
    """
    Tracks overall progress metrics for each user.
    Aggregates data from sessions and exercises.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='progress')
    total_sessions_completed = models.IntegerField(default=0)
    total_exercises_completed = models.IntegerField(default=0)
    average_form_score = models.FloatField(default=0.0, help_text="Average form score 0-100")
    total_minutes_exercised = models.IntegerField(default=0)
    current_streak_days = models.IntegerField(default=0, help_text="Current consecutive days exercising")
    longest_streak_days = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Progress - {self.user.username}"

    class Meta:
        verbose_name = 'User Progress'
        verbose_name_plural = 'User Progress'


class DailyMetrics(models.Model):
    """
    Stores daily aggregated metrics for analytics and reporting.
    One record per user per day.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_metrics')
    date = models.DateField()
    sessions_completed = models.IntegerField(default=0)
    exercises_completed = models.IntegerField(default=0)
    average_form_score = models.FloatField(default=0.0)
    total_minutes_exercised = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    class Meta:
        verbose_name = 'Daily Metrics'
        verbose_name_plural = 'Daily Metrics'
        unique_together = ['user', 'date']
        ordering = ['-date']


class ExerciseStatistics(models.Model):
    """
    Tracks statistics for each exercise across all users.
    Used for analytics and exercise recommendations.
    """
    exercise_id = models.IntegerField(help_text="ID of the exercise")
    exercise_name = models.CharField(max_length=200)
    total_times_completed = models.IntegerField(default=0)
    average_form_score = models.FloatField(default=0.0)
    average_duration_seconds = models.IntegerField(default=0)
    popularity_score = models.FloatField(default=0.0, help_text="How often exercise is used")
    difficulty_distribution = models.JSONField(
        default=dict,
        help_text="Distribution of difficulty levels in sessions"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.exercise_name

    class Meta:
        verbose_name = 'Exercise Statistics'
        verbose_name_plural = 'Exercise Statistics'


class Report(models.Model):
    """
    Generated reports for users to track their progress.
    Can be weekly, monthly, or custom reports.
    """
    REPORT_TYPES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    summary = models.TextField()
    metrics = models.JSONField(help_text="Report metrics and data")
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    class Meta:
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-generated_at']
