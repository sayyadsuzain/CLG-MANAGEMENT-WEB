# Deployment Guide for CMS on Linux with NGINX and Daphne

## Prerequisites
1. Ubuntu/Debian Linux server
2. Python 3.8 or higher
3. NGINX
4. Let's Encrypt for SSL
5. Git

## Installation Steps

### 1. System Updates and Dependencies
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx
```

### 2. Create Project Directory
```bash
sudo mkdir -p /var/www/cms
sudo chown -R $USER:$USER /var/www/cms
```

### 3. Clone Project and Setup Virtual Environment
```bash
cd /var/www/cms
git clone [your-repository-url] .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install daphne channels django-channels
```

### 4. Configure NGINX
```bash
# Copy nginx.conf
sudo cp deployment/nginx.conf /etc/nginx/sites-available/cms
sudo ln -s /etc/nginx/sites-available/cms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. Setup SSL with Let's Encrypt
```bash
sudo certbot --nginx -d your_domain.com
```

### 6. Setup Daphne Service
```bash
# Create daphne socket directory
sudo mkdir -p /run/daphne
sudo chown www-data:www-data /run/daphne

# Copy and start daphne service
sudo cp deployment/daphne.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start daphne
sudo systemctl enable daphne
```

### 7. Collect Static Files
```bash
python manage.py collectstatic
sudo mkdir -p /var/www/cms/static
sudo mkdir -p /var/www/cms/media
sudo chown -R www-data:www-data /var/www/cms/static
sudo chown -R www-data:www-data /var/www/cms/media
```

### 8. Database Setup
```bash
python manage.py migrate
```

### 9. Create Superuser
```bash
python manage.py createsuperuser
```

### 10. Set Permissions
```bash
sudo chown -R www-data:www-data /var/www/cms
sudo chmod -R 755 /var/www/cms
```

## Maintenance

### Viewing Logs
- NGINX logs: `sudo tail -f /var/log/nginx/error.log`
- Daphne logs: `sudo journalctl -u daphne`

### Restarting Services
```bash
sudo systemctl restart nginx
sudo systemctl restart daphne
```

### Updating the Application
```bash
cd /var/www/cms
source venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart daphne
```

## Security Notes
1. Make sure to update `your_domain.com` in nginx.conf
2. Keep your system and packages updated
3. Use strong passwords
4. Configure firewall (UFW) to allow only necessary ports
5. Regularly backup your database and media files 