from django.db import models

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
