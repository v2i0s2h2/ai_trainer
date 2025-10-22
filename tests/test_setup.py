"""
Test script to verify all modules are working correctly
"""

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import mediapipe as mp
        print("✅ MediaPipe imported successfully")
    except ImportError as e:
        print(f"❌ MediaPipe import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import pyttsx3
        print("✅ pyttsx3 imported successfully")
    except ImportError as e:
        print(f"❌ pyttsx3 import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import tensorflow as tf
        print("✅ TensorFlow imported successfully")
    except ImportError as e:
        print(f"❌ TensorFlow import failed: {e}")
        return False
    
    try:
        import sklearn
        print("✅ Scikit-learn imported successfully")
    except ImportError as e:
        print(f"❌ Scikit-learn import failed: {e}")
        return False
    
    return True

def test_custom_modules():
    """Test if our custom modules can be imported"""
    try:
        from data_collector import DataCollector
        print("✅ DataCollector imported successfully")
    except ImportError as e:
        print(f"❌ DataCollector import failed: {e}")
        return False
    
    try:
        from posture_rules import PostureRules
        print("✅ PostureRules imported successfully")
    except ImportError as e:
        print(f"❌ PostureRules import failed: {e}")
        return False
    
    try:
        from ml_trainer import MLTrainer
        print("✅ MLTrainer imported successfully")
    except ImportError as e:
        print(f"❌ MLTrainer import failed: {e}")
        return False
    
    return True

def test_mediapipe_setup():
    """Test MediaPipe pose detection setup"""
    try:
        import mediapipe as mp
        
        # Initialize MediaPipe pose
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose()
        print("✅ MediaPipe pose detection initialized successfully")
        
        # Test drawing utilities
        mp_drawing = mp.solutions.drawing_utils
        print("✅ MediaPipe drawing utilities imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ MediaPipe setup failed: {e}")
        return False

def main():
    print("🧪 Testing Glute Fly AI Trainer Setup")
    print("=" * 50)
    
    print("\n📦 Testing External Dependencies:")
    deps_ok = test_imports()
    
    print("\n🔧 Testing Custom Modules:")
    modules_ok = test_custom_modules()
    
    print("\n🎯 Testing MediaPipe Setup:")
    mediapipe_ok = test_mediapipe_setup()
    
    print("\n" + "=" * 50)
    if deps_ok and modules_ok and mediapipe_ok:
        print("🎉 ALL TESTS PASSED! Your setup is ready!")
        print("\n📋 Next Steps:")
        print("1. Connect your camera")
        print("2. Run: py -3.10 glute_fly_trainer.py (original)")
        print("3. Run: py -3.10 glute_fly_trainer_enhanced.py (with ML features)")
        print("4. Press 'c' to calibrate, then start exercising!")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return deps_ok and modules_ok and mediapipe_ok

if __name__ == "__main__":
    main()
