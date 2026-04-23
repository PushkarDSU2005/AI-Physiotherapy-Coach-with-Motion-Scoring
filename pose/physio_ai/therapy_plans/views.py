from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from analytics.services import build_therapy_context
from .models import TherapyPlan


class TherapyPlansIndexView(TemplateView):
    """Display Therapy Plans dashboard."""
    template_name = 'therapy_plans/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_therapy_context(self.request.user))
        return context
