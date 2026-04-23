from django.db import models


class Exercise(models.Model):
    """
    Exercise templates for the physiotherapy AI system.
    Defines exercises that users can perform in sessions.
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    duration_seconds = models.IntegerField(help_text="Duration in seconds")
    muscle_groups = models.CharField(
        max_length=500,
        help_text="Comma-separated muscle groups targeted"
    )
    instructions = models.TextField(help_text="Step-by-step instructions")
    image_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Exercise'
        verbose_name_plural = 'Exercises'
        ordering = ['name']
