#!/bin/bash

# Change to the project directory
cd /var/www/cms

# Activate virtual environment
source venv/bin/activate

# Run Daphne with SSL configuration
daphne -e ssl:8443:privateKey=ssl/private.key:certKey=ssl/certificate.crt college_management.asgi:application 