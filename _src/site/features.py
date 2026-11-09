"""Features page copy (en, ko) and builder.

Facts come from the app's own strings (lib/flutter_flow/i18n_auto.dart) and the pricing
page. Same copy rules as the home page: no profit or win-rate claims, risk notice next to
auto-orders, referral rewards always with their conditions.
"""
from charts import case_svg
from chrome import asset_version
from common import CASES, HERE, ICONS, chrome_vals, icon, render, usd, when, write

ICONS.setdefault("arrow", '<path d="M5 12h14M13 6l6 6-6 6"/>')
TEMPLATE = (HERE / "features.html").read_text(encoding="utf-8")
GALLERY = ["jul-bottom", "may-top", "nov-top", "sep-bottom"]
INDEX = ["divergence", "filters", "alarms", "indicators", "keywords", "auto-order", "log", "ref-reward"]

STRINGS = {
    "en": dict(
        meta_title="DivAlarm Features | RSI Divergence Alarms, Keyword Alarms and Auto-Orders",
        meta_desc="RSI divergence alerts on 9 timeframes, alarms that ring through silent mode, indicator and keyword alarms, and Pro auto-orders on five exchanges.",
        h1_a="Everything DivAlarm does.", h1_b="From the alert to the order.",
        lead="It watches BTC and ETH for divergences and rings only for the signals worth waking you for. When a TradingView alert or your own rule matches, it places the futures order on Binance, Bybit, OKX, Bitget or Gate. Jump to any part:",
        index_label="On this page",
        index=["Divergence alerts", "Filters", "Alarms", "Indicator alerts", "Keyword alarms", "Auto-orders", "Signal log", "Referral rewards"],
        div_h2="RSI divergence alerts, early or confirmed",
        div_lead="DivAlarm checks Bitcoin and Ethereum perpetual futures on nine timeframes, from 1m to 1D, with RSI 7 and RSI 14. You decide when an alert should reach you.",
        stages=[
            ("Early Completed", "Alerts as soon as the conditions are met when the previous candle closes. Fastest, but the signal can be invalidated if the current candle makes a new high or low."),
            ("Confirmed", "Alerts only if the conditions still hold after the next candle closes. Slower, and later candles can't invalidate it."),
            ("Both", "Get the Early alert first and a second one when it is confirmed. If the Early signal is invalidated, no Confirmed alert follows."),
        ],
        cases_h3="Four turns from the past year",
        case_titles={"jul-bottom": "July 2026 bottom, daily chart", "may-top": "May 2026 top, daily chart",
                     "nov-top": "November 2025 top, 4-hour chart", "sep-bottom": "September 2026 bottom, 4-hour chart"},
        case_da="DivAlarm", case_tv="TradingView", case_at="at",
        case_tv_none={"low": "No signal at this bottom", "high": "No signal at this top"},
        case_alert="Alert", case_aria="{title}. DivAlarm sent an alert on {when} at {price}. TradingView's standard RSI divergence showed no signal at this turn.",
        cases_fine="Selected cases, replayed on Binance BTCUSDT perpetual history, times in UTC. TradingView = standard RSI indicator divergence rules (5-bar pivots). DivAlarm sends far more alerts than TradingView, and not every alert leads to a reversal. Past signals don't guarantee future results.",
        flt_h2="Filters that cut the noise",
        flt_lead="Divergences show up often on small timeframes. Add conditions so only the setups you trade get through. Each condition you add makes alerts rarer.",
        flt_items=[
            ("filter", "RSI threshold", "Only alert when RSI is past a level you set, such as above 70 for bearish divergences."),
            ("chart", "Bollinger Bands", "Only alert when price is outside the Bollinger Bands."),
            ("layers", "Price filter and signal stage", "Add a price condition, and choose Early Completed, Confirmed or both."),
        ],
        mf_title="Filter 1, BTCUSDT", mf_tfs='<span class="da-chip">5m</span><span class="da-chip on">15m</span><span class="da-chip on">1h</span><span class="da-chip on">4h</span><span class="da-chip">1D</span>',
        mf_rsi="RSI threshold", mf_bb="Outside Bollinger Bands", mf_price="Price filter", mf_stage="Confirmed only",
        alm_h2="Alarms that wake you, not just notify you",
        alm_lead="A force alarm rings through silent mode and Do Not Disturb, full screen. Keep it ringing until you stop it, or let it ring once.",
        alm_items=[
            ("bell", "Force alarm or phone settings", "Ring through silent mode, or follow your phone's sound settings."),
            ("toggle", "Repeat, once or vibrate", "Keep ringing until you stop it, ring once, or vibrate only."),
            ("list", "Five alarm types", "Types A to E with five built-in sounds, or your own audio file."),
        ],
        ph_title="BTCUSDT 4H bullish divergence", ph_sub="Early Completed", ph_tag="Bullish", ph_stop="Stop alarm",
        ind_h2="More than divergence",
        ind_lead="Turn on extra indicator alerts for the timeframes you watch.",
        ind_items=[
            ("Supertrend", "Buy and sell flips."),
            ("Support and resistance", "Price approaching a support or resistance level."),
            ("Bollinger Bands", "Price breaking out of the bands."),
            ("EMA crosses", "Crosses of the 20, 50, 100 and 200 EMA."),
            ("Price alerts", "Price moving above or below a level you set."),
        ],
        kw_h2="Keyword alarms turn any alert into an alarm",
        kw_lead="Pick a keyword and what should happen when it shows up. DivAlarm looks for it in three places.",
        kw_sources=[
            ("TradingView webhooks", "Messages sent to your personal webhook URL from TradingView or another service."),
            ("Phone notifications (Android)", "Titles and messages of notifications on your phone, after you allow notification access."),
            ("DivAlarm signals", "Its own divergence, indicator and price signals, as @D, @E and @P conditions."),
        ],
        kw_rule="Rule", kw_rule_kw="when this keyword arrives", kw_rule_combo="or combine signals within a time window",
        kw_actions=[("bell", "Alarm"), ("link", "Combined alarm"), ("candles", "Auto-order (Pro)")],
        kw_note="Keyword alarms are part of Pro. Every account can try them 5 times free. The 5 uses are shared by webhooks, phone keywords and combined alarms, and don't include auto-orders.",
        kw_link="Set up TradingView webhooks",
        ao_h2="Auto-orders on five exchanges",
        ao_lead="When a keyword rule matches, the DivAlarm app on your phone places the futures order on Binance, Bybit, OKX, Bitget or Gate with the settings you chose.",
        ao_opts=[
            ("Order types", "Market, limit with a price offset and an expiry, or fast limit, which fills within your slippage limit and cancels the rest."),
            ("Position and risk", "Size, leverage, isolated or cross margin, take-profit and stop-loss."),
            ("Open, close or reverse", "Reverse checks the live position size at order time."),
            ("When it runs", "Once, or every time the rule matches. Up to 5 orders per rule."),
        ],
        tk_title="when this keyword arrives",
        tk_rows=[("Symbol", "BTCUSDT"), ("Side", "Long"), ("Type", "Fast limit, slippage 0.1%"), ("Margin", "Isolated, 10×"), ("TP / SL", "2% / 1%"), ("Runs", "Once only")],
        tk_toast="Order placed: BTCUSDT long",
        risk_auto="Auto-orders use real money on leveraged futures, and there is no paper-trading mode. Start with a small size. Auto-Order requires Pro.",
        video_h3="Watch a TradingView alert place an order",
        log_h2="Check the details before you act",
        log_h3="Signal log",
        log_p="Every alert stays in your log with its details: prices and RSI values at both pivots, start and end times, which timeframes are still forming, and where price sits against the Bollinger Bands.",
        log_rows=[("Signal", "15m Bearish Completed"), ("Price 1", "88,637.40"), ("Price 2", "89,170.30"), ("RSI 1", "79.34"), ("RSI 2", "77.16"), ("Forming", "bear 30m, bear 1h")],
        chart_h3="Live chart",
        chart_p="BTCUSDT and ETHUSDT candles from Binance with divergence marks, EMA and Bollinger Band overlays, and drawing tools.",
        chart_tools=["Measure", "Risk/Reward", "Fibonacci", "Trend line", "Channel"],
        ref_h2="Referral rewards",
        ref_lead="Share your referral code or link from the app. People who subscribe with it pay less for Basic, and you receive USDT each time their paid subscription renews.",
        ref_rows=[
            ("Monthly subscriptions", "Each month, 1.50 USDT per referral while you have 1–10 referrals, 2.00 USDT with 11–50, and 2.50 USDT with 51 or more."),
            ("Annual subscriptions", "25 USDT per referral."),
            ("Price for people you refer", "Basic monthly costs $5.40 for the first month, then $6.50 a month, before tax."),
            ("Payout", "Each reward is confirmed 14 days after the payment. Once your confirmed balance reaches 3 USDT, it is sent in USDT (BEP-20) to the wallet you register."),
        ],
        ref_note="Rewards depend on the people you refer keeping a paid subscription, so there is no guaranteed amount. Your referral code is in the app under Referral rewards.",
        close_a="Reversals don't wait.", close_b="Keep your alarm on.",
        cta_play="Get it on Google Play", cta_trial="Try Premium free for 5 days",
    ),
    "ko": dict(
        meta_title="DivAlarm 기능 | RSI 다이버전스 알람, 키워드 알람, 자동 주문",
        meta_desc="9개 시간대 RSI 다이버전스 알림, 무음을 뚫는 알람, 지표·키워드 알람, 거래소 5곳 Pro 자동 주문까지 한 번에 보세요.",
        h1_a="DivAlarm이 하는 일, 전부.", h1_b="알림에서 끝나지 않고, 주문까지.",
        lead="BTC와 ETH의 다이버전스를 지켜보다가 깨울 만한 신호에만 알람을 울려요. TradingView 알림이나 내가 만든 규칙이 맞으면 Binance, Bybit, OKX, Bitget, Gate에 선물 주문까지 넣어요. 궁금한 기능으로 바로 가 보세요.",
        index_label="이 페이지 목차",
        index=["다이버전스 알림", "필터", "알람", "지표 알림", "키워드 알람", "자동 주문", "신호 기록", "추천 보상"],
        div_h2="RSI 다이버전스 알림, 빠르게 또는 확실하게",
        div_lead="비트코인과 이더리움 무기한 선물을 1분봉부터 일봉까지 9개 시간대에서 RSI 7과 RSI 14로 지켜봐요. 알림을 언제 받을지는 직접 정해요.",
        stages=[
            ("Early Completed", "직전 봉이 마감되며 조건이 충족되는 순간 알려요. 가장 빠르지만, 진행 중인 봉이 새 고점이나 저점을 만들면 무효화될 수 있어요."),
            ("Confirmed", "다음 봉까지 마감된 뒤에도 조건이 유지될 때만 알려요. 느리지만 이후 봉 때문에 무효화되지 않아요."),
            ("둘 다", "Early 알림을 먼저 받고, 확정되면 한 번 더 받아요. Early 신호가 무효화되면 Confirmed 알림은 오지 않아요."),
        ],
        cases_h3="지난 1년의 반전 네 장면",
        case_titles={"jul-bottom": "2026년 7월 바닥, 일봉", "may-top": "2026년 5월 고점, 일봉",
                     "nov-top": "2025년 11월 고점, 4시간봉", "sep-bottom": "2026년 9월 바닥, 4시간봉"},
        case_da="DivAlarm", case_tv="TradingView", case_at="",
        case_tv_none={"low": "이 바닥에서 신호 없음", "high": "이 고점에서 신호 없음"},
        case_alert="알림", case_aria="{title}. DivAlarm은 {when}(한국 시간) {price}에서 알림을 보냈어요. TradingView 기본 RSI 다이버전스는 이 반전에서 신호가 없었어요.",
        cases_fine="골라 낸 사례예요. Binance BTCUSDT 무기한 선물 과거 데이터로 재현했고, 시각은 한국 시간이에요. TradingView는 기본 RSI 지표의 다이버전스 규칙(피벗 좌우 5봉) 기준. DivAlarm은 TradingView보다 훨씬 많은 알림을 보내며, 모든 알림이 반전으로 이어지지는 않아요. 과거 신호가 미래 결과를 보장하지 않아요.",
        flt_h2="잡음을 거르는 필터",
        flt_lead="작은 시간대에서는 다이버전스가 자주 나와요. 조건을 더해서 내가 매매하는 자리만 받으세요. 조건을 더할수록 알림은 드물어져요.",
        flt_items=[
            ("filter", "RSI 임계값", "하락 다이버전스는 RSI 70 이상일 때만처럼, 정한 수준을 넘을 때만 알려요."),
            ("chart", "볼린저 밴드", "가격이 볼린저 밴드 밖에 있을 때만 알려요."),
            ("layers", "가격 필터와 신호 단계", "가격 조건을 더하고, Early Completed와 Confirmed 중 무엇을 받을지 골라요."),
        ],
        mf_title="필터 1, BTCUSDT", mf_tfs='<span class="da-chip">5m</span><span class="da-chip on">15m</span><span class="da-chip on">1h</span><span class="da-chip on">4h</span><span class="da-chip">1D</span>',
        mf_rsi="RSI 임계값", mf_bb="볼린저 밴드 밖", mf_price="가격 필터", mf_stage="Confirmed만 받기",
        alm_h2="알림이 아니라, 깨우는 알람",
        alm_lead="강제 알람은 무음과 방해 금지 모드에서도 전체 화면으로 울려요. 끌 때까지 계속 울리게 할 수도, 한 번만 울리게 할 수도 있어요.",
        alm_items=[
            ("bell", "강제 알람 또는 폰 설정 따르기", "무음을 뚫고 울리거나, 폰의 소리 설정을 따르게 해요."),
            ("toggle", "반복, 한 번, 진동", "끌 때까지 반복, 한 번만, 진동만 중에서 골라요."),
            ("list", "알람 유형 5가지", "A~E 유형과 기본 알림음 5개, 또는 내 음원 파일."),
        ],
        ph_title="BTCUSDT 4H 상승 다이버전스", ph_sub="Early Completed", ph_tag="상승", ph_stop="알람 끄기",
        ind_h2="다이버전스 말고도",
        ind_lead="지켜보는 시간대에서 보조 지표 알림도 켤 수 있어요.",
        ind_items=[
            ("슈퍼트렌드", "매수·매도 전환."),
            ("지지·저항", "가격이 지지선이나 저항선에 다가올 때."),
            ("볼린저 밴드", "가격이 밴드를 벗어날 때."),
            ("EMA 교차", "20, 50, 100, 200 EMA 교차."),
            ("가격 알림", "정한 가격 위나 아래로 움직일 때."),
        ],
        kw_h2="키워드 알람: 어떤 알림이든 알람으로",
        kw_lead="키워드를 정하고, 그 키워드가 나타나면 무엇을 할지 고르세요. DivAlarm은 세 곳에서 키워드를 찾아요.",
        kw_sources=[
            ("TradingView 웹훅", "TradingView 등에서 내 웹훅 URL로 보낸 메시지."),
            ("폰 알림 (Android)", "알림 접근을 허용하면 폰에 온 알림의 제목과 내용."),
            ("DivAlarm 신호", "자체 다이버전스·지표·가격 신호를 @D, @E, @P 조건으로."),
        ],
        kw_rule="규칙", kw_rule_kw="이 키워드가 오면", kw_rule_combo="또는 시간 창 안에서 신호를 묶어서",
        kw_actions=[("bell", "알람"), ("link", "결합 알람"), ("candles", "자동 주문 (Pro)")],
        kw_note="키워드 알람은 Pro 기능이에요. 모든 계정은 5회 무료로 써 볼 수 있어요. 5회는 웹훅, 폰 알림 키워드, 결합 알람이 함께 쓰고, 자동 주문은 포함되지 않아요.",
        kw_link="TradingView 웹훅 연결하기",
        ao_h2="거래소 5곳 자동 주문",
        ao_lead="키워드 규칙이 맞으면 폰의 DivAlarm 앱이 Binance, Bybit, OKX, Bitget, Gate에 정해 둔 설정대로 선물 주문을 넣어요.",
        ao_opts=[
            ("주문 방식", "시장가, 가격 오프셋과 만료 시간을 정하는 지정가, 허용 슬리피지 안에서 바로 체결하고 나머지는 취소하는 빠른 지정가."),
            ("포지션과 위험 관리", "수량, 레버리지, 격리·교차 마진, 익절·손절."),
            ("진입, 청산, 반전", "반전은 주문 시점의 실제 포지션 수량을 조회해요."),
            ("실행 시점", "한 번만, 또는 규칙이 맞을 때마다. 규칙당 주문은 최대 5개예요."),
        ],
        tk_title="이 키워드가 오면",
        tk_rows=[("종목", "BTCUSDT"), ("방향", "롱"), ("주문", "빠른 지정가, 슬리피지 0.1%"), ("마진", "격리, 10×"), ("익절 / 손절", "2% / 1%"), ("실행", "한 번만")],
        tk_toast="주문 완료: BTCUSDT 롱",
        risk_auto="자동 주문은 레버리지 선물 계좌의 실제 자금으로 실행되고, 모의 거래 모드는 없어요. 작은 수량부터 시작하세요. 자동 주문은 Pro 전용이에요.",
        video_h3="TradingView 알림이 주문으로 이어지는 모습",
        log_h2="행동하기 전에 자세히 확인하세요",
        log_h3="신호 기록",
        log_p="모든 알림은 기록에 남고, 두 피벗의 가격과 RSI 값, 시작·끝 시각, 아직 형성 중인 시간대, 볼린저 밴드 대비 위치까지 볼 수 있어요.",
        log_rows=[("신호", "15m Bearish Completed"), ("가격 1", "88,637.40"), ("가격 2", "89,170.30"), ("RSI 1", "79.34"), ("RSI 2", "77.16"), ("형성 중", "bear 30m, bear 1h")],
        chart_h3="실시간 차트",
        chart_p="Binance BTCUSDT·ETHUSDT 캔들에 다이버전스 표시, EMA·볼린저 밴드, 그리기 도구까지 있어요.",
        chart_tools=["측정", "손익비", "피보나치", "추세선", "채널"],
        ref_h2="추천 보상",
        ref_lead="앱에서 내 추천 코드나 링크를 공유하세요. 그 코드로 구독한 사람은 Basic을 더 싸게 쓰고, 나는 그 사람의 유료 구독이 갱신될 때마다 USDT를 받아요.",
        ref_rows=[
            ("월간 구독", "추천 1~10명이면 1명당 매월 1.50 USDT, 11~50명이면 2.00 USDT, 51명 이상이면 2.50 USDT."),
            ("연간 구독", "추천 1건당 25 USDT."),
            ("추천받은 사람의 가격", "Basic 월간이 첫 달 $5.40, 이후 월 $6.50이에요 (세전)."),
            ("지급", "보상은 결제 14일 뒤 확정돼요. 확정 금액이 3 USDT 이상이면 등록한 지갑으로 USDT(BEP-20)를 보내요."),
        ],
        ref_note="보상은 추천한 사람이 유료 구독을 유지할 때만 생기며, 정해진 금액을 보장하지 않아요. 추천 코드는 앱의 추천 보상 메뉴에서 확인할 수 있어요.",
        close_a="반전은 기다려주지 않아요.", close_b="알람을 켜 두세요.",
        cta_play="Google Play에서 받기", cta_trial="프리미엄 5일 무료체험",
    ),
}


def case_card(cid, L, lang):
    c = CASES[cid]
    title = L["case_titles"][cid]
    t = when(c["detectedAt"], lang)
    price = usd(c["detPrice"])
    at = f"{t} {L['case_at']} {price}".replace("  ", " ") if L["case_at"] else f"{t}, {price}"
    aria = L["case_aria"].format(title=title, when=when(c["detectedAt"], lang), price=price)
    opts = dict(alert_label=f'{L["case_alert"]} {price}', tv_label="TradingView", aria=aria, cls="case-chart", uid=cid.replace("-", ""))
    return (f'<figure class="case da-panel"><h4>{title}</h4>'
            f'{case_svg(c, lang, **opts)}{case_svg(c, lang, narrow=True, **opts)}'
            f'<dl><dt>{L["case_da"]}</dt><dd class="da">{at}</dd>'
            f'<dt>{L["case_tv"]}</dt><dd class="tv">{L["case_tv_none"][c["kind"]]}</dd></dl></figure>')


def li_items(items):
    return "".join(f"<li>{icon(i)}<b>{b}</b><span>{s}</span></li>" for i, b, s in items)


def build(lang):
    L = STRINGS[lang]
    vals = {k: v for k, v in L.items() if isinstance(v, str)}
    vals.update(chrome_vals(lang, "features.html"))
    vals.update(
        lang_v=asset_version("js/lang-switcher.js", "css/lang-switcher.css"),
        index_links="".join(f'<a href="#{a}"{" class=\"hot\"" if a == "auto-order" else ""}>{t}</a>' for a, t in zip(INDEX, L["index"])),
        stages="".join(f'<li class="da-panel"><div class="k">{k}</div><p>{p}</p></li>' for k, p in L["stages"]),
        cases="".join(case_card(cid, L, lang) for cid in GALLERY),
        flt_items=li_items(L["flt_items"]), alm_items=li_items(L["alm_items"]),
        ind_items="".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in L["ind_items"]),
        kw_sources="".join(f'<div class="da-panel"><b>{a}</b><span>{b}</span></div>' for a, b in L["kw_sources"]),
        kw_actions="".join(f'<div class="da-panel">{icon(i)}{t}</div>' for i, t in L["kw_actions"]),
        ao_opts="".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in L["ao_opts"]),
        tk_rows="".join(f'<div class="row"><span>{a}</span><span>{b}</span></div>' for a, b in L["tk_rows"]),
        log_rows="".join(f"<span>{a}</span><span>{b}</span>" for a, b in L["log_rows"]),
        chart_tools="".join(f"<span>{t}</span>" for t in L["chart_tools"]),
        ref_rows="".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in L["ref_rows"]),
        icon_bell=icon("bell"), icon_arrow=icon("arrow"), icon_warn=icon("warn"),
    )
    write(lang, "features.html", render(TEMPLATE, vals))
