"""'What I'm building' cards: status badge, name, short description, stack and stars.

Public projects show their live star count and main language; private ones show
PRIVATE and the stack from config instead.
"""
import math

from . import common as c

FACE_H = 190
PAD = 22
DESC_CHARS = 36
DESC_LINES = 3
STATUS_TEXT = {"building": "BUILDING", "live": "LIVE"}


def _star(cx, cy, r_out=6.5, r_in=2.8):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = -math.pi / 2 + i * math.pi / 5
        pts.append(f"{c.num(cx + r * math.cos(a))},{c.num(cy + r * math.sin(a))}")
    return (f'<polygon points="{" ".join(pts)}" fill="{c.INK}" stroke="{c.INK}" '
            'stroke-width="1" stroke-linejoin="round"/>')


def _lock(x, y):
    return (
        f'<rect x="{c.num(x)}" y="{c.num(y + 4)}" width="10" height="8" rx="1.5" fill="{c.INK}"/>'
        f'<path d="M{c.num(x + 2.2)} {c.num(y + 4)} V{c.num(y + 2)} a2.8 2.8 0 0 1 5.6 0 V{c.num(y + 4)}" '
        f'fill="none" stroke="{c.INK}" stroke-width="1.6"/>'
    )


def _status(status, private):
    text = STATUS_TEXT.get(status, status.upper())
    tw = c.text_width(text, 10.5, "mono-b", 1.2)
    w = 24 + tw + 10
    out = (
        f'<rect x="{PAD}" y="18" width="{c.num(w)}" height="22" rx="11" fill="{c.PAPER}" '
        f'stroke="{c.INK}" stroke-width="1.5"/>'
        f'<circle class="pulse" cx="{PAD + 12}" cy="29" r="3.5" fill="{c.INK}"/>'
        + c.text(PAD + 22, 32.8, text, 10.5, c.MONO, 700, spacing=1.2)
    )
    if private:
        x = PAD + w + 12
        out += _lock(x, 21) + c.text(x + 16, 32.8, "PRIVATE", 10.5, c.MONO, 700, c.MUTED, spacing=1.2)
    return out


def render(cfg, data, index):
    item = cfg.FEATURED[index]
    repo = item.get("repo")
    live = data.get("repos", {}).get(repo, {}) if repo else {}
    svg_w, x, w = c.split_geometry(index)
    stagger = 0.12 * index

    lines = c.wrap(item["desc"], DESC_CHARS)
    if len(lines) > DESC_LINES:
        lines = lines[:DESC_LINES]
        lines[-1] = lines[-1].rstrip(".,;") + "…"

    body = [
        _status(item.get("status", "building"), private=not repo),
        c.arrow(w - PAD - 14, 22, delay=stagger),
        c.text(PAD, 66, item["title"], 15.5, c.MONO, 700),
    ]
    desc = "".join(
        c.text(PAD, 92 + 18 * i, line, 13, c.SANS, fill=c.INK_SOFT, cls="desc")
        for i, line in enumerate(lines)
    )
    body.append(f'<g class="fade" style="animation-delay:{0.3 + stagger:.2f}s">{desc}</g>')
    body.append(
        f'<line x1="{PAD}" y1="146" x2="{c.num(w - PAD)}" y2="146" stroke="{c.INK}" '
        'stroke-width="1" stroke-opacity=".18"/>'
    )

    footer_y = 171
    stack = live.get("language") or item.get("stack")
    if stack:
        body.append(f'<rect x="{PAD}" y="{footer_y - 9}" width="10" height="10" rx="2" fill="{c.INK}"/>')
        body.append(c.text(PAD + 17, footer_y, stack, 12, c.MONO, fill=c.INK_SOFT))
    if repo:
        stars = str(live.get("stars", 0))
        sw = c.text_width(stars, 12, "mono-b")
        body.append(_star(w - PAD - sw - 12, footer_y - 4.5))
        body.append(c.text(w - PAD, footer_y, stars, 12, c.MONO, 700, anchor="end"))

    h = c.full_card_height(FACE_H)
    framed = c.card(x, c.CARD_X, w, FACE_H, "".join(body))
    return c.svg_doc(
        svg_w, h, f'<g class="rise" style="animation-delay:{0.1 + stagger:.2f}s">{framed}</g>',
        fonts=("mono", "mono-b"), title=f"{item['title']}: {item['desc']}",
    )
