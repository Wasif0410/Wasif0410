"""
Everything on the profile cards that you edit by hand lives here.

Live numbers (contributions, streaks, stars, Trajectory entries) come from
data/profile.json, which scripts/fetch_data.py refreshes every day.
After editing, run:  python scripts/render_cards.py
"""

USER = "Wasif0410"

# ---- hero ---------------------------------------------------------------------
PILL = "ONLINE · TORONTO"
NAME_LINES = ("WASIF", "SAEED")
ROLE = "// AI & SOFTWARE DEVELOPER"
HEADLINE = (
    "5th-year CS at TMU. I build intelligent software systems, "
    "automation tools and AI-powered products."
)
SITE = "https://wasifsaeed.com"

# ---- three tiles: work, study, research -------------------------------------------
# "value" is the big word on the tile; all three share one size, fitted to the longest.
TILES = [
    {
        "key": "work",
        "label": "01 / WORK",
        "value": "Achievers",
        "caption": "Software Engineer",
        "note": "before: Dayforce, 8-month intern",
        "href": "https://www.linkedin.com/in/wasif-s",
    },
    {
        "key": "study",
        "label": "02 / STUDY",
        "value": "TMU",
        "caption": "B.Sc. Computer Science, co-op",
        "note": "graduating April 2027",
        "href": "https://wasifsaeed.com/#education",
    },
    {
        "key": "research",
        "label": "03 / RESEARCH",
        "value": "Circle Labs",
        "caption": "AI/NLP bachelor's thesis",
        "note": "research lab at TMU",
        "href": "https://wasifsaeed.com/#experience",
    },
]

# ---- "What I'm building" cards ------------------------------------------------------
# repo: public repo name for live stars/language (None for private projects).
# status: "building" or "live". stack: shown when there is no public repo.
FEATURED = [
    {
        "title": "Probative Labs",
        "repo": None,
        "href": "https://probative-web.vercel.app",
        "desc": "Independent testing for AI security agents, run against a frozen replica of a company's security history.",
        "status": "building",
        "stack": "Python · TypeScript",
    },
    {
        "title": "My Daily Standup",
        "repo": "My-Daily-Standup",
        "href": "https://github.com/Wasif0410/My-Daily-Standup",
        "desc": "Local-first planner that turns my Obsidian goals into daily actions, with voice standups.",
        "status": "building",
    },
    {
        "title": "Seven XI match centre",
        "repo": "footy-site",
        "href": "https://footy-site.vercel.app",
        "desc": "Results, player ratings with proof, stats and match reviews for my football team.",
        "status": "live",
    },
]

# ---- links row under the cards (README.md) ----------------------------------------
LINKS = [
    ("wasifsaeed.com", "https://wasifsaeed.com"),
    ("linkedin", "https://www.linkedin.com/in/wasif-s"),
    ("medium", "https://medium.com/@wasifsaeed0410"),
    ("email", "mailto:Wasifsaeed0410@gmail.com"),
]
