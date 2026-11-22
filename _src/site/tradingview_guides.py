"""Build the static keyword and PC guides from the English pages and local catalogs."""
import argparse
import json
import re
from collections import Counter
from html import unescape
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup, Tag

from chrome import DEPLOY, LABELS, LOCALES

GUIDES = ("tradingview-connect.html", "tradingview-webhook.html")
LANGS = [*LOCALES, "zh-hant"]
CATALOGS = Path(__file__).with_name("guide-copy")
TAGS = {"zh-hans": "zh-Hans", "zh-hant": "zh-Hant", "pt-br": "pt-BR"}
OG = {
    "en": "en_US", "ko": "ko_KR", "ru": "ru_RU", "vi": "vi_VN", "tr": "tr_TR",
    "pt-br": "pt_BR", "uk": "uk_UA", "id": "id_ID", "ja": "ja_JP", "de": "de_DE",
    "ur": "ur_PK", "fil": "fil_PH", "th": "th_TH", "ms": "ms_MY", "zh-hans": "zh_CN",
    "es": "es_419", "zh-hant": "zh_TW",
}
INLINE = {"a", "b", "br", "code", "em", "i", "span", "strong"}
UNCHANGED = {"DivAlarm", "TradingView"}


def soup(text):
    return BeautifulSoup(text, "html.parser")


def translate_blocks(tag, translate):
    """Keep links, emphasis, UI elements and copyable protocol literals in the template."""
    if tag.name in {"style", "script", "svg"} or tag.has_attr("data-keep"):
        return
    if tag.name == "code" and tag.get("id") != "hook-url":
        return
    children = tag.find_all(recursive=False)
    if not children:
        source = " ".join(tag.get_text().split())
        if source not in UNCHANGED and re.search("[a-zA-Z]", source):
            tag.string = translate(source)
        return
    if tag.name not in {"li", "p"} or any(t.name not in INLINE for t in tag.find_all()):
        for child in children:
            translate_blocks(child, translate)
        return
    # A lone link/strong/code is just a normal text element (or a literal).
    if len(children) == 1 and tag.get_text(strip=True) == children[0].get_text(strip=True):
        translate_blocks(children[0], translate)
        return
    fragment = soup(tag.decode_contents())
    originals = {}
    for idx, node in enumerate(fragment.find_all()):
        if node.name == "br":
            continue
        key = f"{node.name}{idx}"
        originals[key] = node.name, node.attrs, node.get_text() if node.name == "code" else None
        node.name, node.attrs = key, {}
    source = " ".join(fragment.decode_contents().split())
    localized = soup(translate(source))
    expected = Counter(n.name for n in fragment.find_all())
    if Counter(n.name for n in localized.find_all()) != expected:
        raise ValueError(f"Inline markup changed in {source}")
    for node in localized.find_all():
        if node.attrs:
            raise ValueError(f"Unexpected attributes in {source}")
        if node.name != "br":
            name, attrs, literal = originals[node.name]
            if literal is not None and node.get_text() != literal:
                raise ValueError(f"Protocol literal {literal!r} changed in {source}")
            node.name, node.attrs = name, attrs
    tag.clear()
    for child in list(localized.contents):
        tag.append(child.extract())


def localize_schema(value, lang, translate):
    if isinstance(value, list):
        return [localize_schema(item, lang, translate) for item in value]
    if not isinstance(value, dict):
        return value
    result = {}
    for key, item in value.items():
        if key in {"name", "description", "text"} and isinstance(item, str) and item not in UNCHANGED:
            result[key] = translate(item)
        elif key in {"url", "item"} and isinstance(item, str):
            directory = "zh-hans" if lang == "zh-hant" and item.endswith("/en/") else lang
            result[key] = item.replace("/en/", f"/{directory}/")
        elif key == "inLanguage":
            result[key] = TAGS.get(lang, lang)
        else:
            result[key] = localize_schema(item, lang, translate)
    return result


def localize(page, lang, translate):
    doc = soup((DEPLOY / "en" / page).read_text(encoding="utf-8"))
    doc.html["lang"] = TAGS.get(lang, lang)
    if lang == "ur":
        doc.html["dir"] = "rtl"
        for code in doc.select("code:not(#hook-url)"):
            code["dir"] = "ltr"
    translate_blocks(doc.title, translate)
    translate_blocks(doc.body, translate)
    for tag in doc.find_all():
        for key in ("alt", "aria-label", "title"):
            if tag.get(key):
                tag[key] = translate(tag[key])
    for meta in doc.select("meta[content]"):
        prop = meta.get("property") or meta.get("name")
        if prop in {"description", "og:title", "og:description", "twitter:title", "twitter:description"}:
            meta["content"] = translate(meta["content"])
        elif prop == "og:locale":
            meta["content"] = OG[lang]
        elif prop == "og:url":
            meta["content"] = meta["content"].replace("/en/", f"/{lang}/")
    schema = doc.find("script", type="application/ld+json")
    if schema:
        data = localize_schema(json.loads(schema.string), lang, translate)
        schema.string = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    canonical = doc.find("link", rel="canonical")
    if canonical:
        canonical["href"] = canonical["href"].replace("/en/", f"/{lang}/")
    for link in doc.select("a[href]"):
        target = urlsplit(link["href"])
        if target.netloc or target.scheme or not target.path:
            continue
        filename = target.path.split("/")[-1]
        if filename in GUIDES:
            link["href"] = f"{filename}?lang={lang}" + (f"#{target.fragment}" if target.fragment else "")
            if link.has_attr("hreflang"):
                link["hreflang"] = TAGS.get(lang, lang)
        elif lang == "zh-hant" and not target.path.startswith("/") and not (DEPLOY / lang / target.path).exists():
            # Traditional Chinese has the two guides; other site pages exist in Simplified Chinese.
            link["href"] = f"../zh-hans/{link['href']}"
    return str(doc)


def build(lang):
    catalog = json.loads((CATALOGS / f"{lang}.json").read_text(encoding="utf-8"))
    # Shared header/footer labels already come translated with the rest of the site.
    shared = {unescape(value): unescape(LABELS[lang][key])
              for key, value in LABELS["en"].items()} if lang in LABELS else {}
    def translate(source):
        if source in shared:
            return shared[source]
        if source not in catalog:
            raise ValueError(f"{lang}: missing translation for {source!r}")
        result = catalog[source]
        if not result.strip() or Counter(re.findall(r"\{\d+\}", source)) != Counter(re.findall(r"\{\d+\}", result)):
            raise ValueError(f"{lang}: empty or invalid placeholder in {source}")
        return result
    destination = DEPLOY / lang
    destination.mkdir(exist_ok=True)
    for page in GUIDES:
        html = localize(page, lang, translate)
        (destination / page).write_text(html, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list-strings", action="store_true", help="print the English messages for translators")
    ap.add_argument("languages", nargs="*", help="default: every translated locale except English and Korean")
    args = ap.parse_args()
    if args.list_strings:
        messages = {}
        def collect(text):
            messages[text] = text
            return text
        for filename in GUIDES:
            localize(filename, "en", collect)
        print(json.dumps(messages, ensure_ascii=False, indent=2))
    else:
        for locale in args.languages or LANGS:
            if locale not in LANGS:
                ap.error(f"Unknown language {locale!r}")
            if locale not in {"en", "ko"}:
                build(locale)
