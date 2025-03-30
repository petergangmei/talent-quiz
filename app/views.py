from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Quiz, Question, AnswerOption, QuizResult, UserQuiz, UserResponse
from .utils import get_client_ip, conditional_csrf_exempt, calculate_assessment_results, SPIRITUAL_GIFTS_MAPPING
import json
import math

def home(request):
    """
    Home page view that displays all available quizzes.
    """
    quizzes = Quiz.objects.all()
    return render(request, 'home.html', {'quizzes': quizzes})

@csrf_exempt
def quiz_start(request, quiz_id):
    """
    Start a quiz and redirect to the first question.
    """
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Create a new UserQuiz instance
    client_ip = get_client_ip(request)
    
    if request.method == 'POST':
        user_name = request.POST.get('user_name', '')
        if not user_name:
            user_name = f"Anonymous User {client_ip}"
        
        # Create UserQuiz and start with question 1
        user_quiz = UserQuiz.objects.create(
            quiz=quiz,
            user_name=user_name,
            ip_address=client_ip,
            current_question=1,
            is_completed=False
        )
        
        # After creating the user_quiz, redirect to the batch questions view
        context = {
            'quiz': quiz,
            'token': user_quiz.token
        }
        
        # Redirect to the batch questions view instead of single question view
        return redirect('app:quiz-batch-questions', token=user_quiz.token)
    
    # Show the quiz start form (GET request)
    return render(request, 'app/quiz_start.html', {'quiz': quiz})

@csrf_exempt
def quiz_question(request, token):
    """
    Display a question and handle user responses.
    """
    # Get the UserQuiz instance using the token
    user_quiz = get_object_or_404(UserQuiz, access_token=token)
    
    # Check if the quiz is expired
    if user_quiz.is_expired:
        return HttpResponse("This quiz link has expired.", status=403)
    
    # Prevent access if already completed
    if user_quiz.is_completed:
        return redirect('app:quiz-result', token=token)
        
    # Get the current question based on UserQuiz.current_question
    try:
        # Use order field for question sequence (1-based index)
        question = Question.objects.get(quiz=user_quiz.quiz, order=user_quiz.current_question)
    except Question.DoesNotExist:
        # If we can't find the question, mark as completed and show results
        user_quiz.is_completed = True
        user_quiz.save()
        
        # Calculate results before showing
        calculate_results(user_quiz)
        
        return redirect('app:quiz-result', token=token)
    
    # Handle form submission
    if request.method == 'POST':
        # Check if this is a JSON request (from sendBeacon)
        is_json_request = request.content_type and 'application/json' in request.content_type
        
        if is_json_request:
            try:
                # Parse JSON data
                import json
                data = json.loads(request.body)
                action = data.get('action', '')
                option_id = data.get('option', None)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)
        else:
            # Regular form submission
            action = request.POST.get('action', '')
            option_id = request.POST.get('option', None)
        
        # Process the submission
        if action == 'skip':
            # Handle skipped question
            UserResponse.objects.update_or_create(
                user_quiz=user_quiz,
                question=question,
                defaults={'is_skipped': True, 'selected_option': None}
            )
        else:
            # Handle answered question
            if option_id:
                selected_option = get_object_or_404(AnswerOption, id=option_id, question=question)
                UserResponse.objects.update_or_create(
                    user_quiz=user_quiz,
                    question=question,
                    defaults={'selected_option': selected_option, 'is_skipped': False}
                )
            else:
                # If no option selected and not skipping, show error
                # Only show error for regular form submissions, not beacon requests
                if action != 'skip' and not is_json_request:
                    return render(request, 'app/assessment_question.html', {
                        'user_quiz': user_quiz,
                        'question': question,
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
            
            # For JSON requests, return a simple success response
            if is_json_request:
                return JsonResponse({'status': 'success', 'next': 'result'})
                
            return redirect('app:quiz-result', token=token)
        
        # For JSON requests, return a simple success response
        if is_json_request:
            return JsonResponse({'status': 'success', 'next': 'question'})
            
        # Redirect to the next question
        return redirect('app:quiz-question', token=token)
    
    # Check if this question has already been answered
    existing_response = UserResponse.objects.filter(user_quiz=user_quiz, question=question).first()
    
    # Get total questions for progress calculation
    total_questions = user_quiz.quiz.questions.count()
    progress = int(((user_quiz.current_question - 1) / total_questions) * 100)
    
    # Determine if this is the assessment survey
    is_assessment = "assessment" in user_quiz.quiz.title.lower()
    
    # If this is the assessment survey, use the assessment template
    if is_assessment:
        return render(request, 'app/assessment_question.html', {
            'user_quiz': user_quiz,
            'question': question,
            'existing_response': existing_response,
            'total_questions': total_questions,
            'progress': progress
        })
    
    # Regular quiz template
    return render(request, 'app/quiz_question.html', {
        'user_quiz': user_quiz,
        'question': question,
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

@csrf_exempt
def quiz_result(request, token):
    """
    Display quiz results for a user.
    """
    # Get the user quiz instance
    user_quiz = get_object_or_404(UserQuiz, access_token=token)
    
    # If the quiz hasn't been completed, redirect to continue
    if not user_quiz.is_completed and user_quiz.current_question <= user_quiz.quiz.questions.count():
        return redirect('app:quiz-question', token=token)
    
    # Force calculation if no results found
    if not user_quiz.result_data:
        calculate_results(user_quiz)

    # Initialize dictionary to store interpretations based on scores
    result_interpretations = {}

    # Check if quiz is expired
    if user_quiz.is_expired:
        return render(request, 'app/quiz_expired.html', {'user_quiz': user_quiz})
    
    # Check if this is the assessment or regular quiz
    is_assessment = user_quiz.result_data.get('is_assessment', False)
    
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
    return redirect('app:quiz-start', quiz_id=quiz_id)

def assessment_continue(request, token):
    """
    Handler for continuing from assessment instructions to the first question.
    """
    return redirect('app:quiz-question', token=token)

@csrf_exempt
def quiz_batch_questions(request, token, batch=1):
    """
    Display a batch of 5 questions at once and handle user responses for all of them.
    """
    # Get the UserQuiz instance using the token
    user_quiz = get_object_or_404(UserQuiz, access_token=token)
    
    # Check if the quiz is expired
    if user_quiz.is_expired:
        return HttpResponse("This quiz link has expired.", status=403)
    
    # Prevent access if already completed
    if user_quiz.is_completed:
        return redirect('app:quiz-result', token=token)
    
    # Get total number of questions
    total_questions = user_quiz.quiz.questions.count()
    
    # Calculate total number of batches (ceiling division to ensure all questions are included)
    batch_size = 5
    total_batches = math.ceil(total_questions / batch_size)
    
    # Validate batch number
    try:
        batch = int(batch)
        if batch < 1 or batch > total_batches:
            batch = 1
    except (ValueError, TypeError):
        batch = 1
    
    # Calculate start and end questions for this batch
    start_question = ((batch - 1) * batch_size) + 1
    end_question = min(start_question + batch_size - 1, total_questions)
    
    # Check if this is a valid batch (still within range)
    if start_question > total_questions:
        # If we're past the end, mark as completed and show results
        user_quiz.is_completed = True
        user_quiz.save()
        
        # Calculate results before showing
        calculate_results(user_quiz)
        
        return redirect('app:quiz-result', token=token)
    
    # Get the batch of questions
    questions = Question.objects.filter(
        quiz=user_quiz.quiz, 
        order__gte=start_question,
        order__lte=end_question
    ).order_by('order')
    
    # Get existing responses for these questions
    responses = UserResponse.objects.filter(
        user_quiz=user_quiz,
        question__in=questions
    )
    
    # Create a dictionary of question_id -> selected_option_id for easier template access
    responses_dict = {}
    for response in responses:
        if response.selected_option:
            responses_dict[response.question_id] = response.selected_option_id
    
    # Handle form submission
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        if action == 'skip_all':
            # Skip all questions in this batch
            for question in questions:
                UserResponse.objects.update_or_create(
                    user_quiz=user_quiz,
                    question=question,
                    defaults={'is_skipped': True, 'selected_option': None}
                )
        else:  # 'submit'
            # Process each question's response
            for question in questions:
                question_key = f"question_{question.id}"
                option_id = request.POST.get(question_key)
                
                if option_id:
                    # Question was answered
                    selected_option = get_object_or_404(AnswerOption, id=option_id, question=question)
                    UserResponse.objects.update_or_create(
                        user_quiz=user_quiz,
                        question=question,
                        defaults={'selected_option': selected_option, 'is_skipped': False}
                    )
                else:
                    # Question was not answered (treat as skip)
                    UserResponse.objects.update_or_create(
                        user_quiz=user_quiz,
                        question=question,
                        defaults={'is_skipped': True, 'selected_option': None}
                    )
        
        # Update current_question to point to the start of the next batch
        user_quiz.current_question = end_question + 1
        user_quiz.save()
        
        # Check if that was the last batch
        if end_question >= total_questions:
            user_quiz.is_completed = True
            calculate_results(user_quiz)
            user_quiz.save()
            return redirect('app:quiz-result', token=token)
        
        # Redirect to the next batch
        return redirect('app:quiz-batch-questions', token=token, batch=batch+1)
    
    # Calculate progress percentage
    progress = int(((start_question - 1) / total_questions) * 100)
    
    # Check if this is the first or last batch
    is_first_batch = (batch == 1)
    is_last_batch = (end_question == total_questions)
    
    # Calculate previous batch number
    prev_batch = batch - 1 if batch > 1 else 1
    
    # Render the batch questions template
    return render(request, 'app/assessment_batch_questions.html', {
        'user_quiz': user_quiz,
        'questions': questions,
        'responses_dict': responses_dict,
        'total_questions': total_questions,
        'progress': progress,
        'current_batch': batch,
        'total_batches': total_batches,
        'is_first_batch': is_first_batch,
        'is_last_batch': is_last_batch,
        'prev_batch': prev_batch
    })
