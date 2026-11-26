# I-MAK LinkedIn data collection notes (2026-11-26)

Page: "I-MAK REDUKTOR - Gearboxes and drives", https://www.linkedin.com/company/i-mak---gearboxes (company id 5033019).
Window wanted: 1 Jan to 26 Nov 2026. Everything below was collected logged-out, without paid APIs, and without getting around any block.

## What is in the files

- `posts.json`: 10 entries, sorted by date. 9 are original posts by the page (8 Oct to 16 Nov 2026). 1 is a repost without comment (3 Oct 2026) of a Makina İmalatçıları Birliği (MIB) post that names I-MAK. Its reactions and comments belong to MIB's original post, not to I-MAK.
- `followers.json`: 1 dated data point, 19,268 followers on 2026-11-26.

Field notes:
- `date_utc` is computed from the activity id (`id >> 22` = Unix ms). For every original post it matches the schema.org `datePublished` on the post page to the millisecond.
- `reactions` and `comments` come from the schema.org `interactionStatistic` on each public post page, fetched 2026-11-26. They are a snapshot taken that day, not final lifetime totals. `reactions` is LinkedIn's LikeAction count, i.e. all reaction types combined.
- `reposts` is null everywhere because logged-out post pages do not show a repost count.
- `video_seconds` comes from the schema.org `duration`.
- `image_count` comes from the media in each post's card on the company page.
- `topic` and `post_type` were assigned by hand from the post text and media. "expo-after" means a wrap-up post. The PACK EXPO wrap-up went out on the final show day.
- `language`: every original post is in English. The repost is in Turkish.

## Methods tried

| Method | Result |
|---|---|
| Public company page, Playwright, www.linkedin.com and tr.linkedin.com, scrolled | Works. Shows 19,268 followers and only the latest posts: 9 originals plus 1 repost. No pagination or "show more" for logged-out visitors. |
| `/company/i-mak---gearboxes/posts/` tab | Sends logged-out visitors to the authwall (HTTP 999). Not pursued. |
| curl on individual post pages | Works (HTTP 200). All 10 fetched. |
| Breadth-first crawl of links on post pages (2 hops, 38 post pages fetched, 1.5-3 s apart) | No new I-MAK company posts. The "related posts" blocks on public post pages link to other authors' posts (MAAG, Chongqing Gearbox, Aokman, Cimak, distributors, SIREXE exhibitors), never to older posts from the same page. The crawl dried up immediately. |
| Employee and partner profile pages (to see reshares) | curl gets HTTP 999. Playwright hits the authwall (HTTP 429). Blocked. |
| WebSearch tool (about 15 queries: site:linkedin.com/posts, expo names, WIN Eurasia, Hannover Messe, Global Industrie, Electra Mining, EXPOSIBRAM, IFAT, Maden Türkiye, Egypt facility, hashtags) | Not one linkedin.com/posts/i-mak---gearboxes_ URL came back. Results were profiles, the company page and trade press. The snippets mention topics the page probably posted about in 2026 (SIM 2026, IPPE Atlanta, IRC hoist series, the Egypt facility), but give no URL or date, so nothing was recorded from them. |
| Bing, Google, DuckDuckGo, Brave, Yahoo, Startpage, Ecosia, Mojeek, Yandex by direct HTTP | Bot checks or CAPTCHAs (DuckDuckGo, Google), 403, 429, 500 or redirects. Bing rendered in Playwright returned unrelated results. Nothing usable, and no CAPTCHA was attempted. |
| Wayback Machine | `archive.org/wayback/available` answers. It reports exactly one snapshot of the company page, from 2025-07-27 (no closer snapshot to any date in 2025-2026), and none for the tr. subdomain, `/posts`, or `/company/5033019`. **web.archive.org (CDX API and snapshot pages) is blocked by this environment's egress policy, over curl and WebFetch alike**, so that snapshot's follower count and post list could not be read. |
| imakreduktor.com (WordPress REST API and Fairs & Events page) | Works. Used only as context for gaps (see below). It contains no LinkedIn post links. |

## How complete is the 2026 list?

**Not complete. This covers about the last 7 weeks only (3 Oct to 16 Nov 2026).** No post from 1 Jan to 2 Oct 2026 could be found. A logged-out visitor sees only the latest roughly 10 feed items, and every other route to older posts was blocked or empty. Do not read these monthly counts as the year's activity:

| Month | Original posts found | Reposts found |
|---|---|---|
| Jan-Sep 2026 | 0 (not collectable, NOT zero activity) | 0 |
| Oct 2026 | 6 | 1 |
| Nov 2026 (to 26th) | 3 | 0 |

The page was almost certainly active before October. The company's own Fairs & Events page lists 2026 shows the page usually announces: Expo Minería Ecuador (Mar), Maden Türkiye (Apr), BATIMATEC, IFAT, NAMPO, SIPSA-FILAHA (May), Smart Manufacturing Week, WIN Eurasia, WATREX, IDMA (Jun), Expo USIPA (Jul), Feira Carajás, EXPOSIBRAM (Aug), Electra Mining, NAMPO Cape, RWM, Mining Metals, WEFTEC (Sep). Its news feed has 2026 stories on a Tunisia seminar (2 Jan), a UAE partner visit (5 Feb), the I-GUIDE selector (10 Mar), the Egypt facility start (25 Jun), Ecuador growth (6 Aug) and others. None of the matching LinkedIn posts could be reached.

Within the window we do see:
- No original post from 16 Nov to 26 Nov. The SAPRI 2026 (Tunis, 17-20 Nov) opening-day post was published by a separate *member profile* named "I-MAK Gearboxes and drives" (linkedin.com/in/i-mak-gearboxes-and-drives-a28511114), not by the company page.
- Several shows on the company's own calendar during the window have no company-page post: PTC Shanghai got only a wrap-up, and Propak Cape and Warsaw Industry Week got only before/during posts.

No 2025 company-page posts were found either, so a year-over-year comparison is not possible from this data.

## Follower history

Only one dated value: **19,268 on 2026-11-26**. Undated values in search-engine snippets, NOT put in followers.json because their dates are unknown: about 11,773 for the company page and about 1,341 for the showcase page "I-MAK REDUKTOR - Gearboxes and mechanical variators". The 11,773 figure probably comes from an older index copy, but its date cannot be checked. The 2025-07-27 Wayback snapshot would give a real dated point if someone can open web.archive.org from an unrestricted network: http://web.archive.org/web/20250727145704/https://www.linkedin.com/company/i-mak---gearboxes

## Related accounts found (not in posts.json)

- Showcase page "I-MAK REDUKTOR - Gearboxes and mechanical variators": one video post found on 2026-07-17 (34 reactions), activity 7483753738482925568.
- Member profile "I-MAK Gearboxes and drives" (in/i-mak-gearboxes-and-drives-a28511114) posts company-style content: SAPRI 2026 Tunis, 2026-11-17, 28 reactions. "Powering UK Industry...", 2026-07-15, 11 reactions. Content split between this profile and the company page will dilute the page's numbers.
- Employee and partner posts about I-MAK in 2026: Tahir Mohammed (warehouse, 2026-11-14, 73 reactions), Salim Haffar (Africa manufacturing, 2026-02-14, 85 reactions), ZAKARIA IBRAHIM (Standard Group partnership, 2026-05-10, 45 reactions), DriveTech Solutions (2026-07-21, 43 reactions; 2026-08-10, 26 reactions), Alexandra Sanchez / SERCORPVI (2026-09-04, 31 reactions), Ramzi Faour (SIREXE, 2026-11-16, 7 reactions).

## Caveats

- Reaction counts are a 26 Nov snapshot. Recent posts (SIREXE, 16 Nov) are still collecting reactions.
- Topic labels are hand-assigned. The Propak dates differ between the post (26-29 Oct) and the website (27-29 Oct).
- To get the full year, the page admin can export LinkedIn Page Analytics (Content and Followers tabs, custom range 1 Jan to 26 Nov 2026). It gives every post with impressions, reactions, comments, reposts and CTR, plus daily follower gains. That is the only complete source.
