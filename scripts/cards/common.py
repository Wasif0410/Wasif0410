"""
Shared pieces for every card: brand tokens, embedded fonts, animation CSS,
the card frame (hard shadow + hatched paper + ink border) and text helpers.

Cards are shown through <img>, so they can only use what GitHub allows there:
inline CSS (including animations) and fonts embedded as data URIs. No JS, no
external requests.
"""
import base64
import functools
import os
from html import escape

FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "fonts")

# ---- brand tokens (match wasifsaeed.com) --------------------------------------------
PAPER = "#F7F7F2"
PAPER_DEEP = "#EDEDE6"
INK = "#050505"
INK_SOFT = "#444444"
MUTED = "#777777"
WHITE = "#FFFFFF"
GRAPH_LEVELS = (PAPER_DEEP, "#C9C9C0", "#8F8F88", "#4A4A46", INK)

W = 880  # GitHub's README column at 100%
SHADOW = 5
BORDER = 2
RADIUS = 14
GAP = 14  # space under each card
GUTTER = 16  # space between cards in a three-across row
CARD_X = 1
CARD_W = W - CARD_X - SHADOW - 2  # 872: shadow ends at 878, inside the 880 canvas

DISPLAY = "'Archivo Black', 'Arial Black', Impact, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"

FONT_FILES = {
    "display": ("Archivo Black", 400, "archivo-black.woff"),
    "mono": ("JetBrains Mono", 400, "jetbrains-mono-400.woff"),
    "mono-b": ("JetBrains Mono", 700, "jetbrains-mono-700.woff"),
}

BASE_CSS = (
    "@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}"
    "@keyframes drop{0%{opacity:0;transform:translateY(-36px)}65%{opacity:1;transform:translateY(3px)}"
    "100%{opacity:1;transform:none}}"
    "@keyframes fade{from{opacity:0}to{opacity:1}}"
    "@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}"
    "@keyframes pop{0%{opacity:0;transform:scale(.4)}70%{opacity:1;transform:scale(1.1)}"
    "100%{opacity:1;transform:none}}"
    "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.15}}"
    "@keyframes nudge{0%,100%{transform:none}50%{transform:translate(3px,-3px)}}"
    ".rise{animation:rise .7s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}"
    ".drop{animation:drop .8s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}"
    ".fade{animation:fade .6s ease-out both}"
    ".grow{animation:grow .7s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box;transform-origin:50% 100%}"
    ".pop{animation:pop .5s ease-out both;transform-box:fill-box;transform-origin:50% 50%}"
    ".pulse{animation:pulse 1.6s ease-in-out infinite}"
    ".nu{animation:nudge 1.8s ease-in-out infinite;transform-box:fill-box}"
    "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
)


def num(x):
    """Format a coordinate compactly: 12.0 -> '12', 3.66667 -> '3.667'."""
    return f"{x:.3f}".rstrip("0").rstrip(".")


def esc(s):
    return escape(str(s), quote=True)


def fmt_int(n):
    return f"{n:,}"


def wrap(text, max_chars):
    lines, line = [], ""
    for word in text.split():
        candidate = f"{line} {word}" if line else word
        if len(candidate) <= max_chars or not line:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


@functools.lru_cache(maxsize=None)
def _font_face(key):
    family, weight, filename = FONT_FILES[key]
    with open(os.path.join(FONTS_DIR, filename), "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return (
        f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:normal;"
        f"src:url(data:font/woff;base64,{data}) format('woff')}}"
    )


def font_css(*keys):
    return "".join(_font_face(k) for k in keys)


def svg_doc(width, height, body, fonts=("display", "mono", "mono-b"), extra_css="", title=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{num(width)}" height="{num(height)}" '
        f'viewBox="0 0 {num(width)} {num(height)}" role="img">'
        f"<title>{esc(title)}</title>"
        f"<style>{font_css(*fonts)}{BASE_CSS}{extra_css}</style>"
        f"{body}</svg>"
    )


def card(x, y, w, h, body=""):
    """Hard ink shadow, hatched paper face, ink border; body is drawn in card coordinates."""
    return (
        '<defs><pattern id="hatch" width="9" height="9" patternUnits="userSpaceOnUse" '
        'patternTransform="rotate(45)">'
        f'<rect width="9" height="9" fill="{PAPER}"/>'
        f'<line x1="0" y1="0" x2="0" y2="9" stroke="{PAPER_DEEP}" stroke-width="1.4"/>'
        "</pattern></defs>"
        f'<rect x="{num(x + SHADOW)}" y="{num(y + SHADOW)}" width="{num(w)}" height="{num(h)}" '
        f'rx="{RADIUS}" fill="{INK}"/>'
        f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" rx="{RADIUS}" '
        f'fill="url(#hatch)" stroke="{INK}" stroke-width="{BORDER}"/>'
        f'<g transform="translate({num(x)},{num(y)})">{body}</g>'
    )


def full_card_height(h):
    """Canvas height for a full-width card whose face is h tall."""
    return CARD_X + h + SHADOW + GAP


def split_geometry(index):
    """(svg width, card x inside that svg, card width) for card `index` of a three-across row.

    The three SVGs sit side by side at width 33.333%, so each card's x is shifted
    to line the row up with the full-width cards: global x = 1, 297, 593.
    """
    svg_w = W / 3
    card_w = (CARD_W - 2 * GUTTER) / 3
    global_x = CARD_X + index * (card_w + GUTTER)
    return svg_w, global_x - index * svg_w, card_w


def text(x, y, s, size, family=MONO, weight=400, fill=INK, anchor="start",
         spacing=0, cls="", delay=None, extra=""):
    attrs = [
        f'x="{num(x)}"', f'y="{num(y)}"', f'font-family="{family}"', f'font-size="{num(size)}"',
        f'fill="{fill}"',
    ]
    if weight != 400:
        attrs.append(f'font-weight="{weight}"')
    if anchor != "start":
        attrs.append(f'text-anchor="{anchor}"')
    if spacing:
        attrs.append(f'letter-spacing="{num(spacing)}"')
    if cls:
        attrs.append(f'class="{cls}"')
    if delay is not None:
        attrs.append(f'style="animation-delay:{delay:.2f}s"')
    if extra:
        attrs.append(extra)
    return f"<text {' '.join(attrs)}>{esc(s)}</text>"


def label(x, y, s, fill=INK, anchor="start", delay=None, bold=True):
    """Mono caps label in the site's '01 / ABOUT' style."""
    return text(x, y, s, 11.5, MONO, 700 if bold else 400, fill, anchor, spacing=1.4,
                cls="fade" if delay is not None else "", delay=delay)


def arrow(x, y, size=14, delay=0.0):
    """A north-east arrow that nudges forever (the 'opens a link' cue)."""
    s = size
    return (
        f'<g class="nu" style="animation-delay:{delay:.2f}s">'
        f'<path d="M{num(x)} {num(y + s)} L{num(x + s)} {num(y)} M{num(x + 4)} {num(y)} '
        f'L{num(x + s)} {num(y)} L{num(x + s)} {num(y + s - 4)}" fill="none" stroke="{INK}" '
        'stroke-width="2.2" stroke-linecap="square"/></g>'
    )
