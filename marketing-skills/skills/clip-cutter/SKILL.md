---
name: clip-cutter
description: Turns long-form YouTube (and other source) videos into ready-to-post vertical short clips with burned-in captions, then publishes them to TikTok. This skill should be used when repurposing podcasts, interviews, webinars, or long videos into Shorts/Reels/TikToks, building a faceless or personal clipping channel, feeding a short-form content calendar, or when someone asks to "cut clips," "make shorts," or "post to TikTok."
---

# Clip Cutter

This skill runs an end-to-end short-form video pipeline: take a long video, automatically find the most clip-worthy moments, cut them into vertical captioned clips, and publish the winners to TikTok. It orchestrates the Higgsfield MCP tools that do the actual cutting and posting.

## Objective

Convert one long-form video into multiple platform-ready short clips and get them published to TikTok with minimal manual editing, while keeping a human in the loop for the two decisions that matter: **which clips are good** and **what/when to post**.

## Prerequisites

This skill depends on the **Higgsfield MCP server** being connected (it provides the clipping and TikTok tools). Confirm access before starting:

- **Clipping** uses `personal_clipper_create` / `personal_clipper_status`.
- **Restyled AI shorts** (optional) use `shorts_studio_create` / `shorts_studio_status`.
- **Publishing** uses `tiktok_accounts` → `tiktok_prepare_publish` → `tiktok_publish` → `tiktok_publish_status`.
- **Optional scoring** uses `virality_predictor` to rank clips before posting.

If these tools are not available, tell the user this skill requires the Higgsfield MCP server and stop.

## Intake Questions

Gather these before running anything (the clipper is a long job — get the settings right the first time):

1. **Source video**: A YouTube URL (or several). The native clipper (`personal_clipper_create`) accepts **YouTube URLs only**. For a local upload or a non-YouTube source, see "Alternate sources" below.
2. **How many clips?** 1–20 per video. Default to 5–10 for a first pass.
3. **Aspect ratio**: `9:16` (TikTok/Reels/Shorts — the default), `1:1`, or `16:9`.
4. **Subtitle font**: one of the supported fonts (see below). Default `Bebas Neue` or `Montserrat` for punchy captions.
5. **Publish target**: TikTok now, TikTok drafts, or just export the files. (This skill auto-publishes to **TikTok**; see "Platform coverage.")
6. **Post mode**: `DIRECT_POST` (goes live / scheduled to profile) or `UPLOAD_TO_DRAFT` (saved to TikTok drafts for final review in-app). Default to `UPLOAD_TO_DRAFT` for the first run so nothing goes public unreviewed.
7. **Caption + hashtags**: brand voice, CTA, and hashtag set for the TikTok description. (Pull tone from the `brand-voice` skill if it exists.)

**Supported subtitle fonts:** Noto Sans, Noto Serif, Noto Sans Display, IBM Plex Sans, M PLUS Rounded 1c, Bebas Neue, Archivo Black, Unbounded, Inter, Montserrat, Bangers, Permanent Marker, Playfair Display, Caveat.

## The Pipeline

```
  ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐
  │ 1. SOURCE  │──▶│ 2. CLIP    │──▶│ 3. REVIEW  │──▶│ 4. PREP    │──▶│ 5. PUBLISH │
  │ YouTube URL│   │ auto-cut + │   │ pick best  │   │ caption +  │   │ to TikTok  │
  │            │   │ captions   │   │ (score)    │   │ hashtags   │   │            │
  └────────────┘   └────────────┘   └────────────┘   └────────────┘   └────────────┘
```

### Step 1 — Source

Collect the YouTube URL(s) and confirm the intake settings (clip count, aspect, font, post mode). Sanity-check that the video is long enough to yield the requested number of clips (a good rule of thumb: don't ask for more than ~1 clip per 2–3 minutes of source).

### Step 2 — Cut the clips

Call `personal_clipper_create` with the URLs, `clips_num`, `clip_aspect`, and `subtitle_font`.

- **This is a long-running job — 30+ minutes is normal.** Set expectations with the user.
- The tool returns a job/row id. Poll `personal_clipper_status` with that id.
- Do **not** busy-wait in a tight loop. Poll on a sensible interval, and for very long jobs prefer scheduling a check-in (e.g. `send_later`) over blocking.
- When the job completes, you'll have a set of clips, each already cut to the chosen aspect ratio with burned-in subtitles.

### Step 3 — Review & rank

Never auto-post everything. Present the finished clips to the user and help them pick.

- Optionally run `virality_predictor` on each clip to get a hook-strength / retention / engagement read, and sort by score.
- Recommend the top N and say **why** (strong hook in first 3s, self-contained payoff, clear CTA moment).
- Let the user approve the final set. This is a required human checkpoint.

### Step 4 — Prep each clip for posting

For every approved clip, assemble the TikTok metadata:

- **Title/caption** (≤150 chars): hook-forward, matches brand voice, no em-dashes.
- **Description** (≤4000 chars): context + CTA + hashtags.
- **Hashtags**: 3–6 relevant tags (mix broad + niche). Avoid banned/spammy tags.
- **AIGC disclosure**: if any clip was AI-generated or AI-restyled (e.g. via `shorts_studio_create`), it must be flagged as AI-generated (`is_aigc: true`) at publish time.
- The clip's media URL must be a **Higgsfield-hosted asset** — TikTok requires a verified source domain, so publish clips produced by the Higgsfield tools directly (don't re-host elsewhere first).

### Step 5 — Publish to TikTok

1. `tiktok_accounts` — confirm there's an `active` account and grab its `connector_id`.
   - No accounts → run `tiktok_connect` and have the user authorize.
   - Account in `error` → run `tiktok_reconnect`.
2. `tiktok_prepare_publish` — pass `connector_id`, `mode` (`DIRECT_POST` or `UPLOAD_TO_DRAFT`), `media_type: VIDEO`, the Higgsfield `video_url`, and (for `DIRECT_POST`) `video_duration_sec`. This returns the required confirmations, privacy options, and a `publish_session_id`.
3. **Show the user the preview and choices** (privacy level, comment/duet/stitch, any required declarations). Collect explicit approval — this is a required human checkpoint, especially for `DIRECT_POST`.
4. `tiktok_publish` — pass the `publish_session_id`, set `user_confirmed` and `preview_confirmed` true, and set every flag the prepare step listed under `required_confirmations`. For `DIRECT_POST`, pick a `privacy_level` (default `SELF_ONLY` or `PUBLIC_TO_EVERYONE` per the user's choice). Returns a `publish_id`.
5. `tiktok_publish_status` — poll until the post is confirmed live or saved to drafts. Report the result (and link) back to the user.

Repeat Step 5 per clip. Space multiple posts out rather than dumping them all at once.

## Alternate sources & AI restyling

- **Non-YouTube / local video**: `personal_clipper_create` only takes YouTube URLs. For an uploaded file, use `media_upload_widget` to upload, then `shorts_studio_create` to restyle a 4–120s source into AI-generated shorts with a style preset (`shorts_studio_list_presets` / `shorts_studio_create_preset`). This is **paid / reserves credits** and output is AI-generated, so it must be published with `is_aigc: true`.
- **Reframing an existing horizontal clip** to vertical: use `reframe`.
- **Upscaling** a low-res clip before posting: use `upscale_video`.

## Platform coverage

- **TikTok**: fully automated end-to-end via the Higgsfield `tiktok_*` tools (connect → prepare → publish → status).
- **YouTube Shorts / Instagram Reels**: **not auto-published by this skill** — there is no connected YouTube/Instagram upload tool in the default setup. The clips produced here (9:16 with captions) are ready to upload manually to those platforms. If YouTube/IG auto-upload is needed, it would require adding those platform APIs (YouTube Data API OAuth, Instagram Graph API) as separate integrations. State this limitation plainly rather than implying auto-upload.

## Output Format

When running this skill, deliver:

1. **Run plan**: source, clip count, aspect, font, post mode — confirmed before starting.
2. **Job status**: the clipper job id and progress updates (it's a long job).
3. **Clip review table**: each clip with an optional virality score and a keep/cut recommendation.
4. **Post metadata**: caption, description, and hashtags per approved clip.
5. **Publish results**: TikTok `publish_id`, final status (live / draft), and any links.
6. **Manual-upload handoff** (if requested): the exported clips ready for YouTube/IG.

## Guardrails

- **Two human checkpoints are mandatory**: approving the clip selection (Step 3) and approving the TikTok publish (Step 5). Never post to a public profile without explicit sign-off.
- Default the first run to `UPLOAD_TO_DRAFT` so nothing goes live unreviewed.
- Always disclose AI-generated/restyled content (`is_aigc: true`).
- Respect the source's copyright/usage rights — only clip content the user is allowed to repurpose.
- The clipper is a 30+ minute job; don't block on it — set expectations and poll or schedule a check-in.

## Cross-References

- Pair with `content-atomizer` — clips are the short-form leg of a full atomization plan.
- Pull caption tone from `brand-voice` for consistent hooks and CTAs.
- Use `positioning-angles` to decide which moments to feature for a given audience.
- Feed the best-performing clips back into `newsletter` and other channels.
