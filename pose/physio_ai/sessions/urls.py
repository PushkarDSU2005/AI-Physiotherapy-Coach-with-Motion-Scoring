from django.urls import path
from . import views, api_views

app_name = 'sessions'

urlpatterns = [
    # Session list and detail
    path('', views.SessionListView.as_view(), name='session_list'),
    path('<int:session_id>/', views.SessionDetailView.as_view(), name='session_detail'),
    
    # Pose capture
    path('pose-capture-demo/', views.pose_capture_demo, name='pose_capture_demo'),
    path('capture-demo-live/', views.pose_capture_demo_live, name='pose_capture_demo_live'),
    path('exercise/<int:session_exercise_id>/capture/', views.pose_capture_view, name='pose_capture'),
    
    # API endpoints
    path('api/upload_pose_frame/', api_views.upload_pose_frame, name='upload_pose_frame'),
    path('api/get_pose_capture/<int:session_exercise_id>/', api_views.get_pose_capture_page, name='get_pose_capture'),
]
