#!/bin/sh
# Composite the final transparent renders onto the photos and lay out TR + EN versions.
cd "$(dirname "$0")"
mkdir -p web
BG=/home/user/zak/downloads/bg
python3 -I tools/composite.py $BG/bg_hall.jpg   out/irc_post_raw_photo.png  out/irc_comp.png  --focus 0.35,0.5  --blur 8 --dark 0.25
python3 -I tools/composite.py $BG/bg_quarry.jpg out/irnx_post_raw_photo.png out/irnx_comp.png --focus 0.45,0.55 --blur 6 --dark 0.10
for l in tr en; do
  python3 -I tools/post_layout.py out/irc_comp.png  web/imak_post_irc93_hoist_$l.jpg  --lang $l --copy irc
  python3 -I tools/post_layout.py out/irnx_comp.png web/imak_post_irnx07_quarry_$l.jpg --lang $l --copy irnx
done
ls -la web/imak_post_*
