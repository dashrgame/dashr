#!/bin/bash

# Configurable variables
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

# Check if Dashr is installed
if [ ! -d "$INSTALL_DIR" ] && [ ! -d "$USER_DATA_DIR" ]; then
  echo "Dashr is not installed."
  echo "Nothing to uninstall."
  exit 0
fi

if [ -d "$INSTALL_DIR" ]; then
  echo "Dashr installation found at $INSTALL_DIR."
fi

if [ -d "$USER_DATA_DIR" ]; then
  echo "Dashr user data found at $USER_DATA_DIR."
fi

echo ""
echo "This will remove:"
echo "- Game installation (at $INSTALL_DIR)"
echo "- Launcher script and desktop integration"
echo ""
echo "User data at $USER_DATA_DIR will be handled separately."

if ! confirm "Are you sure you want to uninstall Dashr? (y/N): "; then
  echo "Uninstallation cancelled."
  exit 0
fi

# Handle user data separately
REMOVE_USER_DATA=false

if [ -d "$USER_DATA_DIR" ] && [ "$(ls -A "$USER_DATA_DIR" 2>/dev/null)" ]; then
  echo ""
  echo "Found user data at $USER_DATA_DIR"
  echo "This includes your settings, local levels (not online ones), and locally saved data."
  
  if confirm "Do you want to REMOVE user data as well? (y/N): "; then
    REMOVE_USER_DATA=true
  else
    echo "User data will be preserved at $USER_DATA_DIR"
  fi
fi

echo ""
echo "Uninstalling Dashr..."

# Remove main installation directory
if [ -d "$INSTALL_DIR" ]; then
  echo "Removing installation directory..."
  rm -rf "$INSTALL_DIR"
  echo "Installation directory removed."
fi

# Remove user data if requested
if [ "$REMOVE_USER_DATA" = true ] && [ -d "$USER_DATA_DIR" ]; then
  echo "Removing user data directory..."
  rm -rf "$USER_DATA_DIR"
  echo "User data directory removed."
fi

# Remove launcher script
if [ -f "$LAUNCHER_PATH" ]; then
  echo "Removing launcher script (requires sudo)..."
  if command -v sudo &> /dev/null; then
    sudo rm -f "$LAUNCHER_PATH"
    echo "Launcher script removed."
  else
    echo "Warning: sudo not available. Please manually remove: $LAUNCHER_PATH"
  fi
else
  echo "Launcher script not found (already removed or not installed)."
fi

# Remove desktop file (Linux only)
OS=$(uname -s)
if [[ "$OS" == "Linux" ]]; then
  DESKTOP_FILE="$HOME/.local/share/applications/dashr.desktop"
  if [ -f "$DESKTOP_FILE" ]; then
    rm -f "$DESKTOP_FILE"
    update-desktop-database "$HOME/.local/share/applications" || true
    
    echo "Desktop file removed."
  else
    echo "Desktop file not found (already removed or not installed)."
  fi
  
  # Update desktop database if available
  if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
  fi
fi

echo ""
echo "Dashr has been uninstalled!"

if [ "$REMOVE_USER_DATA" = false ] && [ -d "$USER_DATA_DIR" ]; then
  echo ""
  echo "Your user data is preserved at: $USER_DATA_DIR"
  echo "If you reinstall Dashr, your settings and levels will be available."
fi

echo ""
echo "If you want to reinstall Dashr in the future, you can run the install script again."

# Final cleanup check
REMAINING_FILES=()
if [ -d "$INSTALL_DIR" ]; then
  REMAINING_FILES+=("Installation directory: $INSTALL_DIR")
fi
if [ -f "$LAUNCHER_PATH" ]; then
  REMAINING_FILES+=("Launcher script: $LAUNCHER_PATH")
fi

if [ ${#REMAINING_FILES[@]} -gt 0 ]; then
  echo ""
  echo "Warning: Some files may still remain. Please check manually:"
  for file in "${REMAINING_FILES[@]}"; do
    echo "- $file"
  done
fi
