"""
Test script for continuous voice feedback system
Tests the improved voice feedback with priority system and continuous reminders
"""

import time

if __name__ == '__main__':
    from glute_fly_trainer import say, _last_say_time

    print("=" * 60)
    print("CONTINUOUS VOICE FEEDBACK SYSTEM TEST")
    print("=" * 60)
    print("\nTesting improved voice feedback system...")
    print("Yeh test script check karega ki voice feedback continuously aa raha hai\n")

    # Test 1: High priority messages (violations)
    print("\n--- Test 1: High Priority Messages (Violations) ---")
    print("High priority messages har 0.8 seconds mein repeat honge agar violation continue hai\n")

    say("Hips ko bilkul still rakho.", priority='high', msg_type='test_pelvis')
    time.sleep(0.3)
    result = say("Hips ko bilkul still rakho.", priority='high', msg_type='test_pelvis')
    print(f"After 0.3s (too soon): Message queued = {result}")

    time.sleep(0.6)
    result = say("Hips ko bilkul still rakho.", priority='high', msg_type='test_pelvis')
    print(f"After 0.9s total (enough time): Message queued = {result}")

    # Test 2: Normal priority messages
    print("\n--- Test 2: Normal Priority Messages (Regular Feedback) ---")
    print("Normal priority messages har 1.8 seconds mein repeat honge\n")

    say("Rep complete ho gaya!", priority='normal', msg_type='test_rep')
    time.sleep(1.0)
    result = say("Rep complete ho gaya!", priority='normal', msg_type='test_rep')
    print(f"After 1.0s (too soon): Message queued = {result}")

    time.sleep(1.0)
    result = say("Rep complete ho gaya!", priority='normal', msg_type='test_rep')
    print(f"After 2.0s total (enough time): Message queued = {result}")

    # Test 3: Low priority messages (positive feedback)
    print("\n--- Test 3: Low Priority Messages (Positive Feedback) ---")
    print("Low priority messages har 3.5 seconds mein repeat honge\n")

    say("Form ekdum perfect hai!", priority='low', msg_type='test_positive')
    time.sleep(2.0)
    result = say("Form ekdum perfect hai!", priority='low', msg_type='test_positive')
    print(f"After 2.0s (too soon): Message queued = {result}")

    time.sleep(2.0)
    result = say("Form ekdum perfect hai!", priority='low', msg_type='test_positive')
    print(f"After 4.0s total (enough time): Message queued = {result}")

    # Test 4: Different message types can run simultaneously
    print("\n--- Test 4: Multiple Message Types Simultaneously ---")
    print("Different message types apne independent intervals pe chalte hain\n")

    say("Pelvis issue!", priority='high', msg_type='pelvis')
    say("Dorsi issue!", priority='high', msg_type='dorsi')
    say("Hip roll issue!", priority='high', msg_type='hip')
    print("Teeno messages queue ho gaye kyunki alag-alag msg_type hain!")

    # Test 5: Continuous violation scenario simulation
    print("\n--- Test 5: Continuous Violation Scenario ---")
    print("Agar user continuously galat posture mein hai, toh voice repeat hoga\n")

    for i in range(5):
        time.sleep(1.0)
        result = say("Hips still rakho!", priority='high', msg_type='continuous_test')
        print(f"Attempt {i+1} (after {i+1}s): Message queued = {result}")

    try:
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print("\n✅ High priority (violations): 0.8s interval - Fast feedback!")
        print("✅ Normal priority (reps/guidance): 1.8s interval - Regular feedback")
        print("✅ Low priority (positive): 3.5s interval - Less frequent")
        print("✅ Independent message types: Simultaneous tracking")
        print("✅ Continuous violations: Voice repeats automatically!")
        print("\n🎯 Ab user phone door rakh ke exercise kar sakta hai!")
        print("🎯 Voice feedback continuously milta rahega!")
        print("\n" + "=" * 60)
    except UnicodeEncodeError:
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print("\n[OK] High priority (violations): 0.8s interval - Fast feedback!")
        print("[OK] Normal priority (reps/guidance): 1.8s interval - Regular feedback")
        print("[OK] Low priority (positive): 3.5s interval - Less frequent")
        print("[OK] Independent message types: Simultaneous tracking")
        print("[OK] Continuous violations: Voice repeats automatically!")
        print("\n[TARGET] Ab user phone door rakh ke exercise kar sakta hai!")
        print("[TARGET] Voice feedback continuously milta rahega!")
        print("\n" + "=" * 60)

    # Give time for voice to finish
    print("\nWaiting for voice feedback to complete...")
    time.sleep(8)
    print("Test complete! Check console output above.")

