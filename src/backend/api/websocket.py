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

class WorkoutStreamManager:
    """Manages workout video streaming via WebSocket"""
    
    def __init__(self, exercise: str):
        self.exercise = exercise
        self.active = False
        self.trainer = None
        
    def get_trainer(self):
        """Initialize the appropriate trainer based on exercise type"""
        if self.exercise == "squat":
            return SquatTrainer()
        # Add more trainers as needed
        else:
            raise ValueError(f"Unknown exercise: {self.exercise}")
    
    async def stream_frames(self, websocket: WebSocket):
        """Stream video frames with pose detection"""
        self.active = True
        self.trainer = self.get_trainer()
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            await websocket.send_json({
                "type": "error",
                "message": "Could not open webcam"
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
    exercise: str = Query(..., description="Exercise type (squat, glute-fly, etc)")
):
    """
    WebSocket endpoint for real-time workout streaming
    
    Query Parameters:
    - exercise: Type of exercise to perform
    
    Message Types:
    - frame: Video frame with pose detection
    - feedback: Real-time form corrections
    - rep: Rep count update
    - error: Error messages
    """
    await websocket.accept()
    logger.info(f"WebSocket connected for exercise: {exercise}")
    
    manager = WorkoutStreamManager(exercise)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "exercise": exercise,
            "message": "Ready to start workout"
        })
        
        # Start streaming frames
        await manager.stream_frames(websocket)
        
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

