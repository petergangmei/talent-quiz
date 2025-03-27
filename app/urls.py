from django.urls import path
from .views import home, quiz_detail, quiz_submit

urlpatterns = [
    path('', home, name='home'),
    path('quiz/<int:quiz_id>/', quiz_detail, name='quiz-detail'),
    path('quiz/<int:quiz_id>/submit/', quiz_submit, name='quiz-submit'),
]
