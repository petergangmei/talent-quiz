from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.utils import timezone
from .models import Quiz, Question, AnswerOption, QuizResult, UserQuiz, UserResponse
import json

def get_client_ip(request):
    """Helper function to get the client's IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def home(request):
    """
    Home page view that displays all available quizzes.
    """
    quizzes = Quiz.objects.all()
    return render(request, 'home.html', {'quizzes': quizzes})

def quiz_start(request, quiz_id):
    """
    Display form to collect user name before starting the quiz.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.method == 'POST':
        user_name = request.POST.get('user_name', '').strip()
        if not user_name:
            return render(request, 'app/quiz_start.html', {
                'quiz': quiz,
                'error': 'Please enter your name to start the quiz.'
            })
        
        # Create a new UserQuiz instance
        user_quiz = UserQuiz.objects.create(
            quiz=quiz,
            user_name=user_name,
            ip_address=get_client_ip(request),
            current_question=1
        )
        
        # Redirect to the first question
        return redirect('quiz-question', token=user_quiz.access_token)
    
    return render(request, 'app/quiz_start.html', {'quiz': quiz})

def quiz_question(request, token):
    """
    Display a single question from the quiz and handle responses.
    """
    user_quiz = get_object_or_404(UserQuiz, access_token=token)
    
    # Check if quiz is already completed
    if user_quiz.is_completed:
        return redirect('quiz-result', token=token)
    
    # Check if quiz is expired
    if user_quiz.is_expired:
        return render(request, 'app/quiz_expired.html', {'user_quiz': user_quiz})
    
    # Get the current question
    try:
        current_question = user_quiz.quiz.questions.get(order=user_quiz.current_question)
    except Question.DoesNotExist:
        # If current_question exceeds the number of questions, mark as completed and show results
        user_quiz.is_completed = True
        user_quiz.save()
        return redirect('quiz-result', token=token)
    
    # Handle form submission
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        if action == 'skip':
            # Handle skipped question
            UserResponse.objects.update_or_create(
                user_quiz=user_quiz,
                question=current_question,
                defaults={'is_skipped': True, 'selected_option': None}
            )
        else:
            # Handle answered question
            option_id = request.POST.get('option')
            if option_id:
                selected_option = get_object_or_404(AnswerOption, id=option_id, question=current_question)
                UserResponse.objects.update_or_create(
                    user_quiz=user_quiz,
                    question=current_question,
                    defaults={'selected_option': selected_option, 'is_skipped': False}
                )
            else:
                # If no option selected and not skipping, show error
                if action != 'skip':
                    return render(request, 'app/quiz_question.html', {
                        'user_quiz': user_quiz,
                        'question': current_question,
                        'error': 'Please select an option or skip this question.'
                    })
        
        # Move to next question
        user_quiz.current_question += 1
        user_quiz.save()
        
        # Check if that was the last question
        if user_quiz.current_question > user_quiz.quiz.questions.count():
            user_quiz.is_completed = True
            calculate_results(user_quiz)
            user_quiz.save()
            return redirect('quiz-result', token=token)
        
        # Redirect to the next question
        return redirect('quiz-question', token=token)
    
    # Check if this question has already been answered
    existing_response = UserResponse.objects.filter(user_quiz=user_quiz, question=current_question).first()
    
    return render(request, 'app/quiz_question.html', {
        'user_quiz': user_quiz,
        'question': current_question,
        'existing_response': existing_response,
        'total_questions': user_quiz.quiz.questions.count(),
        'progress': user_quiz.progress_percentage
    })

def calculate_results(user_quiz):
    """
    Calculate quiz results based on user responses.
    """
    scores = {
        "Hospitality": 0,
        "Teaching": 0,
        "Leadership": 0,
        "Counsel/Wisdom": 0,
        "Service": 0
    }
    
    # Add up the scores from all answered questions
    responses = UserResponse.objects.filter(
        user_quiz=user_quiz, 
        is_skipped=False
    ).select_related('selected_option')
    
    for response in responses:
        if response.selected_option:
            for category, points in response.selected_option.mapping.items():
                scores[category] = scores.get(category, 0) + points
    
    # Determine primary gift and secondary gifts
    if scores:
        primary_category = max(scores.items(), key=lambda x: x[1])
        
        # Find secondary gifts (within 15% of primary)
        primary_score = primary_category[1]
        secondary_gifts = []
        
        for category, score in scores.items():
            if category != primary_category[0] and score >= (primary_score * 0.85):
                secondary_gifts.append((category, score))
        
        # Store the result data
        user_quiz.result_data = {
            'scores': scores,
            'primary_category': primary_category[0],
            'primary_score': primary_category[1],
            'secondary_gifts': [{
                'category': cat, 
                'score': score
            } for cat, score in secondary_gifts]
        }
    else:
        user_quiz.result_data = {'scores': {}}
    
    user_quiz.save()

def quiz_result(request, token):
    """
    Display the quiz results.
    """
    user_quiz = get_object_or_404(UserQuiz, access_token=token)
    
    # If the quiz is not completed, redirect to the current question
    if not user_quiz.is_completed:
        return redirect('quiz-question', token=token)
    
    # Check if quiz is expired
    if user_quiz.is_expired:
        return render(request, 'app/quiz_expired.html', {'user_quiz': user_quiz})
    
    # Calculate results if not already done
    if not user_quiz.result_data:
        calculate_results(user_quiz)
    
    # Get interpretations for primary and secondary gifts
    result_interpretations = {}
    if 'primary_category' in user_quiz.result_data:
        primary_category = user_quiz.result_data['primary_category']
        primary_score = user_quiz.result_data['scores'].get(primary_category, 0)
        
        primary_interpretation = QuizResult.objects.filter(
            quiz=user_quiz.quiz,
            category=primary_category,
            min_score__lte=primary_score,
            max_score__gte=primary_score
        ).first()
        
        if primary_interpretation:
            result_interpretations[primary_category] = primary_interpretation.description
        
        # Get interpretations for secondary gifts
        for gift in user_quiz.result_data.get('secondary_gifts', []):
            category = gift['category']
            score = gift['score']
            
            interpretation = QuizResult.objects.filter(
                quiz=user_quiz.quiz,
                category=category,
                min_score__lte=score,
                max_score__gte=score
            ).first()
            
            if interpretation:
                result_interpretations[category] = interpretation.description
    
    return render(request, 'app/quiz_result.html', {
        'user_quiz': user_quiz,
        'quiz': user_quiz.quiz,
        'result_data': user_quiz.result_data,
        'result_interpretations': result_interpretations
    })

def quiz_detail(request, quiz_id):
    """
    Display information about a quiz and prompt to start.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return render(request, 'app/quiz_detail.html', {'quiz': quiz})

def quiz_submit(request, quiz_id):
    """
    Legacy quiz submission handler - redirects to quiz_start.
    """
    return redirect('quiz-start', quiz_id=quiz_id)
