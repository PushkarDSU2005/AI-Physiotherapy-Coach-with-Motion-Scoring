from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from .models import PoseAnalysis, AIFeedback


class AIEngineIndexView(TemplateView):
    """Display AI Engine dashboard."""
    template_name = 'ai_engine/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_analyses'] = PoseAnalysis.objects.count()
        context['total_feedbacks'] = AIFeedback.objects.count()
        return context


class PoseAnalysisView(View):
    """Display pose analysis results for an exercise."""
    def get(self, request, session_exercise_id):
        try:
            analyses = PoseAnalysis.objects.filter(
                session_exercise_id=session_exercise_id
            ).order_by('frame_number')
            return render(request, 'ai_engine/pose_analysis.html', {
                'analyses': analyses,
                'total_frames': analyses.count()
            })
        except PoseAnalysis.DoesNotExist:
            return render(request, 'ai_engine/analysis_not_found.html', status=404)


class AIFeedbackView(View):
    """Display AI-generated feedback for an exercise."""
    def get(self, request, session_exercise_id):
        try:
            feedback = AIFeedback.objects.get(session_exercise_id=session_exercise_id)
            return render(request, 'ai_engine/feedback.html', {'feedback': feedback})
        except AIFeedback.DoesNotExist:
            return render(request, 'ai_engine/feedback_not_found.html', status=404)
