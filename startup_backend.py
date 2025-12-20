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

# Load .env file from current directory
env_path = Path(__file__).parent / ".env"
_ = load_dotenv(dotenv_path=env_path)

def run_migrations():
    """Add missing columns to existing tables if needed"""
    import sqlite3
    db_path = Path("data/fitness.db")
    if not db_path.exists():
        return
        
    print(f"🔍 Checking for database migrations...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check users table for role column
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'role' not in columns:
            print("🚀 Adding 'role' column to 'users' table...")
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
            conn.commit()
            print("✅ Migration: Added 'role' column to users.")
            
        conn.close()
    except Exception as e:
        print(f"⚠️  Migration warning: {e}")

# Now import and run
if __name__ == "__main__":
    # Initialize database tables
    try:
        from src.backend.database.db import init_db

        print("Initializing database...")
        init_db()
        
        # Run migrations for existing tables
        run_migrations()
        
        # Auto-promote admin (Update this email with yours)
        ensure_admin("vv083150@gmail.com")
        
    except Exception as e:
        print(f"Warning: Database initialization/migration failed: {e}")

    import uvicorn

    uvicorn.run(
        "src.backend.main:app", host="0.0.0.0", port=8001, reload=True, log_level="info"
    )
