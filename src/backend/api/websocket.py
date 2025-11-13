"""
WebSocket Handler for Real-time Workout Streaming
Streams video frames with pose detection and rep counting
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import logging
import asyncio
import json
import cv2
import base64
import numpy as np

router = APIRouter()
logger = logging.getLogger(__name__)

# Import trainers
from src.backend.exercises.squat_trainer import SquatTrainer
from src.backend.exercises.pushup_trainer import PushupTrainer
from src.backend.exercises.shoulder_press_trainer import ShoulderPressTrainer
from src.backend.exercises.bicep_curl_trainer import BicepCurlTrainer
from src.backend.exercises.plank_trainer import PlankTrainer
from src.backend.exercises.row_trainer import RowTrainer
from src.backend.exercises.pullup_trainer import PullupTrainer
from src.backend.exercises.lunge_trainer import LungeTrainer
from src.backend.exercises.crunch_trainer import CrunchTrainer
from src.backend.exercises.tricep_dip_trainer import TricepDipTrainer
from src.backend.exercises.lateral_raise_trainer import LateralRaiseTrainer

# Glute Fly wrapper (glute_fly.py is script-based, so we'll create a simple wrapper)
class GluteFlyTrainer:
    """Wrapper for Glute Fly exercise - uses basic processing for now"""
    def __init__(self):
        self.reps = 0
        self.current_feedback = "Glute Fly - Position yourself for calibration"
        print("[GluteFlyTrainer] Using basic processing (full trainer coming soon)")
    
    def process_frame(self, results, w: int, h: int, side: str = 'left'):
        """Basic process_frame for WebSocket compatibility"""
        if not results.pose_landmarks:
            return {
                "reps": self.reps,
                "feedback": "No pose detected - step into frame",
                "angles": {},
                "progress": 0.0
            }
        
        # Basic feedback for now
        return {
            "reps": self.reps,
            "feedback": "Glute Fly exercise - Full trainer coming soon",
            "angles": {},
            "progress": 0.0
        }

class WorkoutStreamManager:
    """Manages workout video streaming via WebSocket"""
    
    def __init__(self, exercise: str):
        self.exercise = exercise
        self.active = False
        self.trainer = None
        
    def get_trainer(self):
        """Initialize the appropriate trainer based on exercise type"""
        # Normalize exercise ID (handle variations like "push-ups" vs "pushup")
        exercise_lower = self.exercise.lower().replace("-", "").replace("_", "").replace(" ", "")
        
        if exercise_lower == "squat" or exercise_lower == "squats":
            return SquatTrainer()
        elif "pushup" in exercise_lower or "push" in exercise_lower:
            return PushupTrainer()
        elif "shoulder" in exercise_lower or "press" in exercise_lower:
            return ShoulderPressTrainer()
        elif "bicep" in exercise_lower or "curl" in exercise_lower:
            return BicepCurlTrainer()
        elif exercise_lower == "plank":
            return PlankTrainer()
        elif "row" in exercise_lower and "pull" not in exercise_lower:
            return RowTrainer()
        elif "pullup" in exercise_lower or "pull" in exercise_lower:
            return PullupTrainer()
        elif "lunge" in exercise_lower:
            return LungeTrainer()
        elif "crunch" in exercise_lower:
            return CrunchTrainer()
        elif "tricep" in exercise_lower or "dip" in exercise_lower:
            return TricepDipTrainer()
        elif "lateral" in exercise_lower or "raise" in exercise_lower:
            return LateralRaiseTrainer()
        elif exercise_lower == "glutefly" or exercise_lower == "glute" or "glute" in exercise_lower:
            # Glute Fly trainer wrapper
            try:
                return GluteFlyTrainer()
            except Exception as e:
                logger.error(f"Error initializing GluteFlyTrainer: {e}")
                raise ValueError(f"Glute Fly trainer not available: {e}")
        else:
            available = "squat, push-ups, shoulder-press, bicep-curl, plank, row, pull-up, lunge, crunch, tricep-dip, lateral-raise, glute-fly"
            raise ValueError(f"Unknown exercise: {self.exercise}. Available: {available}")
    
    async def stream_frames(self, websocket: WebSocket, camera_device: str = "auto"):
        """Stream video frames with pose detection"""
        self.active = True
        self.trainer = self.get_trainer()
        
        # Get camera index (auto-detect external webcam by default)
        from src.backend.core.camera_utils import get_camera_index
        camera_idx = get_camera_index(camera_device)
        
        logger.info(f"Using camera device: {camera_device} (index: {camera_idx})")
        
        cap = cv2.VideoCapture(camera_idx)
        if not cap.isOpened():
            await websocket.send_json({
                "type": "error",
                "message": f"Could not open webcam (index {camera_idx})"
            })
            return
        
        # Initialize MediaPipe
        import mediapipe as mp
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        
        with mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as pose:
            
            frame_count = 0
            
            while self.active:
                try:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # Flip frame for mirror effect
                    frame = cv2.flip(frame, 1)
                    h, w = frame.shape[:2]
                    
                    # Process with MediaPipe
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = pose.process(rgb)
                    
                    # Draw pose landmarks
                    if results.pose_landmarks:
                        mp_drawing.draw_landmarks(
                            frame,
                            results.pose_landmarks,
                            mp_pose.POSE_CONNECTIONS
                        )
                        
                        # Get trainer feedback (rep count, angles, corrections)
                        feedback = self.trainer.process_frame(results, w, h)
                    else:
                        feedback = {
                            "reps": 0,
                            "feedback": "No pose detected",
                            "angles": {}
                        }
                    
                    # Encode frame to JPEG
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    frame_b64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # Send frame data via WebSocket (throttle to ~30fps)
                    if frame_count % 1 == 0:  # Send every frame
                        await websocket.send_json({
                            "type": "frame",
                            "image": f"data:image/jpeg;base64,{frame_b64}",
                            "reps": feedback.get("reps", 0),
                            "feedback": feedback.get("feedback", ""),
                            "angles": feedback.get("angles", {}),
                            "progress": feedback.get("progress", 0.0)
                        })
                    
                    frame_count += 1
                    
                    # Small delay to prevent overwhelming the connection
                    await asyncio.sleep(0.033)  # ~30fps
                    
                except Exception as e:
                    logger.error(f"Error in stream: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
                    break
        
        cap.release()
        logger.info("Workout stream ended")

@router.websocket("/ws/workout")
async def workout_websocket(
    websocket: WebSocket,
    exercise: str = Query(..., description="Exercise type (squat, glute-fly, etc)"),
    camera: str = Query("auto", description="Camera device (auto, 0, 1, etc)")
):
    """
    WebSocket endpoint for real-time workout streaming
    
    Query Parameters:
    - exercise: Type of exercise to perform
    - camera: Camera device ID ("auto" for auto-detect external, or "0", "1", etc)
    
    Message Types:
    - frame: Video frame with pose detection
    - feedback: Real-time form corrections
    - rep: Rep count update
    - error: Error messages
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for exercise: {exercise}, camera: {camera}")
    
    manager = WorkoutStreamManager(exercise)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "exercise": exercise,
            "message": "Ready to start workout"
        })
        
        # Start streaming frames with camera selection
        await manager.stream_frames(websocket, camera_device=camera)
        
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        manager.active = False
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
    finally:
        manager.active = False
        try:
            await websocket.close()
        except:
            pass

