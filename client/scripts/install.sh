#!/bin/bash

# Exit on error
set -e

REPO_URL="https://github.com/dashrgame/dashr.git"
INSTALL_DIR="$HOME/dashr"
PYTHON_VERSION="3.8"

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

# Clone repo
git clone "$REPO_URL" "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Install python dependencies
if [ -f "client/src/requirements.txt" ]; then
  python3 -m pip install --break-system-packages --upgrade pip
  python3 -m pip install --break-system-packages -r client/src/requirements.txt
else
  echo "No requirements.txt found. Skipping dependency installation."
fi

# Check OS
OS=$(uname -s)
echo "Detected OS: $OS"

# OS-specific instructions
if [[ "$OS" == "Linux" ]]; then
  # Install .desktop file for Linux
  DESKTOP_FILE="$HOME/.local/share/applications/dashr.desktop"

  # Create .desktop file directory if it doesn't exist
  mkdir -p "$(dirname "$DESKTOP_FILE")"

  # Create .desktop file
  cat > "$DESKTOP_FILE" <<EOL
[Desktop Entry]
Name=Dashr
Comment=Dashr Client Application
Exec=cd $INSTALL_DIR && python3 -m client.src.main
Icon=$INSTALL_DIR/images/logo.png
Terminal=false
Type=Application
Categories=Game;
EOL

  # Make .desktop file executable
  chmod +x "$DESKTOP_FILE"

  echo "You can now launch Dashr from your application menu."
elif [[ "$OS" == "Darwin" ]]; then
  # Install instructions for macOS
  echo "For macOS, you can run Dashr using the terminal:"
  echo "1. Open Terminal."
  echo "2. Navigate to the installation directory: cd $INSTALL_DIR"
  echo "3. Run the application: python3 -m client.src.main"
  echo "You may want to create an alias or a shortcut for easier access."
else
  echo "Error: Unsupported OS. Please use Linux or macOS."
  exit 1
fi
