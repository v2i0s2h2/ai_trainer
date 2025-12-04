#!/bin/bash

echo "🔊 AI Trainer - Browser Voice Fix Script"
echo "========================================="
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  This script is for Linux only"
    exit 1
fi

# Step 1: Install TTS engine
echo "📦 Step 1: Installing TTS engines..."
if command -v pacman &> /dev/null; then
    echo "   Using pacman (Arch Linux detected)"
    sudo pacman -S --needed espeak-ng speech-dispatcher
elif command -v apt &> /dev/null; then
    echo "   Using apt (Debian/Ubuntu detected)"
    sudo apt install -y espeak-ng speech-dispatcher
else
    echo "   ⚠️  Package manager not recognized. Install manually:"
    echo "      - espeak-ng"
    echo "      - speech-dispatcher"
    exit 1
fi

echo "   ✅ Packages installed"
echo ""

# Step 2: Enable and start speech-dispatcher
echo "🚀 Step 2: Starting speech-dispatcher service..."
systemctl --user enable speech-dispatcherd --now 2>/dev/null || \
    systemctl --user enable speech-dispatcher --now

# Wait a moment for service to start
sleep 2

# Check status
if systemctl --user is-active speech-dispatcherd &>/dev/null || \
   systemctl --user is-active speech-dispatcher &>/dev/null; then
    echo "   ✅ speech-dispatcher is running"
else
    echo "   ⚠️  speech-dispatcher may not be running properly"
    echo "   Try manually: systemctl --user status speech-dispatcherd"
fi

echo ""

# Step 3: Test espeak
echo "🎤 Step 3: Testing espeak..."
if command -v espeak-ng &> /dev/null; then
    echo "   Speaking test message..."
    espeak-ng "Voice test successful" 2>/dev/null
    echo "   ✅ espeak-ng is working"
else
    echo "   ❌ espeak-ng not found"
fi

echo ""

# Step 4: Instructions for Chrome
echo "🌐 Step 4: Chrome/Chromium Setup"
echo "   To enable voices in Chrome:"
echo ""
echo "   1. Close ALL Chrome windows completely"
echo "   2. Start Chrome with this command:"
echo ""
if command -v google-chrome &> /dev/null; then
    echo "      google-chrome --enable-speech-dispatcher"
elif command -v chromium &> /dev/null; then
    echo "      chromium --enable-speech-dispatcher"
elif command -v google-chrome-stable &> /dev/null; then
    echo "      google-chrome-stable --enable-speech-dispatcher"
else
    echo "      chrome --enable-speech-dispatcher"
fi
echo ""
echo "   3. Open: http://localhost:5174/workout/squat"
echo "   4. Open Console (F12) and run:"
echo "      speechSynthesis.getVoices()"
echo ""
echo "   You should see an array of voices (not empty)"
echo ""

# Step 5: Create a desktop launcher (optional)
echo "💡 Optional: Create desktop launcher?"
read -p "   Create Chrome launcher with speech enabled? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    LAUNCHER_PATH="$HOME/.local/share/applications/chrome-with-speech.desktop"
    
    # Find Chrome executable
    CHROME_EXEC=""
    if command -v google-chrome &> /dev/null; then
        CHROME_EXEC="google-chrome"
    elif command -v chromium &> /dev/null; then
        CHROME_EXEC="chromium"
    elif command -v google-chrome-stable &> /dev/null; then
        CHROME_EXEC="google-chrome-stable"
    fi
    
    if [ -n "$CHROME_EXEC" ]; then
        mkdir -p "$HOME/.local/share/applications"
        cat > "$LAUNCHER_PATH" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Chrome (with Speech)
Comment=Chrome with speech-dispatcher enabled
Exec=$CHROME_EXEC --enable-speech-dispatcher %U
Icon=google-chrome
Terminal=false
Categories=Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml+xml;
EOF
        echo "   ✅ Launcher created: $LAUNCHER_PATH"
        echo "   You can now launch Chrome from your app menu"
    else
        echo "   ❌ Chrome not found, skipping launcher"
    fi
fi

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "  1. Close all Chrome windows"
echo "  2. Start Chrome with --enable-speech-dispatcher flag"
echo "  3. Go to workout page and click 'Enable Voice'"
echo "  4. You should hear voice feedback!"
echo ""
echo "If voices still don't work:"
echo "  - Check: systemctl --user status speech-dispatcherd"
echo "  - Test: espeak-ng 'hello world'"
echo "  - Restart computer and try again"
echo ""

