#!/bin/bash
# Python 3.10 Setup Script
# Yeh script Python 3.10 install karega aur virtual environment setup karega

echo "=== Python 3.10 Setup Script ==="
echo ""

# Method 1: Try pyenv
if command -v pyenv &> /dev/null; then
    echo "✓ pyenv found. Installing Python 3.10.19..."
    pyenv install 3.10.19
    pyenv local 3.10.19
    python -m venv .venv
    echo "✓ Virtual environment created with Python 3.10.19"
else
    echo "pyenv not found. Checking for python310..."
    
    # Method 2: Check if python310 is already installed
    if command -v python3.10 &> /dev/null; then
        echo "✓ python3.10 found!"
        python3.10 -m venv .venv
        echo "✓ Virtual environment created"
    else
        echo "❌ python3.10 not found"
        echo ""
        echo "Please install Python 3.10 using ONE of these methods:"
        echo ""
        echo "Method 1: Install via yay (AUR helper)"
        echo "  yay -S python310-bin"
        echo ""
        echo "Method 2: Install pyenv"
        echo "  sudo pacman -S pyenv-bin"
        echo "  pyenv install 3.10.13"
        echo ""
        echo "Method 3: Use conda/miniconda"
        echo "  conda create -n ai_trainer python=3.10"
        echo ""
        exit 1
    fi
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✓ Setup complete! Run ./scripts/run.py to start"

