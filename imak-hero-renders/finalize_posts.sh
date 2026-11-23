#!/bin/sh
# Render the two photoreal product posts (HDRI-lit, real floor shadow) and lay out TR + EN versions.
# Needs the Poly Haven 16K HDRIs in /home/user/zak/downloads/bg/hdri (see README).
cd "$(dirname "$0")"
mkdir -p web out
for u in irc irnx; do
  [ -f out/photo_$u.png ] || UNIT=$u python3 tools/scene_photo_product.py --samples ${SAMPLES:-384} > out/log_photo_$u.txt 2>&1
  for l in tr en; do
    python3 -I tools/post_layout.py out/photo_$u.png web/imak_post_${u}_$l.jpg --lang $l --copy $u
  done
done
echo ALLDONE
