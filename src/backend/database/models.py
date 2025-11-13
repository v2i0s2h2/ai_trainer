"""
Database Models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from src.backend.database.db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Champion")
    email = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    workouts = relationship("Workout", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")

class Exercise(Base):
    __tablename__ = "exercises"
    
    id = Column(String, primary_key=True)  # e.g., "squat", "push-ups"
    name = Column(String)
    category = Column(String)  # legs, chest, back, etc.
    difficulty = Column(String)  # beginner, intermediate, advanced
    duration_minutes = Column(Integer)
    default_sets = Column(Integer)
    default_reps = Column(Integer)
    description = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    
    # Relationships
    workouts = relationship("Workout", back_populates="exercise")

class Workout(Base):
    __tablename__ = "workouts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exercise_id = Column(String, ForeignKey("exercises.id"))
    date = Column(DateTime, default=datetime.utcnow, index=True)
    duration_seconds = Column(Integer)  # Total workout duration
    reps_completed = Column(Integer)
    calories_burned = Column(Integer)
    
    # Relationships
    user = relationship("User", back_populates="workouts")
    exercise = relationship("Exercise", back_populates="workouts")

class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(String, primary_key=True)  # e.g., "100-reps-club"
    name = Column(String)
    description = Column(String)
    icon = Column(String)  # emoji or icon name
    requirement = Column(String)  # Description of how to unlock
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement")

class UserAchievement(Base):
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    achievement_id = Column(String, ForeignKey("achievements.id"))
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

class DietEntry(Base):
    __tablename__ = "diet_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), default=1)  # Default user for now
    meal_name = Column(String)  # e.g., "Breakfast", "Lunch", "Dinner", "Snack"
    food_item = Column(String)  # e.g., "2 Eggs", "Chicken Breast 200g"
    date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Macronutrients (in grams)
    protein = Column(Float, default=0.0)
    carbs = Column(Float, default=0.0)
    fats = Column(Float, default=0.0)
    calories = Column(Float, default=0.0)
    
    # Micronutrients (optional, in mg or IU)
    omega3 = Column(Float, default=0.0)  # mg
    magnesium = Column(Float, default=0.0)  # mg
    vitamin_b1 = Column(Float, default=0.0)  # mg
    vitamin_d3 = Column(Float, default=0.0)  # IU
    zinc = Column(Float, default=0.0)  # mg
    
    notes = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

