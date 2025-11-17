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
    exercise_type: str  # "rehab", "basic", "advanced", "lifting"
    category: str  # "upper" or "lower" (body part classification)
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
    calories_burned: int = 0  # Not used, kept for backward compatibility

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

# User Profile Models
class UserStats(BaseModel):
    total_workouts: int
    current_streak: int
    days_active: int
    total_reps: int
    total_muscle_gain: float  # Estimated: total_reps * 0.06

class UserPreferences(BaseModel):
    notifications_enabled: bool = True
    units: str = "metric"  # "metric" or "imperial"
    language: str = "en"

class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    stats: UserStats
    preferences: UserPreferences
    created_at: datetime

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    preferences: Optional[UserPreferences] = None

# Mock data for now (will replace with database)
EXERCISES = [
    {
        "id": "squat",
        "name": "Squats",
        "exercise_type": "basic",
        "category": "lower",
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
        "exercise_type": "basic",
        "category": "upper",
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
        "exercise_type": "rehab",
        "category": "lower",
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
        "exercise_type": "basic",
        "category": "upper",
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
        "exercise_type": "basic",
        "category": "upper",
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
        "exercise_type": "basic",
        "category": "lower",
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
        "exercise_type": "basic",
        "category": "upper",
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
        "exercise_type": "basic",
        "category": "upper",
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
        "exercise_type": "basic",
        "category": "lower",
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
        "exercise_type": "basic",
        "category": "upper",
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
        "exercise_type": "basic",
        "category": "upper",
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
        "exercise_type": "basic",
        "category": "upper",
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
async def get_today_stats(db: Session = Depends(get_db)):
    """Get today's workout statistics"""
    from src.backend.database.models import Workout
    from datetime import datetime, timedelta, date
    
    # Get today's date
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Query today's workouts
    today_workouts = db.query(Workout).filter(
        Workout.user_id == 1,
        Workout.date >= today_start,
        Workout.date <= today_end
    ).all()
    
    # Calculate reps today
    reps_today = sum(w.reps_completed for w in today_workouts) if today_workouts else 0
    
    # Calculate streak (reuse logic from profile endpoint)
    all_workouts = db.query(Workout).filter(Workout.user_id == 1).all()
    current_streak = 0
    
    if all_workouts:
        # Sort workouts by date (most recent first)
        sorted_workouts = sorted(all_workouts, key=lambda w: w.date, reverse=True)
        check_date = today
        
        for workout in sorted_workouts:
            workout_date = workout.date.date() if hasattr(workout.date, 'date') else workout.date
            if workout_date == check_date or workout_date == check_date - timedelta(days=1):
                if workout_date == check_date:
                    # Same day workout, continue
                    pass
                else:
                    # Previous day workout, increment streak
                    current_streak += 1
                    check_date = workout_date
            else:
                # Gap found, break streak
                break
        
        # If most recent workout is today, add 1 to streak
        most_recent_date = sorted_workouts[0].date.date() if hasattr(sorted_workouts[0].date, 'date') else sorted_workouts[0].date
        if most_recent_date == today:
            current_streak += 1
    
    return {
        "reps_today": reps_today,
        "streak": current_streak,
        "calories": 0  # Not used, set to 0
    }

@router.get("/stats/weekly")
async def get_weekly_stats(db: Session = Depends(get_db)):
    """Get weekly workout statistics for last 7 days (Mon-Sun)"""
    from src.backend.database.models import Workout
    from datetime import datetime, timedelta, date
    
    # Get today and calculate start of week (Monday)
    today = datetime.now().date()
    # Get Monday of current week
    days_since_monday = today.weekday()  # 0 = Monday, 6 = Sunday
    monday = today - timedelta(days=days_since_monday)
    
    # Calculate date range (Monday to Sunday)
    week_start = datetime.combine(monday, datetime.min.time())
    week_end = datetime.combine(monday + timedelta(days=6), datetime.max.time())
    
    # Query workouts for this week
    week_workouts = db.query(Workout).filter(
        Workout.user_id == 1,
        Workout.date >= week_start,
        Workout.date <= week_end
    ).all()
    
    # Initialize reps per day array (Mon=0, Sun=6)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    reps_per_day = [0] * 7
    
    # Group workouts by day and sum reps
    for workout in week_workouts:
        workout_date = workout.date.date() if hasattr(workout.date, 'date') else workout.date
        day_index = (workout_date - monday).days
        if 0 <= day_index < 7:
            reps_per_day[day_index] += workout.reps_completed
    
    # Calculate totals
    total_reps = sum(reps_per_day)
    workouts_completed = len(week_workouts)
    
    return {
        "reps_per_day": reps_per_day,
        "days": days,
        "total_reps": total_reps,
        "total_calories": 0,  # Not used, set to 0
        "workouts_completed": workouts_completed
    }

@router.post("/workouts", response_model=dict)
async def save_workout(workout: WorkoutCreate, db: Session = Depends(get_db)):
    """Save a completed workout to database"""
    from src.backend.database.models import Workout, User
    
    # Get or create default user (user_id=1)
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        user = User(id=1, name="Champion", email=None)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create workout record
    db_workout = Workout(
        user_id=user.id,
        exercise_id=workout.exercise_id,
        date=datetime.utcnow(),
        duration_seconds=workout.duration,
        reps_completed=workout.reps_completed,
        calories_burned=0  # Not used, set to 0
    )
    
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    
    return {
        "success": True,
        "workout_id": db_workout.id,
        "message": "Workout saved successfully"
    }

@router.get("/workouts/history", response_model=List[WorkoutResponse])
async def get_workout_history(limit: int = 10, db: Session = Depends(get_db)):
    """Get workout history - list of past workouts user completed"""
    from src.backend.database.models import Workout, Exercise
    
    # Query workouts with exercise details
    workouts = db.query(Workout, Exercise).join(
        Exercise, Workout.exercise_id == Exercise.id
    ).filter(
        Workout.user_id == 1  # Default user for now
    ).order_by(
        Workout.date.desc()
    ).limit(limit).all()
    
    # Format response
    history = []
    for workout, exercise in workouts:
        history.append({
            "id": workout.id,
            "exercise_name": exercise.name,
            "date": workout.date,
            "duration": workout.duration_seconds,
            "reps": workout.reps_completed,
            "calories": 0  # Not used, set to 0
        })
    
    return history

@router.get("/achievements")
async def get_achievements(db: Session = Depends(get_db)):
    """Get user achievements with category filtering (rehab/basic/advanced/lifting)"""
    from src.backend.database.models import Achievement, UserAchievement
    
    try:
        # Get all achievements
        all_achievements = db.query(Achievement).all()
        
        # Get unlocked achievements for user_id = 1
        unlocked_achievement_ids = set()
        unlocked_with_dates = {}
        
        user_achievements = db.query(UserAchievement).filter(
            UserAchievement.user_id == 1
        ).all()
        
        for ua in user_achievements:
            unlocked_achievement_ids.add(ua.achievement_id)
            unlocked_with_dates[ua.achievement_id] = ua.unlocked_at
        
        # Separate into unlocked and locked
        unlocked = []
        locked = []
        
        for achievement in all_achievements:
            # Handle category field - might not exist in old database
            category = getattr(achievement, 'category', None) or "basic"
            
            achievement_data = {
                "id": achievement.id,
                "name": achievement.name,
                "icon": achievement.icon or "🏆",
                "category": category
            }
            
            if achievement.id in unlocked_achievement_ids:
                # Format date
                unlock_date = unlocked_with_dates[achievement.id]
                if unlock_date:
                    date_str = unlock_date.strftime("%b %d") if hasattr(unlock_date, 'strftime') else str(unlock_date)
                else:
                    date_str = ""
                achievement_data["date"] = date_str
                unlocked.append(achievement_data)
            else:
                achievement_data["requirement"] = achievement.requirement or ""
                locked.append(achievement_data)
        
        return {
            "unlocked": unlocked,
            "locked": locked,
            "total": len(all_achievements),
            "unlocked_count": len(unlocked)
        }
    except Exception as e:
        # Return empty structure if there's any error (table doesn't exist, etc.)
        import traceback
        print(f"Error loading achievements: {e}")
        print(traceback.format_exc())
        return {
            "unlocked": [],
            "locked": [],
            "total": 0,
            "unlocked_count": 0
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

@router.get("/user/profile", response_model=UserProfileResponse)
async def get_user_profile(db: Session = Depends(get_db)):
    """Get user profile with stats and preferences"""
    from src.backend.database.models import User, Workout, UserAchievement
    from datetime import datetime, timedelta
    
    # Get default user (user_id=1) for now
    # In future, this will use authentication to get current user
    user = db.query(User).filter(User.id == 1).first()
    
    if not user:
        # Create default user if doesn't exist
        user = User(id=1, name="Champion", email=None)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Calculate stats from workouts
    workouts = db.query(Workout).filter(Workout.user_id == user.id).all()
    
    total_workouts = len(workouts)
    total_reps = sum(w.reps_completed for w in workouts) if workouts else 0
    total_muscle_gain = total_reps * 0.06  # Estimated muscle gain
    
    # Calculate days active (distinct workout dates)
    workout_dates = set()
    for workout in workouts:
        workout_date = workout.date.date() if hasattr(workout.date, 'date') else workout.date
        workout_dates.add(workout_date)
    days_active = len(workout_dates)
    
    # Calculate current streak
    current_streak = 0
    if workouts:
        # Sort workouts by date (most recent first)
        sorted_workouts = sorted(workouts, key=lambda w: w.date, reverse=True)
        today = datetime.now().date()
        check_date = today
        
        for workout in sorted_workouts:
            workout_date = workout.date.date() if hasattr(workout.date, 'date') else workout.date
            if workout_date == check_date or workout_date == check_date - timedelta(days=1):
                if workout_date == check_date:
                    # Same day workout, continue
                    pass
                else:
                    # Previous day workout, increment streak
                    current_streak += 1
                    check_date = workout_date
            else:
                # Gap found, break streak
                break
        
        # If most recent workout is today, add 1 to streak
        most_recent_date = sorted_workouts[0].date.date() if hasattr(sorted_workouts[0].date, 'date') else sorted_workouts[0].date
        if most_recent_date == today:
            current_streak += 1
    
    stats = UserStats(
        total_workouts=total_workouts,
        current_streak=current_streak,
        days_active=days_active,
        total_reps=total_reps,
        total_muscle_gain=round(total_muscle_gain, 2)
    )
    
    # Default preferences (in future, store in database)
    preferences = UserPreferences(
        notifications_enabled=True,
        units="metric",
        language="en"
    )
    
    return UserProfileResponse(
        id=user.id,
        name=user.name or "Champion",
        email=user.email,
        stats=stats,
        preferences=preferences,
        created_at=user.created_at
    )

@router.put("/user/profile", response_model=UserProfileResponse)
async def update_user_profile(
    updates: UpdateProfileRequest,
    db: Session = Depends(get_db)
):
    """Update user profile"""
    from src.backend.database.models import User
    
    # Get default user (user_id=1) for now
    user = db.query(User).filter(User.id == 1).first()
    
    if not user:
        # Create user if doesn't exist
        user = User(id=1, name="Champion", email=None)
        db.add(user)
    
    # Update fields if provided
    if updates.name is not None:
        user.name = updates.name
    if updates.email is not None:
        user.email = updates.email
    
    db.commit()
    db.refresh(user)
    
    # Get updated profile (reuse get_user_profile logic)
    # For now, just return with updated name/email
    # Preferences will be stored in database in future
    from datetime import datetime
    from src.backend.database.models import Workout
    from datetime import timedelta
    
    workouts = db.query(Workout).filter(Workout.user_id == user.id).all()
    total_workouts = len(workouts)
    total_reps = sum(w.reps_completed for w in workouts) if workouts else 0
    total_muscle_gain = total_reps * 0.06
    
    workout_dates = set()
    for workout in workouts:
        workout_date = workout.date.date() if hasattr(workout.date, 'date') else workout.date
        workout_dates.add(workout_date)
    days_active = len(workout_dates)
    
    current_streak = 0
    if workouts:
        sorted_workouts = sorted(workouts, key=lambda w: w.date, reverse=True)
        today = datetime.now().date()
        check_date = today
        
        for workout in sorted_workouts:
            workout_date = workout.date.date() if hasattr(workout.date, 'date') else workout.date
            if workout_date == check_date or workout_date == check_date - timedelta(days=1):
                if workout_date == check_date:
                    pass
                else:
                    current_streak += 1
                    check_date = workout_date
            else:
                break
        
        most_recent_date = sorted_workouts[0].date.date() if hasattr(sorted_workouts[0].date, 'date') else sorted_workouts[0].date
        if most_recent_date == today:
            current_streak += 1
    
    stats = UserStats(
        total_workouts=total_workouts,
        current_streak=current_streak,
        days_active=days_active,
        total_reps=total_reps,
        total_muscle_gain=round(total_muscle_gain, 2)
    )
    
    # Use updated preferences if provided, otherwise default
    preferences = updates.preferences if updates.preferences else UserPreferences()
    
    return UserProfileResponse(
        id=user.id,
        name=user.name or "Champion",
        email=user.email,
        stats=stats,
        preferences=preferences,
        created_at=user.created_at
    )

