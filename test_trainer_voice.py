"""
Quick test to verify trainer voice is working with debug
"""

if __name__ == '__main__':
    print("=" * 60)
    print("TESTING TRAINER VOICE WITH DEBUG")
    print("=" * 60)
    print("\nThis will test the enhanced_calibration_guide function")
    print("You should hear ALL voice messages in sequence\n")
    
    from glute_fly_trainer import enhanced_calibration_guide
    import time
    
    print("Starting calibration guide...")
    print("-" * 60)
    
    enhanced_calibration_guide()
    
    print("-" * 60)
    print("\nAll messages queued!")
    print("Waiting 30 seconds for voice to finish speaking...")
    print("Listen carefully - you should hear multiple instructions\n")
    
    time.sleep(30)
    
    print("=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)
    print("\nDid you hear ALL the voice messages about:")
    print("  - Trainer starting")
    print("  - Equipment needed")
    print("  - Position instructions")
    print("  - Calibration instructions")
    print("\nIf YES: Voice system is working!")
    print("If NO: Check the debug output above")
    print("=" * 60)

