#!/usr/bin/env python3
"""
Backend startup script
Adds project root to Python path and starts FastAPI
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
root = Path(__file__).parent
sys.path.insert(0, str(root))

# Load .env file from parent directory
env_path = Path(__file__).parent.parent / ".env"
_ = load_dotenv(dotenv_path=env_path)

# Now import and run
if __name__ == "__main__":
    # Initialize database
    try:
        from src.backend.database.db import init_db

        print("Initializing database...")
        init_db()
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")

    import uvicorn

    uvicorn.run(
        "src.backend.main:app", host="0.0.0.0", port=8001, reload=True, log_level="info"
    )
