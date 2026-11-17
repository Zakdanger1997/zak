#!/usr/bin/env bash
# Download the CC0 sky HDRI used to light the scene (Poly Haven — free for commercial use).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p hdri
URL="https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/4k/the_sky_is_on_fire_4k.hdr"
if [ ! -s hdri/the_sky_is_on_fire_4k.hdr ]; then
  curl -L --fail -o hdri/the_sky_is_on_fire_4k.hdr "$URL"
fi
ls -lh hdri/
