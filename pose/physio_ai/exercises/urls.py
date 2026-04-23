from django.urls import path
from . import views

app_name = 'exercises'

urlpatterns = [
    path('', views.ExerciseListView.as_view(), name='exercise_list'),
    path('<int:exercise_id>/', views.ExerciseDetailView.as_view(), name='exercise_detail'),
]
