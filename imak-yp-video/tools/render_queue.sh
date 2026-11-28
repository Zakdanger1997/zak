#!/bin/bash
# Progressive render: every 2nd frame first (enough with motion interpolation), then the rest. Resumable.
cd "$(dirname "$0")/.."
for step in ${STEPS:-2 1}; do
  echo "=== pass step=$step $(date +%T)"
  python3 tools/yp_scene.py --frames 0-479 --step $step --samples ${SAMPLES:-32} --res ${RES:-900x1600} 2>&1 | grep -E "^frame|Error" | grep -v CUEW
done
echo "=== ALL DONE $(date +%T)"
