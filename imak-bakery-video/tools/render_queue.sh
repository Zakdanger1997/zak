#!/bin/bash
cd "$(dirname "$0")/.."
for step in ${STEPS:-4 2}; do
  echo "=== step $step $(date +%T)"
  python3 tools/bakery_scene.py --frames 0-1296 --step $step --samples ${SAMPLES:-20} --res ${RES:-1280x720} 2>&1 | grep -E "^frame|Error" | grep -v "Not freed\|CUEW"
done
echo "=== ALL DONE $(date +%T)"
