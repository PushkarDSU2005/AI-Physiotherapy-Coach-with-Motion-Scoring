from django.urls import path
from . import views

app_name = 'ai_engine'

urlpatterns = [
    path('', views.AIEngineIndexView.as_view(), name='index'),
    path('analysis/<int:session_exercise_id>/', views.PoseAnalysisView.as_view(), name='pose_analysis'),
    path('feedback/<int:session_exercise_id>/', views.AIFeedbackView.as_view(), name='ai_feedback'),
]
