"""
Posture Rules Module for Glute Fly AI Trainer
Implements all the detailed posture rules from the exercise guide
"""

import numpy as np
import math

class PostureRules:
    def __init__(self):
        # Thresholds for different posture checks
        self.HEELS_HIP_DISTANCE_THRESHOLD = 0.05  # 5% of frame width
        self.ACHILLES_TOUCH_ANGLE_MIN = 60
        self.ACHILLES_TOUCH_ANGLE_MAX = 120
        self.BACK_ARCH_ANGLE_MIN = 160
        self.BACK_ARCH_ANGLE_MAX = 180
        self.HIP_STABILITY_THRESHOLD = 0.03  # 3% movement tolerance
        self.HIP_ROTATION_THRESHOLD = 0.02   # 2% rotation tolerance
        
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
        
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle at point2 formed by point1-point2-point3"""
        # Convert to numpy arrays
        p1 = np.array(point1, dtype=float)
        p2 = np.array(point2, dtype=float)
        p3 = np.array(point3, dtype=float)
        
        # Calculate vectors
        v1 = p1 - p2
        v2 = p3 - p2
        
        # Normalize vectors
        v1_norm = v1 / (np.linalg.norm(v1) + 1e-8)
        v2_norm = v2 / (np.linalg.norm(v2) + 1e-8)
        
        # Calculate angle
        cos_angle = np.clip(np.dot(v1_norm, v2_norm), -1.0, 1.0)
        angle = math.degrees(math.acos(cos_angle))
        
        return angle
        
    def check_heels_position(self, heels_left, heels_right, hips_left, hips_right, frame_width):
        """
        Check if heels are positioned at the edge of hips
        Rule: Heels ko hips ke bilkul edge par hona chahiye
        """
        if not all([heels_left, heels_right, hips_left, hips_right]):
            return False, "missing_landmarks"
            
        # Calculate distances between heels and hips
        left_distance = self.calculate_distance(heels_left, hips_left)
        right_distance = self.calculate_distance(heels_right, hips_right)
        
        # Normalize by frame width
        left_distance_norm = left_distance / frame_width
        right_distance_norm = right_distance / frame_width
        
        # Check if both distances are within threshold
        if (left_distance_norm <= self.HEELS_HIP_DISTANCE_THRESHOLD and 
            right_distance_norm <= self.HEELS_HIP_DISTANCE_THRESHOLD):
            return True, "good"
        else:
            return False, "too_far_from_hips"
            
    def check_achilles_touch(self, knee, ankle, foot):
        """
        Check if Achilles is touching (knee-ankle-foot angle)
        Rule: Achilles ke top ko touch karna hai
        """
        if not all([knee, ankle, foot]):
            return False, "missing_landmarks"
            
        angle = self.calculate_angle(knee, ankle, foot)
        
        if self.ACHILLES_TOUCH_ANGLE_MIN <= angle <= self.ACHILLES_TOUCH_ANGLE_MAX:
            return True, "touching"
        else:
            return False, "not_touching"
            
    def check_back_arch(self, shoulder, hip, knee):
        """
        Check if back has slight arch
        Rule: Back mein halka sa arch maintain karna hai
        """
        if not all([shoulder, hip, knee]):
            return False, "missing_landmarks"
            
        angle = self.calculate_angle(shoulder, hip, knee)
        
        if self.BACK_ARCH_ANGLE_MIN <= angle <= self.BACK_ARCH_ANGLE_MAX:
            return True, "good_arch"
        else:
            return False, "no_arch"
            
    def check_hip_stability(self, current_hip, baseline_hip, frame_width):
        """
        Check if hip is stable (not moving forward/backward)
        Rule: Hips ko completely still aur straight up and down rakhna hai
        """
        if not all([current_hip, baseline_hip]):
            return False, "missing_baseline"
            
        # Calculate horizontal movement
        horizontal_movement = abs(current_hip[0] - baseline_hip[0])
        horizontal_movement_norm = horizontal_movement / frame_width
        
        if horizontal_movement_norm <= self.HIP_STABILITY_THRESHOLD:
            return True, "stable"
        else:
            return False, "unstable"
            
    def check_hip_rotation(self, side, current_hip, baseline_hip, frame_width):
        """
        Check side-specific hip rotation
        Rule: Left side - hip turn down nahi hona chahiye
              Right side - hip roll back nahi hona chahiye
        """
        if not all([current_hip, baseline_hip]):
            return False, "missing_baseline"
            
        if side == 'left':
            # Left side: check for downward rotation (Y coordinate)
            vertical_movement = current_hip[1] - baseline_hip[1]
            if vertical_movement > self.HIP_ROTATION_THRESHOLD * frame_width:
                return False, "turning_down"
            else:
                return True, "stable"
        else:
            # Right side: check for backward rotation (X coordinate)
            horizontal_movement = current_hip[0] - baseline_hip[0]
            if horizontal_movement > self.HIP_ROTATION_THRESHOLD * frame_width:
                return False, "rolling_back"
            else:
                return True, "stable"
                
    def check_dorsiflexion(self, knee, ankle, foot):
        """
        Check if ankle is in dorsiflexed position
        Rule: Foot ko dorsiflex rakho (toes ko shin ki taraf)
        """
        if not all([knee, ankle, foot]):
            return False, "missing_landmarks"
            
        angle = self.calculate_angle(knee, ankle, foot)
        
        # Dorsiflexion angle should be between 80-120 degrees
        if 80 <= angle <= 120:
            return True, "dorsiflexed"
        else:
            return False, "not_dorsiflexed"
            
    def check_range_of_motion(self, current_knee_y, baseline_knee_y, target_knee_y):
        """
        Check if leg lift range is appropriate
        Rule: Beginners ke liye sirf ek inch ya ek fist ki height tak lift
        """
        if not all([current_knee_y, baseline_knee_y, target_knee_y]):
            return False, "missing_baseline"
            
        lift_distance = baseline_knee_y - current_knee_y
        target_distance = baseline_knee_y - target_knee_y
        
        if lift_distance < target_distance * 0.5:
            return False, "too_low"
        elif lift_distance > target_distance * 1.5:
            return False, "too_high"
        else:
            return True, "correct_range"
            
    def evaluate_posture(self, landmarks, side, baseline_data, frame_width, frame_height):
        """
        Evaluate complete posture and return overall assessment
        """
        results = {}
        
        # Extract key landmarks
        heels_left = landmarks[29] if landmarks[29] else None
        heels_right = landmarks[30] if landmarks[30] else None
        hips_left = landmarks[23] if landmarks[23] else None
        hips_right = landmarks[24] if landmarks[24] else None
        knee = landmarks[25] if side == 'left' else landmarks[26]
        ankle = landmarks[27] if side == 'left' else landmarks[28]
        foot = landmarks[31] if side == 'left' else landmarks[32]
        shoulder = landmarks[11] if side == 'left' else landmarks[12]
        
        # Check all posture rules
        results['heels_position'] = self.check_heels_position(
            heels_left, heels_right, hips_left, hips_right, frame_width
        )
        
        results['achilles_touch'] = self.check_achilles_touch(knee, ankle, foot)
        
        results['back_arch'] = self.check_back_arch(shoulder, hips_left, knee)
        
        current_hip = hips_left if side == 'left' else hips_right
        baseline_hip = baseline_data.get('hip_position')
        if baseline_hip:
            results['hip_stability'] = self.check_hip_stability(
                current_hip, baseline_hip, frame_width
            )
            results['hip_rotation'] = self.check_hip_rotation(
                side, current_hip, baseline_hip, frame_width
            )
        
        results['dorsiflexion'] = self.check_dorsiflexion(knee, ankle, foot)
        
        baseline_knee_y = baseline_data.get('knee_y')
        target_knee_y = baseline_data.get('target_knee_y')
        if baseline_knee_y and target_knee_y:
            results['range_status'] = self.check_range_of_motion(
                knee[1], baseline_knee_y, target_knee_y
            )
        
        # Determine overall label
        results['overall_label'] = self._determine_overall_label(results)
        
        return results
        
    def _determine_overall_label(self, results):
        """Determine overall posture label based on individual checks"""
        failed_checks = []
        
        for check_name, (passed, status) in results.items():
            if check_name == 'overall_label':
                continue
            if not passed:
                failed_checks.append(check_name)
        
        if not failed_checks:
            return "correct_posture"
        elif len(failed_checks) == 1:
            return f"{failed_checks[0]}_issue"
        else:
            return "multiple_issues"

# Example usage:
if __name__ == "__main__":
    rules = PostureRules()
    
    # Example landmarks (simplified)
    landmarks = {
        11: (0.5, 0.3),  # left shoulder
        12: (0.6, 0.3),  # right shoulder
        23: (0.5, 0.5),  # left hip
        24: (0.6, 0.5),  # right hip
        25: (0.5, 0.7),  # left knee
        26: (0.6, 0.7),  # right knee
        27: (0.5, 0.9),  # left ankle
        28: (0.6, 0.9),  # right ankle
        29: (0.5, 0.95), # left heel
        30: (0.6, 0.95), # right heel
        31: (0.5, 0.98), # left foot
        32: (0.6, 0.98), # right foot
    }
    
    baseline_data = {
        'hip_position': (0.5, 0.5),
        'knee_y': 0.7,
        'target_knee_y': 0.6
    }
    
    results = rules.evaluate_posture(landmarks, 'left', baseline_data, 640, 480)
    print("Posture evaluation results:", results)
