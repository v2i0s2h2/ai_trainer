#!/bin/bash

# --- Helper Functions for Colored Output ---
print_info() {
    echo -e "\e[34m\e[1m[INFO]\e[0m $1"
}

print_success() {
    echo -e "\e[32m\e[1m[SUCCESS]\e[0m $1"
}

print_error() {
    echo -e "\e[31m\e[1m[ERROR]\e[0m $1" >&2
}

print_warning() {
    echo -e "\e[33m\e[1m[WARNING]\e[0m $1"
}

# Exit immediately if a command exits with a non-zero status.
set -e

# 1. Check for Python 3.10
print_info "Checking for Python 3.10..."
if ! command -v python3.10 &> /dev/null; then
    print_error "Python 3.10 is not installed. Please install it to proceed."
    exit 1
fi

# Check if the default python3 is 3.10
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info[:2] == (3, 10) else 1)'; then
    PYTHON_VERSION=$(python3 --version 2>&1 | head -n 1)
    print_error "Default Python version is not 3.10. You are using ${PYTHON_VERSION}. Please use 'update-alternatives' or similar to set python3 to python3.10."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
print_success "Python 3.10 found: $PYTHON_VERSION"

# 2. Check for requirements.txt
print_info "Looking for requirements.txt..."
if [ ! -f "requirements.txt" ]; then
    print_error "'requirements.txt' not found in the current directory. Cannot proceed."
    exit 1
fi
print_success "requirements.txt found."

# 3. Create or Re-use Virtual Environment
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    print_info "Creating Python virtual environment in './$VENV_DIR' with python3.10..."
    python3.10 -m venv $VENV_DIR
    print_success "Virtual environment created."
else
    print_info "Virtual environment './$VENV_DIR' already exists. Re-using it."
fi

# 4. Activate Virtual Environment and Install Dependencies
print_info "Activating virtual environment..."
source $VENV_DIR/bin/activate

print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null

print_info "Installing dependencies from requirements.txt... (This may take a while)"
pip install -r requirements.txt

print_success "Setup complete! All dependencies are installed in the virtual environment."
print_info "To activate the virtual environment in your current shell, run:"
echo -e "\nsource $VENV_DIR/bin/activate\n"
