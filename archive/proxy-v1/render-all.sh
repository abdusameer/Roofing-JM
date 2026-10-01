#!/bin/bash
# Rebuilds the master scene and every derived asset for the roof-sequence prototype.
# Raw frames go to review/ (git-ignored); only encoded media, stills and anchor JSON
# land in prototype/roof-sequence/media/.
#   tools/render-all.sh            full quality
#   SAMPLES=8 SCALE=50 tools/render-all.sh   quick draft
set -euo pipefail
cd "$(dirname "$0")/.."
B=/Applications/Blender.app/Contents/MacOS/Blender
SAMPLES=${SAMPLES:-24}
SCALE=${SCALE:-100}
MEDIA=prototype/roof-sequence/media
# Raw PNG frames are large and disposable. Keep them OUTSIDE ~/Documents: that folder syncs to
# iCloud on this machine, and uploading ~800 frames stalled the first render for over an hour.
FRAMES=${FRAMES_DIR:-${TMPDIR:-/tmp}/roofing-jm-frames}
STAGES=${STAGES:-scene anchors stills frames encode}
mkdir -p "$FRAMES/desktop" "$FRAMES/portrait" "$MEDIA"
has() { [[ " $STAGES " == *" $1 "* ]]; }

has scene && { "$B" -b --factory-startup -P blender/build_scene.py -- --out review/roof.blend | grep -E "saved|rror" || true; }

for cam in desktop portrait; do
  has anchors && { "$B" -b review/roof.blend -P blender/render.py -- --camera "$cam" --anchors "$MEDIA/anchors-$cam.json" | grep -E "anchors|rror" || true; }
  has stills && { "$B" -b review/roof.blend -P blender/render.py -- --camera "$cam" --stills --out "$MEDIA/stills-$cam" --fmt WEBP --quality 78 --scale "$SCALE" --samples "$SAMPLES" | grep -E "done|rror" || true; }
  has frames && { "$B" -b review/roof.blend -P blender/render.py -- --camera "$cam" --frames 0-405 --skip-existing --out "$FRAMES/$cam" --fmt PNG --scale "$SCALE" --samples "$SAMPLES" | grep -E "frame|done|rror" || true; }
done

# Short GOP and no B-frames so any frame is a cheap seek in both scroll directions.
has encode && for cam in desktop portrait; do
  ffmpeg -loglevel error -y -framerate 30 -i "$FRAMES/$cam/%04d.png" \
    -c:v libx264 -preset slow -crf "${CRF:-24}" -pix_fmt yuv420p -g 6 -keyint_min 6 -sc_threshold 0 -bf 0 \
    -movflags +faststart -an "$MEDIA/sequence-$cam.mp4"
done
ls -la "$MEDIA" "$MEDIA"/stills-*
