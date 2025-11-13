"""
REST API Routes
Handles exercises, workouts, stats, and user data
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta, date
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.backend.database.db import get_db

router = APIRouter()

# Pydantic models for API requests/responses
class CameraPosition(BaseModel):
    distance: str  # e.g., "2 meters away"
    angle: str  # e.g., "Side view", "Front view", "45° angle"
    height: str  # e.g., "Waist level", "Knee level", "Shoulder level"
    tips: List[str] = []  # Specific tips for camera setup

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
    camera_position: Optional[CameraPosition] = None  # Camera setup instructions

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

# Diet tracking models
class DietEntryCreate(BaseModel):
    meal_name: str
    food_item: str
    protein: float = 0.0
    carbs: float = 0.0
    fats: float = 0.0
    calories: float = 0.0
    omega3: float = 0.0
    magnesium: float = 0.0
    vitamin_b1: float = 0.0
    vitamin_d3: float = 0.0
    zinc: float = 0.0
    notes: Optional[str] = None

class DietEntryResponse(BaseModel):
    id: int
    meal_name: str
    food_item: str
    date: datetime
    protein: float
    carbs: float
    fats: float
    calories: float
    omega3: float
    magnesium: float
    vitamin_b1: float
    vitamin_d3: float
    zinc: float
    notes: Optional[str] = None

class DietStatsResponse(BaseModel):
    date: date
    total_protein: float
    total_carbs: float
    total_fats: float
    total_calories: float
    total_omega3: float
    total_magnesium: float
    total_vitamin_b1: float
    total_vitamin_d3: float
    total_zinc: float
    protein_goal: float  # Based on user's body weight and age
    entries_count: int

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
        "youtube_link": "https://www.youtube.com/watch?v=YaXPRqUwItQ",
        "camera_position": {
            "distance": "2-3 meters away",
            "angle": "Side view (90°)",
            "height": "Waist to hip level",
            "tips": [
                "Place camera on your side to see full body profile",
                "Ensure both feet and head are visible in frame",
                "Keep camera stable (use tripod or prop against wall)",
                "Good lighting helps with pose detection"
            ]
        }
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
        "youtube_link": "https://www.youtube.com/watch?v=IODxDxX7oi4",
        "camera_position": {
            "distance": "1.5-2 meters away",
            "angle": "Side view (90°)",
            "height": "Ground level or slightly elevated",
            "tips": [
                "Place camera on your side to see body alignment",
                "Camera should be at same level as your body (on floor or low surface)",
                "Ensure full body from head to feet is visible",
                "Make sure arms and shoulders are clearly visible"
            ]
        }
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
        "youtube_link": "https://www.youtube.com/watch?v=4Y2ZdHCOXok",
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Side view (90°)",
            "height": "Hip level",
            "tips": [
                "Place camera on your side to see leg movement",
                "Ensure hips and legs are fully visible",
                "Camera should capture full range of leg motion",
                "Keep camera stable for consistent tracking"
            ]
        }
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
        "youtube_link": "https://www.youtube.com/watch?v=qEwKCR5JCog",
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Front view (0°)",
            "height": "Shoulder to chest level",
            "tips": [
                "Place camera directly in front of you",
                "Ensure full upper body is visible (head to waist)",
                "Keep arms and shoulders clearly in frame",
                "Camera should capture full range of arm motion"
            ]
        }
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
        "youtube_link": "https://www.youtube.com/watch?v=ykJmrZ5v0Oo",
        "camera_position": {
            "distance": "1.5-2 meters away",
            "angle": "Front view (0°) or 45° angle",
            "height": "Chest to shoulder level",
            "tips": [
                "Place camera in front of you, slightly to the side if needed",
                "Ensure both arms are fully visible",
                "Camera should capture full range of arm curl motion",
                "Keep elbows in frame for proper form tracking"
            ]
        }
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
        "youtube_link": "https://www.youtube.com/watch?v=pSHjTRCQxIw",
        "camera_position": {
            "distance": "1.5-2 meters away",
            "angle": "Side view (90°)",
            "height": "Ground level or slightly elevated",
            "tips": [
                "Place camera on your side to see body alignment",
                "Camera should be at ground level or slightly above",
                "Ensure full body from head to feet is visible",
                "Check that your body forms a straight line in frame"
            ]
        }
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
        "youtube_link": "https://www.youtube.com/watch?v=rep-qVOkqgk",
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Side view (90°)",
            "height": "Chest to shoulder level",
            "tips": [
                "Place camera on your side to see pulling motion",
                "Ensure full upper body is visible",
                "Camera should capture arm pull-back range",
                "Keep back and shoulders clearly in frame"
            ]
        }
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
        "youtube_link": "https://www.youtube.com/watch?v=eGo4IYlbE5g",
        "camera_position": {
            "distance": "2.5-3 meters away",
            "angle": "Front view (0°)",
            "height": "Chest to head level",
            "tips": [
                "Place camera directly in front of you",
                "Ensure full body from head to feet is visible",
                "Camera should capture full pull-up range (hanging to chin-over-bar)",
                "Keep bar and full arm extension visible"
            ]
        }
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
        "youtube_link": "https://www.youtube.com/watch?v=QOVaHwm-Q6U",
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Side view (90°)",
            "height": "Hip to waist level",
            "tips": [
                "Place camera on your side to see leg movement",
                "Ensure both legs are fully visible in frame",
                "Camera should capture full lunge depth",
                "Keep torso upright and visible"
            ]
        }
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
        "youtube_link": "https://www.youtube.com/watch?v=MKmrqcoCZ-M",
        "camera_position": {
            "distance": "1.5-2 meters away",
            "angle": "Side view (90°)",
            "height": "Ground level or slightly elevated",
            "tips": [
                "Place camera on your side to see torso curl",
                "Camera should be at ground level or slightly above",
                "Ensure upper body and core are visible",
                "Keep head and shoulders in frame for rep counting"
            ]
        }
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
        "youtube_link": "https://www.youtube.com/watch?v=6kALZikXxLc",
        "camera_position": {
            "distance": "1.5-2 meters away",
            "angle": "Side view (90°)",
            "height": "Chest to shoulder level",
            "tips": [
                "Place camera on your side to see arm movement",
                "Ensure full upper body is visible",
                "Camera should capture full dip range (up to down)",
                "Keep elbows and shoulders clearly in frame"
            ]
        }
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
        "youtube_link": "https://www.youtube.com/watch?v=3VcKaXpzqRo",
        "camera_position": {
            "distance": "1.5-2 meters away",
            "angle": "Front view (0°)",
            "height": "Shoulder to chest level",
            "tips": [
                "Place camera directly in front of you",
                "Ensure both arms are fully visible",
                "Camera should capture full arm raise range (down to shoulder height)",
                "Keep shoulders and arms clearly in frame"
            ]
        }
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

@router.post("/diet/entries", response_model=DietEntryResponse)
async def create_diet_entry(entry: DietEntryCreate, db: Session = Depends(get_db)):
    """Add a new diet entry"""
    from src.backend.database.models import DietEntry
    
    db_entry = DietEntry(
        meal_name=entry.meal_name,
        food_item=entry.food_item,
        protein=entry.protein,
        carbs=entry.carbs,
        fats=entry.fats,
        calories=entry.calories,
        omega3=entry.omega3,
        magnesium=entry.magnesium,
        vitamin_b1=entry.vitamin_b1,
        vitamin_d3=entry.vitamin_d3,
        zinc=entry.zinc,
        notes=entry.notes,
        date=datetime.utcnow()
    )
    
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    return db_entry

@router.get("/diet/entries", response_model=List[DietEntryResponse])
async def get_diet_entries(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get diet entries for a date range (defaults to today)"""
    from src.backend.database.models import DietEntry
    
    query = db.query(DietEntry)
    
    if start_date:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        query = query.filter(DietEntry.date >= start)
    
    if end_date:
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        query = query.filter(DietEntry.date <= end)
    
    if not start_date and not end_date:
        # Default to today
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_end = datetime.combine(date.today(), datetime.max.time())
        query = query.filter(DietEntry.date >= today_start, DietEntry.date <= today_end)
    
    entries = query.order_by(DietEntry.date.desc()).all()
    return entries

@router.get("/diet/stats", response_model=DietStatsResponse)
async def get_diet_stats(
    target_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get daily nutrition statistics"""
    from src.backend.database.models import DietEntry
    
    if target_date:
        target = datetime.fromisoformat(target_date.replace('Z', '+00:00')).date()
    else:
        target = date.today()
    
    start = datetime.combine(target, datetime.min.time())
    end = datetime.combine(target, datetime.max.time())
    
    entries = db.query(DietEntry).filter(
        DietEntry.date >= start,
        DietEntry.date <= end
    ).all()
    
    # Calculate totals
    stats = {
        "date": target,
        "total_protein": sum(e.protein for e in entries),
        "total_carbs": sum(e.carbs for e in entries),
        "total_fats": sum(e.fats for e in entries),
        "total_calories": sum(e.calories for e in entries),
        "total_omega3": sum(e.omega3 for e in entries),
        "total_magnesium": sum(e.magnesium for e in entries),
        "total_vitamin_b1": sum(e.vitamin_b1 for e in entries),
        "total_vitamin_d3": sum(e.vitamin_d3 for e in entries),
        "total_zinc": sum(e.zinc for e in entries),
        "entries_count": len(entries)
    }
    
    # Calculate protein goal (default: 1.8g per kg, assuming 70kg = 126g)
    # In future, this can be based on user profile (age, weight)
    stats["protein_goal"] = 126.0  # 70kg * 1.8g/kg
    
    return stats

@router.delete("/diet/entries/{entry_id}")
async def delete_diet_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delete a diet entry"""
    from src.backend.database.models import DietEntry
    
    entry = db.query(DietEntry).filter(DietEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Diet entry not found")
    
    db.delete(entry)
    db.commit()
    
    return {"message": "Diet entry deleted successfully"}

