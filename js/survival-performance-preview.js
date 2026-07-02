(() => {
  const DEFAULT_MANIFEST_JSON_URLS = [
    "../data/performance/btcusdt/manifest.json",
    "https://cdn.jsdelivr.net/gh/Inkee1/DivAlarm-Site@main/data/performance/btcusdt/manifest.json",
  ];
  const DEFAULT_MANIFEST_SCRIPT_URLS = [
    "../data/performance/btcusdt/manifest.js",
    "https://cdn.jsdelivr.net/gh/Inkee1/DivAlarm-Site@main/data/performance/btcusdt/manifest.js",
  ];

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function formatPct(value) {
    if (typeof value !== "number" || Number.isNaN(value)) {
      return "N/A";
    }
    return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
  }

  function formatUtcDate(value) {
    if (!value) {
      return "N/A";
    }
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      timeZone: "UTC",
    }).format(date);
  }

  function resolveManifestCandidates(kind) {
    const configured =
      kind === "script"
        ? window.DIVALARM_PERFORMANCE_MANIFEST_SCRIPT_URLS
        : window.DIVALARM_PERFORMANCE_MANIFEST_URLS;
    if (Array.isArray(configured) && configured.length > 0) {
      return configured;
    }
    return kind === "script" ? DEFAULT_MANIFEST_SCRIPT_URLS : DEFAULT_MANIFEST_JSON_URLS;
  }

  async function loadManifestViaFetch(candidate) {
    const requestUrl = new URL(candidate, window.location.href);
    requestUrl.searchParams.set("ts", String(Date.now()));
    const response = await fetch(requestUrl.toString(), { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const payload = await response.json();
    const manifestUrl = new URL(candidate, window.location.href);
    return {
      payload,
      manifestBaseUrl: new URL("./", manifestUrl),
    };
  }

  async function loadManifestViaScript(candidate) {
    const scriptUrl = new URL(candidate, window.location.href);
    scriptUrl.searchParams.set("ts", String(Date.now()));
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = scriptUrl.toString();
      script.async = true;
      script.onload = () => {
        const payload = window.DIVALARM_PERFORMANCE_MANIFEST;
        if (!payload) {
          reject(new Error("Manifest script loaded but no manifest payload was found."));
          return;
        }
        resolve({
          payload,
          manifestBaseUrl: new URL("./", scriptUrl),
        });
      };
      script.onerror = () => reject(new Error(`Could not load ${scriptUrl}`));
      document.head.appendChild(script);
    });
  }

  async function loadManifest() {
    const strategies = window.location.protocol === "file:" ? ["script", "json"] : ["json", "script"];
    let lastError = new Error("No manifest sources configured");

    for (const strategy of strategies) {
      const candidates = resolveManifestCandidates(strategy);
      for (const candidate of candidates) {
        try {
          if (strategy === "script") {
            return await loadManifestViaScript(candidate);
          }
          return await loadManifestViaFetch(candidate);
        } catch (error) {
          lastError = error instanceof Error ? error : new Error(String(error));
        }
      }
    }

    throw lastError;
  }

  function createCardMarkup(week, manifestBaseUrl) {
    const imageUrl = new URL(week.image, manifestBaseUrl).toString();
    const x10 = formatPct(week.range?.x10_pct);
    const base = formatPct(week.range?.change_pct);
    const weekLabel = formatUtcDate(week.week_end_utc);

    return `
      <article class="survival-weekly-card">
        <div class="survival-weekly-chart">
          <img alt="${escapeHtml(week.image_alt || `${week.symbol} weekly chart`)}" loading="lazy" src="${escapeHtml(imageUrl)}"/>
        </div>
        <div class="survival-weekly-meta">
          <span class="survival-weekly-date">${escapeHtml(weekLabel)}</span>
          <span class="survival-weekly-returns">
            <strong class="survival-weekly-x10">${escapeHtml(x10)} <span class="survival-weekly-x10-tag">x10</span></strong>
            <span class="survival-weekly-base">${escapeHtml(base)}</span>
          </span>
        </div>
      </article>
    `;
  }

  async function init() {
    const root = document.getElementById("survival-weekly-performance");
    if (!root) {
      return;
    }

    const track = root.querySelector(".survival-weekly-track");
    const status = root.querySelector(".survival-weekly-status");
    if (!track) {
      return;
    }

    const loadingText = root.dataset.loadingText || "Loading…";
    const errorText = root.dataset.errorText || "Could not load performance data.";
    const emptyText = root.dataset.emptyText || "No weekly data yet.";

    if (status) {
      status.textContent = loadingText;
      status.hidden = false;
    }

    try {
      const manifest = await loadManifest();
      const weeks = Array.isArray(manifest.payload?.weeks) ? manifest.payload.weeks.slice() : [];
      weeks.sort((a, b) => Date.parse(a.week_end_utc) - Date.parse(b.week_end_utc));

      if (weeks.length === 0) {
        track.innerHTML = `<p class="survival-weekly-empty">${escapeHtml(emptyText)}</p>`;
        if (status) {
          status.hidden = true;
        }
        return;
      }

      track.innerHTML = weeks.map((week) => createCardMarkup(week, manifest.manifestBaseUrl)).join("");
      if (status) {
        status.hidden = true;
      }

      requestAnimationFrame(() => {
        const viewport = root.querySelector(".survival-weekly-viewport");
        if (viewport) {
          viewport.scrollLeft = viewport.scrollWidth;
        }
      });
    } catch (error) {
      track.innerHTML = "";
      if (status) {
        const message = error instanceof Error ? error.message : String(error);
        status.textContent = `${errorText} ${message}`;
        status.dataset.tone = "error";
        status.hidden = false;
      }
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
