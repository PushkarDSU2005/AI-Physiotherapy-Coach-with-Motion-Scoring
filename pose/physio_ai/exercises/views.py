from django.shortcuts import render
from django.views import View
from .models import Exercise


class ExerciseListView(View):
    """Display all available exercises."""
    def get(self, request):
        exercises = Exercise.objects.filter(is_active=True)
        difficulty = request.GET.get('difficulty', None)
        
        if difficulty:
            exercises = exercises.filter(difficulty_level=difficulty)
        
        return render(request, 'exercises/exercise_list.html', {'exercises': exercises})


class ExerciseDetailView(View):
    """Display details for a specific exercise."""
    def get(self, request, exercise_id):
        try:
            exercise = Exercise.objects.get(id=exercise_id, is_active=True)
            return render(request, 'exercises/exercise_detail.html', {'exercise': exercise})
        except Exercise.DoesNotExist:
            return render(request, 'exercises/exercise_not_found.html', status=404)
