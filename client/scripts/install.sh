#!/bin/bash

set -e

REPO_URL="https://github.com/dashrgame/dashr.git"
INSTALL_DIR="$HOME/dashr"
PYTHON_VERSION="3.8"
VENV_DIR="$INSTALL_DIR/venv"
LAUNCHER_PATH="/usr/local/bin/dashr"

# Check for git
if ! command -v git &> /dev/null; then
  echo "Error: git is not installed."
  exit 1
fi

# Check for python
if ! command -v python3 &> /dev/null; then
  echo "Error: python3 is not installed."
  exit 1
fi

PY_VER=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ "$(printf '%s\n' "$PY_VER" "$PYTHON_VERSION" | sort -V | head -n1)" != "$PYTHON_VERSION" ]]; then
  echo "Warning: Python $PYTHON_VERSION or above is recommended, but $PY_VER is installed."
fi

# Check for existing installation
if [ -d "$INSTALL_DIR" ]; then
  echo "An existing Dashr installation was found at $INSTALL_DIR."
  echo "WARNING: Reinstalling will DELETE ALL SETTINGS and ALL LOCAL LEVELS."
  read -p "Are you sure you want to DELETE and REINSTALL Dashr? (y/N): " CONFIRM1
  if [[ ! "$CONFIRM1" =~ ^[Yy]$ ]]; then
    echo "Aborting installation."
    exit 1
  fi
  echo "This action is IRREVERSIBLE. ALL LOCAL DATA WILL BE LOST."
  read -p "Please type 'DELETE' to confirm: " CONFIRM2
  if [[ "$CONFIRM2" != "DELETE" ]]; then
    echo "Aborting installation."
    exit 1
  fi
  rm -rf "$INSTALL_DIR"
  echo "Previous installation deleted."
fi

# Clone repo
git clone "$REPO_URL" "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Try to create virtualenv
if python3 -m venv "$VENV_DIR"; then
  source "$VENV_DIR/bin/activate"
  echo "Using virtual environment at $VENV_DIR."
  PIP_CMD="pip"
else
  echo "Warning: Could not create virtual environment."
  read -p "Do you want to install dependencies using --break-system-packages? (y/N): " CONFIRM
  if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
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
exec python3 -m client.src.main "\$@"
EOF
sudo chmod +x "$LAUNCHER_PATH"
echo "Launcher script installed to $LAUNCHER_PATH."

# Check OS
OS=$(uname -s)
echo "Detected OS: $OS"

if [[ "$OS" == "Linux" ]]; then
  DESKTOP_FILE="$HOME/.local/share/applications/dashr.desktop"
  mkdir -p "$(dirname "$DESKTOP_FILE")"
  cat > "$DESKTOP_FILE" <<EOL
[Desktop Entry]
Name=Dashr
Comment=Dashr Client Application
Exec=dashr
Icon=$INSTALL_DIR/images/logo.png
Terminal=false
Type=Application
Categories=Game;
EOL
  chmod +x "$DESKTOP_FILE"
  echo "You can now launch Dashr from your application menu."
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
  echo "You may want to create an alias or a shortcut for easier access."
else
  echo "Error: Unsupported OS. Please use Linux or macOS."
  exit 1
fi
