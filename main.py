#!/usr/bin/env python3
"""
Main entry point for AI Trainer Pro
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the glute fly trainer
from exercises.glute_fly import main

if __name__ == "__main__":
    main()


