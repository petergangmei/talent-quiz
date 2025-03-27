from django.db import models
import uuid
from datetime import timedelta
from django.utils import timezone

# Create your models here.

class Quiz(models.Model):
    """
    Represents a complete quiz with title and description.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Quizzes"


class Question(models.Model):
    """
    Represents a question in a quiz.
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.text
    
    class Meta:
        ordering = ['order']


class AnswerOption(models.Model):
    """
    Represents an answer option for a question with mapping to result categories.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answer_options')
    text = models.CharField(max_length=255)
    # Example: storing mapping points as JSON (e.g., {"Hospitality": 2})
    mapping = models.JSONField(default=dict)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.text
    
    class Meta:
        ordering = ['order']


class QuizResult(models.Model):
    """
    Defines the interpretation of quiz results based on score ranges.
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    category = models.CharField(max_length=255)
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return f"{self.category} ({self.min_score}-{self.max_score})"
    
    class Meta:
        ordering = ['category', 'min_score']


class UserQuiz(models.Model):
    """
    Represents a quiz instance being taken by a specific user.
    Stores user identification and tracks quiz progress.
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='user_quizzes')
    user_name = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    access_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    current_question = models.IntegerField(default=1)  # 1-based index of current question
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    result_data = models.JSONField(default=dict, blank=True)  # Stores the calculated results
    
    def save(self, *args, **kwargs):
        """Set expiry date to 30 days from creation if not already set."""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user_name}'s attempt at {self.quiz.title}"
    
    @property
    def is_expired(self):
        """Check if the UserQuiz has expired."""
        return timezone.now() > self.expires_at
    
    @property
    def progress_percentage(self):
        """Calculate progress as a percentage."""
        total_questions = self.quiz.questions.count()
        if not total_questions:
            return 0
        return min(int((self.current_question - 1) / total_questions * 100), 100)


class UserResponse(models.Model):
    """
    Stores an individual user's response to a question.
    """
    user_quiz = models.ForeignKey(UserQuiz, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(AnswerOption, on_delete=models.CASCADE, null=True, blank=True)
    is_skipped = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.is_skipped:
            return f"{self.user_quiz.user_name} skipped question {self.question.order}"
        elif self.selected_option:
            return f"{self.user_quiz.user_name} selected '{self.selected_option.text}' for question {self.question.order}"
        else:
            return f"{self.user_quiz.user_name}'s response to question {self.question.order}"
    
    class Meta:
        unique_together = ('user_quiz', 'question')
        ordering = ['question__order']
