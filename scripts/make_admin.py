#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add project root to sys.path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from sqlalchemy.orm import Session
from src.backend.database.db import SessionLocal
from src.backend.database.models import User

def make_admin(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Error: User with email '{email}' not found.")
            return

        user.role = "admin"
        db.commit()
        print(f"Success: User '{email}' is now an admin (role: {user.role}).")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/make_admin.py <email>")
    else:
        make_admin(sys.argv[1])
