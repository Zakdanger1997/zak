#!/usr/bin/env python3
"""Find each hero's five closest careers and write the story JSON for compose.html.

Metrics (all from data/players.json, Wikipedia career tables):
  club goals per game, international goals per cap, career goals (club+intl), career games (club+intl), seasons.
Each metric is z-scored over the pool (totals in log scale so a 900-goal career does not dominate), then the
Euclidean distance between careers is turned into a 0-100 % similarity index (1 - d / (2 * median pair distance)).
'The match' = the 3 metrics with the smallest standardized gap, 'the gap' = the largest.
Usage: python3 tools/twins.py   -> data/story_ronaldo.json, data/story_messi.json
"""
import json
import math
import os
import statistics as st

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = json.load(open(os.path.join(ROOT, "data", "players.json")))
YEAR = 2026
METRICS = [
    {"key": "gpg", "label": "club goals / game", "long": "CLUB GOALS PER GAME", "fmt": "rate", "log": False},
    {"key": "gpc", "label": "intl goals / cap", "long": "INTERNATIONAL GOALS PER CAP", "fmt": "rate", "log": False},
    {"key": "goals", "label": "career goals", "long": "CAREER GOALS", "fmt": "int", "log": True},
    {"key": "games", "label": "career games", "long": "CAREER GAMES", "fmt": "int", "log": True},
    {"key": "seasons", "label": "seasons", "long": "SEASONS AT THE TOP", "fmt": "int", "log": False},
]


def vals(p):
    try:
        v = {"gpg": p["club_goals"] / p["club_apps"], "gpc": p["intl_goals"] / p["intl_caps"],
             "goals": p["club_goals"] + p["intl_goals"], "games": p["club_apps"] + p["intl_caps"],
             "seasons": (p.get("active_to") or YEAR) - p["active_from"] + 1}
    except (TypeError, KeyError, ZeroDivisionError):
        return None
    return v


pool = [dict(p, values=vals(p)) for p in P]
pool = [p for p in pool if p["values"] and p.get("photo_file")]
mu, sd = {}, {}
for m in METRICS:
    xs = [math.log(p["values"][m["key"]]) if m["log"] else p["values"][m["key"]] for p in pool]
    mu[m["key"]], sd[m["key"]] = st.mean(xs), st.pstdev(xs) or 1
z = lambda p, m: ((math.log(p["values"][m["key"]]) if m["log"] else p["values"][m["key"]]) - mu[m["key"]]) / sd[m["key"]]
dist = lambda a, b: math.sqrt(sum((z(a, m) - z(b, m)) ** 2 for m in METRICS))
pairs = [dist(a, b) for i, a in enumerate(pool) for b in pool[i + 1:]]
D = 2 * st.median(pairs)


def lower_title(name):
    return name.lower() + "."


def short(name):
    special = {"Cristiano Ronaldo": "RONALDO", "Lionel Messi": "MESSI", "Ronaldo Nazário": "R9", "Diego Maradona": "MARADONA"}
    return special.get(name, name.split()[-1].upper())


def years(p):
    return f"{p['active_from']}–{p['active_to'] or 'present'}"


def story(hero_name, slug):
    hero = next(p for p in pool if p["name"] == hero_name)
    others = sorted((p for p in pool if p is not hero), key=lambda p: dist(hero, p))[:5]
    twins = []
    for r, p in enumerate(others, 1):
        diffs = sorted(METRICS, key=lambda m: abs(z(hero, m) - z(p, m)))
        twins.append({"rank": r, "name": p["name"], "title": lower_title(p.get("display", p["name"])), "short": short(p["name"]), "years": years(p),
                      "photo": p["photo_file"], "values": p["values"], "sim": max(0.0, 1 - dist(hero, p) / D),
                      "match": [m["key"] for m in diffs[:3]], "gap": [diffs[-1]["key"]]})
    t1 = twins[0]; m0 = next(m for m in METRICS if m["key"] == t1["match"][0])
    t1["line"] = f"closest on {m0['label']} · biggest gap: {next(m for m in METRICS if m['key'] == t1['gap'][0])['label']}"
    s = {"hero": {"name": hero["name"], "title": lower_title(hero.get("display", hero["name"])), "short": short(hero["name"]), "photo": hero["photo_file"],
                  "values": hero["values"]},
         "metrics": [{k: m[k] for k in ("key", "label", "long", "fmt")} for m in METRICS], "pool": len(pool) - 1, "twins": twins,
         "source": "Data: Wikipedia career statistics (club + international, official matches), as of Nov 2026. "
                   "Similarity: standardized distance on the five metrics. Photos: Wikimedia Commons (see description).",
         "audio": f"music_{slug}.wav"}
    json.dump(s, open(os.path.join(ROOT, "data", f"story_{slug}.json"), "w"), indent=1, ensure_ascii=False)
    print(hero_name, "->", [(t["name"], round(t["sim"] * 100)) for t in twins])
    return s


story("Cristiano Ronaldo", "ronaldo")
story("Lionel Messi", "messi")
