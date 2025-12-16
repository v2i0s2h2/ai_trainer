# Lateral Raise Trainer (Shoulders Exercise)
# Run: python -m src.backend.exercises.lateral_raise_trainer

import cv2
import numpy as np
import time
from typing import Optional, Tuple, Dict, Any

# Lazy import mediapipe to prevent hang at module load time
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
    import os
    if os.environ.get('DISPLAY') or os.name == 'nt':  # Has display or is Windows
        from src.backend.core.voice_feedback import VoiceSystem
        voice = VoiceSystem()
        VOICE_ENABLED = True
    else:
        VOICE_ENABLED = False
        print("[LateralRaiseTrainer] Voice disabled - no display available (server mode)")
except Exception as e:
    VOICE_ENABLED = False
    print(f"[LateralRaiseTrainer] Voice disabled: {e}")

# Import enhanced pose processor - skip on headless servers
# EnhancedPoseProcessor imports mediapipe at module level which hangs on VPS
import os
ENHANCED_PROCESSOR_AVAILABLE = False
if os.environ.get('DISPLAY') or os.name == 'nt':  # Has display or Windows
    try:
        from src.backend.core.pose_processor import EnhancedPoseProcessor
        ENHANCED_PROCESSOR_AVAILABLE = True
    except ImportError:
        print("[WARNING] EnhancedPoseProcessor not available, using basic processing")
else:
    print("[LateralRaiseTrainer] EnhancedPoseProcessor disabled - server mode (no display)")

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
		voice.say(text, priority=priority, msg_type='lateral')

class LateralRaiseTrainer:
	def __init__(self, use_enhanced_processor: bool = True) -> None:
		self.reps = 0
		self.direction = 0  # 0 = down, 1 = up
		self.shoulder_min_angle = 30.0   # target top angle (arms raised)
		self.shoulder_down_angle = 160.0   # bottom threshold (arms down)
		self.last_guidance_time = time.time()
		self.last_feedback_time = 0.0
		self.feedback_cooldown = 2.0
		self.guidance_interval = 12
		self.calibrated = False
		self.current_feedback = ""
		
		self.use_enhanced = use_enhanced_processor and ENHANCED_PROCESSOR_AVAILABLE
		if self.use_enhanced:
			self.processor = EnhancedPoseProcessor(use_mediapipe=True)
			print("[LateralRaiseTrainer] ✅ Using EnhancedPoseProcessor")
		else:
			self.processor = None

	def posture_guide(self) -> None:
		say("Lateral raise start karne se pehle sahi posture set karo.")
		say("Stand straight, arms ko sides mein rakho.")
		say("Elbows slightly bent rakho, weights ko sides se uthao.")
		say("Arms ko shoulder height tak uthao, parallel to floor.")
		say("Slow controlled movement karo, dono arms simultaneously.")

	def check_setup(self, results, w: int, h: int) -> bool:
		"""Check if lateral raise setup is correct"""
		if not results.pose_landmarks:
			return False
		return True  # Basic check

	def compute_shoulder_angle(self, results, side: str, w: int, h: int) -> Optional[float]:
		"""Compute shoulder angle (shoulder-elbow-wrist) - measures arm elevation"""
		_, mp_pose, _ = get_mediapipe()  # Lazy load mediapipe
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
				self.current_feedback = "Setup verified! Start lateral raises"
			else:
				self.current_feedback = "Adjust position"
		
		# For lateral raises, track wrist height relative to shoulder
		_, mp_pose, _ = get_mediapipe()  # Lazy load mediapipe
		L_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
		R_SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
		L_WRIST = mp_pose.PoseLandmark.LEFT_WRIST.value
		R_WRIST = mp_pose.PoseLandmark.RIGHT_WRIST.value
		
		lsh = get_xy(results, L_SHOULDER, w, h)
		rsh = get_xy(results, R_SHOULDER, w, h)
		lwrist = get_xy(results, L_WRIST, w, h)
		rwrist = get_xy(results, R_WRIST, w, h)
		
		# Calculate arm elevation (wrist height relative to shoulder)
		shoulder_y = (lsh[1] + rsh[1]) / 2.0
		wrist_y = (lwrist[1] + rwrist[1]) / 2.0
		elevation = (shoulder_y - wrist_y) / h  # Positive when wrists above shoulders
		
		# Check form
		now = time.time()
		if now - self.last_feedback_time > self.feedback_cooldown:
			# Check symmetry
			height_diff = abs(lwrist[1] - rwrist[1]) / h
			if height_diff > 0.15:
				feedback_messages.append("Dono arms ko same level par rakho")
				self.last_feedback_time = now
		
		# Rep detection based on elevation
		if elevation > 0.15 and self.direction == 0:  # Arms raised
			self.direction = 1  # up
			feedback_messages.append("Arms upar, shoulder height tak")
		elif elevation < -0.05 and self.direction == 1:  # Arms down
			self.direction = 0  # back down
			self.reps += 1
			feedback_messages.append(f"Rep {self.reps} complete! Shabash!")
			say(f"Rep {self.reps} complete. Shabash!", 1.5)
		
		# Calculate progress
		progress = max(0.0, min(1.0, (elevation + 0.05) / 0.2))
		
		if feedback_messages:
			self.current_feedback = " | ".join(feedback_messages)
		elif not self.current_feedback or now - self.last_feedback_time > 5.0:
			self.current_feedback = "Good form - keep going!"
		
		return {
			"reps": self.reps,
			"feedback": self.current_feedback,
			"angles": {
				"elevation": round(elevation * 100, 1)  # Percentage
			},
			"progress": round(progress, 2)
		}

	def run(self) -> None:
		_, mp_pose, mp_drawing = get_mediapipe()  # Lazy load mediapipe
		cap = cv2.VideoCapture(0)
		if not cap.isOpened():
			print("❌ Could not open webcam.")
			return
		
		cv2.namedWindow("Lateral Raise Trainer", cv2.WINDOW_NORMAL)
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
					cv2.putText(img, f"Reps: {self.reps}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
				
				cv2.imshow("Lateral Raise Trainer", img)
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
	trainer = LateralRaiseTrainer()
	trainer.run()


if __name__ == "__main__":
	main()

