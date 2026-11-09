"""Site-wide header and footer ("chrome") for every DivAlarm page and locale.

The same markup goes on the built pages (home, features) and is swapped into the
legacy Webflow pages by apply_chrome.py, so navigation is identical everywhere.
"""
import hashlib
from pathlib import Path

DEPLOY = Path(__file__).resolve().parent.parent.parent
PLAY_URL = "https://play.google.com/store/apps/details?id=com.flutterflow.divalarm2"
PRETENDARD = "https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css"
LOCALES = ["en", "ko", "ru", "vi", "tr", "pt-br", "uk", "id", "ja", "de", "ur", "fil", "th", "ms", "zh-hans", "es"]

NAV = [("features.html", "nav_features"), ("performance.html", "nav_performance"),
       ("tradingview-webhook.html", "nav_tv"), ("pricing.html", "nav_pricing"), ("qna.html", "nav_qna")]

LABELS = {
    "en": dict(skip="Skip to content", nav_label="Main", menu="Menu",
               nav_features="Features", nav_performance="Performance", nav_tv="TradingView", nav_pricing="Pricing", nav_qna="Q&amp;A",
               sign_in="Sign in", my_account="My account", sign_out="Sign out", get_app="Get the app",
               foot_risk="DivAlarm is an alert tool, not investment advice. Crypto futures trading carries a high risk of loss. Past signals don't guarantee future results.",
               f_product="Product", f_downloads="Downloads", f_guides="Guides", f_rsi="RSI divergence", f_manual="User manual",
               f_tv="TradingView setup", f_company="Company", f_referral="Referral rewards", f_contact="Contact"),
    "ko": dict(skip="본문으로 건너뛰기", nav_label="주 메뉴", menu="메뉴",
               nav_features="기능", nav_performance="신호 기록", nav_tv="TradingView 연결", nav_pricing="요금제", nav_qna="Q&amp;A",
               sign_in="로그인", my_account="내 계정", sign_out="로그아웃", get_app="앱 받기",
               foot_risk="DivAlarm은 알림 도구이며 투자 조언이 아니에요. 암호화폐 선물 거래는 원금 손실 위험이 커요. 과거 신호가 미래 결과를 보장하지 않아요.",
               f_product="제품", f_downloads="다운로드", f_guides="가이드", f_rsi="RSI 다이버전스", f_manual="사용 설명서",
               f_tv="TradingView 연결", f_company="회사", f_referral="추천 보상", f_contact="문의하기"),
    "ja": dict(skip="本文へスキップ", nav_label="メインメニュー", menu="メニュー",
               nav_features="機能", nav_performance="パフォーマンス", nav_tv="TradingView連携", nav_pricing="料金", nav_qna="よくある質問",
               sign_in="ログイン", my_account="マイアカウント", sign_out="ログアウト", get_app="アプリを入手",
               foot_risk="DivAlarmはアラートツールであり、投資助言ではありません。暗号資産の先物取引には大きな損失リスクがあります。過去のシグナルは将来の結果を保証しません。",
               f_product="製品", f_downloads="ダウンロード", f_guides="ガイド", f_rsi="RSIダイバージェンス", f_manual="ユーザーマニュアル",
               f_tv="TradingView設定", f_company="会社", f_referral="紹介報酬", f_contact="お問い合わせ"),
    "zh-hans": dict(skip="跳到正文", nav_label="主菜单", menu="菜单",
                    nav_features="功能", nav_performance="表现", nav_tv="TradingView 连接", nav_pricing="定价", nav_qna="问答",
                    sign_in="登录", my_account="我的账户", sign_out="退出登录", get_app="获取应用",
                    foot_risk="DivAlarm 是提醒工具，不构成投资建议。加密货币期货交易存在较高的亏损风险。过往信号不代表未来结果。",
                    f_product="产品", f_downloads="下载", f_guides="指南", f_rsi="RSI 背离", f_manual="用户手册",
                    f_tv="TradingView 设置", f_company="公司", f_referral="推荐奖励", f_contact="联系我们"),
    "es": dict(skip="Saltar al contenido", nav_label="Principal", menu="Menú",
               nav_features="Funciones", nav_performance="Rendimiento", nav_tv="TradingView", nav_pricing="Precios", nav_qna="Preguntas",
               sign_in="Iniciar sesión", my_account="Mi cuenta", sign_out="Cerrar sesión", get_app="Obtener la app",
               foot_risk="DivAlarm es una herramienta de alertas, no asesoramiento de inversión. Operar futuros de criptomonedas conlleva un alto riesgo de pérdida. Las señales pasadas no garantizan resultados futuros.",
               f_product="Producto", f_downloads="Descargas", f_guides="Guías", f_rsi="Divergencia RSI", f_manual="Manual de usuario",
               f_tv="Configurar TradingView", f_company="Empresa", f_referral="Recompensas por referidos", f_contact="Contacto"),
    "pt-br": dict(skip="Pular para o conteúdo", nav_label="Principal", menu="Menu",
                  nav_features="Recursos", nav_performance="Desempenho", nav_tv="TradingView", nav_pricing="Preços", nav_qna="Dúvidas",
                  sign_in="Entrar", my_account="Minha conta", sign_out="Sair", get_app="Baixar o app",
                  foot_risk="O DivAlarm é uma ferramenta de alertas, não uma recomendação de investimento. Negociar futuros de criptomoedas envolve alto risco de perda. Sinais passados não garantem resultados futuros.",
                  f_product="Produto", f_downloads="Downloads", f_guides="Guias", f_rsi="Divergência RSI", f_manual="Manual do usuário",
                  f_tv="Configurar TradingView", f_company="Empresa", f_referral="Recompensas por indicação", f_contact="Contato"),
    "de": dict(skip="Zum Inhalt springen", nav_label="Hauptmenü", menu="Menü",
               nav_features="Funktionen", nav_performance="Performance", nav_tv="TradingView", nav_pricing="Preise", nav_qna="FAQ",
               sign_in="Anmelden", my_account="Mein Konto", sign_out="Abmelden", get_app="App holen",
               foot_risk="DivAlarm ist ein Alarm-Tool und keine Anlageberatung. Der Handel mit Krypto-Futures birgt ein hohes Verlustrisiko. Vergangene Signale garantieren keine zukünftigen Ergebnisse.",
               f_product="Produkt", f_downloads="Downloads", f_guides="Anleitungen", f_rsi="RSI-Divergenz", f_manual="Benutzerhandbuch",
               f_tv="TradingView einrichten", f_company="Unternehmen", f_referral="Empfehlungsprämien", f_contact="Kontakt"),
    "ru": dict(skip="Перейти к содержимому", nav_label="Главное меню", menu="Меню",
               nav_features="Функции", nav_performance="Результаты", nav_tv="TradingView", nav_pricing="Тарифы", nav_qna="Вопросы",
               sign_in="Войти", my_account="Мой аккаунт", sign_out="Выйти", get_app="Скачать",
               foot_risk="DivAlarm — инструмент оповещений, а не инвестиционная рекомендация. Торговля криптовалютными фьючерсами связана с высоким риском потерь. Прошлые сигналы не гарантируют будущих результатов.",
               f_product="Продукт", f_downloads="Загрузки", f_guides="Руководства", f_rsi="Дивергенция RSI", f_manual="Руководство пользователя",
               f_tv="Настройка TradingView", f_company="Компания", f_referral="Реферальные награды", f_contact="Контакты"),
    "uk": dict(skip="Перейти до вмісту", nav_label="Головне меню", menu="Меню",
               nav_features="Функції", nav_performance="Результати", nav_tv="TradingView", nav_pricing="Ціни", nav_qna="Питання",
               sign_in="Увійти", my_account="Мій акаунт", sign_out="Вийти", get_app="Завантажити",
               foot_risk="DivAlarm — інструмент сповіщень, а не інвестиційна порада. Торгівля криптовалютними ф'ючерсами пов'язана з високим ризиком втрат. Минулі сигнали не гарантують майбутніх результатів.",
               f_product="Продукт", f_downloads="Завантаження", f_guides="Посібники", f_rsi="Дивергенція RSI", f_manual="Посібник користувача",
               f_tv="Налаштування TradingView", f_company="Компанія", f_referral="Реферальні винагороди", f_contact="Контакти"),
    "tr": dict(skip="İçeriğe geç", nav_label="Ana menü", menu="Menü",
               nav_features="Özellikler", nav_performance="Performans", nav_tv="TradingView", nav_pricing="Fiyatlandırma", nav_qna="Soru-Cevap",
               sign_in="Giriş yap", my_account="Hesabım", sign_out="Çıkış yap", get_app="Uygulamayı indir",
               foot_risk="DivAlarm bir alarm aracıdır, yatırım tavsiyesi değildir. Kripto vadeli işlemler yüksek kayıp riski taşır. Geçmiş sinyaller gelecekteki sonuçları garanti etmez.",
               f_product="Ürün", f_downloads="İndirmeler", f_guides="Kılavuzlar", f_rsi="RSI uyumsuzluğu", f_manual="Kullanım kılavuzu",
               f_tv="TradingView kurulumu", f_company="Şirket", f_referral="Referans ödülleri", f_contact="İletişim"),
    "vi": dict(skip="Chuyển đến nội dung", nav_label="Menu chính", menu="Menu",
               nav_features="Tính năng", nav_performance="Hiệu suất", nav_tv="TradingView", nav_pricing="Bảng giá", nav_qna="Hỏi &amp; Đáp",
               sign_in="Đăng nhập", my_account="Tài khoản", sign_out="Đăng xuất", get_app="Tải ứng dụng",
               foot_risk="DivAlarm là công cụ cảnh báo, không phải lời khuyên đầu tư. Giao dịch hợp đồng tương lai tiền mã hóa có rủi ro thua lỗ cao. Tín hiệu trong quá khứ không đảm bảo kết quả trong tương lai.",
               f_product="Sản phẩm", f_downloads="Tải xuống", f_guides="Hướng dẫn", f_rsi="Phân kỳ RSI", f_manual="Hướng dẫn sử dụng",
               f_tv="Thiết lập TradingView", f_company="Công ty", f_referral="Thưởng giới thiệu", f_contact="Liên hệ"),
    "id": dict(skip="Lewati ke konten", nav_label="Menu utama", menu="Menu",
               nav_features="Fitur", nav_performance="Performa", nav_tv="TradingView", nav_pricing="Harga", nav_qna="Tanya Jawab",
               sign_in="Masuk", my_account="Akun saya", sign_out="Keluar", get_app="Unduh aplikasi",
               foot_risk="DivAlarm adalah alat peringatan, bukan nasihat investasi. Trading futures kripto memiliki risiko kerugian yang tinggi. Sinyal masa lalu tidak menjamin hasil di masa depan.",
               f_product="Produk", f_downloads="Unduhan", f_guides="Panduan", f_rsi="Divergensi RSI", f_manual="Panduan pengguna",
               f_tv="Pengaturan TradingView", f_company="Perusahaan", f_referral="Hadiah referral", f_contact="Kontak"),
    "ms": dict(skip="Langkau ke kandungan", nav_label="Menu utama", menu="Menu",
               nav_features="Ciri", nav_performance="Prestasi", nav_tv="TradingView", nav_pricing="Harga", nav_qna="Soal Jawab",
               sign_in="Log masuk", my_account="Akaun saya", sign_out="Log keluar", get_app="Dapatkan aplikasi",
               foot_risk="DivAlarm ialah alat amaran, bukan nasihat pelaburan. Dagangan niaga hadapan kripto membawa risiko kerugian yang tinggi. Isyarat lalu tidak menjamin keputusan masa depan.",
               f_product="Produk", f_downloads="Muat turun", f_guides="Panduan", f_rsi="Pencapahan RSI", f_manual="Manual pengguna",
               f_tv="Persediaan TradingView", f_company="Syarikat", f_referral="Ganjaran rujukan", f_contact="Hubungi"),
    "fil": dict(skip="Lumaktaw sa nilalaman", nav_label="Pangunahing menu", menu="Menu",
                nav_features="Mga Feature", nav_performance="Performance", nav_tv="TradingView", nav_pricing="Presyo", nav_qna="Q&amp;A",
                sign_in="Mag-sign in", my_account="Aking account", sign_out="Mag-sign out", get_app="Kunin ang app",
                foot_risk="Ang DivAlarm ay isang alert tool, hindi payo sa pamumuhunan. Mataas ang panganib ng pagkalugi sa pag-trade ng crypto futures. Hindi garantiya ng mga nakaraang signal ang mga resulta sa hinaharap.",
                f_product="Produkto", f_downloads="Mga Download", f_guides="Mga Gabay", f_rsi="RSI Divergence", f_manual="Manwal ng User",
                f_tv="Setup ng TradingView", f_company="Kompanya", f_referral="Mga Referral Reward", f_contact="Makipag-ugnayan"),
    "th": dict(skip="ข้ามไปยังเนื้อหา", nav_label="เมนูหลัก", menu="เมนู",
               nav_features="ฟีเจอร์", nav_performance="ประสิทธิภาพ", nav_tv="TradingView", nav_pricing="ราคา", nav_qna="ถาม-ตอบ",
               sign_in="เข้าสู่ระบบ", my_account="บัญชีของฉัน", sign_out="ออกจากระบบ", get_app="ดาวน์โหลดแอป",
               foot_risk="DivAlarm เป็นเครื่องมือแจ้งเตือน ไม่ใช่คำแนะนำการลงทุน การเทรดฟิวเจอร์สคริปโตมีความเสี่ยงสูงที่จะขาดทุน สัญญาณในอดีตไม่ได้รับประกันผลลัพธ์ในอนาคต",
               f_product="ผลิตภัณฑ์", f_downloads="ดาวน์โหลด", f_guides="คู่มือ", f_rsi="RSI ไดเวอร์เจนซ์", f_manual="คู่มือผู้ใช้",
               f_tv="ตั้งค่า TradingView", f_company="บริษัท", f_referral="รางวัลการแนะนำ", f_contact="ติดต่อเรา"),
    "ur": dict(skip="مواد پر جائیں", nav_label="مرکزی مینو", menu="مینو",
               nav_features="فیچرز", nav_performance="کارکردگی", nav_tv="TradingView", nav_pricing="قیمتیں", nav_qna="سوال و جواب",
               sign_in="سائن ان", my_account="میرا اکاؤنٹ", sign_out="سائن آؤٹ", get_app="ایپ حاصل کریں",
               foot_risk="DivAlarm ایک الرٹ ٹول ہے، سرمایہ کاری کا مشورہ نہیں۔ کرپٹو فیوچرز ٹریڈنگ میں نقصان کا خطرہ زیادہ ہے۔ ماضی کے سگنل مستقبل کے نتائج کی ضمانت نہیں دیتے۔",
               f_product="پروڈکٹ", f_downloads="ڈاؤن لوڈز", f_guides="گائیڈز", f_rsi="RSI ڈائیورجنس", f_manual="یوزر مینول",
               f_tv="TradingView سیٹ اپ", f_company="کمپنی", f_referral="ریفرل انعامات", f_contact="رابطہ"),
}


def asset_version(*rel_paths):
    """Short content hash so browsers pick up changed CSS/JS right away."""
    h = hashlib.sha1()
    for rel in rel_paths:
        h.update((DEPLOY / rel).read_bytes())
    return h.hexdigest()[:8]


def head_links(legacy=False):
    css = ["css/site.css"] + (["css/legacy-skin.css"] if legacy else [])
    v = asset_version(*css)
    out = [f'<link rel="stylesheet" href="{PRETENDARD}" data-da-chrome=""/>']
    out += [f'<link rel="stylesheet" href="../{c}?v={v}" data-da-chrome=""/>' for c in css]
    return "\n".join(out)


def body_script():
    return f'<script type="module" src="../js/site.js?v={asset_version("js/site.js")}" data-da-chrome=""></script>'


MENU_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'


def header_html(lang, current=""):
    L = LABELS.get(lang, LABELS["en"])
    links = []
    for href, key in NAV:
        cur = ' aria-current="page"' if href == current else ""
        links.append(f'<a href="{href}"{cur}>{L[key]}</a>')
    return (
        f'<a class="da-skip" href="#main" data-da-chrome="">{L["skip"]}</a>\n'
        f'<header class="da-top" id="da-top">\n'
        f'  <div class="da-wrap da-top-row">\n'
        f'    <a class="da-brand" href="index.html"><img src="../images/divblue3-140.png" alt="" width="30" height="30"/><span>DivAlarm</span></a>\n'
        f'    <nav class="da-nav" id="da-nav" aria-label="{L["nav_label"]}">\n'
        f'      {"".join(links)}\n'
        f'      <div class="da-acct"><a href="sign-in-page.html" id="da-signin">{L["sign_in"]}</a>'
        f'<a href="my-account.html" id="da-account" hidden>{L["my_account"]}</a>'
        f'<button type="button" id="da-signout" hidden>{L["sign_out"]}</button></div>\n'
        f'    </nav>\n'
        f'    <div class="da-actions">\n'
        f'      <div class="da-lang" data-lang-slot=""></div>\n'
        f'      <a class="da-btn da-btn-primary da-btn-sm da-get" href="{PLAY_URL}" target="_blank" rel="noopener">{L["get_app"]}</a>\n'
        f'      <button class="da-menu" type="button" aria-expanded="false" aria-controls="da-nav" aria-label="{L["menu"]}">{MENU_ICON}</button>\n'
        f'    </div>\n'
        f'  </div>\n'
        # Older page scripts still write their sign-in state into #sign-btn2; keep a hidden target.
        f'  <a id="sign-btn2" href="sign-in-page.html" hidden></a>\n'
        f'</header>'
    )


def footer_html(lang):
    L = LABELS.get(lang, LABELS["en"])
    col = lambda title, items: (f'<div><p class="da-foot-h">{title}</p><ul>'
                                + "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in items) + "</ul></div>")
    return (
        f'<footer class="da-foot" id="da-foot">\n'
        f'  <div class="da-wrap">\n'
        f'    <div class="da-foot-grid">\n'
        f'      <div><a class="da-brand" href="index.html"><img src="../images/divblue3-140.png" alt="" width="30" height="30"/><span>DivAlarm</span></a>'
        f'<p class="da-foot-risk">{L["foot_risk"]}</p></div>\n'
        f'      {col(L["f_product"], [("features.html", L["nav_features"]), ("performance.html", L["nav_performance"]), ("pricing.html", L["nav_pricing"]), ("downloads.html", L["f_downloads"])])}\n'
        f'      {col(L["f_guides"], [("rsi-divergence.html", L["f_rsi"]), ("user-manual.html", L["f_manual"]), ("tradingview-webhook.html", L["f_tv"]), ("qna.html", L["nav_qna"])])}\n'
        f'      {col(L["f_company"], [("features.html#ref-reward", L["f_referral"]), ("mailto:info@wise-signal.com", L["f_contact"])])}\n'
        f'    </div>\n'
        # The locale generator replaces #wisesignal-legal-footer unless it carries data-keep.
        f'    <div class="da-legal" id="wisesignal-legal-footer" data-keep="1">\n'
        f'      <div>© 2026 WiseSignal Ltd.</div>\n'
        f'      <div>WiseSignal Ltd is registered in England and Wales (No. 16253236).</div>\n'
        f'      <div>Registered Office: 71-75 Shelton Street, London, WC2H 9JQ, UK.</div>\n'
        f'      <div>Contact: <a href="mailto:info@wise-signal.com">info@wise-signal.com</a></div>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</footer>'
    )
