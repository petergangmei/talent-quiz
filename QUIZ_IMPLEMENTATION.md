# Spiritual Gifts Quiz Implementation

## Overview

The Extensive Spiritual Gifts Quiz has been implemented as part of the Quiz Application. The quiz consists of 20 questions that help identify a person's spiritual gifts across five categories:

1. Hospitality
2. Teaching
3. Leadership
4. Counsel/Wisdom
5. Service/Practical Support

## New Step-by-Step Quiz Experience

The quiz now features a step-by-step experience with the following improvements:

1. **User Identification**: Users enter their name before starting a quiz
2. **One Question at a Time**: Questions are presented individually for better focus
3. **Progress Tracking**: A progress bar shows completion percentage
4. **Skip Option**: Users can skip questions they're unsure about
5. **Persistent Results**: Quiz results are stored and accessible for 30 days
6. **Unique Result URLs**: Each completed quiz has a unique URL with token for access

## Database Schema

The quiz utilizes the following data model structure:

- **Quiz**: The main quiz entity
- **Question**: 20 questions about personal tendencies and preferences
- **AnswerOption**: 4 options per question, each with a JSON mapping to categories and points
- **QuizResult**: Interpretation of scores for each category
- **UserQuiz**: Tracks a user's quiz session with name, IP, progress, and results
- **UserResponse**: Records individual responses to questions (or skips)

## Setup Process

The quiz is loaded into the database using a custom management command:

```bash
python manage.py load_spiritual_gifts_quiz --settings=core.settings.dev
```

This command creates:
- The main quiz with its description
- All 20 questions in the specified order
- 4 answer options for each question with their category point mappings
- Result interpretations for each spiritual gift category

## Scoring Algorithm

The scoring algorithm follows these steps:

1. **Initialize Scores**: Create a score counter for each category (Hospitality, Teaching, Leadership, Counsel/Wisdom, Service).

2. **Process Answers**: For each selected answer option, add the corresponding points to the categories based on the mapping.

3. **Calculate Results**: After processing all answers, determine the primary spiritual gift (category with highest score).

4. **Identify Secondary Gifts**: Categories with scores close to the primary gift (within 15% of primary) are considered secondary gifts.

5. **Match Result Interpretations**: Display the descriptions corresponding to the user's highest-scoring categories.

## User Experience Flow

1. **Start**: User visits the quiz detail page and clicks "Start Quiz"
2. **Name Entry**: User provides their name to begin
3. **Question Navigation**: 
   - One question is displayed at a time
   - User selects an answer or skips
   - Progress bar updates after each question
4. **Results**: Upon completion, detailed results are shown with:
   - Primary gift with score and interpretation
   - Secondary gifts with scores and interpretations
   - Complete breakdown of all category scores

## Quiz Content

The quiz includes questions about:
- Social behaviors and preferences
- Problem-solving approaches
- Teaching and learning styles
- Leadership and service tendencies
- Communication preferences
- Crisis response patterns

Each answer option is carefully mapped to one or more spiritual gift categories with appropriate point values.

## Result Persistence

Users can:
- Bookmark their result page for future reference
- Return to view results for up to 30 days
- Take the quiz again to get updated results

## Maintenance and Cleanup

A management command is available to clean up expired quiz attempts:

```bash
# Preview what would be deleted
python manage.py cleanup_expired_quizzes --dry-run --settings=core.settings.dev

# Actually delete expired quiz attempts
python manage.py cleanup_expired_quizzes --settings=core.settings.dev
```

## Technical Implementation

- The `JSONField` in the `AnswerOption` model stores the category-point mappings
- The algorithm in `calculate_results` aggregates scores per category
- The `UserQuiz` model stores quiz progress and result data
- The `UserResponse` model tracks individual question responses
- Templates display questions, options, and results in a user-friendly format 