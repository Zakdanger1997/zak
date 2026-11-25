# Stat twins

Two 9:16 shorts that find the closest careers to Cristiano Ronaldo and Lionel Messi among 36 legends, using real numbers.

- `data/players.json`: club and international apps/goals from each player's Wikipedia article (the revision id is stored per player). Disputed cases are covered in `data/NOTES.md`.
- `tools/twins.py`: five metrics (club goals/game, intl goals/cap, career goals, career games, seasons as a pro). Each is z-scored (totals in log scale), and the distance becomes a similarity % → `data/story_*.json`.
- `tools/music.py`: synthesized music bed. `tools/compose.js`: records `compose.html` frame by frame → `video/*.mp4`.

```
python3 tools/twins.py
python3 tools/music.py ronaldo 66 60; python3 tools/music.py messi 66 57
node tools/compose.js data/story_ronaldo.json video/ronaldo-stat-twin.mp4
node tools/compose.js data/story_messi.json video/messi-stat-twin.mp4
```

## Photo credits (Wikimedia Commons; put these in the video description)

- Cristiano Ronaldo: Bryan Berlin, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Cristiano_Ronaldo_Croatia_v_Portugal_2_July_2026-075_(cropped).jpg
- Lionel Messi: Bryan Berlin, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Leo_Messi_Argentina_v_Egypt_7_July_2026-1.jpg
- Robert Lewandowski: Bryan Berlin, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Robert_Lewandowski_NYCFC_v_Chicago_25_July_2026-383.jpg
- Luis Suárez: The White House, Public domain, https://commons.wikimedia.org/wiki/File:Luis_Su%C3%A1rez_2026_(cropped).jpg
- Karim Benzema: Chris Deahr, CC BY 2.0, https://commons.wikimedia.org/wiki/File:Karim_Benzema_vs._FC_Schalke_04_(16647992937).jpg
- Zlatan Ibrahimović: Colleen Sturtevant, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Zlatan_Ibrahimovi%C4%87_nyc.jpg
- Harry Kane: Bryan Berlin, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Harry_Kane_England_v_Ghana_23_June_2026-024_(cropped).jpg
- Kylian Mbappé: Bryan Berlin, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Kylian_Mbappe_France_v_Senegal_16_June_2026-391_(cropped).jpg
- Erling Haaland: Bryan Berlin, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Erling_Haaland_Morocco_v_Norway_7_June_2026-51.jpg
- Mohamed Salah: Bryan Berlin, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Mohamed_Salah_Argentina_v_Egypt_7_July_2026-163_(cropped).jpg
- Neymar: Bryan Berlin, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Neymar_Junior_Brazil_V_Morocco_13_June_2026-40.jpg
- Thierry Henry: Web Summit, CC BY 2.0, https://commons.wikimedia.org/wiki/File:Thierry_Henry_(51649035951)_(cropped).jpg
- Wayne Rooney: All-Pro Reels from District of Columbia, USA, CC BY-SA 2.0, https://commons.wikimedia.org/wiki/File:Wayne_Rooney_(50121495731)_(cropped).jpg
- Sergio Agüero: Кирилл Венедиктов, CC BY-SA 3.0, https://commons.wikimedia.org/wiki/File:Ag%C3%BCero_in_2018.jpg
- Samuel Eto'o: BACHELOR45, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Sammuel_Eto%27o_Fils_02.jpg
- Ronaldo Nazário: Lula Oficial, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:12.12.2025_%E2%80%93_Cerim%C3%B4nia_de_lan%C3%A7amento_do_SBT_News_-_54980664160_(cropped2).jpg
- Ronaldinho: Web Summit, CC BY 2.0, https://commons.wikimedia.org/wiki/File:2019_-_Press_conferences_-_Day_1_ENX_6950_(49019873887)_(cropped).jpg
- Kaká: Евгений Асмолов, CC BY-SA 3.0, https://commons.wikimedia.org/wiki/File:Kak%C3%A1_visited_Stadium_St._Petersburg.jpg
- Andriy Shevchenko: Міністерство молоді та спорту України, CC BY 4.0, https://commons.wikimedia.org/wiki/File:Andriy_Shevchenko_Volia_Space_03_(cropped).png
- Didier Drogba: Y.Leclercq©, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Didier_Drogba_(2019)_(cropped2).jpg
- Gerd Müller: Unknown author, Public domain, https://commons.wikimedia.org/wiki/File:Gerd_M%C3%BCller_c1973_(cropped).jpg
- Pelé: Unknown author, Public domain, https://commons.wikimedia.org/wiki/File:Pele_con_brasil_(cropped).jpg
- Diego Maradona: Unknown author, Public domain, https://commons.wikimedia.org/wiki/File:Argentina_celebrando_copa_(cropped).jpg
- Johan Cruyff: Rob Mieremet / Anefo, CC0, https://commons.wikimedia.org/wiki/File:Johan_Cruijff_(1974).jpg
- Zinedine Zidane: Hadi Abyar, CC BY 4.0, https://commons.wikimedia.org/wiki/File:Zinedine_Zidane_by_Tasnim_03.jpg
- Romário: Agência Senado from Brasilia, Brazil, CC BY 2.0, https://commons.wikimedia.org/wiki/File:Senadores_da_57%C2%AA_Legislatura_(52689451805)_(cropped_-_3x4).jpg
- Eusébio: Panini, Public domain, https://commons.wikimedia.org/wiki/File:Eusebio_en_1973.jpg
- Ferenc Puskás: Panini, Public domain, https://commons.wikimedia.org/wiki/File:Ferenc_Puskas_en_1965.jpg
- Alfredo Di Stéfano: Unknown author, Public domain, https://commons.wikimedia.org/wiki/File:Alfredo_Di_Stefano_River_Plate.jpg
- Raúl: Barcex, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:25th_Laureus_World_Sports_Awards_-_Ra%C3%BAl_-_240422_132916-2_(cropped).jpg
- Antoine Griezmann: Антон Зайцев, CC BY-SA 3.0, https://commons.wikimedia.org/wiki/File:FRA-ARG_(10)_(cropped).jpg
- Edinson Cavani: soccerdigital, Public domain, https://commons.wikimedia.org/wiki/File:PALMEIRAS_X_BOCA_JUNIORS_-_COPA_LIBERTADORES_2023_-_53286889335_(cropped_2).jpg
- Luka Modrić: Bryan Berlin, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Luka_Modric_Croatia_v_Portugal_2_July_2026-055.jpg
- Kevin De Bruyne: Bryan Berlin, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Kevin_De_Bruyne_USMNT_v_Belgium_Mar_28_2026-64_(cropped).jpg
- Andrés Iniesta: Bryan Berlin, CC BY-SA 4.0, https://commons.wikimedia.org/wiki/File:Andr%C3%A9s_Iniesta_Argentina_v_Spain_19_July_2026-034_(cropped).jpg
- Xavi: Meysam Mehabadi, CC BY 4.0, https://commons.wikimedia.org/wiki/File:Xavi,_Persepolis_vs._Al_Sadd,_20190520_02_(cropped).jpg
