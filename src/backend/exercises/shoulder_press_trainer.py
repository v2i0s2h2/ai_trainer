# Shoulder Press Trainer
# Run: python -m src.backend.exercises.shoulder_press_trainer

import cv2
import cv2
import numpy as np
import time
from typing import Optional, Tuple, Dict, Any
import os

# Lazy load mediapipe to prevent hang at module load time
mp = None
mp_pose = None
mp_drawing = None

def get_mediapipe():
    """Lazy load mediapipe"""
    global mp, mp_pose, mp_drawing
    if mp is None:
        import mediapipe as _mp
        mp = _mp
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
    return mp, mp_pose, mp_drawing

try:
    # Skip voice on headless servers - check if display available
    if os.environ.get('DISPLAY') or os.name == 'nt':  # Has display or is Windows
        from src.backend.core.voice_feedback import VoiceSystem
        voice = VoiceSystem()
        VOICE_ENABLED = True
    else:
        VOICE_ENABLED = False
        print("[ShoulderPressTrainer] Voice disabled - no display available (server mode)")
except Exception as e:
    VOICE_ENABLED = False
    print(f"[ShoulderPressTrainer] Voice disabled: {e}")

# Import enhanced pose processor - skip on headless servers
ENHANCED_PROCESSOR_AVAILABLE = False
if os.environ.get('DISPLAY') or os.name == 'nt':
    try:
        from src.backend.core.pose_processor import EnhancedPoseProcessor
        ENHANCED_PROCESSOR_AVAILABLE = True
    except ImportError:
        print("[WARNING] EnhancedPoseProcessor not available, using basic processing")
else:
    print("[ShoulderPressTrainer] EnhancedPoseProcessor disabled - server mode (no display)")

# Legacy functions for backward compatibility
def get_xy(results, idx, w, h):
	lm = results.pose_landmarks.landmark[idx]
	return (lm.x * w, lm.y * h)


def angle_deg(a, b, c) -> float:
	pa = np.array(a, dtype=float)
	pb = np.array(b, dtype=float)
	pc = np.array(c, dtype=float)
	v1 = pa - pb
	v2 = pc - pb
	n1 = v1 / (np.linalg.norm(v1) + 1e-8)
	n2 = v2 / (np.linalg.norm(v2) + 1e-8)
	cosang = float(np.clip(np.dot(n1, n2), -1.0, 1.0))
	return float(np.degrees(np.arccos(cosang)))


def say(text: str, min_interval: float = 1.8) -> None:
	if VOICE_ENABLED:
		priority = 'high' if min_interval <= 1.0 else ('normal' if min_interval <= 2.0 else 'low')
		voice.say(text, priority=priority, msg_type='shoulder')


class ShoulderPressTrainer:
	def __init__(self, use_enhanced_processor: bool = True) -> None:
		self.reps = 0
		self.direction = 0  # 0 = up, 1 = down (for hysteresis)
		self.shoulder_min_angle = 60.0   # target bottom angle (arms down)
		self.shoulder_up_angle = 160.0   # top threshold (arms up)
		self.last_guidance_time = time.time()
		self.last_feedback_time = 0.0
		self.feedback_cooldown = 2.0
		self.guidance_interval = 12
		self.calibrated = False
		self.current_feedback = ""
		
		# Initialize enhanced pose processor if available
		self.use_enhanced = use_enhanced_processor and ENHANCED_PROCESSOR_AVAILABLE
		if self.use_enhanced:
			self.processor = EnhancedPoseProcessor(use_mediapipe=True)
			print("[ShoulderPressTrainer] ✅ Using EnhancedPoseProcessor")
		else:
			self.processor = None
			if use_enhanced_processor:
				print("[ShoulderPressTrainer] ⚠️ EnhancedPoseProcessor not available")

	def posture_guide(self) -> None:
		say("Shoulder press start karne se pehle sahi posture set karo.")
		say("Feet ko shoulder-width par rakho, core tight.")
		say("Arms ko sides mein rakho, elbows slightly bent.")
		say("Slow controlled movement karo, dono arms simultaneously.")

	def check_setup(self, results, w: int, h: int) -> bool:
		"""Check if shoulder press setup is correct"""
		if not results.pose_landmarks:
			return False
		
		# Check if standing upright
		_, mp_pose, _ = get_mediapipe()
		L_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
		R_SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
		L_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
		R_HIP = mp_pose.PoseLandmark.RIGHT_HIP.value
		
		lsh = get_xy(results, L_SHOULDER, w, h)
		rsh = get_xy(results, R_SHOULDER, w, h)
		lhip = get_xy(results, L_HIP, w, h)
		rhip = get_xy(results, R_HIP, w, h)
		
		# Shoulders should be above hips (standing position)
		shoulder_y = (lsh[1] + rsh[1]) / 2.0
		hip_y = (lhip[1] + rhip[1]) / 2.0
		
		if shoulder_y > hip_y:  # Shoulders below hips (wrong)
			say("Stand straight, shoulders ko upar rakho.", 1.2)
			return False
		
		return True

	def compute_shoulder_angle(self, results, side: str, w: int, h: int) -> Optional[float]:
		"""Compute shoulder angle (shoulder-elbow-wrist)"""
		if self.use_enhanced and self.processor:
			if side == 'left':
				SHOULDER_IDX = mp_pose.PoseLandmark.LEFT_SHOULDER.value
				ELBOW_IDX = mp_pose.PoseLandmark.LEFT_ELBOW.value
				WRIST_IDX = mp_pose.PoseLandmark.LEFT_WRIST.value
			else:
				SHOULDER_IDX = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
				ELBOW_IDX = mp_pose.PoseLandmark.RIGHT_ELBOW.value
				WRIST_IDX = mp_pose.PoseLandmark.RIGHT_WRIST.value
			
			shoulder = self.processor.get_landmark_with_confidence(results, SHOULDER_IDX, w, h)
			elbow = self.processor.get_landmark_with_confidence(results, ELBOW_IDX, w, h)
			wrist = self.processor.get_landmark_with_confidence(results, WRIST_IDX, w, h)
			
			if not all([shoulder, elbow, wrist]):
				return None
			
			shoulder_pt = (shoulder[0], shoulder[1])
			elbow_pt = (elbow[0], elbow[1])
			wrist_pt = (wrist[0], wrist[1])
			
			return self.processor.compute_angle_enhanced(shoulder_pt, elbow_pt, wrist_pt)
		else:
			_, mp_pose, _ = get_mediapipe()
			if side == 'left':
				SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
				ELBOW = mp_pose.PoseLandmark.LEFT_ELBOW.value
				WRIST = mp_pose.PoseLandmark.LEFT_WRIST.value
			else:
				SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
				ELBOW = mp_pose.PoseLandmark.RIGHT_ELBOW.value
				WRIST = mp_pose.PoseLandmark.RIGHT_WRIST.value
			
			shoulder = get_xy(results, SHOULDER, w, h)
			elbow = get_xy(results, ELBOW, w, h)
			wrist = get_xy(results, WRIST, w, h)
			return angle_deg(shoulder, elbow, wrist)
	
	def process_frame(self, results, w: int, h: int, side: str = 'left') -> Dict[str, Any]:
		"""Process a single frame for API/WebSocket use"""
		feedback_messages = []
		
		if not results.pose_landmarks:
			return {
				"reps": self.reps,
				"feedback": "No pose detected - step into frame",
				"angles": {},
				"progress": 0.0
			}
		
		# Auto-calibrate if not done
		if not self.calibrated:
			if self.check_setup(results, w, h):
				self.calibrated = True
				self.current_feedback = "Setup verified! Start shoulder press"
			else:
				self.current_feedback = "Adjust position - stand straight"
		
		# Compute angles
		shoulder_angle = self.compute_shoulder_angle(results, side, w, h)
		
		if shoulder_angle is None:
			return {
				"reps": self.reps,
				"feedback": "Low confidence - adjust position",
				"angles": {},
				"progress": 0.0
			}
		
		# Check form
		now = time.time()
		if now - self.last_feedback_time > self.feedback_cooldown:
			# Check if both arms moving together
			_, mp_pose, _ = get_mediapipe()
			L_WRIST = mp_pose.PoseLandmark.LEFT_WRIST.value
			R_WRIST = mp_pose.PoseLandmark.RIGHT_WRIST.value
			lwrist = get_xy(results, L_WRIST, w, h)
			rwrist = get_xy(results, R_WRIST, w, h)
			
			# Check symmetry
			height_diff = abs(lwrist[1] - rwrist[1]) / h
			if height_diff > 0.15:  # More than 15% difference
				feedback_messages.append("Dono arms ko same level par rakho")
				self.last_feedback_time = now
		
		# Rep detection
		if shoulder_angle <= self.shoulder_min_angle and self.direction == 0:
			self.direction = 1  # going up
			feedback_messages.append("Upar jao, control ke saath")
		elif shoulder_angle >= self.shoulder_up_angle and self.direction == 1:
			self.direction = 0  # back down
			self.reps += 1
			feedback_messages.append(f"Rep {self.reps} complete! Shabash!")
			say(f"Rep {self.reps} complete. Shabash!", 1.5)
		
		# Calculate progress
		progress = 0.0
		if shoulder_angle < self.shoulder_up_angle:
			progress = 1.0 - (shoulder_angle - self.shoulder_min_angle) / (self.shoulder_up_angle - self.shoulder_min_angle)
			progress = max(0.0, min(1.0, progress))
		
		if feedback_messages:
			self.current_feedback = " | ".join(feedback_messages)
		elif not self.current_feedback or now - self.last_feedback_time > 5.0:
			self.current_feedback = "Good form - keep going!"
		
		return {
			"reps": self.reps,
			"feedback": self.current_feedback,
			"angles": {
				"shoulder": round(shoulder_angle, 1) if shoulder_angle is not None else None
			},
			"progress": round(progress, 2)
		}

	def run(self) -> None:
		cap = cv2.VideoCapture(0)
		if not cap.isOpened():
			print("❌ Could not open webcam.")
			return
		
		cv2.namedWindow("Shoulder Press Trainer", cv2.WINDOW_NORMAL)
		side = 'left'
		self.posture_guide()
		
		pose_context = None
		if self.use_enhanced and self.processor:
			pose = self.processor.pose
		else:
			# Lazy load mediapipe
			_, mp_pose, mp_drawing = get_mediapipe()
			
			pose_context = mp_pose.Pose(
				static_image_mode=False,
				model_complexity=1,
				enable_segmentation=False,
				min_detection_confidence=0.5,
				min_tracking_confidence=0.5
			)
			pose = pose_context.__enter__()
		
		try:
			while True:
				ok, frame = cap.read()
				if not ok:
					continue
				
				h, w = frame.shape[:2]
				rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
				results = pose.process(rgb)
				img = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
				
				if results.pose_landmarks:
					mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
					
					shoulder_angle = self.compute_shoulder_angle(results, side, w, h)
					if shoulder_angle is not None:
						cv2.putText(img, f"Shoulder angle: {int(shoulder_angle)}°", (10, 110), 
								   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
					
					cv2.putText(img, f"Reps: {self.reps}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
				
				cv2.imshow("Shoulder Press Trainer", img)
				if cv2.waitKey(1) & 0xFF == ord('q'):
					break
		finally:
			if not self.use_enhanced and pose_context:
				try:
					pose_context.__exit__(None, None, None)
				except:
					pass
			if self.use_enhanced and self.processor:
				self.processor.reset()
		
		cap.release()
		cv2.destroyAllWindows()


def main() -> None:
	trainer = ShoulderPressTrainer()
	trainer.run()


if __name__ == "__main__":
	main()

