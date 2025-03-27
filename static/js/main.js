// Custom JavaScript for Quiz App

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    
    // Add form validation for quiz submissions
    const quizForm = document.querySelector('form[action*="quiz"]');
    if (quizForm) {
        quizForm.addEventListener('submit', function(event) {
            const questions = document.querySelectorAll('.card-header');
            const answered = Array.from(questions).map(header => {
                const questionId = header.closest('.card').querySelector('input[type="radio"]:checked');
                return !!questionId;
            });
            
            const unanswered = answered.indexOf(false);
            
            if (unanswered !== -1) {
                event.preventDefault();
                alert(`Please answer question ${unanswered + 1} before submitting.`);
                questions[unanswered].scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
    
    // Add animation to result cards
    const resultCards = document.querySelectorAll('.card-body .card');
    if (resultCards.length) {
        resultCards.forEach((card, index) => {
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 200);
        });
    }
    
    // Initialize any tooltips
    const tooltips = document.querySelectorAll('[data-toggle="tooltip"]');
    if (tooltips.length && typeof $().tooltip === 'function') {
        $(function () {
            $('[data-toggle="tooltip"]').tooltip();
        });
    }
}); 