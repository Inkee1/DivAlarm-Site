/* DivAlarm Language Switcher
 * - Adds a mobile-friendly language switcher on every page
 * - Optionally auto-redirects based on ?lang=, saved localStorage, or navigator language
 *
 * Disable auto-redirect:
 *   - Append ?noredirect=1
 *   - Or set window.DIV_LANG_SWITCHER_DISABLE_AUTO_REDIRECT = true before this script runs
 */
(function () {
  "use strict";

  // ✅ “실제 폴더”로 존재시키려는 목록(폴더명과 동일)
  var SUPPORTED = [
    "en",
    "ko",
    "ru",
    "vi",
    "tr",
    "pt-br",
    "uk",
    "id",
    "ja",
    "de",
    "ur",
    "fil",
    "th",
    "ms",
    "zh-hans",
    "es",
  ];

  // ✅ 흔한/기기별 언어코드 차이를 폴더명으로 매핑 (alias)
  var ALIASES = {
    pt: "pt-br",
    "pt-pt": "pt-br",
    tl: "fil",
    zh: "zh-hans",
    "zh-cn": "zh-hans",
    "zh-sg": "zh-hans",
    "zh-hans-cn": "zh-hans",
    "zh-hans-sg": "zh-hans",
  };

  var LABELS = {
    en: "English",
    ko: "한국어",
    ru: "Русский",
    vi: "Tiếng Việt",
    tr: "Türkçe",
    "pt-br": "Português (Brasil)",
    uk: "Українська",
    id: "Bahasa Indonesia",
    ja: "日本語",
    de: "Deutsch",
    ur: "اردو",
    fil: "Filipino",
    th: "ไทย",
    ms: "Bahasa Melayu",
    "zh-hans": "中文(简体)",
    es: "Español",
  };

  var supportedSet = new Set(SUPPORTED);

  function safeGet(key) {
    try {
      return window.localStorage ? window.localStorage.getItem(key) : null;
    } catch (e) {
      return null;
    }
  }

  function safeSet(key, value) {
    try {
      if (!window.localStorage) return;
      window.localStorage.setItem(key, value);
    } catch (e) {
      // ignore
    }
  }

  function normalize(tag) {
    if (!tag) return "";
    return String(tag).toLowerCase().replace(/_/g, "-");
  }

  // full -> progressive truncate match: e.g. "pt-br-x" -> "pt-br" -> "pt"
  function resolve(tag) {
    var t = normalize(tag);
    if (!t) return "";

    if (ALIASES[t]) t = ALIASES[t];
    if (supportedSet.has(t)) return t;

    while (t.indexOf("-") !== -1) {
      t = t.substring(0, t.lastIndexOf("-"));
      if (ALIASES[t]) t = ALIASES[t];
      if (supportedSet.has(t)) return t;
    }

    if (ALIASES[t]) return ALIASES[t];
    return supportedSet.has(t) ? t : "";
  }

  function getNavigatorBest() {
    var list =
      window.navigator && window.navigator.languages && window.navigator.languages.length
        ? window.navigator.languages
        : [window.navigator && window.navigator.language ? window.navigator.language : "en"];

    for (var i = 0; i < list.length; i++) {
      var r = resolve(list[i]);
      if (r) return r;
    }
    return "en";
  }

  function getPathParts(pathname) {
    return String(pathname || "").split("/");
  }

  function findLangInParts(parts) {
    for (var i = 0; i < parts.length; i++) {
      if (supportedSet.has(parts[i])) return { lang: parts[i], index: i };
    }
    return { lang: "", index: -1 };
  }

  function getCurrentLang() {
    try {
      var url = new URL(window.location.href);
      var parts = getPathParts(url.pathname);
      var found = findLangInParts(parts);
      return found.lang || "";
    } catch (e) {
      return "";
    }
  }

  function buildUrlForLang(targetLang) {
    var l = resolve(targetLang) || "en";
    var url = new URL(window.location.href);
    var parts = getPathParts(url.pathname);
    var found = findLangInParts(parts);

    if (found.index >= 0) {
      var suffix = parts.slice(found.index + 1);
      var rel = suffix.join("/");
      if (!rel) rel = "index.html";
      else if (rel.endsWith("/")) rel = rel + "index.html";
      else {
        var last = suffix[suffix.length - 1] || "";
        // If the current page is accessed via a "pretty URL" like /ko/my-account,
        // GitHub Pages resolves it to my-account.html (not a directory). In that case,
        // switching languages must keep it as a file, not /index.html.
        if (last.indexOf(".") === -1) rel = rel + ".html";
      }

      var prefix = parts.slice(0, found.index);
      url.pathname = prefix.concat([l]).concat(rel.split("/")).join("/").replace(/\/{2,}/g, "/");
    } else {
      // No lang segment found; append /<lang>/<file> to the current directory
      var base = parts.slice();
      if (base.length > 1 && base[base.length - 1] === "") {
        base = base.slice(0, -1);
      }
      if (base.length && base[base.length - 1] && base[base.length - 1].indexOf(".") !== -1) {
        var file = base[base.length - 1];
        base = base.slice(0, -1);
        url.pathname = base.concat([l, file]).join("/").replace(/\/{2,}/g, "/");
      } else {
        url.pathname = base.concat([l, "index.html"]).join("/").replace(/\/{2,}/g, "/");
      }
    }

    // Keep any marketing params etc, but remove language control params
    url.searchParams.delete("lang");
    url.searchParams.delete("noredirect");
    return url.toString();
  }

  function isAutoRedirectDisabled() {
    try {
      var url = new URL(window.location.href);
      if (url.searchParams.get("noredirect") === "1") return true;
    } catch (e) {
      // ignore
    }
    return window.DIV_LANG_SWITCHER_DISABLE_AUTO_REDIRECT === true;
  }

  function maybeAutoRedirect() {
    if (isAutoRedirectDisabled()) return;

    var currentLang = getCurrentLang();
    if (!currentLang) return;

    var url = new URL(window.location.href);
    var qsLang = resolve(url.searchParams.get("lang"));
    if (qsLang) {
      safeSet("lang", qsLang);
      if (qsLang !== currentLang) {
        window.location.replace(buildUrlForLang(qsLang));
      }
      return;
    }

    var saved = resolve(safeGet("lang"));
    if (saved) {
      if (saved !== currentLang) {
        window.location.replace(buildUrlForLang(saved));
      }
      return;
    }

    var best = getNavigatorBest();
    if (best && best !== currentLang) {
      // Save so direct-entry pages don’t flip-flop across sessions
      safeSet("lang", best);
      window.location.replace(buildUrlForLang(best));
    }
  }

  // Try redirect as early as possible (still safe even if DOM isn't ready)
  try {
    maybeAutoRedirect();
  } catch (e) {
    // ignore
  }

  function createEl(tag, className, text) {
    var el = document.createElement(tag);
    if (className) el.className = className;
    if (typeof text === "string") el.textContent = text;
    return el;
  }

  function mountSwitcher() {
    var currentLang = getCurrentLang() || resolve(safeGet("lang")) || "en";

    // Root container
    var root = createEl("div", "div-lang-switcher");
    root.setAttribute("data-current-lang", currentLang);

    // Backdrop
    var backdrop = createEl("div", "div-lang-backdrop");
    backdrop.hidden = true;

    // Trigger button
    var trigger = createEl("button", "div-lang-trigger");
    trigger.type = "button";
    trigger.setAttribute("aria-haspopup", "dialog");
    trigger.setAttribute("aria-expanded", "false");
    trigger.setAttribute("aria-label", "Change language");
    trigger.innerHTML =
      '<span class="div-lang-icon" aria-hidden="true">🌐</span>' +
      '<span class="div-lang-code">' +
      String(currentLang).toUpperCase() +
      "</span>";

    // Panel
    var panel = createEl("div", "div-lang-panel");
    panel.hidden = true;
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-modal", "true");
    panel.setAttribute("aria-label", "Language selection");

    var header = createEl("div", "div-lang-header");
    var title = createEl("div", "div-lang-title", "Language");
    var closeBtn = createEl("button", "div-lang-close", "×");
    closeBtn.type = "button";
    closeBtn.setAttribute("aria-label", "Close");
    header.appendChild(title);
    header.appendChild(closeBtn);

    var list = createEl("div", "div-lang-list");
    SUPPORTED.forEach(function (code) {
      var item = createEl("button", "div-lang-item");
      item.type = "button";
      item.setAttribute("data-lang", code);
      item.setAttribute("aria-current", code === currentLang ? "true" : "false");
      item.innerHTML =
        '<span class="div-lang-name">' +
        (LABELS[code] || code) +
        '</span><span class="div-lang-tag">' +
        code +
        "</span>";
      item.addEventListener("click", function () {
        var target = resolve(code) || "en";
        safeSet("lang", target);
        window.location.href = buildUrlForLang(target);
      });
      list.appendChild(item);
    });

    panel.appendChild(header);
    panel.appendChild(list);

    function open() {
      panel.hidden = false;
      backdrop.hidden = false;
      trigger.setAttribute("aria-expanded", "true");
      root.classList.add("is-open");
      // Focus first item (current) if present
      var currentBtn = list.querySelector('[data-lang="' + currentLang + '"]');
      if (currentBtn) currentBtn.focus();
    }

    function close() {
      panel.hidden = true;
      backdrop.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
      root.classList.remove("is-open");
      trigger.focus();
    }

    function toggle() {
      if (panel.hidden) open();
      else close();
    }

    trigger.addEventListener("click", toggle);
    closeBtn.addEventListener("click", close);
    backdrop.addEventListener("click", close);

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !panel.hidden) close();
    });

    root.appendChild(trigger);
    root.appendChild(panel);
    document.body.appendChild(backdrop);
    document.body.appendChild(root);

    // Place the switcher at the top-right when the page has a top navigation
    // (Webflow) or when it's one of the standalone "manual-style" pages.
    // This keeps the switcher in a consistent spot across the site.
    var hasWebflowNav = !!document.querySelector(".navbar-wrapper-three");
    var hasManualLayout = !!document.querySelector(".manual-container");
    if (hasWebflowNav || hasManualLayout) {
      root.classList.add("is-top");
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountSwitcher);
  } else {
    mountSwitcher();
  }
})();


