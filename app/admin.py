from django.contrib import admin
from .models import Quiz, Question, AnswerOption, QuizResult

# Register your models here.

class AnswerOptionInline(admin.TabularInline):
    """
    Inline admin for answer options within questions.
    """
    model = AnswerOption
    extra = 1
    fields = ('text', 'mapping', 'order')


class QuestionInline(admin.TabularInline):
    """
    Inline admin for questions within quizzes.
    """
    model = Question
    extra = 1
    fields = ('text', 'order')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """
    Admin configuration for Quiz model.
    """
    list_display = ('title', 'created_at')
    search_fields = ('title', 'description')
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Question model.
    """
    list_display = ('text', 'quiz', 'order')
    list_filter = ('quiz',)
    search_fields = ('text',)
    inlines = [AnswerOptionInline]


@admin.register(AnswerOption)
class AnswerOptionAdmin(admin.ModelAdmin):
    """
    Admin configuration for AnswerOption model.
    """
    list_display = ('text', 'question', 'order')
    list_filter = ('question__quiz',)
    search_fields = ('text',)


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    """
    Admin configuration for QuizResult model.
    """
    list_display = ('quiz', 'category', 'min_score', 'max_score')
    list_filter = ('quiz', 'category')
    search_fields = ('category', 'description')
