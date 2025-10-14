# glute_fly_trainer.py
# Run: python glute_fly_trainer.py

import cv2
import mediapipe as mp
import numpy as np
import time
import math
from gtts import gTTS
import pygame
import os
import tempfile
from threading import Thread
from queue import Queue
import atexit

# --- TTS (voice) Setup with gTTS + pygame (RELIABLE on Windows!) ---
class VoiceSystem:
    def __init__(self):
        """Initialize pygame mixer for audio playback"""
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.queue = Queue()
        self.temp_dir = tempfile.gettempdir()
        self.last_say_time = {}
        self.running = True  # Set before starting thread!
        self.thread = Thread(target=self._worker, daemon=True)
        self.thread.start()
        print("[VOICE] gTTS + pygame voice system initialized!")
    
    def _worker(self):
        """Worker thread that processes voice messages"""
        print("[VOICE WORKER] Started")
        message_count = 0
        
        while self.running:
            try:
                msg = self.queue.get(timeout=1)
                if msg is None:
                    print("[VOICE WORKER] Stopping")
                    break
                
                text, msg_id = msg
                message_count += 1
                
                print(f"[VOICE WORKER] #{message_count}: Generating audio for: {text[:50]}...")
                
                # Generate speech file
                tts = gTTS(text=text, lang='hi', slow=False)
                audio_file = os.path.join(self.temp_dir, f"voice_{msg_id}.mp3")
                tts.save(audio_file)
                
                print(f"[VOICE WORKER] #{message_count}: Playing audio...")
                
                # Play audio
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy() and self.running:
                    time.sleep(0.1)
                
                # Cleanup
                try:
                    os.remove(audio_file)
                except:
                    pass
                
                print(f"[VOICE WORKER] #{message_count}: Finished")
                
            except:
                # Timeout or error, continue
                pass
    
    def say(self, text, priority='normal', msg_type='general'):
        """Queue text to be spoken"""
        intervals = {
            'high': 0.8,
            'normal': 1.8,
            'low': 3.5
        }
        min_interval = intervals.get(priority, 1.8)
        
        now = time.time()
        last_time = self.last_say_time.get(msg_type, 0)
        time_since_last = now - last_time
        
        if time_since_last > min_interval:
            msg_id = f"{msg_type}_{int(now*1000)}"
            self.queue.put((text, msg_id))
            self.last_say_time[msg_type] = now
            print(f"[VOICE] Queued [{priority}][{msg_type}]: {text[:50]}...")
            return True
        else:
            print(f"[VOICE DEBUG] Skipped [{msg_type}]: too soon ({time_since_last:.2f}s < {min_interval}s)")
            return False
    
    def stop(self):
        """Stop the voice system"""
        print("[VOICE] Stopping...")
        self.running = False
        self.queue.put(None)
        self.thread.join(timeout=5)
        pygame.mixer.quit()
        print("[VOICE] Stopped")

_voice_system = None

def init_voice():
    """Initialize voice system - called lazily on first use"""
    global _voice_system
    if _voice_system is None:
        print("[VOICE MAIN] Initializing gTTS voice system...")
        _voice_system = VoiceSystem()
        print("[VOICE MAIN] Voice system ready!")

def say(text, min_interval=1.8, priority='normal', msg_type='general'):
    """
    Sends text to the TTS system to be spoken.
    
    Args:
        text: Text to speak
        min_interval: Minimum time between same message type (seconds)
        priority: 'high' (0.8s interval), 'normal' (1.8s), 'low' (3.5s)
        msg_type: Message type for tracking (e.g., 'pelvis', 'dorsi', 'rep')
    """
    # Initialize voice system on first use
    init_voice()
    
    # Use the voice system
    if _voice_system:
        return _voice_system.say(text, priority, msg_type)
    return False

def stop_tts():
    """Stops the text-to-speech engine gracefully."""
    global _voice_system
    if _voice_system:
        _voice_system.stop()


atexit.register(stop_tts)
# -------------------------

# ------------- Mediapipe setup -------------
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# ------------- helpers -------------
def to_px(landmark, w, h):
    return int(landmark.x * w), int(landmark.y * h)

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
    return prev * (1 - alpha) + new * alpha

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# ------------- config -------------
SHOW_SKELETON = True
MODEL_COMPLEXITY = 1

# knee lift target (pixels) from baseline knee y → smaller y = higher lift
KNEE_LIFT_TARGET_FRACTION = 0.09   # 9% of frame height
KNEE_UP_THRESHOLD = 0.85           # % progress considered "up"
KNEE_DOWN_THRESHOLD = 0.20         # % progress considered "down"

# pelvis stability thresholds
PELVIS_MAX_X_SHIFT_FRAC = 0.05     # 5% of frame width allowed from baseline
HIP_ROLL_MAX_DIFF_FRAC  = 0.04     # L/R hip relative X spread change

# dorsiflexion angle desired (knee-ankle-foot_index)
DORSI_MIN = 80
DORSI_MAX = 120

# voice feedback gating
VIOLATION_PERSIST_FRAMES = 8

def enhanced_calibration_guide():
    """Enhanced calibration with comprehensive setup guidance"""
    # Sequential voice instructions - each with unique msg_type to avoid blocking
    print("[DEBUG] Starting enhanced calibration guide...")
    
    say("Glute Fly AI Trainer shuru ho raha hai.", priority='normal', msg_type='intro1')
    say("Yeh exercise hip problems aur FAI fix karne mein madad karta hai.", priority='normal', msg_type='intro2')
    say("Pehle apna equipment aur position set karo.", priority='normal', msg_type='setup1')
    
    # Equipment setup
    say("Equipment chahiye: 2 inch mota pad ya towel, aur 2 kg dumbbell.", priority='normal', msg_type='equipment1')
    say("Pad ko apne hip ke neeche rakho support ke liye.", priority='normal', msg_type='equipment2')
    
    # Position setup
    say("Ab apni position sahi karo.", priority='normal', msg_type='position1')
    say("Side pe let jao, legs seedhi rakho.", priority='normal', msg_type='position2')
    say("Heels ko hips ke edge par rakho.", priority='normal', msg_type='position3')
    say("Achilles ka top dusre knee ko touch karna chahiye.", priority='normal', msg_type='position4')
    say("Foot dorsiflexed rakho - toes shin ki taraf.", priority='normal', msg_type='position5')
    say("Hips 4 inch forward rakhne hain square position se.", priority='normal', msg_type='position6')
    say("Chest forward, back mein halka sa arch.", priority='normal', msg_type='position7')
    say("Position ready hai? Toh C press karo calibration ke liye.", priority='normal', msg_type='ready')
    
    print("[DEBUG] Enhanced calibration guide complete - all messages queued")

def enhanced_calibration_process(pose, cap, side, baseline):
    """Enhanced calibration with real-time setup validation"""
    say("Calibration shuru kar rahe hain. Position still rakho.", priority='normal', msg_type='calibration1')
    say("Position check ho raha hai. 3 seconds still raho.", priority='normal', msg_type='calibration2')
    
    frames = 0
    sum_pelvis_x = 0.0
    sum_knee_y = 0.0
    sum_lrhip_dx = 0.0
    sum_hip_ang = 0.0
    
    # Setup validation counters
    setup_checks = {
        'heels_position': 0,
        'achilles_touch': 0,
        'dorsiflexion': 0,
        'hip_angle': 0,
        'back_arch': 0
    }
    
    # Track which corrections have been given
    corrections_given = set()
    
    t0 = time.time()
    last_correction_time = 0
    
    while frames < 30:
        ok2, fr2 = cap.read()
        if not ok2:
            continue
            
        h2, w2 = fr2.shape[:2]
        rgb2 = cv2.cvtColor(fr2, cv2.COLOR_BGR2RGB)
        res2 = pose.process(rgb2)
        vis = cv2.cvtColor(rgb2, cv2.COLOR_RGB2BGR)

        cv2.putText(vis, "Calibrating... hold still", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)
        cv2.putText(vis, "Setup validation in progress", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

        if res2.pose_landmarks:
            # Get landmarks
            if side == 'left':
                SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
                HIP = mp_pose.PoseLandmark.LEFT_HIP.value
                KNEE = mp_pose.PoseLandmark.LEFT_KNEE.value
                ANKLE = mp_pose.PoseLandmark.LEFT_ANKLE.value
                FOOT = mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value
                HEEL = mp_pose.PoseLandmark.LEFT_HEEL.value
            else:
                SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
                HIP = mp_pose.PoseLandmark.RIGHT_HIP.value
                KNEE = mp_pose.PoseLandmark.RIGHT_KNEE.value
                ANKLE = mp_pose.PoseLandmark.RIGHT_ANKLE.value
                FOOT = mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value
                HEEL = mp_pose.PoseLandmark.RIGHT_HEEL.value

            L_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
            R_HIP = mp_pose.PoseLandmark.RIGHT_HIP.value

            sh2 = get_xy(res2, SHOULDER, w2, h2)
            hip2 = get_xy(res2, HIP, w2, h2)
            knee2 = get_xy(res2, KNEE, w2, h2)
            ankle2 = get_xy(res2, ANKLE, w2, h2)
            foot2 = get_xy(res2, FOOT, w2, h2)
            heel2 = get_xy(res2, HEEL, w2, h2)
            lhip2 = get_xy(res2, L_HIP, w2, h2)
            rhip2 = get_xy(res2, R_HIP, w2, h2)

            pelvis_x2 = (lhip2[0] + rhip2[0]) / 2.0
            lrhip_dx2 = abs(lhip2[0] - rhip2[0])
            hip_ang2 = angle_deg(sh2, hip2, knee2)
            dorsi_ang2 = angle_deg(knee2, ankle2, foot2)

            # Real-time setup validation with voice corrections
            current_time = time.time()
            if current_time - last_correction_time > 3.0:  # Rate limit corrections
                
                # Check heels position (distance from hips)
                heels_hip_distance = abs(heel2[0] - hip2[0]) / w2
                if heels_hip_distance > 0.08:  # 8% threshold
                    if 'heels' not in corrections_given:
                        say("Heels ko hip edge ke paas rakho.", priority='high', msg_type='calib_heels')
                        corrections_given.add('heels')
                        last_correction_time = current_time
                else:
                    setup_checks['heels_position'] += 1

                # Check Achilles touch (knee-ankle-foot angle)
                if not (60 <= dorsi_ang2 <= 120):
                    if 'achilles' not in corrections_given:
                        say("Achilles ka top dusre knee ko touch karo.", priority='high', msg_type='calib_achilles')
                        corrections_given.add('achilles')
                        last_correction_time = current_time
                else:
                    setup_checks['achilles_touch'] += 1

                # Check dorsiflexion
                if not (80 <= dorsi_ang2 <= 120):
                    if 'dorsi' not in corrections_given:
                        say("Foot dorsiflexed rakho - toes shin ki taraf.", priority='high', msg_type='calib_dorsi')
                        corrections_given.add('dorsi')
                        last_correction_time = current_time
                else:
                    setup_checks['dorsiflexion'] += 1

                # Check hip angle (shoulder-hip-knee)
                if not (160 <= hip_ang2 <= 180):
                    if 'hip_angle' not in corrections_given:
                        say("Hips 4 inch forward rakhne hain square se.", priority='high', msg_type='calib_hip')
                        corrections_given.add('hip_angle')
                        last_correction_time = current_time
                else:
                    setup_checks['hip_angle'] += 1

                # Check back arch
                if hip_ang2 < 160:
                    if 'back_arch' not in corrections_given:
                        say("Chest forward rakho, back mein arch maintain karo.", priority='high', msg_type='calib_arch')
                        corrections_given.add('back_arch')
                        last_correction_time = current_time
                else:
                    setup_checks['back_arch'] += 1

            # Accumulate calibration data
            sum_pelvis_x += pelvis_x2
            sum_knee_y += knee2[1]
            sum_lrhip_dx += lrhip_dx2
            sum_hip_ang += hip_ang2
            frames += 1

        cv2.imshow("Glute Fly AI Trainer", vis)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
        # Safety timeout
        if time.time() - t0 > 5.0 and frames >= 10:
            break

    if frames > 0:
        baseline['pelvis_x'] = sum_pelvis_x / frames
        baseline['knee_y'] = sum_knee_y / frames
        baseline['lrhip_dx'] = sum_lrhip_dx / frames
        baseline['hip_angle'] = sum_hip_ang / frames
        
        # Setup validation summary
        total_checks = sum(setup_checks.values())
        if total_checks > frames * 0.7:  # 70% of frames passed checks
            say("Calibration complete! Setup verified hai.", priority='normal', msg_type='calib_done1')
            say("Choti lifts se shuru karo - sirf ek inch height.", priority='normal', msg_type='calib_done2')
            say("Hips bilkul still rakhne hain movement mein.", priority='normal', msg_type='calib_done3')
            say("Speed pe control rakho - slow aur controlled.", priority='normal', msg_type='calib_done4')
        else:
            say("Calibration ho gaya, lekin setup improve karna padega.", priority='normal', msg_type='calib_warning1')
            say("Sahi positioning pe focus karo better results ke liye.", priority='normal', msg_type='calib_warning2')
            
        return True
    else:
        say("Calibration fail ho gaya. Dobara try karo sahi position ke saath.", priority='normal', msg_type='calib_fail')
        return False

def main():
    # Voice system will auto-initialize on first say() call (lazy initialization)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam.")
        return

    # Create a named window and set it to fullscreen
    cv2.namedWindow("Glute Fly AI Trainer", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Glute Fly AI Trainer", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    side = 'left'  # start side
    reps = 0
    direction = 0  # 0 = down, 1 = up
    fps_prev = 0.0
    p_time = 0.0
    
    # Continuous guidance system - periodic reminders
    last_guidance_time = time.time()
    guidance_interval = 15  # Reminder every 15 seconds
    guidance_messages = [
        "Yaad rakho, hips bilkul still rakhne hain.",
        "Control ke saath lift karo. Speed se nahi.",
        "Ankle dorsiflexed rakho throughout.",
        "Choti lifts karo, ek inch hi kaafi hai.",
        "Pelvis ko straight rakho, roll mat hone do.",
        "Slow aur controlled movement maintain karo."
    ]
    guidance_index = 0

    # calibration stores
    baseline = {
        'pelvis_x': None,      # pelvis center x
        'knee_y': None,        # knee y in start position
        'hip_angle': None,     # hip angle (shoulder-hip-knee)
        'lrhip_dx': None       # |x_left_hip - x_right_hip|
    }
    knee_lift_target_px = None

    # violations accumulator
    vio = {
        'pelvis_shift': 0,
        'hip_roll': 0,
        'dorsi': 0
    }
    
    # positive feedback accumulator
    positive_vio = {
        'pelvis_stable': 0,
        'hip_straight': 0,
        'dorsi_good': 0
    }

    print("Glute Fly Trainer — Controls: c=calibrate, l=toggle side, r=reset reps, q=quit")
    print("Equipment: 2 inch pad/towel, 2 kg dumbbell")
    
    # Give initial voice guidance (will be quick since say() is non-blocking now)
    enhanced_calibration_guide()

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=MODEL_COMPLEXITY,
        smooth_landmarks=True,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:

        sm_knee_y = None
        sm_pelvis_x = None
        sm_lrhip_dx = None
        sm_hip_angle = None
        sm_dorsi = None
        sm_progress = None

        while True:
            ok, frame = cap.read()
            if not ok:
                continue

            h, w = frame.shape[:2]
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img.flags.writeable = False
            results = pose.process(img)
            img.flags.writeable = True
            image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                if SHOW_SKELETON:
                    mp_drawing.draw_landmarks(
                        image,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        mp_drawing.DrawingSpec(thickness=2, circle_radius=2),
                        mp_drawing.DrawingSpec(thickness=2)
                    )

                # landmark indices by side
                if side == 'left':
                    SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
                    HIP      = mp_pose.PoseLandmark.LEFT_HIP.value
                    KNEE     = mp_pose.PoseLandmark.LEFT_KNEE.value
                    ANKLE    = mp_pose.PoseLandmark.LEFT_ANKLE.value
                    HEEL     = mp_pose.PoseLandmark.LEFT_HEEL.value
                    FOOT     = mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value
                else:
                    SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
                    HIP      = mp_pose.PoseLandmark.RIGHT_HIP.value
                    KNEE     = mp_pose.PoseLandmark.RIGHT_KNEE.value
                    ANKLE    = mp_pose.PoseLandmark.RIGHT_ANKLE.value
                    HEEL     = mp_pose.PoseLandmark.RIGHT_HEEL.value
                    FOOT     = mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value

                L_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
                R_HIP = mp_pose.PoseLandmark.RIGHT_HIP.value
                L_SH  = mp_pose.PoseLandmark.LEFT_SHOULDER.value
                R_SH  = mp_pose.PoseLandmark.RIGHT_SHOULDER.value

                # xy coords (in pixels)
                sh = get_xy(results, SHOULDER, w, h)
                hip = get_xy(results, HIP, w, h)
                knee = get_xy(results, KNEE, w, h)
                ankle = get_xy(results, ANKLE, w, h)
                foot = get_xy(results, FOOT, w, h)
                lhip = get_xy(results, L_HIP, w, h)
                rhip = get_xy(results, R_HIP, w, h)
                lsh = get_xy(results, L_SH, w, h)
                rsh = get_xy(results, R_SH, w, h)

                # pelvis center (avg hips)
                pelvis_x = (lhip[0] + rhip[0]) / 2.0
                pelvis_y = (lhip[1] + rhip[1]) / 2.0
                lrhip_dx = abs(lhip[0] - rhip[0])

                # smoothing
                sm_knee_y = smooth(sm_knee_y, knee[1], 0.35)
                sm_pelvis_x = smooth(sm_pelvis_x, pelvis_x, 0.35)
                sm_lrhip_dx = smooth(sm_lrhip_dx, lrhip_dx, 0.35)

                # main angles
                hip_angle = angle_deg(sh, hip, knee)         # torso-hip-thigh
                dorsi_angle = angle_deg(knee, ankle, foot)   # shin-ankle-foot
                sm_hip_angle = smooth(sm_hip_angle, hip_angle, 0.35)
                sm_dorsi = smooth(sm_dorsi, dorsi_angle, 0.35)

                # draw some points
                cv2.circle(image, (int(pelvis_x), int(pelvis_y)), 6, (0, 255, 255), -1)
                cv2.circle(image, (int(knee[0]), int(knee[1])), 6, (0, 255, 0), -1)
                cv2.putText(image, f"HipAngle:{int(sm_hip_angle or 0)}", (10, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
                cv2.putText(image, f"Dorsi:{int(sm_dorsi or 0)}", (10, 140),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

                # --- calibration hint and equipment info ---
                if baseline['knee_y'] is None:
                    cv2.putText(image, "Press 'c' to calibrate in start position",
                                (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,200,255), 2)
                    cv2.putText(image, "Equipment: 2 inch pad/towel + 2 kg dumbbell",
                                (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
                    cv2.putText(image, "Setup: Heels at hip edge, Achilles touch knee",
                                (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
                    cv2.putText(image, "Position: Hips 4 inches forward, dorsiflexed foot",
                                (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

                # progress from knee lift (baseline required)
                progress = 0.0
                if baseline['knee_y'] is not None and knee_lift_target_px:
                    # For lying down on side: smaller y = higher lift
                    # Current knee position relative to baseline
                    current_knee_y = sm_knee_y if sm_knee_y is not None else knee[1]
                    
                    # Calculate lift distance (negative when lifting up)
                    dy = baseline['knee_y'] - current_knee_y
                    
                    # Normalize to 0-1 range
                    if knee_lift_target_px > 0:
                        progress = clamp(dy / knee_lift_target_px, 0.0, 1.0)
                    else:
                        progress = 0.0
                    
                    sm_progress = smooth(sm_progress, progress, 0.4)
                    
                    # Debug info
                    cv2.putText(image, f"Lift: {int(dy)}px Target: {int(knee_lift_target_px)}px", 
                                (10, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,0), 1)

                    # vertical bar
                    top = 100
                    bottom = h - 70
                    bar_x1, bar_x2 = w - 80, w - 40
                    cv2.rectangle(image, (bar_x1, top), (bar_x2, bottom), (255, 255, 255), 2)
                    fill_h = int((sm_progress or 0) * (bottom - top))
                    cv2.rectangle(image, (bar_x1, bottom - fill_h), (bar_x2, bottom), (0, 200, 0), -1)
                    cv2.putText(image, f"{int((sm_progress or 0)*100)}%", (bar_x1-5, top-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

                    # rep logic (hysteresis) with Hindi/English mixed feedback
                    if (sm_progress or 0) >= KNEE_UP_THRESHOLD and direction == 0:
                        direction = 1
                        say("Achha! Leg upar hai. Position hold karo.", priority='normal', msg_type='rep_up')
                    if (sm_progress or 0) <= KNEE_DOWN_THRESHOLD and direction == 1:
                        direction = 0
                        reps += 1
                        say(f"Shabash! Rep {reps} complete. Hips still rakho.", priority='normal', msg_type='rep_complete')

                # --------- form checks ----------
                warnings = []
                positive_feedback = []

                # pelvis stability in X (no forward/back drift)
                if baseline['pelvis_x'] is not None:
                    x_shift = abs((sm_pelvis_x or pelvis_x) - baseline['pelvis_x'])
                    if x_shift > PELVIS_MAX_X_SHIFT_FRAC * w:
                        vio['pelvis_shift'] += 1
                        positive_vio['pelvis_stable'] = 0
                        warnings.append("Keep hips stable. Don't drift forward/back.")
                    else:
                        vio['pelvis_shift'] = 0
                        positive_vio['pelvis_stable'] += 1
                        positive_feedback.append("Hips stable - good!")

                # hip roll (relative spread between L/R hip vs baseline)
                if baseline['lrhip_dx'] is not None:
                    roll_diff = abs((sm_lrhip_dx or lrhip_dx) - baseline['lrhip_dx'])
                    if roll_diff > HIP_ROLL_MAX_DIFF_FRAC * w:
                        vio['hip_roll'] += 1
                        positive_vio['hip_straight'] = 0
                        warnings.append("Don't let the pelvis roll back.")
                    else:
                        vio['hip_roll'] = 0
                        positive_vio['hip_straight'] += 1
                        positive_feedback.append("Pelvis straight - excellent!")

                # dorsiflexion check
                if sm_dorsi is not None:
                    if not (DORSI_MIN <= sm_dorsi <= DORSI_MAX):
                        vio['dorsi'] += 1
                        positive_vio['dorsi_good'] = 0
                        warnings.append("Dorsiflex your ankle. Toes toward shin.")
                    else:
                        vio['dorsi'] = 0
                        positive_vio['dorsi_good'] += 1
                        positive_feedback.append("Ankle dorsiflexed - perfect!")

                # show warnings and positive feedback
                ycursor = 200
                
                # Show warnings in red
                for wtxt in set(warnings):
                    cv2.putText(image, "⚠ " + wtxt, (10, ycursor),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    ycursor += 28
                
                # Show positive feedback in green
                for ptext in set(positive_feedback):
                    cv2.putText(image, "✅ " + ptext, (10, ycursor),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    ycursor += 28

                # Voice feedback for violations with continuous reminders
                if vio['pelvis_shift'] > VIOLATION_PERSIST_FRAMES:
                    if say("Hips ko bilkul still rakho. Forward ya backward mat jao.", 
                           priority='high', msg_type='pelvis_shift'):
                        vio['pelvis_shift'] = -5  # Small negative allows quick re-trigger if still violating
                        
                if vio['hip_roll'] > VIOLATION_PERSIST_FRAMES:
                    if say("Pelvis ko roll back mat hone do. Seedha rakho.", 
                           priority='high', msg_type='hip_roll'):
                        vio['hip_roll'] = -5
                        
                if vio['dorsi'] > VIOLATION_PERSIST_FRAMES:
                    if say("Ankle dorsiflexed rakho. Toes ko shin ki taraf.", 
                           priority='high', msg_type='dorsi'):
                        vio['dorsi'] = -5
                
                # Individual positive voice feedback with low priority (less frequent)
                if positive_vio['pelvis_stable'] > VIOLATION_PERSIST_FRAMES * 2:
                    if say("Bahut badhiya! Hips bilkul stable hain!", 
                           priority='low', msg_type='pelvis_stable'):
                        positive_vio['pelvis_stable'] = 0
                        
                if positive_vio['hip_straight'] > VIOLATION_PERSIST_FRAMES * 2:
                    if say("Ekdum perfect! Pelvis straight hai!", 
                           priority='low', msg_type='hip_straight'):
                        positive_vio['hip_straight'] = 0
                        
                if positive_vio['dorsi_good'] > VIOLATION_PERSIST_FRAMES * 2:
                    if say("Zabardast! Ankle dorsiflexion ekdum sahi hai!", 
                           priority='low', msg_type='dorsi_good'):
                        positive_vio['dorsi_good'] = 0
                
                # Overall positive voice feedback when form is good
                if len(positive_feedback) >= 3:  # If all 3 things are correct
                    if vio['pelvis_shift'] <= 0 and vio['hip_roll'] <= 0 and vio['dorsi'] <= 0:
                        # Random positive feedback to avoid repetition
                        positive_messages = [
                            "Bahut achha! Form perfect hai!",
                            "Shabash! Posture ekdum sahi hai!",
                            "Kamaal ka! Keep it up!",
                            "Ekdum mast! Form maintain karo!",
                            "Perfect! Aise hi karte raho!",
                            "Zabardast! Technique ekdum perfect!"
                        ]
                        import random
                        if say(random.choice(positive_messages), priority='low', msg_type='overall_good'):
                            # Reset to avoid spam
                            vio['pelvis_shift'] = -15
                            vio['hip_roll'] = -15
                            vio['dorsi'] = -15
                
                # Continuous guidance system - periodic reminders during exercise
                current_time = time.time()
                if baseline['knee_y'] is not None:  # Only after calibration
                    if current_time - last_guidance_time > guidance_interval:
                        # Only give guidance if no active violations
                        if (vio['pelvis_shift'] <= 0 and vio['hip_roll'] <= 0 and 
                            vio['dorsi'] <= 0 and len(warnings) == 0):
                            if say(guidance_messages[guidance_index], 
                                   priority='low', msg_type='guidance'):
                                guidance_index = (guidance_index + 1) % len(guidance_messages)
                                last_guidance_time = current_time

                # UI header/footer
                cv2.putText(image, f"Side: {side}   Reps: {reps}", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

            else:
                cv2.putText(image, "No pose detected", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

            # FPS
            c_time = time.time()
            fps = 1.0 / (c_time - p_time) if c_time > p_time else fps_prev
            p_time, fps_prev = c_time, fps
            cv2.putText(image, f"FPS: {int(fps)}", (10, h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)

            cv2.imshow("Glute Fly AI Trainer", image)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break
            elif key == ord('l'):
                side = 'right' if side == 'left' else 'left'
                say(f"Ab {side} side. Position adjust karo.", priority='normal', msg_type='side_switch')
                # reset smoothing to avoid jump artifacts
                sm_knee_y = sm_pelvis_x = sm_lrhip_dx = sm_hip_angle = sm_dorsi = sm_progress = None
                # keep baseline (user can recalibrate)
            elif key == ord('r'):
                reps = 0
                direction = 0
                say("Counter reset ho gaya. Phir se shuru karo.", priority='normal', msg_type='reset')
            elif key == ord('c'):
                # Enhanced calibration with setup validation
                success = enhanced_calibration_process(pose, cap, side, baseline)
                if success:
                    knee_lift_target_px = KNEE_LIFT_TARGET_FRACTION * h

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
