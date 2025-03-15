#!/bin/bash

# Fix package manager
sudo dpkg --configure -a
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx

# Create and activate virtual environment
cd /var/www/cms
python3 -m venv venv
source venv/bin/activate

# Install Daphne and dependencies
pip install daphne channels django-channels

# Create Daphne socket directory
sudo mkdir -p /run/daphne
sudo chown www-data:www-data /run/daphne

# Copy Daphne service file
sudo cp deployment/daphne.service /etc/systemd/system/

# Reload systemd and start Daphne
sudo systemctl daemon-reload
sudo systemctl start daphne
sudo systemctl enable daphne

# Check status
sudo systemctl status daphne 