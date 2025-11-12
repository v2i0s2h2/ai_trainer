# Lunge Trainer (Legs Exercise)
# Run: python -m src.backend.exercises.lunge_trainer

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
		voice.say(text, priority=priority, msg_type='lunge')

class LungeTrainer:
	def __init__(self, use_enhanced_processor: bool = True) -> None:
		self.reps = 0
		self.direction = 0  # 0 = standing, 1 = lunged
		self.knee_min_angle = 70.0   # target bottom angle (lunge position)
		self.knee_up_angle = 160.0   # standing threshold
		self.last_guidance_time = time.time()
		self.last_feedback_time = 0.0
		self.feedback_cooldown = 2.0
		self.guidance_interval = 12
		self.calibrated = False
		self.current_feedback = ""
		self.current_side = 'left'  # Track which leg is forward
		
		self.use_enhanced = use_enhanced_processor and ENHANCED_PROCESSOR_AVAILABLE
		if self.use_enhanced:
			self.processor = EnhancedPoseProcessor(use_mediapipe=True)
			print("[LungeTrainer] ✅ Using EnhancedPoseProcessor")
		else:
			self.processor = None

	def posture_guide(self) -> None:
		say("Lunge start karne se pehle sahi posture set karo.")
		say("Stand straight, feet hip-width apart.")
		say("Ek leg aage rakho, dusri leg piche.")
		say("Front knee ko 90 degrees tak bend karo.")
		say("Back knee ko ground ke close rakho but touch mat karo.")
		say("Torso upright rakho, core tight.")

	def check_setup(self, results, w: int, h: int) -> bool:
		"""Check if lunge setup is correct"""
		if not results.pose_landmarks:
			return False
		return True  # Basic check

	def compute_knee_angle(self, results, side: str, w: int, h: int) -> Optional[float]:
		"""Compute knee angle (hip-knee-ankle)"""
		if self.use_enhanced and self.processor:
			landmarks = self.processor.get_key_landmarks(results, w, h, side)
			angle = self.processor.compute_knee_angle_enhanced(landmarks)
			return angle
		else:
			if side == 'left':
				HIP = mp_pose.PoseLandmark.LEFT_HIP.value
				KNEE = mp_pose.PoseLandmark.LEFT_KNEE.value
				ANKLE = mp_pose.PoseLandmark.LEFT_ANKLE.value
			else:
				HIP = mp_pose.PoseLandmark.RIGHT_HIP.value
				KNEE = mp_pose.PoseLandmark.RIGHT_KNEE.value
				ANKLE = mp_pose.PoseLandmark.RIGHT_ANKLE.value
			
			hip = get_xy(results, HIP, w, h)
			knee = get_xy(results, KNEE, w, h)
			ankle = get_xy(results, ANKLE, w, h)
			return angle_deg(hip, knee, ankle)
	
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
				self.current_feedback = "Setup verified! Start lunges"
			else:
				self.current_feedback = "Adjust position"
		
		# Detect which leg is forward (front knee lower)
		L_KNEE = mp_pose.PoseLandmark.LEFT_KNEE.value
		R_KNEE = mp_pose.PoseLandmark.RIGHT_KNEE.value
		lknee = get_xy(results, L_KNEE, w, h)
		rknee = get_xy(results, R_KNEE, w, h)
		
		# Front leg has lower knee (higher y value)
		if lknee[1] > rknee[1]:
			front_leg = 'left'
		else:
			front_leg = 'right'
		
		# Compute angle for front leg
		knee_angle = self.compute_knee_angle(results, front_leg, w, h)
		
		if knee_angle is None:
			return {
				"reps": self.reps,
				"feedback": "Low confidence - adjust position",
				"angles": {},
				"progress": 0.0
			}
		
		# Check form
		now = time.time()
		if now - self.last_feedback_time > self.feedback_cooldown:
			# Check torso alignment
			L_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
			R_SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
			L_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
			R_HIP = mp_pose.PoseLandmark.RIGHT_HIP.value
			
			lsh = get_xy(results, L_SHOULDER, w, h)
			rsh = get_xy(results, R_SHOULDER, w, h)
			lhip = get_xy(results, L_HIP, w, h)
			rhip = get_xy(results, R_HIP, w, h)
			
			shoulder_y = (lsh[1] + rsh[1]) / 2.0
			hip_y = (lhip[1] + rhip[1]) / 2.0
			
			# Torso should be upright
			if abs(shoulder_y - hip_y) < 0.05 * h:
				feedback_messages.append("Torso upright rakho, forward lean mat karo")
				self.last_feedback_time = now
		
		# Rep detection
		if knee_angle <= self.knee_min_angle and self.direction == 0:
			self.direction = 1  # lunged down
			feedback_messages.append("Neeche jao, control ke saath")
		elif knee_angle >= self.knee_up_angle and self.direction == 1:
			self.direction = 0  # back up
			self.reps += 1
			feedback_messages.append(f"Rep {self.reps} complete! Shabash!")
			say(f"Rep {self.reps} complete. Shabash!", 1.5)
		
		# Calculate progress
		progress = 0.0
		if knee_angle < self.knee_up_angle:
			progress = 1.0 - (knee_angle - self.knee_min_angle) / (self.knee_up_angle - self.knee_min_angle)
			progress = max(0.0, min(1.0, progress))
		
		if feedback_messages:
			self.current_feedback = " | ".join(feedback_messages)
		elif not self.current_feedback or now - self.last_feedback_time > 5.0:
			self.current_feedback = f"Good form - {front_leg} leg forward"
		
		return {
			"reps": self.reps,
			"feedback": self.current_feedback,
			"angles": {
				"knee": round(knee_angle, 1) if knee_angle is not None else None
			},
			"progress": round(progress, 2)
		}

	def run(self) -> None:
		cap = cv2.VideoCapture(0)
		if not cap.isOpened():
			print("❌ Could not open webcam.")
			return
		
		cv2.namedWindow("Lunge Trainer", cv2.WINDOW_NORMAL)
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
					knee_angle = self.compute_knee_angle(results, 'left', w, h)
					if knee_angle is not None:
						cv2.putText(img, f"Knee angle: {int(knee_angle)}°", (10, 110), 
								   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
					cv2.putText(img, f"Reps: {self.reps}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
				
				cv2.imshow("Lunge Trainer", img)
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
	trainer = LungeTrainer()
	trainer.run()


if __name__ == "__main__":
	main()

