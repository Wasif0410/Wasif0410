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


def repo_card_name(repo):
    return f"repo-{repo.lower()}.svg"


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
        "title-building.svg": tiles.title(config, "WHAT I'M BUILDING", "LIVE FROM GITHUB"),
    }
    for i, tile in enumerate(config.TILES):
        cards[f"tile-{tile['key']}.svg"] = tiles.render(config, data, i)
    for i, item in enumerate(config.FEATURED):
        cards[repo_card_name(item["repo"])] = repos.render(config, data, i)

    os.makedirs(OUT, exist_ok=True)
    for name, svg in cards.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(svg)
        print(f"wrote cards/{name} ({len(svg.encode('utf-8')) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
