from datetime import datetime, timedelta
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from src.backend.auth.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from src.backend.database.db import get_db
from src.backend.database.models import User

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


# Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = "Champion"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict  # Basic user info to return with token


class GoogleLogin(BaseModel):
    credential: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str

    class Config:
        from_attributes = True


class AdminUserResponse(BaseModel):
    id: int
    email: Optional[str]
    name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


# Routes
@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email, name=user_in.name, hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(new_user.id)}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role,
        },
    }


@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not user.hashed_password:
        # If user exists but has no password (legacy/guest user), we might want to handle differently,
        # but for now, deny login.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }


@router.post("/google", response_model=Token)
def google_login(login_data: GoogleLogin, db: Session = Depends(get_db)):
    """Verify Google ID token and login/register user"""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google Client ID not configured on server",
        )

    try:
        # Verify the ID token
        idinfo = id_token.verify_oauth2_token(
            login_data.credential, google_requests.Request(), GOOGLE_CLIENT_ID
        )

        # ID token is valid. Get user's Google ID and email.
        google_id = idinfo["sub"]
        email = idinfo.get("email")
        name = idinfo.get("name", "Champion")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google",
            )

        # 1. Try to find user by google_id
        user = db.query(User).filter(User.google_id == google_id).first()

        if not user:
            # 2. Try to find user by email (account linking)
            user = db.query(User).filter(User.email == email).first()

            if user:
                # Link account
                user.google_id = google_id
                if not user.name or user.name == "Champion":
                    user.name = name
            else:
                # 3. Create new user with auto-admin promotion for specific email
                role = "admin" if email == "vv083150@gmail.com" else "user"
                user = User(
                    email=email,
                    name=name,
                    google_id=google_id,
                    role=role,
                )
                db.add(user)

            db.commit()
            db.refresh(user)

        # Hardcoded admin promotion for existing Google user (fail-safe)
        if user.email == "vv083150@gmail.com" and user.role != "admin":
            user.role = "admin"
            db.commit()
            db.refresh(user)

        # Generate token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
            },
        }

    except ValueError:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google login failed: {str(e)}",
        )


# Dependency
security = HTTPBearer()


def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token.credentials)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        user_id_int = int(user_id)
    except ValueError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id_int).first()
    if user is None:
        raise credentials_exception

    return user


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user data including role"""
    return current_user


@router.get("/admin/users", response_model=List[AdminUserResponse])
def get_all_users(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Admin only: Get list of all registered users"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )

    users = db.query(User).all()
    return users
