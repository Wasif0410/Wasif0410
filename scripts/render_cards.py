#!/usr/bin/env python3
"""
Draw every profile card into cards/*.svg from scripts/config.py and
data/profile.json. Never touches the network, so it always produces cards.

Run after fetch_data.py (the daily workflow does both), or on its own after
editing config.py:  python scripts/render_cards.py
"""
import json
import os

import config
from cards import activity, heatmap, hero, repos, tiles

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "data", "profile.json")
PORTRAIT = os.path.join(ROOT, "portrait.svg")
OUT = os.path.join(ROOT, "cards")


def project_card_name(title):
    slug = "".join(ch if ch.isalnum() else "-" for ch in title.lower()).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return f"project-{slug}.svg"


def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    portrait = None
    if os.path.exists(PORTRAIT):
        with open(PORTRAIT, encoding="utf-8") as f:
            portrait = f.read()

    cards = {
        "hero.svg": hero.render(config, data, portrait),
        "heatmap.svg": heatmap.render(config, data),
        "activity.svg": activity.render(config, data),
        "title-building.svg": tiles.title(config, "WHAT I'M BUILDING", "RIGHT NOW"),
    }
    for i, tile in enumerate(config.TILES):
        cards[f"tile-{tile['key']}.svg"] = tiles.render(config, data, i)
    for i, item in enumerate(config.FEATURED):
        cards[project_card_name(item["title"])] = repos.render(config, data, i)

    os.makedirs(OUT, exist_ok=True)
    for old in os.listdir(OUT):  # drop cards that config no longer produces
        if old.endswith(".svg") and old not in cards:
            os.remove(os.path.join(OUT, old))
            print(f"removed cards/{old}")
    for name, svg in cards.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print(f"wrote cards/{name} ({len(svg.encode('utf-8')) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
