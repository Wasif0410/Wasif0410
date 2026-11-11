"""Year in numbers: big total, one tall bar per month, and a column of three stats.

Only the busiest month carries a number (drawn as a white bar with an ink
outline and hard shadow); the current, unfinished month is drawn light.
"""
import datetime

from . import common as c

FACE_H = 304
PAD = 32
LEFT_W = 548  # bars and headline live in x = PAD .. PAD + LEFT_W
STATS_X = 632
BAR_TOP, BAR_BOTTOM = 132, 252
HEADLINE_Y = 98


def _headline(total):
    """'2,074' in ink, then 'contributions' in grey, sized to fill the left column."""
    words = f"{total} contributions"
    size = min(50, LEFT_W / c.text_width(words, 1))
    num_w = c.text_width(f"{total} ", size)
    return (
        f'<g class="rise" style="animation-delay:.1s">{c.text(PAD, HEADLINE_Y, total, size, c.DISPLAY)}</g>'
        f'<g class="rise" style="animation-delay:.25s">'
        + c.text(PAD + num_w, HEADLINE_Y, "contributions", size, c.DISPLAY, fill=c.GRAPH_LEVELS[2])
        + "</g>"
    )


def _bars(months):
    out = []
    peak_i = max(range(len(months)), key=lambda i: months[i]["total"]) if months else -1
    peak = months[peak_i]["total"] if months else 0
    pitch = LEFT_W / max(len(months), 1)
    bar_w = pitch * 0.74
    span = BAR_BOTTOM - BAR_TOP
    for i, m in enumerate(months):
        cx = PAD + pitch * (i + 0.5)
        x = cx - bar_w / 2
        total = m["total"]
        hgt = max(4, span * total / peak) if peak else 4
        y = BAR_BOTTOM - hgt
        delay = 0.4 + 0.06 * i
        is_current = i == len(months) - 1
        if i == peak_i and total:
            rect = (
                f'<rect x="{c.num(x + 3)}" y="{c.num(y + 3)}" width="{c.num(bar_w)}" height="{c.num(hgt)}" '
                f'rx="4" fill="{c.INK}"/>'
                f'<rect class="bar" x="{c.num(x)}" y="{c.num(y)}" width="{c.num(bar_w)}" height="{c.num(hgt)}" '
                f'rx="4" fill="{c.WHITE}" stroke="{c.INK}" stroke-width="2"/>'
            )
            out.append(c.text(cx, y - 9, c.fmt_int(total), 11.5, c.MONO, 700, anchor="middle",
                              cls="pop", delay=delay + 0.6))
        else:
            fill = c.INK if total and not is_current else (c.GRAPH_LEVELS[1] if total else c.PAPER_DEEP)
            rect = (
                f'<rect class="bar" x="{c.num(x)}" y="{c.num(y)}" width="{c.num(bar_w)}" '
                f'height="{c.num(hgt)}" rx="4" fill="{fill}"/>'
            )
        out.append(f'<g class="grow" style="animation-delay:{delay:.2f}s">{rect}</g>')
        month = datetime.date.fromisoformat(m["month"] + "-01")
        out.append(c.text(cx, BAR_BOTTOM + 22, f"{month:%b}", 11, c.MONO, fill=c.MUTED, anchor="middle"))
    return "".join(out)


def _stat(top, value, caption, delay, suffix=""):
    """Big number with a plain-English caption under it."""
    parts = [f'<g class="pop" style="animation-delay:{delay:.2f}s">',
             c.text(STATS_X, top + 40, value, 38, c.DISPLAY)]
    if suffix:
        parts.append(c.text(STATS_X + c.text_width(value + " ", 38), top + 40, suffix, 38,
                            c.DISPLAY, fill=c.GRAPH_LEVELS[2]))
    parts.append("</g>")
    parts.append(c.text(STATS_X, top + 64, caption, 13, c.SANS, fill=c.MUTED, cls="fade",
                        delay=delay + 0.15))
    return "".join(parts)


def render(cfg, data):
    s = data["contributions"]
    total = c.fmt_int(s["total"])
    active = s.get("active_days", sum(1 for d in s.get("days", []) if d["count"] > 0))
    busiest = s.get("busiest") or {"date": None, "count": 0}
    when = ""
    if busiest["date"]:
        dt = datetime.date.fromisoformat(busiest["date"])
        when = f", {dt:%b} {dt.day}"

    body = [
        c.label(PAD, 44, "THE LAST 12 MONTHS ON GITHUB", fill=c.MUTED),
        _headline(total),
        _bars(s["months"]),
    ]

    rule = f'stroke="{c.INK}" stroke-width="1" stroke-opacity=".18"'
    body.append(_stat(40, str(s["current_streak"]), "current streak, and the longest", 0.5,
                      suffix=f"/ {s['longest_streak']}"))
    body.append(f'<line x1="{STATS_X}" y1="124" x2="{c.CARD_W - PAD}" y2="124" {rule}/>')
    body.append(_stat(128, str(active), "days with a contribution", 0.65))
    body.append(f'<line x1="{STATS_X}" y1="212" x2="{c.CARD_W - PAD}" y2="212" {rule}/>')
    body.append(_stat(216, c.fmt_int(busiest["count"]), f"on the busiest day{when}", 0.8))

    h = c.full_card_height(FACE_H)
    title = (f"{total} contributions in the last 12 months. Current streak {s['current_streak']} days, "
             f"longest {s['longest_streak']}, {active} active days.")
    return c.svg_doc(c.W, h, c.card(c.CARD_X, c.CARD_X, c.CARD_W, FACE_H, "".join(body)), title=title)
