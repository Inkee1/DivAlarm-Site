"""Browser regression tests for the signed-in webhook connection diagnostic."""
import functools
import http.server
import json
import threading
import unittest
from pathlib import Path

try:
    from playwright.sync_api import expect, sync_playwright
except ImportError:
    sync_playwright = None

ROOT = Path(__file__).resolve().parents[2]


class QuietFiles(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@unittest.skipUnless(sync_playwright, "Install Playwright and Chromium for browser tests")
class ConnectionTestUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(
            ("127.0.0.1", 0), functools.partial(QuietFiles, directory=ROOT)
        )
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = "http://127.0.0.1:" + str(cls.server.server_port)
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.context = self.browser.new_context()
        self.addCleanup(self.context.close)
        self.sent = []
        self.status = 200
        self.retry = 120
        self.context.route("**/*", self.route)

    def route(self, route):
        url = route.request.url
        if url.startswith(self.base):
            if "/posthog.js" in url:
                return route.fulfill(content_type="text/javascript", body="")
            return route.continue_()
        if "/firebasejs/" in url:
            modules = {
                "firebase-app.js": "export const initializeApp=()=>({}),getApps=()=>[],getApp=()=>({});",
                "firebase-auth.js": """export const getAuth=()=>({}),onAuthStateChanged=(a,f)=>{
                  window.login=uid=>f(uid?{uid,email:'demo@example.test'}:null);
                  window.login(sessionStorage.getItem('account')||'demo');
                },signOut=()=>{},signInWithCustomToken=()=>Promise.resolve(),
                GoogleAuthProvider=class{},signInWithPopup=()=>{};""",
                "firebase-firestore.js": """export const getFirestore=()=>({}),doc=(d,...path)=>path,
                  getDoc=async path=>({exists:()=>path.length===2,data:()=>({hookid:'fixture'})}),
                  onSnapshot=(_,on)=>{window.ack=id=>on({data:()=>({test_id:id,issues:[]}),
                    metadata:{hasPendingWrites:false}});return ()=>{};};""",
            }
            return route.fulfill(content_type="text/javascript", headers={"Access-Control-Allow-Origin": "*"},
                                 body=modules[url.rsplit("/", 1)[-1]])
        if url.endswith("/hookRelay/hook/fixture"):
            body = route.request.post_data_json
            self.sent.append(body["divalarm_test"])
            return route.fulfill(status=self.status, content_type="application/json", headers={
                "Access-Control-Allow-Origin": "*", "Access-Control-Expose-Headers": "Retry-After, X-Dropped-Reason",
                "Retry-After": str(self.retry),
                "X-Dropped-Reason": "test_hourly_limit" if self.status == 429 else "",
            }, body=json.dumps({"success": self.status == 200}))
        return route.abort()

    def open(self, lang="en"):
        page = self.context.new_page()
        page.set_default_timeout(6000)
        page.goto(f"{self.base}/{lang}/tradingview-connect.html?lang={lang}", wait_until="domcontentloaded")
        expect(page.locator("#run-test")).to_be_visible()
        return page

    def test_accepted_test_waits_across_tabs_and_reloads_for_the_same_account(self):
        first = self.open()
        second = self.open()
        first.locator("#run-test").click()
        expect(first.locator("#hop-relay")).to_have_attribute("data-state", "ok")
        first.evaluate("id=>window.ack(id)", self.sent[0])
        expect(first.locator("#hop-phone")).to_have_attribute("data-state", "ok")
        for page in (first, second):
            expect(page.locator("#run-test")).to_be_disabled()
        first.reload(wait_until="domcontentloaded")
        expect(first.locator("#run-test")).to_be_visible()
        expect(first.locator("#run-test")).to_be_disabled()
        second.evaluate("window.login('another-account')")
        expect(second.locator("#run-test")).to_be_enabled()
        self.assertEqual(len(self.sent), 1)

    def test_hourly_retry_after_counts_down_and_allows_retry_on_expiry(self):
        self.status, self.retry = 429, 1500
        page = self.open("ko")
        page.clock.install()
        button = page.locator("#run-test")
        button.click()
        expect(page.locator("#hop-relay")).to_have_attribute("data-state", "fail")
        expect(button).to_be_disabled()
        expect(button).to_contain_text("25:00")
        page.clock.fast_forward(1_500_001)
        expect(button).to_be_enabled()
        self.assertEqual(len(self.sent), 1)

    def test_traditional_chinese_is_selectable_on_guides_only(self):
        p = self.open()
        p.locator(".div-lang-trigger").click()
        option = p.locator(".div-lang-item[data-lang='zh-hant']")
        expect(option).to_be_visible()
        option.click()
        expect(p).to_have_url(self.base + "/zh-hant/tradingview-connect.html?lang=zh-hant")
        expect(p.locator("html")).to_have_attribute("lang", "zh-Hant")
        p.goto(self.base + "/en/tradingview-webhook.html?lang=zh-TW#keyword")
        p.wait_for_url("**/zh-hant/tradingview-webhook.html?lang=zh-hant#keyword")
        p.goto(self.base + "/en/index.html?lang=en")
        self.assertEqual(p.locator(".div-lang-item[data-lang='zh-hant']").count(), 0)


if __name__ == "__main__":
    unittest.main()
