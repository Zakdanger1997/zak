#!/bin/bash
# Progressive render of every MA/MK shot (every 4th frame, then every 2nd); existing frames are skipped.
cd "$(dirname "$0")/.."
RES=${RES:-900x1600}
SAMPLES=${SAMPLES:-24}
declare -A RANGE=( [drive]=0-143 [conveyor]=0-143 [steel]=0-143 [dark]=0-95 [studio]=0-191 )
[ -f render/lineup_still_0000.png ] && [ "$(python3 -c "from PIL import Image;print(Image.open('render/lineup_still_0000.png').size[0])")" = 3200 ] || \
  python3 tools/mamk_scene.py lineup --still 0 --samples 40 --res 3200x1800 2>&1 | grep -E "still /|Error" | grep -v "Not freed\|CUEW"
[ -f render/duo_still_0000.png ] || python3 tools/mamk_scene.py duo --still 0 --samples 40 --res 1440x2560 2>&1 | grep -E "still /|Error" | grep -v "Not freed\|CUEW"
for step in ${STEPS:-4 2}; do
  for shot in drive conveyor steel dark studio; do
    echo "=== pass step=$step shot=$shot $(date +%T)"
    python3 tools/mamk_scene.py $shot --frames ${RANGE[$shot]} --step $step --samples $SAMPLES --res $RES 2>&1 | grep -E "^frame|Error" | grep -v "Not freed\|CUEW"
  done
done
echo "=== ALL DONE $(date +%T)"
