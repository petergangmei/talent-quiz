from django.urls import path
from .views import home, quiz_detail, quiz_submit, quiz_start, quiz_question, quiz_result, assessment_continue, quiz_batch_questions

# Register the app namespace
app_name = 'app'

urlpatterns = [
    path('', home, name='home'),
    path('quiz/<int:quiz_id>/', quiz_detail, name='quiz-detail'),
    path('quiz/<int:quiz_id>/submit/', quiz_submit, name='quiz-submit'),
    path('quiz/<int:quiz_id>/start/', quiz_start, name='quiz-start'),
    path('quiz/question/<uuid:token>/', quiz_question, name='quiz-question'),
    path('quiz/questions/<uuid:token>/', quiz_batch_questions, name='quiz-batch-questions'),
    path('quiz/questions/<uuid:token>/<int:batch>/', quiz_batch_questions, name='quiz-batch-questions'),
    path('quiz/result/<uuid:token>/', quiz_result, name='quiz-result'),
    path('assessment/continue/<uuid:token>/', assessment_continue, name='assessment-continue'),
]
