"""
Enhanced Glute Fly AI Trainer
Integrates data collection, posture rules, and ML training
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import pyttsx3
import math
from data_collector import DataCollector
from posture_rules import PostureRules
from ml_trainer import MLTrainer

# MediaPipe pose landmarks
L_HIP = 23
R_HIP = 24
L_KNEE = 25
R_KNEE = 26
L_ANKLE = 27
R_ANKLE = 28
L_HEEL = 29
R_HEEL = 30
L_FOOT = 31
R_FOOT = 32
L_SH = 11
R_SH = 12

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
    n1 = v1 / (np.linalg.norm(v1) + 1e-8)
    n2 = v2 / (np.linalg.norm(v2) + 1e-8)
    cosang = float(np.clip(np.dot(n1, n2), -1.0, 1.0))
    return math.degrees(math.acos(cosang))

def smooth(prev, new, alpha=0.3):
    """Exponential smoothing."""
    if prev is None:
        return new
    return alpha * new + (1 - alpha) * prev

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# Voice feedback with rate limiting
_last_say = 0.0
def say(text, min_interval=1.8):
    """Rate-limit TTS so it doesn't spam."""
    global _last_say
    now = time.time()
    if now - _last_say >= min_interval:
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 165)   # speaking speed
            engine.setProperty('volume', 1.0)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"❌ Voice error: {e}")
        _last_say = now

class EnhancedGluteFlyTrainer:
    def __init__(self):
        # Initialize modules
        self.data_collector = DataCollector()
        self.posture_rules = PostureRules()
        self.ml_trainer = MLTrainer()
        
        # Training mode flags
        self.data_collection_mode = False
        self.ml_prediction_mode = False
        
        # Calibration and tracking
        self.baseline = {
            'pelvis_x': None,
            'knee_y': None,
            'hip_angle': None,
            'lrhip_dx': None,
            'hip_position': None,
            'target_knee_y': None
        }
        
        # Session tracking
        self.session_start_time = None
        self.total_reps = 0
        self.correct_reps = 0
        
    def start_data_collection(self, side='left'):
        """Start data collection session"""
        self.data_collection_mode = True
        csv_file = self.data_collector.start_session(side)
        print(f"📊 Data collection started: {csv_file}")
        return csv_file
        
    def stop_data_collection(self):
        """Stop data collection session"""
        self.data_collection_mode = False
        self.data_collector.stop_session()
        stats = self.data_collector.get_session_stats()
        print(f"📊 Session completed: {stats['frame_count']} frames collected")
        
    def load_ml_model(self, model_path):
        """Load trained ML model"""
        try:
            self.ml_trainer.load_model(model_path)
            self.ml_prediction_mode = True
            print("🤖 ML model loaded successfully")
            return True
        except Exception as e:
            print(f"❌ Error loading ML model: {e}")
            return False
            
    def calibrate(self, results, w, h):
        """Enhanced calibration with all required measurements"""
        print("🎯 Starting enhanced calibration...")
        
        # Get key landmarks
        lhip = get_xy(results, L_HIP, w, h)
        rhip = get_xy(results, R_HIP, w, h)
        lknee = get_xy(results, L_KNEE, w, h)
        rknee = get_xy(results, R_KNEE, w, h)
        lsh = get_xy(results, L_SH, w, h)
        rsh = get_xy(results, R_SH, w, h)
        
        # Calculate baseline measurements
        pelvis_x = (lhip[0] + rhip[0]) / 2.0
        pelvis_y = (lhip[1] + rhip[1]) / 2.0
        lrhip_dx = abs(lhip[0] - rhip[0])
        
        # Calculate angles
        hip_angle = angle_deg(lsh, lhip, lknee)
        
        # Store baseline data
        self.baseline['pelvis_x'] = pelvis_x
        self.baseline['knee_y'] = lknee[1]  # Use left knee as default
        self.baseline['lrhip_dx'] = lrhip_dx
        self.baseline['hip_angle'] = hip_angle
        self.baseline['hip_position'] = lhip  # Store hip position for stability check
        self.baseline['target_knee_y'] = lknee[1] - (h * 0.09)  # 9% of frame height
        
        print("✅ Enhanced calibration completed")
        say("Calibration done. Start your exercise.")
        
    def evaluate_posture_enhanced(self, results, side, w, h):
        """Enhanced posture evaluation using all rules"""
        if not results.pose_landmarks:
            return None
            
        # Extract all landmarks
        landmarks = {}
        for i in range(33):
            lm = results.pose_landmarks.landmark[i]
            landmarks[i] = (lm.x, lm.y, lm.z)
            
        # Evaluate posture using rules
        posture_results = self.posture_rules.evaluate_posture(
            landmarks, side, self.baseline, w, h
        )
        
        return posture_results
        
    def collect_frame_data(self, results, side, posture_results, metrics):
        """Collect data for current frame"""
        if not self.data_collection_mode:
            return
            
        # Prepare metrics for data collection
        collection_metrics = {
            'hip_angle': metrics.get('hip_angle', 0),
            'dorsi_angle': metrics.get('dorsi_angle', 0),
            'progress': metrics.get('progress', 0),
            'rep_count': self.total_reps,
            'heels_position': posture_results.get('heels_position', ('unknown', 'unknown'))[1],
            'achilles_touch': posture_results.get('achilles_touch', ('unknown', 'unknown'))[1],
            'back_arch': posture_results.get('back_arch', ('unknown', 'unknown'))[1],
            'hip_stability': posture_results.get('hip_stability', ('unknown', 'unknown'))[1],
            'hip_rotation': posture_results.get('hip_rotation', ('unknown', 'unknown'))[1],
            'range_status': posture_results.get('range_status', ('unknown', 'unknown'))[1]
        }
        
        # Collect frame data
        label = posture_results.get('overall_label', 'unknown')
        self.data_collector.collect_frame(results, side, label, collection_metrics)
        
    def get_ml_prediction(self, results):
        """Get ML prediction for current frame"""
        if not self.ml_prediction_mode or not results.pose_landmarks:
            return None, 0.0
            
        # Extract landmarks for ML prediction
        landmarks = {}
        for i in range(33):
            lm = results.pose_landmarks.landmark[i]
            landmarks[i] = (lm.x, lm.y, lm.z)
            
        # Get prediction
        try:
            predicted_label, confidence = self.ml_trainer.predict_posture(landmarks)
            return predicted_label, confidence
        except Exception as e:
            print(f"❌ ML prediction error: {e}")
            return None, 0.0
    
    def provide_voice_feedback(self, posture_results):
        """Provide voice feedback based on posture evaluation"""
        if not posture_results:
            return
            
        # Voice feedback for specific posture issues
        if 'hip_stability' in posture_results:
            passed, status = posture_results['hip_stability']
            if not passed and status == "unstable":
                say("Keep your hips completely still.")
        
        if 'hip_rotation' in posture_results:
            passed, status = posture_results['hip_rotation']
            if not passed and status in ["turning_down", "rolling_back"]:
                say("Don't let that roll back.")
        
        if 'achilles_touch' in posture_results:
            passed, status = posture_results['achilles_touch']
            if not passed and status == "not_touching":
                say("Touch your Achilles tendon.")
        
        if 'heels_position' in posture_results:
            passed, status = posture_results['heels_position']
            if not passed and status == "too_far_from_hips":
                say("Move your heels to hip edge.")
        
        if 'back_arch' in posture_results:
            passed, status = posture_results['back_arch']
            if not passed and status == "no_arch":
                say("Maintain slight back arch.")
            
    def run(self):
        """Main training loop"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Could not open webcam.")
            return

        # Create window
        cv2.namedWindow("Enhanced Glute Fly AI Trainer", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Enhanced Glute Fly AI Trainer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        side = 'left'
        reps = 0
        direction = 0
        fps_prev = 0.0
        p_time = 0.0
        
        # Smoothing variables
        sm_knee_y = None
        sm_pelvis_x = None
        sm_lrhip_dx = None
        sm_hip_angle = None
        sm_dorsi = None
        
        # Violations accumulator
        vio = {
            'pelvis_shift': 0,
            'hip_roll': 0,
            'dorsi': 0,
            'heels_position': 0,
            'achilles_touch': 0,
            'back_arch': 0
        }

        print("Enhanced Glute Fly Trainer — Controls:")
        print("  c = calibrate")
        print("  l = toggle side")
        print("  r = reset reps")
        print("  d = start/stop data collection")
        print("  m = load ML model")
        print("  q = quit")
        
        say("Enhanced Glute Fly trainer started. Press C to calibrate.")

        with mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as pose:
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb)
                
                if results.pose_landmarks:
                    # Get key landmarks
                    lhip = get_xy(results, L_HIP, w, h)
                    rhip = get_xy(results, R_HIP, w, h)
                    lsh = get_xy(results, L_SH, w, h)
                    rsh = get_xy(results, R_SH, w, h)
                    
                    # Select side-specific landmarks
                    if side == 'left':
                        hip = lhip
                        sh = lsh
                        knee = get_xy(results, L_KNEE, w, h)
                        ankle = get_xy(results, L_ANKLE, w, h)
                        foot = get_xy(results, L_FOOT, w, h)
                    else:
                        hip = rhip
                        sh = rsh
                        knee = get_xy(results, R_KNEE, w, h)
                        ankle = get_xy(results, R_ANKLE, w, h)
                        foot = get_xy(results, R_FOOT, w, h)
                    
                    # Calculate metrics
                    pelvis_x = (lhip[0] + rhip[0]) / 2.0
                    pelvis_y = (lhip[1] + rhip[1]) / 2.0
                    lrhip_dx = abs(lhip[0] - rhip[0])
                    
                    # Smoothing
                    sm_knee_y = smooth(sm_knee_y, knee[1], 0.35)
                    sm_pelvis_x = smooth(sm_pelvis_x, pelvis_x, 0.35)
                    sm_lrhip_dx = smooth(sm_lrhip_dx, lrhip_dx, 0.35)
                    
                    # Calculate angles
                    hip_angle = angle_deg(sh, hip, knee)
                    dorsi_angle = angle_deg(knee, ankle, foot)
                    sm_hip_angle = smooth(sm_hip_angle, hip_angle, 0.35)
                    sm_dorsi = smooth(sm_dorsi, dorsi_angle, 0.35)
                    
                    # Enhanced posture evaluation
                    posture_results = self.evaluate_posture_enhanced(results, side, w, h)
                    
                    # ML prediction
                    ml_label, ml_confidence = self.get_ml_prediction(results)
                    
                    # Calculate progress
                    progress = 0.0
                    if self.baseline['knee_y'] is not None:
                        knee_lift_target_px = self.baseline['target_knee_y']
                        progress = clamp((self.baseline['knee_y'] - sm_knee_y) / 
                                       (self.baseline['knee_y'] - knee_lift_target_px), 0.0, 1.0)
                    
                    # Rep counting logic
                    if progress > 0.85 and direction == 0:
                        direction = 1
                    elif progress < 0.20 and direction == 1:
                        direction = 0
                        reps += 1
                        self.total_reps += 1
                        
                        # Check if rep was correct
                        if posture_results and posture_results.get('overall_label') == 'correct_posture':
                            self.correct_reps += 1
                            say(f"Good rep! Total: {reps}")
                        else:
                            say(f"Rep {reps}. Check your form.")
                    
                    # Prepare metrics for data collection
                    metrics = {
                        'hip_angle': sm_hip_angle,
                        'dorsi_angle': sm_dorsi,
                        'progress': progress,
                        'rep_count': reps
                    }
                    
                    # Collect data if in collection mode
                    self.collect_frame_data(results, side, posture_results, metrics)
                    
                    # Voice feedback for posture corrections
                    self.provide_voice_feedback(posture_results)
                    
                    # Draw visualizations
                    self.draw_enhanced_visualization(frame, results, side, posture_results, 
                                                   ml_label, ml_confidence, progress, reps, w, h)
                
                # Handle keyboard input
                key = cv2.waitKey(10) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('c'):
                    self.calibrate(results, w, h)
                elif key == ord('l'):
                    side = 'right' if side == 'left' else 'left'
                    say(f"Switched to {side} side")
                elif key == ord('r'):
                    reps = 0
                    self.total_reps = 0
                    self.correct_reps = 0
                    say("Reps reset")
                elif key == ord('d'):
                    if self.data_collection_mode:
                        self.stop_data_collection()
                    else:
                        self.start_data_collection(side)
                elif key == ord('m'):
                    model_path = input("Enter model path: ")
                    self.load_ml_model(model_path)
                
                cv2.imshow("Enhanced Glute Fly AI Trainer", frame)
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Final session summary
        if self.session_start_time:
            session_duration = time.time() - self.session_start_time
            accuracy = (self.correct_reps / self.total_reps * 100) if self.total_reps > 0 else 0
            print(f"\n📊 Session Summary:")
            print(f"  Total Reps: {self.total_reps}")
            print(f"  Correct Reps: {self.correct_reps}")
            print(f"  Accuracy: {accuracy:.1f}%")
            print(f"  Duration: {session_duration:.1f} seconds")
    
    def draw_enhanced_visualization(self, frame, results, side, posture_results, 
                                  ml_label, ml_confidence, progress, reps, w, h):
        """Draw enhanced visualization with all feedback"""
        # Draw skeleton
        if results.pose_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(
                frame, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS
            )
        
        # Draw progress bar
        bar_width = 200
        bar_height = 20
        bar_x = w - bar_width - 20
        bar_y = 50
        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
        progress_width = int(bar_width * progress)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + progress_width, bar_y + bar_height), (0, 255, 0), -1)
        
        # Draw text information
        y_offset = 30
        cv2.putText(frame, f"Side: {side.upper()}", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y_offset += 30
        
        cv2.putText(frame, f"Reps: {reps}", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y_offset += 30
        
        cv2.putText(frame, f"Progress: {progress:.1%}", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y_offset += 30
        
        # Draw posture evaluation results
        if posture_results:
            cv2.putText(frame, f"Overall: {posture_results.get('overall_label', 'unknown')}", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y_offset += 25
            
            # Draw individual checks
            checks = ['heels_position', 'achilles_touch', 'back_arch', 'hip_stability', 'hip_rotation']
            for check in checks:
                if check in posture_results:
                    passed, status = posture_results[check]
                    color = (0, 255, 0) if passed else (0, 0, 255)
                    cv2.putText(frame, f"{check}: {status}", (10, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                    y_offset += 20
        
        # Draw ML prediction
        if ml_label:
            cv2.putText(frame, f"ML: {ml_label} ({ml_confidence:.2f})", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
            y_offset += 25
        
        # Draw mode indicators
        if self.data_collection_mode:
            cv2.putText(frame, "DATA COLLECTION ON", (w - 200, h - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        if self.ml_prediction_mode:
            cv2.putText(frame, "ML PREDICTION ON", (w - 200, h - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

if __name__ == "__main__":
    print("Enhanced Glute Fly Trainer — Controls:")
    print("  c = calibrate")
    print("  l = toggle side")
    print("  r = reset reps")
    print("  d = start/stop data collection")
    print("  m = load ML model")
    print("  q = quit")
    
    trainer = EnhancedGluteFlyTrainer()
    say("Enhanced Glute Fly trainer started. Press C to calibrate.")
    trainer.run()
