from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('', views.UserListView.as_view(), name='profile_list'),
    path('<int:user_id>/', views.UserDetailView.as_view(), name='profile_detail'),
]
