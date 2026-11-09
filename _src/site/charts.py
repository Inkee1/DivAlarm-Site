"""Inline SVG charts drawn from promo-data.json (the marketing images' data)."""
import html
import math
from datetime import datetime, timezone

from common import DATA, MONTHS, f1

C = {"ink": "#06122B", "grid": "#16305F", "da": "#22A9F2", "dahi": "#8AD8FF",
     "tv": "#8A93B0", "faint": "#5E719B", "up": "#3BD69B", "down": "#FF5D73"}


def _nice_step(span, want=5):
    raw = span / want
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def case_svg(case, lang, *, alert_label, tv_label, aria, narrow=False, cls="case-chart", uid="c"):
    """Price candles + DivAlarm RSI pane, the divergence, the alert pin and (if any)
    TradingView's later signal. The hero animates the hc-* classes; elsewhere they are static."""
    cs = case["candles"]
    n = len(cs)
    fs = 1.5 if narrow else 1
    W, H = (400, 400) if narrow else (720, 452)
    padL, padR = (4, 40) if narrow else (6, 52)
    pT, pB = (44, 246) if narrow else (34, 288)    # price pane
    rT, rB = (272, 392) if narrow else (320, 440)   # RSI pane
    bw = (W - padL - padR) / n
    x = lambda i: padL + (i + .5) * bw
    high = case["kind"] == "high"
    lo = min(k[3] for k in cs)
    hi = max(k[2] for k in cs)
    span = hi - lo
    # leave room for the alert label: above a top, below a bottom
    lo -= span * (.04 if high else .2)
    hi += span * .1
    y = lambda v: pB - (v - lo) / (hi - lo) * (pB - pT)
    yr = lambda v: rB - 8 - (v - 10) / (95 - 10) * (rB - rT - 16)
    zc = C["down"] if high else C["up"]
    gid = f"z{uid}{'n' if narrow else 'w'}"

    s = [f'<svg class="{cls} {"narrow" if narrow else "wide"}" viewBox="0 0 {W} {H}" role="img" aria-label="{html.escape(aria)}">',
         f'<defs><linearGradient id="{gid}" x1="0" y1="{0 if high else 1}" x2="0" y2="{1 if high else 0}">'
         f'<stop offset="0" stop-color="{zc}" stop-opacity=".02"/><stop offset="1" stop-color="{zc}" stop-opacity=".16"/></linearGradient></defs>']
    step = _nice_step(hi - lo)
    v = math.ceil(lo / step) * step
    while v < hi:
        lab = f"{v / 1000:g}K"
        s.append(f'<line x1="{padL}" x2="{W - padR + 4}" y1="{f1(y(v))}" y2="{f1(y(v))}" stroke="{C["grid"]}"/>'
                 f'<text x="{f1(W - padR + 6 * fs)}" y="{f1(y(v) + 4 * fs)}" font-size="{f1(11 * fs)}" fill="{C["faint"]}">{lab}</text>')
        v += step
    prev = None
    for i, k in enumerate(cs):
        d = datetime.fromtimestamp(k[0], timezone.utc)
        if prev is not None and d.month != prev and i > 2:
            s.append(f'<line x1="{f1(x(i))}" x2="{f1(x(i))}" y1="{pT}" y2="{pB}" stroke="{C["grid"]}" stroke-dasharray="2 6"/>'
                     f'<text x="{f1(x(i) + 5)}" y="{pB - 8}" font-size="{f1(11 * fs)}" fill="{C["faint"]}">{MONTHS[lang][d.month - 1]}</text>')
        prev = d.month

    det, far = case["detectedBar"], min(case["far"], n - 1)
    y0, y1 = sorted((y(case["detPrice"]), y(case["farPrice"])))
    s.append(f'<rect class="hc-div" x="{f1(x(det))}" y="{f1(y0)}" width="{f1(x(far) - x(det))}" height="{f1(y1 - y0)}" fill="url(#{gid})"/>')
    s.append(f'<line class="hc-div" x1="{f1(x(det))}" x2="{f1(x(far))}" y1="{f1(y(case["detPrice"]))}" y2="{f1(y(case["detPrice"]))}" stroke="{C["dahi"]}" stroke-opacity=".45" stroke-dasharray="4 5"/>')

    s.append('<g class="hc-reveal">')
    cw = max(1.6, bw * .6)
    for i, (t, o, h, l, cl) in enumerate(cs):
        col = C["up"] if cl >= o else C["down"]
        top, bot = y(max(o, cl)), y(min(o, cl))
        s.append(f'<line x1="{f1(x(i))}" x2="{f1(x(i))}" y1="{f1(y(h))}" y2="{f1(y(l))}" stroke="{col}" stroke-width="{1.3 if bw > 6 else 1}"/>'
                 f'<rect x="{f1(x(i) - cw / 2)}" y="{f1(top)}" width="{f1(cw)}" height="{f1(max(1.2, bot - top))}" rx="{1 if bw > 6 else 0}" fill="{col}"/>')
    s.append(f'<rect x="{padL}" y="{rT}" width="{W - padL - padR}" height="{rB - rT}" rx="10" fill="rgba(34,169,242,.07)" stroke="#1F4F8F"/>')
    for v in (30, 70):
        s.append(f'<line x1="{padL}" x2="{W - padR}" y1="{f1(yr(v))}" y2="{f1(yr(v))}" stroke="#24508F" stroke-dasharray="4 6"/>'
                 f'<text x="{f1(W - padR + 6 * fs)}" y="{f1(yr(v) + 4 * fs)}" font-size="{f1(11 * fs)}" fill="{C["faint"]}">{v}</text>')
    pts = [(x(i), yr(v)) for i, v in enumerate(case["rsiDa"]) if v is not None]
    s.append('<path d="M' + " L".join(f"{f1(a)} {f1(b)}" for a, b in pts) + '" fill="none" stroke="#D6ECFF" stroke-width="1.8" stroke-linejoin="round" opacity=".9"/>')
    s.append('</g>')
    s.append(f'<text x="{padL + 2}" y="{f1(rT - 8)}" font-size="{f1(12 * fs)}" font-weight="700" fill="{C["dahi"]}">DivAlarm RSI {case["period"]}</text>')

    dv = case["div"]
    off = -6 if high else 6
    s.append('<g class="hc-div">'
             f'<line x1="{f1(x(dv["start"]))}" y1="{f1(y(dv["valueStart"]) + off)}" x2="{f1(x(dv["end"]))}" y2="{f1(y(dv["valueEnd"]) + off)}" stroke="{C["da"]}" stroke-width="3" stroke-linecap="round"/>'
             f'<line x1="{f1(x(dv["start"]))}" y1="{f1(yr(dv["rsiStart"]))}" x2="{f1(x(dv["end"]))}" y2="{f1(yr(dv["rsiEnd"]))}" stroke="{C["da"]}" stroke-width="3" stroke-linecap="round"/>'
             + "".join(f'<circle cx="{f1(x(i))}" cy="{f1(yr(v))}" r="4" fill="{C["da"]}"/>' for i, v in ((dv["start"], dv["rsiStart"]), (dv["end"], dv["rsiEnd"])))
             + '</g>')

    if case.get("tvLate"):
        tvb = case["tvLate"]["detectedBar"]
        tw = (10 + len(tv_label) * 6.6) * fs
        tx = x(tvb) + 6 if x(tvb) + 6 + tw < W - padR else x(tvb) - 6 - tw
        s.append(f'<g class="hc-tv"><line x1="{f1(x(tvb))}" x2="{f1(x(tvb))}" y1="{pT + 10}" y2="{rB - 4}" stroke="#C9CFE0" stroke-opacity=".75" stroke-dasharray="3 4" stroke-width="1.4"/>'
                 f'<rect x="{f1(tx)}" y="{f1(rB - 8 - 22 * fs)}" width="{f1(tw)}" height="{f1(22 * fs)}" rx="6" fill="#C9CFE0"/>'
                 f'<text x="{f1(tx + tw / 2)}" y="{f1(rB - 8 - 7 * fs)}" text-anchor="middle" font-size="{f1(11.5 * fs)}" font-weight="800" fill="#0A1630">{html.escape(tv_label)}</text></g>')

    px, py = x(det), y(case["detPrice"])
    lw = (18 + len(alert_label) * 7.2) * fs
    lx = min(max(px - lw / 2, padL), W - padR - lw)
    if high:
        pill_y = pT - 4 - 26 * fs
        line_to = pT - 6
    else:
        pill_y = min(py + 18 * fs, pB - 26 * fs - 2)
        line_to = pill_y
    s.append(f'<g class="hc-pin"><line x1="{f1(px)}" x2="{f1(px)}" y1="{f1(py - 10 if high else py + 10)}" y2="{f1(line_to)}" stroke="{C["da"]}" stroke-width="1.5"/>'
             f'<rect x="{f1(lx)}" y="{f1(pill_y)}" width="{f1(lw)}" height="{f1(26 * fs)}" rx="{f1(13 * fs)}" fill="{C["da"]}"/>'
             f'<text x="{f1(lx + lw / 2)}" y="{f1(pill_y + 17.5 * fs)}" text-anchor="middle" font-size="{f1(13 * fs)}" font-weight="800" fill="#03122B">{html.escape(alert_label)}</text>'
             f'<circle cx="{f1(px)}" cy="{f1(py)}" r="12" fill="{C["da"]}" fill-opacity=".22"/>'
             f'<circle cx="{f1(px)}" cy="{f1(py)}" r="6" fill="{C["ink"]}" stroke="{C["da"]}" stroke-width="3"/></g>')
    s.append('</svg>')
    return "".join(s)


def proof_svg(aria, narrow=False):
    """One year of BTC 4H closes, the big reversals, and which tool signalled at each."""
    r = DATA["rev4h"]
    fs = 1.6 if narrow else 1
    W, H = (380, 330) if narrow else (760, 300)
    pad = 14
    pT, pB = (14, 120) if narrow else (14, 132)
    t0, t1 = r["start"], r["end"]
    closes = r["closes"][::(4 if narrow else 2)]
    items = sorted(r["items"], key=lambda it: it["time"])
    vals = [p for _, p in closes] + [it["price"] for it in items]
    lo, hi = min(vals), max(vals)
    X = lambda t: pad + (t - t0) / (t1 - t0) * (W - pad * 2)
    Y = lambda v: pB - (v - lo) / (hi - lo) * (pB - pT)
    m = len(items)
    colw = (W - pad * 2) / m
    colx = lambda k: pad + (k + .5) * colw
    rowA, rowB = (228, 300) if narrow else (218, 270)
    dot = min(9.0, colw * .4)

    s = [f'<svg class="proof-chart {"narrow" if narrow else "wide"}" viewBox="0 0 {W} {H}" role="img" aria-label="{html.escape(aria)}">']
    s.append('<path d="M' + " L".join(f"{f1(X(t))} {f1(Y(v))}" for t, v in closes) + f'" fill="none" stroke="{C["tv"]}" stroke-width="1.4" stroke-linejoin="round" opacity=".85"/>')
    for k, it in enumerate(items):
        px, py = X(it["time"]), Y(it["price"])
        cx = colx(k)
        s.append(f'<path d="M{f1(px)} {f1(py)} C{f1(px)} {f1(pB + 40)} {f1(cx)} {f1(pB + 30)} {f1(cx)} {f1(rowA - dot - 4)}" fill="none" stroke="{C["dahi"]}" stroke-opacity=".16"/>')
    for k, it in enumerate(items):
        px, py = X(it["time"]), Y(it["price"])
        col = C["up"] if it["kind"] == "low" else C["down"]
        s.append(f'<circle cx="{f1(px)}" cy="{f1(py)}" r="{f1(3.4 if narrow else 4.5)}" fill="{col}" stroke="{C["ink"]}" stroke-width="1.5"/>')
        cx = colx(k)
        s.append(f'<circle cx="{f1(cx)}" cy="{rowA}" r="{f1(dot)}" fill="{C["da"]}"/>' if it["da"] else
                 f'<circle cx="{f1(cx)}" cy="{rowA}" r="{f1(dot - 1)}" fill="none" stroke="#2C4C88" stroke-width="2"/>')
        s.append(f'<circle cx="{f1(cx)}" cy="{rowB}" r="{f1(dot)}" fill="#B9C0D6"/>' if it["tv"] else
                 f'<circle cx="{f1(cx)}" cy="{rowB}" r="{f1(dot - 1)}" fill="none" stroke="#2A3A60" stroke-width="2"/>')
    s.append(f'<text x="{pad}" y="{rowA - dot - 10}" font-size="{f1(12 * fs)}" font-weight="700" fill="{C["dahi"]}">DivAlarm</text>')
    s.append(f'<text x="{pad}" y="{rowB - dot - 10}" font-size="{f1(12 * fs)}" font-weight="700" fill="{C["tv"]}">TradingView</text>')
    s.append('</svg>')
    return "".join(s)
