"""
Utility functions for the quiz application.
"""
from functools import wraps
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

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