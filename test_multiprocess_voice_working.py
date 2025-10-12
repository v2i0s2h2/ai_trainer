"""
Test if multiprocessing voice worker is actually speaking
"""

import pyttsx3
from multiprocessing import Process, Queue
import time

def voice_worker(queue):
    """Function to run in a separate process for text-to-speech."""
    print("[WORKER] Voice worker process started")
    try:
        engine = pyttsx3.init()
        print("[WORKER] Engine initialized in worker process")
        engine.setProperty('rate', 165)
        engine.setProperty('volume', 1.0)
        print("[WORKER] Properties set, ready to speak")
        
        while True:
            text_to_say = queue.get()
            print(f"[WORKER] Received text: {text_to_say}")
            if text_to_say is None:
                print("[WORKER] Received None, breaking")
                break
            try:
                print(f"[WORKER] Speaking: {text_to_say}")
                engine.say(text_to_say)
                engine.runAndWait()
                print(f"[WORKER] Finished speaking: {text_to_say}")
            except Exception as e:
                print(f"[WORKER] Error in TTS engine: {e}")
    except Exception as e:
        print(f"[WORKER] Error initializing worker: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("Testing multiprocess voice worker...")
    print("=" * 60)
    
    # Create queue and process
    tts_queue = Queue()
    tts_process = Process(target=voice_worker, args=(tts_queue,), daemon=True)
    
    print("\n1. Starting voice worker process...")
    tts_process.start()
    print(f"   [OK] Process started, PID: {tts_process.pid}")
    print(f"   [OK] Process alive: {tts_process.is_alive()}")
    
    time.sleep(1)  # Give process time to initialize
    
    print("\n2. Sending test messages...")
    
    messages = [
        "Test message one",
        "Test message two", 
        "Namaste, yeh multiprocess test hai",
        "Final test message"
    ]
    
    for i, msg in enumerate(messages):
        print(f"\n   [{i+1}] Main process: Queuing '{msg}'")
        tts_queue.put(msg)
        print(f"   [{i+1}] Main process: Message queued")
        time.sleep(3)  # Wait for voice to finish
        print(f"   [{i+1}] Main process: Moving to next")
    
    print("\n3. Sending stop signal...")
    tts_queue.put(None)
    
    print("\n4. Waiting for worker to finish...")
    tts_process.join(timeout=5)
    
    if tts_process.is_alive():
        print("   [WARNING] Worker still alive, terminating...")
        tts_process.terminate()
    else:
        print("   [OK] Worker finished cleanly")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("Did you hear the voice messages? (Check speakers)")
    print("=" * 60)

