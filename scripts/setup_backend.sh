#!/bin/bash

# --- Helper Functions ---
log_info() {
    echo "[INFO] $1"
}

log_success() {
    echo "[SUCCESS] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
    exit 1
}

log_warning() {
    echo "[WARNING] $1"
}

# Exit immediately if a command exits with a non-zero status.
set -e

# 1. Check for Python 3.10+
log_info "Checking for Python 3.10..."
PYTHON_EXEC=""
if command -v python3.10 &>/dev/null; then
    PYTHON_EXEC="python3.10"
elif command -v python3 &>/dev/null && python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
    PYTHON_EXEC="python3"
else
    log_error "Python 3.10 or higher is not installed or not in PATH. Please install it to continue."
fi
log_success "$($PYTHON_EXEC -V) found."

# 2. Check for requirements.txt
log_info "Looking for requirements.txt..."
if [ ! -f "requirements.txt" ]; then
    log_error "'requirements.txt' not found in the current directory. Cannot proceed."
fi
log_success "requirements.txt found."

# 3. Create or Re-use Virtual Environment
VENV_DIR=".venv"
if [ -d "$VENV_DIR" ]; then
    print_warning "Virtual environment './$VENV_DIR' already exists."
    print_info "If you have issues, remove it and run this script again: rm -rf $VENV_DIR"
else
    log_info "Creating Python virtual environment in './$VENV_DIR'..."
    $PYTHON_EXEC -m venv $VENV_DIR
    print_success "Virtual environment created."
fi

# 4. Activate Virtual Environment and Install Dependencies
log_info "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

log_info "Upgrading pip..."
pip install --upgrade pip > /dev/null

log_info "Installing dependencies from requirements.txt... (This may take a while)"
pip install -r requirements.txt

print_success "Setup complete! All dependencies are installed in the virtual environment."
print_info "To activate the virtual environment in your current shell, run:"
echo -e "\nsource $VENV_DIR/bin/activate\n"
