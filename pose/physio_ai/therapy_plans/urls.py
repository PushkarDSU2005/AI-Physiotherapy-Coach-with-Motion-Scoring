"""
Therapy Plans URL Routing
"""

from django.urls import path
from . import views

app_name = 'therapy_plans'

urlpatterns = [
    path('', views.TherapyPlansIndexView.as_view(), name='index'),
]
