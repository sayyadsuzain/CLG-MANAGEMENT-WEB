# College Management System (CMS)

A comprehensive web-based College Management System built with Django and Daphne, featuring SSL support and real-time capabilities.

## Features

- **Secure Authentication**: SSL-enabled secure login system
- **Faculty Management**: Course assignments, grading, and resource management
- **Student Portal**: Course enrollment, assignment submission, and grade viewing
- **Real-time Updates**: WebSocket-based notifications and updates
- **Resource Management**: Upload and manage course materials
- **Attendance Tracking**: Digital attendance management system
- **Excel Integration**: Export data to Excel format for reporting

## Prerequisites

- Python 3.12+
- WSL (Windows Subsystem for Linux) or Linux
- Virtual Environment
- SSL Certificate and Private Key

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/sayyadsuzain/CLG-MANAGEMENT-WEB.git
   cd CLG-MANAGEMENT-WEB
   ```

2. Create and activate virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # Linux/WSL
   # OR
   .\venv\Scripts\activate  # Windows
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Configure SSL:

   ```
   mkdir ssl
   # Place your SSL certificates in the ssl directory:
   # - ssl/private.key
   # - ssl/certificate.crt
   ```

5. Set up the database:

   ```
   python manage.py migrate
   python manage.py createsuperuser
   ```

## Running the Server

### Using the Simplified Scripts

1. Windows Command Prompt:

   ```
   deployment\run_daphne.bat
   ```

2. WSL/Linux:

   ```
   bash deployment/run_daphne.sh
   ```

The server will start at `https://localhost:8443`

## Project Structure

```
college_management/
├── attendance/           # Main application module
│   ├── migrations/      # Database migrations
│   ├── templates/       # HTML templates
│   ├── static/         # Static files (CSS, JS)
│   ├── models.py       # Database models
│   ├── views.py        # View controllers
│   └── urls.py         # URL routing
├── college_management/  # Project settings
│   ├── settings.py     # Main settings file
│   ├── urls.py         # Main URL routing
│   └── asgi.py         # ASGI configuration
├── deployment/         # Deployment scripts
│   ├── run_daphne.bat  # Windows startup script
│   └── run_daphne.sh   # Linux startup script
├── ssl/               # SSL certificates
├── static/            # Global static files
├── templates/         # Global templates
├── manage.py          # Django management script
└── requirements.txt   # Project dependencies
```

## Security Notes

- Keep SSL certificates secure and set proper permissions
- Never commit sensitive data or credentials
- Regularly update dependencies
- Use environment variables for sensitive settings

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
