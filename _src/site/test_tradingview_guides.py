"""Check that each published keyword guide can lead readers through PC setup."""
import re
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from bs4 import BeautifulSoup

SITE = Path(__file__).resolve().parents[2]
GUIDE_LOCALES = "en ko ja ru vi tr pt-br es id th de ms fil uk ur zh-hans zh-hant".split()


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.tags = []
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, name, attributes):
        self.tags.append((name, dict(attributes)))

    def attrs(self, tag, attr):
        return [a[attr] for name, a in self.tags if name == tag and a.get(attr)]


class TradingViewGuidesTest(unittest.TestCase):
    def test_all_diagnostic_states_supply_local_copy_and_format_variables(self):
        def strings(lang):
            path = SITE / lang / "tradingview-connect.html"
            return {el["data-k"]: el.get_text(strip=True)
                    for el in BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser").select("#i18n [data-k]")}
        english = strings("en")
        for lang in GUIDE_LOCALES:
            with self.subTest(lang=lang):
                translated = strings(lang)
                self.assertEqual(english.keys(), translated.keys())
                for key, value in translated.items():
                    self.assertTrue(value, key)
                    self.assertEqual(Counter(re.findall(r"\{\d+\}", english[key])),
                                     Counter(re.findall(r"\{\d+\}", value)), key)
                    if lang != "en" and len(english[key]) > 50:
                        self.assertNotEqual(english[key], value, key)

    def test_pc_steps_include_the_manual_videos_and_illustrated_walkthrough(self):
        for lang in GUIDE_LOCALES:
            with self.subTest(lang=lang):
                path = SITE / lang / "tradingview-connect.html"
                self.assertTrue(path.is_file(), path)
                setup = Page(path)
                manual = Page(SITE / lang / "tradingview-webhook.html")
                for page in (setup, manual):
                    html = next(a for tag, a in page.tags if tag == "html")
                    self.assertEqual(lang, html["lang"].lower())
                    if lang == "ur":
                        self.assertEqual("rtl", html.get("dir"))
                manual_ids = {a["id"] for _, a in manual.tags if "id" in a}
                self.assertTrue({"keyword-source", "keyword", "auto-order", "combination",
                                 "divalarm-keywords", "exchange-api-setup"} <= manual_ids)
                def shorts(page):
                    return Counter(urlsplit(url).path for url in page.attrs("a", "href")
                                   if "youtube.com/shorts/" in url)
                self.assertEqual(5, sum(shorts(manual).values()))
                self.assertEqual(shorts(manual), shorts(setup))
                examples = [a for tag, a in setup.tags if tag == "img" and "/tradingview-setup/" in a.get("src", "")]
                self.assertEqual(7, len({a["src"] for a in examples}))
                for img in examples:
                    self.assertTrue(img["alt"].strip())
                    self.assertTrue((SITE / lang / img["src"]).is_file(), img["src"])
                    self.assertIn(img["src"], setup.attrs("a", "href"))
                ids = [a["id"] for _, a in setup.tags if "id" in a]
                self.assertEqual(len(ids), len(set(ids)))
                for key in ("hook-url", "sample-message", "run-test", "hop-relay", "hop-phone"):
                    self.assertIn(key, ids)
                self.assertEqual({"hook-url", "sample-message"}, set(setup.attrs("button", "data-copy")))
                self.assertIn("AA Webhook test", (SITE / lang / "tradingview-connect.html").read_text(encoding="utf-8"))
                self.assertFalse(any("youtube" in url for url in setup.attrs("iframe", "src")))
                for url in setup.attrs("a", "href"):
                    target = urlsplit(url)
                    if not target.netloc and not target.path and target.fragment:
                        self.assertIn(target.fragment, ids)
                    if target.path.endswith("tradingview-webhook.html"):
                        self.assertEqual(lang, parse_qs(target.query).get("lang", [None])[0], url)
                        self.assertEqual((path.parent / target.path).resolve(),
                                         SITE / lang / "tradingview-webhook.html")
                        if target.fragment:
                            self.assertIn(target.fragment, manual_ids, url)

    def test_every_localized_manual_links_to_a_published_setup_page(self):
        for lang in GUIDE_LOCALES:
            with self.subTest(lang=lang):
                guide = SITE / lang / "tradingview-webhook.html"
                self.assertTrue(guide.is_file(), guide)
                links = [urlsplit(url) for url in Page(guide).attrs("a", "href")
                         if "tradingview-connect.html" in url]
                self.assertIn("connection-test", [link.fragment for link in links])
                for link in links:
                    dest = ((SITE / link.path.lstrip("/")) if link.path.startswith("/")
                            else (guide.parent / link.path)).resolve()
                    self.assertEqual(guide.with_name("tradingview-connect.html"), dest)
                    self.assertTrue(dest.is_file(), dest)
                    self.assertEqual(lang, parse_qs(link.query).get("lang", [None])[0])


if __name__ == "__main__":
    unittest.main()
