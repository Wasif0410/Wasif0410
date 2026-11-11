"""The three BUILD / RESEARCH / LEARN tiles, and the slim section-title card."""
from . import common as c

FACE_H = 180
TITLE_H = 70
PAD = 22


def tile_value(tile, data):
    if tile["value"] is not None:
        return str(tile["value"])
    if tile["key"] == "learn":
        return c.fmt_int(data.get("trajectory_entries", 0))
    return "-"


def render(cfg, data, index):
    tile = cfg.TILES[index]
    svg_w, x, w = c.split_geometry(index)
    stagger = 0.15 * index
    body = [
        c.label(PAD, 36, tile["label"]),
        c.arrow(w - PAD - 14, 23, delay=stagger),
        f'<g class="pop" style="animation-delay:{0.35 + stagger:.2f}s">'
        + c.text(PAD, 108, tile_value(tile, data), 60, c.DISPLAY)
        + "</g>",
        c.text(PAD, 134, tile["caption"], 13, c.MONO, 700, c.INK_SOFT),
        c.text(PAD, 158, tile["note"], 12, c.SANS, fill=c.MUTED),
    ]
    h = c.full_card_height(FACE_H)
    framed = c.card(x, c.CARD_X, w, FACE_H, "".join(body))
    return c.svg_doc(
        svg_w, h, f'<g class="rise" style="animation-delay:{stagger:.2f}s">{framed}</g>',
        title=f"{tile['label'].split('/')[-1].strip()}: {tile_value(tile, data)} {tile['caption']}",
    )


def title(cfg, text, label):
    body = [
        c.text(PAD, 45, text, 24, c.DISPLAY, fill=c.INK, spacing=0.5),
        c.label(c.CARD_W - PAD, 41, label, fill=c.MUTED, anchor="end"),
    ]
    h = c.full_card_height(TITLE_H)
    return c.svg_doc(
        c.W, h, c.card(c.CARD_X, c.CARD_X, c.CARD_W, TITLE_H, "".join(body)),
        title=text.capitalize(),
    )
