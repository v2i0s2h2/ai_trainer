"""
Debug script to test if pyttsx3 voice is working at all
"""

import pyttsx3
import time

print("Testing pyttsx3 voice engine...")
print("=" * 60)

try:
    print("\n1. Initializing pyttsx3 engine...")
    engine = pyttsx3.init()
    print("   [OK] Engine initialized successfully!")
    
    print("\n2. Getting engine properties...")
    rate = engine.getProperty('rate')
    volume = engine.getProperty('volume')
    voices = engine.getProperty('voices')
    
    print(f"   Rate: {rate}")
    print(f"   Volume: {volume}")
    print(f"   Available voices: {len(voices)}")
    
    for i, voice in enumerate(voices):
        print(f"   Voice {i}: {voice.name}")
    
    print("\n3. Setting properties...")
    engine.setProperty('rate', 165)
    engine.setProperty('volume', 1.0)
    print("   [OK] Properties set!")
    
    print("\n4. Testing voice output...")
    print("   [VOICE] Speaking: 'Testing voice one two three'")
    engine.say("Testing voice one two three")
    engine.runAndWait()
    print("   [OK] First test complete!")
    
    time.sleep(1)
    
    print("\n5. Testing Hindi/Hinglish...")
    print("   [VOICE] Speaking: 'Namaste, yeh test hai'")
    engine.say("Namaste, yeh test hai")
    engine.runAndWait()
    print("   [OK] Hindi test complete!")
    
    time.sleep(1)
    
    print("\n6. Testing rapid messages...")
    for i in range(3):
        print(f"   [VOICE] Message {i+1}")
        engine.say(f"Message {i+1}")
        engine.runAndWait()
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS PASSED!")
    print("pyttsx3 is working properly on your system.")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    print(f"\nError type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    print("\nPossible issues:")
    print("1. pyttsx3 not installed properly")
    print("2. No audio output device")
    print("3. Audio drivers issue")
    print("\nTry: pip install pyttsx3 --force-reinstall")

