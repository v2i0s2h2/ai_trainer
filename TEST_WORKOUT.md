# Test Your Live Workout! 🎉

## ✅ Phase 2 is Complete!

You can now test the **live workout screen** with real-time pose detection!

## 🚀 Quick Test

### 1. Make sure servers are running:
```bash
cd /home/vishnu/ai/ai_trainer
./scripts/dev.sh
```

You should see:
- Backend: http://localhost:8000 ✅
- Frontend: http://localhost:5174 ✅

### 2. Open your browser:
```
http://localhost:5174
```

### 3. Navigate to workout:
1. Click **"Exercises"** tab at the bottom
2. Click on **"Squats"** card
3. You'll be taken to `/workout/squat`

## 🎯 What You Should See:

### Loading Phase:
- "Connecting to camera..." spinner
- Backend opens your webcam
- "Initializing pose detection..." message

### Active Workout:
- **Video feed** with your webcam (with pose skeleton overlay)
- **Rep counter** in top-right (starts at 0)
- **Angle displays** in top-left (knee & torso angles)
- **Progress bar** at bottom showing movement (0-100%)
- **Feedback messages** like "Good form - keep going!"
- **Duration timer** and rep count at bottom
- **"End Workout"** button

## 🏋️ Try It:

1. **Stand in front of camera** (full body visible)
2. **Do squats:**
   - Stand upright (knees ~160°)
   - Squat down (knees ~70°)
   - Stand back up
3. **Watch:**
   - Rep counter should increment
   - Progress bar fills as you go down
   - Feedback messages appear
   - Angles update in real-time

## 🎨 What It Looks Like:

```
┌─────────────────────────────────────┐
│ Knee: 85°                   5       │ ← Angles & Reps
│ Torso: 72°                REPS      │
│                                      │
│    [YOUR VIDEO WITH SKELETON]       │ ← Live feed
│                                      │
│ ──────────────────── 75%            │ ← Progress
│ "Keep going - good form!"           │ ← Feedback
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ Squats        ⏱️ 0:45  🔥 5 reps   │ ← Stats
│          [End Workout]               │ ← Button
└─────────────────────────────────────┘
```

## 🐛 If Something Goes Wrong:

### No video appears:
```bash
# Check backend logs for webcam errors
# Make sure webcam isn't being used by another app
```

### WebSocket connection fails:
- Check if backend is running on port 8000
- Look at browser console (F12) for errors
- Check backend terminal for WebSocket logs

### Rep counter doesn't update:
- Make sure full body is visible in camera
- Check if pose landmarks are detected
- Look for MediaPipe warnings in backend terminal

## 📊 Expected Behavior:

✅ **Connecting Phase** (2-3 seconds)
- Loading spinner
- Backend initializes MediaPipe
- Opens webcam

✅ **Active Phase**
- Video streams at ~30fps
- Skeleton overlay on your body
- Rep counter updates when you complete a squat
- Progress bar fills when going down, empties when going up
- Feedback changes based on form

✅ **End Phase**
- Click "End Workout"
- Confirmation dialog appears
- Workout saves to database
- Returns to exercise list

## 🎯 Success Indicators:

1. **Backend logs show:**
   ```
   INFO: WebSocket connected for exercise: squat
   [VOICE] Initialized gTTS + pygame backend
   INFO: Started server process
   ```

2. **Browser console shows:**
   ```
   [Workout Store] Connecting to: ws://localhost:8000/ws/workout?exercise=squat
   [Workout Store] WebSocket connected
   [Workout Store] Message: frame
   ```

3. **You see:**
   - Your video feed
   - Skeleton overlay
   - Rep counter incrementing
   - Feedback messages changing

## 🎉 When It Works:

You'll experience:
- Real-time pose detection
- Automatic rep counting
- Form corrections as you exercise
- Smooth 30fps video
- Accurate angle measurements
- Professional-looking HUD overlay

## 📱 Test on Mobile (Optional):

Open on your phone (same WiFi):
```
http://192.168.1.12:5174/workout/squat
```

*Note: Backend webcam is on your laptop, so your phone will show the laptop's camera feed*

## 🔄 Next Time:

Just run and go to exercises:
```bash
./scripts/dev.sh
# Open http://localhost:5174
# Click Exercises → Squats
```

---

**Ready to see yourself with AI pose detection?** 💪  
Open http://localhost:5174 and click on Squats!

