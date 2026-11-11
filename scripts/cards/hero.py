"""Top card: status pill, name in outlined block letters, role, headline, portrait."""
import re

from . import common as c

FACE_H = 360
NAME_SIZE = 118
NAME_X = 34
BASELINES = (156, 255)
EXTRUDE = 6  # depth of the hard block shadow behind the letters, in px
PORTRAIT_BOX = (572, 40, 276)  # x, y, size inside the card

# Shown on the right until portrait.svg exists (scripts/make_portrait.py).
TERMINAL_LINES = (
    ("$ whoami", True),
    ("wasif saeed, cs @ tmu", False),
    ("$ ls ~/building", True),
    ("probative   mechlens", False),
    ("trajectory  monelyth", False),
)


def _pill(text):
    tw = c.text_width(text, 11.5, "mono-b", 1.4)
    w = 30 + tw + 14
    return (
        '<g class="fade">'
        f'<rect x="35" y="31" width="{c.num(w)}" height="26" rx="13" fill="{c.INK}"/>'
        f'<rect x="32" y="28" width="{c.num(w)}" height="26" rx="13" fill="{c.PAPER}" '
        f'stroke="{c.INK}" stroke-width="1.8"/>'
        f'<circle class="pulse" cx="48" cy="41" r="4" fill="{c.INK}"/>'
        + c.text(60, 45.2, text, 11.5, c.MONO, 700, spacing=1.4)
        + "</g>"
    )


def _name(lines):
    stroke = f'stroke="{c.INK}" stroke-width="4" stroke-linejoin="round"'
    out = []
    for i, (word, base) in enumerate(zip(lines, BASELINES)):
        depth = "".join(
            c.text(NAME_X + k, base + k, word, NAME_SIZE, c.DISPLAY, fill=c.INK, extra=stroke)
            for k in range(1, EXTRUDE + 1)
        )
        out.append(f'<g class="fade" style="animation-delay:{0.75 + 0.12 * i:.2f}s">{depth}</g>')
        out.append(
            c.text(NAME_X, base, word, NAME_SIZE, c.DISPLAY, fill=c.WHITE, cls="drop",
                   delay=0.1 + 0.15 * i, extra=f'{stroke} paint-order="stroke"')
        )
    return "".join(out)


def _portrait(svg):
    x, y, size = PORTRAIT_BOX
    m = re.search(r'viewBox="\s*([-\d.]+)[\s,]+([-\d.]+)[\s,]+([-\d.]+)[\s,]+([-\d.]+)\s*"', svg)
    vx, vy, vw, vh = (float(v) for v in m.groups()) if m else (0, 0, size, size)
    inner = re.sub(r"^.*?<svg\b[^>]*>", "", svg, count=1, flags=re.S)
    inner = re.sub(r"</svg>\s*$", "", inner.strip())
    scale = size / max(vw, vh)
    return (
        f'<g transform="translate({c.num(x)},{c.num(y)}) scale({scale:.5f}) '
        f'translate({c.num(-vx)},{c.num(-vy)})">{inner}</g>'
    )


def _terminal():
    x, y, size = PORTRAIT_BOX
    w, h = size, 250
    y += 12
    parts = [
        f'<rect x="{x + 4}" y="{y + 4}" width="{w}" height="{h}" rx="10" fill="{c.INK}"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{c.PAPER}" '
        f'stroke="{c.INK}" stroke-width="2"/>',
        f'<line x1="{x}" y1="{y + 30}" x2="{x + w}" y2="{y + 30}" stroke="{c.INK}" stroke-width="2"/>',
    ]
    for i in range(3):
        parts.append(
            f'<circle cx="{x + 18 + 14 * i}" cy="{y + 15}" r="4.5" fill="none" '
            f'stroke="{c.INK}" stroke-width="1.6"/>'
        )
    parts.append(c.text(x + w / 2, y + 19.5, "~/wasif", 11, c.MONO, fill=c.MUTED, anchor="middle"))
    line_y = y + 62
    for i, (line, is_cmd) in enumerate(TERMINAL_LINES):
        parts.append(
            c.text(x + 18, line_y + 26 * i, line, 12.5, c.MONO, 700 if is_cmd else 400,
                   c.INK if is_cmd else c.INK_SOFT, cls="fade", delay=0.6 + 0.3 * i)
        )
    cursor_y = line_y + 26 * len(TERMINAL_LINES)
    parts.append(
        c.text(x + 18, cursor_y, "$", 12.5, c.MONO, 700, cls="fade",
               delay=0.6 + 0.3 * len(TERMINAL_LINES))
    )
    parts.append(
        f'<rect class="pulse" x="{x + 34}" y="{cursor_y - 11}" width="8" height="14" fill="{c.INK}"/>'
    )
    return f'<g class="rise" style="animation-delay:.3s">{"".join(parts)}</g>'


def render(cfg, data, portrait_svg=None):
    body = [_pill(cfg.PILL), _name(cfg.NAME_LINES)]
    body.append(c.text(NAME_X, 291, cfg.ROLE, 12.5, c.MONO, 700, c.INK_SOFT, spacing=1.6,
                       cls="rise", delay=0.9))
    for i, line in enumerate(c.wrap(cfg.HEADLINE, 58)[:2]):
        body.append(c.text(NAME_X, 318 + 21 * i, line, 15, c.SANS, fill=c.INK_SOFT,
                           cls="rise", delay=1.0 + 0.1 * i))
    body.append(_portrait(portrait_svg) if portrait_svg else _terminal())

    h = c.full_card_height(FACE_H)
    title = f"{' '.join(cfg.NAME_LINES).title()}. {cfg.HEADLINE}"
    return c.svg_doc(c.W, h, c.card(c.CARD_X, c.CARD_X, c.CARD_W, FACE_H, "".join(body)), title=title)
