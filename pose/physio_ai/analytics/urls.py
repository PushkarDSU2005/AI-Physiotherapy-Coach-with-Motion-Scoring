from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.AnalyticsIndexView.as_view(), name='index'),
    path('export/pdf/', views.export_progress_pdf, name='export_pdf'),
    path('progress/', views.UserProgressView.as_view(), name='progress'),
    path('daily-metrics/', views.DailyMetricsView.as_view(), name='daily_metrics'),
    path('reports/', views.ReportListView.as_view(), name='report_list'),
    path('reports/<int:report_id>/', views.ReportDetailView.as_view(), name='report_detail'),
]
