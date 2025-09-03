# glute_fly_trainer.py
# Run: python glute_fly_trainer.py

import cv2
import mediapipe as mp
import numpy as np
import time
import math
import pyttsx3

# ------------- TTS (voice) -------------
engine = pyttsx3.init()
engine.setProperty('rate', 165)   # speaking speed
engine.setProperty('volume', 1.0)

_last_say = 0.0
def say(text, min_interval=1.8):
    """Rate-limit TTS so it doesn't spam."""
    global _last_say
    now = time.time()
    if now - _last_say >= min_interval:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass
        _last_say = now

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

def main():
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

    print("Glute Fly Trainer — Controls: c=calibrate, l=toggle side, r=reset reps, q=quit")
    say("Glute Fly trainer started. Press C to calibrate in your start position.")

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

                # --- calibration hint ---
                if baseline['knee_y'] is None:
                    cv2.putText(image, "Press 'c' to calibrate in start position",
                                (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,200,255), 2)

                # progress from knee lift (baseline required)
                progress = 0.0
                if baseline['knee_y'] is not None and knee_lift_target_px:
                    # downward y increases, up is smaller y
                    dy = baseline['knee_y'] - (sm_knee_y or knee[1])
                    progress = clamp(dy / knee_lift_target_px, 0.0, 1.0)
                    sm_progress = smooth(sm_progress, progress, 0.4)

                    # vertical bar
                    top = 100
                    bottom = h - 70
                    bar_x1, bar_x2 = w - 80, w - 40
                    cv2.rectangle(image, (bar_x1, top), (bar_x2, bottom), (255, 255, 255), 2)
                    fill_h = int((sm_progress or 0) * (bottom - top))
                    cv2.rectangle(image, (bar_x1, bottom - fill_h), (bar_x2, bottom), (0, 200, 0), -1)
                    cv2.putText(image, f"{int((sm_progress or 0)*100)}%", (bar_x1-5, top-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

                    # rep logic (hysteresis)
                    if (sm_progress or 0) >= KNEE_UP_THRESHOLD and direction == 0:
                        direction = 1
                        say("Good lift. Hold.")
                    if (sm_progress or 0) <= KNEE_DOWN_THRESHOLD and direction == 1:
                        direction = 0
                        reps += 1
                        say(f"One rep. Total {reps}")

                # --------- form checks ----------
                warnings = []

                # pelvis stability in X (no forward/back drift)
                if baseline['pelvis_x'] is not None:
                    x_shift = abs((sm_pelvis_x or pelvis_x) - baseline['pelvis_x'])
                    if x_shift > PELVIS_MAX_X_SHIFT_FRAC * w:
                        vio['pelvis_shift'] += 1
                        warnings.append("Keep hips stable. Don't drift forward/back.")
                    else:
                        vio['pelvis_shift'] = 0

                # hip roll (relative spread between L/R hip vs baseline)
                if baseline['lrhip_dx'] is not None:
                    roll_diff = abs((sm_lrhip_dx or lrhip_dx) - baseline['lrhip_dx'])
                    if roll_diff > HIP_ROLL_MAX_DIFF_FRAC * w:
                        vio['hip_roll'] += 1
                        warnings.append("Don't let the pelvis roll back.")
                    else:
                        vio['hip_roll'] = 0

                # dorsiflexion check
                if sm_dorsi is not None:
                    if not (DORSI_MIN <= sm_dorsi <= DORSI_MAX):
                        vio['dorsi'] += 1
                        warnings.append("Dorsiflex your ankle. Toes toward shin.")
                    else:
                        vio['dorsi'] = 0

                # show warnings and speak if persisted
                ycursor = 200
                for wtxt in set(warnings):
                    cv2.putText(image, "⚠ " + wtxt, (10, ycursor),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    ycursor += 28

                if vio['pelvis_shift'] > VIOLATION_PERSIST_FRAMES:
                    say("Keep your hips completely still.")
                    vio['pelvis_shift'] = 0
                if vio['hip_roll'] > VIOLATION_PERSIST_FRAMES:
                    say("Don't let that roll back.")
                    vio['hip_roll'] = 0
                if vio['dorsi'] > VIOLATION_PERSIST_FRAMES:
                    say("Keep your ankle dorsiflexed.")
                    vio['dorsi'] = 0

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
                say(f"{side} side")
                # reset smoothing to avoid jump artifacts
                sm_knee_y = sm_pelvis_x = sm_lrhip_dx = sm_hip_angle = sm_dorsi = sm_progress = None
                # keep baseline (user can recalibrate)
            elif key == ord('r'):
                reps = 0
                direction = 0
                say("Counters reset")
            elif key == ord('c'):
                # quick calibration: average ~30 frames
                say("Calibrating. Hold your start position still.")
                frames = 0
                sum_pelvis_x = 0.0
                sum_knee_y = 0.0
                sum_lrhip_dx = 0.0
                sum_hip_ang = 0.0
                t0 = time.time()
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

                    if res2.pose_landmarks:
                        if side == 'left':
                            SHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER.value
                            HIP      = mp_pose.PoseLandmark.LEFT_HIP.value
                            KNEE     = mp_pose.PoseLandmark.LEFT_KNEE.value
                        else:
                            SHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
                            HIP      = mp_pose.PoseLandmark.RIGHT_HIP.value
                            KNEE     = mp_pose.PoseLandmark.RIGHT_KNEE.value

                        L_HIP = mp_pose.PoseLandmark.LEFT_HIP.value
                        R_HIP = mp_pose.PoseLandmark.RIGHT_HIP.value

                        sh2 = get_xy(res2, SHOULDER, w2, h2)
                        hip2 = get_xy(res2, HIP, w2, h2)
                        knee2 = get_xy(res2, KNEE, w2, h2)
                        lhip2 = get_xy(res2, L_HIP, w2, h2)
                        rhip2 = get_xy(res2, R_HIP, w2, h2)

                        pelvis_x2 = (lhip2[0] + rhip2[0]) / 2.0
                        lrhip_dx2 = abs(lhip2[0] - rhip2[0])
                        hip_ang2 = angle_deg(sh2, hip2, knee2)

                        sum_pelvis_x += pelvis_x2
                        sum_knee_y += knee2[1]
                        sum_lrhip_dx += lrhip_dx2
                        sum_hip_ang += hip_ang2
                        frames += 1

                    cv2.imshow("Glute Fly AI Trainer", vis)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    # safety timeout
                    if time.time() - t0 > 3.0 and frames >= 10:
                        # accept partial if user moves
                        break

                if frames > 0:
                    baseline['pelvis_x'] = sum_pelvis_x / frames
                    baseline['knee_y'] = sum_knee_y / frames
                    baseline['lrhip_dx'] = sum_lrhip_dx / frames
                    baseline['hip_angle'] = sum_hip_ang / frames
                    knee_lift_target_px = KNEE_LIFT_TARGET_FRACTION * h
                    say("Calibration done. Start small lifts.")
                else:
                    say("Calibration failed. Try again.")

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
