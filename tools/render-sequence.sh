#!/usr/bin/env bash
# Production render of the roof sequence (photoreal rework).
#   tools/render-sequence.sh [frames_dir]
# 1. builds blender/roof_master.blend from blender/prod/*.py (+ cameras.json, timeline.json)
# 2. renders the desktop sequence (every master frame, 1600x900) and the portrait sequence
#    (112 frames sampling the same master timeline, 900x1200) as PNG
# 3. projects the layer-marker anchors through both cameras
# 4. encodes WebP frames + stills and writes media/seq/manifest.json (tools/build_media.py)
# PNG frames stay outside the repo (default: $TMPDIR/roof-frames); iCloud-synced folders stall on
# thousands of large files. Re-running resumes: finished frames are skipped.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BLENDER="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"
FRAMES="${1:-${TMPDIR:-/tmp}/roof-frames}"
PORTRAIT_COUNT="${PORTRAIT_COUNT:-112}"
SAMPLES_D="${SAMPLES_D:-40}"; SAMPLES_P="${SAMPLES_P:-32}"
mkdir -p "$FRAMES/desktop" "$FRAMES/portrait"
cd "$ROOT"

if [ "${SKIP_BUILD:-0}" != "1" ]; then
  "$BLENDER" -b --factory-startup -P blender/prod/build.py -- --out blender/roof_master.blend 2>&1 | grep --line-buffered -E "^saved|panel check|Error|Traceback"
fi
"$BLENDER" -b blender/roof_master.blend -P blender/prod/render.py -- --camera desktop --frames 0-167 \
  --samples "$SAMPLES_D" --out "$FRAMES/desktop" --skip-existing 2>&1 | grep --line-buffered -E "^\[desktop\]|^done|Error|Traceback"
"$BLENDER" -b blender/roof_master.blend -P blender/prod/render.py -- --camera portrait --count "$PORTRAIT_COUNT" \
  --samples "$SAMPLES_P" --out "$FRAMES/portrait" --skip-existing 2>&1 | grep --line-buffered -E "^\[portrait\]|^done|Error|Traceback"
"$BLENDER" -b blender/roof_master.blend -P blender/prod/export_anchors.py -- --portrait-count "$PORTRAIT_COUNT" \
  --out "$FRAMES/anchors.json" 2>&1 | grep --line-buffered -E "^anchors|^wrote|Error|Traceback"
python3 tools/build_media.py --desktop "$FRAMES/desktop" --portrait "$FRAMES/portrait" --anchors "$FRAMES/anchors.json"
