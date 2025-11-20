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

class WeightProgression(BaseModel):
    starting_weight_lbs: float  # Starting weight recommendation
    progression_range: str  # e.g., "5-10 lbs", "10-20 lbs"
    progression_notes: Optional[str] = None  # Tips for progression

class EquipmentItem(BaseModel):
    name: str  # e.g., "5 lbs Ankle Weights"
    required: bool = True  # Required or optional
    description: Optional[str] = None  # Additional details
    image: Optional[str] = None  # Equipment image URL
    link: Optional[str] = None  # Link to buy/purchase equipment

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
    weight_progression: Optional[WeightProgression] = None  # Weight progression guidance
    equipment: List[EquipmentItem] = []  # Required equipment for this exercise

class TodayStatsResponse(BaseModel):
    reps_today: int
    streak: int
    calories: int

class WorkoutCreate(BaseModel):
    exercise_id: str
    duration: int  # seconds
    reps_completed: int
    calories_burned: int = 0  # Not used, kept for backward compatibility
    weight_lbs: Optional[float] = None  # Weight used in lbs
    sets_completed: int = 2  # Number of sets (2-3)
    reps_per_set: int = 15  # Reps per set (15-20)

class WorkoutResponse(BaseModel):
    id: int
    exercise_name: str
    date: datetime
    duration: int
    reps: int
    calories: int
    weight_lbs: Optional[float] = None
    sets_completed: int = 2
    reps_per_set: int = 15

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
        "id": "wall-squat",
        "name": "Wall Squat",
        "exercise_type": "basic",
        "category": "lower",
        "difficulty": "beginner",
        "duration": 15,
        "sets": 5,
        "reps": 5,
        "thumbnail": "/images/exercises/wall-squat.jpg",
        "description": "Exercise starts at 12th minute in video.",
        "target_muscles": ["Hip External Rotators", "Posterior Pelvis", "Quadriceps", "Glutes", "Hip Flexors"],
        "youtube_link": "https://youtu.be/6-VSoQnIEnA?si=ZVbenydW41nl8OFF&t=720",
        "weight_progression": {
            "starting_weight_lbs": 0.0,
            "progression_range": "Bodyweight",
            "progression_notes": "Bodyweight only exercise. Focus on breathing technique (5 deep breaths per set), position control, and pelvic biomechanics. Progress by increasing squat depth gradually as hip mobility improves. Practice twice daily for 2-4 weeks. Key is understanding sacral counternutation and posterior pelvic expansion for correct deep squat."
        },
        "equipment": [
            {
                "name": "Wall",
                "required": True,
                "description": "Stand one foot away from wall for support and reference",
                "image": None,
                "link": None
            }
        ],
        "camera_position": {
            "distance": "2-3 meters away",
            "angle": "Side view (90°)",
            "height": "Waist to hip level",
            "tips": [
                "Place camera on your side to see full body profile and squat depth",
                "Ensure both feet, knees, and hip position are visible in frame",
                "Camera should capture posterior pelvic expansion and hip external rotation",
                "Keep back arch and chest lift clearly visible",
                "Watch for proper toe angle (45 degrees) and weight distribution on contact points"
            ]
        }
    },
    {
        "id": "plank",
        "name": "Plank",
        "exercise_type": "basic",
        "category": "lower",
        "difficulty": "beginner",
        "duration": 5,
        "sets": 3,
        "reps": 1,
        "thumbnail": "/images/exercises/plank.jpg",
        "description": "Exercise starts in video.",
        "target_muscles": ["Rectus Abdominis", "Transverse Abdominis", "Obliques", "Erector Spinae", "Core Stabilizers"],
        "youtube_link": "https://youtu.be/xijbLirwKtc?si=P0iazX0cJwvvbmcQ",
        "weight_progression": {
            "starting_weight_lbs": 0.0,
            "progression_range": "Bodyweight",
            "progression_notes": "Bodyweight only exercise. Focus on proper core engagement - actively squeeze abs and tighten butt. Keep feet slightly back so shoulders align with elbows. When plank becomes difficult, drop to knees and continue holding. Progress by increasing hold duration gradually. Regular practice improves pelvis control, posture, and core strength."
        },
        "equipment": [
            {
                "name": "Exercise Mat",
                "required": False,
                "description": "Optional - use mat for comfort on hard surfaces",
                "image": None,
                "link": "https://example.com/buy/exercise-mat"
            }
        ],
        "camera_position": {
            "distance": "1.5-2 meters away",
            "angle": "Side view (90°)",
            "height": "Ground level or slightly elevated",
            "tips": [
                "Place camera on your side to see body alignment",
                "Camera should be at ground level or slightly above",
                "Ensure full body from head to feet is visible",
                "Check that your body forms a straight line in frame",
                "Watch for proper core engagement and butt squeeze"
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
        "description": "Glute fly exercise for hip mobility and glute activation. Start with bodyweight or light resistance band, then progress to ankle weights. Focus on glute medius activation in the dimple/half-moon area.",
        "target_muscles": ["Glute Medius", "Glute Minimus", "Hip Abductors"],
        "youtube_link": "https://youtu.be/ogXvRPqlj8s?si=j6vintQy_kABVj5W",
        "weight_progression": {
            "starting_weight_lbs": 0.0,
            "progression_range": "0-6 lbs",
            "progression_notes": "Start with bodyweight, hold 30 seconds. Add 5-6 lbs weight when correct muscle firing is achieved. Keep movement short and compact. Focus on glute medius dimple activation."
        },
        "equipment": [
            {
                "name": "2-inch Pad or Towel",
                "required": True,
                "description": "Place under knee for support",
                "image": None,
                "link": "https://example.com/buy/yoga-block"
            },
            {
                "name": "5-6 lbs Ankle Weight or Dumbbell",
                "required": False,
                "description": "Optional - start with bodyweight, add weight when form is correct",
                "image": None,
                "link": "https://example.com/buy/ankle-weights"
            }
        ],
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
        "id": "knee-drop",
        "name": "Knee Drop",
        "exercise_type": "rehab",
        "category": "lower",
        "difficulty": "intermediate",
        "duration": 15,
        "sets": 3,
        "reps": 15,
        "thumbnail": "/images/exercises/knee-drop.jpg",
        "description": "Knee drop exercise for glute minimus and medius activation. Performed in sideline position with controlled up-down knee movement. Focus on slow, controlled motion with emphasis on down phase.",
        "target_muscles": ["Glute Minimus", "Glute Medius", "Hip Abductors"],
        "youtube_link": "https://youtu.be/ogXvRPqlj8s?si=j6vintQy_kABVj5W",
        "weight_progression": {
            "starting_weight_lbs": 0.0,
            "progression_range": "0-8 lbs",
            "progression_notes": "Start without weight, use 2-inch pad/towel under knee. Progress to 5-8 lbs ankle weight or dumbbell when form is perfect. Focus on down phase for minimus activation. No hip or compensation movement."
        },
        "equipment": [
            {
                "name": "2-inch Pad or Towel",
                "required": True,
                "description": "Place under knee for medial rotation support",
                "image": None,
                "link": "https://example.com/buy/yoga-block"
            },
            {
                "name": "5-8 lbs Ankle Weight or Dumbbell",
                "required": False,
                "description": "Optional - add when form is perfect",
                "image": None,
                "link": "https://example.com/buy/ankle-weights"
            }
        ],
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Side view (90°)",
            "height": "Hip to knee level",
            "tips": [
                "Place camera on your side to see knee movement",
                "Ensure heel alignment with butt center is visible",
                "Camera should capture knee up-down range",
                "Keep knees stacked and visible in frame"
            ]
        }
    },
    {
        "id": "hamstring-medial-bridge",
        "name": "Hamstring Medial Bridge",
        "exercise_type": "rehab",
        "category": "lower",
        "difficulty": "intermediate",
        "duration": 12,
        "sets": 3,
        "reps": 15,
        "thumbnail": "/images/exercises/hamstring-medial-bridge.jpg",
        "description": "Hamstring medial bridge for medial hamstring (semimembranosus) activation. Lie on back, lift hips with glute squeeze. Focus on inner hamstring tension, not high lift. Avoid back pressure.",
        "target_muscles": ["Medial Hamstring", "Semimembranosus", "Glutes"],
        "youtube_link": "https://youtu.be/ogXvRPqlj8s?si=j6vintQy_kABVj5W",
        "weight_progression": {
            "starting_weight_lbs": 0.0,
            "progression_range": "0-10 lbs",
            "progression_notes": "Start with bodyweight, focus on medial hamstring feel. Don't lift too high, just enough for inner hamstring tension. Progress to single leg (advanced) after mastering both legs."
        },
        "equipment": [
            {
                "name": "Bench",
                "required": True,
                "description": "Use a bench for hamstring medial bridge",
                "image": None,
                "link": "https://example.com/buy/bench"
            }
        ],
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Side view (90°)",
            "height": "Hip to knee level",
            "tips": [
                "Place camera on your side to see hip lift",
                "Ensure full body from head to feet is visible",
                "Camera should capture hip bridge range",
                "Keep ankles at 90-degree angle visible"
            ]
        }
    },
    {
        "id": "ball-squeeze",
        "name": "Ball Squeeze",
        "exercise_type": "rehab",
        "category": "lower",
        "difficulty": "beginner",
        "duration": 10,
        "sets": 3,
        "reps": 20,
        "thumbnail": "/images/exercises/ball-squeeze.jpg",
        "description": "Ball squeeze exercise for adductor chain activation. Butterfly position with medicine ball or football between knees. Squeeze and relax, focus on groin/adductor activation. Keep back arch for better activation.",
        "target_muscles": ["Adductors", "Hip Flexors", "Groin"],
        "youtube_link": "https://youtu.be/ogXvRPqlj8s?si=j6vintQy_kABVj5W",
        "weight_progression": {
            "starting_weight_lbs": 0.0,
            "progression_range": "N/A (ball size)",
            "progression_notes": "Start with smaller ball, progress to larger medicine ball. Focus on adductor (groin) feel, not hip flexor pinch. If adductors don't fire, do other exercises first for 3-4 weeks."
        },
        "equipment": [
            {
                "name": "Medicine Ball or Football",
                "required": True,
                "description": "Start with smaller ball, progress to larger size",
                "image": None,
                "link": "https://example.com/buy/medicine-ball"
            }
        ],
        "camera_position": {
            "distance": "1.5-2 meters away",
            "angle": "Front view (0°) or 45° angle",
            "height": "Hip to knee level",
            "tips": [
                "Place camera in front or slightly to side",
                "Ensure ball and knee position are visible",
                "Camera should capture squeeze motion",
                "Keep butterfly position clearly in frame"
            ]
        }
    },
    {
        "id": "quad-stretch",
        "name": "Quad Stretch / Safe Extension",
        "exercise_type": "rehab",
        "category": "lower",
        "difficulty": "beginner",
        "duration": 10,
        "sets": 3,
        "reps": 15,
        "thumbnail": "/images/exercises/quad-stretch.jpg",
        "description": "Quad stretch and safe extension for knee rehab. Lie on back, one heel at butt line, other leg extended. Gentle quad stretch with toe up. Start with light weight (2.5-5 kg), work within available range.",
        "target_muscles": ["Quadriceps", "Hip Flexors"],
        "youtube_link": "https://youtu.be/ogXvRPqlj8s?si=j6vintQy_kABVj5W",
        "weight_progression": {
            "starting_weight_lbs": 0.0,
            "progression_range": "0-11 lbs (5 kg)",
            "progression_notes": "Start with bodyweight, gentle stretch. Add 2.5-5 kg (5.5-11 lbs) ankle weight when comfortable. Healthy side can use more weight. Work within available range, don't force. Range improves gradually."
        },
        "equipment": [
            {
                "name": "2.5-5 kg (5.5-11 lbs) Ankle Weight",
                "required": True,
                "description": "Ankle weight for quad stretch and safe extension",
                "image": None,
                "link": "https://example.com/buy/ankle-weights"
            }
        ],
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Side view (90°)",
            "height": "Hip to knee level",
            "tips": [
                "Place camera on your side to see leg extension",
                "Ensure heel-to-butt alignment is visible",
                "Camera should capture quad stretch range",
                "Keep toe position and knee angle visible"
            ]
        }
    },
    {
        "id": "depression-row",
        "name": "Depression Row",
        "exercise_type": "rehab",
        "category": "upper",
        "difficulty": "intermediate",
        "duration": 12,
        "sets": 3,
        "reps": 12,
        "thumbnail": "/images/exercises/depression-row.jpg",
        "description": "Depression row for winged scapula, labrum tears, and shoulder instability. Focus on scapula depression with shoulder slightly forward, chest lifted, and elbow at 45-degree angle. Key is depression movement, not rowing motion. Avoid rolling shoulder back - keep it forward with chest high for proper scapula flat position.",
        "target_muscles": ["Teres Major", "Teres Minor", "Infraspinatus", "Scapula Stabilizers", "Lower Trapezius"],
        "youtube_link": "https://youtu.be/45uGOybW-Ys?si=bTAo23bUEw6Jvj8e",
        "weight_progression": {
            "starting_weight_lbs": 0.0,
            "progression_range": "0-15 lbs",
            "progression_notes": "Start with light resistance band or cable. Focus on proper depression technique - shoulder forward, chest lifted, elbow at 45-degree angle. Progress slowly - depression angle improves about 1/4 inch per month with correct form. Master depression before adding advanced exercises."
        },
        "equipment": [
            {
                "name": "Exercise Bands",
                "required": True,
                "description": "Resistance band or cable for depression row. Start with light resistance, focus on form over weight.",
                "image": None,
                "link": "https://example.com/buy/exercise-bands"
            },
            {
                "name": "Cable Machine",
                "required": False,
                "description": "Alternative to bands - use cable machine if available",
                "image": None,
                "link": "https://example.com/buy/cable-machine"
            }
        ],
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Side view (90°) or 45° angle",
            "height": "Shoulder to chest level",
            "tips": [
                "Place camera on your side to see scapula movement",
                "Ensure full upper body and shoulder blade are visible",
                "Camera should capture scapula depression range",
                "Keep chest lift and shoulder position clearly in frame",
                "Watch for winged scapula correction during depression"
            ]
        }
    },
    {
        "id": "rear-delt-raise",
        "name": "Rear Delt Raise",
        "exercise_type": "basic",
        "category": "upper",
        "difficulty": "intermediate",
        "duration": 10,
        "sets": 3,
        "reps": 12,
        "thumbnail": "/images/exercises/rear-delt-raise.jpg",
        "description": "Rear delt raise over bench for rear deltoid and scapular stabilizer strengthening. Performed lying on bench with chest supported. Focus on controlled movement with slow eccentric phase. Helps fix winged scapula and improve shoulder stability. Emphasize scapular retraction and depression.",
        "target_muscles": ["Rear Deltoids", "Rhomboids", "Infraspinatus", "Scapular Stabilizers", "Middle Trapezius"],
        "youtube_link": "https://youtu.be/C-YRTquDjbg?si=wlSdPkuC81_3QnMU",
        "weight_progression": {
            "starting_weight_lbs": 5.0,
            "progression_range": "5-10 lbs",
            "progression_notes": "Start with light weight (5-8 lbs). Focus on form and muscle feel over weight. Progress weight only when form is perfect and scapular control is complete. Slow eccentric (lowering) phase is important to maintain tension in scapula muscles."
        },
        "equipment": [
            {
                "name": "Bench",
                "required": True,
                "description": "Bench for chest support - lie on side or support torso on bench",
                "image": None,
                "link": "https://example.com/buy/bench"
            },
            {
                "name": "5-10 lbs Dumbbells",
                "required": True,
                "description": "Light dumbbells per arm - rear delts are small muscles, start light",
                "image": None,
                "link": "https://example.com/buy/dumbbells"
            }
        ],
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Side view (90°) or 45° angle",
            "height": "Shoulder to chest level",
            "tips": [
                "Place camera on your side to see rear delt movement",
                "Ensure full upper body and shoulder blade are visible",
                "Camera should capture arm raise range (shoulder height parallel)",
                "Keep scapular retraction and rear delt squeeze clearly in frame",
                "Watch for controlled lowering phase and no trunk rotation"
            ]
        }
    },
    {
        "id": "pant-pull",
        "name": "Pant Pull",
        "exercise_type": "basic",
        "category": "upper",
        "difficulty": "beginner",
        "duration": 8,
        "sets": 3,
        "reps": 15,
        "thumbnail": "/images/exercises/pant-pull.jpg",
        "description": "Pant pull exercise for scapular strengthening and fixing winged scapula. Standing or slight bend forward stance with arms pulled back like pulling pants waistband. Focus on scapular retraction - squeeze shoulder blades together without shrugging up. Controlled movement to activate scapular stabilizers (rhomboids, rear delts, lower traps). Daily practice recommended to retrain scapular muscles and build strong movement pattern.",
        "target_muscles": ["Rhomboids", "Rear Deltoids", "Lower Trapezius", "Scapular Stabilizers", "Middle Trapezius"],
        "youtube_link": "https://youtu.be/T70OdD3ckcI?si=gTgATcsIuuhWOzT_",
        "weight_progression": {
            "starting_weight_lbs": 0.0,
            "progression_range": "Bodyweight",
            "progression_notes": "Start with bodyweight. Focus on proper scapular retraction and controlled movement. Can progress to using resistance bands or light weights once form is perfect. Daily practice is beneficial for scapular stability improvement."
        },
        "equipment": [
            {
                "name": "None (Bodyweight)",
                "required": False,
                "description": "Can be done with bodyweight only",
                "image": None,
                "link": None
            },
            {
                "name": "Exercise Bands",
                "required": False,
                "description": "Optional - add resistance bands for progression once form is perfect",
                "image": None,
                "link": "https://example.com/buy/exercise-bands"
            }
        ],
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Side view (90°) or 45° angle",
            "height": "Shoulder to chest level",
            "tips": [
                "Place camera on your side to see scapular movement",
                "Ensure full upper body and shoulder blades are visible",
                "Camera should capture scapular retraction range",
                "Keep arms and shoulder blade position clearly in frame",
                "Watch for controlled movement without shoulder shrugging"
            ]
        }
    },
    {
        "id": "pad-cuff",
        "name": "Pad Cuff",
        "exercise_type": "basic",
        "category": "upper",
        "difficulty": "beginner",
        "duration": 10,
        "sets": 3,
        "reps": 15,
        "thumbnail": "/images/exercises/pad-cuff.jpg",
        "description": "Pad cuff exercise for shoulder rehab focusing on infraspinatus region. Elbow at hip center line, arm at 90-degree angle. Short range controlled movement with light pressure (5% push down). Goal is to feel tension in infraspinatus region, not front/side shoulder or rear delt. Start with light weight (1-3 kg / 2-6 lbs). Slow and controlled reps, avoid over-stressing shoulder. Focus on mind-muscle connection to infraspinatus region. Perform 2x per week for recovery, avoid high frequency if technique not perfect.",
        "target_muscles": ["Infraspinatus", "Teres Minor", "Rotator Cuff", "Posterior Deltoids"],
        "youtube_link": "https://youtu.be/FLGcoOxTaR4?si=FQBMRtrCKpFHWsac",
        "weight_progression": {
            "starting_weight_lbs": 2.0,
            "progression_range": "2-6 lbs",
            "progression_notes": "Start with very light weight (1-3 kg / 2-6 lbs). Too much weight can irritate shoulder. Focus on proper form and infraspinatus activation over weight. Progress weight only when technique is perfect and you can consistently feel tension in infraspinatus region. Avoid compensation from other muscles."
        },
        "equipment": [
            {
                "name": "Pad or Towel",
                "required": True,
                "description": "2-inch pad or towel for support during exercise",
                "image": None,
                "link": "https://example.com/buy/pad-towel"
            },
            {
                "name": "Light Dumbbell",
                "required": True,
                "description": "Very light dumbbell (1-3 kg / 2-6 lbs) - start low to avoid shoulder irritation",
                "image": None,
                "link": "https://example.com/buy/dumbbells"
            }
        ],
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Side view (90°) or 45° angle",
            "height": "Shoulder to chest level",
            "tips": [
                "Place camera on your side to see shoulder and arm position",
                "Ensure elbow position at hip center line is clearly visible",
                "Camera should capture 90-degree arm angle and short range movement",
                "Keep infraspinatus region and shoulder blade position in frame",
                "Watch for controlled movement without compensation"
            ]
        }
    },
    {
        "id": "weighted-pull-ups",
        "name": "Weighted Pull-ups",
        "exercise_type": "advanced",
        "category": "upper",
        "difficulty": "advanced",
        "duration": 10,
        "sets": 1,
        "reps": 12,
        "thumbnail": "/images/exercises/pull-ups.jpg",
        "description": "Exercise starts in video. NOTE: Requires gym equipment (assisted pull-up machine for warm-up, pull-up bar with weight attachment for working set). Cannot be performed at home without proper setup.",
        "target_muscles": ["Latissimus Dorsi", "Rhomboids", "Middle Trapezius", "Rear Deltoids", "Biceps", "Brachialis"],
        "youtube_link": "https://youtu.be/s8irV9uIxgI?si=W5rk10Gpfk9eexqS",
        "weight_progression": {
            "starting_weight_lbs": 0.0,
            "progression_range": "Bodyweight to 10-20 lbs",
            "progression_notes": "Start with assisted pull-ups (20 lbs assist) to build form. Once you can do 11-12 reps with bodyweight, add 5 lbs weight. Focus on correct form: stay back, drive arms to bottom of chest, no shrug. All-out set to failure. If you hit 7-9 reps, use rest-pause (15-30 second rest, then more reps)."
        },
        "equipment": [
            {
                "name": "Assisted Pull-up Machine",
                "required": True,
                "description": "Gym machine with ankle strap for assisted pull-ups (warm-up: 20 lbs assist). Required for form building.",
                "image": None,
                "link": "https://example.com/buy/assisted-pull-up-machine"
            },
            {
                "name": "Pull-up Bar with Weight Attachment",
                "required": True,
                "description": "Gym pull-up bar with weight belt attachment for weighted pull-ups (working set: 5-20 lbs added weight)",
                "image": None,
                "link": "https://example.com/buy/pull-up-bar"
            },
            {
                "name": "Weight Belt",
                "required": True,
                "description": "Weight belt for adding weight to pull-ups (5-20 lbs progression)",
                "image": None,
                "link": "https://example.com/buy/weight-belt"
            }
        ],
        "camera_position": {
            "distance": "2-3 meters away",
            "angle": "Side view (90°) or front view",
            "height": "Chest to head level",
            "tips": [
                "Place camera to capture full body from side or front",
                "Ensure pull-up bar and full range of motion is visible",
                "Camera should show body position and arm drive to chest",
                "Watch for proper form: stay back, no shrug, controlled movement"
            ]
        }
    },
    {
        "id": "close-grip-pull-down",
        "name": "Close Grip Pull Down",
        "exercise_type": "advanced",
        "category": "upper",
        "difficulty": "advanced",
        "duration": 5,
        "sets": 1,
        "reps": 12,
        "thumbnail": "/images/exercises/pull-down.jpg",
        "description": "Exercise starts in video. NOTE: This exercise requires gym equipment (pulldown machine). Cannot be performed at home.",
        "target_muscles": ["Latissimus Dorsi", "Rhomboids", "Middle Trapezius", "Biceps", "Brachialis"],
        "youtube_link": "https://youtu.be/s8irV9uIxgI?si=W5rk10Gpfk9eexqS",
        "weight_progression": {
            "starting_weight_lbs": 100.0,
            "progression_range": "100-120 lbs",
            "progression_notes": "Warm up with 20 lbs less than working weight (100 lbs warm-up, 120 lbs working set). Working set: all-out to failure. Goal is 11-12 reps before increasing weight. Take small pause at bottom for muscle connection and control. After working set, perform drop set for additional volume."
        },
        "equipment": [
            {
                "name": "Pulldown Machine (Cable System)",
                "required": True,
                "description": "Gym pulldown machine with cable system. Warm-up: 100 lbs, Working set: 120 lbs. Required - cannot be done at home.",
                "image": None,
                "link": "https://example.com/buy/pulldown-machine"
            },
            {
                "name": "Close Grip Handle",
                "required": True,
                "description": "Close grip attachment for pulldown machine",
                "image": None,
                "link": "https://example.com/buy/close-grip-handle"
            }
        ],
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Side view (90°)",
            "height": "Chest to head level",
            "tips": [
                "Place camera on your side to see full range of motion",
                "Ensure cable machine and handle position are visible",
                "Camera should capture controlled pull-down with pause at bottom",
                "Watch for proper lat engagement and muscle connection"
            ]
        }
    },
    {
        "id": "wide-grip-row",
        "name": "Wide Grip Row",
        "exercise_type": "advanced",
        "category": "upper",
        "difficulty": "advanced",
        "duration": 5,
        "sets": 1,
        "reps": 9,
        "thumbnail": "/images/exercises/row.jpg",
        "description": "Exercise starts in video. NOTE: This exercise requires gym equipment (wide grip row machine). Cannot be performed at home.",
        "target_muscles": ["Upper Latissimus Dorsi", "Rhomboids", "Middle Trapezius", "Rear Deltoids"],
        "youtube_link": "https://youtu.be/s8irV9uIxgI?si=W5rk10Gpfk9eexqS",
        "weight_progression": {
            "starting_weight_lbs": 90.0,
            "progression_range": "90-110 lbs",
            "progression_notes": "Warm up with 20 lbs less than working weight (90 lbs warm-up, 110 lbs working set). Working set: all-out to failure. Goal is 9 reps. This exercise targets upper section of lats. Fatigue from previous exercises may affect performance, which is normal."
        },
        "equipment": [
            {
                "name": "Wide Grip Row Machine",
                "required": True,
                "description": "Gym row machine with wide grip handle. Warm-up: 90 lbs, Working set: 110 lbs. Required - cannot be done at home.",
                "image": None,
                "link": "https://example.com/buy/row-machine"
            },
            {
                "name": "Wide Grip Handle",
                "required": True,
                "description": "Wide grip handle attachment for row machine",
                "image": None,
                "link": "https://example.com/buy/wide-grip-handle"
            }
        ],
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Side view (90°)",
            "height": "Chest level",
            "tips": [
                "Place camera on your side to see rowing motion",
                "Ensure cable machine and handle position are visible",
                "Camera should capture upper lat engagement",
                "Watch for controlled rowing motion and proper form"
            ]
        }
    },
    {
        "id": "single-arm-row",
        "name": "Single Arm Row (Cable Machine)",
        "exercise_type": "advanced",
        "category": "upper",
        "difficulty": "advanced",
        "duration": 5,
        "sets": 1,
        "reps": 9,
        "thumbnail": "/images/exercises/row.jpg",
        "description": "Exercise starts in video. NOTE: This exercise requires gym equipment (cable machine). Preferred over dumbbell rows for less hip pressure. Cannot be performed at home.",
        "target_muscles": ["Latissimus Dorsi", "Rhomboids", "Middle Trapezius", "Rear Deltoids", "Biceps"],
        "youtube_link": "https://youtu.be/s8irV9uIxgI?si=W5rk10Gpfk9eexqS",
        "weight_progression": {
            "starting_weight_lbs": 80.0,
            "progression_range": "80-100 lbs",
            "progression_notes": "Preferred over dumbbell rows for less hip pressure. Warm up first, then working set at 100 units (10). All-out set to failure. Single arm allows for better muscle connection and focus. No rest-pause needed if already fatigued from previous exercises."
        },
        "equipment": [
            {
                "name": "Cable Machine",
                "required": True,
                "description": "Gym cable machine with single handle attachment. Working set: 100 units (10). Required - cannot be done at home.",
                "image": None,
                "link": "https://example.com/buy/cable-machine"
            },
            {
                "name": "Single Handle",
                "required": True,
                "description": "Single handle attachment for cable machine rowing",
                "image": None,
                "link": "https://example.com/buy/single-handle"
            }
        ],
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Side view (90°)",
            "height": "Chest level",
            "tips": [
                "Place camera on your side to see single arm rowing motion",
                "Ensure cable machine and handle position are visible",
                "Camera should capture full range of motion and muscle engagement",
                "Watch for proper form and controlled movement"
            ]
        }
    },
    {
        "id": "weighted-dips",
        "name": "Dips Off The Bench (Weighted)",
        "exercise_type": "advanced",
        "category": "upper",
        "difficulty": "advanced",
        "duration": 5,
        "sets": 1,
        "reps": 15,
        "thumbnail": "/images/exercises/dips.jpg",
        "description": "Exercise starts in video. NOTE: Can be performed at home with bench and dumbbell.",
        "target_muscles": ["Triceps Brachii", "Anterior Deltoids", "Pectoralis Major (Lower)", "Triceps Horseshoe"],
        "youtube_link": "https://youtu.be/s8irV9uIxgI?si=W5rk10Gpfk9eexqS",
        "weight_progression": {
            "starting_weight_lbs": 70.0,
            "progression_range": "70-80 lbs",
            "progression_notes": "Best exercise for tricep development and horseshoe shape. Keep reps in 12-15 failure range. Warm up first, then working set with 80 lb dumbbell. Once you hit 15 reps, increase weight next week. After weighted set, perform bodyweight burnout for additional volume."
        },
        "equipment": [
            {
                "name": "Bench",
                "required": True,
                "description": "Flat bench for dips off the bench. Can use home bench or gym bench.",
                "image": None,
                "link": "https://example.com/buy/bench"
            },
            {
                "name": "Dumbbell",
                "required": True,
                "description": "Weighted dumbbell (70-80 lbs) placed on lap during dips",
                "image": None,
                "link": "https://example.com/buy/dumbbells"
            }
        ],
        "camera_position": {
            "distance": "2-3 meters away",
            "angle": "Side view (90°)",
            "height": "Chest to head level",
            "tips": [
                "Place camera on your side to see full dip motion",
                "Ensure bench and full range of motion are visible",
                "Camera should capture tricep engagement and contraction",
                "Watch for proper form and controlled movement"
            ]
        }
    },
    {
        "id": "incline-skull-crushers",
        "name": "Incline Skull Crushers (Dumbbells)",
        "exercise_type": "advanced",
        "category": "upper",
        "difficulty": "advanced",
        "duration": 5,
        "sets": 1,
        "reps": 12,
        "thumbnail": "/images/exercises/skull-crushers.jpg",
        "description": "Exercise starts in video. NOTE: Can be performed at home with adjustable incline bench and dumbbells.",
        "target_muscles": ["Triceps Brachii", "Triceps Long Head", "Triceps Lateral Head", "Triceps Medial Head"],
        "youtube_link": "https://youtu.be/s8irV9uIxgI?si=W5rk10Gpfk9eexqS",
        "weight_progression": {
            "starting_weight_lbs": 30.0,
            "progression_range": "30-35 lbs",
            "progression_notes": "Incline version reduces elbow torque compared to flat skull crushers. Warm up first, then working set with 35 lb dumbbells. Goal is 7-12 reps. If you hit 12 reps, increase weight next week. All-out set to failure. No drop set if already fatigued."
        },
        "equipment": [
            {
                "name": "Adjustable Incline Bench",
                "required": True,
                "description": "Incline bench (30-45 degrees) for skull crushers. Can use adjustable home bench or gym bench.",
                "image": None,
                "link": "https://example.com/buy/incline-bench"
            },
            {
                "name": "Dumbbells",
                "required": True,
                "description": "Dumbbells (30-35 lbs each) for incline skull crushers",
                "image": None,
                "link": "https://example.com/buy/dumbbells"
            }
        ],
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Side view (90°) or front view",
            "height": "Chest to head level",
            "tips": [
                "Place camera on your side to see full tricep extension",
                "Ensure incline bench and dumbbell position are visible",
                "Camera should capture tricep engagement and controlled movement",
                "Watch for proper elbow position and reduced torque"
            ]
        }
    },
    {
        "id": "incline-bench-press",
        "name": "Incline Bench Press",
        "exercise_type": "advanced",
        "category": "upper",
        "difficulty": "advanced",
        "duration": 10,
        "sets": 1,
        "reps": 12,
        "thumbnail": "/images/exercises/bench-press.jpg",
        "description": "Exercise starts in video. NOTE: Requires gym equipment (incline bench press machine or barbell with incline bench). Cannot be performed at home.",
        "target_muscles": ["Pectoralis Major (Upper)", "Anterior Deltoids", "Triceps Brachii"],
        "youtube_link": "https://youtu.be/s8irV9uIxgI?si=W5rk10Gpfk9eexqS",
        "weight_progression": {
            "starting_weight_lbs": 0.0,
            "progression_range": "Varies by strength level",
            "progression_notes": "Warm up with 10-15 lbs less than working weight (8 reps). Working set: all-out to failure. Goal is 10-12 reps. Once you hit 12 reps, increase weight next week. Use rest-pause after failure for 2-3 extra reps. Grip: Pinky on bench notch, hands slightly inside elbows (like dumbbell press position). Avoid wider grip to reduce shoulder pressure."
        },
        "equipment": [
            {
                "name": "Incline Bench Press Machine",
                "required": True,
                "description": "Gym incline bench press machine (30-45 degree angle) or barbell with incline bench",
                "image": None,
                "link": "https://example.com/buy/incline-bench-press"
            }
        ],
        "camera_position": {
            "distance": "2-3 meters away",
            "angle": "Side view (90°)",
            "height": "Chest to head level",
            "tips": [
                "Place camera on your side to see full bench press motion",
                "Ensure bench angle and full range of motion are visible",
                "Camera should capture proper grip position and bar path",
                "Watch for controlled movement and proper form"
            ]
        }
    },
    {
        "id": "flat-dumbbell-bench-press",
        "name": "Flat Dumbbell Bench Press",
        "exercise_type": "advanced",
        "category": "upper",
        "difficulty": "advanced",
        "duration": 8,
        "sets": 1,
        "reps": 8,
        "thumbnail": "/images/exercises/bench-press.jpg",
        "description": "Exercise starts in video. NOTE: Requires gym equipment (flat bench and heavy dumbbells). Cannot be performed at home without proper setup.",
        "target_muscles": ["Pectoralis Major", "Anterior Deltoids", "Triceps Brachii"],
        "youtube_link": "https://youtu.be/s8irV9uIxgI?si=W5rk10Gpfk9eexqS",
        "weight_progression": {
            "starting_weight_lbs": 70.0,
            "progression_range": "70-80 lbs",
            "progression_notes": "Working set with 80 lbs dumbbells. Goal is 8 reps. Once you hit target reps, increase weight next week. Take 3-4 minute rest before working set. After working set, perform quick drop set (e.g., 80 lbs to 60 lbs). No rest-pause with dumbbells (too risky)."
        },
        "equipment": [
            {
                "name": "Flat Bench",
                "required": True,
                "description": "Gym flat bench for dumbbell press",
                "image": None,
                "link": "https://example.com/buy/bench"
            },
            {
                "name": "Heavy Dumbbells",
                "required": True,
                "description": "Heavy dumbbells (70-80 lbs each) for bench press",
                "image": None,
                "link": "https://example.com/buy/dumbbells"
            }
        ],
        "camera_position": {
            "distance": "2-3 meters away",
            "angle": "Side view (90°)",
            "height": "Chest level",
            "tips": [
                "Place camera on your side to see full dumbbell press motion",
                "Ensure bench and full range of motion are visible",
                "Camera should capture controlled movement and proper form",
                "Watch for proper dumbbell path and chest engagement"
            ]
        }
    },
    {
        "id": "cable-crossovers",
        "name": "Cable Crossovers/Flys",
        "exercise_type": "advanced",
        "category": "upper",
        "difficulty": "advanced",
        "duration": 5,
        "sets": 1,
        "reps": 12,
        "thumbnail": "/images/exercises/cable-fly.jpg",
        "description": "Exercise starts in video. NOTE: Requires gym equipment (cable machine). Cannot be performed at home.",
        "target_muscles": ["Pectoralis Major (Inner)", "Anterior Deltoids"],
        "youtube_link": "https://youtu.be/s8irV9uIxgI?si=W5rk10Gpfk9eexqS",
        "weight_progression": {
            "starting_weight_lbs": 0.0,
            "progression_range": "Varies by strength level",
            "progression_notes": "Warm up first, then all-out set to failure. Goal is 12 solid reps. Don't go too far back - only go back as far as you can without shrugging and while maintaining inner chest connection. After failure, perform partials for total fatigue (these don't count in main rep count)."
        },
        "equipment": [
            {
                "name": "Cable Machine",
                "required": True,
                "description": "Gym cable machine with cable crossover setup",
                "image": None,
                "link": "https://example.com/buy/cable-machine"
            }
        ],
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Front view or side view (90°)",
            "height": "Chest level",
            "tips": [
                "Place camera in front or side to see cable fly motion",
                "Ensure cable machine and full range of motion are visible",
                "Camera should capture inner chest engagement",
                "Watch for proper form - don't go too far back, maintain chest connection"
            ]
        }
    },
    {
        "id": "hammer-curls",
        "name": "Hammer Curls",
        "exercise_type": "advanced",
        "category": "upper",
        "difficulty": "advanced",
        "duration": 5,
        "sets": 1,
        "reps": 8,
        "thumbnail": "/images/exercises/bicep-curl.jpg",
        "description": "Exercise starts in video. NOTE: Requires gym equipment (dumbbells). Safer alternative to regular curls for elbow pressure.",
        "target_muscles": ["Biceps Brachii", "Brachialis", "Brachioradialis", "Forearm Extensors"],
        "youtube_link": "https://youtu.be/s8irV9uIxgI?si=W5rk10Gpfk9eexqS",
        "weight_progression": {
            "starting_weight_lbs": 30.0,
            "progression_range": "30-35 lbs",
            "progression_notes": "Warm up with 30 lbs (12 reps target). Working set with 35 lbs (7-8 reps target). If too much elbow pressure, drop weight and do lighter high reps (15-20) for burnout. Hammer curls put more pressure on wrist extensors."
        },
        "equipment": [
            {
                "name": "Dumbbells",
                "required": True,
                "description": "Dumbbells (30-35 lbs each) for hammer curls",
                "image": None,
                "link": "https://example.com/buy/dumbbells"
            }
        ],
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Front view or side view (90°)",
            "height": "Chest to shoulder level",
            "tips": [
                "Place camera in front or side to see hammer curl motion",
                "Ensure full range of motion and arm position are visible",
                "Camera should capture bicep and forearm engagement",
                "Watch for proper form and controlled movement"
            ]
        }
    },
    {
        "id": "barbell-curls",
        "name": "Barbell Curls",
        "exercise_type": "advanced",
        "category": "upper",
        "difficulty": "advanced",
        "duration": 5,
        "sets": 1,
        "reps": 12,
        "thumbnail": "/images/exercises/bicep-curl.jpg",
        "description": "Exercise starts in video. NOTE: Requires gym equipment (barbell). Cannot be performed at home.",
        "target_muscles": ["Biceps Brachii", "Brachialis", "Forearm Flexors"],
        "youtube_link": "https://youtu.be/s8irV9uIxgI?si=W5rk10Gpfk9eexqS",
        "weight_progression": {
            "starting_weight_lbs": 0.0,
            "progression_range": "Varies by strength level",
            "progression_notes": "Quick 2-rep warm-up, then 1.5 minute rest before working set. When you fail, use swing to get weight up, then focus on eccentric (negative) portion for 4 extra reps. This technique helps maximize volume after failure."
        },
        "equipment": [
            {
                "name": "Barbell",
                "required": True,
                "description": "Gym barbell with appropriate weight plates",
                "image": None,
                "link": "https://example.com/buy/barbell"
            }
        ],
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Front view or side view (90°)",
            "height": "Chest to shoulder level",
            "tips": [
                "Place camera in front or side to see barbell curl motion",
                "Ensure full range of motion and bar path are visible",
                "Camera should capture bicep engagement and form",
                "Watch for controlled movement and proper technique"
            ]
        }
    },
    {
        "id": "cable-crunch",
        "name": "Cable Crunch/Ab Roll",
        "exercise_type": "advanced",
        "category": "upper",
        "difficulty": "advanced",
        "duration": 5,
        "sets": 1,
        "reps": 15,
        "thumbnail": "/images/exercises/crunch.jpg",
        "description": "Exercise starts in video. NOTE: Requires gym equipment (cable system). Cannot be performed at home.",
        "target_muscles": ["Rectus Abdominis", "Obliques", "Transverse Abdominis"],
        "youtube_link": "https://youtu.be/s8irV9uIxgI?si=W5rk10Gpfk9eexqS",
        "weight_progression": {
            "starting_weight_lbs": 0.0,
            "progression_range": "Bodyweight to weighted",
            "progression_notes": "Performed on knees using cable system. Focus on squeezing butt and tucking under. If you feel pressure in low back, you're not ready for this position. Should only feel abs, not low back. Usually paired with side raises for obliques."
        },
        "equipment": [
            {
                "name": "Cable System",
                "required": True,
                "description": "Gym cable machine with cable crunch attachment",
                "image": None,
                "link": "https://example.com/buy/cable-machine"
            }
        ],
        "camera_position": {
            "distance": "2-2.5 meters away",
            "angle": "Side view (90°)",
            "height": "Waist to chest level",
            "tips": [
                "Place camera on your side to see cable crunch motion",
                "Ensure cable system and full range of motion are visible",
                "Camera should capture core engagement and form",
                "Watch for proper butt squeeze and tuck position"
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
        calories_burned=0,  # Not used, set to 0
        weight_lbs=workout.weight_lbs,
        sets_completed=workout.sets_completed,
        reps_per_set=workout.reps_per_set
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
            "calories": 0,  # Not used, set to 0
            "weight_lbs": workout.weight_lbs,
            "sets_completed": workout.sets_completed or 2,
            "reps_per_set": workout.reps_per_set or 15
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

