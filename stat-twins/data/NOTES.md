# Data notes for players.json

Source: current English Wikipedia articles, fetched 2026-11-25 via the MediaWiki API (`action=parse`, wikitext + rendered HTML). The revision ID of every article used is stored per player as `source_revid`, so each number can be checked against that exact revision.

## Method

- **club_apps / club_goals**: the "Career total" row of the article's "Appearances and goals by club, season and competition" table, using the last Total Apps/Goals column. This counts official club matches in all competitions as Wikipedia totals them. It is not the infobox figure, which on Wikipedia counts league matches only.
- **club_assists**: null for everyone. None of the 36 career-stats tables has an assists column.
- **intl_caps / intl_goals**: the senior national team line of the infobox. Youth, Olympic, B and regional teams are excluded. These match the senior "Total" rows of the international tables wherever I checked (Messi 208/126, Ronaldo 234/146, Maradona 91/34, Ronaldinho 97/33).
- **active_from**: the start year of the first senior-career entry in the infobox (`years1`). This can be a year before the first senior appearance. For example, Kane's entry is "2009" (Tottenham), and some career tables start a season later (Shevchenko, Müller, Kaká, Zidane) or earlier (Puskás).
- **active_to**: the last year of the last infobox club spell. It is null when the spell is open-ended ("2023–"), or when the article says the player is still active.
- **ballon_dor_wins**: counted from the Honours section ("Ballon d'Or: years"). Messi's 8 and Ronaldo's 5 include the 2010–2015 merged FIFA Ballon d'Or, as Wikipedia lists them.
- **ballon_dor_podiums**: filled only when the Honours section explicitly lists runner-up or third places. The value is wins plus the listed placings. Null means the article does not list placings, not that there were none. This applies to Messi, Ronaldo, Kaká, Benzema, Zidane and others, even where they had podiums. Ronaldo's article mentions runner-up finishes in the prose (2007, 2011, 2012) but gives no complete count, so his value stays null.
- **major_trophies_count**: filled only where the article states a career figure: Ronaldo 35 ("His 35 trophies"), Messi 47 ("47 team trophies"), Modrić 34 ("34 major trophies"), Ibrahimović 34 ("34 trophies in his career"). Club-only figures are not used: Iniesta 33 with Barça, Benzema 25 with Real Madrid, Mbappé 15 with PSG, De Bruyne 16 with Man City, Rooney 16 with United.
- **stats_as_of**: the `{{updated|...}}` date in the Club statistics subsection. It is null when the article has none, which is the case for most retired players.

## Uncertain / disputed items

- **Pelé**: his article has no career-total row. It has separate Santos (659 apps / 643 goals) and New York Cosmos (107 / 66) tables, and the Cosmos "Other" column is marked "citation needed" and probably includes exhibitions. I used the article's explicit statement: "According to the RSSSF, Pelé scored ... a total of 775 goals in 840 official games" → 840 / 775. The alternatives are the sum of the two tables (766 / 709) and the Guinness figure including friendlies (1,279 goals in 1,363 games, also given as 1,283). International: 92 / 77 per the infobox and table. The article notes that this includes one match FIFA does not recognise. Ballon d'Or: he was ineligible at the time. The article lists 7 retroactive "Le nouveau palmarès" awards (1958–1970) as France Football honours. I recorded 0 official wins and noted the retroactive ones here.
- **Ferenc Puskás**: club 659 / 670 from the career-stats table. Older sources disagree. International: Hungary 85 / 84 plus Spain 4 / 0 = 89 / 84 (my sum). I excluded his single match for Castile (1 / 2), which the article's table includes in its 90 / 86 total. His "Ballon d'Or Silver Award 1960" (runner-up) is counted as 1 podium.
- **Alfredo Di Stéfano**: club 669 / 480 from the table (the infobox league-only figure is 521 / 376). International: 37 / 29, the article's table total for Argentina 6 / 6 plus Spain 31 / 23. His 4 caps for Colombia (1951) are excluded because they are not FIFA-recognised.
- **Romário**: the table total (893 / 690) includes Brazilian state-league matches. The infobox total is 698 / 542. His 1994 "Ballon d'Or – Le nouveau palmarès" is retroactive, recorded as 0 official wins.
- **Diego Maradona**: his 1995 Ballon d'Or "for services to football" is honorary, recorded as 0 wins.
- **Eusébio**: club 577 / 582 per the table (more goals than apps). The infobox total is 436 / 424.
- **Gerd Müller**: the 1972 runner-up place was shared with Günter Netzer. Podiums = 4 (1970 win, 1972 2nd, 1969 and 1973 3rd).
- **Ibrahimović**: the Honours section lists nominations with a best finish of 4th (2013), so podiums = 0.
- **Xavi**: the Honours section lists 3rd place in 2009, 2010 and 2011, so podiums = 3 and wins = 0.
- **Benzema and Cavani**: their last club spells closed in 2026, but both articles still say they "play" (Benzema is described as a free agent). active_to is set to null.
- **Ronaldinho**: the article says he came out of retirement and joined Ravenna (Serie C) in 2026, with 1 appearance so far. It is sourced (Sky Sports, Reuters, BBC), so active_to is null, and his club total includes that match.
- **Retirees in management**: Raúl, Xavi, Zidane, Iniesta, Henry and Shevchenko now manage clubs or teams. Some of their articles have `{{updated}}` tags that refer to managerial tables, so I ignored those.
- **Article titles**: "Luis Suárez" and "Xavi" are disambiguation pages. I used "Luis Suárez (Uruguayan footballer)" and "Xavi (footballer, born 1980)". Ronaldo Nazário is "Ronaldo (Brazilian footballer)", and Raúl is "Raúl (footballer)", which redirects to "Raúl González".
- **Primary position**: the first position listed in the infobox.

## Stats "as of" for active players (club table `{{updated}}`)

| Player | Club stats as of |
|---|---|
| Cristiano Ronaldo | match played 24 Nov 2026 |
| Lionel Messi | match played 21 Nov 2026 |
| Robert Lewandowski | match played 22 Nov 2026 |
| Luis Suárez | match played 21 Nov 2026 |
| Karim Benzema | match played 20 Aug 2026 (free agent) |
| Harry Kane | match played 20 Nov 2026 |
| Kylian Mbappé | match played 24 Nov 2026 |
| Erling Haaland | match played 21 Nov 2026 |
| Mohamed Salah | match played 22 Nov 2026 |
| Neymar | match played 23 Nov 2026 |
| Ronaldinho | match played 15 Nov 2026 |
| Antoine Griezmann | match played 19 Nov 2026 |
| Edinson Cavani | match played 20 Feb 2026 |
| Luka Modrić | match played 22 Nov 2026 |
| Kevin De Bruyne | match played 24 Nov 2026 |

National-team figures come from the infobox. Ronaldo's infobox club figures carry "club_update 20 Nov 2026", which is earlier than his career table. Active players' totals will change after each match, so re-pull them before you render the video.

## Photos

- Every photo is the article's current infobox image, hosted on Wikimedia Commons. Its licence was read from the Commons `extmetadata` (LicenseShortName). All 36 are free: CC BY, CC BY-SA, CC0 or public domain. None was skipped.
- Images were resized so the long side is at most 1200 px and saved as JPEG. Shevchenko's source is a PNG and was flattened onto white.
- CC BY and CC BY-SA images need attribution in the video (author + licence + link). Use `photo_author`, `photo_license` and `photo_page`. Many 2026 match photos are by "Bryan Berlin" (CC BY-SA 4.0).
- Public-domain status of the historic photos (Di Stéfano, Maradona, Pelé, Müller, Eusébio, Puskás) rests on the Commons tags, which are usually based on Argentine, Brazilian or Spanish copyright terms. Commons treats them as PD, but PD status can vary by country.
- Some infobox images are not tight headshots. Maradona's is a crop of a trophy-celebration photo, Cavani's is a crop of a match photo, and Romário's is a Senate portrait. Check the framing before compositing.

## Photo resolution caveat

Wikimedia blocked this client from downloading originals during the session: HTTP 429 with a 600 s back-off, and a message asking for standard thumbnail sizes. Images were therefore fetched at Wikimedia's standard thumbnail widths (250/330/500/960/1280 px) and then capped at 1200 px. Most images are 800–1200 px on the long side. The small historic originals came out at low resolution: Gerd Müller (330x439), Pelé (330x447), Diego Maradona (365x572), Zinedine Zidane (330x438), Ferenc Puskás (250x323), Xavi (330x441). If you need sharper copies, download the originals from `photo_page` by hand.

Benzema's infobox image is a full-body match shot, so the face is small. Crop it tightly or swap it for another free Commons portrait.
