"""Year in numbers: total contributions, streaks, busiest day, one bar per month."""
import datetime

from . import common as c

FACE_H = 262
PAD = 32
BAR_TOP, BAR_BOTTOM = 182, 230


def _stat(x, label, value, sub, delay):
    return (
        c.text(x, 62, label, 10.5, c.MONO, 700, c.MUTED, spacing=1.2, cls="fade", delay=delay)
        + f'<g class="pop" style="animation-delay:{delay + 0.1:.2f}s">'
        + c.text(x, 102, value, 32, c.DISPLAY)
        + "</g>"
        + c.text(x, 124, sub, 12, c.MONO, fill=c.INK_SOFT, cls="fade", delay=delay + 0.2)
    )


def render(cfg, data):
    s = data["contributions"]
    total = c.fmt_int(s["total"])
    body = [c.label(PAD, 38, "THE LAST 12 MONTHS ON GITHUB")]

    body.append(f'<g class="rise" style="animation-delay:.1s">{c.text(PAD, 108, total, 58, c.DISPLAY)}</g>')
    body.append(c.text(PAD + c.text_width(total, 58) + 12, 108, "contributions", 15, c.MONO, 700,
                       c.INK_SOFT, cls="fade", delay=0.4))
    body.append(c.text(PAD, 132, "commits, PRs, issues and reviews", 12, c.MONO, fill=c.MUTED,
                       cls="fade", delay=0.5))

    busiest = s.get("busiest") or {"date": None, "count": 0}
    when = ""
    if busiest["date"]:
        dt = datetime.date.fromisoformat(busiest["date"])
        when = f"on {dt:%b} {dt.day}"
    cur, best = s["current_streak"], s["longest_streak"]
    stats = (
        ("CURRENT STREAK", str(cur), "day" if cur == 1 else "days"),
        ("LONGEST STREAK", str(best), "day" if best == 1 else "days"),
        ("BUSIEST DAY", str(busiest["count"]), when),
    )
    for i, (label, value, sub) in enumerate(stats):
        body.append(_stat(468 + 136 * i, label, value, sub, 0.3 + 0.12 * i))

    body.append(
        f'<line x1="{PAD}" y1="150" x2="{c.CARD_W - PAD}" y2="150" stroke="{c.INK}" '
        'stroke-width="1.5" stroke-dasharray="2 5" stroke-linecap="round"/>'
    )

    months = s["months"]
    peak = max((m["total"] for m in months), default=0) or 1
    pitch = (c.CARD_W - 2 * PAD) / max(len(months), 1)
    bar_w = pitch * 0.62
    for i, m in enumerate(months):
        cx = PAD + pitch * (i + 0.5)
        hgt = max(3, (BAR_BOTTOM - BAR_TOP) * m["total"] / peak)
        fill = c.INK if m["total"] else c.PAPER_DEEP
        delay = 0.5 + 0.06 * i
        body.append(
            f'<g class="grow" style="animation-delay:{delay:.2f}s"><rect class="bar" '
            f'x="{c.num(cx - bar_w / 2)}" y="{c.num(BAR_BOTTOM - hgt)}" width="{c.num(bar_w)}" '
            f'height="{c.num(hgt)}" rx="3" fill="{fill}"/></g>'
        )
        if m["total"]:
            body.append(c.text(cx, BAR_BOTTOM - hgt - 6, c.fmt_int(m["total"]), 10, c.MONO,
                               fill=c.INK_SOFT, anchor="middle", cls="fade", delay=delay + 0.4))
        month = datetime.date.fromisoformat(m["month"] + "-01")
        body.append(c.text(cx, BAR_BOTTOM + 18, f"{month:%b}", 10.5, c.MONO, fill=c.MUTED,
                           anchor="middle"))

    h = c.full_card_height(FACE_H)
    title = f"{total} contributions in the last 12 months, current streak {cur}, longest {best}"
    return c.svg_doc(c.W, h, c.card(c.CARD_X, c.CARD_X, c.CARD_W, FACE_H, "".join(body)), title=title)
