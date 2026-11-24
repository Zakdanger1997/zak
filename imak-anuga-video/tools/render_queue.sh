#!/bin/bash
# Render the three 3D shots (every 2nd frame, then every frame left over if time allows).
cd "$(dirname "$0")/.."
for step in ${STEPS:-2}; do
  for shot in ${SHOTS:-hero conveyor lineup}; do
    echo "=== $shot step $step $(date +%T)"
    python3 tools/anuga_scene.py --shot $shot --step $step --samples ${SAMPLES:-20} --res ${RES:-1280x720} 2>&1 | grep -E "^frame|Error" | grep -v CUEW
  done
done
echo "=== ALL DONE $(date +%T)"
