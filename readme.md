# Fortify: Messaging Platform with Django, REST API, and WebSocket

**Fortify** is a real-time messaging platform built using **Django**, leveraging **Django REST Framework (DRF)** for user management and **WebSocket** for real-time communication. It allows users to register, log in, and interact with messages instantly, making it an ideal solution for scalable messaging services with bidirectional communication.

---

## Features:
- **User Authentication**: Users can register, log in, and manage their profiles.
- **Real-Time Messaging**: Send and receive messages instantly using WebSocket.
- **Instant Updates**: Messages and notifications appear in real-time without page refresh.
- **REST API**: Exposes RESTful APIs for user management, message history, and more.
- **WebSocket Integration**: Real-time, bidirectional communication between users.

---

## Installation

### Prerequisites:
Ensure you have the following installed:
- Python 3.x
- Django
- Redis server
- PostgreSQL (or another database)

---

### Steps to Install and Set Up:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/username/fortify.git
   cd fortify
   ```

2. **Create a virtual environment and activate it**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # For Windows: venv\Scripts\activate
   ```

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory and add the following environment variables:
   ```ini
   ALLOWED_HOSTS=your-domain.com
   DATABASE_URL=postgres://user:password@localhost:5432/dbname
   DEBUG=True
   DJANGO_SECRET_KEY=your-secret-key
   DJANGO_SETTINGS_MODULE=fortify.settings
   REDIS_URL=redis://localhost:6379/0
   PORT=8000  # Add this line for the port you're using with Gunicorn

   ```
   Replace each value with the correct settings for your environment. Be sure to configure the Redis and PostgreSQL servers before proceeding.

5. **Configure email settings**:
   In `settings.py`, make sure the email configuration is correctly set up:
   ```python
   # Email settings
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = config('EMAIL_HOST')
   EMAIL_PORT = config('EMAIL_PORT', cast=int)
   EMAIL_USE_SSL = config('EMAIL_USE_SSL', cast=bool)
   EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
   EMAIL_HOST_USER = config('EMAIL_HOST_USER')
   EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
   DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
   ```
6. **Create migration files**:
   ```bash
   python manage.py makemigrations
   ```

7. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

8. **Start the Django development server**:
   ```bash
   gunicorn Fortify_back.asgi:application --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   ```

---

## Usage
- Access the platform via your browser at `http://localhost:8000`.
- Register a new account or log in with existing credentials.
- Start sending and receiving messages in real-time.

---

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push to the branch.
4. Submit a pull request.

---

## License
This project is available for free use. There are no strict licensing terms, so feel free to use, modify, distribute, and adapt it for any purpose, personal or commercial, without any restrictions.

---

## Contact
For any questions or issues, please open an issue on the [GitHub repository](https://github.com/amirhossein-moloki/Fortify_backend-publish/) or contact the maintainer at [amirh.moloki@gmail.com](mailto:amirh.moloki@gmail.com).

---

**Enjoy using Fortify!** 🚀
