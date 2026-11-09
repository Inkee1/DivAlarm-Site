"""Helpers shared by the page builders in _src/site."""
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from chrome import DEPLOY, LOCALES, PLAY_URL, body_script, footer_html, head_links, header_html

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "promo-data.json").read_text(encoding="utf-8"))
CASES = {c["id"]: c for c in DATA["cases"]}
HREFLANG = {"pt-br": "pt-BR", "zh-hans": "zh-Hans"}
OG_LOCALE = {"en": "en_US", "ko": "ko_KR"}

MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "ko": [f"{m}월" for m in range(1, 13)],
}


def usd(v):
    return "$" + f"{int(v + .5):,}"


def f1(v):
    return f"{v:.1f}"


def when(ts, lang, with_zone=True):
    """Alert time: UTC for English, Korea time for Korean (as in the marketing images)."""
    d = datetime.fromtimestamp(ts, timezone.utc)
    if lang == "ko":
        d = d + timedelta(hours=9)
        return f"{d.month}월 {d.day}일 {d:%H:%M}"
    return f"{d:%b} {d.day}, {d:%H:%M}" + (" UTC" if with_zone else "")


def hreflang(page):
    """page = 'index.html' or 'features.html' (index links to the folder)."""
    tail = "" if page == "index.html" else page
    out = "".join(f'<link href="https://www.divalarm.com/{loc}/{tail}" hreflang="{HREFLANG.get(loc, loc)}" rel="alternate"/>' for loc in LOCALES)
    return out + f'<link href="https://www.divalarm.com/en/{tail}" hreflang="x-default" rel="alternate"/>'


ICONS = {
    "bell": '<path d="M6 8a6 6 0 1 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>',
    "layers": '<path d="m12 2 10 5-10 5L2 7l10-5Z"/><path d="m2 17 10 5 10-5M2 12l10 5 10-5"/>',
    "clock": '<circle cx="12" cy="12" r="9.5"/><path d="M12 7v5l3 2"/>',
    "chart": '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 6-7"/>',
    "key": '<path d="M4 7h16M4 12h10M4 17h7"/><circle cx="18" cy="16" r="3"/>',
    "link": '<path d="M9 7H7a5 5 0 0 0 0 10h2M15 7h2a5 5 0 0 1 0 10h-2M8 12h8"/>',
    "phone": '<rect x="6" y="2.5" width="12" height="19" rx="2.5"/><path d="m9.5 12 1.8 1.8 3.4-3.6"/>',
    "keyhole": '<circle cx="8" cy="15" r="4"/><path d="m10.8 12.2 8.7-8.7M16 7l2.5 2.5M18.5 4.5 21 7"/>',
    "toggle": '<rect x="2.5" y="7" width="19" height="10" rx="5"/><circle cx="8" cy="12" r="2.5"/>',
    "list": '<path d="M8 6h12M8 12h12M8 18h12M3.5 6h.01M3.5 12h.01M3.5 18h.01"/>',
    "warn": '<path d="M12 3 2 20h20L12 3Z"/><path d="M12 10v4M12 17h.01"/>',
    "filter": '<path d="M3 5h18l-7 8v6l-4 2v-8L3 5Z"/>',
    "gift": '<rect x="3" y="8" width="18" height="13" rx="2"/><path d="M3 12h18M12 8v13M12 8S10.5 3 8 4s-1 4 4 4c5 0 6.5-3 4-4s-4 4-4 4"/>',
    "candles": '<path d="M6 3v3M6 15v6M18 3v6M18 17v4M12 5v4M12 19v2"/><rect x="4" y="6" width="4" height="9" rx="1"/><rect x="16" y="9" width="4" height="8" rx="1"/><rect x="10" y="9" width="4" height="10" rx="1"/>',
}


def icon(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def render(template, vals, keep=("ticker", "close")):
    """Fill {{key}} from vals. Unknown keys stay literal, so TradingView's {{ticker}} survives."""
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: str(vals[m.group(1)]) if m.group(1) in vals else m.group(0), template)
    left = sorted(set(re.findall(r"\{\{(\w+)\}\}", out)) - set(keep))
    if left:
        raise SystemExit(f"unfilled placeholders: {left}")
    return out


def chrome_vals(lang, page):
    return dict(lang=lang, play_url=PLAY_URL, head_links=head_links(), body_script=body_script(),
                site_header=header_html(lang, current=page), site_footer=footer_html(lang),
                hreflang=hreflang(page), og_locale=OG_LOCALE.get(lang, "en_US"))


def write(lang, page, html):
    (DEPLOY / lang / page).write_text(html, encoding="utf-8", newline="\n")
