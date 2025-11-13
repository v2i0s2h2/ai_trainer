"""
Camera utility functions for detecting and selecting cameras
"""
import cv2
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def list_cameras() -> List[Dict[str, any]]:
    """
    List all available camera devices
    Returns list of cameras with their index and name
    """
    cameras = []
    
    # Try to detect cameras by testing each index
    for i in range(10):  # Check first 10 indices
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                # Try to get camera name (may not work on all systems)
                backend = cap.getBackendName()
                cameras.append({
                    "index": i,
                    "name": f"Camera {i}",
                    "backend": backend
                })
                cap.release()
        except Exception as e:
            logger.debug(f"Camera {i} not available: {e}")
            continue
    
    return cameras

def detect_external_webcam() -> Optional[int]:
    """
    Try to detect external webcam (usually index 1 or higher)
    Returns camera index if found, None otherwise
    """
    cameras = list_cameras()
    
    if len(cameras) == 0:
        return None
    
    if len(cameras) == 1:
        # Only one camera, return it
        return cameras[0]["index"]
    
    # Multiple cameras - prefer index 1 or higher (external webcam)
    # Usually laptop camera is index 0, external is index 1+
    for cam in cameras:
        if cam["index"] > 0:
            logger.info(f"Detected external webcam at index {cam['index']}")
            return cam["index"]
    
    # Fallback to first camera
    return cameras[0]["index"]

def get_camera_index(device_id: Optional[str] = None) -> int:
    """
    Get camera index from device_id or auto-detect
    device_id can be:
    - "auto" or None: Auto-detect external webcam
    - "0", "1", etc: Use specific index
    - "external": Try to find external webcam
    """
    if device_id is None or device_id == "auto" or device_id == "external":
        detected = detect_external_webcam()
        if detected is not None:
            return detected
        # Fallback to default
        return 0
    
    try:
        index = int(device_id)
        # Verify camera exists
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            cap.release()
            return index
        else:
            logger.warning(f"Camera {index} not available, falling back to auto-detect")
            return get_camera_index("auto")
    except ValueError:
        logger.warning(f"Invalid camera device_id: {device_id}, falling back to auto-detect")
        return get_camera_index("auto")

