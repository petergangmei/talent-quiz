from django.core.management.base import BaseCommand
from app.models import Quiz, Question, AnswerOption, QuizResult
from django.db import transaction


class Command(BaseCommand):
    """
    Management command to create the Spiritual Gifts Assessment Survey with 
    all 80 questions, 5-point rating scale, and 16 spiritual gift categories.
    """
    help = 'Creates the Spiritual Gifts Assessment Survey with 80 questions and 1-5 rating scale'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating Spiritual Gifts Assessment Survey...'))
        
        with transaction.atomic():
            # Create the quiz
            quiz, created = Quiz.objects.get_or_create(
                title="Spiritual Gifts Assessment Survey",
                defaults={
                    'description': (
                        "This is not a test, so there are no wrong answers. The Spiritual Gifts Survey consists "
                        "of 80 statements. Some items reflect concrete actions, other items are descriptive traits, "
                        "and still others are statements of belief.\n\n"
                        "Select the one response you feel best characterizes yourself for each statement. "
                        "Do not spend too much time on any one item. Usually your immediate response is best."
                    )
                }
            )
            
            if not created:
                self.stdout.write(self.style.WARNING('Quiz already exists. Updating existing quiz...'))
                # Clear existing questions to avoid duplication
                quiz.questions.all().delete()
                quiz.description = (
                    "This is not a test, so there are no wrong answers. The Spiritual Gifts Survey consists "
                    "of 80 statements. Some items reflect concrete actions, other items are descriptive traits, "
                    "and still others are statements of belief.\n\n"
                    "Select the one response you feel best characterizes yourself for each statement. "
                    "Do not spend too much time on any one item. Usually your immediate response is best."
                )
                quiz.save()
            
            # Create quiz result interpretations
            self._create_result_interpretations(quiz)
            
            # Create all questions and answer options
            self._create_questions_and_answers(quiz)
            
            self.stdout.write(self.style.SUCCESS('Spiritual Gifts Assessment Survey successfully created!'))
    
    def _create_result_interpretations(self, quiz):
        """Create result interpretations for the 16 spiritual gift categories"""
        result_categories = {
            "Leadership": {
                "min_score": 5,
                "max_score": 25,
                "description": (
                    "Your gift of Leadership reveals your ability to cast vision, organize resources, "
                    "and inspire others toward a common goal. You naturally take initiative and help groups "
                    "move forward effectively."
                )
            },
            "Administration": {
                "min_score": 5,
                "max_score": 25,
                "description": (
                    "Your gift of Administration shows your ability to organize ideas, resources, time, "
                    "and people effectively. You excel at coordinating tasks and managing details to accomplish goals."
                )
            },
            "Teaching": {
                "min_score": 5,
                "max_score": 25,
                "description": (
                    "Your gift of Teaching demonstrates your ability to communicate knowledge and truth "
                    "in a way that others can understand and apply. You enjoy studying and explaining concepts clearly."
                )
            },
            "Knowledge": {
                "min_score": 5,
                "max_score": 25,
                "description": (
                    "Your gift of Knowledge reflects your love for studying and acquiring deep understanding. "
                    "You enjoy researching, discovering new information, and sharing insights with others."
                )
            },
            "Wisdom": {
                "min_score": 5,
                "max_score": 25,
                "description": (
                    "Your gift of Wisdom shows your ability to apply knowledge practically and discern truth. "
                    "You can relate God's truth to specific situations and provide sound guidance based on spiritual understanding."
                )
            },
            "Prophecy": {
                "min_score": 5,
                "max_score": 25,
                "description": (
                    "Your gift of Prophecy enables you to boldly speak God's truth, sometimes with a focus on "
                    "calling for repentance, righteousness, or revealing God's perspective on current situations."
                )
            },
            "Discernment": {
                "min_score": 5,
                "max_score": 25,
                "description": (
                    "Your gift of Discernment allows you to distinguish between truth and error, recognizing "
                    "the source of spiritual messages or motivations. You can sense when something is or isn't aligned with God's will."
                )
            },
            "Exhortation": {
                "min_score": 5,
                "max_score": 25,
                "description": (
                    "Your gift of Exhortation enables you to encourage, comfort, and motivate others. "
                    "You have a natural ability to offer words that strengthen faith and promote growth in others."
                )
            },
            "Shepherding": {
                "min_score": 5,
                "max_score": 25,
                "description": (
                    "Your gift of Shepherding reflects your ability to guide, nurture, and care for others "
                    "on their spiritual journey. You help others grow in their faith and provide ongoing support."
                )
            },
            "Faith": {
                "min_score": 5,
                "max_score": 25,
                "description": (
                    "Your gift of Faith demonstrates an exceptional ability to trust God in difficult situations. "
                    "You maintain confidence in God's promises even when facing challenges that might cause others to doubt."
                )
            },
            "Evangelism": {
                "min_score": 5,
                "max_score": 25,
                "description": (
                    "Your gift of Evangelism shows your passion and effectiveness in sharing the gospel with "
                    "non-believers. You naturally communicate the message of salvation in ways that resonate with others."
                )
            },
            "Apostleship": {
                "min_score": 5,
                "max_score": 25,
                "description": (
                    "Your gift of Apostleship reflects your desire to start new ministries, churches, or initiatives. "
                    "You're comfortable crossing cultural boundaries and pioneering new work for the Kingdom."
                )
            },
            "Service/Helps": {
                "min_score": 5,
                "max_score": 25,
                "description": (
                    "Your gift of Service/Helps enables you to identify and meet practical needs with joy. "
                    "You find fulfillment in supporting others and working behind the scenes to accomplish necessary tasks."
                )
            },
            "Mercy": {
                "min_score": 5,
                "max_score": 25,
                "description": (
                    "Your gift of Mercy reflects your deep compassion for those who are suffering. "
                    "You have genuine empathy and a desire to alleviate pain, offering comfort and practical help."
                )
            },
            "Giving": {
                "min_score": 5,
                "max_score": 25,
                "description": (
                    "Your gift of Giving shows your generosity and joy in sharing resources to support God's work. "
                    "You manage your resources well and find fulfillment in contributing to worthy causes."
                )
            },
            "Hospitality": {
                "min_score": 5,
                "max_score": 25,
                "description": (
                    "Your gift of Hospitality enables you to make others feel welcome and comfortable. "
                    "You excel at creating warm environments where people feel valued and accepted."
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
        """Create all 80 questions and their answer options with 1-5 rating scale"""
        # Standard answer options for all questions (1-5 rating scale)
        standard_options = [
            {"text": "5 — Highly characteristic of me/definitely true for me", "order": 1},
            {"text": "4 — Most of the time this would describe me/be true for me", "order": 2},
            {"text": "3 — Frequently characteristic of me/true for me – about 50% of the time", "order": 3},
            {"text": "2 — Occasionally characteristic of me/true for me – about 25% of the time", "order": 4},
            {"text": "1 — Not at all characteristic of me/definitely untrue for me", "order": 5}
        ]
        
        # Gift category mapping (question order number to gift category)
        gift_mapping = {
            # Leadership: Items 6, 16, 27, 43, 65
            6: "Leadership", 16: "Leadership", 27: "Leadership", 43: "Leadership", 65: "Leadership",
            # Administration: Items 1, 17, 31, 47, 59
            1: "Administration", 17: "Administration", 31: "Administration", 47: "Administration", 59: "Administration",
            # Teaching: Items 2, 18, 33, 61, 73
            2: "Teaching", 18: "Teaching", 33: "Teaching", 61: "Teaching", 73: "Teaching",
            # Knowledge: Items 9, 24, 39, 68, 79
            9: "Knowledge", 24: "Knowledge", 39: "Knowledge", 68: "Knowledge", 79: "Knowledge",
            # Wisdom: Items 3, 19, 48, 62, 74
            3: "Wisdom", 19: "Wisdom", 48: "Wisdom", 62: "Wisdom", 74: "Wisdom",
            # Prophecy: Items 10, 25, 40, 54, 69
            10: "Prophecy", 25: "Prophecy", 40: "Prophecy", 54: "Prophecy", 69: "Prophecy",
            # Discernment: Items 11, 26, 41, 55, 70
            11: "Discernment", 26: "Discernment", 41: "Discernment", 55: "Discernment", 70: "Discernment",
            # Exhortation: Items 20, 34, 49, 63, 75
            20: "Exhortation", 34: "Exhortation", 49: "Exhortation", 63: "Exhortation", 75: "Exhortation",
            # Shepherding: Items 4, 21, 35, 50, 76
            4: "Shepherding", 21: "Shepherding", 35: "Shepherding", 50: "Shepherding", 76: "Shepherding",
            # Faith: Items 12, 28, 42, 56, 80
            12: "Faith", 28: "Faith", 42: "Faith", 56: "Faith", 80: "Faith",
            # Evangelism: Items 5, 36, 51, 64, 77
            5: "Evangelism", 36: "Evangelism", 51: "Evangelism", 64: "Evangelism", 77: "Evangelism",
            # Apostleship: Items 13, 29, 44, 57, 71
            13: "Apostleship", 29: "Apostleship", 44: "Apostleship", 57: "Apostleship", 71: "Apostleship",
            # Service/Helps: Items 14, 30, 46, 58, 72
            14: "Service/Helps", 30: "Service/Helps", 46: "Service/Helps", 58: "Service/Helps", 72: "Service/Helps",
            # Mercy: Items 7, 22, 37, 52, 66
            7: "Mercy", 22: "Mercy", 37: "Mercy", 52: "Mercy", 66: "Mercy",
            # Giving: Items 8, 23, 38, 53, 67
            8: "Giving", 23: "Giving", 38: "Giving", 53: "Giving", 67: "Giving",
            # Hospitality: Items 15, 32, 45, 60, 78
            15: "Hospitality", 32: "Hospitality", 45: "Hospitality", 60: "Hospitality", 78: "Hospitality"
        }
        
        # Define all 80 questions
        questions_data = [
            {"order": 1, "text": "I have the ability to organize ideas, resources, time, and people effectively."},
            {"order": 2, "text": "I am willing to study and prepare for the task of teaching."},
            {"order": 3, "text": "I am able to relate the truths of God to specific situations."},
            {"order": 4, "text": "I have a God-given ability to help others grow in their faith."},
            {"order": 5, "text": "I possess a special ability to communicate the truth of salvation."},
            {"order": 6, "text": "I have the ability to make critical decisions when necessary."},
            {"order": 7, "text": "I am sensitive to the hurts of people."},
            {"order": 8, "text": "I experience joy in meeting needs through sharing possessions."},
            {"order": 9, "text": "I enjoy studying."},
            {"order": 10, "text": "I have delivered God's message of warning and judgment."},
            {"order": 11, "text": "I am able to sense the true motivation of persons and movements."},
            {"order": 12, "text": "I have a special ability to trust God in difficult situations."},
            {"order": 13, "text": "I have a strong desire to contribute to the establishment of new churches."},
            {"order": 14, "text": "I take action to meet physical and practical needs rather than merely talking about or planning how to help."},
            {"order": 15, "text": "I enjoy entertaining guests in my home."},
            {"order": 16, "text": "I can adapt my guidance to fit the maturity of those working with me."},
            {"order": 17, "text": "I can delegate and assign meaningful work."},
            {"order": 18, "text": "I have an ability and desire to teach."},
            {"order": 19, "text": "I am usually able to analyze a situation correctly."},
            {"order": 20, "text": "I have a natural tendency to encourage others."},
            {"order": 21, "text": "I am willing to take the initiative in helping other Christians grow in their faith."},
            {"order": 22, "text": "I have an acute awareness of other people's emotions, such as loneliness, pain, fear, and anger."},
            {"order": 23, "text": "I am a cheerful giver."},
            {"order": 24, "text": "I spend time digging into facts."},
            {"order": 25, "text": "I feel that I have a message from God to deliver to others."},
            {"order": 26, "text": "I can recognize when a person is genuine/honest."},
            {"order": 27, "text": "I am a person of vision (a clear mental portrait of a preferable future given by God). I am able to communicate vision in such a way that others commit to making the vision a reality."},
            {"order": 28, "text": "I am willing to yield to God's will rather than question and waver."},
            {"order": 29, "text": "I would like to be more active in getting the gospel to people in other countries."},
            {"order": 30, "text": "It makes me happy to do things for people in need."},
            {"order": 31, "text": "I am successful in getting a group to do its work joyfully."},
            {"order": 32, "text": "I am able to make strangers feel at ease."},
            {"order": 33, "text": "I have the ability to teach to a variety of different learning styles."},
            {"order": 34, "text": "I can identify those who need encouragement."},
            {"order": 35, "text": "I have trained Christians to be more obedient disciples of Christ."},
            {"order": 36, "text": "I am willing to do whatever it takes to see others come to Christ."},
            {"order": 37, "text": "I am drawn to people who are hurting."},
            {"order": 38, "text": "I am a generous giver."},
            {"order": 39, "text": "I am able to discover new truths in Scripture."},
            {"order": 40, "text": "I have spiritual insights from Scripture concerning issues and people that compel me to speak out."},
            {"order": 41, "text": "I can sense when a person is acting in accordance with God's will."},
            {"order": 42, "text": "I can trust in God even when things look dark."},
            {"order": 43, "text": "I can determine where God wants a group to go and help it get there."},
            {"order": 44, "text": "I have a strong desire to take the gospel to places where it has never been heard."},
            {"order": 45, "text": "I enjoy reaching out to new people in my church and community."},
            {"order": 46, "text": "I am sensitive to the needs of people."},
            {"order": 47, "text": "I have been able to make effective and efficient plans for accomplishing the goals of a group."},
            {"order": 48, "text": "I often am consulted when fellow Christians are struggling to make difficult decisions."},
            {"order": 49, "text": "I think about how I can comfort and encourage others in my congregation."},
            {"order": 50, "text": "I am able to give spiritual direction to others."},
            {"order": 51, "text": "I am able to present the gospel to lost persons in such a way that they accept the Lord and His salvation."},
            {"order": 52, "text": "I possess an unusual capacity to understand the feelings of those in distress."},
            {"order": 53, "text": "I have a strong sense of stewardship based on the recognition that God owns all things."},
            {"order": 54, "text": "I have delivered to other persons messages that have come directly from God."},
            {"order": 55, "text": "I can sense when a person is acting under God's leadership."},
            {"order": 56, "text": "I try to be in God's will continually and be available for His use."},
            {"order": 57, "text": "I feel that I should take the gospel to people who have different beliefs from me."},
            {"order": 58, "text": "I have an acute awareness of the physical needs of others."},
            {"order": 59, "text": "I am skilled in setting forth positive and precise steps of action."},
            {"order": 60, "text": "I like to meet visitors at church and make them feel welcome."},
            {"order": 61, "text": "I explain Scripture in such a way that others understand it."},
            {"order": 62, "text": "I can usually see spiritual solutions to problems."},
            {"order": 63, "text": "I welcome opportunities to help people who need comfort, consolation, encouragement, and counseling."},
            {"order": 64, "text": "I feel at ease in sharing Christ with nonbelievers."},
            {"order": 65, "text": "I can influence others to perform to their highest God-given potential."},
            {"order": 66, "text": "I recognize the signs of stress and distress in others."},
            {"order": 67, "text": "I desire to give generously and unpretentiously to worthwhile projects and ministries."},
            {"order": 68, "text": "I can organize facts into meaningful relationships."},
            {"order": 69, "text": "God gives me messages to deliver to His people."},
            {"order": 70, "text": "I am able to sense whether people are being honest when they tell of their religious experiences."},
            {"order": 71, "text": "I enjoy presenting the gospel to persons of other cultures and backgrounds."},
            {"order": 72, "text": "I enjoy doing little things that help people."},
            {"order": 73, "text": "I can give a clear, uncomplicated presentation of the gospel."},
            {"order": 74, "text": "I have been able to apply biblical truth to the specific needs of my church."},
            {"order": 75, "text": "God has used me to encourage others to live Christlike lives."},
            {"order": 76, "text": "I have sensed the need to help other people become more effective in their ministries."},
            {"order": 77, "text": "I like to talk about Jesus to those who do not know Him."},
            {"order": 78, "text": "I have the ability to make strangers feel comfortable in my home."},
            {"order": 79, "text": "I have a wide range of study resources and know how to secure information."},
            {"order": 80, "text": "I feel assured that a situation will change for the glory of God even when the situation seem impossible."}
        ]
        
        # Create each question and its answer options
        for question_data in questions_data:
            question = Question.objects.create(
                quiz=quiz,
                text=question_data["text"],
                order=question_data["order"]
            )
            
            # Get which gift category this question belongs to
            gift_category = gift_mapping.get(question_data["order"])
            
            # Create the answer options (1-5 rating scale)
            for option_data in standard_options:
                # The score value is reversed from the display order
                # 5 (highest) is option order 1, 4 is option order 2, etc.
                score_value = 6 - option_data["order"]  # Convert option order to score value
                
                # Create mapping with the appropriate gift category and score
                mapping = {}
                if gift_category:
                    mapping = {gift_category: score_value}
                
                AnswerOption.objects.create(
                    question=question,
                    text=option_data["text"],
                    order=option_data["order"],
                    mapping=mapping
                )
        
        self.stdout.write(self.style.SUCCESS(f'Created 80 questions with rating scale options')) 