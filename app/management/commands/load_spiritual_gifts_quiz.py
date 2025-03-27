from django.core.management.base import BaseCommand
from app.models import Quiz, Question, AnswerOption, QuizResult
from django.db import transaction


class Command(BaseCommand):
    """
    Management command to create the Extensive Spiritual Gifts Quiz with 
    all questions, answer options, and result categories.
    """
    help = 'Creates the Extensive Spiritual Gifts Quiz with questions and answers'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating Extensive Spiritual Gifts Quiz...'))
        
        with transaction.atomic():
            # Create the quiz
            quiz, created = Quiz.objects.get_or_create(
                title="Extensive Spiritual Gifts Quiz",
                defaults={
                    'description': (
                        "This quiz contains 20 questions. For each question, choose the option "
                        "that best describes your natural tendency. Each answer is linked to one "
                        "or more spiritual gift areas."
                    )
                }
            )
            
            if not created:
                self.stdout.write(self.style.WARNING('Quiz already exists. Updating existing quiz...'))
                # Clear existing questions to avoid duplication
                quiz.questions.all().delete()
                quiz.description = (
                    "This quiz contains 20 questions. For each question, choose the option "
                    "that best describes your natural tendency. Each answer is linked to one "
                    "or more spiritual gift areas."
                )
                quiz.save()
            
            # Create quiz categories result interpretations
            self._create_result_interpretations(quiz)
            
            # Create all questions and answer options
            self._create_questions_and_answers(quiz)
            
            self.stdout.write(self.style.SUCCESS('Quiz successfully created!'))
    
    def _create_result_interpretations(self, quiz):
        """Create result interpretations for the quiz"""
        result_categories = {
            "Hospitality": {
                "min_score": 15,
                "max_score": 40,
                "description": (
                    "Your gift of Hospitality reflects your natural ability to make others feel welcome "
                    "and comfortable. You excel in creating warm, inviting environments where people feel "
                    "valued and accepted. Consider serving in roles where you can welcome newcomers, host "
                    "gatherings, or create inclusive community spaces."
                )
            },
            "Teaching": {
                "min_score": 15,
                "max_score": 40,
                "description": (
                    "Your gift of Teaching shows your ability to clearly communicate knowledge and truth "
                    "in a way that others can understand and apply. You enjoy researching, understanding complex "
                    "concepts, and sharing insights with others. Consider roles in education, leading Bible studies, "
                    "or developing training materials."
                )
            },
            "Leadership": {
                "min_score": 15,
                "max_score": 40,
                "description": (
                    "Your gift of Leadership reveals your ability to cast vision, organize resources, "
                    "and inspire others toward a common goal. You naturally take initiative and help groups "
                    "move forward effectively. Consider roles coordinating ministries, leading teams, "
                    "or developing new initiatives."
                )
            },
            "Counsel/Wisdom": {
                "min_score": 15,
                "max_score": 40,
                "description": (
                    "Your gift of Counsel/Wisdom reflects your ability to offer thoughtful, insightful "
                    "guidance based on discernment and understanding. You often see beneath surface issues "
                    "to identify root causes and effective solutions. Consider roles in mentoring, pastoral care, "
                    "or providing guidance to individuals or groups facing challenges."
                )
            },
            "Service": {
                "min_score": 15,
                "max_score": 40,
                "description": (
                    "Your gift of Service demonstrates your dedication to meeting practical needs "
                    "with reliability and humility. You find fulfillment in behind-the-scenes work that "
                    "enables others to thrive. Consider roles in support ministries, practical assistance teams, "
                    "or serving in ways that create a foundation for community activities."
                )
            }
        }
        
        for category, data in result_categories.items():
            QuizResult.objects.get_or_create(
                quiz=quiz,
                category=category,
                defaults={
                    'min_score': data["min_score"],
                    'max_score': data["max_score"],
                    'description': data["description"]
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Result interpretations created'))
    
    def _create_questions_and_answers(self, quiz):
        """Create all questions and their answer options"""
        questions_data = [
            {
                "text": "When attending a social event, you are most likely to:",
                "order": 1,
                "options": [
                    {"text": "Greet everyone and make sure they feel welcome.", "mapping": {"Hospitality": 2}, "order": 1},
                    {"text": "Listen and engage in meaningful one-on-one conversations.", "mapping": {"Counsel/Wisdom": 2}, "order": 2},
                    {"text": "Observe quietly and support where needed.", "mapping": {"Service": 2}, "order": 3},
                    {"text": "Take charge of organizing activities.", "mapping": {"Leadership": 2}, "order": 4}
                ]
            },
            {
                "text": "When you're in a discussion group, you usually:",
                "order": 2,
                "options": [
                    {"text": "Share your understanding and clarify concepts.", "mapping": {"Teaching": 2}, "order": 1},
                    {"text": "Listen carefully and offer measured advice when asked.", "mapping": {"Counsel/Wisdom": 2}, "order": 2},
                    {"text": "Encourage others to speak up and ensure everyone is heard.", "mapping": {"Hospitality": 1, "Leadership": 1}, "order": 3},
                    {"text": "Prefer to let others lead and follow along.", "mapping": {"Service": 2}, "order": 4}
                ]
            },
            {
                "text": "In planning a community event, you prefer to:",
                "order": 3,
                "options": [
                    {"text": "Organize the event from start to finish.", "mapping": {"Leadership": 2}, "order": 1},
                    {"text": "Help set up and support the behind-the-scenes work.", "mapping": {"Service": 2}, "order": 2},
                    {"text": "Focus on making sure every attendee feels comfortable.", "mapping": {"Hospitality": 2}, "order": 3},
                    {"text": "Prepare informative materials or presentations about the event.", "mapping": {"Teaching": 2}, "order": 4}
                ]
            },
            {
                "text": "When someone comes to you with a problem, you tend to:",
                "order": 4,
                "options": [
                    {"text": "Offer thoughtful advice based on personal experience.", "mapping": {"Counsel/Wisdom": 2}, "order": 1},
                    {"text": "Listen carefully without immediately giving advice.", "mapping": {"Counsel/Wisdom": 1, "Service": 1}, "order": 2},
                    {"text": "Encourage them and refer them to someone more experienced.", "mapping": {"Hospitality": 1, "Leadership": 1}, "order": 3},
                    {"text": "Share a relevant lesson or story that might help.", "mapping": {"Teaching": 2}, "order": 4}
                ]
            },
            {
                "text": "If you're asked to lead a small group study, your reaction is:",
                "order": 5,
                "options": [
                    {"text": "Excited, as you enjoy guiding discussions.", "mapping": {"Leadership": 2}, "order": 1},
                    {"text": "Interested, but you'd prefer to contribute by preparing discussion materials.", "mapping": {"Teaching": 2}, "order": 2},
                    {"text": "A bit nervous because you're more comfortable listening.", "mapping": {"Counsel/Wisdom": 1, "Service": 1}, "order": 3},
                    {"text": "You'd rather let someone else take the lead and support them.", "mapping": {"Service": 2}, "order": 4}
                ]
            },
            {
                "text": "When you're invited to a new community or church event, you:",
                "order": 6,
                "options": [
                    {"text": "Immediately volunteer to help with welcoming guests.", "mapping": {"Hospitality": 2}, "order": 1},
                    {"text": "Observe first, then offer support as needed.", "mapping": {"Service": 2}, "order": 2},
                    {"text": "Engage deeply in discussions about the event's topic.", "mapping": {"Teaching": 2}, "order": 3},
                    {"text": "Offer to lead a small part of the program.", "mapping": {"Leadership": 2}, "order": 4}
                ]
            },
            {
                "text": "How do you feel about public speaking?",
                "order": 7,
                "options": [
                    {"text": "Comfortable, especially when sharing a meaningful lesson.", "mapping": {"Teaching": 2}, "order": 1},
                    {"text": "Nervous, but willing to speak if absolutely needed.", "mapping": {"Counsel/Wisdom": 1, "Service": 1}, "order": 2},
                    {"text": "Excited to lead and inspire others.", "mapping": {"Leadership": 2}, "order": 3},
                    {"text": "Prefer one-on-one conversations over speaking to a crowd.", "mapping": {"Hospitality": 2}, "order": 4}
                ]
            },
            {
                "text": "When solving a problem, you tend to:",
                "order": 8,
                "options": [
                    {"text": "Analyze the situation carefully and offer a wise solution.", "mapping": {"Counsel/Wisdom": 2}, "order": 1},
                    {"text": "Brainstorm creative solutions with a team.", "mapping": {"Leadership": 1, "Teaching": 1}, "order": 2},
                    {"text": "Take practical steps immediately to address the issue.", "mapping": {"Service": 2}, "order": 3},
                    {"text": "Consider how best to communicate the solution to others.", "mapping": {"Teaching": 2}, "order": 4}
                ]
            },
            {
                "text": "In your free time, you most enjoy:",
                "order": 9,
                "options": [
                    {"text": "Cooking or hosting gatherings.", "mapping": {"Hospitality": 2}, "order": 1},
                    {"text": "Reading, studying, or teaching a subject you love.", "mapping": {"Teaching": 2}, "order": 2},
                    {"text": "Participating in community service projects.", "mapping": {"Service": 2}, "order": 3},
                    {"text": "Advising friends and family on personal matters.", "mapping": {"Counsel/Wisdom": 2}, "order": 4}
                ]
            },
            {
                "text": "When you think about your strengths, you often mention:",
                "order": 10,
                "options": [
                    {"text": "Your ability to make others feel welcome and cared for.", "mapping": {"Hospitality": 2}, "order": 1},
                    {"text": "Your talent for explaining difficult concepts clearly.", "mapping": {"Teaching": 2}, "order": 2},
                    {"text": "Your practical skills in getting things done efficiently.", "mapping": {"Service": 2}, "order": 3},
                    {"text": "Your knack for offering thoughtful advice.", "mapping": {"Counsel/Wisdom": 2}, "order": 4}
                ]
            },
            {
                "text": "If there is a conflict within a group, you:",
                "order": 11,
                "options": [
                    {"text": "Step in to mediate and help find a balanced solution.", "mapping": {"Counsel/Wisdom": 2}, "order": 1},
                    {"text": "Offer a listening ear and try to understand each side.", "mapping": {"Counsel/Wisdom": 1, "Service": 1}, "order": 2},
                    {"text": "Work to reorganize the team and restore order.", "mapping": {"Leadership": 2}, "order": 3},
                    {"text": "Ensure that everyone is treated with care and respect.", "mapping": {"Hospitality": 2}, "order": 4}
                ]
            },
            {
                "text": "Your ideal role in a ministry project would be:",
                "order": 12,
                "options": [
                    {"text": "Leading the project and making key decisions.", "mapping": {"Leadership": 2}, "order": 1},
                    {"text": "Coordinating logistics and supporting the team.", "mapping": {"Service": 2}, "order": 2},
                    {"text": "Creating and sharing informative materials about the project.", "mapping": {"Teaching": 2}, "order": 3},
                    {"text": "Ensuring that the event is warm, welcoming, and community-focused.", "mapping": {"Hospitality": 2}, "order": 4}
                ]
            },
            {
                "text": "When faced with a challenge, you are most likely to:",
                "order": 13,
                "options": [
                    {"text": "Reflect on the situation and provide considered counsel to others.", "mapping": {"Counsel/Wisdom": 2}, "order": 1},
                    {"text": "Take practical steps to resolve the issue quickly.", "mapping": {"Service": 2}, "order": 2},
                    {"text": "Organize a team to address the challenge collectively.", "mapping": {"Leadership": 2}, "order": 3},
                    {"text": "Seek to understand the emotional needs of those affected.", "mapping": {"Hospitality": 2}, "order": 4}
                ]
            },
            {
                "text": "When studying a new topic, you prefer to:",
                "order": 14,
                "options": [
                    {"text": "Dive deep and later share your findings with a group.", "mapping": {"Teaching": 2}, "order": 1},
                    {"text": "Research quietly and discuss insights with close friends.", "mapping": {"Counsel/Wisdom": 2}, "order": 2},
                    {"text": "Work with others to gather different perspectives.", "mapping": {"Leadership": 1, "Hospitality": 1}, "order": 3},
                    {"text": "Apply the knowledge practically to solve real-life problems.", "mapping": {"Service": 2}, "order": 4}
                ]
            },
            {
                "text": "How do you feel when others seek your opinion on personal matters?",
                "order": 15,
                "options": [
                    {"text": "Honored, and you carefully consider your advice.", "mapping": {"Counsel/Wisdom": 2}, "order": 1},
                    {"text": "You're willing to listen more than to speak.", "mapping": {"Hospitality": 1, "Service": 1}, "order": 2},
                    {"text": "You enjoy providing clear guidance and solutions.", "mapping": {"Teaching": 2}, "order": 3},
                    {"text": "You prefer to stay neutral and let others figure it out.", "mapping": {"Service": 2}, "order": 4}
                ]
            },
            {
                "text": "When participating in group projects, your favorite task is:",
                "order": 16,
                "options": [
                    {"text": "Organizing and coordinating the team.", "mapping": {"Leadership": 2}, "order": 1},
                    {"text": "Providing hands-on help and ensuring tasks are completed.", "mapping": {"Service": 2}, "order": 2},
                    {"text": "Explaining goals and clarifying plans to everyone.", "mapping": {"Teaching": 2}, "order": 3},
                    {"text": "Ensuring that every member feels included and valued.", "mapping": {"Hospitality": 2}, "order": 4}
                ]
            },
            {
                "text": "How do you approach learning new skills?",
                "order": 17,
                "options": [
                    {"text": "With a focus on mastering details to teach others later.", "mapping": {"Teaching": 2}, "order": 1},
                    {"text": "By engaging in practical exercises and applying them immediately.", "mapping": {"Service": 2}, "order": 2},
                    {"text": "Through thoughtful reflection and seeking advice from mentors.", "mapping": {"Counsel/Wisdom": 2}, "order": 3},
                    {"text": "By joining group workshops where you can interact and connect.", "mapping": {"Hospitality": 2}, "order": 4}
                ]
            },
            {
                "text": "When you hear a compelling idea, you are inclined to:",
                "order": 18,
                "options": [
                    {"text": "Analyze its practical implementation.", "mapping": {"Service": 2}, "order": 1},
                    {"text": "Evaluate its deeper meaning and implications.", "mapping": {"Counsel/Wisdom": 2}, "order": 2},
                    {"text": "Share it widely and spark further discussion.", "mapping": {"Teaching": 2}, "order": 3},
                    {"text": "Invite others to a discussion to explore it together.", "mapping": {"Leadership": 1, "Hospitality": 1}, "order": 4}
                ]
            },
            {
                "text": "In a time of crisis, you naturally:",
                "order": 19,
                "options": [
                    {"text": "Provide calm and thoughtful advice.", "mapping": {"Counsel/Wisdom": 2}, "order": 1},
                    {"text": "Step up to organize help and coordinate resources.", "mapping": {"Leadership": 2}, "order": 2},
                    {"text": "Offer practical assistance immediately.", "mapping": {"Service": 2}, "order": 3},
                    {"text": "Create a comforting atmosphere to ease anxiety.", "mapping": {"Hospitality": 2}, "order": 4}
                ]
            },
            {
                "text": "Reflecting on your strengths, you believe you are best at:",
                "order": 20,
                "options": [
                    {"text": "Bringing people together and making them feel at home.", "mapping": {"Hospitality": 2}, "order": 1},
                    {"text": "Teaching others and clarifying complex ideas.", "mapping": {"Teaching": 2}, "order": 2},
                    {"text": "Organizing, planning, and leading initiatives.", "mapping": {"Leadership": 2}, "order": 3},
                    {"text": "Listening and offering wise counsel in challenging times.", "mapping": {"Counsel/Wisdom": 2}, "order": 4}
                ]
            }
        ]
        
        # Create each question and its answer options
        for question_data in questions_data:
            question = Question.objects.create(
                quiz=quiz,
                text=question_data["text"],
                order=question_data["order"]
            )
            
            # Create answer options for this question
            for option_data in question_data["options"]:
                AnswerOption.objects.create(
                    question=question,
                    text=option_data["text"],
                    mapping=option_data["mapping"],
                    order=option_data["order"]
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(questions_data)} questions with answer options')) 