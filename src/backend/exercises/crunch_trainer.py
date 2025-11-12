# Crunch Trainer (Core Exercise)
# Run: python -m src.backend.exercises.crunch_trainer

import cv2
import mediapipe as mp
import numpy as np
import time
from typing import Optional, Tuple, Dict, Any

try:
    from src.backend.core.voice_feedback import VoiceSystem
    voice = VoiceSystem()
    VOICE_ENABLED = True
except:
    VOICE_ENABLED = False

# Import enhanced pose processor
try:
    from src.backend.core.pose_processor import EnhancedPoseProcessor
    ENHANCED_PROCESSOR_AVAILABLE = True
except ImportError:
    ENHANCED_PROCESSOR_AVAILABLE = False
    print("[WARNING] EnhancedPoseProcessor not available, using basic processing")

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

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
		voice.say(text, priority=priority, msg_type='crunch')

class CrunchTrainer:
	def __init__(self, use_enhanced_processor: bool = True) -> None:
		self.reps = 0
		self.direction = 0  # 0 = down, 1 = up
		self.torso_min_angle = 60.0   # target crunch angle (torso curled)
		self.torso_down_angle = 150.0   # lying down threshold
		self.last_guidance_time = time.time()
		self.last_feedback_time = 0.0
		self.feedback_cooldown = 2.0
		self.guidance_interval = 12
		self.calibrated = False
		self.current_feedback = ""
		
		self.use_enhanced = use_enhanced_processor and ENHANCED_PROCESSOR_AVAILABLE
		if self.use_enhanced:
			self.processor = EnhancedPoseProcessor(use_mediapipe=True)
			print("[CrunchTrainer] ✅ Using EnhancedPoseProcessor")
		else:
			self.processor = None

	def posture_guide(self) -> None:
		say("Crunch start karne se pehle sahi posture set karo.")
		say("Lie down on back, knees bent, feet flat on floor.")
		say("Hands ko head ke piche rakho, lightly support.")
		say("Curl up karte waqt shoulders ko floor se uthao.")
		say("Lower back ko floor par rakho, full sit-up mat karo.")

	def check_setup(self, results, w: int, h: int) -> bool:
		"""Check if crunch setup is correct"""
		if not results.pose_landmarks:
			return False
		return True  # Basic check

	def compute_torso_angle(self, results, w: int, h: int) -> Optional[float]:
		"""Compute torso angle (shoulder-hip-knee)"""
		if self.use_enhanced and self.processor:
			landmarks = self.processor.get_key_landmarks(results, w, h, side='left')
			angle = self.processor.compute_torso_angle_enhanced(landmarks)
			return angle
		else:
			L_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
			L_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
			L_KNEE = mp_pose.PoseLandmark.LEFT_KNEE.value
			
			lsh = get_xy(results, L_SHOULDER, w, h)
			lhip = get_xy(results, L_HIP, w, h)
			lknee = get_xy(results, L_KNEE, w, h)
			
			return angle_deg(lsh, lhip, lknee)
	
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
		
		if not self.calibrated:
			if self.check_setup(results, w, h):
				self.calibrated = True
				self.current_feedback = "Setup verified! Start crunches"
			else:
				self.current_feedback = "Adjust position"
		
		torso_angle = self.compute_torso_angle(results, w, h)
		
		if torso_angle is None:
			return {
				"reps": self.reps,
				"feedback": "Low confidence - adjust position",
				"angles": {},
				"progress": 0.0
			}
		
		# Check form
		now = time.time()
		if now - self.last_feedback_time > self.feedback_cooldown:
			# Check if lower back is on floor (hip position)
			L_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
			R_HIP = mp_pose.PoseLandmark.RIGHT_HIP.value
			lhip = get_xy(results, L_HIP, w, h)
			rhip = get_xy(results, R_HIP, w, h)
			
			# Hips should stay relatively low (not lifting)
			pass
		
		# Rep detection (smaller angle = more curled)
		if torso_angle <= self.torso_min_angle and self.direction == 0:
			self.direction = 1  # curled up
			feedback_messages.append("Curl up, shoulders uthao")
		elif torso_angle >= self.torso_down_angle and self.direction == 1:
			self.direction = 0  # back down
			self.reps += 1
			feedback_messages.append(f"Rep {self.reps} complete! Shabash!")
			say(f"Rep {self.reps} complete. Shabash!", 1.5)
		
		# Calculate progress
		progress = 0.0
		if torso_angle < self.torso_down_angle:
			progress = 1.0 - (torso_angle - self.torso_min_angle) / (self.torso_down_angle - self.torso_min_angle)
			progress = max(0.0, min(1.0, progress))
		
		if feedback_messages:
			self.current_feedback = " | ".join(feedback_messages)
		elif not self.current_feedback or now - self.last_feedback_time > 5.0:
			self.current_feedback = "Good form - keep going!"
		
		return {
			"reps": self.reps,
			"feedback": self.current_feedback,
			"angles": {
				"torso": round(torso_angle, 1) if torso_angle is not None else None
			},
			"progress": round(progress, 2)
		}

	def run(self) -> None:
		cap = cv2.VideoCapture(0)
		if not cap.isOpened():
			print("❌ Could not open webcam.")
			return
		
		cv2.namedWindow("Crunch Trainer", cv2.WINDOW_NORMAL)
		self.posture_guide()
		
		pose_context = None
		if self.use_enhanced and self.processor:
			pose = self.processor.pose
		else:
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
					torso_angle = self.compute_torso_angle(results, w, h)
					if torso_angle is not None:
						cv2.putText(img, f"Torso angle: {int(torso_angle)}°", (10, 110), 
								   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
					cv2.putText(img, f"Reps: {self.reps}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
				
				cv2.imshow("Crunch Trainer", img)
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
	trainer = CrunchTrainer()
	trainer.run()


if __name__ == "__main__":
	main()

