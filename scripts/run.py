
#!/bin/bash

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Running setup..."
    # Always use system Python to run the setup which enforces Python 3.10 for the venv
    python scripts/setup_venv.py || {
        echo "Failed to set up virtual environment."
        exit 1
    }
fi

# Activate virtual environment
source .venv/bin/activate

# Ensure dependencies are installed/updated
if [ -f "src/backend/requirements.txt" ]; then
    echo "Ensuring dependencies from requirements.txt..."
    pip install -r src/backend/requirements.txt
fi

# Which trainer to run (default glute fly enhanced)
MODE=${1:-glute}

if [ "$MODE" = "squat" ]; then
    python -m src.exercises.squat_trainer
    exit $?
fi

# Run the trainer (prefer non-enhanced if present; fallback to enhanced)
if [ -f "glute_fly_trainer.py" ]; then
    python glute_fly_trainer.py
elif [ -f "glute_fly_trainer_enhanced.py" ]; then
    python glute_fly_trainer_enhanced.py
else
    echo "No trainer script found (glute_fly_trainer.py or glute_fly_trainer_enhanced.py)."
    exit 1
fi