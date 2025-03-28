from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.utils import timezone
from .models import Quiz, Question, AnswerOption, QuizResult, UserQuiz, UserResponse
from .utils import get_client_ip, conditional_csrf_exempt, calculate_assessment_results, SPIRITUAL_GIFTS_MAPPING
import json

def home(request):
    """
    Home page view that displays all available quizzes.
    """
    quizzes = Quiz.objects.all()
    return render(request, 'home.html', {'quizzes': quizzes})

@conditional_csrf_exempt
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
        
        # For the assessment, show instructions page first
        if "assessment" in quiz.title.lower():
            return render(request, 'app/assessment_instructions.html', {
                'user_quiz': user_quiz,
                'quiz': quiz,
                'token': user_quiz.access_token
            })
        
        # Redirect to the first question
        return redirect('quiz-question', token=user_quiz.access_token)
    
    return render(request, 'app/quiz_start.html', {'quiz': quiz})

@conditional_csrf_exempt
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
    
    # Get total questions for progress calculation
    total_questions = user_quiz.quiz.questions.count()
    progress = int(((user_quiz.current_question - 1) / total_questions) * 100)
    
    # Determine if this is the assessment survey
    is_assessment = "assessment" in user_quiz.quiz.title.lower()
    
    # If this is the assessment survey, use the assessment template
    if is_assessment:
        return render(request, 'app/assessment_question.html', {
            'user_quiz': user_quiz,
            'question': current_question,
            'existing_response': existing_response,
            'total_questions': total_questions,
            'progress': progress
        })
    
    # Regular quiz template
    return render(request, 'app/quiz_question.html', {
        'user_quiz': user_quiz,
        'question': current_question,
        'existing_response': existing_response,
        'total_questions': total_questions,
        'progress': progress
    })

def calculate_results(user_quiz):
    """
    Calculate quiz results based on user responses.
    Detects if this is the spiritual gifts assessment or regular quiz and calls
    the appropriate calculation function.
    """
    # Check if this is the Spiritual Gifts Assessment Survey
    if "assessment" in user_quiz.quiz.title.lower():
        result_data = calculate_assessment_results(user_quiz)
    else:
        # Regular quiz calculation logic
        # Initialize an empty dictionary to hold scores for each category
        scores = {}
        
        # Get all responses for this user quiz
        responses = UserResponse.objects.filter(user_quiz=user_quiz, is_skipped=False)
        
        # Loop through responses and calculate scores for each category
        for response in responses:
            if response.selected_option:
                # Get the mapping from the selected option (e.g., {"Leadership": 2, "Teaching": 1})
                mapping = response.selected_option.mapping
                
                # Add scores to the appropriate categories
                for category, points in mapping.items():
                    if category in scores:
                        scores[category] += points
                    else:
                        scores[category] = points
        
        # Find the primary category (highest score)
        primary_category = None
        max_score = 0
        
        for category, score in scores.items():
            if score > max_score:
                max_score = score
                primary_category = category
        
        # Find secondary gifts (next highest scores)
        secondary_gifts = []
        
        # Convert scores to a list of tuples for sorting
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get up to 2 secondary gifts (skip the primary one)
        for i, (category, score) in enumerate(sorted_scores):
            if i == 0:  # Skip the primary gift
                continue
            if i <= 2:  # Get the next two highest scores
                secondary_gifts.append({'category': category, 'score': score})
            else:
                break
        
        # Store results in user_quiz
        result_data = {
            'scores': scores,
            'primary_category': primary_category,
            'primary_score': max_score if primary_category else 0,
            'secondary_gifts': secondary_gifts,
            'is_assessment': False  # Flag to identify this as a regular quiz
        }
    
    # Save the result data to the user_quiz
    user_quiz.result_data = result_data
    user_quiz.save()
    
    return result_data

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
    
    # Check if this is the assessment or regular quiz
    is_assessment = user_quiz.result_data.get('is_assessment', False)
    
    # Get interpretations for gifts
    result_interpretations = {}
    
    if is_assessment:
        # For assessment, get interpretations for top gifts
        for gift in user_quiz.result_data.get('primary_gifts', []):
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
        
        # Extract top gifts for display
        top_gifts = {}
        for gift in user_quiz.result_data.get('primary_gifts', []):
            top_gifts[gift['category']] = gift['score']
        
        # Get all gift scores
        gift_scores = user_quiz.result_data.get('scores', {})
        
        # Extract gift descriptions from interpretations
        gift_descriptions = {}
        for gift, description in result_interpretations.items():
            gift_descriptions[gift] = description
        
        # For any missing descriptions, provide a default
        for gift in SPIRITUAL_GIFTS_MAPPING.keys():
            if gift not in gift_descriptions:
                gift_descriptions[gift] = f"The gift of {gift} - description not available."
                
        # Render the assessment result template
        return render(request, 'app/assessment_result.html', {
            'user_quiz': user_quiz,
            'quiz': user_quiz.quiz,
            'result_data': user_quiz.result_data,
            'result_interpretations': result_interpretations,
            'gift_mapping': SPIRITUAL_GIFTS_MAPPING,  # Pass the gift mapping for reference
            'top_gifts': top_gifts,
            'gift_scores': gift_scores,
            'gift_descriptions': gift_descriptions
        })
    else:
        # Regular quiz result logic - get primary and secondary gift interpretations
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
        
        # Render the regular quiz result template
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

def assessment_continue(request, token):
    """
    Handler for continuing from assessment instructions to the first question.
    """
    return redirect('quiz-question', token=token)
