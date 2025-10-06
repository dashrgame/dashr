#!/bin/bash

set -e

# Configurable variables
REPO_URL="https://github.com/dashrgame/dashr.git"
INSTALL_DIR="$HOME/dashr"
USER_DATA_DIR="$HOME/dashr-data"
VENV_DIR="$INSTALL_DIR/venv"
LAUNCHER_PATH="/usr/local/bin/dashr"

# Helper functions
confirm() {
  local prompt="$1"
  local var
  read -p "$prompt" var
  # Convert to lowercase and check for various positive responses
  local response=$(echo "$var" | tr '[:upper:]' '[:lower:]')
  [[ "$response" =~ ^(y|yes|yeah|yep|yup|ok|okay|sure|absolutely|definitely).*$ ]]
}


# Check for required tools
for cmd in git python3; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "Error: $cmd is not installed."
    exit 1
  fi
done


# Handle existing installation
if [ -d "$INSTALL_DIR" ]; then
  echo "An existing Dashr installation was found at $INSTALL_DIR."
  echo "Updating installation (user data in $USER_DATA_DIR will be preserved)..."
  rm -rf "$INSTALL_DIR"
  echo "Previous installation removed."
fi

# Create user data directory if it doesn't exist
if [ ! -d "$USER_DATA_DIR" ]; then
  mkdir -p "$USER_DATA_DIR"
  echo "Created user data directory at $USER_DATA_DIR"
else
  echo "User data directory found at $USER_DATA_DIR (will be preserved)"
fi


# Clone repo
git clone "$REPO_URL" "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Create virtualenv or fallback
if python3 -m venv "$VENV_DIR"; then
  source "$VENV_DIR/bin/activate"
  echo "Using virtual environment at $VENV_DIR."
  PIP_CMD="pip"
else
  echo "Warning: Could not create virtual environment."
  if confirm "Do you want to install dependencies using --break-system-packages? (y/N): "; then
    PIP_CMD="python3 -m pip --break-system-packages"
  else
    echo "Aborting installation."
    exit 1
  fi
fi

# Install python dependencies
if [ -f "client/src/requirements.txt" ]; then
  $PIP_CMD install --upgrade pip
  $PIP_CMD install -r client/src/requirements.txt
else
  echo "No requirements.txt found. Skipping dependency installation."
fi


# Create launcher script
echo "Creating launcher at $LAUNCHER_PATH (requires sudo)..."
sudo tee "$LAUNCHER_PATH" > /dev/null <<EOF
#!/bin/bash
cd "$INSTALL_DIR"
if [ -d "$VENV_DIR" ]; then
  source "$VENV_DIR/bin/activate"
fi
exec python3 -m client.src.main "$@"
EOF
sudo chmod +x "$LAUNCHER_PATH"
echo "Launcher script installed to $LAUNCHER_PATH."


# OS-specific setup
OS=$(uname -s)
echo "Detected OS: $OS"

if [[ "$OS" == "Linux" ]]; then
  DESKTOP_FILE="$HOME/.local/share/applications/dashr.desktop"
  DESKTOP_SOURCE="$INSTALL_DIR/client/scripts/resources/dashr.desktop"
  
  mkdir -p "$(dirname "$DESKTOP_FILE")"
  
  if [ -f "$DESKTOP_SOURCE" ]; then
    # Replace placeholder with actual install directory path
    sed "s|__INSTALL_DIR__|$INSTALL_DIR|g" "$DESKTOP_SOURCE" > "$DESKTOP_FILE"
    chmod +x "$DESKTOP_FILE"
    update-desktop-database "$HOME/.local/share/applications" || true
    
    echo "Desktop file copied from $DESKTOP_SOURCE to $DESKTOP_FILE"
    echo "You can now launch Dashr from your application menu."
  else
    echo "Warning: Desktop file not found at $DESKTOP_SOURCE"
  fi
  
  echo "Alternatively, you can run Dashr from any terminal using: dashr"
elif [[ "$OS" == "Darwin" ]]; then
  echo "For macOS, you can run Dashr using the terminal:"
  echo "Just type: dashr"
  echo "Or, if you prefer:"
  echo "1. Open Terminal."
  echo "2. Navigate to the installation directory: cd $INSTALL_DIR"
  if [ -d "$VENV_DIR" ]; then
    echo "3. Activate the virtualenv: source venv/bin/activate"
    echo "4. Run the application: python3 -m client.src.main"
  else
    echo "3. Run the application: python3 -m client.src.main"
  fi
else
  echo "Error: Unsupported OS. Please use Linux or macOS."
  exit 1
fi
