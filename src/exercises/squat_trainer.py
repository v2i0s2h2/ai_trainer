# Squat Trainer
# Run: python -m src.exercises.squat_trainer

import cv2
import mediapipe as mp
import numpy as np
import time
from typing import Optional, Tuple

from src.core.voice_feedback import VoiceSystem


mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

voice = VoiceSystem()

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
	priority = 'high' if min_interval <= 1.0 else ('normal' if min_interval <= 2.0 else 'low')
	voice.say(text, priority=priority, msg_type='squat')


class SquatTrainer:
	def __init__(self) -> None:
		self.reps = 0
		self.direction = 0  # 0 = up, 1 = down (for hysteresis)
		self.knee_min_angle = 70.0   # target bottom angle
		self.knee_up_angle = 160.0   # standing threshold
		self.last_guidance_time = time.time()
		self.guidance_interval = 12
		self.calibrated = False
		self.stance_width_px: Optional[float] = None
		self.torso_upright_min_angle = 45.0  # torso vs vertical min (rough check)

	def posture_guide(self) -> None:
		say("Squat start karne se pehle sahi posture set karo.")
		say("Feet ko shoulder-width par rakho, toes thode bahar.")
		say("Chest up rakho, back straight aur core tight.")
		say("Weight heels par, knees ko toes se aage mat le jao.")

	def check_setup(self, results, w: int, h: int) -> bool:
		# Simple stance width check using ankle distance
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

	def compute_knee_angle(self, results, side: str, w: int, h: int) -> float:
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

	def compute_torso_angle_from_vertical(self, results, w: int, h: int) -> float:
		# Angle between shoulder-hip vector and vertical axis
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
		
		with mp_pose.Pose(
			static_image_mode=False,
			model_complexity=1,
			enable_segmentation=False,
			min_detection_confidence=0.5,
			min_tracking_confidence=0.5
		) as pose:
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
						
					# Rep logic based on knee angle on chosen side
					knee_angle = self.compute_knee_angle(results, side, w, h)
					cv2.putText(img, f"Knee angle: {int(knee_angle)}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
					
					# Corrections during movement
					torso_angle = self.compute_torso_angle_from_vertical(results, w, h)
					if torso_angle < self.torso_upright_min_angle:
						say("Chest up rakho, back straight.", 1.0)
					
					# Knees tracking heuristic (knee vs ankle x distance)
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
					
					# Rep detection using hysteresis on knee angle
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
		
		cap.release()
		cv2.destroyAllWindows()


def main() -> None:
	trainer = SquatTrainer()
	trainer.run()


if __name__ == "__main__":
	main()
