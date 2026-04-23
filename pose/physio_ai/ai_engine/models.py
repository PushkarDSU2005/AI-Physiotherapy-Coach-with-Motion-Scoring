from django.db import models
from django.contrib.auth.models import User
from sessions.models import SessionExercise


class AIModel(models.Model):
    """
    Tracks different AI models and their versions used for pose detection/analysis.
    """
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=50)
    model_type = models.CharField(
        max_length=50,
        choices=[
            ('pose_detection', 'Pose Detection'),
            ('form_analysis', 'Form Analysis'),
            ('movement_tracking', 'Movement Tracking'),
        ]
    )
    accuracy_score = models.FloatField(help_text="Accuracy percentage 0-100")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} v{self.version}"

    class Meta:
        verbose_name = 'AI Model'
        verbose_name_plural = 'AI Models'
        unique_together = ['name', 'version']


class PoseAnalysis(models.Model):
    """
    Stores AI analysis results for user poses during exercise execution.
    Each analysis represents one pose frame captured during an exercise.
    """
    session_exercise = models.ForeignKey(
        SessionExercise,
        on_delete=models.CASCADE,
        related_name='pose_analyses'
    )
    ai_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True)
    frame_number = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Analysis results
    form_score = models.FloatField(help_text="Form quality 0-100")
    confidence_level = models.FloatField(help_text="Model confidence 0-100")
    detected_joints = models.JSONField(default=dict, help_text="JSON with joint positions")
    issues_detected = models.JSONField(default=list, help_text="List of form issues detected")
    recommendations = models.TextField(blank=True)

    def __str__(self):
        return f"Pose Analysis - {self.session_exercise} Frame {self.frame_number}"

    class Meta:
        verbose_name = 'Pose Analysis'
        verbose_name_plural = 'Pose Analyses'
        ordering = ['session_exercise', 'frame_number']
        unique_together = ['session_exercise', 'frame_number']


class AIFeedback(models.Model):
    """
    Stores AI-generated feedback for users after completing exercises.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_feedbacks')
    session_exercise = models.OneToOneField(
        SessionExercise,
        on_delete=models.CASCADE,
        related_name='ai_feedback'
    )
    feedback_text = models.TextField()
    improvement_areas = models.JSONField(default=list, help_text="List of areas to improve")
    positive_feedback = models.JSONField(default=list, help_text="What went well")
    overall_score = models.FloatField()
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Feedback - {self.user.username}"

    class Meta:
        verbose_name = 'AI Feedback'
        verbose_name_plural = 'AI Feedbacks'
        ordering = ['-generated_at']
