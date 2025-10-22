"""
Super simple direct test - no multiprocessing, just direct voice
"""

import pyttsx3
import time

print("=" * 60)
print("SIMPLE DIRECT VOICE TEST")
print("=" * 60)
print("\nThis will speak DIRECTLY - no multiprocessing")
print("Turn up your volume and listen carefully!")
print("\n")

try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Slower for clarity
    engine.setProperty('volume', 1.0)  # Max volume
    
    messages = [
        "Test one",
        "Test two", 
        "Test three",
        "Namaste",
        "Yeh test hai"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"{i}. Speaking: '{msg}'")
        print(f"   LISTEN NOW!!! >>>>> '{msg}' <<<<<")
        engine.say(msg)
        engine.runAndWait()
        print(f"   Finished speaking '{msg}'")
        print()
        time.sleep(1)
    
    print("=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)
    print("\nDid you HEAR the voice?")
    print("\nIf YES:")
    print("  -> Your audio is working!")
    print("  -> Run: python glute_fly_trainer.py")
    print("\nIf NO:")
    print("  -> Check speakers are ON")
    print("  -> Check volume is UP")  
    print("  -> Check audio output device")
    print("  -> Try headphones")
    print("=" * 60)
    
except Exception as e:
    print(f"ERROR: {e}")
    print("\nTry:")
    print("  pip install pyttsx3 --force-reinstall")

