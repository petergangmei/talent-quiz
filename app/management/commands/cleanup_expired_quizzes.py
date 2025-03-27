from django.core.management.base import BaseCommand
from django.utils import timezone
from app.models import UserQuiz


class Command(BaseCommand):
    """
    Management command to delete expired UserQuiz instances and their related UserResponses.
    """
    help = 'Deletes UserQuiz instances that have expired (older than 30 days)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all expired UserQuiz instances
        now = timezone.now()
        expired_quizzes = UserQuiz.objects.filter(expires_at__lt=now)
        
        count = expired_quizzes.count()
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'Found {count} expired quiz attempts. (DRY RUN - nothing will be deleted)'))
            for quiz in expired_quizzes:
                self.stdout.write(f'  - {quiz.user_name} - {quiz.quiz.title} - Created: {quiz.created_at}, Expired: {quiz.expires_at}')
        else:
            if count > 0:
                self.stdout.write(self.style.WARNING(f'Deleting {count} expired quiz attempts...'))
                # Delete will cascade to associated UserResponses
                expired_quizzes.delete()
                self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} expired quiz attempts.'))
            else:
                self.stdout.write(self.style.SUCCESS('No expired quiz attempts found.')) 