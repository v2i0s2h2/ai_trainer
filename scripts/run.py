#!/usr/bin/env python3
"""
Run script for AI Trainer Pro
"""
import os
import sys
import subprocess

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    # Path to main.py
    main_path = os.path.join(parent_dir, 'main.py')
    
    # Check if file exists
    if not os.path.exists(main_path):
        print(f"Error: {main_path} not found!")
        return
    
    # Path to virtual environment
    venv_python = os.path.join(parent_dir, '.venv', 'Scripts', 'python.exe')
    
    # Check if virtual environment exists
    if not os.path.exists(venv_python):
        print(f"Error: Virtual environment not found at {venv_python}")
        print("Please run: python -m venv .venv")
        return
    
    print("Starting AI Trainer Pro...")
    print(f"Working directory: {parent_dir}")
    print(f"Python: {venv_python}")
    print(f"Main: {main_path}")
    print("-" * 50)
    
    try:
        # Run the trainer
        subprocess.run([venv_python, main_path], cwd=parent_dir)
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error running trainer: {e}")

if __name__ == "__main__":
    main()


