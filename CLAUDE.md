# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is **Salesably Marketplace**, a collection of Claude Code plugins for sales and marketing teams. It functions as a marketplace that users add to Claude Code, then install individual plugins from.

## Architecture

```
salesably-marketplace/
├── .claude-plugin/
│   └── marketplace.json     # Marketplace manifest - lists available plugins
├── marketing-skills/        # Marketing plugin (10 skills)
│   ├── .claude-plugin/
│   │   └── plugin.json      # Plugin manifest - declares skills path
│   ├── README.md            # Plugin documentation
│   └── skills/              # 10 marketing skills (each folder has SKILL.md)
│       ├── brand-voice/
│       ├── positioning-angles/
│       ├── keyword-research/
│       ├── lead-magnet/
│       ├── direct-response-copy/
│       ├── seo-content/
│       ├── newsletter/
│       ├── email-sequences/
│       ├── content-atomizer/
│       └── orchestrator/
├── sales-skills/            # Sales plugin (9 skills)
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── README.md
│   └── skills/
│       ├── powerful-framework/
│       ├── prospect-research/
│       ├── account-qualification/
│       ├── company-intelligence/
│       ├── cold-call-scripts/
│       ├── call-analysis/
│       ├── follow-up-emails/
│       ├── multithread-outreach/
│       └── sales-orchestrator/
├── rea/                     # REA plugin (MCP server + 1 skill, vendored from morluto/rea)
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── .mcp.json            # Launches `npx -y rea-agents@<version> mcp`
│   ├── LICENSE              # Upstream MIT license
│   ├── README.md
│   └── skills/
│       └── reverse-engineer-anything/   # SKILL.md + references/ copied from upstream
├── ai-video-studio/         # Video plugin (1 skill + freevid pipeline: edge-tts, Pollinations, ffmpeg)
│   ├── .claude-plugin/plugin.json
│   ├── skills/make-ai-video/SKILL.md
│   ├── tools/               # freevid.py, styles.json, requirements.txt
│   ├── fonts/               # Cairo-Bold.ttf for Arabic captions
│   └── examples/
├── yt-dlp/                  # Downloader plugin (1 skill wrapping the yt-dlp CLI; no vendored code)
│   ├── .claude-plugin/plugin.json
│   └── skills/yt-dlp/       # SKILL.md + references/recipes.md
├── gearbox-explainer-video/ # Stand-alone project: hand-animated Arabic explainer short (Canvas + edge-tts + ffmpeg)
├── imak-mixing-brochure/    # Stand-alone print project (not a plugin): i.Mak 12-page A4 mixing/agitating brochure
│   ├── brochure.html/.css   # Layout (absolute mm positions); build with tools/build_pdf.js (Playwright)
│   ├── assets/              # Processed i.Mak images (tools/prepare_assets.py); SOURCES.md lists originals
│   └── imak-mixing-agitating-brochure-EN.pdf
├── imak-drive-handbook/     # Stand-alone web app (not a plugin): interactive 3D handbook + LinkedIn video
│   ├── index.html, src/     # three.js (vendored in vendor/), lessons in src/lessons.js, video script in src/demo.js
│   ├── models/              # i.Mak GLBs converted from the official STEP models (tools/parts_to_glb.py)
│   ├── tools/               # record.js (frame-by-frame MP4), shot.js, carousel.py, build_standalone.js
│   ├── dist/                # imak-drive-handbook.html: single self-contained file (works by double-click)
│   ├── video/               # drive-handbook-4x5.mp4 (1080x1350)
│   └── linkedin/            # POST.md (post text + plan), carousel.pdf, cover.jpg
├── imak-irc-video/          # Stand-alone video project (not a plugin): IRC crane hoist video, 9:16
│   ├── tools/               # irc_scene.py (Blender), render_queue.sh, interp.py, voiceover.py, timeline.py, soundtrack.py, compose.js
│   ├── compose.html         # frame-by-frame compositor; assets/ (logos, photos + SOURCES.md), audio/, video/
│   └── render/              # gitignored render frames
├── imak-mamk-video/         # Stand-alone video project: MA/MK conveyor drives in mines/steel, 9:16 (same pipeline; tools/mamk_scene.py + scenekit.py)
├── imak-story-video/        # Stand-alone video: i.Mak company story in a paper-collage style, 16:9 (story.html recorded by tools/compose.js)
├── imak-bakery-video/       # Stand-alone video: "Solutions for baking process", clay-style 3D line with i.Mak drives, 16:9
├── imak-reduktor-secim/     # Stand-alone web app (not a plugin): i.Mak gearbox selector
│   ├── index.html           # Single-page app, TR/EN, no dependencies
│   ├── data/                # Generated: catalog.js (performance tables), applications.js
│   ├── tools/               # parse_catalogs.py (PDF -> JSON), build_data.py, apps.py
│   └── README.md
└── README.md                # Marketplace installation instructions
```

## Key Concepts

**Marketplace vs Plugin**: The root directory is a marketplace container. Individual plugins (like `marketing-skills`, `sales-skills`) live in subdirectories with their own `plugin.json`.

**Video plugin**: `ai-video-studio/` is a real plugin (registered in `marketplace.json`). Its pipeline lives in `tools/freevid.py`; keep every stage idempotent and keep the style cards in `tools/styles.json`. `gearbox-explainer-video/` is a one-off project built before the plugin existed and is not a plugin.

**Downloader plugin**: `yt-dlp/` is a hand-written skill that drives the upstream [yt-dlp](https://github.com/yt-dlp/yt-dlp) CLI (installed by the user with pip); it does not vendor upstream code. When yt-dlp changes flags, re-check every flag in `SKILL.md` and `references/recipes.md` against `yt-dlp --help`.

**Non-plugin content**: `imak-mixing-brochure/` is a print brochure built from HTML with Playwright; use only i.Mak images (record each in its `SOURCES.md`) and i.Mak catalogue figures, then rebuild the PDF. `imak-drive-handbook/` is a static three.js app (no build step for development; `tools/build_standalone.js` regenerates `dist/imak-drive-handbook.html`, the single file users open by double-click, so rebuild it after every change); its LinkedIn video is rendered from the scripted walkthrough in `src/demo.js` with `tools/record.js`, so change the script and re-record rather than editing the MP4. Keep every number in `src/lessons.js` physically correct or traceable to the i.Mak catalogue. `imak-reduktor-secim/` is a browser application, not a Claude Code plugin, and is not registered in `marketplace.json`. Its `data/*.js` files are generated by the scripts in its `tools/` folder from i.Mak's public catalogue PDFs; edit the scripts and rebuild rather than editing the data by hand (see its README).

**Vendored plugins**: `rea/` wraps the upstream [morluto/rea](https://github.com/morluto/rea) project. Its skill folder is a verbatim copy of upstream `.agents/skills/reverse-engineer-anything/`; to upgrade, bump the pinned `rea-agents` version in `rea/.mcp.json` and `rea/.claude-plugin/plugin.json`, then re-copy the skill folder. Do not hand-edit the copied SKILL.md.

**Skills**: Each skill is a markdown file (`SKILL.md`) with YAML frontmatter containing `name` and `description`. The markdown body provides detailed instructions Claude uses when the skill is invoked.

**Marketing Skill Layers**:
- Foundation: brand-voice, positioning-angles
- Strategy: keyword-research, lead-magnet
- Execution: direct-response-copy, seo-content, newsletter, email-sequences
- Distribution: content-atomizer, orchestrator

**Sales Skill Layers**:
- Foundation: powerful-framework, prospect-research
- Strategy: account-qualification, company-intelligence
- Execution: cold-call-scripts, call-analysis, follow-up-emails, multithread-outreach
- Orchestration: sales-orchestrator

## Working with Skills

Skills follow this structure:
```markdown
---
name: skill-name
description: When to trigger this skill...
---

# Skill Name

[Detailed instructions, frameworks, and output formats]
```

The `description` field in frontmatter determines when Claude automatically suggests using the skill.

## Adding New Skills

1. Create a new directory under the appropriate plugin's `skills/` folder
   - Marketing skills: `marketing-skills/skills/`
   - Sales skills: `sales-skills/skills/`
2. Add a `SKILL.md` file with proper frontmatter
3. Skills are auto-discovered via the `"skills": "./skills"` path in `plugin.json`

## Adding New Plugins

1. Create a new directory at the repository root
2. Add `.claude-plugin/plugin.json` with plugin metadata
3. Register in `.claude-plugin/marketplace.json` under the `plugins` array

## MCP Tool Integrations

The sales-skills plugin includes optional MCP server integrations for enhanced research:

**Location:** `sales-skills/.mcp.json`

**Available Tools:**
- **Perplexity** - AI-powered web search
- **Exa** - Semantic search for companies/people
- **Apify** - Web scraping and data extraction
- **Hunter.io** - Email finding and verification

**Configuration:**
- All tools are disabled by default (`"disabled": true`)
- Users set API keys as environment variables
- Enable tools by changing `"disabled": false` in `.mcp.json`
- See `sales-skills/README.md` for detailed setup instructions
