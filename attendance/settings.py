import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Ensure the log file exists and is writable
LOG_FILE = os.path.join(LOGS_DIR, 'cms.log')
try:
    # Create the file if it doesn't exist
    with open(LOG_FILE, 'a') as f:
        f.write('Log file initialized\n')
except Exception as e:
    print(f"Error creating log file: {e}")

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} [{name}] {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',  # Using RotatingFileHandler instead of FileHandler
            'filename': LOG_FILE,
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'encoding': 'utf-8',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
        },
        'django': {  # Django logger
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {  # Server requests and responses
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {  # Request processing
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.template': {  # Template rendering
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {  # Database operations
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'attendance': {  # Your app's logger
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

# ... rest of your settings ...

# ... existing middleware ...
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'attendance.middleware.RequestLoggingMiddleware',  # Add our custom middleware
]

# ... rest of settings ... 