# 🔧 Voice Not Working? Troubleshooting Guide

## Agar voice nahi aa raha hai, yeh steps follow karo:

### ✅ Step 1: Check Speakers/Headphones
```
1. Speakers ON hain?
2. Volume UP hai? (50% se zyada rakho)
3. Mute toh nahi hai?
4. Sahi audio output device selected hai?
```

### ✅ Step 2: Test Windows Text-to-Speech
```powershell
# Windows PowerShell mein ye command run karo:
Add-Type -AssemblyName System.Speech
$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speak.Speak("Testing Windows voice")
```

**Agar ye bola toh:** Windows TTS kaam kar raha hai ✅  
**Agar nahi bola toh:** Windows TTS issue hai ❌

### ✅ Step 3: Reinstall pyttsx3
```bash
# Current installation remove karo
pip uninstall pyttsx3

# Fresh install karo
pip install pyttsx3

# Test karo
python test_voice_debug.py
```

### ✅ Step 4: Check Audio Output Device

Windows Settings:
1. Settings → System → Sound
2. Check "Choose your output device"
3. Test kar ke dekho koi device se awaaz aa raha hai

### ✅ Step 5: Try Alternative TTS Backend

If pyttsx3 doesn't work, we can use gTTS (Google Text-to-Speech):

```bash
# Install gTTS
pip install gtts playsound

# Test karo:
python -c "from gtts import gTTS; import os; tts=gTTS('Testing voice', lang='en'); tts.save('test.mp3'); os.system('test.mp3')"
```

### ✅ Step 6: Check Windows Speech Settings

1. Windows Settings → Time & Language → Speech
2. Make sure "Speech" is enabled
3. Test "Preview voice" button

---

## 🎯 Quick Test Commands

### Test 1: Basic pyttsx3
```python
import pyttsx3
engine = pyttsx3.init()
engine.say("Hello testing")
engine.runAndWait()
```

### Test 2: With our system
```bash
python test_voice_final.py
```

### Test 3: Multiprocess worker
```bash
python test_multiprocess_voice_working.py
```

---

## 🔍 Debug Information

Run this to get system info:
```python
import pyttsx3
engine = pyttsx3.init()
print("Rate:", engine.getProperty('rate'))
print("Volume:", engine.getProperty('volume'))
print("Voices:", [v.name for v in engine.getProperty('voices')])
```

---

## 💡 Alternative Solution: Use Visual Indicators

Agar voice nahi chal raha, hum visual indicators enhance kar sakte hain:

1. Larger text on screen
2. Color-coded feedback (Red = wrong, Green = good)
3. Progress bars
4. Flashing indicators for violations

Would you like me to add enhanced visual feedback as backup?

---

## 🆘 Still Not Working?

Share these details:
1. Windows version (run: `ver` in CMD)
2. Python version (run: `python --version`)
3. Audio device type (Speakers/Headphones/Bluetooth)
4. Error messages if any
5. Output of: `python test_voice_debug.py`

---

## ✅ If Voice IS Working

Great! Now you can use:
```bash
# Start the trainer
python glute_fly_trainer.py

# Follow the voice instructions
# Place phone 3-4 feet away
# Exercise with continuous voice feedback!
```

Enjoy your AI-powered workout! 💪

