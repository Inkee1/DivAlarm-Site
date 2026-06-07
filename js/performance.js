(() => {
  const DEFAULT_MANIFEST_JSON_URLS = [
    "../data/performance/btcusdt/manifest.json",
    "https://cdn.jsdelivr.net/gh/Inkee1/DivAlarm-Site@main/data/performance/btcusdt/manifest.json",
  ];
  const DEFAULT_MANIFEST_SCRIPT_URLS = [
    "../data/performance/btcusdt/manifest.js",
    "https://cdn.jsdelivr.net/gh/Inkee1/DivAlarm-Site@main/data/performance/btcusdt/manifest.js",
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

  function divergenceLabelForKind(kind) {
    const normalized = String(kind || "").toLowerCase();
    if (normalized === "low") {
      return "Bullish divergence";
    }
    if (normalized === "high") {
      return "Bearish divergence";
    }
    return "Divergence";
  }

  function emptyDivergenceLabelForKind(kind) {
    const normalized = String(kind || "").toLowerCase();
    if (normalized === "low") {
      return "No bullish divergence";
    }
    if (normalized === "high") {
      return "No bearish divergence";
    }
    return "No divergence";
  }

  function monthLabel(year, month) {
    return new Intl.DateTimeFormat("en-US", {
      year: "numeric",
      month: "long",
      timeZone: "UTC",
    }).format(new Date(Date.UTC(year, month - 1, 1)));
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
      manifestUrl,
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
          manifestUrl: scriptUrl,
          manifestBaseUrl: new URL("./", scriptUrl),
        });
      };
      script.onerror = () => reject(new Error(`Could not load ${scriptUrl}`));
      document.head.appendChild(script);
    });
  }

  function describeManifestSource(manifestUrl) {
    if (!manifestUrl) {
      return "unknown";
    }
    if (manifestUrl.protocol === "file:") {
      return "local files";
    }
    return manifestUrl.hostname || manifestUrl.href;
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

  function showStatus(message, tone = "info") {
    if (!elements.status) {
      return;
    }
    elements.status.textContent = message;
    elements.status.dataset.tone = tone;
    elements.status.hidden = !message;
  }

  window.openLightbox = function(imgSrc) {
    let overlay = document.getElementById("img-lightbox");
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.id = "img-lightbox";
      overlay.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(0,0,0,0.95); z-index: 99999;
        display: flex; align-items: center; justify-content: center;
        overflow: auto;
      `;
      overlay.innerHTML = `
        <div style="position: absolute; top: 15px; right: 20px; color: white; font-size: 35px; cursor: pointer; z-index: 100000;" id="lightbox-close">&times;</div>
        <img id="lightbox-img" src="" style="margin: auto; display: block; max-width: 100%; max-height: 100%; transition: transform 0.25s;" />
      `;
      document.body.appendChild(overlay);

      overlay.addEventListener("click", (e) => {
        if (e.target.id === "img-lightbox" || e.target.id === "lightbox-close") {
          overlay.style.display = "none";
          document.body.style.overflow = "";
        }
      });

      const img = overlay.querySelector("#lightbox-img");
      let scale = 1;
      img.addEventListener("click", (e) => {
        e.stopPropagation();
        scale = scale === 1 ? 2.5 : 1;
        img.style.transform = `scale(${scale})`;
        img.style.cursor = scale === 1 ? "zoom-out" : "zoom-in";
        if(scale > 1) {
            img.style.transformOrigin = `${e.offsetX}px ${e.offsetY}px`;
            overlay.style.alignItems = "flex-start";
            overlay.style.justifyContent = "flex-start";
        } else {
            overlay.style.alignItems = "center";
            overlay.style.justifyContent = "center";
        }
      });
    }

    const img = overlay.querySelector("#lightbox-img");
    img.src = imgSrc;
    img.style.transform = "scale(1)";
    img.style.cursor = "zoom-in";
    overlay.style.alignItems = "center";
    overlay.style.justifyContent = "center";
    overlay.style.display = "flex";
    document.body.style.overflow = "hidden";
  };

  function createListHtml(items, emptyLabel) {
    if (!Array.isArray(items) || items.length === 0) {
      return `<span class="performance-muted">${escapeHtml(emptyLabel)}</span>`;
    }
    return items
      .map((item) => `<span class="performance-pill">${escapeHtml(item)}</span>`)
      .join("");
  }

  function createMoveMarkup(move, options = {}) {
    const showDivergences = options.showDivergences !== false;
    if (move.same_as_range) {
      return `
        <article class="performance-move-card performance-move-card-muted">
          <div class="performance-move-head">
            <span class="performance-rank">#${escapeHtml(move.rank)}</span>
            <strong>Same as 7D range</strong>
            <span class="performance-move-change performance-move-change-highlight">${escapeHtml(formatPct(move.x10_pct))} x10</span>
          </div>
        </article>
      `;
    }

    const start = move.start || {};
    const end = move.end || {};
    const startDivergenceLabel = divergenceLabelForKind(start.kind);
    const endDivergenceLabel = divergenceLabelForKind(end.kind);
    const divergenceMarkup = showDivergences
      ? `
          <div class="performance-div-grid">
            <div>
              <span class="performance-mini-label">${escapeHtml(startDivergenceLabel)}</span>
              <div class="performance-pill-list">${createListHtml(move.a_divergences, emptyDivergenceLabelForKind(start.kind))}</div>
            </div>
            <div>
              <span class="performance-mini-label">${escapeHtml(endDivergenceLabel)}</span>
              <div class="performance-pill-list">${createListHtml(move.b_divergences, emptyDivergenceLabelForKind(end.kind))}</div>
            </div>
          </div>
        `
      : "";
    return `
      <article class="performance-move-card">
        <div class="performance-move-head">
          <span class="performance-rank">#${escapeHtml(move.rank)}</span>
          <strong>${escapeHtml(move.direction)}</strong>
          <span class="performance-move-change performance-move-change-highlight">${escapeHtml(formatPct(move.x10_pct))} x10</span>
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
          ${divergenceMarkup}
        </div>
      </article>
    `;
  }

  function resolveAssetUrl(assetPath) {
    return new URL(assetPath, state.manifest.manifestBaseUrl).toString();
  }

  function createTrailingWindowMarkup(trailing) {
    if (!trailing || !trailing.image) {
      return "";
    }

    const topMoves = Array.isArray(trailing.top_moves) ? trailing.top_moves : [];
    const range = trailing.range || {};
    const showDivergences = trailing.divergence_status !== "unavailable";
    const bestX10Value =
      typeof range.x10_pct === "number"
        ? range.x10_pct
        : topMoves.length > 0 && typeof topMoves[0]?.x10_pct === "number"
          ? topMoves[0].x10_pct
          : null;
    const rangeCaption = `${formatUtcDate(trailing.window_start_utc)} - ${formatUtcDate(trailing.window_end_utc)} UTC`;

    return `
      <section class="performance-trailing-window">
        <div class="performance-card-header performance-trailing-header">
          <div>
            <p class="performance-eyebrow">Trailing 30-day archive</p>
            <h2>Previous 30 Days Best</h2>
            <p class="performance-headline">${escapeHtml(rangeCaption)} · ${escapeHtml(String(trailing.interval || "12H"))} candles</p>
          </div>
          <div class="performance-card-badges">
            <span class="performance-badge performance-badge-primary">${escapeHtml(trailing.headline || "Previous 30 days best")}</span>
            <span class="performance-badge">Window ${escapeHtml(String(trailing.window_days || 30))}D</span>
          </div>
        </div>
        <div class="performance-card-body performance-card-body-subsection performance-trailing-grid">
          <div class="performance-trailing-visual">
            <div class="performance-chart-panel performance-chart-panel-secondary">
              <div class="performance-mobile-arrows">
                <button class="performance-overlay-arrow left-arrow" aria-label="Previous week">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"></polyline></svg>
                </button>
                <button class="performance-overlay-arrow right-arrow" aria-label="Next week">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
                </button>
              </div>
              <img alt="${escapeHtml(trailing.image_alt || "Previous 30 days best chart")}" loading="lazy" src="${escapeHtml(resolveAssetUrl(trailing.image))}" style="cursor: pointer;" onclick="window.openLightbox && window.openLightbox(this.src)"/>
            </div>
            <p class="performance-trailing-hint">Tap the chart to zoom in.</p>
          </div>
          <div class="performance-details-panel performance-trailing-details">
            <div class="performance-stat-grid">
              <article class="performance-stat-card performance-stat-card-accent performance-hero-stat">
                <div class="performance-hero-stat-left">
                  <span class="performance-mini-label performance-hero-label">Best x10 Return</span>
                  <div class="performance-x10-highlight">${escapeHtml(formatPct(bestX10Value))}</div>
                </div>
                <div class="performance-hero-stat-right">
                  <span class="performance-mini-label">Base Move</span>
                  <div class="performance-base-move">${escapeHtml(formatPct(range.change_pct))}</div>
                </div>
              </article>
              <div class="performance-stat-grid-duo">
                <article class="performance-stat-card">
                  <span class="performance-mini-label">Low</span>
                  <strong>${escapeHtml(typeof range.low === "number" ? range.low.toLocaleString("en-US") : "N/A")}</strong>
                  <span class="performance-muted">${escapeHtml(formatUtcDateTime(range.low_time_utc))}${range.low_time_utc ? " UTC" : ""}</span>
                </article>
                <article class="performance-stat-card">
                  <span class="performance-mini-label">High</span>
                  <strong>${escapeHtml(typeof range.high === "number" ? range.high.toLocaleString("en-US") : "N/A")}</strong>
                  <span class="performance-muted">${escapeHtml(formatUtcDateTime(range.high_time_utc))}${range.high_time_utc ? " UTC" : ""}</span>
                </article>
              </div>
            </div>
            ${
              showDivergences
                ? `
                  <div class="performance-div-grid performance-div-grid-range">
                    <div>
                      <span class="performance-mini-label">Bullish divergence on low</span>
                      <div class="performance-pill-list">${createListHtml(trailing.range_divergences?.bullish, "No bullish divergence")}</div>
                    </div>
                    <div>
                      <span class="performance-mini-label">Bearish divergence on high</span>
                      <div class="performance-pill-list">${createListHtml(trailing.range_divergences?.bearish, "No bearish divergence")}</div>
                    </div>
                  </div>
                `
                : `<p class="performance-trailing-note">Historical divergence labels are not available for this 30-day view.</p>`
            }
            <div class="performance-section performance-section-nested">
              <div class="performance-section-head">
                <h3>Top 30D moves</h3>
                <span>${escapeHtml(String(topMoves.length))} entries</span>
              </div>
              <div class="performance-move-list">
                ${
                  topMoves.length
                    ? topMoves.map((move) => createMoveMarkup(move, { showDivergences })).join("")
                    : '<p class="performance-empty">No move entries for this 30-day window.</p>'
                }
              </div>
            </div>
          </div>
        </div>
      </section>
    `;
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
            <div class="performance-mobile-arrows">
              <button class="performance-overlay-arrow left-arrow" aria-label="Previous week">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"></polyline></svg>
              </button>
              <button class="performance-overlay-arrow right-arrow" aria-label="Next week">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
              </button>
            </div>
            <img alt="${escapeHtml(week.image_alt || `${week.symbol} performance chart`)}" loading="lazy" src="${escapeHtml(resolveAssetUrl(week.image))}" style="cursor: pointer;" onclick="window.openLightbox && window.openLightbox(this.src)"/>
          </div>
          <div class="performance-details-panel">
            <div class="performance-stat-grid">
              <article class="performance-stat-card performance-stat-card-accent performance-hero-stat">
                <div class="performance-hero-stat-left">
                  <span class="performance-mini-label performance-hero-label">x10 Leveraged Return</span>
                  <div class="performance-x10-highlight">${escapeHtml(formatPct(week.range.x10_pct))}</div>
                </div>
                <div class="performance-hero-stat-right">
                  <span class="performance-mini-label">Base Move</span>
                  <div class="performance-base-move">${escapeHtml(formatPct(week.range.change_pct))}</div>
                </div>
              </article>
              <div class="performance-controls-slot"></div>
              <div class="performance-stat-grid-duo">
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
          </div>
        </div>
        ${createTrailingWindowMarkup(week.trailing_30d)}
      `;
      elements.track.appendChild(card);
    });
  }

  function updateButtons() {
    if (elements.prev) elements.prev.disabled = state.currentIndex <= 0;
    if (elements.next) elements.next.disabled = state.currentIndex >= state.weeks.length - 1;

    const activeCard = elements.track.children[state.currentIndex];
    if (activeCard) {
      const leftBtns = activeCard.querySelectorAll('.left-arrow');
      const rightBtns = activeCard.querySelectorAll('.right-arrow');
      const isStart = state.currentIndex <= 0;
      const isEnd = state.currentIndex >= state.weeks.length - 1;

      leftBtns.forEach((leftBtn) => {
        leftBtn.disabled = isStart;
        leftBtn.style.opacity = isStart ? "0.4" : "1";
        leftBtn.style.cursor = isStart ? "not-allowed" : "pointer";
      });
      rightBtns.forEach((rightBtn) => {
        rightBtn.disabled = isEnd;
        rightBtn.style.opacity = isEnd ? "0.4" : "1";
        rightBtn.style.cursor = isEnd ? "not-allowed" : "pointer";
      });
    }
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

    const slot = activeCard.querySelector('.performance-controls-slot');
    if (elements.controls && slot) {
      slot.appendChild(elements.controls);
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

  let touchStartX = 0;
  let touchStartY = 0;

  function handleTouchStart(e) {
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
  }

  function handleTouchEnd(e) {
    if (!touchStartX || !touchStartY) return;
    const touchEndX = e.changedTouches[0].clientX;
    const touchEndY = e.changedTouches[0].clientY;
    const diffX = touchStartX - touchEndX;
    const diffY = touchStartY - touchEndY;

    if (Math.abs(diffX) > Math.abs(diffY)) {
      if (diffX > 40) {
        setCurrentIndex(state.currentIndex + 1);
      } else if (diffX < -40) {
        setCurrentIndex(state.currentIndex - 1);
      }
    }
    touchStartX = 0;
    touchStartY = 0;
  }

  function bindEvents() {
    if (elements.prev) elements.prev.addEventListener("click", () => setCurrentIndex(state.currentIndex - 1));
    if (elements.next) elements.next.addEventListener("click", () => setCurrentIndex(state.currentIndex + 1));
    elements.year.addEventListener("change", handleYearChange);
    elements.month.addEventListener("change", handleMonthChange);
    elements.update.addEventListener("change", () => jumpToWeekById(elements.update.value));
    
    // Swipe Mechanics
    elements.carouselWindow.addEventListener("touchstart", handleTouchStart, { passive: true });
    elements.carouselWindow.addEventListener("touchend", handleTouchEnd, { passive: true });
    
    // Overlay Arrow Mechanics
    elements.carouselWindow.addEventListener("click", (e) => {
      const btn = e.target.closest(".performance-overlay-arrow");
      if (btn && !btn.disabled) {
        if (btn.classList.contains("left-arrow")) setCurrentIndex(state.currentIndex - 1);
        else if (btn.classList.contains("right-arrow")) setCurrentIndex(state.currentIndex + 1);
      }
    });

    window.addEventListener("resize", () => window.requestAnimationFrame(updateTrackPosition));
  }

  function collectElements() {
    elements.status = document.getElementById("performance-status");
    elements.controls = document.querySelector(".performance-controls");
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

    showStatus("Loading performance history…");

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
      showStatus("");
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      showStatus(`Could not load performance data. ${message}`, "error");
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
