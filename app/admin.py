from django.contrib import admin
from .models import Quiz, Question, AnswerOption, QuizResult, UserQuiz, UserResponse

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


class UserResponseInline(admin.TabularInline):
    """
    Inline admin for user responses within user quizzes.
    """
    model = UserResponse
    extra = 0
    readonly_fields = ('question', 'selected_option', 'is_skipped', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(UserQuiz)
class UserQuizAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserQuiz model.
    """
    list_display = ('user_name', 'quiz', 'ip_address', 'is_completed', 'progress_percentage', 'created_at', 'expires_at', 'is_expired')
    list_filter = ('quiz', 'is_completed', 'created_at')
    search_fields = ('user_name', 'ip_address')
    readonly_fields = ('access_token', 'created_at', 'expires_at', 'progress_percentage', 'is_expired')
    inlines = [UserResponseInline]
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = "Expired"


@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserResponse model.
    """
    list_display = ('user_quiz', 'question', 'selected_option', 'is_skipped', 'created_at')
    list_filter = ('user_quiz__quiz', 'is_skipped', 'created_at')
    search_fields = ('user_quiz__user_name', 'question__text')
    readonly_fields = ('created_at',)
