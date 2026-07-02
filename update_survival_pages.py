import os
import re
import glob

css_to_inject = """
  .survival-weekly-performance {
    margin: 3rem 0 2.5rem;
    padding: 1.5rem 1.2rem 1.4rem;
    border-radius: 24px;
    border: 1px solid rgba(56, 189, 248, 0.3);
    background: linear-gradient(165deg, rgba(15, 23, 42, 0.95) 0%, rgba(2, 6, 23, 0.98) 100%);
    box-shadow: 0 20px 50px -15px rgba(0, 0, 0, 0.8), 0 0 25px rgba(56, 189, 248, 0.15) inset;
    position: relative;
    overflow: hidden;
  }
  .survival-weekly-performance::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.08) 0%, transparent 60%);
    pointer-events: none;
    animation: rotateGlow 15s linear infinite;
  }
  @keyframes rotateGlow {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  .survival-weekly-performance-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    margin-bottom: 1.2rem;
    position: relative;
    z-index: 2;
  }
  .survival-weekly-performance-title {
    margin: 0;
    font-size: clamp(1.2rem, 4vw, 1.4rem);
    font-weight: 900;
    color: #f8fafc;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .survival-weekly-performance-title::before {
    content: '🔥';
    font-size: 1.2em;
  }
  .survival-weekly-scroll-hint {
    flex-shrink: 0;
    font-size: 0.75rem;
    font-weight: 700;
    color: #38bdf8;
    background: rgba(56, 189, 248, 0.15);
    padding: 0.3rem 0.6rem;
    border-radius: 999px;
    white-space: nowrap;
    animation: pulseHint 2s infinite;
  }
  @keyframes pulseHint {
    0% { opacity: 0.7; }
    50% { opacity: 1; transform: translateX(3px); }
    100% { opacity: 0.7; }
  }
  .survival-weekly-viewport {
    height: clamp(190px, 28vh, 250px);
    overflow-x: auto;
    overflow-y: hidden;
    -webkit-overflow-scrolling: touch;
    scroll-snap-type: x mandatory;
    scrollbar-width: thin;
    scrollbar-color: rgba(56, 189, 248, 0.6) rgba(15, 23, 42, 0.5);
    position: relative;
    z-index: 2;
    padding-bottom: 0.5rem;
  }
  .survival-weekly-viewport::-webkit-scrollbar {
    height: 6px;
  }
  .survival-weekly-viewport::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.5);
    border-radius: 999px;
  }
  .survival-weekly-viewport::-webkit-scrollbar-thumb {
    background: rgba(56, 189, 248, 0.6);
    border-radius: 999px;
  }
  .survival-weekly-track {
    display: flex;
    gap: 1rem;
    height: 100%;
    width: max-content;
  }
  .survival-weekly-card {
    flex: 0 0 min(82vw, 320px);
    width: min(82vw, 320px);
    height: 100%;
    display: grid;
    grid-template-rows: 1fr auto;
    gap: 0;
    scroll-snap-align: center;
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    background: linear-gradient(180deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    box-shadow: 0 10px 20px -10px rgba(0,0,0,0.5);
  }
  .survival-weekly-card:hover {
    transform: translateY(-4px);
    border-color: rgba(56, 189, 248, 0.5);
    box-shadow: 0 15px 30px -10px rgba(0,0,0,0.7), 0 0 20px rgba(56, 189, 248, 0.2);
  }
  .survival-weekly-chart {
    min-height: 0;
    overflow: hidden;
    background: rgba(15, 23, 42, 0.8);
    position: relative;
  }
  .survival-weekly-chart::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(0deg, rgba(15,23,42,0.9) 0%, transparent 30%);
    pointer-events: none;
  }
  .survival-weekly-chart img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center top;
    transition: transform 0.5s ease;
  }
  .survival-weekly-card:hover .survival-weekly-chart img {
    transform: scale(1.05);
  }
  .survival-weekly-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    padding: 0.8rem 1rem;
    background: rgba(15, 23, 42, 0.95);
    border-top: 1px solid rgba(255,255,255,0.05);
  }
  .survival-weekly-date {
    font-size: 0.8rem;
    font-weight: 600;
    color: #cbd5e1;
    white-space: nowrap;
  }
  .survival-weekly-returns {
    display: inline-flex;
    align-items: baseline;
    gap: 0.4rem;
    white-space: nowrap;
  }
  .survival-weekly-x10 {
    font-size: 1.15rem;
    font-weight: 900;
    color: #4ade80;
    letter-spacing: -0.02em;
    text-shadow: 0 0 15px rgba(74, 222, 128, 0.4);
  }
  .survival-weekly-x10-tag {
    font-size: 0.75rem;
    font-weight: 800;
    color: #22c55e;
    opacity: 0.9;
    background: rgba(34, 197, 94, 0.15);
    padding: 0.15rem 0.4rem;
    border-radius: 6px;
    vertical-align: middle;
  }
  .survival-weekly-base {
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748b;
  }
  .survival-weekly-status,
  .survival-weekly-empty {
    margin: 0;
    padding: 1rem 0.2rem;
    font-size: 0.9rem;
    color: #94a3b8;
    text-align: center;
    position: relative;
    z-index: 2;
  }
  .survival-weekly-status[data-tone="error"] {
    color: #fca5a5;
  }
  .survival-weekly-more {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin: 1.5rem auto 0;
    padding: 0.9rem 2rem;
    border-radius: 999px;
    border: none;
    background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
    color: #ffffff;
    font-size: 1.05rem;
    font-weight: 800;
    text-decoration: none;
    box-shadow: 0 10px 25px -8px rgba(14, 165, 233, 0.6);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    z-index: 2;
  }
  .survival-weekly-more:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 15px 35px -10px rgba(14, 165, 233, 0.8);
    background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
  }
  .survival-weekly-more-wrap {
    text-align: center;
    position: relative;
    z-index: 2;
  }
"""

translations = {
    "en": {
        "title": "Best Weekly Performance",
        "empty": "No data for this week.",
        "error": "Failed to load performance data.",
        "loading": "Loading...",
        "more": "View More"
    },
    "es": {
        "title": "Mejor Rendimiento Semanal",
        "empty": "No hay datos para esta semana.",
        "error": "Error al cargar los datos de rendimiento.",
        "loading": "Cargando...",
        "more": "Ver Más"
    },
    "de": {
        "title": "Beste Wöchentliche Leistung",
        "empty": "Keine Daten für diese Woche.",
        "error": "Leistungsdaten konnten nicht geladen werden.",
        "loading": "Wird geladen...",
        "more": "Mehr Sehen"
    },
    "uk": {
        "title": "Найкращі Тижневі Результати",
        "empty": "Немає даних за цей тиждень.",
        "error": "Не вдалося завантажити дані про результати.",
        "loading": "Завантаження...",
        "more": "Детальніше"
    },
    "ur": {
        "title": "بہترین ہفتہ وار کارکردگی",
        "empty": "اس ہفتے کا کوئی ڈیٹا نہیں ہے۔",
        "error": "کارکردگی کا ڈیٹا لوڈ کرنے میں ناکام۔",
        "loading": "لوڈ ہو رہا ہے...",
        "more": "مزید دیکھیں"
    },
    "zh-hans": {
        "title": "最佳周表现",
        "empty": "本周无数据。",
        "error": "无法加载表现数据。",
        "loading": "加载中...",
        "more": "查看更多"
    },
    "pt-br": {
        "title": "Melhor Desempenho Semanal",
        "empty": "Sem dados para esta semana.",
        "error": "Falha ao carregar dados de desempenho.",
        "loading": "Carregando...",
        "more": "Ver Mais"
    },
    "ms": {
        "title": "Prestasi Mingguan Terbaik",
        "empty": "Tiada data untuk minggu ini.",
        "error": "Gagal memuatkan data prestasi.",
        "loading": "Sedang memuatkan...",
        "more": "Lihat Lagi"
    },
    "id": {
        "title": "Performa Mingguan Terbaik",
        "empty": "Tidak ada data untuk minggu ini.",
        "error": "Gagal memuat data performa.",
        "loading": "Memuat...",
        "more": "Lihat Lebih Banyak"
    },
    "tr": {
        "title": "En İyi Haftalık Performans",
        "empty": "Bu hafta için veri yok.",
        "error": "Performans verileri yüklenemedi.",
        "loading": "Yükleniyor...",
        "more": "Daha Fazla Gör"
    },
    "ja": {
        "title": "最高の週間パフォーマンス",
        "empty": "今週のデータはありません。",
        "error": "パフォーマンスデータの読み込みに失敗しました。",
        "loading": "読み込み中...",
        "more": "もっと見る"
    },
    "fil": {
        "title": "Pinakamahusay na Lingguhang Pagganap",
        "empty": "Walang data para sa linggong ito.",
        "error": "Nabigong i-load ang data ng pagganap.",
        "loading": "Naglo-load...",
        "more": "Tingnan Pa"
    },
    "th": {
        "title": "ผลงานประจำสัปดาห์ที่ดีที่สุด",
        "empty": "ไม่มีข้อมูลสำหรับสัปดาห์นี้",
        "error": "ไม่สามารถโหลดข้อมูลผลงานได้",
        "loading": "กำลังโหลด...",
        "more": "ดูเพิ่มเติม"
    },
    "vi": {
        "title": "Hiệu Suất Hàng Tuần Tốt Nhất",
        "empty": "Không có dữ liệu cho tuần này.",
        "error": "Không thể tải dữ liệu hiệu suất.",
        "loading": "Đang tải...",
        "more": "Xem Thêm"
    }
}

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already has survival-weekly-performance
    if 'class="survival-weekly-performance"' in content:
        print(f"Skipping {filepath} - already has the section.")
        return

    # Extract language
    lang_match = re.search(r'<html[^>]*lang="([^"]+)"', content)
    lang = lang_match.group(1).lower() if lang_match else 'en'
    
    # Map zh-Hans to zh-hans
    if lang == 'zh-hans':
        lang = 'zh-hans'
    elif lang == 'pt-br':
        lang = 'pt-br'

    t = translations.get(lang, translations['en'])

    # 1. Inject CSS
    if '</style>' in content:
        # Find the last </style> before </head>
        head_end = content.find('</head>')
        last_style_end = content.rfind('</style>', 0, head_end)
        if last_style_end != -1:
            content = content[:last_style_end] + css_to_inject + content[last_style_end:]

    # 2. Inject HTML
    # We need to find the end of the <div class="missed-signal-glass"> block.
    # It looks like:
    # <div class="missed-signal-glass">
    # ...
    # </div>
    # </div>
    # </section>
    
    html_to_inject = f"""
<section aria-label="{t['title']}" class="survival-weekly-performance" data-empty-text="{t['empty']}" data-error-text="{t['error']}" data-loading-text="{t['loading']}" id="survival-weekly-performance">
<div class="survival-weekly-performance-head">
<h3 class="survival-weekly-performance-title">{t['title']}</h3>
<span class="survival-weekly-scroll-hint">← →</span>
</div>
<div class="survival-weekly-viewport">
<div class="survival-weekly-track"></div>
</div>
<p class="survival-weekly-status" hidden="">{t['loading']}</p>
<div class="survival-weekly-more-wrap">
<a class="survival-weekly-more" href="performance.html">{t['more']} <span aria-hidden="true">→</span></a>
</div>
</section>
"""

    # Find the features-header-ultimate section
    glass_match = re.search(r'<div class="missed-signal-glass">.*?</div>\s*</div>\s*</section>', content, re.DOTALL)
    if glass_match:
        insert_pos = glass_match.end()
        # Wait, the structure is:
        # <div class="missed-signal-glass">...</div>
        # </div>
        # </section>
        # We want to insert it AFTER <div class="missed-signal-glass">...</div> but BEFORE the closing </div> of container?
        # Let's check ko/survival.html:
        # <div class="missed-signal-glass">...</div>
        # <section aria-label="..." class="survival-weekly-performance" ...>
        # ...
        # </section>
        # </div>
        # </section>
        
        # So we should insert it right after the closing </div> of missed-signal-glass.
        glass_div_match = re.search(r'<div class="missed-signal-glass">.*?</div>', content, re.DOTALL)
        if glass_div_match:
            insert_pos = glass_div_match.end()
            content = content[:insert_pos] + html_to_inject + content[insert_pos:]
    
    # 3. Inject JS script
    # <script defer="" src="../js/survival-performance-preview.js" type="text/javascript"></script>
    # Right before the jquery script: <script crossorigin="anonymous" ... src="...jquery..."></script>
    js_to_inject = '\n<script defer="" src="../js/survival-performance-preview.js" type="text/javascript"></script>\n'
    jquery_match = re.search(r'<script[^>]*src="[^"]*jquery[^"]*"[^>]*></script>', content)
    if jquery_match:
        insert_pos = jquery_match.start()
        content = content[:insert_pos] + js_to_inject + content[insert_pos:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {filepath}")

if __name__ == "__main__":
    files = glob.glob("C:/Users/hijko3/Desktop/Work/Site2/DEPLOY/**/survival.html", recursive=True)
    for f in files:
        if 'ko\\survival.html' in f or 'ru\\survival.html' in f:
            continue
        process_file(f)
