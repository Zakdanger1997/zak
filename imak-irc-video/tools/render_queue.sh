#!/bin/bash
# Progressive overnight render: every 4th frame of every shot first (an animatic to edit with),
# then every 2nd, then the rest. Frames already on disk are skipped, so it can be restarted.
cd "$(dirname "$0")/.."
RES=${RES:-900x1600}
SAMPLES=${SAMPLES:-24}
declare -A RANGE=( [hoist]=0-143 [spline]=0-95 [dark]=0-95 [studio]=0-191 [hoistwide]=0-143 )
for step in ${STEPS:-4 2}; do
  for shot in hoist spline dark studio hoistwide; do
    echo "=== pass step=$step shot=$shot $(date +%T)"
    python3 tools/irc_scene.py $shot --frames ${RANGE[$shot]} --step $step --samples $SAMPLES --res $RES 2>&1 | grep -E "^frame|Error" | grep -v "Not freed\|CUEW"
  done
done
echo "=== ALL DONE $(date +%T)"
