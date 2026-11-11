"""'Shipped in <year>' card: the count, and every finished project as an outlined pill."""
from . import common as c

PAD = 32
CHIPS_X = 214  # pills fill x = CHIPS_X .. card width - PAD
CHIP_H = 30
CHIP_GAP_X = 10
CHIP_GAP_Y = 12
CHIP_PAD = 13
CHIP_SIZE = 12
TOP = 30


def layout(names, width):
    """Greedy rows of pills: returns [(name, x, row, w)] and the number of rows."""
    placed, x, row = [], 0.0, 0
    for name in names:
        w = c.text_width(name, CHIP_SIZE, "mono-b") + 2 * CHIP_PAD
        if x and x + w > width:
            x, row = 0.0, row + 1
        placed.append((name, x, row, w))
        x += w + CHIP_GAP_X
    return placed, (row + 1 if names else 0)


def render(cfg, data):
    names = list(cfg.SHIPPED)
    placed, rows = layout(names, c.CARD_W - PAD - CHIPS_X)
    chips_h = rows * CHIP_H + max(rows - 1, 0) * CHIP_GAP_Y
    face_h = max(156, TOP + chips_h + TOP)

    body = [
        c.label(PAD, 44, f"SHIPPED IN {cfg.SHIPPED_YEAR}"),
        f'<g class="pop" style="animation-delay:.2s">{c.text(PAD, 112, str(len(names)), 64, c.DISPLAY)}</g>',
        c.text(PAD, 136, "finished projects", 12.5, c.MONO, 700, c.INK_SOFT, cls="fade", delay=0.4),
        f'<line x1="{CHIPS_X - 22}" y1="{TOP}" x2="{CHIPS_X - 22}" y2="{face_h - TOP}" '
        f'stroke="{c.INK}" stroke-width="1" stroke-opacity=".18"/>',
    ]
    for i, (name, x, row, w) in enumerate(placed):
        cx = CHIPS_X + x
        cy = TOP + row * (CHIP_H + CHIP_GAP_Y)
        body.append(
            f'<g class="pop" style="animation-delay:{0.4 + 0.07 * i:.2f}s">'
            f'<rect x="{c.num(cx + 3)}" y="{c.num(cy + 3)}" width="{c.num(w)}" height="{CHIP_H}" '
            f'rx="{CHIP_H / 2}" fill="{c.INK}"/>'
            f'<rect x="{c.num(cx)}" y="{c.num(cy)}" width="{c.num(w)}" height="{CHIP_H}" '
            f'rx="{CHIP_H / 2}" fill="{c.PAPER}" stroke="{c.INK}" stroke-width="1.8"/>'
            + c.text(cx + CHIP_PAD, cy + 19.5, name, CHIP_SIZE, c.MONO, 700, extra='class="chip"')
            + "</g>"
        )

    h = c.full_card_height(face_h)
    title = f"Shipped in {cfg.SHIPPED_YEAR}: {len(names)} finished projects. " + ", ".join(names)
    return c.svg_doc(c.W, h, c.card(c.CARD_X, c.CARD_X, c.CARD_W, face_h, "".join(body)),
                     fonts=("display", "mono-b"), title=title)
