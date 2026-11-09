"""Put the shared header/footer and theme on every legacy page, in every locale.

    python _src/site/apply_chrome.py          # from DEPLOY; safe to run repeatedly

Pages built from _src/site templates (<html data-da-built>) already contain the chrome
and are skipped, as are redirect stubs and the standalone connection-test tool. Run this
again after translate_deploy_locales.py regenerates locale folders.
"""
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chrome import DEPLOY, LOCALES, asset_version, body_script, footer_html, head_links, header_html  # noqa: E402

SKIP_FILES = {"tradingview-connect.html"}
BUILT_LANGS = {"en", "ko"}  # build.py writes these from _src/site templates


def blank(node):
    return isinstance(node, NavigableString) and not node.strip()


def frag(markup):
    return [n for n in BeautifulSoup(markup, "html.parser").contents if not blank(n)]


def remove(el):
    """Drop an element and the line break after it, so re-runs don't pile up blank lines."""
    if blank(el.next_sibling):
        el.next_sibling.extract()
    el.decompose()


def apply(path: Path, lang: str) -> str:
    raw = path.read_text(encoding="utf-8")
    if 'http-equiv="refresh"' in raw[:3000] or len(raw) < 1500:
        return "redirect"
    soup = BeautifulSoup(raw, "html.parser")
    html = soup.find("html")
    body, head = soup.body, soup.head
    if html is None or body is None or head is None:
        return "no-body"
    if html.has_attr("data-da-built"):
        if lang in BUILT_LANGS:
            return "built"
        # A built page that translate_deploy_locales.py copied into another locale:
        # swap in the localized header and footer, leave the rest as translated.
        top, foot = soup.find(id="da-top"), soup.find(id="da-foot")
        if top is None or foot is None:
            return "built-missing-chrome"
        skip = soup.select_one(".da-skip")
        if skip is not None:
            remove(skip)
        nodes = frag(header_html(lang, current=path.name))
        top.replace_with(nodes[-1])
        nodes[-1].insert_before(nodes[0])
        nodes[-1].insert_before(NavigableString("\n"))
        foot.replace_with(frag(footer_html(lang))[0])
        out = str(soup)
        if out != raw:
            path.write_text(out, encoding="utf-8", newline="\n")
            return "relocalized"
        return "unchanged"

    # previous chrome (idempotent) and legacy navigation/footer
    for el in soup.select("#da-top, #da-foot, .da-skip, [data-da-chrome]"):
        remove(el)
    for el in body.find_all(recursive=False):
        if any(c.startswith("navbar-logo-center") for c in (el.get("class") or [])):
            remove(el)
    for el in body.select("section.section-2"):
        if not el.get_text(strip=True) and not el.find(["img", "iframe", "video", "svg"]):
            remove(el)
    for el in soup.select("#wisesignal-legal-footer"):
        remove(el)

    # header first in <body>, a #main target for the skip link, footer + script last
    for node in reversed(frag(header_html(lang, current=path.name))):
        body.insert(0, NavigableString("\n"))
        body.insert(0, node)
    if not soup.find(id="main"):
        main = body.find("main")
        if main is not None:
            main["id"] = "main"
        else:
            header = body.find("header", id="da-top")
            header.insert_after(soup.new_tag("span", id="main"))
            header.insert_after(NavigableString("\n"))
    for node in frag(footer_html(lang)) + frag(body_script()):
        body.append(node)
        body.append(NavigableString("\n"))

    # theme stylesheets go last in <head> so they win over the Webflow CSS
    for node in frag(head_links(legacy=True)):
        head.append(node)
        head.append(NavigableString("\n"))

    out = str(soup)
    v = asset_version("js/lang-switcher.js", "css/lang-switcher.css")
    out = re.sub(r'(\.\./(?:js|css)/lang-switcher\.(?:js|css))(\?v=[0-9a-f]+)?"', rf'\1?v={v}"', out)
    if out != raw:
        path.write_text(out, encoding="utf-8", newline="\n")
        return "updated"
    return "unchanged"


def main(locales=None):
    counts = {}
    for lang in locales or LOCALES:
        root = DEPLOY / lang
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.html")):
            if path.name in SKIP_FILES:
                continue
            status = apply(path, lang)
            counts[status] = counts.get(status, 0) + 1
    print("chrome:", ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
