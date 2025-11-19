#!/bin/bash

# SOURCE FOLDER (where downloads are)
SRC="$HOME/Downloads"

# DESTINATION FOLDER (your project)
DEST="$HOME/ai/ai_trainer/src/frontend/static/images/equipments"

# Make sure dest folder exists
mkdir -p "$DEST"

# Install ImageMagick if missing
if ! command -v convert &> /dev/null
then
    echo "ImageMagick not found. Installing..."
    sudo pacman -S imagemagick --noconfirm
fi

echo "Converting PNG → JPG and moving files…"

# Process all PNG images in Downloads
for img in "$SRC"/*.png; do
    [ -e "$img" ] || continue

    # Get base filename (no path, no extension)
    base=$(basename "$img" .png)

    # Convert to clean snake_case
    clean=$(echo "$base" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr '_' '-')

    # Final output path
    output="$DEST/${clean}.jpg"

    # Convert PNG → JPG
    convert "$img" "$output"

    echo "✔ Converted & moved: $img → $output"

    # OPTIONAL: remove original PNG
    rm "$img"
done

echo "🎉 All images converted and moved successfully!"
