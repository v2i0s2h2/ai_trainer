"""
Data Collection Module for Glute Fly AI Trainer
Collects pose landmarks and automatically labels them based on posture rules
"""

import csv
import time
import os
from datetime import datetime
import numpy as np

class DataCollector:
    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        self.csv_file = None
        self.writer = None
        self.session_id = None
        self.frame_count = 0
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
    def start_session(self, side='left'):
        """Start a new data collection session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"glute_fly_{side}_{timestamp}"
        csv_filename = os.path.join(self.output_dir, f"{self.session_id}.csv")
        
        self.csv_file = open(csv_filename, 'w', newline='')
        self.writer = csv.writer(self.csv_file)
        
        # Write header
        header = self._create_header()
        self.writer.writerow(header)
        
        print(f"📊 Data collection started: {csv_filename}")
        return csv_filename
        
    def _create_header(self):
        """Create CSV header with all landmark coordinates"""
        header = ["timestamp", "frame_number", "side", "label"]
        
        # Add all 33 MediaPipe landmarks (x, y, z coordinates)
        for i in range(33):
            header.extend([f"x{i}", f"y{i}", f"z{i}"])
            
        # Add calculated metrics
        header.extend([
            "hip_angle", "dorsi_angle", "progress", "rep_count",
            "heels_position", "achilles_touch", "back_arch", 
            "hip_stability", "hip_rotation", "range_status"
        ])
        
        return header
        
    def collect_frame(self, results, side, label, metrics):
        """Collect data for current frame"""
        if not self.writer:
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Extract landmark coordinates
        landmarks = []
        if results.pose_landmarks:
            for landmark in results.pose_landmarks.landmark:
                landmarks.extend([landmark.x, landmark.y, landmark.z])
        else:
            # Fill with zeros if no landmarks detected
            landmarks = [0.0] * 99  # 33 landmarks * 3 coordinates
            
        # Create row data
        row = [
            timestamp,
            self.frame_count,
            side,
            label
        ]
        
        # Add landmarks
        row.extend(landmarks)
        
        # Add calculated metrics
        row.extend([
            metrics.get('hip_angle', 0),
            metrics.get('dorsi_angle', 0),
            metrics.get('progress', 0),
            metrics.get('rep_count', 0),
            metrics.get('heels_position', 'unknown'),
            metrics.get('achilles_touch', 'unknown'),
            metrics.get('back_arch', 'unknown'),
            metrics.get('hip_stability', 'unknown'),
            metrics.get('hip_rotation', 'unknown'),
            metrics.get('range_status', 'unknown')
        ])
        
        self.writer.writerow(row)
        self.frame_count += 1
        
    def stop_session(self):
        """Stop data collection session"""
        if self.csv_file:
            self.csv_file.close()
            print(f"📊 Data collection stopped. Total frames: {self.frame_count}")
            
    def get_session_stats(self):
        """Get statistics for current session"""
        return {
            'session_id': self.session_id,
            'frame_count': self.frame_count,
            'output_file': f"{self.session_id}.csv" if self.session_id else None
        }

# Example usage:
if __name__ == "__main__":
    collector = DataCollector()
    collector.start_session('left')
    
    # Simulate data collection
    metrics = {
        'hip_angle': 85.2,
        'dorsi_angle': 95.1,
        'progress': 0.3,
        'rep_count': 5,
        'heels_position': 'good',
        'achilles_touch': 'touching',
        'back_arch': 'good',
        'hip_stability': 'stable',
        'hip_rotation': 'none',
        'range_status': 'correct'
    }
    
    # collector.collect_frame(results, 'left', 'correct_posture', metrics)
    collector.stop_session()
