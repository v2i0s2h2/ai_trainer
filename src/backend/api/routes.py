"""
REST API Routes
Handles exercises, workouts, stats, and user data
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.orm import Session

router = APIRouter()

# Pydantic models for API requests/responses
class ExerciseResponse(BaseModel):
    id: str
    name: str
    category: str
    difficulty: str
    duration: int  # minutes
    sets: int
    reps: int
    thumbnail: Optional[str] = None
    description: Optional[str] = None
    target_muscles: List[str] = []  # Target muscles for this exercise
    youtube_link: Optional[str] = None  # YouTube tutorial video link

class TodayStatsResponse(BaseModel):
    reps_today: int
    streak: int
    calories: int

class WorkoutCreate(BaseModel):
    exercise_id: str
    duration: int  # seconds
    reps_completed: int
    calories_burned: int

class WorkoutResponse(BaseModel):
    id: int
    exercise_name: str
    date: datetime
    duration: int
    reps: int
    calories: int

# Mock data for now (will replace with database)
EXERCISES = [
    {
        "id": "squat",
        "name": "Squats",
        "category": "legs",
        "difficulty": "beginner",
        "duration": 12,
        "sets": 4,
        "reps": 15,
        "thumbnail": "/images/exercises/squat.jpg",
        "description": "Basic squat exercise for legs",
        "target_muscles": ["Quadriceps", "Glutes", "Hamstrings", "Calves"],
        "youtube_link": "https://www.youtube.com/watch?v=YaXPRqUwItQ"
    },
    {
        "id": "push-ups",
        "name": "Push-ups",
        "category": "chest",
        "difficulty": "beginner",
        "duration": 10,
        "sets": 3,
        "reps": 12,
        "thumbnail": "/images/exercises/pushup.jpg",
        "description": "Classic push-up for chest and arms",
        "target_muscles": ["Pectorals", "Triceps", "Anterior Deltoids", "Core"],
        "youtube_link": "https://www.youtube.com/watch?v=IODxDxX7oi4"
    },
    {
        "id": "glute-fly",
        "name": "Glute Fly",
        "category": "legs",
        "difficulty": "intermediate",
        "duration": 15,
        "sets": 3,
        "reps": 10,
        "thumbnail": "/images/exercises/glute-fly.jpg",
        "description": "Glute fly exercise for hip mobility",
        "target_muscles": ["Glutes", "Hamstrings", "Hip Abductors"],
        "youtube_link": "https://www.youtube.com/watch?v=4Y2ZdHCOXok"
    },
    {
        "id": "shoulder-press",
        "name": "Shoulder Press",
        "category": "shoulders",
        "difficulty": "beginner",
        "duration": 10,
        "sets": 3,
        "reps": 12,
        "thumbnail": "/images/exercises/shoulder-press.jpg",
        "description": "Shoulder press for shoulder strength",
        "target_muscles": ["Anterior Deltoids", "Lateral Deltoids", "Triceps", "Upper Trapezius"],
        "youtube_link": "https://www.youtube.com/watch?v=qEwKCR5JCog"
    },
    {
        "id": "bicep-curl",
        "name": "Bicep Curls",
        "category": "arms",
        "difficulty": "beginner",
        "duration": 8,
        "sets": 3,
        "reps": 15,
        "thumbnail": "/images/exercises/bicep-curl.jpg",
        "description": "Bicep curls for arm strength",
        "target_muscles": ["Biceps Brachii", "Brachialis", "Brachioradialis"],
        "youtube_link": "https://www.youtube.com/watch?v=ykJmrZ5v0Oo"
    },
    {
        "id": "plank",
        "name": "Plank",
        "category": "core",
        "difficulty": "intermediate",
        "duration": 5,
        "sets": 3,
        "reps": 1,
        "thumbnail": "/images/exercises/plank.jpg",
        "description": "Plank hold for core strength",
        "target_muscles": ["Rectus Abdominis", "Transverse Abdominis", "Obliques", "Erector Spinae"],
        "youtube_link": "https://www.youtube.com/watch?v=pSHjTRCQxIw"
    },
    {
        "id": "row",
        "name": "Rows",
        "category": "back",
        "difficulty": "beginner",
        "duration": 10,
        "sets": 3,
        "reps": 12,
        "thumbnail": "/images/exercises/row.jpg",
        "description": "Row exercise for back strength",
        "target_muscles": ["Latissimus Dorsi", "Rhomboids", "Middle Trapezius", "Rear Deltoids", "Biceps"],
        "youtube_link": "https://www.youtube.com/watch?v=rep-qVOkqgk"
    },
    {
        "id": "pull-up",
        "name": "Pull-ups",
        "category": "back",
        "difficulty": "advanced",
        "duration": 8,
        "sets": 3,
        "reps": 8,
        "thumbnail": "/images/exercises/pullup.jpg",
        "description": "Pull-ups for upper body strength",
        "target_muscles": ["Latissimus Dorsi", "Rhomboids", "Biceps", "Rear Deltoids", "Teres Major"],
        "youtube_link": "https://www.youtube.com/watch?v=eGo4IYlbE5g"
    },
    {
        "id": "lunge",
        "name": "Lunges",
        "category": "legs",
        "difficulty": "beginner",
        "duration": 10,
        "sets": 3,
        "reps": 12,
        "thumbnail": "/images/exercises/lunge.jpg",
        "description": "Lunges for leg strength",
        "target_muscles": ["Quadriceps", "Glutes", "Hamstrings", "Calves"],
        "youtube_link": "https://www.youtube.com/watch?v=QOVaHwm-Q6U"
    },
    {
        "id": "crunch",
        "name": "Crunches",
        "category": "core",
        "difficulty": "beginner",
        "duration": 8,
        "sets": 3,
        "reps": 15,
        "thumbnail": "/images/exercises/crunch.jpg",
        "description": "Crunches for core strength",
        "target_muscles": ["Rectus Abdominis", "Obliques"],
        "youtube_link": "https://www.youtube.com/watch?v=MKmrqcoCZ-M"
    },
    {
        "id": "tricep-dip",
        "name": "Tricep Dips",
        "category": "arms",
        "difficulty": "intermediate",
        "duration": 8,
        "sets": 3,
        "reps": 10,
        "thumbnail": "/images/exercises/tricep-dip.jpg",
        "description": "Tricep dips for arm strength",
        "target_muscles": ["Triceps", "Anterior Deltoids", "Pectorals"],
        "youtube_link": "https://www.youtube.com/watch?v=6kALZikXxLc"
    },
    {
        "id": "lateral-raise",
        "name": "Lateral Raises",
        "category": "shoulders",
        "difficulty": "beginner",
        "duration": 8,
        "sets": 3,
        "reps": 12,
        "thumbnail": "/images/exercises/lateral-raise.jpg",
        "description": "Lateral raises for shoulder strength",
        "target_muscles": ["Lateral Deltoids", "Anterior Deltoids", "Supraspinatus"],
        "youtube_link": "https://www.youtube.com/watch?v=3VcKaXpzqRo"
    }
]

@router.get("/exercises", response_model=List[ExerciseResponse])
async def get_exercises(category: Optional[str] = None, difficulty: Optional[str] = None):
    """Get list of all exercises with optional filters"""
    exercises = EXERCISES.copy()
    
    if category:
        exercises = [e for e in exercises if e["category"] == category]
    
    if difficulty:
        exercises = [e for e in exercises if e["difficulty"] == difficulty]
    
    return exercises

@router.get("/exercises/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(exercise_id: str):
    """Get details of a specific exercise"""
    exercise = next((e for e in EXERCISES if e["id"] == exercise_id), None)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise

@router.get("/cameras")
async def get_cameras():
    """Get list of available camera devices"""
    from src.backend.core.camera_utils import list_cameras
    cameras = list_cameras()
    return {"cameras": cameras}

@router.get("/stats/today", response_model=TodayStatsResponse)
async def get_today_stats():
    """Get today's workout statistics"""
    # Mock data - will replace with database query
    return {
        "reps_today": 247,
        "streak": 12,
        "calories": 1245
    }

@router.get("/stats/weekly")
async def get_weekly_stats():
    """Get weekly workout statistics"""
    # Mock data
    return {
        "reps_per_day": [120, 145, 95, 165, 185, 200, 155],
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "total_reps": 1065,
        "total_calories": 4050,
        "workouts_completed": 7
    }

@router.post("/workouts", response_model=dict)
async def save_workout(workout: WorkoutCreate):
    """Save a completed workout"""
    # Will implement database save later
    return {
        "success": True,
        "workout_id": 123,
        "message": "Workout saved successfully"
    }

@router.get("/workouts/history", response_model=List[WorkoutResponse])
async def get_workout_history(limit: int = 10):
    """Get workout history"""
    # Mock data
    return [
        {
            "id": 1,
            "exercise_name": "Squats",
            "date": datetime.now() - timedelta(days=1),
            "duration": 720,
            "reps": 67,
            "calories": 180
        }
    ]

@router.get("/achievements")
async def get_achievements():
    """Get user achievements"""
    return {
        "unlocked": [
            {
                "id": "100-reps",
                "name": "100 Reps Club",
                "icon": "💪",
                "date": "Oct 10"
            },
            {
                "id": "7-day-streak",
                "name": "7-Day Streak",
                "icon": "🔥",
                "date": "Oct 12"
            },
            {
                "id": "early-bird",
                "name": "Early Bird",
                "icon": "🌅",
                "date": "Oct 8"
            }
        ],
        "locked": [
            {
                "id": "14-day-streak",
                "name": "14-Day Streak",
                "icon": "🔥",
                "requirement": "Maintain 14-day workout streak"
            }
        ],
        "total": 6,
        "unlocked_count": 3
    }

