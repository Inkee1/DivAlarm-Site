import { initializeApp, getApps, getApp } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js";
import { getAuth, onAuthStateChanged, signOut, signInWithCustomToken, GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-auth.js";
import { getFirestore, doc, getDoc, onSnapshot } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-firestore.js";

const RELAY = "https://asia-northeast1-divergence-alarm.cloudfunctions.net/hookRelay/hook/";
const PHONE_TIMEOUT_MS = 30000;
const TEST_INTERVAL_SECONDS = 120;

// The relay enforces both limits. The button shows its next allowed time in the page language.
const quotaText = {
  en: ["One test per account every 2 minutes, up to 5 in any 60 minutes.", "Try again in {0}"],
  ko: ["계정당 2분에 한 번, 최근 1시간 동안 최대 5회까지 테스트할 수 있습니다.", "{0} 후 다시 전송"],
  ja: ["テストは1アカウントにつき2分に1回、直近60分で最大5回です。", "あと {0} で再送信"],
  ru: ["С одного аккаунта можно отправлять тест раз в 2 минуты, до 5 раз за любые 60 минут.", "Повторить через {0}"],
  vi: ["Mỗi tài khoản có thể gửi một lần thử sau mỗi 2 phút, tối đa 5 lần trong 60 phút.", "Gửi lại sau {0}"],
  tr: ["Her hesap 2 dakikada bir, 60 dakikalık bir sürede en fazla 5 test gönderebilir.", "{0} sonra tekrar gönder"],
  "pt-br": ["Cada conta pode enviar um teste a cada 2 minutos, até 5 em qualquer período de 60 minutos.", "Tentar de novo em {0}"],
  es: ["Cada cuenta puede enviar una prueba cada 2 minutos, hasta 5 en un período de 60 minutos.", "Volver a enviar en {0}"],
  id: ["Setiap akun dapat mengirim satu tes setiap 2 menit, maksimal 5 kali dalam rentang 60 menit.", "Kirim lagi dalam {0}"],
  th: ["แต่ละบัญชีส่งสัญญาณทดสอบได้ทุก 2 นาที สูงสุด 5 ครั้งในช่วง 60 นาที", "ส่งอีกครั้งใน {0}"],
  de: ["Pro Konto ist alle 2 Minuten ein Test möglich, höchstens 5 innerhalb von 60 Minuten.", "Erneut senden in {0}"],
  ms: ["Setiap akaun boleh menghantar satu ujian setiap 2 minit, sehingga 5 kali dalam tempoh 60 minit.", "Hantar semula dalam {0}"],
  fil: ["Puwedeng magpadala ng isang test bawat 2 minuto sa bawat account, hanggang 5 sa loob ng 60 minuto.", "Ipadala muli pagkalipas ng {0}"],
  uk: ["З одного облікового запису можна надіслати один тест кожні 2 хвилини, до 5 разів за будь-які 60 хвилин.", "Повторити через {0}"],
  ur: ["ہر اکاؤنٹ سے ہر 2 منٹ میں ایک ٹیسٹ اور کسی بھی 60 منٹ کے دوران زیادہ سے زیادہ 5 ٹیسٹ بھیجے جا سکتے ہیں۔", "{0} بعد دوبارہ بھیجیں"],
  "zh-hans": ["每个账号每 2 分钟可测试一次，任意 60 分钟内最多 5 次。", "{0} 后可重新发送"],
  "zh-hant": ["每個帳號每 2 分鐘可測試一次，任意 60 分鐘內最多 5 次。", "{0} 後可重新傳送"],
};

const $ = (id) => document.getElementById(id);
const T = Object.fromEntries([...document.querySelectorAll("#i18n [data-k]")].map((el) => [el.dataset.k, el.textContent.trim()]));
const fmt = (s, ...a) => s.replace(/\{(\d)\}/g, (_, i) => a[i] ?? "");
const say = (msg) => { $("live").textContent = msg; };
const pageLang = document.documentElement.lang.toLowerCase();
const [quotaDescription, waitLabel] = quotaText[pageLang] || quotaText[pageLang.split("-")[0]] || quotaText.en;
const runButton = $("run-test");
const quotaNote = document.createElement("p");
quotaNote.id = "test-quota";
quotaNote.textContent = quotaDescription;
runButton.after(quotaNote);
runButton.setAttribute("aria-describedby", quotaNote.id);
const urlPlaceholder = $("hook-url-placeholder");
const initialHopDetails = ["hop-send", "hop-relay", "hop-phone"].map((id) => [id, $(id + "-detail").innerHTML]);
const plansUrl = pageLang === "zh-hant" ? "../zh-hans/pricing.html" : "pricing.html";
let activeEnv = null;
let running = false;
let attempted = false;
let nextTestAt = 0;
let timer = null;
let pendingPhone = null;

function storageKey() {
  return "divalarm.webhook-test.next." + activeEnv.account;
}

function storedDeadline() {
  try {
    return Number(localStorage.getItem(storageKey())) || 0;
  } catch {
    return 0;
  }
}

function renderButton() {
  clearTimeout(timer);
  if (!activeEnv) return;
  const seconds = Math.max(0, Math.ceil((nextTestAt - Date.now()) / 1000));
  runButton.disabled = running || seconds > 0;
  if (running) {
    runButton.textContent = T.running;
  } else if (seconds) {
    const clock = Math.floor(seconds / 60) + ":" + String(seconds % 60).padStart(2, "0");
    runButton.textContent = fmt(waitLabel, clock);
    timer = setTimeout(renderButton, 1000);
  } else {
    runButton.textContent = attempted ? T.runAgain : T.run;
  }
}

function holdButton(seconds) {
  if (!Number.isFinite(seconds) || seconds <= 0) return;
  nextTestAt = Math.max(storedDeadline(), nextTestAt, Date.now() + seconds * 1000);
  try { localStorage.setItem(storageKey(), String(nextTestAt)); } catch { /* Private browsing. */ }
  renderButton();
}

function setEnvironment(env) {
  pendingPhone?.cancel();
  pendingPhone = null;
  activeEnv = env;
  attempted = false;
  running = false;
  nextTestAt = env ? storedDeadline() : 0;
  renderButton();
}

window.addEventListener("storage", (event) => {
  if (!activeEnv || event.key !== storageKey()) return;
  nextTestAt = Math.max(nextTestAt, storedDeadline());
  renderButton();
});
window.addEventListener("pageshow", () => {
  if (activeEnv) {
    nextTestAt = Math.max(nextTestAt, storedDeadline());
    renderButton();
  }
});
runButton.addEventListener("click", () => runTest(activeEnv));

// ---------- view helpers ----------
function show(view) {
  $("gate-signin").hidden = view !== "signin";
  $("gate-nohook").hidden = view !== "nohook";
  $("tester").hidden = view !== "ready";
}

function setHop(id, state, html) {
  const hop = $(id);
  hop.dataset.state = state;
  if (html != null) $(id + "-detail").innerHTML = html;
}
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const list = (items) => "<ul>" + items.map((t) => `<li>${esc(t)}</li>`).join("") + "</ul>";

function setHookUrl(url) {
  $("hook-url").textContent = url;
  document.querySelector('[data-copy="hook-url"]').disabled = false;
}

function showLastTest(data) {
  if (!data || !data.received_at) return;
  const when = data.received_at.toDate ? data.received_at.toDate() : new Date(data.received_at);
  const el = $("last-test");
  el.textContent = fmt(T.lastTest, when.toLocaleString(document.documentElement.lang), data.device || T.yourPhone);
  el.hidden = false;
}

// ---------- copy ----------
document.addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-copy]");
  if (!btn) return;
  const text = $(btn.dataset.copy).textContent.trim();
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const range = document.createRange();
    range.selectNodeContents($(btn.dataset.copy));
    const sel = getSelection(); sel.removeAllRanges(); sel.addRange(range);
    document.execCommand("copy");
    sel.removeAllRanges();
  }
  btn.textContent = T.copied; btn.dataset.done = "";
  say(T.copiedLive);
  clearTimeout(btn._t);
  btn._t = setTimeout(() => { btn.textContent = T.copy; delete btn.dataset.done; }, 2000);
});

// ---------- connection test ----------
async function runTest(env) {
  if (!env || env !== activeEnv || running || Date.now() < nextTestAt) return;
  attempted = running = true;
  renderButton();
  setHop("hop-send", "busy", esc(T.sendBusy));
  setHop("hop-relay", "idle", esc(T.relayBusy));
  setHop("hop-phone", "idle", esc(T.phoneBusy));
  say(T.sendBusy);

  const testId = "t_" + crypto.randomUUID().replace(/-/g, "").slice(0, 24);
  const phone = env.waitForPhone(testId, PHONE_TIMEOUT_MS);
  pendingPhone = phone;
  let res;
  try {
    res = await env.send(testId);
  } catch {
    if (env !== activeEnv) return;
    phone.cancel();
    setHop("hop-send", "fail", esc(T.sendFail));
    return finish();
  }
  if (env !== activeEnv) return;
  setHop("hop-send", "ok", esc(T.sendOk));

  if (res.status === 204) {
    const msg = /^qpd_/.test(res.reason || "") ? T.relayDaily : /rate/.test(res.reason || "") ? T.relayRate : T.relayStopped;
    setHop("hop-relay", "fail", esc(msg) + (msg === T.relayStopped ? ` <a href="${plansUrl}">${esc(T.plans)}</a>` : ""));
    phone.cancel();
    setHop("hop-phone", "idle", "");
    return finish();
  }
  if (res.status === 429) {
    const testLimit = res.reason === "test_cooldown" || res.reason === "test_hourly_limit";
    holdButton(res.retryAfter || (testLimit ? TEST_INTERVAL_SECONDS : 0));
    setHop("hop-relay", "fail", esc(testLimit ? quotaDescription : T.relayRate));
    setHop("hop-phone", "idle", "");
    phone.cancel();
    return finish();
  }
  if (res.status !== 200) { setHop("hop-relay", "fail", esc(fmt(T.relayError, res.status))); phone.cancel(); return finish(); }

  holdButton(res.retryAfter || TEST_INTERVAL_SECONDS);
  setHop("hop-relay", "ok", esc(T.relayOk));
  setHop("hop-phone", "busy", esc(T.phoneBusy));
  say(T.phoneBusy);

  const ack = await phone.result;
  if (env !== activeEnv) return;
  if (!ack) {
    setHop("hop-phone", "fail", esc(T.phoneTimeout) + list([T.tipUpdate, T.tipLogin, T.tipBattery]));
  } else {
    const device = ack.device || T.yourPhone;
    const issues = (ack.issues || []).map((k) => T["issue_" + k]).filter(Boolean);
    if (issues.length) setHop("hop-phone", "warn", esc(fmt(T.phoneWarn, device)) + list(issues));
    else setHop("hop-phone", "ok", esc(fmt(T.phoneOk, device)));
    showLastTest({ ...ack, received_at: ack.received_at || new Date() });
  }
  return finish();

  function finish() {
    pendingPhone = null;
    running = false;
    renderButton();
    say(T.liveDone);
  }
}

function firebaseEnv(db, uid, hookId) {
  return {
    account: uid,
    async send(testId) {
      const r = await fetch(RELAY + hookId, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ divalarm_test: testId, title: T.testTitle }),
      });
      return { status: r.status, reason: r.headers.get("X-Dropped-Reason"), retryAfter: Number(r.headers.get("Retry-After")) };
    },
    waitForPhone(testId, ms) {
      let unsub = () => {}, timer, done;
      const result = new Promise((resolve) => {
        done = (v) => { unsub(); clearTimeout(timer); resolve(v); };
        timer = setTimeout(() => done(null), ms);
        unsub = onSnapshot(doc(db, "users", uid, "userstate", "webhook_test"), (snap) => {
          const d = snap.data();
          if (d && d.test_id === testId && !snap.metadata.hasPendingWrites) done(d);
        }, () => {});
      });
      return { result, cancel: () => done(null) };
    },
  };
}

// ---------- local preview (localhost only): ?demo=ok|warn|timeout|stopped|offline|signin|nohook ----------
const params = new URLSearchParams(location.search);
const demo = /^(localhost|127\.0\.0\.1)$/.test(location.hostname) ? params.get("demo") : null;

if (demo) {
  if (demo === "signin" || demo === "nohook") { show(demo); }
  else {
    $("who").hidden = false; $("who-email").textContent = "trader@example.com";
    setHookUrl(RELAY + "AbCdEfGhIj0123456789");
    show("ready");
    const wait = (ms) => new Promise((r) => setTimeout(r, ms));
    const env = {
      account: "preview-" + demo,
      async send() {
        await wait(500);
        if (demo === "offline") throw new TypeError("Failed to fetch");
        return demo === "stopped" ? { status: 204, reason: null } : { status: 200 };
      },
      waitForPhone() {
        const result = (async () => {
          await wait(1400);
          if (demo === "timeout") return null;
          return { device: "samsung SM-S926N", issues: demo === "warn" ? ["source_phone"] : [], received_at: new Date() };
        })();
        return { result, cancel() {} };
      },
    };
    setEnvironment(env);
    if (params.has("auto")) runTest(env);
  }
} else {
  const app = getApps().length ? getApp() : initializeApp({
    apiKey: "AIzaSyDB0uVFhbk3_2uEoCt8iz0LhE_2OOK_adQ",
    authDomain: "divergence-alarm.firebaseapp.com",
    projectId: "divergence-alarm",
    storageBucket: "divergence-alarm.firebasestorage.app",
    messagingSenderId: "912910128238",
    appId: "1:912910128238:web:a42ca6881960fcde76427f",
    measurementId: "G-NGCZKMQF67",
  });
  const auth = getAuth(app);
  const db = getFirestore(app);

  // App -> web sign-in: the app opens this page with #ct=<custom token>.
  const hash = new URLSearchParams(location.hash.slice(1));
  const ct = hash.get("ct");
  if (ct) {
    history.replaceState(null, "", location.pathname + location.search);
    signInWithCustomToken(auth, ct).catch((e) => console.error("App sign-in failed", e));
  }

  $("google-signin").addEventListener("click", async () => {
    try { await signInWithPopup(auth, new GoogleAuthProvider()); }
    catch (e) { if (e.code !== "auth/popup-closed-by-user") alert(fmt(T.signinFailed, e.message)); }
  });
  $("sign-out").addEventListener("click", () => signOut(auth));

  let authRevision = 0;

  onAuthStateChanged(auth, async (user) => {
    const revision = ++authRevision;
    setEnvironment(null);
    $("hook-url").replaceChildren(urlPlaceholder);
    document.querySelector('[data-copy="hook-url"]').disabled = true;
    $("last-test").hidden = true;
    for (const [id, detail] of initialHopDetails) setHop(id, "idle", detail);
    $("who").hidden = !user;
    show("signin");
    if (!user) return;
    $("who-email").textContent = user.email || "";
    const snap = await getDoc(doc(db, "users", user.uid)).catch(() => null);
    if (revision !== authRevision) return;
    const hookId = snap && snap.exists() ? String(snap.data().hookid || "") : "";
    if (!hookId) { show("nohook"); return; }
    setHookUrl(RELAY + hookId);
    setEnvironment(firebaseEnv(db, user.uid, hookId));
    show("ready");
    getDoc(doc(db, "users", user.uid, "userstate", "webhook_test"))
      .then((s) => revision === authRevision && s.exists() && showLastTest(s.data()))
      .catch(() => {});
  });
}
