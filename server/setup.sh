#!/usr/bin/env bash

PROJECT_MAIN_DIR_NAME="tq"

# Add menu to choose between new and old instance
echo "---------------------------------------"
echo "Welcome to the RuangmeiDictionary Setup"
echo "---------------------------------------"
echo "Please select an option:"
echo "1. New Instance (Full installation)"
echo "2. Old Instance (Skip system dependencies)"
echo "---------------------------------------"
read -p "Enter your choice (1 or 2): " choice

# Check if the input is valid
while [[ "$choice" != "1" && "$choice" != "2" ]]; do
    echo "Invalid input. Please enter 1 or 2."
    read -p "Enter your choice (1 or 2): " choice
done

# Execute system dependencies installation only for new instance
if [[ "$choice" == "1" ]]; then
    echo "Selected: New Instance - Installing all dependencies..."
    
    sudo apt-get update
    sudo apt-get upgrade -y

    # Install Nginx
    sudo apt install -y nginx

    # Install Python3 pip
    sudo apt install -y python3-pip

    # Install Virtualenv
    # sudo apt install -y virtualenv
    sudo apt-get install python3-venv -y
else
    echo "Selected: Old Instance - Skipping system dependencies installation..."
fi

# Common steps for both new and old instances
echo "Performing common setup steps..."

# Change ownership and permissions
sudo chown -R $USER:$USER "/home/ubuntu/$PROJECT_MAIN_DIR_NAME"
sudo chmod -R 755 "/home/ubuntu/$PROJECT_MAIN_DIR_NAME"

echo "Copying gunicorn.conf file..."
sudo cp "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/server/gunicorn.service" "/etc/systemd/system/$PROJECT_MAIN_DIR_NAME.service"

sudo systemctl daemon-reload
sudo systemctl start $PROJECT_MAIN_DIR_NAME
sudo systemctl enable $PROJECT_MAIN_DIR_NAME

sudo cp "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/server/nginx.conf" "/etc/nginx/sites-available/$PROJECT_MAIN_DIR_NAME.conf"
sudo ln -s "/etc/nginx/sites-available/$PROJECT_MAIN_DIR_NAME.conf" "/etc/nginx/sites-enabled/"

sudo nginx -t
# sudo systemctl restart nginx
sudo systemctl reload nginx

#create virtual environment
echo "Creating virtual environment..."
python3 -m venv "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/venv"

# Change ownership and permissions for the virtual environment
sudo chown -R $USER:$USER "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/venv"
sudo chmod -R 755 "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/venv"
sudo chmod -R 755 "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/server"

# Install requirements
echo "Installing requirements..."
source "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/venv/bin/activate"
pip install psycopg2-binary gunicorn gevent
pip install -r "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/requirements.txt"

# Migrate
echo "Migrating..."
python "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/manage.py" migrate --settings=core.settings.prod

# Collect static
echo "Collecting static files..."
# python "/home/ubuntu/$PROJECT_MAIN_DIR_NAME/manage.py" collectstatic --settings=core.settings.prod

# Restart gunicorn
echo "Restarting gunicorn..."
sudo systemctl daemon-reload
sudo systemctl restart $PROJECT_MAIN_DIR_NAME.service
sudo systemctl reload nginx

echo "Setup completed successfully!"
