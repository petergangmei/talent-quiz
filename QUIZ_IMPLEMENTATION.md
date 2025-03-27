# Spiritual Gifts Quiz Implementation

## Overview

The Extensive Spiritual Gifts Quiz has been implemented as part of the Quiz Application. The quiz consists of 20 questions that help identify a person's spiritual gifts across five categories:

1. Hospitality
2. Teaching
3. Leadership
4. Counsel/Wisdom
5. Service/Practical Support

## Database Schema

The quiz utilizes the existing data model structure:

- **Quiz**: The main quiz entity
- **Question**: 20 questions about personal tendencies and preferences
- **AnswerOption**: 4 options per question, each with a JSON mapping to categories and points
- **QuizResult**: Interpretation of scores for each category

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

4. **Identify Secondary Gifts**: Categories with scores close to the primary gift (within 10-15%) are considered secondary gifts.

5. **Match Result Interpretations**: Display the descriptions corresponding to the user's highest-scoring categories.

The algorithm is implemented in the `quiz_submit` view, which:
- Processes form submissions
- Calculates category scores
- Identifies the primary category
- Finds matching result interpretations
- Displays personalized results

## Quiz Content

The quiz includes questions about:
- Social behaviors and preferences
- Problem-solving approaches
- Teaching and learning styles
- Leadership and service tendencies
- Communication preferences
- Crisis response patterns

Each answer option is carefully mapped to one or more spiritual gift categories with appropriate point values.

## Accessing the Quiz

Users can access the quiz through the main application:

1. Navigate to the home page
2. Find "Extensive Spiritual Gifts Quiz" in the available quizzes
3. Complete all 20 questions
4. Submit to see personalized results

## Result Interpretation

After completing the quiz, users receive:
- Their primary spiritual gift category
- The score for each category
- Detailed descriptions of their top gifts
- Suggestions for using these gifts in ministry or community service

## Technical Implementation

- The `JSONField` in the `AnswerOption` model stores the category-point mappings
- The algorithm in `quiz_submit` view aggregates scores per category
- The `QuizResult` model stores score ranges and interpretations
- Templates display questions, options, and results in a user-friendly format 