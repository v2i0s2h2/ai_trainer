
#!/bin/bash

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating..."
    # Try to use Python 3.10 if available
    if command -v python3.10 &> /dev/null; then
        echo "Using Python 3.10"
        python3.10 -m venv .venv
    else
        echo "Python 3.10 not found. Using default Python. Consider installing Python 3.10 via pyenv."
        python3 -m venv .venv
    fi
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if not already installed
echo "Checking dependencies..."
pip install --quiet opencv-python mediapipe numpy gtts pygame tensorflow pandas scikit-learn joblib 2>/dev/null || pip install -r requirements.txt

# Run the trainer
python glute_fly_trainer.py