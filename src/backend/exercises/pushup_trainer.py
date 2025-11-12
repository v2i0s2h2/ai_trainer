# Push-up Trainer
# Run: python -m src.backend.exercises.pushup_trainer

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
		voice.say(text, priority=priority, msg_type='pushup')


class PushupTrainer:
	def __init__(self, use_enhanced_processor: bool = True) -> None:
		self.reps = 0
		self.direction = 0  # 0 = up, 1 = down (for hysteresis)
		self.elbow_min_angle = 80.0   # target bottom angle (elbow bent)
		self.elbow_up_angle = 160.0   # top threshold (elbow straight)
		self.last_guidance_time = time.time()
		self.last_feedback_time = 0.0
		self.feedback_cooldown = 2.0  # seconds between feedback messages
		self.guidance_interval = 12
		self.calibrated = False
		self.current_feedback = ""  # Store current feedback message
		self.body_angle_threshold = 10.0  # Max deviation from straight line
		
		# Initialize enhanced pose processor if available
		self.use_enhanced = use_enhanced_processor and ENHANCED_PROCESSOR_AVAILABLE
		if self.use_enhanced:
			self.processor = EnhancedPoseProcessor(use_mediapipe=True)
			print("[PushupTrainer] ✅ Using EnhancedPoseProcessor for better accuracy")
		else:
			self.processor = None
			if use_enhanced_processor:
				print("[PushupTrainer] ⚠️ EnhancedPoseProcessor requested but not available, using basic processing")

	def posture_guide(self) -> None:
		say("Push-up start karne se pehle sahi posture set karo.")
		say("Hands ko shoulder-width par rakho, fingers forward.")
		say("Body ko straight line mein rakho - head se heels tak.")
		say("Core tight rakho, hips ko upar ya neeche mat jane do.")

	def check_setup(self, results, w: int, h: int) -> bool:
		"""Check if push-up setup is correct"""
		if not results.pose_landmarks:
			return False
		
		# Check if body is in push-up position (horizontal)
		L_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
		R_SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
		L_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
		R_HIP = mp_pose.PoseLandmark.RIGHT_HIP.value
		L_ANKLE = mp_pose.PoseLandmark.LEFT_ANKLE.value
		R_ANKLE = mp_pose.PoseLandmark.RIGHT_ANKLE.value
		
		lsh = get_xy(results, L_SHOULDER, w, h)
		rsh = get_xy(results, R_SHOULDER, w, h)
		lhip = get_xy(results, L_HIP, w, h)
		rhip = get_xy(results, R_HIP, w, h)
		lank = get_xy(results, L_ANKLE, w, h)
		rank = get_xy(results, R_ANKLE, w, h)
		
		# Check if body is roughly horizontal (shoulder-hip-ankle alignment)
		shoulder_y = (lsh[1] + rsh[1]) / 2.0
		hip_y = (lhip[1] + rhip[1]) / 2.0
		ankle_y = (lank[1] + rank[1]) / 2.0
		
		# Body should be roughly straight (y coordinates should be similar)
		body_angle = abs(shoulder_y - ankle_y) / w
		
		if body_angle > 0.3:  # Too much deviation
			say("Body ko straight line mein rakho - head se heels tak ek line.", 1.2)
			return False
		
		return True

	def compute_elbow_angle(self, results, side: str, w: int, h: int) -> Optional[float]:
		"""Compute elbow angle with enhanced processing if available"""
		if self.use_enhanced and self.processor:
			# Use enhanced processor with confidence checking
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
			# Fallback to basic calculation
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

	def compute_body_angle(self, results, w: int, h: int) -> Optional[float]:
		"""Compute body angle from horizontal (should be close to 0 for good form)"""
		if self.use_enhanced and self.processor:
			L_SHOULDER_IDX = mp_pose.PoseLandmark.LEFT_SHOULDER.value
			L_HIP_IDX = mp_pose.PoseLandmark.LEFT_HIP.value
			L_ANKLE_IDX = mp_pose.PoseLandmark.LEFT_ANKLE.value
			
			left_shoulder = self.processor.get_landmark_with_confidence(results, L_SHOULDER_IDX, w, h)
			left_hip = self.processor.get_landmark_with_confidence(results, L_HIP_IDX, w, h)
			left_ankle = self.processor.get_landmark_with_confidence(results, L_ANKLE_IDX, w, h)
			
			if not all([left_shoulder, left_hip, left_ankle]):
				return None
			
			# Calculate angle from horizontal
			shoulder_pt = (left_shoulder[0], left_shoulder[1])
			ankle_pt = (left_ankle[0], left_ankle[1])
			hip_pt = (left_hip[0], left_hip[1])
			
			# Angle between shoulder-ankle line and horizontal
			# For push-ups, body should be straight (angle close to 0)
			angle = self.processor.compute_angle_enhanced(shoulder_pt, hip_pt, ankle_pt)
			return angle
		else:
			# Basic calculation
			L_SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
			L_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
			L_ANKLE = mp_pose.PoseLandmark.LEFT_ANKLE.value
			
			lsh = get_xy(results, L_SHOULDER, w, h)
			lhip = get_xy(results, L_HIP, w, h)
			lank = get_xy(results, L_ANKLE, w, h)
			
			return angle_deg(lsh, lhip, lank)
	
	def process_frame(self, results, w: int, h: int, side: str = 'left') -> Dict[str, Any]:
		"""
		Process a single frame for API/WebSocket use
		Returns feedback dict with reps, angles, corrections
		"""
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
				self.current_feedback = "Setup verified! Start push-ups"
			else:
				self.current_feedback = "Adjust position - body straight line"
		
		# Compute angles (with enhanced processing if available)
		elbow_angle = self.compute_elbow_angle(results, side, w, h)
		body_angle = self.compute_body_angle(results, w, h)
		
		# Skip processing if angles are None (low confidence landmarks)
		if elbow_angle is None:
			return {
				"reps": self.reps,
				"feedback": "Low confidence - adjust position for better detection",
				"angles": {},
				"progress": 0.0
			}
		
		# Check form and provide corrections (with cooldown)
		now = time.time()
		if now - self.last_feedback_time > self.feedback_cooldown:
			# Check body alignment
			if body_angle is not None and body_angle > self.body_angle_threshold:
				feedback_messages.append("Body ko straight line mein rakho")
				self.last_feedback_time = now
			
			# Check if hips are sagging
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
			
			# Hips should not be lower than shoulders (sagging)
			if hip_y > shoulder_y + 0.1 * h:
				feedback_messages.append("Hips ko upar rakho, core tight")
				self.last_feedback_time = now
		
		# Rep detection using hysteresis on elbow angle
		if elbow_angle <= self.elbow_min_angle and self.direction == 0:
			self.direction = 1  # going down
			feedback_messages.append("Neeche jao, control ke saath")
		elif elbow_angle >= self.elbow_up_angle and self.direction == 1:
			self.direction = 0  # back up
			self.reps += 1
			feedback_messages.append(f"Rep {self.reps} complete! Shabash!")
			# Voice announcement for rep count
			say(f"Rep {self.reps} complete. Shabash!", 1.5)
		
		# Calculate progress (0-1 range based on elbow angle)
		progress = 0.0
		if elbow_angle < self.elbow_up_angle:
			progress = 1.0 - (elbow_angle - self.elbow_min_angle) / (self.elbow_up_angle - self.elbow_min_angle)
			progress = max(0.0, min(1.0, progress))
		
		# Update feedback if we have new messages
		if feedback_messages:
			self.current_feedback = " | ".join(feedback_messages)
		elif not self.current_feedback or now - self.last_feedback_time > 5.0:
			self.current_feedback = "Good form - keep going!"
		
		return {
			"reps": self.reps,
			"feedback": self.current_feedback,
			"angles": {
				"elbow": round(elbow_angle, 1) if elbow_angle is not None else None,
				"body": round(body_angle, 1) if body_angle is not None else None
			},
			"progress": round(progress, 2)
		}

	def run(self) -> None:
		cap = cv2.VideoCapture(0)
		if not cap.isOpened():
			print("❌ Could not open webcam.")
			return
		
		cv2.namedWindow("Push-up Trainer", cv2.WINDOW_NORMAL)
		cv2.setWindowProperty("Push-up Trainer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
		side = 'left'
		self.posture_guide()
		say("Ready? Start hone se pehle C press karke posture verify karo.")
		
		# Use enhanced processor's pose if available, otherwise use basic MediaPipe
		pose_context = None
		if self.use_enhanced and self.processor:
			# Enhanced processor's pose is already initialized
			pose = self.processor.pose
			# No context manager needed for enhanced processor
		else:
			# Use basic MediaPipe with context manager
			pose_context = mp_pose.Pose(
				static_image_mode=False,
				model_complexity=1,
				enable_segmentation=False,
				min_detection_confidence=0.5,
				min_tracking_confidence=0.5
			)
			pose = pose_context.__enter__()
		
		try:
			p_time = 0.0
			fps_prev = 0.0
			
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
					
					if not self.calibrated:
						if self.check_setup(results, w, h):
							self.calibrated = True
							say("Setup sahi hai. Slow controlled push-ups start karo.")
						else:
							cv2.putText(img, "Adjust position - body straight line", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
						
					# Rep logic based on elbow angle on chosen side
					elbow_angle = self.compute_elbow_angle(results, side, w, h)
					if elbow_angle is not None:
						cv2.putText(img, f"Elbow angle: {int(elbow_angle)}°", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
					else:
						cv2.putText(img, "Elbow angle: Low confidence", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
					
					# Corrections during movement
					body_angle = self.compute_body_angle(results, w, h)
					if body_angle is not None and body_angle > self.body_angle_threshold:
						say("Body ko straight line mein rakho.", 1.0)
					
					# Rep detection using hysteresis on elbow angle (only if angle is valid)
					if elbow_angle is not None:
						if elbow_angle <= self.elbow_min_angle and self.direction == 0:
							self.direction = 1  # down achieved
							say("Neeche jao, control ke saath.", 1.2)
						elif elbow_angle >= self.elbow_up_angle and self.direction == 1:
							self.direction = 0
							self.reps += 1
							say(f"Rep {self.reps} complete. Shabash!", 1.5)
					
					# Periodic guidance if form is clean
					now = time.time()
					if now - self.last_guidance_time > self.guidance_interval:
						self.last_guidance_time = now
						say("Core tight rakho, body straight line mein.", 2.5)
				else:
					cv2.putText(img, "No pose detected", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
				
				# HUD
				cv2.putText(img, f"Reps: {self.reps}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
				cv2.putText(img, "q=quit, l=switch side", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)
				
				# FPS
				c_time = time.time()
				fps = 1.0 / (c_time - p_time) if c_time > p_time else fps_prev
				p_time, fps_prev = c_time, fps
				cv2.putText(img, f"FPS: {int(fps)}", (w - 120, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)
				
				cv2.imshow("Push-up Trainer", img)
				key = cv2.waitKey(1) & 0xFF
				if key == ord('q'):
					break
				elif key == ord('l'):
					side = 'right' if side == 'left' else 'left'
					say(f"Ab {side} side.")
		finally:
			# Cleanup: only exit context manager for basic MediaPipe
			if not self.use_enhanced:
				try:
					pose_context.__exit__(None, None, None)
				except:
					pass
			# Reset enhanced processor if used
			if self.use_enhanced and self.processor:
				self.processor.reset()
		
		cap.release()
		cv2.destroyAllWindows()


def main() -> None:
	trainer = PushupTrainer()
	trainer.run()


if __name__ == "__main__":
	main()

