"""
Enhanced Pose Processing Module
Improves accuracy by:
1. Landmark confidence checking
2. Temporal smoothing (Kalman filter / exponential moving average)
3. OpenCV DNN support as alternative to MediaPipe
4. Better angle calculations with biomechanics
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Tuple, Optional, List
from collections import deque
import time

class LandmarkSmoother:
    """Smooth landmarks using exponential moving average"""
    def __init__(self, alpha=0.3, history_size=5):
        self.alpha = alpha
        self.history = {}
        self.history_size = history_size
        
    def smooth_landmark(self, landmark_idx: int, x: float, y: float, z: float, 
                       visibility: float) -> Tuple[float, float, float]:
        """Smooth a single landmark"""
        if landmark_idx not in self.history:
            self.history[landmark_idx] = deque(maxlen=self.history_size)
        
        # Only use if visibility is good
        if visibility < 0.5:
            # Use last known good value
            if len(self.history[landmark_idx]) > 0:
                return self.history[landmark_idx][-1]
            else:
                return (x, y, z)
        
        # Add to history
        self.history[landmark_idx].append((x, y, z))
        
        # Exponential moving average
        if len(self.history[landmark_idx]) == 1:
            return (x, y, z)
        
        smoothed = list(self.history[landmark_idx][-1])
        for i in range(len(self.history[landmark_idx]) - 2, -1, -1):
            prev = self.history[landmark_idx][i]
            smoothed[0] = self.alpha * smoothed[0] + (1 - self.alpha) * prev[0]
            smoothed[1] = self.alpha * smoothed[1] + (1 - self.alpha) * prev[1]
            smoothed[2] = self.alpha * smoothed[2] + (1 - self.alpha) * prev[2]
        
        return tuple(smoothed)
    
    def reset(self):
        """Reset smoothing history"""
        self.history.clear()


class EnhancedPoseProcessor:
    """
    Enhanced pose processing with confidence checking and smoothing
    """
    def __init__(self, use_mediapipe=True, use_opencv_dnn=False):
        self.use_mediapipe = use_mediapipe
        self.use_opencv_dnn = use_opencv_dnn
        self.smoother = LandmarkSmoother(alpha=0.3)
        
        # MediaPipe setup
        if use_mediapipe:
            self.mp_pose = mp.solutions.pose
            self.mp_drawing = mp.solutions.drawing_utils
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=2,  # Higher complexity for better accuracy
                enable_segmentation=False,
                smooth_landmarks=True,  # MediaPipe's built-in smoothing
                min_detection_confidence=0.7,  # Higher threshold
                min_tracking_confidence=0.7
            )
        
        # OpenCV DNN setup (optional)
        if use_opencv_dnn:
            self.setup_opencv_dnn()
        
        # Confidence thresholds
        self.min_visibility = 0.5
        self.min_presence = 0.5
        
    def setup_opencv_dnn(self):
        """Setup OpenCV DNN for pose estimation (optional)"""
        # Note: You'll need to download a pose estimation model
        # Example: OpenPose, MoveNet, etc.
        # For now, this is a placeholder
        self.dnn_net = None
        self.dnn_input_size = (368, 368)  # Common input size for pose models
        print("[POSE PROCESSOR] OpenCV DNN setup - model loading required")
    
    def check_landmark_confidence(self, landmark) -> bool:
        """Check if landmark has sufficient confidence"""
        # MediaPipe landmarks have visibility attribute
        if hasattr(landmark, 'visibility'):
            return landmark.visibility >= self.min_visibility
        if hasattr(landmark, 'presence'):
            return landmark.presence >= self.min_presence
        return True  # Default to true if no confidence metric
    
    def get_landmark_with_confidence(self, results, idx: int, w: int, h: int) -> Optional[Tuple[float, float, float, float]]:
        """
        Get landmark coordinates with confidence checking
        Returns: (x, y, z, visibility) or None if low confidence
        """
        if not results.pose_landmarks:
            return None
        
        landmark = results.pose_landmarks.landmark[idx]
        
        # Check confidence
        if not self.check_landmark_confidence(landmark):
            return None
        
        visibility = getattr(landmark, 'visibility', 1.0)
        presence = getattr(landmark, 'presence', 1.0)
        confidence = min(visibility, presence)
        
        # Convert to pixel coordinates
        x = landmark.x * w
        y = landmark.y * h
        z = landmark.z * w  # z is normalized by width
        
        # Apply smoothing
        x, y, z = self.smoother.smooth_landmark(idx, x, y, z, confidence)
        
        return (x, y, z, confidence)
    
    def process_frame_mediapipe(self, frame: np.ndarray):
        """Process frame with MediaPipe"""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        return results.pose_landmarks if results.pose_landmarks else None
    
    def compute_angle_enhanced(self, point1: Tuple[float, float], 
                             point2: Tuple[float, float], 
                             point3: Tuple[float, float]) -> float:
        """
        Enhanced angle calculation with better precision
        Returns angle in degrees (0-180)
        """
        p1 = np.array(point1[:2], dtype=float)  # Only use x, y
        p2 = np.array(point2[:2], dtype=float)
        p3 = np.array(point3[:2], dtype=float)
        
        # Calculate vectors
        v1 = p1 - p2
        v2 = p3 - p2
        
        # Normalize
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 < 1e-8 or norm2 < 1e-8:
            return 0.0
        
        v1_norm = v1 / norm1
        v2_norm = v2 / norm2
        
        # Calculate angle
        cos_angle = np.clip(np.dot(v1_norm, v2_norm), -1.0, 1.0)
        angle = np.degrees(np.arccos(cos_angle))
        
        return float(angle)
    
    def get_key_landmarks(self, results, w: int, h: int, side: str = 'left') -> Dict[str, Optional[Tuple[float, float, float, float]]]:
        """
        Get key landmarks with confidence checking
        Returns dict with landmark coordinates and confidence
        """
        landmarks = {}
        
        if not results.pose_landmarks:
            return landmarks
        
        # Define landmark indices based on side
        if side == 'left':
            indices = {
                'shoulder': self.mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                'hip': self.mp_pose.PoseLandmark.LEFT_HIP.value,
                'knee': self.mp_pose.PoseLandmark.LEFT_KNEE.value,
                'ankle': self.mp_pose.PoseLandmark.LEFT_ANKLE.value,
                'foot': self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value,
                'heel': self.mp_pose.PoseLandmark.LEFT_HEEL.value,
            }
        else:
            indices = {
                'shoulder': self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
                'hip': self.mp_pose.PoseLandmark.RIGHT_HIP.value,
                'knee': self.mp_pose.PoseLandmark.RIGHT_KNEE.value,
                'ankle': self.mp_pose.PoseLandmark.RIGHT_ANKLE.value,
                'foot': self.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value,
                'heel': self.mp_pose.PoseLandmark.RIGHT_HEEL.value,
            }
        
        # Get both sides for some landmarks
        indices['left_hip'] = self.mp_pose.PoseLandmark.LEFT_HIP.value
        indices['right_hip'] = self.mp_pose.PoseLandmark.RIGHT_HIP.value
        indices['left_shoulder'] = self.mp_pose.PoseLandmark.LEFT_SHOULDER.value
        indices['right_shoulder'] = self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value
        
        # Extract landmarks with confidence
        for name, idx in indices.items():
            landmarks[name] = self.get_landmark_with_confidence(results, idx, w, h)
        
        return landmarks
    
    def compute_knee_angle_enhanced(self, landmarks: Dict) -> Optional[float]:
        """Compute knee angle with confidence checking"""
        hip = landmarks.get('hip')
        knee = landmarks.get('knee')
        ankle = landmarks.get('ankle')
        
        if not all([hip, knee, ankle]):
            return None
        
        # Extract coordinates (x, y, confidence)
        hip_pt = (hip[0], hip[1])
        knee_pt = (knee[0], knee[1])
        ankle_pt = (ankle[0], ankle[1])
        
        return self.compute_angle_enhanced(hip_pt, knee_pt, ankle_pt)
    
    def compute_torso_angle_enhanced(self, landmarks: Dict) -> Optional[float]:
        """Compute torso angle from vertical with confidence checking"""
        left_shoulder = landmarks.get('left_shoulder')
        right_shoulder = landmarks.get('right_shoulder')
        left_hip = landmarks.get('left_hip')
        right_hip = landmarks.get('right_hip')
        
        if not all([left_shoulder, right_shoulder, left_hip, right_hip]):
            return None
        
        # Average shoulder and hip positions
        shoulder = ((left_shoulder[0] + right_shoulder[0]) / 2,
                   (left_shoulder[1] + right_shoulder[1]) / 2)
        hip = ((left_hip[0] + right_hip[0]) / 2,
              (left_hip[1] + right_hip[1]) / 2)
        
        # Vertical reference point
        vert = (hip[0], hip[1] + 100)
        
        return self.compute_angle_enhanced(shoulder, hip, vert)
    
    def validate_landmarks(self, landmarks: Dict, required: List[str]) -> bool:
        """Check if required landmarks are available with good confidence"""
        for key in required:
            if key not in landmarks or landmarks[key] is None:
                return False
            # Check confidence
            if len(landmarks[key]) > 3 and landmarks[key][3] < self.min_visibility:
                return False
        return True
    
    def reset(self):
        """Reset processor state"""
        self.smoother.reset()


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing Enhanced Pose Processor")
    print("=" * 60)
    
    processor = EnhancedPoseProcessor(use_mediapipe=True)
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam")
        exit(1)
    
    print("✅ Webcam opened")
    print("📹 Processing frames... (Press 'q' to quit)")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        h, w = frame.shape[:2]
        
        # Process with MediaPipe
        results = processor.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        if results.pose_landmarks:
            # Get enhanced landmarks
            landmarks = processor.get_key_landmarks(results, w, h, side='left')
            
            # Compute angles with confidence
            knee_angle = processor.compute_knee_angle_enhanced(landmarks)
            torso_angle = processor.compute_torso_angle_enhanced(landmarks)
            
            # Draw
            processor.mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, processor.mp_pose.POSE_CONNECTIONS
            )
            
            # Display info
            if knee_angle:
                cv2.putText(frame, f"Knee: {int(knee_angle)}°", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            if torso_angle:
                cv2.putText(frame, f"Torso: {int(torso_angle)}°", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Show confidence
            if landmarks.get('knee'):
                conf = landmarks['knee'][3]
                cv2.putText(frame, f"Conf: {conf:.2f}", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        cv2.imshow("Enhanced Pose Processor", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"✅ Processed {frame_count} frames")
    print("=" * 60)

