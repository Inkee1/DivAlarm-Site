"""Check that each published keyword guide can lead readers through PC setup."""
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

SITE = Path(__file__).resolve().parents[2]


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
    def test_pc_steps_include_the_manual_videos_and_illustrated_walkthrough(self):
        for lang in ("en", "ko"):
            with self.subTest(lang=lang):
                setup = Page(SITE / lang / "tradingview-connect.html")
                manual = Page(SITE / lang / "tradingview-webhook.html")
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
                    if target.path.endswith("tradingview-webhook.html") and target.fragment:
                        self.assertTrue(any(a.get("id") == target.fragment for _, a in manual.tags), url)

    def test_every_localized_manual_links_to_a_published_setup_page(self):
        guides = list(SITE.glob("*/tradingview-webhook.html"))
        self.assertGreaterEqual(len(guides), 16)
        for guide in guides:
            with self.subTest(lang=guide.parent.name):
                links = [urlsplit(url).path for url in Page(guide).attrs("a", "href")
                         if "tradingview-connect.html" in url]
                self.assertTrue(links)
                for path in links:
                    dest = ((SITE / path.lstrip("/")) if path.startswith("/") else (guide.parent / path)).resolve()
                    self.assertTrue(dest.is_file(), path)
                    local_setup = guide.with_name("tradingview-connect.html")
                    self.assertEqual(local_setup if local_setup.is_file() else SITE / "en/tradingview-connect.html", dest)


if __name__ == "__main__":
    unittest.main()
