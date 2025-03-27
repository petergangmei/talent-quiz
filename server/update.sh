#!/bin/bash

# Set path to virtual environment
VENV_PATH="$HOME/tq/venv"

# Update the code repository
git stash
git stash drop
git pull

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
fi

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source "$VENV_PATH/bin/activate"
pip install -r requirements.txt
deactivate

# Restart the server
echo "Restarting services..."
sudo systemctl daemon-reload
sudo systemctl restart tq
sudo systemctl reload nginx

echo "Update completed successfully!"