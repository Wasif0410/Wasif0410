#!/usr/bin/env python3
"""
Collect the live numbers for the profile cards into data/profile.json:

  - daily contribution counts, read from GitHub's public contributions page
    (the same HTML the profile page loads; no login needed), plus the streaks,
    busiest day and monthly totals derived from them
  - stars and main language of the featured public repos (GitHub REST API)

Each source is fetched on its own. If one fails, its value from the previous
data/profile.json is kept, so the cards still render. The script exits with an
error only when contribution data is missing and there is nothing to fall back on.

Standard library only, so the daily workflow needs no installs.
"""
import datetime
import json
import os
import re
import sys
import urllib.request
from html import unescape

import config

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT_PATH = os.path.join(ROOT, "data", "profile.json")
CONTRIB_URL = f"https://github.com/users/{config.USER}/contributions"
API = "https://api.github.com"

TD_RE = re.compile(r"<td\b[^>]*ContributionCalendar-day[^>]*>", re.I)
TIP_RE = re.compile(r"<tool-tip\b([^>]*)>(.*?)</tool-tip>", re.I | re.S)
ATTR_RE = re.compile(r'([\w:-]+)="([^"]*)"')
COUNT_RE = re.compile(r"(\d[\d,]*)\s+contribution", re.I)


# ---- parsing and maths (pure, unit-tested) -----------------------------------------

def parse_contributions(html):
    """Return [{date, count, level}] sorted by date from the contributions HTML."""
    tips = {}
    for attrs, text in TIP_RE.findall(html):
        target = dict(ATTR_RE.findall(attrs)).get("for")
        if target:
            tips[target] = unescape(re.sub(r"<[^>]+>", "", text)).strip()

    days = []
    for tag in TD_RE.findall(html):
        attrs = dict(ATTR_RE.findall(tag))
        date = attrs.get("data-date")
        if not date:
            continue
        match = COUNT_RE.match(tips.get(attrs.get("id", ""), ""))
        count = int(match.group(1).replace(",", "")) if match else 0
        days.append({"date": date, "count": count, "level": int(attrs.get("data-level") or 0)})
    days.sort(key=lambda d: d["date"])
    return days


def _current_streak(days):
    i = len(days) - 1
    if i >= 0 and days[i]["count"] == 0:
        i -= 1  # today isn't over yet, so an empty today doesn't break the streak
    streak = 0
    while i >= 0 and days[i]["count"] > 0:
        streak += 1
        i -= 1
    return streak


def _longest_streak(days):
    best = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        best = max(best, run)
    return best


def summarize(days):
    totals = {}
    for d in days:
        key = d["date"][:7]
        totals[key] = totals.get(key, 0) + d["count"]
    months = [{"month": k, "total": v} for k, v in sorted(totals.items())][-12:]

    busiest = max(days, key=lambda d: (d["count"], d["date"])) if days else None
    return {
        "total": sum(d["count"] for d in days),
        "active_days": sum(1 for d in days if d["count"] > 0),
        "current_streak": _current_streak(days),
        "longest_streak": _longest_streak(days),
        "busiest": {"date": busiest["date"], "count": busiest["count"]} if busiest else None,
        "months": months,
        "days": days,
    }


# ---- network --------------------------------------------------------------------------

def http_get(url):
    headers = {"User-Agent": "profile-cards-bot/1.0"}
    if url.startswith(API):
        headers["Accept"] = "application/vnd.github+json"
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def fetch_contributions():
    days = parse_contributions(http_get(CONTRIB_URL))
    if not days:
        raise ValueError("no calendar cells found; GitHub's page markup may have changed")
    return summarize(days)


def fetch_repo(name):
    info = json.loads(http_get(f"{API}/repos/{config.USER}/{name}"))
    return {"stars": info["stargazers_count"], "language": info["language"]}


# ---- main -------------------------------------------------------------------------------

def load_previous():
    try:
        with open(OUT_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def warn(what, err):
    print(f"warning: could not fetch {what}: {err}", file=sys.stderr)


def main():
    prev = load_previous()
    out = {"generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")}

    try:
        out["contributions"] = fetch_contributions()
    except Exception as err:  # noqa: BLE001  any failure falls back to yesterday's data
        warn("contributions", err)
        if not prev.get("contributions"):
            sys.exit("error: no contribution data and nothing to fall back on")
        out["contributions"] = prev["contributions"]

    out["repos"] = {}
    for item in config.FEATURED:
        name = item.get("repo")
        if not name:  # private project: nothing public to fetch
            continue
        try:
            out["repos"][name] = fetch_repo(name)
        except Exception as err:  # noqa: BLE001
            warn(f"repo {name}", err)
            out["repos"][name] = prev.get("repos", {}).get(name, {"stars": 0, "language": None})

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1)
        f.write("\n")

    c = out["contributions"]
    print(
        f"wrote data/profile.json: {c['total']:,} contributions, "
        f"streak {c['current_streak']}, longest {c['longest_streak']}, "
        f"{c['active_days']} active days"
    )


if __name__ == "__main__":
    main()
