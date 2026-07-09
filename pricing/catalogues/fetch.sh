#!/usr/bin/env bash
# Re-download all current I-MAK catalogues into this folder.
# Source: https://www.imakreduktor.com/catalogs/  (captured 2026-07-09)
set -euo pipefail
cd "$(dirname "$0")"

urls=(
  "https://www.imakreduktor.com/wp-content/uploads/2026/07/IR_Katalog_2026_Rev.01.pdf"
  "https://www.imakreduktor.com/wp-content/uploads/2026/02/IRK-Katalog-web.pdf"
  "https://www.imakreduktor.com/wp-content/uploads/2026/02/YP-Katalog-2026.pdf"
  "https://www.imakreduktor.com/wp-content/uploads/2026/07/IRS_IRSD_Katalog_2026_Rev.01.pdf"
  "https://www.imakreduktor.com/wp-content/uploads/2024/05/IRC-Katalog-2024-Rev.00.pdf"
  "https://www.imakreduktor.com/wp-content/uploads/2024/05/IRNX-Katalog-2024-Rev.00.pdf"
  "https://www.imakreduktor.com/wp-content/uploads/2024/05/IRO-Katalog-2024-Rev.00.pdf"
  "https://www.imakreduktor.com/wp-content/uploads/2024/05/4DS-Katalog-2024-Rev.00.pdf"
  "https://www.imakreduktor.com/wp-content/uploads/2024/05/ADK-ADS-Katalog-2024-Rev.00.pdf"
  "https://www.imakreduktor.com/wp-content/uploads/2025/07/MA-MK-Katalog-2025-Rev.00.pdf"
  "https://www.imakreduktor.com/wp-content/uploads/2026/05/A-Katalog-2024-Rev.00.pdf"
  "https://www.imakreduktor.com/wp-content/uploads/2026/01/M-Katalog.pdf"
  "https://www.imakreduktor.com/wp-content/uploads/2026/01/Mini-Katalog.pdf"
  "https://www.imakreduktor.com/wp-content/uploads/2026/01/Genel-Ozet-Mini-Katalog-2026-Rev.00_compressed.pdf"
  "https://www.imakreduktor.com/wp-content/uploads/2025/07/B00_2025_TR-EN.pdf"
  "https://www.imakreduktor.com/wp-content/uploads/2025/04/B09_2024_TR-EN.pdf"
)

for u in "${urls[@]}"; do
  f="$(basename "$u")"
  echo "Fetching $f ..."
  curl -fSL -o "$f" "$u"
done
echo "Done. $(ls -1 *.pdf | wc -l) catalogues in $(pwd)"
