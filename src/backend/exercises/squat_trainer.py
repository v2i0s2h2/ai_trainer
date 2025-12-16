# Squat Trainer
# Run: python -m src.backend.exercises.squat_trainer

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
        print("[SquatTrainer] Voice disabled - no display available (server mode)")
except Exception as e:
    VOICE_ENABLED = False
    print(f"[SquatTrainer] Voice disabled: {e}")

# Import enhanced pose processor - skip on headless servers
ENHANCED_PROCESSOR_AVAILABLE = False
if os.environ.get('DISPLAY') or os.name == 'nt':
    try:
        from src.backend.core.pose_processor import EnhancedPoseProcessor
        ENHANCED_PROCESSOR_AVAILABLE = True
    except ImportError:
        print("[WARNING] EnhancedPoseProcessor not available, using basic processing")
else:
    print("[SquatTrainer] EnhancedPoseProcessor disabled - server mode (no display)")

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
		voice.say(text, priority=priority, msg_type='squat')


class SquatTrainer:
	def __init__(self, use_enhanced_processor: bool = True) -> None:
		self.reps = 0
		self.direction = 0  # 0 = up, 1 = down (for hysteresis)
		self.knee_min_angle = 70.0   # target bottom angle
		self.knee_up_angle = 160.0   # standing threshold
		self.last_guidance_time = time.time()
		self.last_feedback_time = 0.0
		self.feedback_cooldown = 2.0  # seconds between feedback messages
		self.guidance_interval = 12
		self.calibrated = False
		self.stance_width_px: Optional[float] = None
		self.torso_upright_min_angle = 45.0  # torso vs vertical min (rough check)
		self.current_feedback = ""  # Store current feedback message
		
		# Initialize enhanced pose processor if available
		self.use_enhanced = use_enhanced_processor and ENHANCED_PROCESSOR_AVAILABLE
		if self.use_enhanced:
			self.processor = EnhancedPoseProcessor(use_mediapipe=True)
			print("[SquatTrainer] ✅ Using EnhancedPoseProcessor for better accuracy")
		else:
			self.processor = None
			if use_enhanced_processor:
				print("[SquatTrainer] ⚠️ EnhancedPoseProcessor requested but not available, using basic processing")

	def posture_guide(self) -> None:
		say("Squat start karne se pehle sahi posture set karo.")
		say("Feet ko shoulder-width par rakho, toes thode bahar.")
		say("Chest up rakho, back straight aur core tight.")
		say("Weight heels par, knees ko toes se aage mat le jao.")

	def check_setup(self, results, w: int, h: int) -> bool:
		# Simple stance width check using ankle distance
		_, mp_pose, _ = get_mediapipe()
		L_ANKLE = mp_pose.PoseLandmark.LEFT_ANKLE.value
		R_ANKLE = mp_pose.PoseLandmark.RIGHT_ANKLE.value
		L_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
		R_HIP = mp_pose.PoseLandmark.RIGHT_HIP.value
		
		lank = get_xy(results, L_ANKLE, w, h)
		rank = get_xy(results, R_ANKLE, w, h)
		lhip = get_xy(results, L_HIP, w, h)
		rhip = get_xy(results, R_HIP, w, h)
		
		stance = abs(lank[0] - rank[0])
		hip_width = abs(lhip[0] - rhip[0])
		self.stance_width_px = stance
		
		if stance < 0.8 * hip_width:
			say("Stance thoda wide rakho - shoulder width.", 1.2)
			return False
		return True

	def compute_knee_angle(self, results, side: str, w: int, h: int) -> Optional[float]:
		"""Compute knee angle with enhanced processing if available"""
		if self.use_enhanced and self.processor:
			# Use enhanced processor with confidence checking
			landmarks = self.processor.get_key_landmarks(results, w, h, side)
			angle = self.processor.compute_knee_angle_enhanced(landmarks)
			return angle
		else:
			# Fallback to basic calculation
			_, mp_pose, _ = get_mediapipe()
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

	def compute_torso_angle_from_vertical(self, results, w: int, h: int) -> Optional[float]:
		"""Compute torso angle with enhanced processing if available"""
		if self.use_enhanced and self.processor:
			# Use enhanced processor with confidence checking
			landmarks = self.processor.get_key_landmarks(results, w, h, side='left')
			angle = self.processor.compute_torso_angle_enhanced(landmarks)
			return angle
		else:
			# Fallback to basic calculation
			_, mp_pose, _ = get_mediapipe()
			L_SH = mp_pose.PoseLandmark.LEFT_SHOULDER.value
			R_SH = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
			L_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
			R_HIP = mp_pose.PoseLandmark.RIGHT_HIP.value
			lsh = get_xy(results, L_SH, w, h)
			rsh = get_xy(results, R_SH, w, h)
			lhip = get_xy(results, L_HIP, w, h)
			rhip = get_xy(results, R_HIP, w, h)
			sh = ((lsh[0] + rsh[0]) / 2.0, (lsh[1] + rsh[1]) / 2.0)
			hip = ((lhip[0] + rhip[0]) / 2.0, (lhip[1] + rhip[1]) / 2.0)
			# vertical ref point below hip
			vert = (hip[0], hip[1] + 100)
			return angle_deg(sh, hip, vert)
	
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
				self.current_feedback = "Setup verified! Start squats"
			else:
				self.current_feedback = "Adjust stance to shoulder width"
		
		# Compute angles (with enhanced processing if available)
		knee_angle = self.compute_knee_angle(results, side, w, h)
		torso_angle = self.compute_torso_angle_from_vertical(results, w, h)
		
		# Skip processing if angles are None (low confidence landmarks)
		if knee_angle is None:
			return {
				"reps": self.reps,
				"feedback": "Low confidence - adjust position for better detection",
				"angles": {},
				"progress": 0.0
			}
		
		# Check form and provide corrections (with cooldown)
		now = time.time()
		if now - self.last_feedback_time > self.feedback_cooldown:
			if torso_angle is not None and torso_angle < self.torso_upright_min_angle:
				feedback_messages.append("Chest up, back straight")
				self.last_feedback_time = now
			
			# Check knee tracking
			_, mp_pose, _ = get_mediapipe()
			L_KNEE = mp_pose.PoseLandmark.LEFT_KNEE.value
			R_KNEE = mp_pose.PoseLandmark.RIGHT_KNEE.value
			L_ANKLE = mp_pose.PoseLandmark.LEFT_ANKLE.value
			R_ANKLE = mp_pose.PoseLandmark.RIGHT_ANKLE.value
			lknee = get_xy(results, L_KNEE, w, h)
			rknee = get_xy(results, R_KNEE, w, h)
			lank = get_xy(results, L_ANKLE, w, h)
			rank = get_xy(results, R_ANKLE, w, h)
			
			if abs(lknee[0] - lank[0]) > 0.25 * w or abs(rknee[0] - rank[0]) > 0.25 * w:
				feedback_messages.append("Keep knees over toes")
				self.last_feedback_time = now
		
		# Rep detection using hysteresis
		if knee_angle <= self.knee_min_angle and self.direction == 0:
			self.direction = 1  # going down
			feedback_messages.append("Going down - keep control")
		elif knee_angle >= self.knee_up_angle and self.direction == 1:
			self.direction = 0  # back up
			self.reps += 1
			feedback_messages.append(f"Rep {self.reps} complete! Good job")
			# Voice announcement for rep count
			say(f"Rep {self.reps} complete. Shabash!", 1.5)
		
		# Calculate progress (0-1 range based on knee angle)
		progress = 0.0
		if knee_angle < self.knee_up_angle:
			progress = 1.0 - (knee_angle - self.knee_min_angle) / (self.knee_up_angle - self.knee_min_angle)
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
				"knee": round(knee_angle, 1) if knee_angle is not None else None,
				"torso": round(torso_angle, 1) if torso_angle is not None else None
			},
			"progress": round(progress, 2)
		}

	def run(self) -> None:
		cap = cv2.VideoCapture(0)
		if not cap.isOpened():
			print("❌ Could not open webcam.")
			return
		
		cv2.namedWindow("Squat Trainer", cv2.WINDOW_NORMAL)
		cv2.setWindowProperty("Squat Trainer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
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
			# Lazy load mediapipe
			_, mp_pose, mp_drawing = get_mediapipe()
			
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
							say("Setup sahi hai. Slow controlled squats start karo.")
						else:
							cv2.putText(img, "Adjust stance to shoulder width", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
						
					# Rep logic based on knee angle on chosen side (with enhanced processing)
					knee_angle = self.compute_knee_angle(results, side, w, h)
					if knee_angle is not None:
						cv2.putText(img, f"Knee angle: {int(knee_angle)}°", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
					else:
						cv2.putText(img, "Knee angle: Low confidence", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
					
					# Corrections during movement
					torso_angle = self.compute_torso_angle_from_vertical(results, w, h)
					if torso_angle is not None and torso_angle < self.torso_upright_min_angle:
						say("Chest up rakho, back straight.", 1.0)
					
					# Knees tracking heuristic (knee vs ankle x distance)
					_, mp_pose, _ = get_mediapipe()
					L_KNEE = mp_pose.PoseLandmark.LEFT_KNEE.value
					R_KNEE = mp_pose.PoseLandmark.RIGHT_KNEE.value
					L_ANKLE = mp_pose.PoseLandmark.LEFT_ANKLE.value
					R_ANKLE = mp_pose.PoseLandmark.RIGHT_ANKLE.value
					lknee = get_xy(results, L_KNEE, w, h)
					rknee = get_xy(results, R_KNEE, w, h)
					lank = get_xy(results, L_ANKLE, w, h)
					rank = get_xy(results, R_ANKLE, w, h)
					if abs(lknee[0] - lank[0]) > 0.25 * w or abs(rknee[0] - rank[0]) > 0.25 * w:
						say("Knees ko toes ke upar track karo, aage mat nikaalo.", 1.0)
					
					# Rep detection using hysteresis on knee angle (only if angle is valid)
					if knee_angle is not None:
						if knee_angle <= self.knee_min_angle and self.direction == 0:
							self.direction = 1  # down achieved
							say("Neeche jao, control ke saath.", 1.2)
						elif knee_angle >= self.knee_up_angle and self.direction == 1:
							self.direction = 0
							self.reps += 1
							say(f"Rep {self.reps} complete. Shabash!", 1.5)
					
					# Periodic guidance if form is clean
					now = time.time()
					if now - self.last_guidance_time > self.guidance_interval:
						self.last_guidance_time = now
						say("Heels par weight rakho, knees outside push karo.", 2.5)
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
				
				cv2.imshow("Squat Trainer", img)
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
	trainer = SquatTrainer()
	trainer.run()


if __name__ == "__main__":
	main()
