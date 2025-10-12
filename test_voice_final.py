"""
Final test to verify voice is working in the glute_fly_trainer
"""

if __name__ == '__main__':
    import time
    from glute_fly_trainer import say
    
    print("=" * 60)
    print("GLUTE FLY TRAINER - VOICE TEST")
    print("=" * 60)
    print("\nTesting voice system with lazy initialization...")
    print("Make sure your speakers are ON and volume is up!\n")
    
    print("1. Testing first voice message (will initialize system)...")
    say("Namaste! Voice system test kar rahe hain.", priority='normal', msg_type='test1')
    print("   Message queued. Listen for voice...\n")
    time.sleep(3)
    
    print("2. Testing high priority message...")
    say("Hips ko bilkul still rakho!", priority='high', msg_type='test2')
    print("   Message queued. Listen for voice...\n")
    time.sleep(2)
    
    print("3. Testing normal priority message...")
    say("Shabash! Rep complete ho gaya!", priority='normal', msg_type='test3')
    print("   Message queued. Listen for voice...\n")
    time.sleep(2)
    
    print("4. Testing low priority positive message...")
    say("Bahut achha! Form perfect hai!", priority='low', msg_type='test4')
    print("   Message queued. Listen for voice...\n")
    time.sleep(3)
    
    print("5. Testing continuous messages...")
    for i in range(3):
        say(f"Message number {i+1}", priority='high', msg_type=f'test{i+5}')
        print(f"   Message {i+1} queued...")
        time.sleep(1.5)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)
    print("\nDid you hear ALL the voice messages?")
    print("If YES: Voice system is working perfectly!")
    print("If NO: Check speakers, volume, or audio output device")
    print("\nWaiting for voice to finish...")
    time.sleep(3)
    print("\nDone!")

