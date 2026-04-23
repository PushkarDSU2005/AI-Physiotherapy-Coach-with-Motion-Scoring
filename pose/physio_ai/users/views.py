from django.shortcuts import render
from django.views import View
from django.contrib.auth.models import User

from analytics.services import build_dashboard_context
from .models import UserProfile


class DashboardView(View):
    """Display the main user dashboard."""
    def get(self, request):
        return render(request, 'dashboard/dashboard.html', build_dashboard_context(request.user))


class UserListView(View):
    """Display all user profiles."""
    def get(self, request):
        profiles = UserProfile.objects.all()
        return render(request, 'users/profile_list.html', {'profiles': profiles})


class UserDetailView(View):
    """Display a specific user's profile."""
    def get(self, request, user_id):
        try:
            profile = UserProfile.objects.get(user_id=user_id)
            return render(request, 'users/profile_detail.html', {'profile': profile})
        except UserProfile.DoesNotExist:
            return render(request, 'users/profile_not_found.html', status=404)
