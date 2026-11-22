#!/bin/sh
cd "$(dirname "$0")"
while pgrep -f "tools/scene_conveyor.py" > /dev/null; do sleep 30; done
./render_all.sh agitator lineup closeup pump
