from django.shortcuts import render, get_object_or_404, redirect
from .models import Quiz, Question, AnswerOption, QuizResult

def home(request):
    """
    Home page view that displays all available quizzes.
    """
    quizzes = Quiz.objects.all()
    return render(request, 'home.html', {'quizzes': quizzes})

def quiz_detail(request, quiz_id):
    """
    Displays a single quiz with its questions and answer options.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return render(request, 'app/quiz_detail.html', {'quiz': quiz})

def quiz_submit(request, quiz_id):
    """
    Processes quiz submissions and calculates results.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        # Process the submitted answers and calculate scores
        scores = {}
        # Loop through questions and map answer choices to scores
        for question in quiz.questions.all():
            answer_id = request.POST.get(f'question_{question.id}')
            if answer_id:
                try:
                    answer = AnswerOption.objects.get(id=answer_id)
                    # Mapping is assumed to be a dict, e.g., {"Hospitality": 2}
                    for key, value in answer.mapping.items():
                        scores[key] = scores.get(key, 0) + value
                except AnswerOption.DoesNotExist:
                    # Handle case where the answer option doesn't exist
                    pass

        # Determine the primary category based on scores
        if scores:
            primary_category = max(scores.items(), key=lambda x: x[1])
            
            # Find matching result interpretation if available
            matching_results = []
            for category, score in scores.items():
                results = QuizResult.objects.filter(
                    quiz=quiz,
                    category=category,
                    min_score__lte=score,
                    max_score__gte=score
                )
                matching_results.extend(results)
        else:
            primary_category = None
            matching_results = []

        context = {
            'quiz': quiz,
            'scores': scores,
            'primary_category': primary_category,
            'matching_results': matching_results,
        }
        return render(request, 'app/quiz_result.html', context)
    else:
        return redirect('quiz-detail', quiz_id=quiz_id)
