# Profile Cards Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the profile README with animated SVG cards in the wasifsaeed.com "Paper" style, refreshed daily by a GitHub Action.

**Architecture:** `fetch_data.py` (stdlib only) writes live data to `data/profile.json`; `render_cards.py` reads `config.py` plus that JSON and calls one `render(cfg, data) -> str` per card module in `scripts/cards/`, writing `cards/*.svg`. Fonts are subset once and embedded as base64 WOFF. A scheduled workflow runs fetch, then render, then commits changes.

**Tech Stack:** Python 3.12 stdlib (urllib, html, json, unittest, xml.etree) for everything that runs in CI. Local one-time tools: fontTools (font subsetting), Pillow + numpy (portrait).

## Global Constraints

- Spec: `docs/superpowers/specs/2026-11-11-profile-cards-design.md`.
- Tokens: PAPER `#F7F7F2`, PAPER_DEEP `#EDEDE6`, INK `#050505`, INK_SOFT `#444444`, MUTED `#777777`, WHITE `#FFFFFF`.
- Fonts: Archivo Black, JetBrains Mono 400/700, both SIL OFL, subset to ASCII + `·` `’`.
- Full card width 880; tiles/repo cards 880/3 wide, global gutter 16, card rect spans x=1..873 overall.
- Card: 2px ink border, rx 14, hard ink shadow offset 5, hatched paper fill, 14px gap below.
- No JS, no external requests inside SVGs. `prefers-reduced-motion` shows the final state.
- Each SVG must parse as XML and stay under 300 KB.
- CI path must need no pip installs.
- Tests: stdlib `unittest`, run with `py -3 -m unittest discover -s tests` locally (`python -m unittest discover -s tests` in CI).

---

### Task 1: Scaffold, config and fonts

**Files:**
- Create: `scripts/config.py`, `scripts/subset_fonts.py`, `scripts/requirements.txt`, `fonts/*.woff`, `fonts/OFL-*.txt`, `.gitignore`
- Test: `tests/test_fonts.py`

**Interfaces:**
- Produces: `config.USER`, `config.PILL`, `config.NAME_LINES`, `config.ROLE`, `config.HEADLINE`, `config.SITE`, `config.TILES` (list of dicts: key, label, value, caption, note, href), `config.FEATURED` (list of dicts: repo, desc), `config.TRAJECTORY_REPO`, `config.TRAJECTORY_DIR`, `config.LINKS`.
- Produces: `fonts/archivo-black.woff`, `fonts/jetbrains-mono-400.woff`, `fonts/jetbrains-mono-700.woff`.

- [ ] Download `ArchivoBlack-Regular.ttf`, `JetBrainsMono[wght].ttf` and both `OFL.txt` from github.com/google/fonts into a temp download folder.
- [ ] `subset_fonts.py <src_dir>`: instance JetBrains Mono at wght 400 and 700 (`fontTools.varLib.instancer`), subset all three to ASCII 0x20-0x7E + U+00B7 + U+2019, save as WOFF in `fonts/`.
- [ ] Test: each WOFF exists, starts with `wOFF` magic, is under 40 KB.
- [ ] Commit.

### Task 2: Data fetcher

**Files:**
- Create: `scripts/fetch_data.py`, `data/profile.json`
- Test: `tests/test_fetch.py`

**Interfaces:**
- Produces: `parse_contributions(html: str) -> list[dict(date:str, count:int, level:int)]` sorted by date.
- Produces: `summarize(days: list) -> dict(total, current_streak, longest_streak, busiest{date,count}, months[list of {month:'YYYY-MM', total}], days)`; months = last 12 distinct months.
- Produces: `data/profile.json` = `{generated_at, contributions: <summarize output>, repos: {name: {stars, language}}, trajectory_entries: int}`.

- [ ] Write tests: parse a fixture with three `td.ContributionCalendar-day` cells and matching `tool-tip`s ("No contributions", "1 contribution", "5 contributions"); summarize a hand-built 10-day series (streak with today = 0 not breaking, longest streak, busiest, month totals).
- [ ] Run tests, expect failures.
- [ ] Implement with `urllib.request` + regex attribute parsing; each source wrapped in try/except falling back to the previous `data/profile.json`; exit 1 only when contributions fail and there is no previous data.
- [ ] Run tests, expect pass. Run the script for real, check the JSON.
- [ ] Commit.

### Task 3: Card toolkit

**Files:**
- Create: `scripts/cards/__init__.py`, `scripts/cards/common.py`
- Test: `tests/test_common.py`

**Interfaces:**
- Produces: tokens as module constants; `esc(s) -> str`; `wrap(text, max_chars) -> list[str]`; `font_css(*keys) -> str` where keys in `{"display","mono","mono-b"}`; `BASE_CSS`; `svg_doc(width, height, body, fonts=(...), extra_css="") -> str`; `card(x, y, w, h, body, uid) -> str` (shadow rect + hatched rect + border); `split_geometry(index) -> (svg_w, local_x, card_w)` for the three-across row; `fmt_int(n) -> str` with thousands separators; `arrow(x, y) -> str`.

- [ ] Tests: `svg_doc` output parses with `xml.etree`; `wrap` never exceeds max_chars; `split_geometry` gives global x of 1, 297, 593 and card width 280.
- [ ] Implement, run tests, commit.

### Task 4: Hero, heatmap and activity cards

**Files:**
- Create: `scripts/cards/hero.py`, `scripts/cards/heatmap.py`, `scripts/cards/activity.py`
- Test: `tests/test_cards.py`

**Interfaces:**
- Consumes: Task 3 helpers, `config`, Task 2 data shape.
- Produces: `hero.render(cfg, data, portrait_svg: str | None) -> str`, `heatmap.render(cfg, data) -> str`, `activity.render(cfg, data) -> str`.

- [ ] Tests: each render returns XML-parseable SVG of width 880 containing expected text (name lines, total contributions formatted, 371 cells for 53 weeks of sample data), under 300 KB.
- [ ] Implement; hero inlines `portrait.svg` contents when present and leaves the space empty otherwise.
- [ ] Run tests, commit.

### Task 5: Tiles, section title and repo cards

**Files:**
- Create: `scripts/cards/tiles.py`, `scripts/cards/repos.py`
- Modify: `tests/test_cards.py`

**Interfaces:**
- Produces: `tiles.render(cfg, data, index) -> str`, `tiles.title(cfg, text, label) -> str`, `repos.render(cfg, data, index) -> str`.
- LEARN tile value comes from `data["trajectory_entries"]`; others from `cfg.TILES[i]["value"]`.

- [ ] Tests: tile 2 shows the trajectory count; repo card shows stars and language from data; long descriptions wrap to at most 3 lines.
- [ ] Implement, run tests, commit.

### Task 6: Renderer entry point, README, workflow

**Files:**
- Create: `scripts/render_cards.py`, `.github/workflows/update-cards.yml`, `preview.html` (gitignored), `cards/*.svg`
- Modify: `README.md`

- [ ] `render_cards.py`: load config and `data/profile.json`, read `portrait.svg` if present, write all cards to `cards/`.
- [ ] README: card block per spec (no blank lines inside the block, row images on one line), links row.
- [ ] Workflow per spec (cron `23 6 * * *`, dispatch, push on paths; commit only on diff; no pip install).
- [ ] Run renderer; open `preview.html` in the browser pane at 880px on light and dark page colours; screenshot; fix layout issues.
- [ ] Commit.

### Task 7: Portrait (after the photo arrives)

**Files:**
- Create: `scripts/make_portrait.py`, `portrait.svg`

- [ ] `make_portrait.py <photo> portrait.svg [--crop x,y,w,h] [--rows 64]`: grayscale, crop, autocontrast, vignette + light threshold to paper, wavy variable-width engraving rows, one `<path>` per row with staggered fade, output a `<g>` sized 272x272.
- [ ] Check output size under 120 KB; re-render cards; preview; commit.

### Task 8: Verify and publish branch

- [ ] Run all unit tests, render, confirm each SVG parses and is under 300 KB.
- [ ] Push `profile-cards`, view README on github.com on the branch, confirm fonts and animation render.
