#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMES_DIR="${ROOT_DIR}/assembly_frames_png"
STL_DIR="${ROOT_DIR}/assembly_frames_stl"
VIDEO_OUT="${ROOT_DIR}/assembly_animation.mp4"
CAD_DIR="${ROOT_DIR}/CAD"
FRAMERATE=12

if command -v blender >/dev/null 2>&1; then
  BLENDER_CMD="blender"
elif [ -x "/Applications/Blender.app/Contents/MacOS/Blender" ]; then
  BLENDER_CMD="/Applications/Blender.app/Contents/MacOS/Blender"
else
  echo "Error: blender is required to render frames."
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Error: ffmpeg is required to assemble the video."
  exit 1
fi

mkdir -p "${FRAMES_DIR}" "${STL_DIR}"
rm -f "${FRAMES_DIR}"/frame_*.png

if command -v conda >/dev/null 2>&1 && conda env list | grep -q "^cq "; then
  PYTHON_CMD="conda run -n cq python"
else
  echo "Error: conda env 'cq' not found; required for STEP->STL conversion."
  exit 1
fi

step_files=( "${CAD_DIR}"/assembly_frame_*.step )
if [ ! -e "${step_files[0]}" ]; then
  echo "No assembly_frame_*.step found in CAD/. Run: python scripts/generate_assembly_animation.py"
  exit 1
fi

stl_files_count=$(find "${STL_DIR}" -name "assembly_frame_*.stl" -maxdepth 1 2>/dev/null | wc -l | tr -d ' ')
if [ "${stl_files_count}" -gt 0 ]; then
  echo "STL frames already present, skipping STEP conversion."
else
  echo "Converting STEP frames to STL..."
  ${PYTHON_CMD} "${ROOT_DIR}/convert_assembly_frames.py"
  conv_status=$?
  if [ "${conv_status}" -ne 0 ]; then
    echo "Error: STEP->STL conversion failed."
    exit "${conv_status}"
  fi
fi

echo "Rendering frames with Blender..."
frame=0
stl_files=()
while IFS= read -r stl; do
  stl_files+=( "${stl}" )
done < <(find "${STL_DIR}" -name "assembly_frame_*.stl" -maxdepth 1 | sort)
if [ ${#stl_files[@]} -eq 0 ]; then
  echo "Error: no STL frames found in ${STL_DIR}."
  exit 1
fi

for stl in "${stl_files[@]}"; do
  frame_name=$(printf "frame_%02d.png" "${frame}")
  "${BLENDER_CMD}" -b -P "${ROOT_DIR}/render_stl_blender.py" -- "${stl}" "${FRAMES_DIR}/${frame_name}"
  if [ $? -ne 0 ]; then
    echo "Error: Blender failed while rendering ${stl}."
    exit 1
  fi
  frame=$((frame + 1))
done

frame_count=$(find "${FRAMES_DIR}" -name "frame_*.png" -maxdepth 1 2>/dev/null | wc -l | tr -d ' ')
if [ "${frame_count}" -eq 0 ]; then
  echo "Error: no frames rendered. Aborting video assembly."
  exit 1
fi
echo "Rendered ${frame_count} frames."

echo "Assembling video..."
ffmpeg -y -framerate "${FRAMERATE}" -i "${FRAMES_DIR}/frame_%02d.png" \
  -c:v libx264 -pix_fmt yuv420p "${VIDEO_OUT}"

echo "✓ Video exported: ${VIDEO_OUT}"
