# Plank Trainer (Core Exercise)
# Run: python -m src.backend.exercises.plank_trainer

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
		voice.say(text, priority=priority, msg_type='plank')

class PlankTrainer:
	def __init__(self, use_enhanced_processor: bool = True) -> None:
		self.reps = 0
		self.start_time = None
		self.hold_duration = 0.0  # seconds
		self.last_guidance_time = time.time()
		self.last_feedback_time = 0.0
		self.feedback_cooldown = 3.0  # Longer cooldown for plank
		self.guidance_interval = 15
		self.calibrated = False
		self.current_feedback = ""
		self.body_angle_threshold = 10.0
		
		self.use_enhanced = use_enhanced_processor and ENHANCED_PROCESSOR_AVAILABLE
		if self.use_enhanced:
			self.processor = EnhancedPoseProcessor(use_mediapipe=True)
			print("[PlankTrainer] ✅ Using EnhancedPoseProcessor")
		else:
			self.processor = None

	def posture_guide(self) -> None:
		say("Plank start karne se pehle sahi posture set karo.")
		say("Hands ko shoulder-width par rakho, directly under shoulders.")
		say("Body ko straight line mein rakho - head se heels tak.")
		say("Core tight rakho, hips ko upar ya neeche mat jane do.")
		say("Hold karo aur breathe normally.")

	def check_setup(self, results, w: int, h: int) -> bool:
		"""Check if plank setup is correct"""
		if not results.pose_landmarks:
			return False
		
		# Similar to push-up - body should be straight
		L_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
		L_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
		L_ANKLE = mp_pose.PoseLandmark.LEFT_ANKLE.value
		
		lsh = get_xy(results, L_SHOULDER, w, h)
		lhip = get_xy(results, L_HIP, w, h)
		lank = get_xy(results, L_ANKLE, w, h)
		
		# Body should be roughly straight
		body_angle = abs(lsh[1] - lank[1]) / w
		
		if body_angle > 0.3:
			say("Body ko straight line mein rakho.", 1.2)
			return False
		
		return True

	def compute_body_angle(self, results, w: int, h: int) -> Optional[float]:
		"""Compute body angle from horizontal"""
		if self.use_enhanced and self.processor:
			L_SHOULDER_IDX = mp_pose.PoseLandmark.LEFT_SHOULDER.value
			L_HIP_IDX = mp_pose.PoseLandmark.LEFT_HIP.value
			L_ANKLE_IDX = mp_pose.PoseLandmark.LEFT_ANKLE.value
			
			shoulder = self.processor.get_landmark_with_confidence(results, L_SHOULDER_IDX, w, h)
			hip = self.processor.get_landmark_with_confidence(results, L_HIP_IDX, w, h)
			ankle = self.processor.get_landmark_with_confidence(results, L_ANKLE_IDX, w, h)
			
			if not all([shoulder, hip, ankle]):
				return None
			
			shoulder_pt = (shoulder[0], shoulder[1])
			ankle_pt = (ankle[0], ankle[1])
			hip_pt = (hip[0], hip[1])
			
			return self.processor.compute_angle_enhanced(shoulder_pt, hip_pt, ankle_pt)
		else:
			L_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
			L_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
			L_ANKLE = mp_pose.PoseLandmark.LEFT_ANKLE.value
			
			lsh = get_xy(results, L_SHOULDER, w, h)
			lhip = get_xy(results, L_HIP, w, h)
			lank = get_xy(results, L_ANKLE, w, h)
			
			return angle_deg(lsh, lhip, lank)
	
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
				self.start_time = time.time()
				self.current_feedback = "Plank started! Hold the position"
			else:
				self.current_feedback = "Adjust position - body straight line"
		
		body_angle = self.compute_body_angle(results, w, h)
		
		# Calculate hold duration
		if self.start_time:
			self.hold_duration = time.time() - self.start_time
		
		# Check form
		now = time.time()
		if now - self.last_feedback_time > self.feedback_cooldown:
			if body_angle is not None and body_angle > self.body_angle_threshold:
				feedback_messages.append("Body ko straight line mein rakho")
				self.last_feedback_time = now
			
			# Check hip position
			L_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
			R_HIP = mp_pose.PoseLandmark.RIGHT_HIP.value
			L_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
			R_SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
			
			lhip = get_xy(results, L_HIP, w, h)
			rhip = get_xy(results, R_HIP, w, h)
			lsh = get_xy(results, L_SHOULDER, w, h)
			rsh = get_xy(results, R_SHOULDER, w, h)
			
			hip_y = (lhip[1] + rhip[1]) / 2.0
			shoulder_y = (lsh[1] + rsh[1]) / 2.0
			
			if hip_y > shoulder_y + 0.1 * h:
				feedback_messages.append("Hips ko upar rakho, core tight")
				self.last_feedback_time = now
			elif hip_y < shoulder_y - 0.1 * h:
				feedback_messages.append("Hips thoda neeche, balance karo")
				self.last_feedback_time = now
		
		# Time-based "reps" (every 10 seconds = 1 rep for tracking)
		if self.start_time and self.hold_duration > 0:
			new_reps = int(self.hold_duration / 10.0)  # 1 rep per 10 seconds
			if new_reps > self.reps:
				self.reps = new_reps
				say(f"Plank hold: {self.reps * 10} seconds. Shabash!", 2.0)
		
		# Progress based on time (for display)
		progress = min(1.0, self.hold_duration / 60.0)  # 60 seconds = 100%
		
		if feedback_messages:
			self.current_feedback = " | ".join(feedback_messages)
		elif not self.current_feedback or now - self.last_feedback_time > 5.0:
			if self.hold_duration > 0:
				self.current_feedback = f"Good form! Hold: {int(self.hold_duration)}s"
			else:
				self.current_feedback = "Hold the position!"
		
		return {
			"reps": self.reps,
			"feedback": self.current_feedback,
			"angles": {
				"body": round(body_angle, 1) if body_angle is not None else None
			},
			"progress": round(progress, 2),
			"duration": round(self.hold_duration, 1)
		}

	def run(self) -> None:
		cap = cv2.VideoCapture(0)
		if not cap.isOpened():
			print("❌ Could not open webcam.")
			return
		
		cv2.namedWindow("Plank Trainer", cv2.WINDOW_NORMAL)
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
					body_angle = self.compute_body_angle(results, w, h)
					if body_angle is not None:
						cv2.putText(img, f"Body angle: {int(body_angle)}°", (10, 110), 
								   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
					
					if self.hold_duration > 0:
						cv2.putText(img, f"Hold: {int(self.hold_duration)}s", (10, 40), 
								   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
				
				cv2.imshow("Plank Trainer", img)
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
	trainer = PlankTrainer()
	trainer.run()


if __name__ == "__main__":
	main()

