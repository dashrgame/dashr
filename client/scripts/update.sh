#!/bin/bash

set -e

# Configurable variables
INSTALL_DIR="$HOME/dashr"
USER_DATA_DIR="$HOME/dashr-data"
VENV_DIR="$INSTALL_DIR/venv"

# Helper functions
confirm() {
  local prompt="$1"
  local var
  read -p "$prompt" var
  [[ "$var" =~ ^[Yy]$ ]]
}

# Check if Dashr is installed
if [ ! -d "$INSTALL_DIR" ]; then
  echo "Error: Dashr is not installed at $INSTALL_DIR."
  echo "Please run the install script first."
  exit 1
fi

echo "Updating Dashr installation at $INSTALL_DIR..."

# Navigate to installation directory
cd "$INSTALL_DIR"

# Check if git repository exists
if [ ! -d ".git" ]; then
  echo "Error: Installation directory is not a git repository."
  echo "Cannot update. Please reinstall using the install script."
  exit 1
fi

# User data is stored separately at $USER_DATA_DIR and will be preserved
if [ -d "$USER_DATA_DIR" ]; then
  echo "User data found at $USER_DATA_DIR (will be preserved)"
else
  echo "No user data found at $USER_DATA_DIR"
fi

# Fetch and pull latest changes
echo "Fetching latest updates from repository..."
git fetch origin

# Check if there are updates available
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u} 2>/dev/null || git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "Dashr is already up to date!"
  echo "User data is stored at: $USER_DATA_DIR"
  exit 0
fi

echo "Updates available. Updating..."
git pull origin main

# Update Python dependencies if virtual environment exists
if [ -d "$VENV_DIR" ]; then
  echo "Updating Python dependencies..."
  source "$VENV_DIR/bin/activate"
  
  if [ -f "client/src/requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r client/src/requirements.txt --upgrade
    echo "Dependencies updated."
  else
    echo "No requirements.txt found. Skipping dependency update."
  fi
else
  echo "Warning: Virtual environment not found. Dependencies may need manual update."
  if [ -f "client/src/requirements.txt" ]; then
    echo "You can manually update dependencies with:"
    echo "python3 -m pip install -r client/src/requirements.txt --upgrade"
  fi
fi


echo ""
echo "Dashr has been successfully updated!"
echo "You can run it using: dashr"
echo "Or from the installation directory:"
echo "cd $INSTALL_DIR"
if [ -d "$VENV_DIR" ]; then
  echo "source venv/bin/activate"
fi
echo "python3 -m client.src.main"

echo ""
echo "User data is stored at: $USER_DATA_DIR"
