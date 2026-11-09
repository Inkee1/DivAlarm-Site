"""Build the DivAlarm home page (en/index.html, ko/index.html).

    python _src/home/build_home.py            # from the DEPLOY folder

template.html holds the markup and CSS, this file holds the copy and draws the two charts
from promo-data.json (exported from `DivAlarm 오토메이션/promo/src/data.js`, the same data
the marketing images use). Other locales are produced from en/index.html by
translate_deploy_locales.py as before.

Copy rules (marketing/projects/divalarm/CLAUDE.md): no profit or win-rate claims, keep the
TradingView comparison's method note, say auto-orders use real funds with no paper mode,
and make no claim that API keys are never stored on a server (the app syncs them today).
"""
import html
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEPLOY = HERE.parent.parent
DATA = json.loads((HERE / "promo-data.json").read_text(encoding="utf-8"))
TEMPLATE = (HERE / "template.html").read_text(encoding="utf-8")

PLAY_URL = "https://play.google.com/store/apps/details?id=com.flutterflow.divalarm2"
LOCALES = ["en", "ko", "ru", "vi", "tr", "pt-br", "uk", "id", "ja", "de", "ur", "fil", "th", "ms", "zh-hans", "es"]
HREFLANG = {"pt-br": "pt-BR", "zh-hans": "zh-Hans"}

C = {"ink": "#06122B", "grid": "#16305F", "line": "#22407A", "da": "#22A9F2", "dahi": "#8AD8FF",
     "tv": "#8A93B0", "faint": "#5E719B", "up": "#3BD69B", "down": "#FF5D73"}


def usd(v):
    return "$" + f"{int(v + .5):,}"


def f1(v):
    return f"{v:.1f}"


# ---------------------------------------------------------------- hero chart
def hero_svg(L, narrow=False):
    c = DATA["janTop"]
    cs = c["candles"]
    n = len(cs)
    # narrow = phone layout: fewer pixels per bar, larger type so it stays legible at 340px
    fs = 1.5 if narrow else 1
    W, H = (400, 400) if narrow else (720, 452)
    padL, padR = (4, 40) if narrow else (6, 52)
    pT, pB = (44, 246) if narrow else (34, 288)   # price pane
    rT, rB = (272, 392) if narrow else (320, 440)  # RSI pane
    bw = (W - padL - padR) / n
    x = lambda i: padL + (i + .5) * bw
    lo = min(k[3] for k in cs)
    hi = max(k[2] for k in cs)
    span = hi - lo
    lo -= span * .04
    hi += span * .1
    y = lambda v: pB - (v - lo) / (hi - lo) * (pB - pT)
    yr = lambda v: rB - 8 - (v - 10) / (95 - 10) * (rB - rT - 16)

    s = []
    s.append(f'<svg class="hero-chart {'narrow' if narrow else 'wide'}" viewBox="0 0 {W} {H}" role="img" aria-label="{html.escape(L["chart_aria"])}">')
    s.append(f'<defs><linearGradient id="hz{'n' if narrow else 'w'}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["down"]}" stop-opacity=".02"/><stop offset="1" stop-color="{C["down"]}" stop-opacity=".16"/></linearGradient></defs>')
    # grid
    for v in range(60000, 110000, 10000):
        if lo < v < hi:
            s.append(f'<line x1="{padL}" x2="{W - padR + 4}" y1="{f1(y(v))}" y2="{f1(y(v))}" stroke="{C["grid"]}"/>')
            s.append(f'<text x="{W - padR + 6 * fs}" y="{f1(y(v) + 4 * fs)}" font-size="{f1(11 * fs)}" fill="{C["faint"]}">{v // 1000}K</text>')
    # month ticks
    for i, k in enumerate(cs):
        d = datetime.fromtimestamp(k[0], timezone.utc)
        if d.day == 1:
            s.append(f'<line x1="{f1(x(i))}" x2="{f1(x(i))}" y1="{pT}" y2="{pB}" stroke="{C["grid"]}" stroke-dasharray="2 6"/>')
            s.append(f'<text x="{f1(x(i) + 5)}" y="{pB - 8}" font-size="{f1(11 * fs)}" fill="{C["faint"]}">{L["months"][d.month - 1]}</text>')
    # drop zone after the alert (historical price action, no % label)
    det = c["detectedBar"]
    far = max(range(n), key=lambda i: -cs[i][3])
    s.append(f'<rect class="hc-div" x="{f1(x(det))}" y="{f1(y(c["detPrice"]))}" width="{f1(x(far) - x(det))}" height="{f1(y(cs[far][3]) - y(c["detPrice"]))}" fill="url(#hz{'n' if narrow else 'w'})"/>')
    s.append(f'<line class="hc-div" x1="{f1(x(det))}" x2="{f1(x(far))}" y1="{f1(y(c["detPrice"]))}" y2="{f1(y(c["detPrice"]))}" stroke="{C["dahi"]}" stroke-opacity=".45" stroke-dasharray="4 5"/>')

    # candles + RSI share one reveal
    s.append('<g class="hc-reveal">')
    cw = max(3, bw * .6)
    for i, (t, o, h, l, cl) in enumerate(cs):
        col = C["up"] if cl >= o else C["down"]
        top, bot = y(max(o, cl)), y(min(o, cl))
        s.append(f'<line x1="{f1(x(i))}" x2="{f1(x(i))}" y1="{f1(y(h))}" y2="{f1(y(l))}" stroke="{col}" stroke-width="1.3"/>'
                 f'<rect x="{f1(x(i) - cw / 2)}" y="{f1(top)}" width="{f1(cw)}" height="{f1(max(1.2, bot - top))}" rx="1" fill="{col}"/>')
    # RSI pane
    s.append(f'<rect x="{padL}" y="{rT}" width="{W - padL - padR}" height="{rB - rT}" rx="10" fill="rgba(34,169,242,.07)" stroke="#1F4F8F"/>')
    for v in (30, 70):
        s.append(f'<line x1="{padL}" x2="{W - padR}" y1="{f1(yr(v))}" y2="{f1(yr(v))}" stroke="#24508F" stroke-dasharray="4 6"/>'
                 f'<text x="{W - padR + 6 * fs}" y="{f1(yr(v) + 4 * fs)}" font-size="{f1(11 * fs)}" fill="{C["faint"]}">{v}</text>')
    pts = [(x(i), yr(v)) for i, v in enumerate(c["rsiDa"]) if v is not None]
    s.append('<path d="M' + " L".join(f"{f1(a)} {f1(b)}" for a, b in pts) + '" fill="none" stroke="#D6ECFF" stroke-width="1.8" stroke-linejoin="round" opacity=".9"/>')
    s.append('</g>')
    s.append(f'<text x="{padL + 2}" y="{f1(rT - 8)}" font-size="{f1(12 * fs)}" font-weight="700" fill="{C["dahi"]}">DivAlarm RSI {c["period"]}</text>')

    # divergence lines (price higher high, RSI lower high)
    dv = c["div"]
    s.append('<g class="hc-div">')
    s.append(f'<line x1="{f1(x(dv["start"]))}" y1="{f1(y(dv["valueStart"]) - 6)}" x2="{f1(x(dv["end"]))}" y2="{f1(y(dv["valueEnd"]) - 6)}" stroke="{C["da"]}" stroke-width="3" stroke-linecap="round"/>')
    s.append(f'<line x1="{f1(x(dv["start"]))}" y1="{f1(yr(dv["rsiStart"]))}" x2="{f1(x(dv["end"]))}" y2="{f1(yr(dv["rsiEnd"]))}" stroke="{C["da"]}" stroke-width="3" stroke-linecap="round"/>')
    for i, v in ((dv["start"], dv["rsiStart"]), (dv["end"], dv["rsiEnd"])):
        s.append(f'<circle cx="{f1(x(i))}" cy="{f1(yr(v))}" r="4" fill="{C["da"]}"/>')
    s.append('</g>')

    # TradingView's later signal
    tvb = c["tvLate"]["detectedBar"]
    lbl = L["chart_tv"]
    tw = (10 + len(lbl) * 6.6) * fs
    s.append(f'<g class="hc-tv"><line x1="{f1(x(tvb))}" x2="{f1(x(tvb))}" y1="{pT + 10}" y2="{rB - 4}" stroke="#C9CFE0" stroke-opacity=".75" stroke-dasharray="3 4" stroke-width="1.4"/>'
             f'<rect x="{f1(x(tvb) + 6)}" y="{f1(rB - 8 - 22 * fs)}" width="{f1(tw)}" height="{f1(22 * fs)}" rx="6" fill="#C9CFE0"/>'
             f'<text x="{f1(x(tvb) + 6 + tw / 2)}" y="{f1(rB - 8 - 7 * fs)}" text-anchor="middle" font-size="{f1(11.5 * fs)}" font-weight="800" fill="#0A1630">{html.escape(lbl)}</text></g>')

    # alert pin
    px, py = x(det), y(c["detPrice"])
    lab = L["chart_alert"]
    lw = (18 + len(lab) * 7.2) * fs
    lx = min(max(px - lw / 2, padL), W - padR - lw)
    s.append(f'<g class="hc-pin"><line x1="{f1(px)}" x2="{f1(px)}" y1="{f1(py - 10)}" y2="{pT - 6}" stroke="{C["da"]}" stroke-width="1.5"/>'
             f'<rect x="{f1(lx)}" y="{f1(pT - 4 - 26 * fs)}" width="{f1(lw)}" height="{f1(26 * fs)}" rx="{f1(13 * fs)}" fill="{C["da"]}"/>'
             f'<text x="{f1(lx + lw / 2)}" y="{f1(pT - 4 - 8.5 * fs)}" text-anchor="middle" font-size="{f1(13 * fs)}" font-weight="800" fill="#03122B">{html.escape(lab)}</text>'
             f'<circle cx="{f1(px)}" cy="{f1(py)}" r="12" fill="{C["da"]}" fill-opacity=".22"/>'
             f'<circle cx="{f1(px)}" cy="{f1(py)}" r="6" fill="{C["ink"]}" stroke="{C["da"]}" stroke-width="3"/></g>')
    s.append('</svg>')
    return "".join(s)


# ---------------------------------------------------------------- proof chart
def proof_svg(L, narrow=False):
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

    s = [f'<svg class="proof-chart {'narrow' if narrow else 'wide'}" viewBox="0 0 {W} {H}" role="img" aria-label="{html.escape(L["proof_aria"])}">']
    s.append('<path d="M' + " L".join(f"{f1(X(t))} {f1(Y(v))}" for t, v in closes) + f'" fill="none" stroke="{C["tv"]}" stroke-width="1.4" stroke-linejoin="round" opacity=".85"/>')
    for k, it in enumerate(items):
        px, py = X(it["time"]), Y(it["price"])
        cx = colx(k)
        s.append(f'<path d="M{f1(px)} {f1(py)} C{f1(px)} {f1(pB + 40)} {f1(cx)} {f1(pB + 30)} {f1(cx)} {f1(rowA - dot - 4)}" fill="none" stroke="{C["dahi"]}" stroke-opacity=".16"/>')
    for k, it in enumerate(items):
        px, py = X(it["time"]), Y(it["price"])
        col = C["up"] if it["kind"] == "low" else C["down"]
        s.append(f'<circle cx="{f1(px)}" cy="{f1(py)}" r="{f1(4.5 if not narrow else 3.4)}" fill="{col}" stroke="{C["ink"]}" stroke-width="1.5"/>')
        cx = colx(k)
        if it["da"]:
            s.append(f'<circle cx="{f1(cx)}" cy="{rowA}" r="{f1(dot)}" fill="{C["da"]}"/>')
        else:
            s.append(f'<circle cx="{f1(cx)}" cy="{rowA}" r="{f1(dot - 1)}" fill="none" stroke="#2C4C88" stroke-width="2"/>')
        if it["tv"]:
            s.append(f'<circle cx="{f1(cx)}" cy="{rowB}" r="{f1(dot)}" fill="#B9C0D6"/>')
        else:
            s.append(f'<circle cx="{f1(cx)}" cy="{rowB}" r="{f1(dot - 1)}" fill="none" stroke="#2A3A60" stroke-width="2"/>')
    s.append(f'<text x="{pad}" y="{rowA - dot - 10}" font-size="{f1(12 * fs)}" font-weight="700" fill="{C["dahi"]}">DivAlarm</text>')
    s.append(f'<text x="{pad}" y="{rowB - dot - 10}" font-size="{f1(12 * fs)}" font-weight="700" fill="{C["tv"]}">TradingView</text>')
    s.append('</svg>')
    return "".join(s)


# ---------------------------------------------------------------- copy
def when(ts, lang):
    d = datetime.fromtimestamp(ts, timezone.utc)
    if lang == "ko":
        d = d + timedelta(hours=9)
        return f"{d.month}월 {d.day}일 {d:%H:%M}"
    return f"{d:%b} {d.day}, {d:%H:%M} UTC"


ICONS = {
    "bell": '<path d="M6 8a6 6 0 1 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>',
    "layers": '<path d="m12 2 10 5-10 5L2 7l10-5Z"/><path d="m2 17 10 5 10-5M2 12l10 5 10-5"/>',
    "clock": '<circle cx="12" cy="12" r="9.5"/><path d="M12 7v5l3 2"/>',
    "chart": '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 6-7"/>',
    "key": '<path d="M4 7h16M4 12h10M4 17h7"/><circle cx="18" cy="16" r="3"/>',
    "link": '<path d="M9 7H7a5 5 0 0 0 0 10h2M15 7h2a5 5 0 0 1 0 10h-2M8 12h8"/>',
}


def feat_items(items):
    out = []
    for icon, dt, dd in items:
        out.append(f'<div class="feat"><dt><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[icon]}</svg>{dt}</dt><dd>{dd}</dd></div>')
    return "\n      ".join(out)


def table_rows(rows, L):
    out = []
    for q, tv, da in rows:
        out.append(f'<div class="row" role="row"><div class="q" role="rowheader">{q}</div>'
                   f'<div class="a-tv" role="cell" data-label="{L["tbl_tv"]}">{tv}</div>'
                   f'<div class="a-da" role="cell"><span class="who">{L["tbl_da"]}</span>{da}</div></div>')
    return "\n      ".join(out)


def plan_cards(plans):
    out = []
    for cls, name, tag, price, per, feats in plans:
        tag_html = f'<span class="tag">{tag}</span>' if tag else ""
        per_html = f"<small>{per}</small>" if per else ""
        lis = "".join(f"<li>{f}</li>" for f in feats)
        out.append(f'<div class="plan {cls}"><div class="plan-top"><h3>{name}</h3>{tag_html}</div><div class="price">{price}{per_html}</div><ul>{lis}</ul></div>')
    return "\n      ".join(out)


c = DATA["janTop"]
r4 = DATA["rev4h"]
EXCH = "Binance, Bybit, OKX, Bitget, Gate"

STRINGS = {
    "en": dict(
        og_locale="en_US",
        meta_title="DivAlarm | RSI Divergence Alarms and TradingView Auto-Orders",
        meta_desc="DivAlarm watches BTC and ETH for RSI divergences on 9 timeframes and rings through silent mode. Turn TradingView alerts into alarms and, with Pro, futures orders placed from your phone.",
        skip="Skip to content", nav_label="Main", menu="Menu",
        nav_features="Features", nav_performance="Performance", nav_tv="TradingView", nav_pricing="Pricing", nav_qna="Q&amp;A",
        sign_in="Sign in", my_account="My account", sign_out="Sign out", get_app="Get the app",
        h1_a="You can't watch charts all night.", h1_b="DivAlarm can.",
        hero_lead="DivAlarm watches BTC and ETH for RSI divergences from the 1-minute to the daily chart and rings through silent mode when one appears. Connect your TradingView alerts too, and with Pro your phone can place the futures order.",
        cta_play="Get it on Google Play", cta_trial="Try Premium free for 5 days",
        hero_note="Android app. Start free with 7 alerts, no card needed.",
        chip_market="BTCUSDT Perp", chip_tf="1D", chart_period="Dec 2025 – Feb 2026",
        months=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        chart_alert=f"Alert {usd(c['detPrice'])}", chart_tv="TradingView",
        chart_aria=f"Bitcoin daily chart, December 2025 to February 2026. DivAlarm sent a bearish divergence alert on {when(c['detectedAt'], 'en')} at {usd(c['detPrice'])}, 22 hours before the {usd(c['extPrice'])} top. TradingView's standard RSI divergence appeared six days later.",
        notif_time=when(c["detectedAt"], "en").split(", ")[1].replace(" UTC", ""),
        notif_title="BTCUSDT 1D bearish divergence",
        notif_body=f"RSI {c['period']} divergence is forming. Price {usd(c['detPrice'])}",
        st1_k="DivAlarm alert", st1_v=when(c["detectedAt"], "en").replace(" UTC", ""), st1_s=f"{usd(c['detPrice'])}, 22 hours before the top",
        st2_k="TradingView signal", st2_v=when(c["tvLate"]["detectedAt"], "en").replace(" UTC", ""), st2_s=f"{usd(c['tvLate']['price'])}, 6 days later",
        st3_k="January top", st3_v=usd(c["extPrice"]), st3_s="Jan 14 daily candle",
        hero_fine="Replayed on Binance BTCUSDT perpetual history, daily RSI 7, times in UTC. TradingView = standard RSI indicator divergence rules (5-bar pivots). Past signals don't guarantee future results.",
        cmp_h2="What changes when you add DivAlarm to TradingView",
        cmp_lead="Keep using TradingView for your charts. DivAlarm watches for divergences on its own, wakes you when one appears, and can act on your alerts.",
        proof_h3=f"{r4['reversals']} big Bitcoin reversals in the past year",
        proof_p="On the 4-hour chart we marked every swing that reversed 8% or more, then checked which tool had a same-direction RSI divergence signal at the turn.",
        proof_aria=f"Bitcoin 4-hour price over 12 months with {r4['reversals']} reversals. DivAlarm had a divergence signal at {r4['divalarm']} of them, TradingView's standard indicator at {r4['tv']}.",
        proof_fine="Reversal: a 4H swing that retraced 8%+ from the prior high or low. Caught: a same-direction RSI divergence signal on that high or low bar (±1 bar). DivAlarm sends far more alerts than TradingView, and not every alert leads to a reversal. TradingView side reproduced from the standard RSI indicator's published rules. Binance BTCUSDT perpetual, Sep 2025 – Sep 2026.",
        tbl_label="TradingView alone compared with DivAlarm", tbl_tv="TradingView alone", tbl_da="With DivAlarm",
        rows=[
            ("Spotting divergences", "The standard RSI indicator confirms a divergence 5 bars after the pivot.", "Early alerts while the divergence is still forming, on 9 timeframes from 1m to 1D. Early signals can be invalidated, so you can wait for Confirmed instead."),
            ("When your phone is on silent", "A regular push notification. Silent mode and Do Not Disturb mute it.", "A full alarm that rings through silent mode until you stop it."),
            ("Acting on a signal", "You open your exchange and place the order yourself.", f"Pro places the futures order for you on {EXCH}."),
            ("Your own TradingView alerts", "Arrive as a notification.", "A keyword in the alert message triggers the alarm, combined rule or order you chose."),
        ],
        auto_h2="Auto-orders in three steps",
        auto_lead="No code and no separate bot service. Your TradingView alert sends a keyword, and the DivAlarm app on your phone does the rest.",
        s1_h="Add your exchange key", s1_p=f"In the app, pick {EXCH.replace(', Gate', ' or Gate')} and paste an API key with futures trading permission.",
        s2_h="Make a keyword rule", s2_p="Choose a keyword, such as AA, and what it does: market or limit order, size, leverage, take-profit and stop-loss.",
        s3_h="Send it from TradingView", s3_p="Paste your DivAlarm webhook URL into a TradingView alert and put the keyword in the message. When the alert fires, your phone places the order and tells you the result.",
        mock_saved="Saved", mock_perm="Permission: futures trading. Withdrawals off.", mock_when="when this keyword arrives",
        mock_long="Long", mock_market="Market", mock_msg="TradingView alert message", mock_toast="Order placed: BTCUSDT long, market",
        ctl_h3="You stay in control",
        c1_b="Your phone signs every order", c1_s="TradingView alerts carry only your keyword. Your API key and secret never go into an alert message.",
        c2_b="Trading permission is enough", c2_s="DivAlarm never needs withdrawal permission. Keep withdrawals switched off on the key you create.",
        c3_b="One switch stops orders", c3_s="Turn Auto-Order off at any time. Your alarms keep ringing.",
        c4_b="Every result is recorded", c4_s="Each order sends a notification with the result and stays in the order log.",
        risk_auto="Auto-orders use real money on leveraged futures, and there is no paper-trading mode. Start with a small size. Auto-Order requires Pro.",
        auto_link="Read the TradingView setup guide",
        feat_h2="Built for alerts you can't miss",
        feats=[
            ("bell", "Alarms that break silent mode", "Five alarm styles, ring once or repeat, and your own sound."),
            ("layers", "Choose your signal stage", "Early for speed, Confirmed for stability, or both."),
            ("clock", "Nine timeframes", "1m, 3m, 5m, 15m, 30m, 1h, 4h, 12h and 1D. Turn each one on or off."),
            ("chart", "More than divergence", "Supertrend flips, support and resistance, Bollinger Band breaks, EMA crosses and price levels."),
            ("key", "Keyword alarms", "Trigger them from TradingView webhooks or, on Android, from other apps' notifications. Try them 5 times free."),
            ("link", "Combined rules", "Ring only when signals line up, like (1 &amp; 2) | 3 within a time window you set."),
        ],
        feat_link1="See all features", feat_link2="See past signals", feat_link3="What is RSI divergence?",
        plans_h2="Start free. Upgrade when you need more.",
        plans=[
            ("", "Free", "", "$0", "", ["7 alerts to start, then one every 3 days", "5 keyword alarm tries"]),
            ("", "Basic", "", "$6.9", "/month", ["BTC and ETH divergence alerts", "Early alerts and forced alarms", "Filters and advanced indicator alerts", "Custom alarm sounds"]),
            ("pro", "Pro", "For TradingView users", "$14.9", "/month", ["Everything in Basic", "TradingView webhooks and keyword alarms", "Combined alarms", f"Auto-orders on {EXCH.replace(', Gate', ' and Gate')}"]),
        ],
        plans_note="Annual plans save 30%. Paid plans start with a 5-day free trial. A payment method is required, and the plan renews automatically unless you cancel before the trial ends.",
        plans_cta="Compare plans",
        close_a="Reversals don't wait.", close_b="Keep your alarm on.",
        foot_risk="DivAlarm is an alert tool, not investment advice. Crypto futures trading carries a high risk of loss. Past signals don't guarantee future results.",
        f_product="Product", f_downloads="Downloads", f_guides="Guides", f_rsi="RSI divergence", f_manual="User manual", f_tv="TradingView setup",
        f_company="Company", f_referral="Referral rewards", f_contact="Contact",
    ),
    "ko": dict(
        og_locale="ko_KR",
        meta_title="DivAlarm | RSI 다이버전스 알람과 TradingView 자동 주문",
        meta_desc="DivAlarm은 BTC·ETH RSI 다이버전스를 9개 시간대에서 지켜보다가 무음 모드도 뚫고 알람을 울려요. TradingView 알림을 알람으로, Pro에서는 폰이 넣는 선물 주문으로 바꿔 보세요.",
        skip="본문으로 건너뛰기", nav_label="주 메뉴", menu="메뉴",
        nav_features="기능", nav_performance="신호 기록", nav_tv="TradingView 연결", nav_pricing="요금제", nav_qna="Q&amp;A",
        sign_in="로그인", my_account="내 계정", sign_out="로그아웃", get_app="앱 받기",
        h1_a="밤새 차트를 볼 수는 없잖아요.", h1_b="DivAlarm이 대신 봅니다.",
        hero_lead="BTC와 ETH의 RSI 다이버전스를 1분봉부터 일봉까지 지켜보다가, 신호가 나오면 무음 모드도 뚫고 알람을 울려요. TradingView 알림도 연결할 수 있고, Pro에서는 폰이 선물 주문까지 넣어요.",
        cta_play="Google Play에서 받기", cta_trial="프리미엄 5일 무료체험",
        hero_note="Android 앱이에요. 무료 알림 7회로 결제 없이 시작할 수 있어요.",
        chip_market="BTCUSDT 무기한", chip_tf="일봉", chart_period="2025년 12월 – 2026년 2월",
        months=[f"{m}월" for m in range(1, 13)],
        chart_alert=f"알림 {usd(c['detPrice'])}", chart_tv="TradingView",
        chart_aria=f"비트코인 일봉 차트, 2025년 12월부터 2026년 2월. DivAlarm은 {when(c['detectedAt'], 'ko')}(한국 시간) {usd(c['detPrice'])}에서 하락 다이버전스 알림을 보냈어요. {usd(c['extPrice'])} 고점 22시간 전이에요. TradingView 기본 RSI 다이버전스는 6일 뒤에 나왔어요.",
        notif_time=when(c["detectedAt"], "ko").split(" ")[-1],
        notif_title="BTCUSDT 1D 하락 다이버전스",
        notif_body=f"RSI {c['period']} 다이버전스가 형성되고 있어요. 현재가 {usd(c['detPrice'])}",
        st1_k="DivAlarm 알림", st1_v=when(c["detectedAt"], "ko"), st1_s=f"{usd(c['detPrice'])}, 고점 22시간 전",
        st2_k="TradingView 신호", st2_v=when(c["tvLate"]["detectedAt"], "ko"), st2_s=f"{usd(c['tvLate']['price'])}, 6일 뒤",
        st3_k="1월 고점", st3_v=usd(c["extPrice"]), st3_s="1월 14일 일봉",
        hero_fine="Binance BTCUSDT 무기한 선물 과거 데이터로 재현한 일봉 RSI 7, 한국 시간 기준. TradingView는 기본 RSI 지표의 다이버전스 규칙(피벗 좌우 5봉) 기준. 과거 신호가 미래 결과를 보장하지 않아요.",
        cmp_h2="TradingView만 쓸 때와 무엇이 다를까요",
        cmp_lead="차트는 지금처럼 TradingView로 보세요. DivAlarm은 다이버전스를 따로 지켜보고, 신호가 나오면 깨워 주고, 내 알림에 맞춰 주문까지 넣을 수 있어요.",
        proof_h3=f"최근 1년, 비트코인 큰 반전 {r4['reversals']}번",
        proof_p="4시간봉에서 8% 이상 되돌린 스윙을 모두 표시하고, 그 반전 지점에서 같은 방향 RSI 다이버전스 신호가 나왔는지 확인했어요.",
        proof_aria=f"최근 12개월 비트코인 4시간봉과 큰 반전 {r4['reversals']}번. DivAlarm은 {r4['divalarm']}번, TradingView 기본 지표는 {r4['tv']}번 반전 지점에서 다이버전스 신호를 냈어요.",
        proof_fine="반전: 4시간봉 기준 직전 고점·저점 대비 8% 이상 되돌린 스윙. 포착: 그 고점·저점 봉(±1봉)에서 같은 방향 RSI 다이버전스 신호가 나온 경우. DivAlarm은 TradingView보다 훨씬 많은 알림을 보내며, 모든 알림이 반전으로 이어지지는 않아요. TradingView 쪽은 기본 RSI 지표의 공개 규칙으로 재현. Binance BTCUSDT 무기한 선물, 2025.9 – 2026.9.",
        tbl_label="TradingView만 쓸 때와 DivAlarm을 함께 쓸 때 비교", tbl_tv="TradingView만", tbl_da="DivAlarm과 함께",
        rows=[
            ("다이버전스 찾기", "기본 RSI 지표는 피벗 뒤 5봉이 지나야 다이버전스를 확정해요.", "다이버전스가 형성되는 중에 Early 알림을 보내요. 1분봉부터 일봉까지 9개 시간대. Early 신호는 무효화될 수 있어서 Confirmed만 받도록 고를 수도 있어요."),
            ("폰이 무음일 때", "일반 푸시 알림이라 무음·방해 금지 모드에서는 소리가 나지 않아요.", "끌 때까지 울리는 알람이 무음 모드도 뚫고 울려요."),
            ("신호를 보고 주문할 때", "거래소 앱을 열고 직접 주문해야 해요.", f"Pro에서는 {EXCH}에 선물 주문을 대신 넣어요."),
            ("내가 만든 TradingView 알림", "알림으로만 와요.", "메시지 속 키워드에 따라 정해 둔 알람, 결합 규칙, 주문이 실행돼요."),
        ],
        auto_h2="자동 주문, 세 단계면 끝",
        auto_lead="코딩도, 따로 돌리는 봇 서비스도 필요 없어요. TradingView 알림이 키워드를 보내면 폰의 DivAlarm 앱이 나머지를 처리해요.",
        s1_h="거래소 키 넣기", s1_p=f"앱에서 {EXCH} 중 하나를 고르고, 선물 거래 권한이 있는 API 키를 붙여넣어요.",
        s2_h="키워드 규칙 만들기", s2_p="AA 같은 키워드를 정하고 무엇을 할지 고르세요. 시장가·지정가, 수량, 레버리지, 익절·손절까지 정할 수 있어요.",
        s3_h="TradingView에서 보내기", s3_p="TradingView 알림에 내 DivAlarm 웹훅 URL을 넣고 메시지에 키워드를 적어요. 알림이 울리면 폰이 주문을 넣고 결과를 알려 줘요.",
        mock_saved="저장됨", mock_perm="권한: 선물 거래. 출금은 꺼 둠.", mock_when="이 키워드가 오면",
        mock_long="롱", mock_market="시장가", mock_msg="TradingView 알림 메시지", mock_toast="주문 완료: BTCUSDT 롱, 시장가",
        ctl_h3="주도권은 계속 나에게",
        c1_b="주문 서명은 내 폰에서", c1_s="TradingView 알림에는 키워드만 담겨요. API 키와 시크릿은 알림 메시지에 들어가지 않아요.",
        c2_b="거래 권한이면 충분해요", c2_s="DivAlarm은 출금 권한이 필요 없어요. API 키를 만들 때 출금은 꺼 두세요.",
        c3_b="스위치 하나로 주문 중지", c3_s="자동 주문은 언제든 끌 수 있고, 꺼도 알람은 계속 울려요.",
        c4_b="모든 결과는 기록으로", c4_s="주문마다 결과 알림이 오고 주문 로그에 남아요.",
        risk_auto="자동 주문은 레버리지 선물 계좌의 실제 자금으로 실행되고, 모의 거래 모드는 없어요. 작은 수량부터 시작하세요. 자동 주문은 Pro 전용이에요.",
        auto_link="TradingView 연결 가이드 보기",
        feat_h2="놓치면 안 되는 알림을 위해",
        feats=[
            ("bell", "무음 모드를 뚫는 알람", "알람 스타일 5가지, 한 번 또는 반복, 내가 고른 알림음까지."),
            ("layers", "신호 단계 고르기", "빠른 Early, 안정적인 Confirmed, 또는 둘 다."),
            ("clock", "9개 시간대", "1분, 3분, 5분, 15분, 30분, 1시간, 4시간, 12시간, 일봉. 시간대마다 켜고 끌 수 있어요."),
            ("chart", "다이버전스 말고도", "슈퍼트렌드 전환, 지지·저항, 볼린저 밴드 돌파, EMA 교차, 가격 알림."),
            ("key", "키워드 알람", "TradingView 웹훅이나, Android에서는 다른 앱 알림 속 키워드로 실행해요. 5회 무료로 써 볼 수 있어요."),
            ("link", "결합 규칙", "(1 &amp; 2) | 3처럼, 정한 시간 안에 신호가 겹칠 때만 울려요."),
        ],
        feat_link1="기능 전체 보기", feat_link2="지난 신호 보기", feat_link3="RSI 다이버전스란?",
        plans_h2="무료로 시작하고, 필요할 때 업그레이드",
        plans=[
            ("", "무료", "", "$0", "", ["처음 7회 알림, 이후 3일에 1회", "키워드 알람 5회 체험"]),
            ("", "베이직", "", "$6.9", "/월", ["BTC·ETH 다이버전스 알림", "Early 알림과 강제 알람", "필터와 고급 지표 알림", "맞춤 알림음"]),
            ("pro", "프로", "TradingView 사용자용", "$14.9", "/월", ["베이직 기능 전부", "TradingView 웹훅·키워드 알람", "결합 알람", "거래소 5곳 자동 주문"]),
        ],
        plans_note="연간 결제는 30% 할인돼요. 유료 플랜은 5일 무료체험으로 시작해요. 결제수단 등록이 필요하고, 체험이 끝나기 전에 취소하지 않으면 자동으로 갱신돼요.",
        plans_cta="요금제 비교하기",
        close_a="반전은 기다려주지 않아요.", close_b="알람을 켜 두세요.",
        foot_risk="DivAlarm은 알림 도구이며 투자 조언이 아니에요. 암호화폐 선물 거래는 원금 손실 위험이 커요. 과거 신호가 미래 결과를 보장하지 않아요.",
        f_product="제품", f_downloads="다운로드", f_guides="가이드", f_rsi="RSI 다이버전스", f_manual="사용 설명서", f_tv="TradingView 연결",
        f_company="회사", f_referral="추천 보상", f_contact="문의하기",
    ),
}


def ld_json(L, lang):
    return json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": "https://www.divalarm.com/#organization", "name": "DivAlarm", "url": "https://www.divalarm.com"},
        {"@type": "WebSite", "@id": "https://www.divalarm.com/#website", "url": "https://www.divalarm.com", "name": "DivAlarm", "inLanguage": lang, "publisher": {"@id": "https://www.divalarm.com/#organization"}},
        {"@type": "SoftwareApplication", "name": "DivAlarm", "applicationCategory": "FinanceApplication", "operatingSystem": "Android",
         "url": f"https://www.divalarm.com/{lang}/", "description": L["meta_desc"], "publisher": {"@id": "https://www.divalarm.com/#organization"},
         "featureList": ["RSI divergence alerts", "Silent-mode-breaking mobile alarms", "TradingView webhook keyword alarms", "Exchange auto-orders from the phone"]},
        {"@type": "WebPage", "url": f"https://www.divalarm.com/{lang}/", "name": L["meta_title"], "description": L["meta_desc"], "inLanguage": lang, "isPartOf": {"@id": "https://www.divalarm.com/#website"}},
    ]}, ensure_ascii=False)


def hreflang():
    out = ""
    for loc in LOCALES:
        out += f'<link href="https://www.divalarm.com/{loc}/" hreflang="{HREFLANG.get(loc, loc)}" rel="alternate"/>'
    out += '<link href="https://www.divalarm.com/en/" hreflang="x-default" rel="alternate"/>'
    return out


def build(lang):
    L = dict(STRINGS[lang])
    vals = {k: v for k, v in L.items() if isinstance(v, str)}
    vals.update(
        lang=lang, lang_img=lang, play_url=PLAY_URL,
        ld_json=ld_json(L, lang), hreflang=hreflang(),
        hero_svg=hero_svg(L) + hero_svg(L, True), proof_svg=proof_svg(L) + proof_svg(L, True),
        n_da=str(r4["divalarm"]), n_tv=str(r4["tv"]), n_total=str(r4["reversals"]),
        tbl_rows=table_rows(L["rows"], L), feat_items=feat_items(L["feats"]), plan_cards=plan_cards(L["plans"]),
    )
    # Only known keys are replaced, so TradingView placeholders like {{ticker}} stay literal.
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: vals.get(m.group(1), m.group(0)), TEMPLATE)
    (DEPLOY / lang / "index.html").write_text(out, encoding="utf-8", newline="\n")
    left = sorted(set(re.findall(r"\{\{(\w+)\}\}", out)) - {"ticker", "close"})
    print(lang, "ok" if not left else f"unfilled: {left}")


if __name__ == "__main__":
    for lang in ("en", "ko"):
        build(lang)
