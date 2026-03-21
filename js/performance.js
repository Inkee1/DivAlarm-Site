(() => {
  const DEFAULT_MANIFEST_URLS = [
    "../data/performance/btcusdt/manifest.json",
    "https://cdn.jsdelivr.net/gh/Inkee1/DivAlarm-Site@main/data/performance/btcusdt/manifest.json",
  ];

  const state = {
    manifest: null,
    weeks: [],
    currentIndex: 0,
  };

  const elements = {};

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

  function formatUtcDate(value, options = {}) {
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
      ...options,
    }).format(date);
  }

  function formatUtcDateTime(value) {
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
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
      timeZone: "UTC",
    }).format(date);
  }

  function monthLabel(year, month) {
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "long",
      timeZone: "UTC",
    }).format(new Date(Date.UTC(year, month - 1, 1)));
  }

  function resolveManifestCandidates() {
    const configured = window.DIVALARM_PERFORMANCE_MANIFEST_URLS;
    if (Array.isArray(configured) && configured.length > 0) {
      return configured;
    }
    return DEFAULT_MANIFEST_URLS;
  }

  async function loadManifest() {
    const candidates = resolveManifestCandidates();
    let lastError = new Error("No manifest sources configured");

    for (const candidate of candidates) {
      try {
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
          manifestUrl,
          manifestBaseUrl: new URL("./", manifestUrl),
        };
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
      }
    }

    throw lastError;
  }

  function showStatus(message, tone = "info") {
    if (!elements.status) {
      return;
    }
    elements.status.textContent = message;
    elements.status.dataset.tone = tone;
    elements.status.hidden = !message;
  }

  function createListHtml(items, emptyLabel) {
    if (!Array.isArray(items) || items.length === 0) {
      return `<span class="performance-muted">${escapeHtml(emptyLabel)}</span>`;
    }
    return items
      .map((item) => `<span class="performance-pill">${escapeHtml(item)}</span>`)
      .join("");
  }

  function createMoveMarkup(move) {
    if (move.same_as_range) {
      return `
        <article class="performance-move-card performance-move-card-muted">
          <div class="performance-move-head">
            <span class="performance-rank">#${escapeHtml(move.rank)}</span>
            <strong>Same as 7D range</strong>
            <span class="performance-move-change">${escapeHtml(formatPct(move.x10_pct))} x10</span>
          </div>
        </article>
      `;
    }

    const start = move.start || {};
    const end = move.end || {};
    return `
      <article class="performance-move-card">
        <div class="performance-move-head">
          <span class="performance-rank">#${escapeHtml(move.rank)}</span>
          <strong>${escapeHtml(move.direction)}</strong>
          <span class="performance-move-change">${escapeHtml(formatPct(move.x10_pct))} x10</span>
        </div>
        <div class="performance-move-body">
          <div class="performance-move-points">
            <div class="performance-move-point">
              <span class="performance-move-point-label">Start</span>
              <strong>${escapeHtml((start.kind || "").toUpperCase())}</strong>
              <span>${escapeHtml(typeof start.price === "number" ? start.price.toLocaleString("en-US") : "N/A")}</span>
              <span class="performance-muted">${escapeHtml(formatUtcDateTime(start.time_utc))}${start.time_utc ? " UTC" : ""}</span>
            </div>
            <div class="performance-move-point">
              <span class="performance-move-point-label">End</span>
              <strong>${escapeHtml((end.kind || "").toUpperCase())}</strong>
              <span>${escapeHtml(typeof end.price === "number" ? end.price.toLocaleString("en-US") : "N/A")}</span>
              <span class="performance-muted">${escapeHtml(formatUtcDateTime(end.time_utc))}${end.time_utc ? " UTC" : ""}</span>
            </div>
          </div>
          <div class="performance-mini-section">
            <div>
              <span class="performance-mini-label">Move</span>
              <strong>${escapeHtml(formatPct(move.change_pct))}</strong>
            </div>
            <div>
              <span class="performance-mini-label">x10</span>
              <strong>${escapeHtml(formatPct(move.x10_pct))}</strong>
            </div>
          </div>
          <div class="performance-div-grid">
            <div>
              <span class="performance-mini-label">A divergence</span>
              <div class="performance-pill-list">${createListHtml(move.a_divergences, "No A divergence")}</div>
            </div>
            <div>
              <span class="performance-mini-label">B divergence</span>
              <div class="performance-pill-list">${createListHtml(move.b_divergences, "No B divergence")}</div>
            </div>
          </div>
        </div>
      </article>
    `;
  }

  function resolveImageUrl(week) {
    return new URL(week.image, state.manifest.manifestBaseUrl).toString();
  }

  function renderCards() {
    elements.track.innerHTML = "";
    state.weeks.forEach((week, index) => {
      const active = index === state.currentIndex;
      const card = document.createElement("article");
      card.className = `performance-card${active ? " is-active" : ""}`;
      card.dataset.weekId = week.id;
      card.innerHTML = `
        <div class="performance-card-header">
          <div>
            <p class="performance-eyebrow">${escapeHtml(week.symbol)} weekly archive</p>
            <h2>Week ending ${escapeHtml(formatUtcDate(week.week_end_utc))} UTC</h2>
            <p class="performance-headline">${escapeHtml(week.headline || "Weekly performance")}</p>
          </div>
          <div class="performance-card-badges">
            <span class="performance-badge performance-badge-primary">Updated ${escapeHtml(formatUtcDate(week.published_at))}</span>
            <span class="performance-badge">${escapeHtml(monthLabel(week.year, week.month))}</span>
          </div>
        </div>
        <div class="performance-card-body">
          <div class="performance-chart-panel">
            <img alt="${escapeHtml(week.image_alt || `${week.symbol} performance chart`)}" loading="lazy" src="${escapeHtml(resolveImageUrl(week))}"/>
          </div>
          <div class="performance-details-panel">
            <div class="performance-stat-grid">
              <article class="performance-stat-card performance-stat-card-accent">
                <span class="performance-mini-label">7D Range</span>
                <strong>${escapeHtml(formatPct(week.range.change_pct))}</strong>
                <span class="performance-muted">x10 ${escapeHtml(formatPct(week.range.x10_pct))}</span>
              </article>
              <article class="performance-stat-card">
                <span class="performance-mini-label">Low</span>
                <strong>${escapeHtml(typeof week.range.low === "number" ? week.range.low.toLocaleString("en-US") : "N/A")}</strong>
                <span class="performance-muted">${escapeHtml(formatUtcDateTime(week.range.low_time_utc))}${week.range.low_time_utc ? " UTC" : ""}</span>
              </article>
              <article class="performance-stat-card">
                <span class="performance-mini-label">High</span>
                <strong>${escapeHtml(typeof week.range.high === "number" ? week.range.high.toLocaleString("en-US") : "N/A")}</strong>
                <span class="performance-muted">${escapeHtml(formatUtcDateTime(week.range.high_time_utc))}${week.range.high_time_utc ? " UTC" : ""}</span>
              </article>
            </div>
            <div class="performance-div-grid performance-div-grid-range">
              <div>
                <span class="performance-mini-label">Bullish divergence on low</span>
                <div class="performance-pill-list">${createListHtml(week.range_divergences.bullish, "No bullish divergence")}</div>
              </div>
              <div>
                <span class="performance-mini-label">Bearish divergence on high</span>
                <div class="performance-pill-list">${createListHtml(week.range_divergences.bearish, "No bearish divergence")}</div>
              </div>
            </div>
            <div class="performance-section">
              <div class="performance-section-head">
                <h3>Top moves</h3>
                <span>${escapeHtml(String(week.top_moves.length))} entries</span>
              </div>
              <div class="performance-move-list">
                ${week.top_moves.length ? week.top_moves.map(createMoveMarkup).join("") : '<p class="performance-empty">No move entries for this week.</p>'}
              </div>
            </div>
            <details class="performance-raw-summary">
              <summary>Raw summary</summary>
              <pre>${escapeHtml(week.raw_summary || "")}</pre>
            </details>
          </div>
        </div>
      `;
      elements.track.appendChild(card);
    });
  }

  function updateButtons() {
    elements.prev.disabled = state.currentIndex <= 0;
    elements.next.disabled = state.currentIndex >= state.weeks.length - 1;
  }

  function updateTrackPosition() {
    const cards = Array.from(elements.track.children);
    cards.forEach((card, index) => {
      card.classList.toggle("is-active", index === state.currentIndex);
      card.classList.toggle("is-neighbour", Math.abs(index - state.currentIndex) === 1);
    });

    const activeCard = cards[state.currentIndex];
    if (!activeCard) {
      return;
    }

    const centerOffset =
      activeCard.offsetLeft - Math.max(0, (elements.carouselWindow.clientWidth - activeCard.clientWidth) / 2);
    elements.track.style.transform = `translateX(${-centerOffset}px)`;
    updateButtons();
  }

  function yearOptions() {
    return Array.from(new Set(state.weeks.map((week) => week.year))).sort((a, b) => b - a);
  }

  function monthOptions(year) {
    return Array.from(new Set(state.weeks.filter((week) => week.year === year).map((week) => week.month))).sort((a, b) => b - a);
  }

  function weekOptions(year, month) {
    return state.weeks
      .filter((week) => week.year === year && week.month === month)
      .sort((a, b) => Date.parse(b.week_end_utc) - Date.parse(a.week_end_utc));
  }

  function syncSelectorsFromCurrentWeek() {
    const currentWeek = state.weeks[state.currentIndex];
    if (!currentWeek) {
      return;
    }

    const years = yearOptions();
    elements.year.innerHTML = years
      .map((year) => `<option value="${escapeHtml(year)}"${year === currentWeek.year ? " selected" : ""}>${escapeHtml(year)}</option>`)
      .join("");

    const months = monthOptions(currentWeek.year);
    elements.month.innerHTML = months
      .map(
        (month) =>
          `<option value="${escapeHtml(month)}"${month === currentWeek.month ? " selected" : ""}>${escapeHtml(monthLabel(currentWeek.year, month))}</option>`
      )
      .join("");

    const monthWeeks = weekOptions(currentWeek.year, currentWeek.month);
    elements.update.innerHTML = monthWeeks
      .map((week) => {
        const label = `${formatUtcDate(week.week_end_utc)} | ${formatPct(week.range.x10_pct)} x10`;
        return `<option value="${escapeHtml(week.id)}"${week.id === currentWeek.id ? " selected" : ""}>${escapeHtml(label)}</option>`;
      })
      .join("");

    const latestInMonth = monthWeeks[0];
    elements.monthUpdated.textContent = latestInMonth
      ? `Latest in month: ${formatUtcDate(latestInMonth.week_end_utc)} UTC`
      : "Latest in month: N/A";
    elements.jumpHint.textContent = `Jumping from ${formatUtcDate(currentWeek.week_end_utc)} UTC, then browse older/newer weeks with arrows.`;
  }

  function setCurrentIndex(index) {
    if (index < 0 || index >= state.weeks.length) {
      return;
    }
    state.currentIndex = index;
    syncSelectorsFromCurrentWeek();
    updateTrackPosition();
  }

  function jumpToWeekById(weekId) {
    const index = state.weeks.findIndex((week) => week.id === weekId);
    if (index >= 0) {
      setCurrentIndex(index);
    }
  }

  function handleYearChange() {
    const selectedYear = Number(elements.year.value);
    const months = monthOptions(selectedYear);
    if (months.length === 0) {
      return;
    }
    const latestMonth = months[0];
    const latestWeek = weekOptions(selectedYear, latestMonth)[0];
    if (latestWeek) {
      jumpToWeekById(latestWeek.id);
    }
  }

  function handleMonthChange() {
    const selectedYear = Number(elements.year.value);
    const selectedMonth = Number(elements.month.value);
    const firstWeek = weekOptions(selectedYear, selectedMonth)[0];
    if (firstWeek) {
      jumpToWeekById(firstWeek.id);
    }
  }

  function bindEvents() {
    elements.prev.addEventListener("click", () => setCurrentIndex(state.currentIndex - 1));
    elements.next.addEventListener("click", () => setCurrentIndex(state.currentIndex + 1));
    elements.year.addEventListener("change", handleYearChange);
    elements.month.addEventListener("change", handleMonthChange);
    elements.update.addEventListener("change", () => jumpToWeekById(elements.update.value));
    window.addEventListener("resize", () => window.requestAnimationFrame(updateTrackPosition));
  }

  function collectElements() {
    elements.status = document.getElementById("performance-status");
    elements.year = document.getElementById("performance-year");
    elements.month = document.getElementById("performance-month");
    elements.update = document.getElementById("performance-update");
    elements.monthUpdated = document.getElementById("performance-month-updated");
    elements.jumpHint = document.getElementById("performance-jump-hint");
    elements.prev = document.getElementById("performance-prev");
    elements.next = document.getElementById("performance-next");
    elements.carouselWindow = document.getElementById("performance-carousel-window");
    elements.track = document.getElementById("performance-carousel-track");
  }

  async function init() {
    collectElements();
    if (!elements.track) {
      return;
    }

    showStatus("Loading weekly performance history…");

    try {
      const manifest = await loadManifest();
      const weeks = Array.isArray(manifest.payload?.weeks) ? manifest.payload.weeks.slice() : [];
      weeks.sort((a, b) => Date.parse(a.week_end_utc) - Date.parse(b.week_end_utc));
      if (weeks.length === 0) {
        throw new Error("Manifest contains no week records.");
      }

      state.manifest = manifest;
      state.weeks = weeks;
      state.currentIndex = weeks.length - 1;

      renderCards();
      bindEvents();
      setCurrentIndex(state.currentIndex);
      showStatus(
        `Loaded ${weeks.length} weekly performance snapshots. Source: ${manifest.manifestUrl.hostname}`,
        "success"
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      showStatus(`Could not load performance data. ${message}`, "error");
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
