
import numpy as np
import time
import math
import os

# Lazy load MediaPipe
mp = None
mp_pose = None
mp_drawing = None

def get_mediapipe():
    global mp, mp_pose, mp_drawing
    if mp is None:
        import mediapipe as _mp
        mp = _mp
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
    return mp, mp_pose, mp_drawing

# --- Helpers ---
def get_xy(results, idx, w, h):
    lm = results.pose_landmarks.landmark[idx]
    return (lm.x * w, lm.y * h)

def angle_deg(a, b, c):
    """Internal angle at b (0..180). Points are (x,y) in pixels."""
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    c = np.array(c, dtype=float)
    v1 = a - b
    v2 = c - b
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    n1 = v1 / norm1
    n2 = v2 / norm2
    cosang = float(np.clip(np.dot(n1, n2), -1.0, 1.0))
    return math.degrees(math.acos(cosang))

def smooth(prev, new, alpha=0.3):
    """Exponential smoothing."""
    if prev is None:
        return new
    return prev * (1 - alpha) + new * alpha

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

class GluteFlyTrainer:
    """
    Glute Fly Trainer integrated for WebSocket use.
    Implements a non-blocking state machine for calibration and exercise tracking.
    """
    def __init__(self):
        # State: 'CALIBRATION' or 'EXERCISE'
        self.state = 'CALIBRATION'
        
        # Calibration progress
        self.calib_frames = 0
        self.calib_target_frames = 30
        self.calib_accumulators = {
            'pelvis_x': 0.0,
            'knee_y': 0.0,
            'lrhip_dx': 0.0,
            'hip_ang': 0.0
        }
        
        # Baseline data (set after calibration)
        self.baseline = {
            'pelvis_x': None,
            'knee_y': None,
            'hip_angle': None,
            'lrhip_dx': None
        }
        self.knee_lift_target_px = None
        
        # Tracking variables
        self.reps = 0
        self.direction = 0  # 0 = down, 1 = up
        self.side = 'left'  # Default side
        
        # Smoothing buffers
        self.sm_knee_y = None
        self.sm_progress = None
        self.sm_pelvis_x = None
        self.sm_lrhip_dx = None
        self.sm_dorsi = None
        
        # Violations (counters for dampening feedback)
        self.vio = {
            'pelvis_shift': 0,
            'hip_roll': 0,
            'dorsi': 0
        }
        self.positive_vio = {
            'pelvis_stable': 0,
            'hip_straight': 0,
            'dorsi_good': 0
        }
        
        # Configuration
        self.KNEE_LIFT_TARGET_FRACTION = 0.09
        self.KNEE_UP_THRESHOLD = 0.85
        self.KNEE_DOWN_THRESHOLD = 0.20
        self.PELVIS_MAX_X_SHIFT_FRAC = 0.05
        self.HIP_ROLL_MAX_DIFF_FRAC = 0.04
        self.DORSI_MIN = 80
        self.DORSI_MAX = 120
        self.VIOLATION_PERSIST_FRAMES = 8 # Threshold to trigger feedback

        print("[GluteFlyTrainer] Initialized (State: CALIBRATION)")

    def process_frame(self, results, w: int, h: int, side: str = "left"):
        """
        Process a single frame and return feedback dict.
        Non-blocking.
        """
        # Ensure MediaPipe is loaded
        _mp, _pose, _drawing = get_mediapipe()
        
        # Update side if changed (can be passed from frontend later, for now internal state or param)
        # Using the passed side parameter if provided, otherwise defaulting to internal
        # In a real app, user might toggle side via UI, which sends a message. 
        # For now, we'll respect the 'side' argument if it changes from default.
        if side and side != self.side:
            self.side = side
            # Reset smoothing on side switch
            self.sm_knee_y = None
            self.sm_progress = None
        
        if not results.pose_landmarks:
            return {
                "reps": self.reps,
                "feedback": "Step into frame so I can see your full body",
                "angles": {},
                "progress": 0.0,
                "instruction": "Ensure camera sees head to toe"
            }

        # Check if user is actually in position before doing anything
        # Simple check: Hip Y should be significantly lower than Shoulder Y (if standing up)
        # But here user is lying down sideways.
        # Ideally: Head, Hip, Foot should be roughly on same Y level (horizontal)
        
        shoulders = self._get_landmarks_dict(results, w, h)['SHOULDER']
        hips = self._get_landmarks_dict(results, w, h)['HIP']
        feet = self._get_landmarks_dict(results, w, h)['FOOT']
        
        # Check if lying horizontally (approximate check)
        # Difference in Y between shoulder and hip should be small relative to width
        y_diff = abs(shoulders[1] - hips[1])
        is_horizontal = y_diff < (h * 0.2) # Threshold for "horizontal-ness"
        
        if not is_horizontal:
             return {
                "reps": self.reps,
                "feedback": "Lie down on your side to start",
                "angles": {},
                "progress": 0.0,
                "instruction": "Lie on side on mat"
            }

        # Route to appropriate handler based on state
        if self.state == 'CALIBRATION':
            return self._handle_calibration(results, w, h)
        else:
            return self._handle_exercise(results, w, h)

    def _get_landmarks_dict(self, results, w, h):
        """Extract relevant landmarks based on current side."""
        _mp, _pose, _drawing = get_mediapipe()
        
        lm_names = {}
        if self.side == 'left':
            lm_names['SHOULDER'] = _pose.PoseLandmark.LEFT_SHOULDER.value
            lm_names['HIP'] = _pose.PoseLandmark.LEFT_HIP.value
            lm_names['KNEE'] = _pose.PoseLandmark.LEFT_KNEE.value
            lm_names['ANKLE'] = _pose.PoseLandmark.LEFT_ANKLE.value
            lm_names['FOOT'] = _pose.PoseLandmark.LEFT_FOOT_INDEX.value
            lm_names['HEEL'] = _pose.PoseLandmark.LEFT_HEEL.value
        else:
            lm_names['SHOULDER'] = _pose.PoseLandmark.RIGHT_SHOULDER.value
            lm_names['HIP'] = _pose.PoseLandmark.RIGHT_HIP.value
            lm_names['KNEE'] = _pose.PoseLandmark.RIGHT_KNEE.value
            lm_names['ANKLE'] = _pose.PoseLandmark.RIGHT_ANKLE.value
            lm_names['FOOT'] = _pose.PoseLandmark.RIGHT_FOOT_INDEX.value
            lm_names['HEEL'] = _pose.PoseLandmark.RIGHT_HEEL.value

        # Always need both hips for pelvis calculations
        lm_names['L_HIP'] = _pose.PoseLandmark.LEFT_HIP.value
        lm_names['R_HIP'] = _pose.PoseLandmark.RIGHT_HIP.value
        
        coords = {}
        for name, idx in lm_names.items():
            coords[name] = get_xy(results, idx, w, h)
            
        return coords

    def _handle_calibration(self, results, w, h):
        """Accumulate calibration data over frames."""
        coords = self._get_landmarks_dict(results, w, h)
        
        # Calculate key metrics
        lhip = coords['L_HIP']
        rhip = coords['R_HIP']
        pelvis_x = (lhip[0] + rhip[0]) / 2.0
        lrhip_dx = abs(lhip[0] - rhip[0])
        
        shoulder = coords['SHOULDER']
        hip = coords['HIP']
        knee = coords['KNEE']
        hip_ang = angle_deg(shoulder, hip, knee)
        
        # Accumulate
        self.calib_accumulators['pelvis_x'] += pelvis_x
        self.calib_accumulators['knee_y'] += knee[1]
        self.calib_accumulators['lrhip_dx'] += lrhip_dx
        self.calib_accumulators['hip_ang'] += hip_ang
        
        self.calib_frames += 1
        
        progress_pct = int((self.calib_frames / self.calib_target_frames) * 100)
        
        if self.calib_frames >= self.calib_target_frames:
            # Finalize calibration
            self.baseline['pelvis_x'] = self.calib_accumulators['pelvis_x'] / self.calib_frames
            self.baseline['knee_y'] = self.calib_accumulators['knee_y'] / self.calib_frames
            self.baseline['lrhip_dx'] = self.calib_accumulators['lrhip_dx'] / self.calib_frames
            self.baseline['hip_angle'] = self.calib_accumulators['hip_ang'] / self.calib_frames
            self.knee_lift_target_px = self.KNEE_LIFT_TARGET_FRACTION * h
            
            self.state = 'EXERCISE'
            return {
                "reps": 0,
                "feedback": "Calibration Complete! maintain this position.",
                "angles": {"progress": 100},
                "progress": 0.0,
                "instruction": "Start lifting your knee slowly"
            }
            
        return {
            "reps": 0,
            "feedback": f"Calibrating... Stay still ({progress_pct}%)",
            "angles": {"calibration": progress_pct},
            "progress": 0.0,
            "instruction": "Hold position for calibration"
        }

    def _handle_exercise(self, results, w, h):
        """Main exercise logic loop."""
        coords = self._get_landmarks_dict(results, w, h)
        
        # Extract metrics
        lhip = coords['L_HIP']
        rhip = coords['R_HIP']
        pelvis_x = (lhip[0] + rhip[0]) / 2.0
        lrhip_dx = abs(lhip[0] - rhip[0])
        
        knee = coords['KNEE']
        ankle = coords['ANKLE']
        foot = coords['FOOT']
        
        dorsi_angle = angle_deg(knee, ankle, foot)
        
        # Smoothing
        self.sm_knee_y = smooth(self.sm_knee_y, knee[1], 0.35)
        self.sm_pelvis_x = smooth(self.sm_pelvis_x, pelvis_x, 0.35)
        self.sm_lrhip_dx = smooth(self.sm_lrhip_dx, lrhip_dx, 0.35)
        self.sm_dorsi = smooth(self.sm_dorsi, dorsi_angle, 0.35)
        
        # --- Rep Counting Logic ---
        progress = 0.0
        feedback_msg = ""
        
        if self.baseline['knee_y'] is not None and self.knee_lift_target_px:
            # For lying down: smaller Y = higher lift (screen coordinates)
            # Lift distance (pixels)
            dy = self.baseline['knee_y'] - self.sm_knee_y
            
            if self.knee_lift_target_px > 0:
                progress = clamp(dy / self.knee_lift_target_px, 0.0, 1.0)
            
            self.sm_progress = smooth(self.sm_progress, progress, 0.4)
            
            # Rep hysteresis
            if (self.sm_progress or 0) >= self.KNEE_UP_THRESHOLD and self.direction == 0:
                self.direction = 1
            if (self.sm_progress or 0) <= self.KNEE_DOWN_THRESHOLD and self.direction == 1:
                self.direction = 0
                self.reps += 1
                feedback_msg = f"Good! Rep {self.reps}"

        # --- Form Checks ---
        warnings = []
        # Pelvis stability (X-axis)
        if self.baseline['pelvis_x']:
            x_shift = abs((self.sm_pelvis_x or pelvis_x) - self.baseline['pelvis_x'])
            if x_shift > self.PELVIS_MAX_X_SHIFT_FRAC * w:
                self.vio['pelvis_shift'] += 1
                if self.vio['pelvis_shift'] > self.VIOLATION_PERSIST_FRAMES:
                    warnings.append("Keep hips stable! Don't rock forward/back.")
            else:
                self.vio['pelvis_shift'] = max(0, self.vio['pelvis_shift'] - 1)

        # Hip Roll (Relative Hip Spread)
        if self.baseline['lrhip_dx']:
            roll_diff = abs((self.sm_lrhip_dx or lrhip_dx) - self.baseline['lrhip_dx'])
            if roll_diff > self.HIP_ROLL_MAX_DIFF_FRAC * w:
                self.vio['hip_roll'] += 1
                if self.vio['hip_roll'] > self.VIOLATION_PERSIST_FRAMES:
                    warnings.append("Don't let pelvis roll back!")
            else:
                self.vio['hip_roll'] = max(0, self.vio['hip_roll'] - 1)

        # Dorsiflexion
        if self.sm_dorsi:
            if not (self.DORSI_MIN <= self.sm_dorsi <= self.DORSI_MAX):
                self.vio['dorsi'] += 1
                if self.vio['dorsi'] > self.VIOLATION_PERSIST_FRAMES:
                    warnings.append("Keep ankle bent (toes to shin)")
            else:
                self.vio['dorsi'] = max(0, self.vio['dorsi'] - 1)
        
        # Priority Feedback Selection
        final_feedback = feedback_msg
        if warnings:
            # If there are warnings, override success message or append
            final_feedback = warnings[0] # Prioritize first warning
        elif not final_feedback:
            # Default state message if no rep event and no warning
            if self.direction == 1:
                final_feedback = "Hold top position..."
            else:
                final_feedback = "Lift knee slowly..."

        return {
            "reps": self.reps,
            "feedback": final_feedback,
            "angles": {
                "dorsi": int(self.sm_dorsi or 0),
                "lift": int((self.sm_progress or 0) * 100)
            },
            "progress": float(self.sm_progress or 0),
            "instruction": "Keep pelvis still"
        }

if __name__ == "__main__":
    # Simple test if run directly
    print("Testing GluteFlyTrainer...")
    trainer = GluteFlyTrainer()
    print("Trainer created successfully.")
