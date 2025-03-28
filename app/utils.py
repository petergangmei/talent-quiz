"""
Utility functions for the quiz application.
"""
from functools import wraps
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import UserResponse

def conditional_csrf_exempt(view_func):
    """
    Decorator that makes a view CSRF exempt when accessed from trusted domains.
    This is useful for handling specific edge cases where CSRF validation might fail.
    
    Usage:
        @conditional_csrf_exempt
        def my_view(request):
            # ...
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Get the origin or referer from the request
        origin = request.META.get('HTTP_ORIGIN', '')
        referer = request.META.get('HTTP_REFERER', '')
        
        # Check if the request is from a trusted origin
        trusted_origins = getattr(settings, 'CSRF_TRUSTED_ORIGINS', [])
        is_trusted = any(origin.startswith(trusted) for trusted in trusted_origins) or \
                    any(referer.startswith(trusted) for trusted in trusted_origins)
        
        if is_trusted:
            # If from a trusted origin, apply csrf_exempt
            return csrf_exempt(view_func)(request, *args, **kwargs)
        else:
            # Otherwise, require CSRF token
            return view_func(request, *args, **kwargs)
    
    return wrapped_view

def get_client_ip(request):
    """Helper function to get the client's IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip 

# Gift mapping for the Spiritual Gifts Assessment
SPIRITUAL_GIFTS_MAPPING = {
    "Leadership": [6, 16, 27, 43, 65],
    "Administration": [1, 17, 31, 47, 59],
    "Teaching": [2, 18, 33, 61, 73],
    "Knowledge": [9, 24, 39, 68, 79],
    "Wisdom": [3, 19, 48, 62, 74],
    "Prophecy": [10, 25, 40, 54, 69],
    "Discernment": [11, 26, 41, 55, 70],
    "Exhortation": [20, 34, 49, 63, 75],
    "Shepherding": [4, 21, 35, 50, 76],
    "Faith": [12, 28, 42, 56, 80],
    "Evangelism": [5, 36, 51, 64, 77],
    "Apostleship": [13, 29, 44, 57, 71],
    "Service/Helps": [14, 30, 46, 58, 72],
    "Mercy": [7, 22, 37, 52, 66],
    "Giving": [8, 23, 38, 53, 67],
    "Hospitality": [15, 32, 45, 60, 78]
}

def calculate_assessment_results(user_quiz):
    """
    Calculate results for the Spiritual Gifts Assessment Survey.
    
    This function processes responses from a completed spiritual gifts assessment
    and calculates scores for each gift category based on the predefined mapping.
    
    Args:
        user_quiz: A UserQuiz instance that has been completed
        
    Returns:
        A dictionary containing the scores, primary gifts, and other result data
    """
    # Initialize scores for each gift category
    gift_scores = {gift: 0 for gift in SPIRITUAL_GIFTS_MAPPING.keys()}
    
    # Get all completed (non-skipped) responses for this quiz
    responses = UserResponse.objects.filter(user_quiz=user_quiz, is_skipped=False)
    
    # Group responses by question order
    responses_by_question = {}
    for response in responses:
        responses_by_question[response.question.order] = response
    
    # Calculate scores for each gift category
    for gift, question_numbers in SPIRITUAL_GIFTS_MAPPING.items():
        for q_num in question_numbers:
            if q_num in responses_by_question:
                response = responses_by_question[q_num]
                if response.selected_option and gift in response.selected_option.mapping:
                    gift_scores[gift] += response.selected_option.mapping[gift]
    
    # Sort gifts by score to determine primary and secondary gifts
    sorted_gifts = sorted(gift_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Get the top 3 gifts
    primary_gifts = []
    for i, (gift, score) in enumerate(sorted_gifts):
        if i < 3 and score > 0:  # Include only the top 3 with scores > 0
            primary_gifts.append({
                'category': gift,
                'score': score
            })
    
    # Store results in a structured format
    result_data = {
        'scores': gift_scores,
        'primary_category': sorted_gifts[0][0] if sorted_gifts else None,
        'primary_score': sorted_gifts[0][1] if sorted_gifts else 0,
        'primary_gifts': primary_gifts,  # Top 3 gifts
        'is_assessment': True  # Flag to identify this as an assessment (not the regular quiz)
    }
    
    return result_data 