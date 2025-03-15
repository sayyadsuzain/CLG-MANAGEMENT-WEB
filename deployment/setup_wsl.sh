#!/bin/bash

echo "Setting up CMS with NGINX and Daphne in WSL..."

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "Installing required packages..."
sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx

# Create project directory
echo "Creating project directory..."
sudo mkdir -p /var/www/cms
sudo chown -R $USER:$USER /var/www/cms

# Copy project files
echo "Copying project files..."
current_dir=$(pwd)
sudo cp -r $current_dir/* /var/www/cms/

# Setup virtual environment
echo "Setting up Python virtual environment..."
cd /var/www/cms
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure NGINX
echo "Configuring NGINX..."
sudo cp deployment/nginx.conf /etc/nginx/sites-available/cms
sudo ln -sf /etc/nginx/sites-available/cms /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Update NGINX config for local development
sudo sed -i 's/your_domain.com/localhost/g' /etc/nginx/sites-available/cms
sudo sed -i 's/listen 443 ssl/listen 443/g' /etc/nginx/sites-available/cms
sudo sed -i 's/ssl_certificate/# ssl_certificate/g' /etc/nginx/sites-available/cms
sudo sed -i 's/ssl_certificate_key/# ssl_certificate_key/g' /etc/nginx/sites-available/cms

# Create directories for Daphne
echo "Setting up Daphne..."
sudo mkdir -p /run/daphne
sudo chown www-data:www-data /run/daphne

# Setup Daphne service
sudo cp deployment/daphne.service /etc/systemd/system/
sudo systemctl daemon-reload

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput
sudo mkdir -p /var/www/cms/static
sudo mkdir -p /var/www/cms/media
sudo chown -R www-data:www-data /var/www/cms/static
sudo chown -R www-data:www-data /var/www/cms/media

# Set permissions
echo "Setting permissions..."
sudo chown -R www-data:www-data /var/www/cms
sudo chmod -R 755 /var/www/cms

# Start services
echo "Starting services..."
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl start daphne
sudo systemctl enable daphne

echo "Setup complete! Your CMS should be running at http://localhost"
echo "Check NGINX status with: sudo systemctl status nginx"
echo "Check Daphne status with: sudo systemctl status daphne" 