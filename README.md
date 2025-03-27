# Talent Quiz

Talent Quiz is an open-source Django application designed to help users discover their talents and spiritual gifts through a customizable quiz. Administrators can easily create quizzes, manage questions and answer options, and define result interpretations using an intuitive admin panel. The frontend leverages Django templating and MDB Bootstrap for a modern, responsive UI.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features

- **Dynamic Quiz Creation:**  
  Create and manage multiple quizzes with titles, descriptions, questions, and answer options via the admin panel.

- **Customizable Answer Mappings:**  
  Define custom point mappings for each answer option to compute results for different talent or spiritual gift categories.

- **Result Calculation:**  
  A built-in algorithm aggregates scores and determines a user's primary talent based on their responses.

- **Responsive UI:**  
  Uses MDB Bootstrap for a modern, mobile-friendly design.

- **Open Source:**  
  Community-driven project with a focus on customization and ease of use.

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** Django Templates, MDB Bootstrap
- **Database:** SQLite (default) or any database supported by Django
- **Version Control:** Git

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/talent-quiz.git
   cd talent-quiz
   ```

2. **Create and Activate a Virtual Environment:**

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Migrations:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a Superuser:**

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the Development Server:**

   ```bash
   python manage.py runserver
   ```

## Configuration

- **Admin Panel:**  
  Log in to `/admin` to add quizzes, questions, and answer options.  
- **Static Files:**  
  Ensure your static files (including MDB Bootstrap) are properly configured in `settings.py` or served via a CDN.

## Usage

1. **Creating a Quiz:**  
   Access the admin panel and add a new quiz with its title and description.

2. **Adding Questions & Answers:**  
   Under each quiz, add questions and provide answer options. Each answer can include a JSON mapping to different talent categories (e.g., `{"Leadership": 2}`).

3. **Taking the Quiz:**  
   Visit `/quiz/` to see a list of available quizzes. Click a quiz to answer questions and submit your responses.

4. **Viewing Results:**  
   After submission, the application calculates scores based on your answers and displays your primary talent along with detailed category scores.

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/my-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push your branch (`git push origin feature/my-feature`).
5. Open a Pull Request.

Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for more details on the code of conduct and submission guidelines.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Thanks to the Django community for the robust framework.
- MDB Bootstrap for the sleek and responsive UI components.
- All contributors who help make this project better!

---

Feel free to modify this README as needed to better reflect your project's specific features and any additional instructions for deployment or customization.