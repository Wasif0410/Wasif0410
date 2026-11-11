"""Contribution graph: one square per day, shaded in ink, weeks as columns."""
import datetime

from . import common as c

FACE_H = 216
TOP = 76  # month labels sit above the grid, legend below it
GAP = 3.2


def _weeks(days):
    first = datetime.date.fromisoformat(days[0]["date"])
    sunday = first - datetime.timedelta(days=(first.weekday() + 1) % 7)
    cols = {}
    for d in days:
        dt = datetime.date.fromisoformat(d["date"])
        col = (dt - sunday).days // 7
        cols.setdefault(col, []).append((dt, (dt.weekday() + 1) % 7, d["level"]))
    return [cols[k] for k in sorted(cols)]


def render(cfg, data):
    days = data["contributions"]["days"]
    weeks = _weeks(days)
    inner_w = c.CARD_W - 64
    pitch = min(15.2, (inner_w + GAP) / len(weeks))
    cell = pitch - GAP
    grid_w = len(weeks) * pitch - GAP
    x0 = (c.CARD_W - grid_w) / 2

    body = [c.label(x0, 38, "CONTRIBUTIONS · LAST 12 MONTHS")]
    right = x0 + grid_w
    tag = "REFRESHED DAILY"
    tw = c.text_width(tag, 11.5, "mono-b", 1.4)
    body.append(f'<circle class="pulse" cx="{c.num(right - tw - 12)}" cy="34" r="4" fill="{c.INK}"/>')
    body.append(c.label(right, 38, tag, anchor="end"))

    months_y = TOP - 9
    legend_y = TOP + 7 * pitch + 22
    last_label_col, last_month = -9, None
    for col, week in enumerate(weeks):
        x = x0 + col * pitch
        rects = "".join(
            f'<rect class="cell" x="{c.num(x)}" y="{c.num(TOP + row * pitch)}" '
            f'width="{c.num(cell)}" height="{c.num(cell)}" rx="2.5" fill="{c.GRAPH_LEVELS[min(level, 4)]}"/>'
            for _, row, level in week
        )
        body.append(f'<g class="fade" style="animation-delay:{0.1 + col * 0.02:.2f}s">{rects}</g>')
        month = week[0][0].month
        if month != last_month and col - last_label_col >= 3 and col < len(weeks) - 2:
            body.append(c.text(x, months_y, f"{week[0][0]:%b}", 10.5, c.MONO, fill=c.MUTED))
            last_label_col = col
        last_month = month

    # legend: LESS [] [] [] [] [] MORE, right-aligned under the grid
    sq, sp = 10, 13.5
    more_w = c.text_width("MORE", 10.5, "mono")
    lx = right - more_w - 8 - 5 * sp
    body.append(c.text(lx - 8, legend_y, "LESS", 10.5, c.MONO, fill=c.MUTED, anchor="end"))
    for i, colour in enumerate(c.GRAPH_LEVELS):
        body.append(
            f'<rect x="{c.num(lx + i * sp)}" y="{c.num(legend_y - 9)}" width="{sq}" height="{sq}" '
            f'rx="2" fill="{colour}"/>'
        )
    body.append(c.text(right, legend_y, "MORE", 10.5, c.MONO, fill=c.MUTED, anchor="end"))
    body.append(c.text(x0, legend_y, "one square per day", 10.5, c.MONO, fill=c.MUTED))

    h = c.full_card_height(FACE_H)
    return c.svg_doc(
        c.W, h, c.card(c.CARD_X, c.CARD_X, c.CARD_W, FACE_H, "".join(body)),
        fonts=("mono", "mono-b"), title="Contribution graph for the last 12 months, refreshed daily",
    )
