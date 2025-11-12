# Row Trainer (Back Exercise)
# Run: python -m src.backend.exercises.row_trainer

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
		voice.say(text, priority=priority, msg_type='row')

class RowTrainer:
	def __init__(self, use_enhanced_processor: bool = True) -> None:
		self.reps = 0
		self.direction = 0  # 0 = extended, 1 = pulled
		self.elbow_min_angle = 30.0   # target pulled angle (elbow bent)
		self.elbow_extended_angle = 160.0   # extended threshold (arm straight)
		self.last_guidance_time = time.time()
		self.last_feedback_time = 0.0
		self.feedback_cooldown = 2.0
		self.guidance_interval = 12
		self.calibrated = False
		self.current_feedback = ""
		
		self.use_enhanced = use_enhanced_processor and ENHANCED_PROCESSOR_AVAILABLE
		if self.use_enhanced:
			self.processor = EnhancedPoseProcessor(use_mediapipe=True)
			print("[RowTrainer] ✅ Using EnhancedPoseProcessor")
		else:
			self.processor = None

	def posture_guide(self) -> None:
		say("Row exercise start karne se pehle sahi posture set karo.")
		say("Stand straight, feet shoulder-width apart.")
		say("Arms ko front mein extend karo, elbows slightly bent.")
		say("Pull karte waqt elbows ko back le jao, squeeze shoulder blades.")
		say("Slow controlled movement karo.")

	def check_setup(self, results, w: int, h: int) -> bool:
		"""Check if row setup is correct"""
		if not results.pose_landmarks:
			return False
		return True  # Basic check

	def compute_elbow_angle(self, results, side: str, w: int, h: int) -> Optional[float]:
		"""Compute elbow angle (shoulder-elbow-wrist)"""
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
		
		if not self.calibrated:
			if self.check_setup(results, w, h):
				self.calibrated = True
				self.current_feedback = "Setup verified! Start rows"
			else:
				self.current_feedback = "Adjust position"
		
		elbow_angle = self.compute_elbow_angle(results, side, w, h)
		
		if elbow_angle is None:
			return {
				"reps": self.reps,
				"feedback": "Low confidence - adjust position",
				"angles": {},
				"progress": 0.0
			}
		
		# Check form
		now = time.time()
		if now - self.last_feedback_time > self.feedback_cooldown:
			# Check if shoulders are retracted (pulled back)
			L_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
			R_SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
			lsh = get_xy(results, L_SHOULDER, w, h)
			rsh = get_xy(results, R_SHOULDER, w, h)
			
			# Shoulders should move back when pulling
			# Simplified check
			pass
		
		# Rep detection (smaller angle = pulled back)
		if elbow_angle <= self.elbow_min_angle and self.direction == 0:
			self.direction = 1  # pulled back
			feedback_messages.append("Pull karo, squeeze shoulder blades")
		elif elbow_angle >= self.elbow_extended_angle and self.direction == 1:
			self.direction = 0  # extended
			self.reps += 1
			feedback_messages.append(f"Rep {self.reps} complete! Shabash!")
			say(f"Rep {self.reps} complete. Shabash!", 1.5)
		
		# Calculate progress
		progress = 0.0
		if elbow_angle < self.elbow_extended_angle:
			progress = 1.0 - (elbow_angle - self.elbow_min_angle) / (self.elbow_extended_angle - self.elbow_min_angle)
			progress = max(0.0, min(1.0, progress))
		
		if feedback_messages:
			self.current_feedback = " | ".join(feedback_messages)
		elif not self.current_feedback or now - self.last_feedback_time > 5.0:
			self.current_feedback = "Good form - keep going!"
		
		return {
			"reps": self.reps,
			"feedback": self.current_feedback,
			"angles": {
				"elbow": round(elbow_angle, 1) if elbow_angle is not None else None
			},
			"progress": round(progress, 2)
		}

	def run(self) -> None:
		cap = cv2.VideoCapture(0)
		if not cap.isOpened():
			print("❌ Could not open webcam.")
			return
		
		cv2.namedWindow("Row Trainer", cv2.WINDOW_NORMAL)
		side = 'left'
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
					elbow_angle = self.compute_elbow_angle(results, side, w, h)
					if elbow_angle is not None:
						cv2.putText(img, f"Elbow angle: {int(elbow_angle)}°", (10, 110), 
								   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
					cv2.putText(img, f"Reps: {self.reps}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
				
				cv2.imshow("Row Trainer", img)
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
	trainer = RowTrainer()
	trainer.run()


if __name__ == "__main__":
	main()

