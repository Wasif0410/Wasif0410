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

# ---- three tiles ----------------------------------------------------------------
# value=None means the number is live (filled from data/profile.json).
TILES = [
    {
        "key": "build",
        "label": "01 / BUILD",
        "value": "6",
        "caption": "products shipped",
        "note": "Probative · MechLens · Monelyth +3",
        "href": "https://wasifsaeed.com/#projects",
    },
    {
        "key": "research",
        "label": "02 / RESEARCH",
        "value": "5",
        "caption": "AI research projects",
        "note": "agents · RAG · vision · NLP",
        "href": "https://medium.com/@wasifsaeed0410/where-ai-agents-break-0337a7507a7e",
    },
    {
        "key": "learn",
        "label": "03 / LEARN",
        "value": None,
        "caption": "entries logged",
        "note": "my Trajectory learning log",
        "href": "https://github.com/Wasif0410/Trajectory",
    },
]

# ---- "What I'm building" repo cards ---------------------------------------------
FEATURED = [
    {
        "repo": "job-application-skills",
        "desc": "Claude Code skills that turn a job posting into a tailored resume, cover letter and form answers.",
    },
    {
        "repo": "Where-AI-Agents-Break",
        "desc": "An independent study of AI agents on realistic SaaS revenue operations tasks.",
    },
    {
        "repo": "Trajectory",
        "desc": "A daily learning log, rendered as a windowed desktop you can browse.",
    },
]

# Where the LEARN tile counts entries from.
TRAJECTORY_REPO = "Wasif0410/Trajectory"
TRAJECTORY_DIR = "content/entries"

# ---- links row under the cards (README.md) ----------------------------------------
LINKS = [
    ("wasifsaeed.com", "https://wasifsaeed.com"),
    ("linkedin", "https://www.linkedin.com/in/wasif-s"),
    ("medium", "https://medium.com/@wasifsaeed0410"),
    ("email", "mailto:Wasifsaeed0410@gmail.com"),
]
