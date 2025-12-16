"""
Reliable voice system using gTTS (Google Text-to-Speech) + pygame
This works PERFECTLY on Windows!
"""

from gtts import gTTS
import pygame
import os
import tempfile
from threading import Thread
from queue import Queue
import time
import traceback
try:
    import pyttsx3  # Fallback TTS on Linux if gTTS/pygame fails
except Exception:
    pyttsx3 = None

class VoiceSystem:
    def __init__(self):
        """Initialize pygame mixer for audio playback"""
        # Prefer PulseAudio on Linux (common on Arch/PipeWire)
        os.environ.setdefault("SDL_AUDIODRIVER", "pulse")
        self.backend = "gtts"
        self.queue = Queue()
        self.temp_dir = tempfile.gettempdir()
        self.last_say_time = {}
        self.pyttsx3_engine = None
        try:
            # Check for display/audio device first
            if not (os.environ.get('DISPLAY') or os.name == 'nt'):
                raise RuntimeError("Headless environment detected")

            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            print("[VOICE] Initialized gTTS + pygame backend")
        except Exception as e:
            print(f"[VOICE] Pygame mixer init failed: {e}")
            if pyttsx3 is not None:
                self.backend = "pyttsx3"
                try:
                    self.pyttsx3_engine = pyttsx3.init()
                    self.pyttsx3_engine.setProperty('rate', 165)
                    self.pyttsx3_engine.setProperty('volume', 1.0)
                    print("[VOICE] Falling back to pyttsx3 backend")
                except Exception as e2:
                    print(f"[VOICE] pyttsx3 init also failed: {e2}")
                    self.backend = "disabled"
            else:
                self.backend = "disabled"
                print("[VOICE] Voice feedback disabled (no audio backend available)")


        self.thread = Thread(target=self._worker, daemon=True)
        self.thread.start()
    
    def _worker(self):
        """Worker thread that processes voice messages"""
        print("[VOICE WORKER] Started")
        message_count = 0
        
        while True:
            try:
                msg = self.queue.get()
                if msg is None:
                    print("[VOICE WORKER] Stopping")
                    break
                
                text, msg_id = msg
                message_count += 1
                
                print(f"[VOICE WORKER] #{message_count}: Generating audio for: {text[:50]}...")
                if self.backend == "gtts":
                    try:
                        # Generate speech file with gTTS
                        tts = gTTS(text=text, lang='hi', slow=False)
                        audio_file = os.path.join(self.temp_dir, f"voice_{msg_id}.mp3")
                        tts.save(audio_file)
                        print(f"[VOICE WORKER] #{message_count}: Playing audio (pygame)...")
                        pygame.mixer.music.load(audio_file)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.1)
                        try:
                            os.remove(audio_file)
                        except Exception:
                            pass
                        print(f"[VOICE WORKER] #{message_count}: Finished")
                        continue
                    except Exception as ge:
                        print(f"[VOICE WORKER] gTTS/pygame error, switching to pyttsx3: {ge}")
                        if pyttsx3 is not None:
                            # Switch backend permanently for this session
                            self.backend = "pyttsx3"
                            if self.pyttsx3_engine is None:
                                try:
                                    self.pyttsx3_engine = pyttsx3.init()
                                    self.pyttsx3_engine.setProperty('rate', 165)
                                    self.pyttsx3_engine.setProperty('volume', 1.0)
                                except Exception as e2:
                                    print(f"[VOICE WORKER] pyttsx3 init failed: {e2}")
                        else:
                            traceback.print_exc()
                # pyttsx3 fallback
                if self.backend == "pyttsx3" and self.pyttsx3_engine is not None:
                    try:
                        self.pyttsx3_engine.say(text)
                        self.pyttsx3_engine.runAndWait()
                        print(f"[VOICE WORKER] #{message_count}: Finished (pyttsx3)")
                    except Exception as e3:
                        print(f"[VOICE WORKER] pyttsx3 error: {e3}")
                
            except Exception as e:
                print(f"[VOICE WORKER] Error: {e}")
                import traceback
                traceback.print_exc()
    
    def say(self, text, priority='normal', msg_type='general'):
        """
        Queue text to be spoken
        
        Args:
            text: Text to speak
            priority: 'high' (0.8s interval), 'normal' (1.8s), 'low' (3.5s)
            msg_type: Message type for tracking
        
        Returns:
            True if queued, False if skipped
        """
        # Priority-based intervals
        intervals = {
            'high': 0.8,
            'normal': 1.8,
            'low': 3.5
        }
        min_interval = intervals.get(priority, 1.8)
        
        # Check timing
        now = time.time()
        last_time = self.last_say_time.get(msg_type, 0)
        time_since_last = now - last_time
        
        if time_since_last > min_interval:
            msg_id = f"{msg_type}_{int(now*1000)}"
            self.queue.put((text, msg_id))
            self.last_say_time[msg_type] = now
            print(f"[VOICE] Queued [{priority}][{msg_type}]: {text[:50]}...")
            return True
        else:
            print(f"[VOICE DEBUG] Skipped [{msg_type}]: too soon ({time_since_last:.2f}s < {min_interval}s)")
            return False
    
    def stop(self):
        """Stop the voice system"""
        print("[VOICE] Stopping...")
        self.queue.put(None)
        self.thread.join(timeout=5)
        try:
            pygame.mixer.quit()
        except Exception:
            pass
        print("[VOICE] Stopped")


# Test it!
if __name__ == '__main__':
    print("=" * 60)
    print("TESTING gTTS + pygame VOICE SYSTEM")
    print("=" * 60)
    print("\nThis should DEFINITELY work on Windows!")
    print("Make sure you have internet connection for gTTS\n")
    
    voice = VoiceSystem()
    
    print("Test 1: Simple message...")
    voice.say("Namaste! Yeh gTTS test hai.", priority='normal', msg_type='test1')
    time.sleep(5)
    
    print("\nTest 2: Hindi/Hinglish...")
    voice.say("Hips ko bilkul still rakho!", priority='high', msg_type='test2')
    time.sleep(4)
    
    print("\nTest 3: Multiple messages...")
    voice.say("Rep ek complete", priority='normal', msg_type='test3')
    voice.say("Rep do complete", priority='normal', msg_type='test4')
    voice.say("Rep teen complete", priority='normal', msg_type='test5')
    
    print("\nWaiting for all messages to play...")
    time.sleep(15)
    
    voice.stop()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("Did you hear ALL the voice messages?")
    print("If YES: This system works! We'll use this!")
    print("If NO: Check internet connection for gTTS")
    print("=" * 60)

