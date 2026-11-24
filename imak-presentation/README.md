# I-MAK Presentation 2025 – updated

The source is the company deck shared from SharePoint ("I-MAK Presentation 2025.pptx"). The output is `I-MAK Presentation 2025 - updated.pptx` (gitignored, about 157 MB).

## Changes
- **Simpler design:** the red diagonal decoration ("Group 6") is removed from the slide master and title layout. The white corner logo (media/image2.png) is recoloured to i.Mak red so it shows on white.
- **Slides 2–3 (history):** rebuilt as animated collage infographics in the style of the company story video. A red hand-drawn line draws itself, then cut-out photos, years and captions appear one after another. EGASEN is removed.
- **Slide 4:** 233 employees changed to 275.
- **New slide 7, "Service centres around the globe":** a world map with the partners from imakreduktor.com/business-partners (EGASEN excluded) and the assembly centres SIPCO (USA) and Hudaco (South Africa).
- **Every slide:** fade transitions, plus staged entrance animations that play automatically (titles, pictures, bullets paragraph by paragraph). Existing video playback is kept.
- **Slide 9 video:** re-encoded from 250 MB to 90 MB (1080p, H.264), visually the same.

## Rebuild
`tools/prep_assets.py` creates the collage assets. `tools/build_deck.py in.pptx out.pptx` applies the slide edits to a deck whose master decoration has already been removed (see the script header).
