"""Featured repo cards: name, short description, live stars and main language."""
import math

from . import common as c

FACE_H = 176
PAD = 22
DESC_CHARS = 36
DESC_LINES = 3


def _star(cx, cy, r_out=6.5, r_in=2.8):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = -math.pi / 2 + i * math.pi / 5
        pts.append(f"{c.num(cx + r * math.cos(a))},{c.num(cy + r * math.sin(a))}")
    return f'<polygon points="{" ".join(pts)}" fill="{c.INK}" stroke="{c.INK}" stroke-width="1" stroke-linejoin="round"/>'


def render(cfg, data, index):
    item = cfg.FEATURED[index]
    name = item["repo"]
    live = data.get("repos", {}).get(name, {})
    svg_w, x, w = c.split_geometry(index)
    stagger = 0.12 * index

    lines = c.wrap(item["desc"], DESC_CHARS)
    if len(lines) > DESC_LINES:
        lines = lines[:DESC_LINES]
        lines[-1] = lines[-1].rstrip(".,;") + "…"

    body = [
        c.text(PAD, 40, name, 15.5, c.MONO, 700),
        c.arrow(w - PAD - 14, 26, delay=stagger),
    ]
    desc = "".join(
        c.text(PAD, 68 + 18 * i, line, 13, c.SANS, fill=c.INK_SOFT, cls="desc")
        for i, line in enumerate(lines)
    )
    body.append(f'<g class="fade" style="animation-delay:{0.3 + stagger:.2f}s">{desc}</g>')
    body.append(
        f'<line x1="{PAD}" y1="128" x2="{c.num(w - PAD)}" y2="128" stroke="{c.INK}" '
        'stroke-width="1.5" stroke-dasharray="2 5" stroke-linecap="round"/>'
    )

    footer_y = 154
    if live.get("language"):
        body.append(f'<rect x="{PAD}" y="{footer_y - 9}" width="10" height="10" rx="2" fill="{c.INK}"/>')
        body.append(c.text(PAD + 17, footer_y, live["language"], 12, c.MONO, fill=c.INK_SOFT))
    stars = str(live.get("stars", 0))
    sw = c.text_width(stars, 12, "mono")
    body.append(_star(w - PAD - sw - 12, footer_y - 4.5))
    body.append(c.text(w - PAD, footer_y, stars, 12, c.MONO, 700, anchor="end"))

    h = c.full_card_height(FACE_H)
    framed = c.card(x, c.CARD_X, w, FACE_H, "".join(body))
    return c.svg_doc(
        svg_w, h, f'<g class="rise" style="animation-delay:{0.1 + stagger:.2f}s">{framed}</g>',
        fonts=("mono", "mono-b"), title=f"{name}: {item['desc']}",
    )
