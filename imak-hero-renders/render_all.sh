#!/bin/sh
# Render every hero scene at 3840x2160 (Cycles, CPU). Each one takes roughly an hour on 4 cores.
# Usage: ./render_all.sh [scene names...]   (default: all five)
cd "$(dirname "$0")"
mkdir -p out
SCENES="${*:-conveyor agitator lineup closeup pump}"
for s in $SCENES; do
  if [ -f "out/hero_${s}_"*.png ] 2>/dev/null; then echo "skip $s (exists)"; continue; fi
  echo "=== $s $(date)"
  python3 "tools/scene_$s.py" > "out/log_$s.txt" 2>&1
  echo "exit $? $(date)" >> "out/log_$s.txt"
  grep -E "^rendered" "out/log_$s.txt"
done
echo ALLDONE
